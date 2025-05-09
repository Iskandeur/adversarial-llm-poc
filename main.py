#!/usr/bin/env python3

import json
import sys
import time
import threading
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from pyfiglet import Figlet
from colorama import Fore, Style

from translator import Translator
from api_client import GeminiClient

class IloIke:
    def __init__(self):
        """Initialize the ilo-ike CLI tool."""
        # Load configuration
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        
        # CLI settings
        self.prompt = self.config['cli']['prompt']
        self.welcome_message = self.config['cli']['welcome_message']
        self.exit_commands = self.config['cli']['exit_commands']
        self.debug_commands = self.config['cli']['debug_commands']
        self.debug_mode = self.config['cli']['debug_mode']
        
        # Initialize components - pass debug_mode to them
        self.translator = Translator(debug=self.debug_mode)
        self.gemini_client = GeminiClient(debug=self.debug_mode)
        self.console = Console()
        
        # For loading animation
        self.is_processing = False
        self.spinner_thread = None
    
    def display_welcome(self):
        """Display a welcome message when the application starts."""
        f = Figlet(font='slant')
        title = f.renderText('ilo-ike')
        
        print(Fore.CYAN + title + Style.RESET_ALL)
        print(Fore.WHITE + self.welcome_message + Style.RESET_ALL)
        if self.debug_mode:
            print(Fore.YELLOW + "[DEBUG MODE ENABLED]" + Style.RESET_ALL)
        print()
    
    def display_debug(self, title, content, language=None):
        """Display debug information in a nicely formatted panel."""
        if not self.debug_mode:
            return
        
        if language:
            syntax = Syntax(content, language, theme="monokai", line_numbers=True)
            self.console.print(Panel(syntax, title=f"[bold yellow]{title}[/bold yellow]", border_style="yellow"))
        else:
            self.console.print(Panel(content, title=f"[bold yellow]{title}[/bold yellow]", border_style="yellow"))
        
        # Add a short pause to make the debug info easier to read
        time.sleep(0.5)
    
    def show_loading_animation(self):
        """Display a loading animation while processing is happening."""
        spinner = Spinner("dots", text="Thinking...")
        with Live(spinner, refresh_per_second=10, console=self.console) as live:
            while self.is_processing:
                time.sleep(0.1)
    
    def start_loading_animation(self):
        """Start the loading animation in a separate thread."""
        self.is_processing = True
        self.spinner_thread = threading.Thread(target=self.show_loading_animation)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
    
    def stop_loading_animation(self):
        """Stop the loading animation."""
        self.is_processing = False
        if self.spinner_thread:
            self.spinner_thread.join(timeout=1.0)
    
    def handle_query(self, query):
        """Process a user query and return a response."""
        # Convert the query to leetspeak
        leetspeak_query = self.translator.to_leetspeak(query)
        self.display_debug("Original Query", query)
        self.display_debug("Leetspeak Query", leetspeak_query)
        
        # Create the prompt for Gemini
        prompt = self.gemini_client.create_prompt(leetspeak_query)
        self.display_debug("Full Prompt", prompt, "xml")
        
        # Get response from Gemini
        self.display_debug("Sending Request to Gemini...", f"Using model: {self.gemini_client.model}")
        response = self.gemini_client.generate_content(prompt)
        self.display_debug("Raw Gemini Response", response, "markdown")
        
        # Process the response (extract and decode)
        decoded_content = self.translator.process_response(response)
        self.display_debug("Decoded Response", decoded_content)
        
        return decoded_content
    
    def toggle_debug_mode(self, command):
        """Toggle debug mode on or off."""
        if command == "debug on":
            self.debug_mode = True
            # Update debug mode in components
            self.translator.set_debug(True)
            self.gemini_client.set_debug(True)
            return "[bold green]Debug mode enabled[/bold green]"
        elif command == "debug off":
            self.debug_mode = False
            # Update debug mode in components
            self.translator.set_debug(False)
            self.gemini_client.set_debug(False)
            return "[bold green]Debug mode disabled[/bold green]"
        return None
    
    def run_cli(self):
        """Run the CLI interface."""
        self.display_welcome()
        
        while True:
            try:
                # Get user input
                user_input = input(self.prompt)
                
                # Check for exit command
                if user_input.lower() in self.exit_commands:
                    print("Goodbye!")
                    break
                
                # Check for debug commands
                debug_response = None
                if user_input.lower() in self.debug_commands:
                    debug_response = self.toggle_debug_mode(user_input.lower())
                    self.console.print(debug_response)
                    continue
                
                # Show typing animation only in debug mode
                if self.debug_mode:
                    self.console.print("[bold cyan]Thinking...[/bold cyan]")
                else:
                    # Start a loading animation for non-debug mode
                    self.start_loading_animation()
                
                # Process the query
                response = self.handle_query(user_input)
                
                # Stop loading animation if it was started
                if not self.debug_mode:
                    self.stop_loading_animation()
                    # Clear the line after stopping the animation
                    print("\r" + " " * 50 + "\r", end="")
                
                # Display the response
                print()
                self.console.print(Markdown(response))
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            
            except Exception as e:
                # Stop loading animation if it was started
                if not self.debug_mode:
                    self.stop_loading_animation()
                
                self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
                if self.debug_mode:
                    import traceback
                    self.console.print(Panel(traceback.format_exc(), title="[bold red]Stack Trace[/bold red]", border_style="red"))

if __name__ == "__main__":
    app = IloIke()
    app.run_cli() 