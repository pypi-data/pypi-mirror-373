"""Main CLI application entry point."""

import typer
from rich.console import Console
from rich.panel import Panel

from .server import create_app

app = typer.Typer(
    name="tsugu-uds",
    help="Tsugu User Data Server CLI",
    add_completion=False,
)

console = Console()


def version_callback(value: bool):
    """Show version information."""
    if value:
        from . import __version__
        console.print(f"Tsugu User Data Server version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(None, "--version", "-v", help="Show version information", callback=version_callback, is_eager=True),
):
    """Tsugu User Data Server CLI"""
    pass


@app.command("serve")
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(3001, "--port", "-p", help="Port to bind to"),
    log_level: str = typer.Option("info", "--log-level", "-l", help="Logging level (debug, info, warning, error)"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of worker processes"),
    direct_unbind: bool = typer.Option(False, "--direct-unbind", help="Enable direct unbind mode (skip Bestdori API verification)"),
    proxy: str = typer.Option("", "--proxy", help="Proxy URL for Bestdori API requests"),
):
    """Start the Tsugu User Data Server."""
    import subprocess
    import sys
    import os

    # Validate log level
    if log_level not in ["debug", "info", "warning", "error"]:
        console.print(f"[red]❌ Invalid log level: {log_level}[/red]")
        console.print("Supported levels: debug, info, warning, error")
        raise typer.Exit(1)

    # When debug log level is enabled, also enable dev mode for logging
    dev_mode = log_level == "debug"

    # Ensure data directory exists
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        console.print(f"📁 Created data directory: {data_dir}", style="blue")

    startup_info = f"""[bold green]🚀 Starting Tsugu User Data Server[/bold green]

• Host: [cyan]{host}[/cyan]
• Port: [cyan]{port}[/cyan]
• Log Level: [cyan]{log_level}[/cyan]
• Workers: [cyan]{workers}[/cyan]
• Direct Unbind: [cyan]{direct_unbind}[/cyan]
• Proxy: [cyan]{proxy if proxy else 'None'}[/cyan]

[bold yellow]Press Ctrl+C to stop[/bold yellow]"""

    panel = Panel(startup_info, title="Tsugu User Data Server", border_style="blue")
    console.print(panel)

    try:
        # Use uvicorn for ASGI
        # Set environment variable to pass log level to the app
        os.environ['TSUGU_UDS_LOG_LEVEL'] = log_level
        
        cmd = [
            sys.executable, "-m", "uvicorn",
            "tsugu_uds.server:create_app",
            "--factory",
            "--host", host,
            "--port", str(port),
            "--workers", str(workers),
            "--log-level", "error",  # Use error for uvicorn to minimize interference
            "--no-access-log"  # Disable access log to reduce noise
        ]
        if log_level == "debug":
            cmd.append("--reload")
        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]Server error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("run")
