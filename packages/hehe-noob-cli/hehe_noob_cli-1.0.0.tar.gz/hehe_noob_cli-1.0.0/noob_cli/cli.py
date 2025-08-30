#!/usr/bin/env python3
"""
HeHe Noob CLI - A command-line interface for Noobs
"""

import os
import sys
import json
import re
from pathlib import Path
import google.generativeai as genai
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.syntax import Syntax
import argparse

class HeHeNoobCLI:
    def __init__(self, api_key=None, model="gemini-2.0-flash-exp"):
        self.console = Console()
        self.model_name = model
        self.conversation_history = []
        
        # Configure HeHe Noob API
        if api_key:
            genai.configure(api_key=api_key)
        else:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                api_key = self.prompt_for_api_key()
            genai.configure(api_key=api_key)
        
        try:
            self.model = genai.GenerativeModel(model)
            self.chat = self.model.start_chat(history=[])
        except Exception as e:
            self.console.print(f"❌ [red]Error initializing HeHe Noob model: {e}[/red]")
            if "API_KEY" in str(e) or "authentication" in str(e).lower():
                self.console.print("[yellow]It seems your API key is invalid. Let's try again.[/yellow]")
                api_key = self.prompt_for_api_key()
                genai.configure(api_key=api_key)
                try:
                    self.model = genai.GenerativeModel(model)
                    self.chat = self.model.start_chat(history=[])
                except Exception as e2:
                    self.console.print(f"❌ [red]Still unable to initialize: {e2}[/red]")
                    sys.exit(1)
            else:
                 sys.exit(1)

    def prompt_for_api_key(self):
        """Prompt user for API key interactively"""
        self.console.print("\n[bold yellow]🔑 HeHe Noob needs your API key to work![/bold yellow]")
        self.console.print("Get your free API key from: [link]https://makersuite.google.com/app/apikey[/link]")
        
        while True:
            api_key = Prompt.ask(
                "\n[bold green]Enter your Gemini API key[/bold green]",
                password=True
            )
            
            if api_key and len(api_key.strip()) > 10:  # Basic validation
                return api_key.strip()
            else:
                self.console.print("[red]❌ Invalid API key. Please try again.[/red]")
                retry = Prompt.ask(
                    "Would you like to try again?",
                    choices=["y", "n", "yes", "no"],
                    default="y"
                )
                if retry.lower() in ['n', 'no']:
                    self.console.print("[yellow]👋 Goodbye! Come back when you have your API key.[/yellow]")
                    sys.exit(0)

    def display_ascii_logo(self):
        """Display the HeHe Noob ASCII logo"""
        logo = """
[cyan]██   ██ ███████ ██   ██ ███████[/cyan] [magenta]███    ██  ██████   ██████  ██████[/magenta]
[cyan]██   ██ ██      ██   ██ ██     [/cyan] [magenta]████   ██ ██    ██ ██    ██ ██   ██[/magenta]
[cyan]███████ █████   ███████ █████  [/cyan] [magenta]██ ██  ██ ██    ██ ██    ██ ██████[/magenta]
[cyan]██   ██ ██      ██   ██ ██     [/cyan] [magenta]██  ██ ██ ██    ██ ██    ██ ██   ██[/magenta]
[cyan]██   ██ ███████ ██   ██ ███████[/cyan] [magenta]██   ████  ██████   ██████  ██████[/magenta]

[bold yellow]🤖 Your Friendly AI Assistant with a Sense of Humor! 😄[/bold yellow]
        """
        self.console.print(logo)
        self.console.print()

    def display_tips(self):
        """Display startup tips"""
        tips = """[bold]Tips for getting started:[/bold]
1. Ask questions, edit files, or run commands.
2. Be specific for the best results.
3. Create HEHE.md files to customize your interactions with HeHe Noob.
4. /help for more information."""
        
        self.console.print(tips)
        self.console.print()

    def display_status(self):
        """Display current status"""
        current_dir = Path.cwd().name
        status_text = f"no sandbox (see /docs)                    {self.model_name}"
        self.console.print(f"[dim]~                          {current_dir}                          {status_text}[/dim]")
        self.console.print()

    def extract_code_blocks(self, text):
        """Extract code blocks from markdown text"""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for language, code in matches:
            if not language:
                language = 'text'
            code_blocks.append({
                'language': language,
                'code': code.strip(),
                'full_block': f"```{language}\n{code.strip()}\n```"
            })
        
        return code_blocks

    def create_file(self, filename, content, language=''):
        """Create a file with the given content"""
        try:
            # Ensure the directory exists
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.console.print(f"✅ [green]Created file: {filename}[/green]")
            return True
        except Exception as e:
            self.console.print(f"❌ [red]Error creating file {filename}: {e}[/red]")
            return False

    def process_response(self, response_text):
        """Process the AI response and handle file creation"""
        # Display the response
        try:
            markdown = Markdown(response_text)
            self.console.print(Panel(markdown, title="[bold cyan]HeHe Noob Response[/bold cyan]", border_style="cyan"))
        except:
            # Fallback if markdown parsing fails
            self.console.print(Panel(response_text, title="[bold cyan]HeHe Noob Response[/bold cyan]", border_style="cyan"))
        
        # Extract and offer to save code blocks
        code_blocks = self.extract_code_blocks(response_text)
        
        if code_blocks:
            self.console.print(f"\n[yellow]Found {len(code_blocks)} code block(s). Would you like to save any as files?[/yellow]")
            
            for i, block in enumerate(code_blocks):
                self.console.print(f"\n[bold]Code Block {i+1} ({block['language']}):[/bold]")
                syntax = Syntax(block['code'], block['language'], theme="monokai", line_numbers=True)
                self.console.print(syntax)
                
                save_choice = Prompt.ask(
                    f"Save this {block['language']} code to a file?",
                    choices=["y", "n", "yes", "no"],
                    default="n"
                )
                
                if save_choice.lower() in ['y', 'yes']:
                    # Suggest a filename based on language
                    extensions = {
                        'python': '.py',
                        'javascript': '.js',
                        'typescript': '.ts',
                        'html': '.html',
                        'css': '.css',
                        'java': '.java',
                        'cpp': '.cpp',
                        'c': '.c',
                        'go': '.go',
                        'rust': '.rs',
                        'php': '.php',
                        'ruby': '.rb',
                        'bash': '.sh',
                        'sql': '.sql',
                        'json': '.json',
                        'yaml': '.yaml',
                        'xml': '.xml'
                    }
                    
                    default_ext = extensions.get(block['language'].lower(), '.txt')
                    default_name = f"gemini_code_{i+1}{default_ext}"
                    
                    filename = Prompt.ask(
                        "Enter filename",
                        default=default_name
                    )
                    
                    self.create_file(filename, block['code'], block['language'])

    def handle_command(self, user_input):
        """Handle special commands"""
        if user_input.startswith('/'):
            command = user_input[1:].strip().lower()
            
            if command == 'help':
                help_text = """[bold cyan]HeHe Noob CLI Commands:[/bold cyan]

[bold]Basic Commands:[/bold]
• /help - Show this help message
• /clear - Clear conversation history
• /exit or /quit - Exit the CLI
• /status - Show current status
• /history - Show conversation history

[bold]File Operations:[/bold]
• /create <filename> - Create a new file interactively
• /read <filename> - Read and display a file
• /list - List files in current directory

[bold]Tips:[/bold]
• Ask HeHe Noob to create code and it will offer to save it as files
• Be specific about what you want to build
• Mention file types, frameworks, or languages for better results
• You can continue conversations across multiple inputs
"""
                self.console.print(Panel(help_text, title="Help", border_style="green"))
                return True
            
            elif command == 'clear':
                self.chat = self.model.start_chat(history=[])
                self.conversation_history = []
                self.console.clear()
                self.display_ascii_logo()
                self.console.print("✅ [green]Conversation history cleared[/green]")
                return True
            
            elif command in ['exit', 'quit']:
                self.console.print("👋 [yellow]Thanks for using HeHe Noob CLI![/yellow]")
                return False
            
            elif command == 'status':
                self.display_status()
                current_dir = os.getcwd()
                file_count = len([f for f in os.listdir('.') if os.path.isfile(f)])
                self.console.print(f"📁 Current directory: {current_dir}")
                self.console.print(f"📄 Files in directory: {file_count}")
                self.console.print(f"💬 Conversation turns: {len(self.conversation_history)}")
                return True
            
            elif command == 'history':
                if not self.conversation_history:
                    self.console.print("[yellow]No conversation history yet[/yellow]")
                else:
                    for i, (user_msg, ai_msg) in enumerate(self.conversation_history, 1):
                        self.console.print(f"\n[bold cyan]Turn {i} - You:[/bold cyan]")
                        self.console.print(user_msg)
                        self.console.print(f"[bold magenta]Turn {i} - Gemini:[/bold magenta]")
                        self.console.print(ai_msg[:200] + "..." if len(ai_msg) > 200 else ai_msg)
                return True
            
            elif command.startswith('create'):
                parts = command.split(None, 1)
                if len(parts) < 2:
                    filename = Prompt.ask("Enter filename")
                else:
                    filename = parts[1]
                
                self.console.print(f"Creating file: {filename}")
                self.console.print("Enter file content (type 'EOF' on a new line to finish):")
                
                content_lines = []
                while True:
                    try:
                        line = input()
                        if line.strip() == 'EOF':
                            break
                        content_lines.append(line)
                    except KeyboardInterrupt:
                        self.console.print("\n[yellow]File creation cancelled[/yellow]")
                        return True
                
                content = '\n'.join(content_lines)
                self.create_file(filename, content)
                return True
            
            elif command.startswith('read'):
                parts = command.split(None, 1)
                if len(parts) < 2:
                    filename = Prompt.ask("Enter filename to read")
                else:
                    filename = parts[1]
                
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Try to detect language for syntax highlighting
                    file_ext = Path(filename).suffix.lower()
                    lang_map = {'.py': 'python', '.js': 'javascript', '.html': 'html', '.css': 'css', '.json': 'json'}
                    language = lang_map.get(file_ext, 'text')
                    
                    syntax = Syntax(content, language, theme="monokai", line_numbers=True)
                    self.console.print(Panel(syntax, title=f"📄 {filename}", border_style="blue"))
                    
                except FileNotFoundError:
                    self.console.print(f"❌ [red]File not found: {filename}[/red]")
                except Exception as e:
                    self.console.print(f"❌ [red]Error reading file: {e}[/red]")
                return True
            
            elif command == 'list':
                files = [f for f in os.listdir('.') if os.path.isfile(f)]
                dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
                
                self.console.print("[bold]📁 Directories:[/bold]")
                for d in sorted(dirs):
                    self.console.print(f"  {d}/")
                
                self.console.print("\n[bold]📄 Files:[/bold]")
                for f in sorted(files):
                    size = os.path.getsize(f)
                    self.console.print(f"  {f} ({size} bytes)")
                
                return True
            
            else:
                self.console.print(f"❌ [red]Unknown command: {command}[/red]")
                self.console.print("Type /help for available commands")
                return True
        
        return None  # Not a command, continue with normal processing

    def run(self):
        """Main CLI loop"""
        try:
            # Display startup screen
            self.console.clear()
            self.display_ascii_logo()
            self.display_tips()
            
            # Check if running in home directory
            if Path.cwd().name == Path.home().name:
                warning = "You are running Gemini CLI in your home directory. It is recommended to run in a project-specific directory."
                self.console.print(Panel(warning, title="⚠️ Warning", border_style="yellow"))
                self.console.print()
            
            self.display_status()
            
            while True:
                try:
                    # Get user input
                    user_input = Prompt.ask(
                        "[bold green]>[/bold green] [dim]Type your message or @path/to/file[/dim]",
                        default=""
                    )
                    
                    if not user_input.strip():
                        continue
                    
                    # Handle special commands
                    command_result = self.handle_command(user_input)
                    if command_result is False:  # Exit command
                        break
                    elif command_result is True:  # Command handled
                        continue
                    
                    # Handle file references (@path/to/file)
                    if user_input.startswith('@'):
                        file_path = user_input[1:].strip()
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            user_input = f"Here's the content of {file_path}:\n\n```\n{file_content}\n```\n\nPlease analyze or help me with this file."
                        except FileNotFoundError:
                            self.console.print(f"❌ [red]File not found: {file_path}[/red]")
                            continue
                        except Exception as e:
                            self.console.print(f"❌ [red]Error reading file: {e}[/red]")
                            continue
                    
                    # Show thinking indicator
                    with self.console.status("[bold green]HeHe Noob is thinking...", spinner="dots"):
                        try:
                            # Send message to Gemini
                            response = self.chat.send_message(user_input)
                            response_text = response.text
                            
                            # Store in conversation history
                            self.conversation_history.append((user_input, response_text))
                            
                        except Exception as e:
                            self.console.print(f"❌ [red]Error getting response from Gemini: {e}[/red]")
                            continue
                    
                    # Process and display the response
                    self.process_response(response_text)
                    self.console.print()
                    
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Use /exit to quit or continue typing...[/yellow]")
                    continue
                except EOFError:
                    break
        
        except Exception as e:
            self.console.print(f"❌ [red]Unexpected error: {e}[/red]")
        
        finally:
            self.console.print("👋 [yellow]Goodbye![/yellow]")

def main():
    parser = argparse.ArgumentParser(description="HeHe Noob CLI - Command-line interface for Google's Gemini AI")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--model", default="gemini-2.0-flash-exp", help="Gemini model to use")
    
    args = parser.parse_args()
    
    cli = HeHeNoobCLI(api_key=args.api_key, model=args.model)
    cli.run()

if __name__ == "__main__":
    main()