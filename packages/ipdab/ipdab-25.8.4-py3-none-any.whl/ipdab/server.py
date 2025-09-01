import asyncio
import atexit
import inspect
import json
import logging
import threading
import time

from .debugger import Debugger


class IPDBAdapterServer:
    """
    A debug adapter server for ipdb, implementing the Debug Adapter Protocol (DAP).
    The debug adapter serves as a singleton that can be used to connect to an ipdb prompt.

    The idea is to start server in a separate thread, and then use the
    `set_trace` method to enter the ipdb prompt, which will be connected to the
    debug adapter server.

    The DAP protocol is only partly implemented, as ipdb blocks the main thread
    and does not allow for asynchronous operations. So, the server can only send information
    to the client, but cannot control the debugger itself. Control over the debugger can only
    be obtained if one controls the terminal where the ipdb prompt is running.

    So, e.g., in Neovim, one can use this debugger in a Neovim terminal, and connect to it via
    the a debugger that uses the DAP protocol to match the IDE with the ipdb prompt. To control
    the ipdb prompt in Neovim, one can create mappings to send debug commands to the terminal, e.g., 'c' for continue,
    'n' for next, 's' for step in, etc.

    The server runs in a separate thread that uses an asyncio event loop to handle incoming DAP messages.
    The server listens for incoming connections on the specified host and port, and handles DAP messages.
    Shutdown of the server is handled gracefully. The main entry points for shutdown are the
    `exited_callback` and the `_cleanup`. The former is called when the debugger exists, the latter is
    called when the adapter is deleted or the script exits using the `atexit` module.

    Note that some methods of the class are supposed to run inside the event loop thread,
    while others are supposed to run in the main thread.

    The setup is as follows. First, `server_main` is the main entry point for the event loop.
    It creates a server task from the `background_server` method.
    The server will be cleaned up automatically when this task is cancelled.
    This happens in the `shutdown_server` method, which should run inside the event loop thread.

    Second, the `run_loop` method is the entry point to start `server_main` in an event loop.
    It creates a runner for a context manager with automatic cleanup.
    The runner is also used in the debugger to schedule the `stopped_callback` and `exited_callback`.

    Third, `run_loop` is called from the `start_in_thread` method, which starts the event loop and its
    server in a seprate thread. In turn, the `start_in_thread` method is called from the `set_trace` method.

    The main entry point from debugging is the `set_trace` function in the module.
    This function uses the `IPDBAdapterServer` instance and calls its `set_trace` to start the server
    if it is not already running,
    """

    def __init__(
        self, host="127.0.0.1", port=9000, debugger="ipdb", on_continue="exit_without_breakpoint"
    ):
        # TODO: refactor to private attributes
        self.host = host
        self.port = port
        self.server = None
        self.server_task = None
        self._read_dap_message_task = None
        self.thread = None
        self.runner = None
        self.on_continue = on_continue
        self.debugger = Debugger(
            backend=debugger,
            stopped_callback=self.stopped_callback,
            exited_callback=self.exited_callback,
            on_continue_callback=lambda: self.on_continue,
        )
        self.client_writer = None
        self.client_reader = None
        # Prevent call the shutdown function twice
        self._shutdown_event = threading.Event()
        self._exited_event = threading.Event()
        self._terminated_event = threading.Event()

    def __del__(self):
        """
        Ensure the server is properly shutdown when the adapter is deleted.
        """
        self.shutdown()

    @property
    def on_continue(self):
        """
        on_continue : str (default="exit_without_breakpoint")
        Behavior when continuing from a breakpoint.
        Options are:
        - "exit_without_breakpoint": Exit the debugger on continue if no further breakpoints are set. Note `set_trace` calls do not count as breakpoints, in such cases the debug server will be reinitialized, and the clients needs to reconnect.
        - "exit": Exit the debug server even if there are break points set.
        - "keep_running": Keep the debug server running after continue, allowing future `set_trace` calls to re-enter the debugger.
        """
        return self._on_continue

    @on_continue.setter
    def on_continue(self, value):
        if not isinstance(value, str):
            raise ValueError("on_continue must be a string")
        if value not in ("exit_without_breakpoint", "exit", "keep_running"):
            raise ValueError(
                "on_continue must be one of 'exit_without_breakpoint', 'exit', or 'keep_running'"
            )
        self._on_continue = value

    async def read_dap_message(self, reader):
        header = b""
        while not header.endswith(b"\r\n\r\n"):
            header += await reader.read(1)
        header_text = header.decode()
        content_length = 0
        for line in header_text.strip().split("\r\n"):
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":")[1].strip())
        body = await reader.read(content_length)
        return json.loads(body.decode())

    def encode_dap_message(self, payload):
        body = json.dumps(payload)
        return f"Content-Length: {len(body)}\r\n\r\n{body}".encode()

    async def send_event(self, event_body):
        event_msg = {"type": "event", "seq": 0, **event_body}
        self.client_writer.write(self.encode_dap_message(event_msg))
        await self.client_writer.drain()

    @property
    def client_connected(self):
        return self.client_writer is not None and self.client_reader is not None

    @property
    def server_running(self):
        if self._shutdown_event.is_set():
            return False
        elif self.server is None and self.server_task is None:
            return False
        elif self.server is not None and self.server_task is not None and self.server.is_serving():
            return self.server.is_serving() and not self.server_task.done()
        else:
            msg = "Inconsistent server state: server and server_task mismatch"
            logging.error(f"[IPDB Server] {msg}")
            raise RuntimeError(msg)

    def stopped_callback(self, reason="breakpoint"):
        in_thread = "in thread" if threading.current_thread() == self.thread else "in main thread"
        function_name = inspect.currentframe().f_code.co_name
        if self._shutdown_event.is_set():
            return
        elif self.server_running:
            asyncio.run_coroutine_threadsafe(
                self.notify_stopped(reason=reason), self.runner._loop
            ).result()
        else:
            msg = f"[IPDB Server {function_name} {in_thread}] Server is not running, skipping stopped notification."
            logging.debug(msg)

    async def notify_stopped(self, reason="breakpoint"):
        if self.client_connected:
            await self.send_event(
                {
                    "event": "stopped",
                    "body": {
                        "reason": reason,
                        "threadId": 1,
                        "allThreadsStopped": True,
                    },
                }
            )

    def exited_callback(self, reason="exited"):
        """
        Notify the client that the program has exited.
        And shutdown the debug adapter server.
        This method is called from the debugger when it exits, i.e., once we do set_quit.
        """
        if self._shutdown_event.is_set():
            return
        elif self._exited_event.is_set():
            return
        elif self.server_running:
            asyncio.run_coroutine_threadsafe(
                self.notify_exited(reason=reason), self.runner._loop
            ).result()
        else:
            msg = "[DEBUGGER] No runner available for exited callback."
            logging.error(msg)
            raise RuntimeError(msg)

    async def notify_exited(self, reason="exited"):
        """
        Notify the client that the program has exited.
        And shutdown the debug adapter server.
        """
        if self._exited_event.is_set():
            return
        else:
            self._exited_event.set()
        if self.client_connected:
            if self._terminated_event.is_set():
                return
            else:
                await self.send_event(
                    {
                        "event": "exited",
                        "body": {"reason": reason},
                    }
                )
                await self.notify_terminated(reason)
        await self.shutdown_server()

    async def notify_terminated(self, reason="terminated"):
        """
        Notify the client that the debug adapter server is terminating.
        """
        if self._terminated_event.is_set():
            return
        else:
            self._terminated_event.set()
        if self.client_connected:
            await self.send_event(
                {
                    "event": "terminated",
                    "body": {reason: reason},
                }
            )

    async def handle_client(self, reader, writer):
        function_name = inspect.currentframe().f_code.co_name
        in_thread = "in thread" if threading.current_thread() == self.thread else "in main thread"
        if self.client_connected:
            logging.debug(
                f"[IPDB Server {function_name} {in_thread}] Client already connected, disconnecting old client"
            )
            self.disconnect_client()
        try:
            logging.info(f"[IPDB Server {function_name} {in_thread}] New client connection")
            self.client_reader = reader
            self.client_writer = writer
            self.debugger.clear_exited()
            while not self._shutdown_event.is_set():
                try:
                    self._read_dap_message_task = asyncio.create_task(
                        self.read_dap_message(reader)
                    )
                    msg = await self._read_dap_message_task
                    if (
                        self._shutdown_event.is_set()
                        or self._exited_event.is_set()
                        or self._terminated_event.is_set()
                    ):
                        logging.debug(
                            f"[IPDB Server {function_name} {in_thread}] Shutdown event set, closing client connection"
                        )
                        break
                except asyncio.CancelledError:
                    logging.debug(
                        f"[IPDB Server {function_name} {in_thread}] Read message cancelled, closing client connection"
                    )
                    break
                except Exception as e:
                    logging.error(
                        f"[IPDB Server {function_name} {in_thread}] Error reading message: {e}"
                    )
                    break
                if msg is None:
                    logging.info(f"[IPDB Server {function_name} {in_thread}] Client disconnected")
                    break
                response = {
                    "type": "response",
                    "seq": msg.get("seq", 0),
                    "request_seq": msg.get("seq", 0),
                    "success": True,
                    "command": msg.get("command", ""),
                }
                cmd = msg.get("command")
                if cmd == "initialize":
                    response["body"] = {"supportsConfigurationDoneRequest": True}
                elif cmd == "launch":
                    response["body"] = {}
                    await self.send_event({"event": "initialized", "body": {}})
                elif cmd == "continue":
                    logging.error(
                        f"[IPDB Server {function_name} {in_thread}] Continue commands can only be send through terminal"
                    )
                    response["success"] = False
                    response["message"] = "Continue commands can only be sent through terminal"
                elif cmd == "pause":
                    logging.error(
                        f"[IPDB Server {function_name} {in_thread}] Pause commands can only be send through terminal"
                    )
                    response["success"] = False
                    response["message"] = "Pause commands can only be sent through terminal"
                elif cmd == "stepIn":
                    logging.error(
                        f"[IPDB Server {function_name} {in_thread}] StepIn commands can only be send through terminal"
                    )
                    response["success"] = False
                    response["message"] = "StepIn commands can only be sent through terminal"
                elif cmd == "stepOut":
                    logging.error(
                        f"[IPDB Server {function_name} {in_thread}] StepOut commands can only be send through terminal"
                    )
                    response["success"] = False
                    response["message"] = "StepOut commands can only be sent through terminal"
                elif cmd == "next":
                    logging.error(
                        f"[IPDB Server {function_name} {in_thread}] Next commands can only be send through terminal"
                    )
                    response["success"] = False
                    response["message"] = "Next commands can only be sent through terminal"
                elif cmd == "configurationDone":
                    response["body"] = {}
                    await self.send_event(
                        {
                            "event": "stopped",
                            "body": {"reason": "entry", "threadId": 1, "allThreadsStopped": True},
                        }
                    )
                elif cmd == "threads":
                    response["body"] = {"threads": [{"id": 1, "name": "MainThread"}]}
                elif cmd == "stackTrace":
                    frames = []
                    if self.debugger.curframe:
                        f = self.debugger.curframe
                        i = 0
                        while f and i < 20:
                            code = f.f_code
                            frames.append(
                                {
                                    "id": i,
                                    "name": code.co_name,
                                    "line": f.f_lineno,
                                    "column": 1,
                                    "source": {"path": code.co_filename},
                                }
                            )
                            f = f.f_back
                            i += 1
                    response["body"] = {"stackFrames": frames, "totalFrames": len(frames)}
                elif cmd == "scopes":
                    frame_id = msg.get("arguments", {}).get("frameId", 0)
                    response["body"] = {
                        "scopes": [
                            {
                                "name": "Locals",
                                "variablesReference": 1000 + frame_id,
                                "expensive": False,
                            },
                            {
                                "name": "Globals",
                                "variablesReference": 2000 + frame_id,
                                "expensive": True,
                            },
                        ]
                    }
                elif cmd == "variables":
                    var_ref = msg.get("arguments", {}).get("variablesReference", 0)
                    frame = self.debugger.curframe
                    variables = []
                    if 1000 <= var_ref < 2000 and frame:
                        for k, v in frame.f_locals.items():
                            variables.append(
                                {"name": k, "value": repr(v), "variablesReference": 0}
                            )
                    elif var_ref >= 2000 and frame:
                        for k, v in frame.f_globals.items():
                            variables.append(
                                {"name": k, "value": repr(v), "variablesReference": 0}
                            )
                    response["body"] = {"variables": variables}
                elif cmd == "evaluate":
                    expr = msg.get("arguments", {}).get("expression", "")
                    try:
                        # Evaluate expression in ipdb debugger context
                        result = eval(
                            expr, self.debugger.curframe.f_globals, self.debugger.curframe.f_locals
                        )
                        response["body"] = {"result": str(result), "variablesReference": 0}
                    except Exception as e:
                        response["body"] = {"result": f"Error: {e}", "variablesReference": 0}
                elif cmd == "setBreakpoints":
                    args = msg.get("arguments", {})
                    source = args.get("source", {})
                    path = source.get("path", "")
                    breakpoints = args.get("breakpoints", [])
                    # Clear old breakpoints in the file
                    if path in self.debugger.get_all_breaks():
                        for bp_line in self.debugger.get_all_breaks()[path]:
                            self.debugger.clear_break(path, bp_line)
                    actual_bps = []
                    for bp in breakpoints:
                        line = bp.get("line")
                        if line:
                            self.debugger.set_break(path, line)
                            actual_bps.append({"verified": True, "line": line})
                    response["body"] = {"breakpoints": actual_bps}
                elif cmd == "setExceptionBreakpoints":
                    # You can store exception breakpoints info if needed or just acknowledge
                    response["body"] = {}
                    # For now, just acknowledge success; real implementation would configure exception breakpoints in debugger
                elif cmd == "source":
                    args = msg.get("arguments", {})
                    # For simplicity, handle only file path sources (no binary or compiled sources)
                    if "path" in args.get("source", {}):
                        path = args["source"]["path"]
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                content = f.read()
                            response["body"] = {"content": content}
                        except Exception as e:
                            response["success"] = False
                            response["message"] = f"Failed to read source: {e}"
                    else:
                        response["success"] = False
                        response["message"] = "Unsupported source reference"
                elif cmd == "disassemble":
                    logging.debug(
                        f"[IPDB Server {function_name} {in_thread}] Disassemble command received"
                    )
                    response["success"] = False
                    response["message"] = "Disassemble not supported in this debugger"
                elif cmd == "disconnect":
                    logging.info(
                        f"[IPDB Server {function_name} {in_thread}] Disconnect command recived"
                    )
                    response["success"] = True
                    response["message"] = "Disconnecting client"
                else:
                    logging.warning(
                        f"[IPDB Server {function_name} {in_thread}] Unsupported command: {cmd}"
                    )
                    response["success"] = False
                    response["message"] = f"Unsupported command: {cmd}"
                    logging.warning(
                        f"[IPDB Server {function_name} {in_thread}] Unsupported command: {cmd}"
                    )
                if (
                    self._shutdown_event.is_set()
                    or self._exited_event.is_set()
                    or self._terminated_event.is_set()
                ):
                    break
                if cmd == "disconnect":
                    break
                else:
                    writer.write(self.encode_dap_message(response))
                    await writer.drain()
                if (
                    self._shutdown_event.is_set()
                    or self._exited_event.is_set()
                    or self._terminated_event.is_set()
                ):
                    break
        finally:
            await self.disconnect_client()

    async def disconnect_client(self):
        if self.client_connected:
            self.client_writer.close()
            await self.client_writer.wait_closed()
            self.client_writer = None
            self.client_reader = None

    async def background_server(self):
        """
        Server logic is implemented as documented here:
        https://superfastpython.com/asyncio-server-background-task/#Example_of_Closing_Asyncio_Server_Safely_With_Context_Manager
        Particularly, we follow the example on how to do this with a context manager.
        """
        function_name = inspect.currentframe().f_code.co_name
        in_thread = "in thread" if threading.current_thread() == self.thread else "in main thread"
        if self.server is not None:
            msg = f"[IPDB Server {function_name} {in_thread}] Server is already running, cannot start again"
            logging.error(msg)
            raise RuntimeError(msg)
        if self._shutdown_event.is_set():
            self._shutdown_event.clear()
        if self._exited_event.is_set():
            self._exited_event.clear()
        if self._terminated_event.is_set():
            self._terminated_event.clear()
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        logging.info(
            f"[IPDB Server {function_name} {in_thread}] DAP server listening on {self.host}:{self.port}"
        )
        try:
            async with self.server:
                await self.server.serve_forever()
        finally:
            if self.server.is_serving():
                msg = "[IPDB Server {function_name} {in_thread}] DAP server is serving after closing it, cleanup failed"
                logging.error(msg)
                raise RuntimeError(msg)
            else:
                # TODO: is this the correct fix?
                self.server = None
                logging.info(
                    f"[IPDB Server {function_name} {in_thread}] DAP server stopped, and closed"
                )

    async def server_main(self):
        """
        Main entry point for the server, to be run in the event loop thread.

        We make the server with a task, cancelling the task, will automatically end the loop
        """
        function_name = inspect.currentframe().f_code.co_name
        in_thread = "in thread" if threading.current_thread() == self.thread else "in main thread"
        logging.debug(f"[IPDB Server {function_name} {in_thread}] Starting DAP server")
        if self.server_running:
            msg = f"[IPDB Server {function_name} {in_thread}] Server is already running, cannot start again"
            logging.error(msg)
            raise RuntimeError(msg)
        # start and run the server as a background task
        self.server_task = asyncio.create_task(self.background_server())
        # wait for the server to shutdown
        try:
            await self.server_task
        except asyncio.CancelledError:
            pass

    def shutdown(self):
        """
        Cleanup logic for the event loop started in start_in_thread.
        Shutdown the DAP server and the loop gracefully.
        """
        function_name = inspect.currentframe().f_code.co_name
        in_thread = "in thread" if threading.current_thread() == self.thread else "in main thread"
        if threading.current_thread() == self.thread:
            raise RuntimeError("Cannot shutdown server from within the event loop thread")
        logging.info(f"[IPDB Server {function_name} {in_thread}] Shutting down DAP server")
        # Handle case where there is no loop or loop is already closed
        if self.server_task is not None:
            asyncio.run_coroutine_threadsafe(self.shutdown_server(), self.runner._loop).result()
        if self.runner is None and (self.server is not None or self.server_task is not None):
            msg = f"[IPDB Server {function_name} {in_thread}] Event loop is None, but server is running, cannot shutdown"
            logging.error(msg)
            raise RuntimeError(msg)
        self.thread.join()
        if self.thread.is_alive():
            msg = f"[IPDB Server {function_name} {in_thread}] Event loop thread is still alive after closing the loop"
            logging.error(msg)
            raise RuntimeError(msg)
        else:
            self.thread = None
        logging.info(f"[IPDB Server {function_name} {in_thread}] DAP server shutdown completed")

    async def shutdown_server(self):
        """
        Shutdown the DAP server gracefully and notify the client if connected.
        To notify the client only once, we use a threading event `_shutdown_event`.
        """
        # Initialize
        function_name = inspect.currentframe().f_code.co_name
        in_thread = "in thread" if threading.current_thread() == self.thread else "in main thread"
        logging.info(f"[IPDB Server {function_name} {in_thread}] Shutting down DAP server")
        # Set the shutdown event to prevent multiple shutdown calls
        if not self._shutdown_event.is_set():
            self._shutdown_event.set()
            # Only notify the client once, we set the shutdown event afterwards
            if self.client_connected:
                await self.notify_terminated("shutdown")
        # Handle some edge cases
        if self.runner is not None:
            if self.server is None or self.server_task is None:
                logging.error(
                    f"[IPDB Server {function_name} {in_thread}] Event loop is None, cannot shutdown server"
                )
                raise RuntimeError("Event loop is not running, cannot shutdown server")
        else:
            return
        # Shutdown the server by cancelling the server task if it is not done
        if self.server_task is not None and not self.server_task.done():
            if self._read_dap_message_task is not None and not self._read_dap_message_task.done():
                self._read_dap_message_task.cancel()
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logging.error(
                    f"[IPDB Server {function_name} {in_thread}] Error while cancelling server task: {e}"
                )
                raise
            finally:
                self.server_task = None

    def run_loop(self):
        """
        Runs the event loop in a context manager
        """
        function_name = inspect.currentframe().f_code.co_name
        in_thread = "in thread" if threading.current_thread() == self.thread else "in main thread"
        try:
            with asyncio.Runner() as runner:
                self.runner = runner
                runner.run(self.server_main())
        except Exception as e:
            logging.error(f"[IPDB Server {function_name} {in_thread}] Event loop exception: {e}")
        finally:
            msg = "with" if self._shutdown_event.is_set() else "without"
            msg = f"Event loop stopping, {msg} shutdown event set"
            self.runner = None

    def start_in_thread(self, max_wait_time=5):
        self.thread = threading.Thread(target=self.run_loop, daemon=True)
        self.thread.start()
        t = time.time()
        dt = min(0.1, max_wait_time / 10)
        while t < time.time() + max_wait_time:
            try:
                server_running = self.server_running
            except RuntimeError as e:
                if "Inconsistent server state" in str(e):
                    time.sleep(dt)
                    continue
                else:
                    logging.error(f"[IPDB Server] Error checking server state: {e}")
                    raise
            if server_running:
                break
            else:
                time.sleep(dt)
                continue
        else:
            raise RuntimeError(
                f"[IPDB Server] DAP server did not start within {max_wait_time} seconds"
            )

    def set_trace(self, frame=None, on_continue="exit_without_breakpoint"):
        function_name = inspect.currentframe().f_code.co_name
        in_thread = "in thread" if threading.current_thread() == self.thread else "in main thread"
        self.on_continue = on_continue
        if not self.server:
            self.start_in_thread()
            self._shutdown_event.clear()
            self._exited_event.clear()
            self._terminated_event.clear()
        # Enter ipdb prompt here
        try:
            return self.debugger.set_trace(frame=frame)
        except Exception as e:
            logging.error(
                f"[IPDB Server {function_name} {in_thread}] Error of type {e.__class__.__name__} while setting trace: {e}"
            )
            raise


