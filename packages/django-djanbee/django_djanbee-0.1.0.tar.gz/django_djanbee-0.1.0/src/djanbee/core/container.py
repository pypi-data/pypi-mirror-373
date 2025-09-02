from dataclasses import dataclass
from typing import Optional
from ..managers import (
    OSManager,
    DjangoManager,
    ConsoleManager,
    DatabaseManager,
    ServerManager,
    SocketManager,
    EnvManager,
    DotenvManager,
)


@dataclass
class AppContainer:
    """Singleton container for shared tools"""

    os_manager: "OSManager"
    django_manager: "DjangoManager"
    console_manager: "ConsoleManager"
    database_manager: "DatabaseManager"
    server_manager: "ServerManager"
    socket_manager: "SocketManager"
    env_manager: "EnvManager"
    dotenv_manager: "DotenvManager"

    _instance: Optional["AppContainer"] = None

    @classmethod
    def get_instance(cls) -> "AppContainer":
        if cls._instance is None:
            os_manager = OSManager()
            console_manager = ConsoleManager()
            
            # Create the environment manager first
            env_manager = EnvManager(os_manager, console_manager)
            
            # Create dotenv manager
            dotenv_manager = DotenvManager(os_manager, console_manager)
            
            # Pass env_manager and dotenv_manager to django_manager
            django_manager = DjangoManager(os_manager, console_manager, env_manager, dotenv_manager)
            
            cls._instance = cls(
                os_manager=os_manager,
                console_manager=console_manager,
                django_manager=django_manager,
                database_manager=DatabaseManager(os_manager, console_manager, env_manager),
                server_manager=ServerManager(
                    os_manager, console_manager, django_manager
                ),
                socket_manager=SocketManager(
                    os_manager, console_manager, django_manager
                ),
                env_manager=env_manager,
                dotenv_manager=dotenv_manager,
            )
        return cls._instance