def run_from_config(
    config_file: str = typer.Argument("tsugu-uds-config.yml", help="Path to the YAML configuration file"),
):
    """Start the Tsugu User Data Server using a YAML configuration file."""
    import yaml
    import os
    import subprocess
    import sys

    if not os.path.exists(config_file):
        console.print(f"❌ Configuration file not found: {config_file}", style="red")
        console.print("💡 Use 'tsugu-uds config new' to generate a configuration file first, or use 'tsugu-uds serve' to start the server without a config")
        return

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Extract configuration
        server_config = config.get("server", {})
        db_config = config.get("database", {})

        host = server_config.get("host", "127.0.0.1")
        port = server_config.get("port", 3001)
        log_level = server_config.get("log_level", "info")
        direct_unbind = server_config.get("direct_unbind", False)
        proxy = server_config.get("proxy", "")
        database_path = db_config.get("path", "./data/user_v3.db")
        workers = server_config.get("workers", 1)

        # Ensure data directory exists
        data_dir = os.path.dirname(database_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
            console.print(f"📁 Created data directory: {data_dir}", style="blue")

        # Validate log level
        if log_level not in ["debug", "info", "warning", "error"]:
            console.print(f"[red]❌ Invalid log level: {log_level}[/red]")
            console.print("Supported levels: debug, info, warning, error")
            raise typer.Exit(1)

        # When debug log level is enabled, also enable dev mode for logging
        dev_mode = log_level == "debug"

        startup_info = f"""[bold green]🚀 Starting Tsugu User Data Server (from config)[/bold green]

• Config: [cyan]{config_file}[/cyan]
• Host: [cyan]{host}[/cyan]
• Port: [cyan]{port}[/cyan]
• Log Level: [cyan]{log_level}[/cyan]
• Workers: [cyan]{workers}[/cyan]
• Direct Unbind: [cyan]{direct_unbind}[/cyan]
• Proxy: [cyan]{proxy if proxy else 'None'}[/cyan]
• Database: [cyan]{database_path}[/cyan]

[bold yellow]Press Ctrl+C to stop[/bold yellow]"""

        panel = Panel(startup_info, title="Tsugu User Data Server", border_style="blue")
        console.print(panel)

        try:
            # Use uvicorn for ASGI
            # Set environment variable to pass log level to the app
            os.environ['TSUGU_UDS_LOG_LEVEL'] = log_level
            
            cmd = [
                sys.executable, "-m", "uvicorn",
                "tsugu_uds.server:create_app",
                "--factory",
                "--host", host,
                "--port", str(port),
                "--workers", str(workers),
                "--log-level", "error",  # Use error for uvicorn to minimize interference
                "--no-access-log"  # Disable access log to reduce noise
            ]
            if log_level == "debug":
                cmd.append("--reload")
            subprocess.run(cmd, check=True)

        except KeyboardInterrupt:
            console.print("\n[yellow]Server stopped[/yellow]")
        except subprocess.CalledProcessError as e:
            console.print(f"\n[red]Server error: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            raise typer.Exit(1)

    except yaml.YAMLError as e:
        console.print(f"❌ Failed to parse configuration file: {e}", style="red")
    except Exception as e:
        console.print(f"❌ Error loading configuration: {e}", style="red")
# Config command group
config_app = typer.Typer(help="Configuration management commands")
app.add_typer(config_app, name="config")


@config_app.command("new")
def config_new(
    output: str = typer.Option("tsugu-uds-config.yml", "--output", "-o", help="Output configuration file path"),
):
    """Generate a new YAML configuration file with default settings."""
    import yaml
    import os
    
    # Default configuration
    config = {
        "server": {
            "host": "127.0.0.1",
            "port": 3001,
            "debug": False,
            "workers": 1,
            "direct_unbind": False,
            "proxy": None,
        }
    }
    
    try:
        # Check if file already exists
        if os.path.exists(output):
            if not typer.confirm(f"Configuration file '{output}' already exists. Do you want to overwrite it?"):
                console.print("❌ Configuration file creation cancelled", style="yellow")
                return
        
        # Generate YAML with comments
        yaml_content = f"""# Tsugu User Data Server Configuration
# This file contains configuration settings for the Tsugu User Data Server

server:
  # Server host address (default: 127.0.0.1)
  host: 127.0.0.1
  
  # Server port number (default: 3001)
  port: 3001
  
  # Enable debug mode (also enables development mode)
  log_level: info
  
  # Number of worker processes (only used for ASGI servers)
  workers: 1
  
  # Enable direct unbind mode (skip Bestdori API verification for player unbinding)
  direct_unbind: false
  
  # Proxy URL for Bestdori API requests (optional)
  proxy: null
"""
        
        with open(output, 'w') as f:
            f.write(yaml_content)
        
        console.print(f"✅ Configuration file created: {output}", style="green")
    except Exception as e:
        console.print(f"❌ Failed to create configuration file: {e}", style="red")


@app.command("db")
def database_info(upgrade: bool = typer.Option(False, "--upgrade", help="Upgrade v2 database to v3 format and optimize storage")):
    """Show database information."""
    import os
    
    v2_db_path = "./data/user_v2.db"
    v3_db_path = "./data/user_v3.db"
    
    # Check database file existence
    v2_exists = os.path.exists(v2_db_path)
    v3_exists = os.path.exists(v3_db_path)
    
    if upgrade:
        # Execute upgrade functionality
        if not v2_exists:
            console.print("❌ No v2 database found to upgrade, Need 'user_v2.db' at './data/user_v2.db'", style="red")
            return
        
        console.print("🔄 Upgrading database...", style="blue")
        
        from .database import DatabaseManager
        import sqlite3
        
        db_manager = None
        try:
            # Initialize and migrate
            db_manager = DatabaseManager(v3_db_path)
            success = db_manager.migrate_v2_to_v3(v2_db_path)
            
            if success:
                # Optimize database
                console.print("🔧 Optimizing database...", style="cyan")
                with sqlite3.connect(v3_db_path) as conn:
                    conn.execute("VACUUM")
                
                console.print("✅ Upgrade completed successfully!", style="green")
            else:
                console.print("❌ Upgrade failed!", style="red")
                
        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style="red")
        finally:
            if db_manager:
                db_manager.close()
            console.print("🏁 Process finished", style="dim")
        return
    
    # Check for database info display
    if not v3_exists:
        console.print("❌ No v3 database found", style="red")
        if v2_exists:
            console.print("💡 v2 database found. Use 'tsugu-uds db --upgrade' to upgrade to v3 format", style="yellow")
        else:
            console.print("📁 Database directory is empty", style="dim")
        return
    
    # Original database info functionality
    from .database import DatabaseManager
    
    try:
        db = DatabaseManager("./data/user_v3.db")
        users = db.list_users()
        
        console.print(f"Database: ./data/user_v3.db")
        console.print(f"Total Users: {len(users)}")
        
        # Count by platform
        platforms = {}
        platform_bound_counts = {}
        total_bound = 0
        
        # Count users by number of bound players
        binding_counts = {}
        
        for user in users:
            platform = user["platform"]
            platforms[platform] = platforms.get(platform, 0) + 1
            
            # Check if user has bound players
            user_player_list = user.get("userPlayerList", [])
            player_count = len(user_player_list) if user_player_list else 0
            
            if player_count > 0:
                platform_bound_counts[platform] = platform_bound_counts.get(platform, 0) + 1
                total_bound += 1
                
                # Count by number of bound players
                binding_counts[player_count] = binding_counts.get(player_count, 0) + 1
        
        console.print(f"\n[bold]Player Binding Summary:[/bold]")
        console.print(f"Total users with bound players: {total_bound}")
        if len(users) > 0:
            bound_percentage = (total_bound / len(users)) * 100
            console.print(f"Binding rate: {bound_percentage:.1f}%")
        
        console.print("\n[bold]Binding Distribution:[/bold]")
        for count in sorted(binding_counts.keys()):
            user_count = binding_counts[count]
            console.print(f"Users with {count} bound player{'s' if count != 1 else ''}: {user_count}")
        
        console.print("\n[bold]Platform Statistics:[/bold]")
        for platform, count in platforms.items():
            bound_count = platform_bound_counts.get(platform, 0)
            if count > 0:
                bound_percentage = (bound_count / count) * 100
                console.print(f"{platform}: {count} users ({bound_count} bound, {bound_percentage:.1f}%)")
            else:
                console.print(f"{platform}: {count} users ({bound_count} bound)")
        
        db.close()
        
    except Exception as e:
        console.print(f"Database error: {e}", style="red")


if __name__ == "__main__":
    app()
