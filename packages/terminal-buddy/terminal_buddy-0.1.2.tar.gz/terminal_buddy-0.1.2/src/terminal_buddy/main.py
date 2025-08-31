import typer
import socket
import threading
import os
import sys
import signal
import subprocess
import json
from terminal_buddy.utils.llm_functions import get_terminal_command
from terminal_buddy.utils.config import config


class TBuddyServer:
    """Server class for managing the Terminal Buddy server."""
    
    def __init__(self):
        self.host = ""
        self.port = 65432
        self.pid_file = "/tmp/tb_server.pid"
    
    def build_resources(self):
        """Build and return the resources needed for the server."""
        typer.echo("Building resources once…")
        from terminal_buddy.utils.example_selection import mmr_prompt_template
        return {
            "mmr_prompt_template": mmr_prompt_template
        }
    
    def handle_client(self, conn, addr):
        """Handle a client connection."""
        with conn:
            data = conn.recv(1024).decode()
            typer.echo(f"Query from {addr}: {data}")
            response = self.parse_request(data)
            conn.sendall(response.encode())
    
    def parse_request(self, request: str):
        """Parse a request and return a terminal command."""
        resources = self.build_resources()
        return get_terminal_command(user_query=request, mmr_prompt_template=resources["mmr_prompt_template"])
    
    def save_pid(self, pid: int):
        """Save the server PID to a file."""
        with open(self.pid_file, 'w') as f:
            json.dump({'pid': pid}, f)
    
    def load_pid(self) -> int:
        """Load the server PID from file."""
        try:
            with open(self.pid_file, 'r') as f:
                data = json.load(f)
                return data['pid']
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None
    
    def is_server_running(self) -> bool:
        """Check if the server is running."""
        pid = self.load_pid()
        if pid is None:
            return False
        
        try:
            # Check if process exists
            os.kill(pid, 0)
            # Check if it's listening on the expected port
            result = subprocess.run(['lsof', '-i', f':{self.port}'], capture_output=True, text=True)
            return str(pid) in result.stdout
        except OSError:
            return False
    
    def run_server(self):
        """Run the server in the main loop."""
        resources = self.build_resources()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            typer.echo(f"Server running on 127.0.0.1:{self.port}")
            while True:
                conn, addr = s.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
    
    def start(self, daemonize: bool = True):
        """Start the server."""
        # Check if server is already running
        if self.is_server_running():
            pid = self.load_pid()
            typer.echo(f"❌ Server is already running (PID: {pid})")
            typer.echo("Use 'tb server down' to stop the current server first.")
            return
        
        if daemonize:
            typer.echo("Starting server in background mode...")
            typer.echo("Note: Server may take 10-20 seconds to fully initialize due to resource loading.")
            # Start the server in a background process
            process = subprocess.Popen([sys.executable, __file__, "server", "up", "--no-daemonize"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL,
                            start_new_session=True)
            # Don't save PID immediately - let the server process save its own PID
            typer.echo(f"Server starting in background. Use 'tb server up --no-daemonize' to run in foreground.")
            typer.echo("Use 'tb server status' to check when the server is ready.")
        else:
            typer.echo("Starting server in foreground mode...")
            typer.echo("Note: Server may take 10-20 seconds to fully initialize due to resource loading.")
            # Save our own PID since we're running the server directly
            self.save_pid(os.getpid())
            self.run_server()
    
    def stop(self):
        """Stop the running server."""
        if not self.is_server_running():
            typer.echo("No server is currently running.")
            return
        
        pid = self.load_pid()
        if pid is None:
            typer.echo("Could not find server PID file.")
            return
        
        try:
            # Try graceful shutdown first
            os.kill(pid, signal.SIGTERM)
            typer.echo(f"Sent SIGTERM to server (PID: {pid}). Waiting for graceful shutdown...")
            
            # Wait a bit for graceful shutdown
            import time
            time.sleep(2)
            
            # Check if process is still running
            try:
                os.kill(pid, 0)
                # Process still running, force kill
                typer.echo("Server did not shut down gracefully. Force killing...")
                os.kill(pid, signal.SIGKILL)
            except OSError:
                # Process already terminated
                pass
            
            # Clean up PID file
            try:
                os.remove(self.pid_file)
            except FileNotFoundError:
                pass
            
            typer.echo("Server stopped successfully.")
            
        except OSError as e:
            typer.echo(f"Error stopping server: {e}")
            # Clean up PID file if process doesn't exist
            try:
                os.remove(self.pid_file)
            except FileNotFoundError:
                pass
    
    def status(self):
        """Check the status of the server."""
        pid = self.load_pid()
        
        if pid is None:
            typer.echo("❌ Server is not running")
            return
        
        # Check if process exists
        try:
            os.kill(pid, 0)
        except OSError:
            typer.echo("❌ Server process not found (may have crashed)")
            return
        
        # Check if it's listening on the expected port
        try:
            result = subprocess.run(['lsof', '-i', f':{self.port}'], capture_output=True, text=True)
            if str(pid) in result.stdout:
                typer.echo(f"✅ Server is running and ready (PID: {pid})")
                typer.echo(f"   Listening on: 127.0.0.1:{self.port}")
            else:
                typer.echo(f"⏳ Server is starting up (PID: {pid})")
                typer.echo("   Still loading resources... (this may take 10-20 seconds)")
        except Exception:
            typer.echo(f"⏳ Server is starting up (PID: {pid})")
            typer.echo("   Still loading resources... (this may take 10-20 seconds)")


# Create a global server instance
server = TBuddyServer()

# Create the main Typer app
app = typer.Typer()

# Create the server sub-app
server_app = typer.Typer()

config_app = typer.Typer()
config 


@config_app.command()
def show():
    """Show current configuration."""
    typer.echo("Current Configuration:")
    typer.echo(f"  LLM Model: {config.OLLAMA_MODEL_NAME}")
    typer.echo(f"  Embeddings Model: {config.OLLAMA_EMBEDDINGS_MODEL_NAME}")
    typer.echo(f"  Examples Path: {config.EXAMPLES_JSON_PATH}")
    typer.echo(f"  Examples Full Path: {config.get_examples_path()}")


@config_app.command()
def set_llm_model(model_name: str = typer.Argument(..., help="Name of the LLM model")):
    """Set the LLM model name."""
    old_model = config.OLLAMA_MODEL_NAME
    config.update_llm_model(model_name)
    typer.echo(f"✅ LLM model updated: {old_model} → {model_name}")


@config_app.command()
def set_embeddings_model(model_name: str = typer.Argument(..., help="Name of the embeddings model")):
    """Set the embeddings model name."""
    old_model = config.OLLAMA_EMBEDDINGS_MODEL_NAME
    config.update_embeddings_model(model_name)
    typer.echo(f"✅ Embeddings model updated: {old_model} → {model_name}")


@config_app.command()
def set_examples_path(path: str = typer.Argument(..., help="Path to the examples JSON file")):
    """Set the examples JSON file path."""
    old_path = config.EXAMPLES_JSON_PATH
    config.update_examples_path(path)
    typer.echo(f"✅ Examples path updated: {old_path} → {path}")
    typer.echo(f"  Full path: {config.get_examples_path()}")


@server_app.command()
def up(
    daemonize: bool = typer.Option(True, "--daemonize/--no-daemonize", "-d/-n", help="Run in background as a daemon (default: daemonize)")
):
    """Start the server."""
    server.start(daemonize=daemonize)


@server_app.command()
def down():
    """Stop the server."""
    server.stop()


@server_app.command()
def status():
    """Check server status."""
    server.status()


@app.command()
def query(query_text: str = typer.Argument(..., help="Query to process")):
    """Process a query and return a terminal command."""
    # Check if server is running and ready
    if server.is_server_running():
        # Send query to the running server
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', server.port))
                s.sendall(query_text.encode())
                response = s.recv(1024).decode().strip()
                typer.echo(response)
        except Exception as e:
            typer.echo(f"Error connecting to server: {e}")
            typer.echo("Falling back to local processing...")
            command = server.parse_request(query_text)
            typer.echo(command)
    else:
        # Server not running, process locally
        typer.echo("Server not running. Processing query locally...")
        command = server.parse_request(query_text)
        typer.echo(command)


# Add the server sub-app to the main app
app.add_typer(server_app, name="server", help="Server management commands")

# Add the config sub-app to the main app
app.add_typer(config_app, name="config", help="Configuration management commands")


@app.callback()
def default_entrypoint(ctx: typer.Context):
    """
    Terminal Buddy - AI-powered terminal command generator.
    
    Use 'tb query "your query"' to get a terminal command, or use 'tb server' for server management.
    """
    if not ctx.invoked_subcommand:
        typer.echo(ctx.get_help())


# --- Poetry entrypoint ---
def main():
    app()


if __name__ == "__main__":
    main()
