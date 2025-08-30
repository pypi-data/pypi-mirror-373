# HeHe Noob CLI

A powerful command-line interface for Google's Gemini AI that enables interactive conversations, code generation, and file management directly from your terminal. Now with extra humor and personality!

## Features

- 🤖 **Interactive AI Chat**: Have natural conversations with Google's Gemini AI
- 📝 **Code Generation**: Generate code in multiple programming languages
- 💾 **Smart File Management**: Automatically save generated code to files
- 🎨 **Rich Terminal UI**: Beautiful, colorful interface with syntax highlighting
- 📁 **File Operations**: Read, create, and manage files directly from the CLI
- 💬 **Conversation History**: Keep track of your chat sessions
- 🔧 **Multiple Commands**: Built-in commands for enhanced productivity

## Installation

### From PyPI (Recommended)

```bash
pip install hehe-noob-cli
```

### From Source

```bash
git clone https://github.com/yourusername/hehe-noob-cli
cd hehe-noob-cli
pip install -e .
```

## Setup

1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set your API key as an environment variable:

```bash
# On Windows
set GEMINI_API_KEY=your-api-key-here

# On macOS/Linux
export GEMINI_API_KEY=your-api-key-here
```

## Usage

### Basic Usage

Start the CLI:

```bash
hehe
# or
hehe-noob
# or
hehenoob
# or (legacy commands)
gemini
gemini-cli
gai
```

### Command Line Options

```bash
hehe --help                      # Show help
hehe --model gemini-pro          # Use specific model
hehe --api-key YOUR_KEY          # Use specific API key
```

### Built-in Commands

Once in the CLI, you can use these commands:

- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/status` - Show current status
- `/history` - Show conversation history
- `/create <filename>` - Create a new file interactively
- `/read <filename>` - Read and display a file
- `/list` - List files in current directory
- `/exit` or `/quit` - Exit the CLI

### File References

You can reference files in your conversations:

```
@path/to/file.py
```

This will include the file content in your message to Gemini.

## Examples

### Code Generation

```
> Create a Python function to calculate fibonacci numbers
```

HeHe Noob will generate the code and offer to save it to a file.

### File Analysis

```
> @my_script.py Please review this code and suggest improvements
```

### Project Setup

```
> Create a Flask web application with user authentication
```

HeHe Noob will help you build it step by step!

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Gemini API key (required for HeHe Noob to work)

### Supported Models

- `gemini-2.0-flash-exp` (default)
- `gemini-1.5-pro`
- `gemini-1.5-flash`

## Requirements

- Python 3.8+
- Google Generative AI Python SDK
- Rich (for terminal UI)
- pathlib2 (for path handling)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/hehe-noob-cli/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide as much detail as possible about your environment and the issue
4. HeHe Noob loves feedback and bug reports!

## Changelog

### v1.0.0
- Initial release as HeHe Noob CLI
- Interactive chat with Gemini AI (now with personality!)
- Code generation and file management
- Rich terminal interface with custom ASCII art
- Built-in commands and file operations
- Interactive API key prompting
- Multiple command aliases (hehe, hehe-noob, hehenoob)

---

**Note**: This tool requires a valid Gemini API key. Make sure to keep your API key secure and never commit it to version control.