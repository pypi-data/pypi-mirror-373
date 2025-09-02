from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import box
from getpass import getpass

class ConsoleManager:
    def __init__(self):
        self.console = Console()
        
    def print_logo(self):
        """Print the Djanbee ASCII logo with a bee"""
        logo = r"""
[#FF8800]    ____  _              [#f8f272] _                [/]
[#FF8800]   |  _ \(_) __ _ _ __   [#f8f272]| |__   ___  ___ [/]            | )/ )[/]
[#FF8800]   | | | | |/ _` | '_ \  [#f8f272]| '_ \ / _ \/ _ \ [/]        \\ |//,' [/]
[#FF8800]   | |_| | | (_| | | | | [#000000]| |_) |  __/  __/[/]        (")(_)-"()))=-[/]
[#FF8800]   |____/|_|\__,_|_| |_| [#f8f272]|_.__/ \___|\___|[/]           (\\ [/]
        [#FF8800]<__|[/]
          
        """
        
        self.console.print(Panel(
            logo,
            border_style="#f8f272",
            box=box.HEAVY,
            title="[yellow]Django Deployment Tool[/]",
            subtitle="[#f8f272]Bee-ploy fast — get ready honey![/]"
        ))
        
    def print_package(self, message):
        text = Text()
        text.append("📦 ", style="")  # Package emoji
        text.append(message, style="bright_blue")
        self.console.print(text, end="")


    def print_warning_critical(self, text: str):
        error_msg = Text(text, style="bold red")
        # Add a blank line before for margin
        self.console.print("")

        self.console.print(Panel(
            f"⛔ {text}",
            box=box.HEAVY,  # Heavy border
            border_style="red",  # Green border
            style="bold #F88379",  # Bold green text 
            padding=(1, 1),  # Minimal padding
            highlight=True  # Enable automatic highlighting of paths
        ))
        # Add a blank line after for margin
        self.console.print("")

    def print_warning(self, text: str):
        """Print warning message with warning emoji and yellow text"""
        # Create warning text with emoji
        text = f"⚠️  {text}"
        # Print in yellow without a panel
        self.console.print(text, style="yellow", highlight=True)

    def print_success(self, text: str):
        """Print success message with thumbs up icon and green text in a panel with highlighted paths"""
        # Add a blank line before for margin
        self.console.print("")
        
        # Use Rich's built-in highlighting
        self.console.print(Panel(
            f"👍 {text}",
            box=box.HEAVY,  # Heavy border
            border_style="green",  # Green border
            style="bold green",  # Bold green text 
            padding=(1, 1),  # Minimal padding
            highlight=True  # Enable automatic highlighting of paths
        ))
        
        # Add a blank line after for margin
        self.console.print("")

    def print_error(self, e: str):
        self.console.print(f"[red]Error: {str(e)}[/]")

    def print_lookup(self, message: str):
        """Print progress message in blue with hammer emoji"""
        text = Text()
        text.append("🔍 ", style="")  # Hammer emoji
        text.append(message, style="blue")
        
        self.console.print(text)

    def print_progress(self, message: str):
        """Print progress message in blue with hammer emoji"""
        text = Text()
        text.append("🔨 ", style="")  # Hammer emoji
        text.append(message, style="blue")
        
        self.console.print(text)

    def print_input(self, message: str):
        """Print progress message in blue with hammer emoji"""
        text = Text()
        text.append("📝 ", style="")  # Hammer emoji
        text.append(message, style="blue")
        
        self.console.print(text)

    def print_question(self, message: str):
        """Print question message in blue with question mark emoji and border"""
        text = Text()
        text.append("❓ ", style="")  # Question mark emoji
        text.append(message, style="blue")
        
        panel = Panel(
            text,
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)

    def print_step_progress(self, step_name: str, message: str)->None:
        text = Text()
        text.append("✅ ", style="") 
        text.append(f"{step_name}: {message}", style="green")
        self.console.print(text)


    def print_step_failure(self, step_name: str, message: str)->None:
        text = Text()
        text.append("❌ ", style="") 
        text.append(f"{step_name}: {message}", style="red")
        self.console.print(text)

    
    def input_profile(self) -> str:
        """Get profile input from user with styled prompt"""
        text = Text()
        text.append("👤 ", style="")
        text.append("Enter your profile name: ", style="bright_blue")
        self.console.print(text, end="")  # Using end="" to keep cursor on same line
        
        try:
            profile = input()
            if profile.strip():
                return profile
            else:
                self.print_step_failure("Profile", "Profile name cannot be empty")
                return self.input_profile()
        except Exception as e:
            self.print_error(str(e))
            return self.input_profile()

    def input_password(self, message="Enter your password: ") -> str:
        """Get password input from user with styled prompt"""
        text = Text()
        text.append("🔐 ", style="")
        text.append(message, style="bright_blue")
        self.console.print(text, end="")  # Using end="" to keep cursor on same line
        
        try:
            password = getpass(prompt="")  # Empty prompt since we already printed our styled one
            if password.strip():
                return password
            else:
                self.print_step_failure("Password", "Password cannot be empty")
                return self.input_password()
        except Exception as e:
            self.print_error(str(e))
            return self.input_password()
    
    def print_info(self, message):
        text = Text()
        text.append("ℹ️  ", style="")  
        text.append(message, style="blue")
        self.console.print(text)






