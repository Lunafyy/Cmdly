# Cmdly

A flexible and extensible command-line interface application providing various utility commands with colorful output. Built with a custom tokenizer, parser, and executor cycle.

## Features

- **Extensible Command System** - Easily add new commands by extending the BaseCommand class
- **Colorful Output** - Enhanced terminal experience with colored text using Colorama
- **Comprehensive Help** - Built-in help system with detailed command descriptions
- **Robust Error Handling** - Graceful error management with contextual messages
- **Configuration Management** - JSON-based settings for customization
- **Logging System** - Comprehensive logging

## Available Commands

- `chat` - Simulated P2P chat service with a Client/Server topology on the backend.
- `echo` - Output text
- `headsortails` - Flip a virtual coin
- `help` - Display available commands or specific command help
- `llm` - Interact with an LLM provided by minoa.cat's free API
- `clear` - Clear the console

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Cmdly.git
   cd Cmdly
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python run_cli.py
   ```

## Usage

```bash
# Navigate into the route directory
cd Cmdly

# Run the entry-point file
python run_cli.py
```

## Building the Executable

To create a standalone executable:

```bash
# Install PyInstaller if you haven't already
pip install pyinstaller

# Build the executable using the provided spec file
pyinstaller run_cli.spec
```

The executable will be created in the `dist/` directory.

## Configuration

The application uses a JSON configuration file located at `src/config/default_settings.json`. You can customize:

- Logging levels and output destinations
- Command aliases
- LLM temperature
- Fun commands toggle
- Default prompt with placeholders

## Extending with New Commands

Create a new command by extending the BaseCommand class:

```python
from core.core_types.command import BaseCommand

class YourCommand(BaseCommand):
    def execute(self, *args, **kwargs) -> int:
        """
        Execute your command logic here.
        
        Args:
            args (list): Command line arguments
            
        Returns:
            int: Exit code
        """
        # Your command implementation
        print("Your command executed successfully!")

        return 0
```

All commands are dynamically registered from their inheritance of the BaseCommand class.

## Dependencies

Please see `requirements.txt`

## Error Handling

The application includes comprehensive error handling:

- Command-specific error messages
- Logging of errors for debugging
- Graceful fallbacks for common issues
- User-friendly error reporting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Created as part of a portfolio project demonstrating clean code architecture, modular design, and CLI application development best practices.