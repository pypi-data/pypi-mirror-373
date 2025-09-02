import click
from .commands import (
    LaunchContainer,
    SetupContainer,
    ConfigureContainer,
    DeployContainer,
    RunContainer
)
from .core import AppContainer


# Implementation functions that can be called directly
def setup_command():
    """Implementation of setup command logic."""
    app = AppContainer.get_instance()
    container = SetupContainer.create(app)
    container.manager.setup_project()
    
def configure_command(database=False, settings=False, path=""):
    """Implementation of configure command logic."""
    app = AppContainer.get_instance()
    container = ConfigureContainer.create(app)
    container.configure_project(database=database, settings=settings)
    
def deploy_command():
    """Implementation of deploy command logic."""
    app = AppContainer.get_instance()
    container = DeployContainer.create(app)
    
    # If package verification fails, stop the deployment process
    if not container.verify_packages():
        return False
    
    # If setting up socket file fails, stop the deployment process
    if not container.set_up_socket_file():
        return False
    
    # If setting up server configuration fails, stop the deployment process
    if not container.set_up_server():
        return False
        
    return True
    
def run_command(path=""):
    """Implementation of run command logic."""
    app = AppContainer.get_instance()
    container = RunContainer.create(app)
    container.run_django_setup(path)


# Click CLI commands that call the implementation functions
@click.group()
def cli():
    """Djanbee deployment tool"""
    pass


@cli.command()
@click.argument("path", default="")
def launch(path=""):
    """Launch Django server deployment"""
    try:
        app = AppContainer.get_instance()
        container = LaunchContainer.create(app)
        container.manager.launch_project(path)
        
        # Get selected commands
        commands = container.manager.select_launch_options()
        
        # Create a map to the implementation functions
        command_map = {
            "setup": setup_command,
            "configure": lambda: configure_command(database=True, settings=True, path=path),
            "deploy": deploy_command,
            "run": lambda: run_command(path)
        }
    
        # Execute each command
        for cmd in commands:
            app.console_manager.console.print(f"\nExecuting: {cmd}...")
            try:
                # Call the implementation function directly
                command_map[cmd]()
                app.console_manager.console.print(f"{cmd} completed successfully.", style="green")
            except Exception as e:
                app.console_manager.console.print(f"{cmd} failed: {str(e)}", style="red")
        
        app.console_manager.console.print("\nAll selected commands have been executed.", style="blue")

    except Exception as e:
        print(f"Error: {e}")


@cli.command()
def setup():
    """Setup Django project environment"""
    try:
        setup_command()
    except Exception as e:
        print(f"Error: {e}")


@cli.command()
@click.option("-s", "--settings", is_flag=True, help="Configure settings")
@click.option("-d", "--database", is_flag=True, help="Configure database")
@click.argument("path", default="")
def configure( settings: bool, database: bool, path: str):
    """Configure Django project and dependencies"""
    try:
        configure_command(database, settings, path)
    except Exception as e:
        print(f"Error {e}")


@cli.command()
def deploy():
    try:
        deploy_command()
    except Exception as e:
        print(f"Error {e}")


@cli.command()
@click.argument("path", default="")
def run(path: str):
    try:
        run_command(path)
    except Exception as e:
        print(f"Error {e}")


if __name__ == "__main__":
    cli()