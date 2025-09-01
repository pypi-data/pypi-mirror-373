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
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode (also enables development mode)"),
    direct_unbind: bool = typer.Option(False, "--direct-unbind", help="Enable direct unbind mode (skip Bestdori API verification)"),
    proxy: str = typer.Option("", "--proxy", help="Proxy URL for Bestdori API requests"),
):
    """Start the Guga server with Quart."""
    # When debug is enabled, also enable dev mode
    dev_mode = debug
    
    # Ensure data directory exists
    import os
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        console.print(f"📁 Created data directory: {data_dir}", style="blue")
    
    startup_info = f"""[bold green]🚀 Starting Tsugu User Data Server[/bold green]

• Host: [cyan]{host}[/cyan]
• Port: [cyan]{port}[/cyan]
• Debug: [cyan]{debug}[/cyan]
• Direct Unbind: [cyan]{direct_unbind}[/cyan]
• Proxy: [cyan]{proxy if proxy else 'None'}[/cyan]

[bold yellow]Press Ctrl+C to stop[/bold yellow]"""
    
    panel = Panel(startup_info, title="Tsugu User Data Server", border_style="blue")
    console.print(panel)
    
    try:
        quart_app = create_app("./data/user_v3.db", dev_mode=dev_mode, direct_unbind=direct_unbind, proxy=proxy)
        quart_app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
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
    
    if not os.path.exists(config_file):
        console.print(f"❌ Configuration file not found: {config_file}", style="red")
        console.print("💡 Use 'tsugu-uds config' to generate a configuration file first, or use 'tsugu-uds serve' to start the server without a config")
        return
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Extract configuration
        server_config = config.get("server", {})
        db_config = config.get("database", {})
        
        host = server_config.get("host", "127.0.0.1")
        port = server_config.get("port", 3001)
        debug = server_config.get("debug", False)
        direct_unbind = server_config.get("direct_unbind", False)
        proxy = server_config.get("proxy", "")
        database_path = db_config.get("path", "./data/user_v3.db")
        
        # Ensure data directory exists
        data_dir = os.path.dirname(database_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
            console.print(f"📁 Created data directory: {data_dir}", style="blue")
        
        # When debug is enabled, also enable dev mode
        dev_mode = debug
        
        startup_info = f"""[bold green]🚀 Starting Tsugu User Data Server (from config)[/bold green]

• Config: [cyan]{config_file}[/cyan]
• Host: [cyan]{host}[/cyan]
• Port: [cyan]{port}[/cyan]
• Debug: [cyan]{debug}[/cyan]
• Direct Unbind: [cyan]{direct_unbind}[/cyan]
• Proxy: [cyan]{proxy if proxy else 'None'}[/cyan]
• Database: [cyan]{database_path}[/cyan]

[bold yellow]Press Ctrl+C to stop[/bold yellow]"""
        
        panel = Panel(startup_info, title="Tsugu User Data Server", border_style="blue")
        console.print(panel)
        
        try:
            quart_app = create_app(database_path, dev_mode=dev_mode, direct_unbind=direct_unbind, proxy=proxy)
            quart_app.run(host=host, port=port, debug=debug)
        except KeyboardInterrupt:
            console.print("\n[yellow]Server stopped[/yellow]")
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
    host: str = typer.Option("127.0.0.1", help="Server host"),
    port: int = typer.Option(3001, help="Server port"),
    debug: bool = typer.Option(False, help="Enable debug mode"),
    direct_unbind: bool = typer.Option(False, help="Enable direct unbind mode"),
    proxy: str = typer.Option("", help="Proxy URL"),
):
    """Generate a new YAML configuration file."""
    import yaml
    import os
    
    config = {
        "server": {
            "host": host,
            "port": port,
            "debug": debug,
            "direct_unbind": direct_unbind,
            "proxy": proxy if proxy else None,
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
  host: {host}
  
  # Server port number (default: 3001)
  port: {port}
  
  # Enable debug mode (also enables development mode)
  debug: {str(debug).lower()}
  
  # Enable direct unbind mode (skip Bestdori API verification for player unbinding)
  direct_unbind: {str(direct_unbind).lower()}
  
  # Proxy URL for Bestdori API requests (optional)
  proxy: {proxy if proxy else 'null'}
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