# Create singleton adapter
ipdab = IPDBAdapterServer()


def set_trace(on_continue="keep_running"):
    """
    Entry point to set trace in the IPDB adapter server.

    Note that the `pdb` debugger exits and removes its injected
    tracing mechanism from the interpreter if you choose continue
    and there are not further breakpoints defined.
    After this, the debugger can still re-enter if you call
    `set_trace` again. The on_continue parameter controls
    what happens with the `ipdab` debug server when you continue
    from a breakpoint.

    Parameters
    ----------
    on_continue : str (default="exit_without_breakpoint")
        Behavior when continuing from a breakpoint.
        Options are:
        - "exit_without_breakpoint": Exit the debugger on continue if no further breakpoints are set. Note `set_trace` calls do not count as breakpoints, in such cases the debug server will be reinitialized, and the clients needs to reconnect.
        - "exit": Exit the debug server even if there are break points set.
        - "keep_running": Keep the debug server running after continue, allowing future `set_trace` calls to re-enter the debugger.
    """
    frame = inspect.currentframe().f_back
    retval = ipdab.set_trace(frame=frame, on_continue=on_continue)
    return retval


def _at_exit_cleanup():
    """
    Cleanup logic, calls the ipdab.shutdown.
    Because the server runs in a daemon thread, this logical is called once the main thread exits.
    """
    ipdab.shutdown()


atexit.register(_at_exit_cleanup)

if __name__ == "__main__":
    # Simple example usage:
    import time

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    print("Starting debug adapter server...")
    ipdab.start_in_thread()

    print("Run your script and call set_trace() to debug.")
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting adapter server")
