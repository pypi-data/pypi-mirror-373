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
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich import box
import argparse
import keyring
from cryptography.fernet import Fernet
import base64

class HeHeNoobCLI:
    def __init__(self, api_key=None, model="gemini-2.0-flash-exp"):
        self.console = Console()
        self.model_name = model
        self.conversation_history = []
        self.config_dir = Path.home() / ".hehenoob"
        self.config_file = self.config_dir / "config.json"
        
        # Configure HeHe Noob API
        if api_key:
            genai.configure(api_key=api_key)
        else:
            api_key = self.get_stored_api_key()
            genai.configure(api_key=api_key)
        
        try:
            self.model = genai.GenerativeModel(model)
            self.chat = self.model.start_chat(history=[])
        except Exception as e:
            self.console.print(f"❌ [red]Error initializing HeHe Noob model: {e}[/red]")
            if "API_KEY" in str(e) or "authentication" in str(e).lower() or "invalid" in str(e).lower():
                self.console.print("[yellow]Your API key seems to be having issues. Let me fix that for you...[/yellow]")
                api_key = self.prompt_for_api_key(force_new=True)
                genai.configure(api_key=api_key)
                try:
                    self.model = genai.GenerativeModel(model)
                    self.chat = self.model.start_chat(history=[])
                except Exception as e2:
                    self.console.print(f"❌ [red]Still unable to initialize: {e2}[/red]")
                    sys.exit(1)
            else:
                sys.exit(1)

    def get_stored_api_key(self):
         """Get API key from storage or prompt for new one"""
         # First check environment variable
         env_key = os.getenv('GEMINI_API_KEY')
         if env_key:
             return env_key
         
         # Then check stored key
         stored_key = self.load_api_key()
         if stored_key:
             return stored_key
         
         # If no key found, prompt for new one
         return self.prompt_for_api_key()
     
    def load_api_key(self):
         """Load API key from secure storage"""
         try:
             # Try keyring first (most secure)
             key = keyring.get_password("hehenoob-cli", "api_key")
             if key:
                 return key
             
             # Fallback to encrypted file
             if self.config_file.exists():
                 with open(self.config_file, 'r') as f:
                     config = json.load(f)
                     encrypted_key = config.get('api_key')
                     if encrypted_key:
                         return self.decrypt_key(encrypted_key)
         except Exception:
             # If anything fails, return None to prompt for new key
             pass
         return None
     
    def save_api_key(self, api_key):
         """Save API key to secure storage"""
         try:
             # Try keyring first (most secure)
             keyring.set_password("hehenoob-cli", "api_key", api_key)
             self.console.print("[dim]✅ API key saved securely (you won't have to do this again)[/dim]")
         except Exception:
             # Fallback to encrypted file
             try:
                 self.config_dir.mkdir(exist_ok=True)
                 encrypted_key = self.encrypt_key(api_key)
                 config = {'api_key': encrypted_key}
                 with open(self.config_file, 'w') as f:
                     json.dump(config, f)
                 self.console.print("[dim]✅ API key saved (encrypted, because I care about your security)[/dim]")
             except Exception:
                 self.console.print("[dim]⚠️ Couldn't save API key, you'll need to enter it again next time[/dim]")
     
    def clear_api_key(self):
         """Delete stored API key from all storage locations"""
         cleared_any = False
         
         # Clear from keyring
         try:
             keyring.delete_password("hehenoob-cli", "api_key")
             cleared_any = True
         except Exception:
             pass
         
         # Clear from encrypted file
         try:
             if self.config_file.exists():
                 self.config_file.unlink()
                 cleared_any = True
         except Exception:
             pass
         
         # Clear from environment (just inform user)
         if os.getenv('GEMINI_API_KEY'):
             self.console.print("[yellow]Note: GEMINI_API_KEY environment variable is still set[/yellow]")
         
         if cleared_any:
             self.console.print("[green]✅ API key cleared successfully! You'll need to enter it again next time.[/green]")
         else:
             self.console.print("[yellow]No stored API key found to clear.[/yellow]")
     
    def load_gitignore_patterns(self, directory='.'):
          """Load and parse .gitignore patterns"""
          gitignore_path = os.path.join(directory, '.gitignore')
          patterns = []
          
          if os.path.exists(gitignore_path):
              try:
                  with open(gitignore_path, 'r', encoding='utf-8') as f:
                      for line in f:
                          line = line.strip()
                          if line and not line.startswith('#'):
                              patterns.append(line)
              except Exception:
                  pass
          
          return patterns
     
    def is_ignored(self, path, gitignore_patterns, base_dir='.'):
          """Check if a path should be ignored based on gitignore patterns"""
          import fnmatch
          
          # Get relative path from base directory
          try:
              rel_path = os.path.relpath(path, base_dir)
              rel_path = rel_path.replace('\\', '/')  # Normalize path separators
          except ValueError:
              return False
          
          for pattern in gitignore_patterns:
              # Handle directory patterns
              if pattern.endswith('/'):
                  pattern = pattern[:-1]
                  if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                      return True
              else:
                  # Handle file patterns
                  if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                      return True
                  # Handle patterns with wildcards
                  if '/' in pattern:
                      if fnmatch.fnmatch(rel_path, pattern):
                          return True
          
          return False
     
    def show_directory_tree(self, directory='.', prefix='', max_depth=10, current_depth=0, gitignore_patterns=None):
          """Display directory tree structure respecting .gitignore"""
          if current_depth >= max_depth:
              return
          
          # Load gitignore patterns on first call
          if gitignore_patterns is None:
              gitignore_patterns = self.load_gitignore_patterns(directory)
          
          try:
              items = sorted(os.listdir(directory))
              
              # Filter out ignored items and hidden files
              dirs = []
              files = []
              
              for item in items:
                  if item.startswith('.'):
                      continue
                  
                  item_path = os.path.join(directory, item)
                  
                  # Check if item should be ignored
                  if self.is_ignored(item_path, gitignore_patterns, '.'):
                      continue
                  
                  if os.path.isdir(item_path):
                      dirs.append(item)
                  elif os.path.isfile(item_path):
                      files.append(item)
              
              # Show directories first
              for i, dirname in enumerate(dirs):
                  is_last_dir = (i == len(dirs) - 1) and len(files) == 0
                  current_prefix = "└── " if is_last_dir else "├── "
                  self.console.print(f"{prefix}{current_prefix}📁 [bold blue]{dirname}/[/bold blue]")
                  
                  # Recursively show subdirectory contents
                  next_prefix = prefix + ("    " if is_last_dir else "│   ")
                  subdir_path = os.path.join(directory, dirname)
                  self.show_directory_tree(subdir_path, next_prefix, max_depth, current_depth + 1, gitignore_patterns)
              
              # Show files
              for i, filename in enumerate(files):
                  is_last = i == len(files) - 1
                  current_prefix = "└── " if is_last else "├── "
                  
                  # Get file size
                  try:
                      size = os.path.getsize(os.path.join(directory, filename))
                      size_str = self.format_file_size(size)
                  except:
                      size_str = "?"
                  
                  # Color code by file extension
                  file_ext = Path(filename).suffix.lower()
                  if file_ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
                      color = "green"
                  elif file_ext in ['.html', '.css', '.scss', '.less']:
                      color = "magenta"
                  elif file_ext in ['.json', '.yaml', '.yml', '.xml', '.toml']:
                      color = "cyan"
                  elif file_ext in ['.md', '.txt', '.rst']:
                      color = "yellow"
                  else:
                      color = "white"
                  
                  self.console.print(f"{prefix}{current_prefix}📄 [{color}]{filename}[/{color}] [dim]({size_str})[/dim]")
          
          except PermissionError:
              self.console.print(f"{prefix}[red]❌ Permission denied[/red]")
          except Exception as e:
              self.console.print(f"{prefix}[red]❌ Error: {e}[/red]")
     
    def format_file_size(self, size_bytes):
         """Format file size in human readable format"""
         if size_bytes == 0:
             return "0 B"
         size_names = ["B", "KB", "MB", "GB"]
         i = 0
         while size_bytes >= 1024 and i < len(size_names) - 1:
             size_bytes /= 1024.0
             i += 1
         return f"{size_bytes:.1f} {size_names[i]}"
     
    def encrypt_key(self, key):
         """Encrypt API key for storage"""
         # Generate a key based on machine-specific info
         machine_key = base64.urlsafe_b64encode(os.urandom(32))
         f = Fernet(machine_key)
         encrypted = f.encrypt(key.encode())
         # Store both the machine key and encrypted data
         return base64.b64encode(machine_key + encrypted).decode()
     
    def decrypt_key(self, encrypted_data):
         """Decrypt API key from storage"""
         try:
             data = base64.b64decode(encrypted_data.encode())
             machine_key = data[:44]  # First 44 bytes are the key
             encrypted = data[44:]    # Rest is encrypted data
             f = Fernet(machine_key)
             return f.decrypt(encrypted).decode()
         except Exception:
             return None
     
    def prompt_for_api_key(self, force_new=False):
          """Streamlined API key input with single UI"""
          # Don't clear screen, show API input right after ASCII art and tips
          
          # Create the API key input panel with embedded input
          if force_new:
              title = "🔑 API Key Update Required"
              subtitle = "Your API key needs updating! Let's get you a fresh one."
          else:
              title = "🔑 API Key Setup"
              subtitle = "First time setup - Let's get you connected to the AI magic!"
          
          # Instructions and input in one panel
          instructions = f"""[bold yellow]{subtitle}[/bold yellow]

[bold]How to get your API key:[/bold]
1. Visit [link]https://aistudio.google.com[/link]
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Paste it below

[dim]Don't worry, I'll just keep it in my pocket, Won't eat it! 🔐[/dim]

[bold cyan]Enter your Gemini API key:[/bold cyan]"""
          
          # API key input loop
          while True:
              # Create the main input panel
              input_panel = Panel(
                  instructions,
                  title=title,
                  border_style="green",
                  padding=(1, 2)
              )
              self.console.print(input_panel)
              
              # Get API key input with prompt inside the conceptual box
              api_key = Prompt.ask(
                  "[bold green]API Key[/bold green]",
                  password=True
              )
              
              if api_key and len(api_key.strip()) > 10:  # Basic validation
                  api_key = api_key.strip()
                  
                  # Show success message
                  success_panel = Panel(
                      "[bold green]✅ API Key validated and saved successfully![/bold green]\n[dim]You're all set to start coding with HeHe Noob! 🎉[/dim]",
                      border_style="green",
                      padding=(1, 2)
                  )
                  self.console.print(success_panel)
                  
                  self.save_api_key(api_key)
                  return api_key
              else:
                  # Show error message
                  error_panel = Panel(
                      "[bold red]❌ Invalid API Key[/bold red]\n[dim]That doesn't look like a valid API key. Please check and try again.[/dim]",
                      border_style="red",
                      padding=(1, 2)
                  )
                  self.console.print(error_panel)
                  
                  retry = Prompt.ask(
                      "[yellow]Would you like to try again?[/yellow]",
                      choices=["y", "n", "yes", "no"],
                      default="y"
                  )
                  if retry.lower() in ['n', 'no']:
                      self.console.print("\n[yellow]👋 Setup cancelled. Run the command again when you're ready![/yellow]")
                      sys.exit(0)

    def display_ascii_logo(self):
        """Display the HeHe Noob ASCII logo"""
        logo = """
[rgb(181,193,227)]██   ██ ███████ ██   ██ ███████[/rgb(181,193,227)] ██ [rgb(181,193,227)]███    ██  ██████   ██████  ██████[/rgb(181,193,227)]
[rgb(189,170,224)]██   ██ ██      ██   ██ ██     [/rgb(189,170,224)] ██ [rgb(189,170,224)]████   ██ ██    ██ ██    ██ ██   ██[/rgb(189,170,224)]
[rgb(197,147,221)]███████ █████   ███████ █████  [/rgb(197,147,221)] ██ [rgb(197,147,221)]██ ██  ██ ██    ██ ██    ██ ██████[/rgb(197,147,221)]
[rgb(205,124,218)]██   ██ ██      ██   ██ ██     [/rgb(205,124,218)]    [rgb(205,124,218)]██  ██ ██ ██    ██ ██    ██ ██   ██[/rgb(205,124,218)]
[rgb(213,101,215)]██   ██ ███████ ██   ██ ███████[/rgb(213,101,215)] ██ [rgb(213,101,215)]██   ████  ██████   ██████  ██████[/rgb(213,101,215)]

[bold yellow]🤖 Your Friendly AI Assistant with a Sense of Humor! 😄[/bold yellow]
        """
        self.console.print(logo)
        self.console.print()

    def display_tips(self):
        """Display startup tips with sass"""
        tips = """[bold]Listen up, coding peasant! Here's how to not embarrass yourself:[/bold]
1. Ask me questions like you actually know what you're doing (spoiler: you don't) 🙄
2. Be specific, or I'll roast you harder than your last deployment 🔥
3. Create HEHE.md files if you want me to pretend to care about your preferences 📝
4. Type /help when you inevitably get confused (which will be soon) 🤡

[dim]Pro tip: I'm smarter than your senior developer, and I'm not even trying 😏[/dim]"""
        
        self.console.print(tips)
        self.console.print()

    def display_status(self):
        """Display current status"""
        current_dir = Path.cwd().name
        status_text = f"no sandbox (see /docs)                    {self.model_name}"
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
            
            self.console.print(f"✅ [green]Created file: {filename}. Wow, you actually did something right! 🎉[/green]")
            return True
        except Exception as e:
            self.console.print(f"❌ [red]Error creating file {filename}: {e}. Even I can't fix your file system issues 🤷‍♂️[/red]")
            return False

    def process_response(self, response_text):
        """Process the AI response and handle file creation"""
        # Display the response with enhanced styling
        try:
            markdown = Markdown(response_text)
            response_panel = Panel(
                markdown, 
                title="[bold magenta]🤖 HeHe Noob Response[/bold magenta]", 
                border_style="magenta",
                padding=(1, 2)
            )
            self.console.print(response_panel)
        except:
            # Fallback if markdown parsing fails
            response_panel = Panel(
                response_text, 
                title="[bold magenta]🤖 HeHe Noob Response[/bold magenta]", 
                border_style="magenta",
                padding=(1, 2)
            )
            self.console.print(response_panel)
        
        # Extract and offer to save code blocks
        code_blocks = self.extract_code_blocks(response_text)
        
        if code_blocks:
            # Create a fancy code blocks header
            code_header = Panel(
                f"[bold yellow]🎯 Found {len(code_blocks)} code block(s) - I made you some actual working code (you're welcome) 💎[/bold yellow]",
                border_style="yellow",
                padding=(0, 1)
            )
            self.console.print(code_header)
            
            for i, block in enumerate(code_blocks):
                # Enhanced code block display
                code_title = f"[bold]📝 Code Block {i+1} ({block['language']}) - [dim]Actually good code (unlike yours)[/dim][/bold]"
                syntax = Syntax(block['code'], block['language'], theme="monokai", line_numbers=True)
                
                code_panel = Panel(
                    syntax,
                    title=code_title,
                    border_style="blue",
                    padding=(1, 1)
                )
                self.console.print(code_panel)
                
                save_choice = Prompt.ask(
                    f"Save this {block['language']} masterpiece to a file? (Smart choice would be 'yes')",
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
                        "Enter filename (try to pick something that makes sense this time)",
                        default=default_name
                    )
                    
                    self.create_file(filename, block['code'], block['language'])

    def handle_command(self, user_input):
        """Handle special commands"""
        if user_input.startswith('/'):
            command = user_input[1:].strip().lower()
            
            if command == 'help':
                help_text = """[bold cyan]HeHe Noob's Command Cheat Sheet (Because You'll Forget):[/bold cyan]

[bold]Basic Commands (Try Not to Break Anything):[/bold]
• /help - Show this again when you inevitably forget 🤦‍♂️
• /clear - Erase your embarrassing conversation history
• /exit or /quit - Run away in shame (I don't blame you)
• /status - See how badly you're doing
• /history - Relive your coding failures

[bold]File Operations (Handle with Care, Noob):[/bold]
• /create <filename> - Make a file (try not to name it 'untitled.txt')
• /read <filename> - Read a file (assuming you can spell the name)
• /list - See what mess you've created in this directory
• /reset-key - Change your API key (when you inevitably mess it up)
• /clear-key - Delete your stored API key (when you want to start fresh)
• /tree - Show the entire folder structure (see your organized chaos)

[bold]Pro Tips (You'll Need Them):[/bold]
• I'll create code that actually works (unlike yours) and save it as files
• Be specific, or I'll assume you want 'Hello World' again 🙄
• Mention frameworks so I know which ones you'll break
• I remember everything, unlike your goldfish memory 🐠

[dim]Remember: I'm not just an AI, I'm your disappointed coding mentor 😤[/dim]
"""
                self.console.print(Panel(help_text, title="Help", border_style="green"))
                return True
            
            elif command == 'clear':
                self.chat = self.model.start_chat(history=[])
                self.conversation_history = []
                self.console.clear()
                self.display_ascii_logo()
                self.console.print("✅ [green]Memory wiped! Now I can pretend your previous questions weren't that stupid 🧠💨[/green]")
                return True
            
            elif command in ['exit', 'quit']:
                self.console.print("👋 [yellow]Fine, abandon me like your last three projects. I'll be here when you need me again (and you will) 😏[/yellow]")
                return False
            
            elif command == 'status':
                self.display_status()
                current_dir = os.getcwd()
                file_count = len([f for f in os.listdir('.') if os.path.isfile(f)])
                self.console.print(f"📁 Current directory: {current_dir} [dim](at least you're somewhere)[/dim]")
                self.console.print(f"📄 Files in directory: {file_count} [dim](probably all broken)[/dim]")
                self.console.print(f"💬 Conversation turns: {len(self.conversation_history)} [dim](each one more desperate than the last)[/dim]")
                self.console.print("[dim]Overall assessment: You're trying, and that's... something 🤷‍♂️[/dim]")
                return True
            
            elif command == 'history':
                if not self.conversation_history:
                    self.console.print("[yellow]No conversation history yet. Congratulations, you haven't embarrassed yourself... yet 🎉[/yellow]")
                else:
                    self.console.print("[dim]Here's a recap of your coding journey (brace yourself):[/dim]")
                    for i, (user_msg, ai_msg) in enumerate(self.conversation_history, 1):
                        self.console.print(f"\n[bold cyan]Turn {i} - You (the confused one):[/bold cyan]")
                        self.console.print(user_msg)
                        self.console.print(f"[bold magenta]Turn {i} - Me (the genius):[/bold magenta]")
                        self.console.print(ai_msg[:200] + "... [dim](I said more brilliant things)[/dim]" if len(ai_msg) > 200 else ai_msg)
                return True
            
            elif command.startswith('create'):
                parts = command.split(None, 1)
                if len(parts) < 2:
                    filename = Prompt.ask("Enter filename")
                else:
                    filename = parts[1]
                
                self.console.print(f"Creating file: {filename} [dim](let's see what masterpiece you'll create)[/dim]")
                self.console.print("Enter file content (type 'EOF' on a new line to finish):")
                self.console.print("[dim]Pro tip: Try not to write spaghetti code this time 🍝[/dim]")
                
                content_lines = []
                while True:
                    try:
                        line = input()
                        if line.strip() == 'EOF':
                            break
                        content_lines.append(line)
                    except KeyboardInterrupt:
                        self.console.print("\n[yellow]File creation cancelled. Smart choice, probably would've been terrible anyway 🤷‍♂️[/yellow]")
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
                    self.console.print(Panel(syntax, title=f"📄 {filename} [dim](let's see what disaster awaits)[/dim]", border_style="blue"))
                    
                except FileNotFoundError:
                    self.console.print(f"❌ [red]File not found: {filename}. Did you spell it right? Probably not 🤦‍♂️[/red]")
                except Exception as e:
                    self.console.print(f"❌ [red]Error reading file: {e}. Congratulations, you broke something 🎉[/red]")
                return True
            
            elif command == 'list':
                files = [f for f in os.listdir('.') if os.path.isfile(f)]
                dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
                
                self.console.print("[bold]📁 Directories (your organized chaos):[/bold]")
                for d in sorted(dirs):
                    self.console.print(f"  {d}/ [dim](probably full of more broken code)[/dim]")
                
                self.console.print("\n[bold]📄 Files (the evidence of your struggles):[/bold]")
                for f in sorted(files):
                    size = os.path.getsize(f)
                    self.console.print(f"  {f} ({size} bytes) [dim](size doesn't matter when it doesn't work)[/dim]")
                
                return True
            
            elif command == 'reset-key':
                self.console.print("[yellow]🔑 Time to change your API key! (Finally being responsible)[/yellow]")
                new_key = self.prompt_for_api_key(force_new=True)
                try:
                    genai.configure(api_key=new_key)
                    self.model = genai.GenerativeModel(self.model_name)
                    self.chat = self.model.start_chat(history=[])
                    self.console.print("[green]✅ API key updated successfully! Now I can work my magic again 🎉[/green]")
                except Exception as e:
                    self.console.print(f"[red]❌ New API key is also problematic: {e}[/red]")
                    self.console.print("[dim]Maybe try getting a key that actually works? 🤷‍♂️[/dim]")
                return True
            
            elif command == 'clear-key':
                self.console.print("[yellow]🗑️ Clearing your stored API key... (Starting fresh, eh?)[/yellow]")
                self.clear_api_key()
                self.console.print("[cyan]Redirecting to API key setup...[/cyan]")
                # Get new API key and reconfigure
                new_api_key = self.prompt_for_api_key(force_new=True)
                genai.configure(api_key=new_api_key)
                try:
                    self.model = genai.GenerativeModel(self.model_name)
                    self.chat = self.model.start_chat(history=[])
                    self.console.print("[green]✅ Ready to continue with new API key![/green]")
                except Exception as e:
                    self.console.print(f"[red]❌ Error with new API key: {e}[/red]")
                    sys.exit(1)
                return True
            
            elif command == 'tree':
                self.console.print("[cyan]🌳 Here's your project structure (brace yourself):[/cyan]")
                current_dir = Path.cwd().name
                self.console.print(f"📁 [bold blue]{current_dir}/[/bold blue]")
                self.show_directory_tree()
                return True
            
            else:
                self.console.print(f"❌ [red]Unknown command: {command}. Nice try, but that's not a thing 🤡[/red]")
                self.console.print("Type /help for available commands [dim](assuming you can read)[/dim]")
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
                    # Create fancy input interface
                    self.show_input_prompt()
                    
                    # Get user input with bordered prompt
                    user_input = self.get_fancy_user_input()
                    
                    if not user_input.strip():
                        continue
                    
                    # Handle special commands
                    command_result = self.handle_command(user_input)
                    if command_result is False:  # Exit command
                        break
                    elif command_result is True:  # Command handled
                        continue
                    
                    # Handle file references (@path/to/file) within messages
                    if '@' in user_input:
                        # Find all @filename references
                        import re
                        file_refs = re.findall(r'@([^\s]+)', user_input)
                        
                        if file_refs:
                            file_contents = []
                            for file_path in file_refs:
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        file_content = f.read()
                                    file_contents.append(f"\n\n--- Content of {file_path} ---\n```\n{file_content}\n```")
                                    # Remove the @filename from the original message
                                    user_input = user_input.replace(f'@{file_path}', f'the file {file_path}')
                                except FileNotFoundError:
                                    self.console.print(f"❌ [red]File not found: {file_path}[/red]")
                                    user_input = user_input.replace(f'@{file_path}', f'[FILE NOT FOUND: {file_path}]')
                                except Exception as e:
                                    self.console.print(f"❌ [red]Error reading {file_path}: {e}[/red]")
                                    user_input = user_input.replace(f'@{file_path}', f'[ERROR READING: {file_path}]')
                            
                            # Append all file contents to the message
                            if file_contents:
                                user_input += ''.join(file_contents)
                    
                    # Show thinking indicator
                    with self.console.status("[bold green]HeHe Noob is thinking...", spinner="dots"):
                        try:
                            # Send message to Gemini
                            response = self.chat.send_message(user_input)
                            response_text = response.text
                            
                            # Store in conversation history
                            self.conversation_history.append((user_input, response_text))
                            
                        except Exception as e:
                            error_msg = str(e).lower()
                            if "quota" in error_msg or "limit" in error_msg or "exceeded" in error_msg:
                                self.console.print(f"❌ [red]Looks like you hit your API quota limit! Time for a new key or wait it out 💸[/red]")
                                retry_choice = Prompt.ask(
                                    "Want to try a different API key?",
                                    choices=["y", "n", "yes", "no"],
                                    default="n"
                                )
                                if retry_choice.lower() in ['y', 'yes']:
                                    new_key = self.prompt_for_api_key(force_new=True)
                                    genai.configure(api_key=new_key)
                                    self.model = genai.GenerativeModel(self.model_name)
                                    self.chat = self.model.start_chat(history=[])
                                    continue
                            elif "api_key" in error_msg or "authentication" in error_msg or "invalid" in error_msg:
                                self.console.print(f"❌ [red]Your API key seems to be invalid. Let's fix that![/red]")
                                new_key = self.prompt_for_api_key(force_new=True)
                                genai.configure(api_key=new_key)
                                self.model = genai.GenerativeModel(self.model_name)
                                self.chat = self.model.start_chat(history=[])
                                continue
                            else:
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
            self.console.print("👋 [yellow]Goodbye! Try not to break anything while I'm gone 😏[/yellow]")
    
    def show_input_prompt(self):
        """Display the current status and input prompt area"""
        # Show current directory and model info
        current_dir = Path.cwd().name
        status_info = f"[dim]📁 {current_dir} | 🤖 {self.model_name} | 💬 {len(self.conversation_history)} turns[/dim]"
        self.console.print(status_info)
    
    def get_fancy_user_input(self):
        """Get user input with a fancy bordered interface"""
        # Create input prompt panel with embedded input instructions
        prompt_content = """[bold green]💬 Just Say it already, that you need help?[/bold green]
[dim]Type your message, use @filename to reference files, or /help for commands[/dim]"""
        
        input_panel = Panel(
            prompt_content,
            title="[bold cyan]HeHe Noob Chat[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(input_panel)
        
        # Get the actual input with a styled prompt (conceptually inside the box)
        user_input = Prompt.ask(
            "[bold cyan]>[/bold cyan]",
            default=""
        )
        
        return user_input

def main():
    parser = argparse.ArgumentParser(description="HeHe Noob CLI - Command-line interface for Google's Gemini AI")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--model", default="gemini-2.0-flash-exp", help="Gemini model to use")
    
    args = parser.parse_args()
    
    cli = HeHeNoobCLI(api_key=args.api_key, model=args.model)
    cli.run()

if __name__ == "__main__":
    main()