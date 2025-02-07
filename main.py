import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import platform
import signal
import subprocess
import shlex

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_terminal():
    return FileResponse("static/index.html")

class TerminalManager:
    def __init__(self):
        self.terminals = {}

    def get_shell_command(self):
        """Get appropriate shell command based on platform"""
        if platform.system() == 'Windows':
            return ['powershell.exe', '-NoLogo']
        else:
            shell = os.environ.get('SHELL', '/bin/bash')
            return [shell]

    async def create_terminal(self, cols=80, rows=24):
        env = os.environ.copy()
        env['COLUMNS'] = str(cols)
        env['LINES'] = str(rows)
        
        # Get shell command for current platform
        shell_cmd = self.get_shell_command()
        
        if platform.system() == 'Windows':
            # For Windows, use ConPTY for better terminal handling
            process = subprocess.Popen(
                shell_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                bufsize=0,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            # For Unix-like systems, use proper PTY
            import pty
            import termios
            import fcntl
            import struct
            
            # Create PTY
            primary, secondary = pty.openpty()
            
            # Set terminal size
            size = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(secondary, termios.TIOCSWINSZ, size)
            
            process = subprocess.Popen(
                shell_cmd,
                stdin=secondary,
                stdout=secondary,
                stderr=secondary,
                env=env,
                preexec_fn=os.setsid,
                universal_newlines=True
            )
            
            os.close(secondary)
            self.primary = primary
            
        return process

    async def read_output(self, process, primary=None):
        if platform.system() == 'Windows':
            return await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: process.stdout.read(1)
            )
        else:
            return await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: os.read(primary, 1024).decode()
            )

    async def write_input(self, process, data, primary=None):
        try:
            if platform.system() == 'Windows':
                if data == '\b':  # Backspace
                    # Send backspace sequence: move back, write space, move back again
                    process.stdin.write('\x08 \x08')
                else:
                    process.stdin.write(data)
                process.stdin.flush()
            else:
                if data == '\b':  # Backspace
                    # Send backspace sequence: move back, write space, move back again
                    os.write(primary, '\x08 \x08'.encode())
                else:
                    os.write(primary, data.encode())
        except Exception as e:
            print(f"Error writing to terminal: {e}")

    async def handle_terminal(self, websocket: WebSocket, terminal_id: str):
        await websocket.accept()
        
        try:
            # Get initial terminal size from client
            data = await websocket.receive_text()
            try:
                size_data = json.loads(data)
                cols = min(size_data.get('cols', 80), 160)  # Limit width to prevent errors
                rows = size_data.get('rows', 24)
            except:
                cols, rows = 80, 24

            process = await self.create_terminal(cols, rows)
            self.terminals[terminal_id] = process
            primary = getattr(self, 'primary', None)

            async def send_output():
                buffer = ""
                while True:
                    try:
                        output = await self.read_output(process, primary)
                        if not output:
                            break
                        await websocket.send_text(output)
                    except Exception as e:
                        print(f"Error reading output: {e}")
                        break

            # Start reading output
            output_task = asyncio.create_task(send_output())

            while True:
                try:
                    data = await websocket.receive_text()
                    
                    try:
                        # Check if it's a resize message
                        msg = json.loads(data)
                        if msg.get('type') == 'resize':
                            continue
                    except json.JSONDecodeError:
                        # Regular input
                        if data == '\x03':  # Ctrl+C
                            if platform.system() == 'Windows':
                                process.send_signal(signal.CTRL_C_EVENT)
                            else:
                                process.send_signal(signal.SIGINT)
                        elif data == '\x04':  # Ctrl+D
                            break
                        else:
                            await self.write_input(process, data, primary)

                except WebSocketDisconnect:
                    break
                except Exception as e:
                    print(f"Error handling websocket: {e}")
                    break

        finally:
            if terminal_id in self.terminals:
                process = self.terminals[terminal_id]
                try:
                    if platform.system() == 'Windows':
                        process.terminate()
                    else:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=1)
                except:
                    if platform.system() == 'Windows':
                        process.kill()
                    else:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                del self.terminals[terminal_id]
                if hasattr(self, 'primary'):
                    os.close(self.primary)

terminal_manager = TerminalManager()

@app.websocket("/ws/{terminal_id}")
async def websocket_endpoint(websocket: WebSocket, terminal_id: str):
    await terminal_manager.handle_terminal(websocket, terminal_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
