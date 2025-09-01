# qufe

A comprehensive Python utility library for data processing, file handling, database management, and automation tasks.

## Features

### Core Utilities (`base`)
- **Timestamp handling**: Convert timestamps to datetime objects with timezone support
- **Code comparison**: Compare code snippets with multiple diff formats (simple, unified, ndiff)
- **Dynamic module import**: Import Python modules dynamically from file paths
- **List flattening**: Flatten nested lists with configurable depth
- **Dictionary utilities**: Flatten three-level nested dictionaries with suffix support

### Database Management (`dbhandler`)
- **PostgreSQL integration**: Easy PostgreSQL database connections and queries using SQLAlchemy
- **Database exploration**: List databases and tables with metadata
- **Connection management**: Automatic connection pooling and cleanup

### Text Processing (`texthandler`, `excludebracket`)
- **Bracket content removal**: Remove content within brackets with validation
- **DokuWiki formatting**: Convert lists to DokuWiki table format
- **String search utilities**: Find all occurrences of substrings with context
- **Dictionary printing**: Pretty-print nested dictionaries with indentation
- **Column formatting**: Display lists in multiple columns with alignment

### File Operations (`filehandler`)
- **Directory traversal**: Get file lists and directory trees with Unicode normalization
- **Pattern matching**: Find latest files based on datetime patterns
- **Pickle operations**: Save and load Python objects to/from pickle files
- **Path utilities**: Create unique filenames and sanitize file names
- **Content extraction**: Extract text content from directory structures

### Data Analysis (`pdhandler`)
- **DataFrame utilities**: Convert lists to tuples in pandas DataFrames
- **Column analysis**: Compare column names across multiple DataFrames
- **Missing data detection**: Find rows and columns with NA or empty values
- **Data validation**: Comprehensive data quality checks

### Automation & Screen Interaction (`interactionhandler`)
- **Screen capture**: Take screenshots of full screen or specific regions
- **Image processing**: Color detection, image comparison, and difference highlighting
- **Mouse automation**: Random clicking within regions for automation
- **Progress tracking**: Real-time progress updates in Jupyter notebooks
- **Color analysis**: Extract and analyze color codes from screen regions

### Web Browser Automation (`wbhandler`)
- **SeleniumBase integration**: Enhanced browser automation with custom timeouts
- **Network monitoring**: Capture fetch/XHR requests with JavaScript injection
- **Element discovery**: Interactive element finding with common attribute detection
- **URL parsing**: Extract parameters and values from URLs
- **Multi-browser support**: Chrome and Firefox browser implementations

## Installation

```bash
pip install qufe
```

## Quick Start

### Basic Usage

```python
from qufe import base, texthandler, filehandler

# Timestamp handling
ts = base.TS('Asia/Seoul')
formatted_time = ts.get_ts_formatted(1640995200)

# File operations
fh = filehandler.FileHandler()
files = fh.get_tree('/path/to/directory')

# Text processing
texthandler.print_dict({'key': ['value1', 'value2']})
```

### Database Operations

Before using database operations, you need to configure your PostgreSQL credentials.

#### Option 1: Using .env file (Recommended)

1. Copy the `.env.example` file to `.env` in your project root:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your database credentials:
```bash
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database
```

3. Use the database handler:
```python
from qufe.dbhandler import PostGreSQLHandler

# Credentials will be loaded automatically from .env file
db = PostGreSQLHandler()
databases = db.get_database_list()
tables = db.get_table_list()
```

#### Option 2: Using environment variables
```bash
export POSTGRES_USER=your_username
export POSTGRES_PASSWORD=your_password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=your_database
```

#### Option 3: Passing credentials directly
```python
from qufe.dbhandler import PostGreSQLHandler

db = PostGreSQLHandler(
    user='your_username',
    password='your_password',
    host='localhost',
    port=5432,
    db_name='your_database'
)
```

### Screen Automation

```python
from qufe.interactionhandler import get_sc, display_img

# Capture screen
screenshot = get_sc(100, 100, 800, 600)
display_img(screenshot, is_bgra=True)
```

### Web Browser Automation

```python
from qufe.wbhandler import FireFox

# Start browser session
browser = FireFox()
browser.sb.open('https://example.com')
browser.inject_capture_with_js()
logs = browser.get_capture()
browser.quit_driver()
```

## Configuration

### Database Configuration

For database operations, qufe supports multiple ways to configure PostgreSQL connections:

1. **`.env` file (Recommended)**: Create a `.env` file in your project root with your database credentials
2. **Environment variables**: Set environment variables in your system or shell
3. **Direct parameters**: Pass credentials directly to the constructor

The `.env` file approach is recommended because it:
- Works consistently across different development environments (Jupyter Lab, PyCharm, terminal, etc.)
- Keeps credentials separate from code
- Is easy to manage and doesn't require system-level configuration

## Requirements

- Python 3.8+
- pandas >= 1.3.0
- numpy >= 1.20.0
- sqlalchemy >= 1.4.0
- seleniumbase >= 4.0.0
- opencv-python >= 4.5.0
- matplotlib >= 3.3.0
- pyautogui >= 0.9.50
- mss >= 6.0.0
- python-dotenv >= 1.0.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Security & Ethics

### Database Configuration
For security, database credentials should be stored in a `.env` file or environment variables, never hardcoded in your source code. The `.env` file should be added to your `.gitignore` to prevent accidental commits of sensitive information.

### Automation Guidelines
When using screen capture and browser automation features:
- Respect website terms of service and robots.txt
- Be mindful of rate limiting and server load
- Only automate interactions you're authorized to perform
- Consider privacy implications of screen capture functionality

### Web Scraping Ethics
- Always check and comply with robots.txt
- Respect rate limits and implement delays
- Review website terms of service before scraping
- Be considerate of server resources

## Support

If you encounter any problems, please file an issue along with a detailed description.