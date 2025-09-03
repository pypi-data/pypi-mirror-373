# z/OS FTP MCP Server

[![PyPI version](https://img.shields.io/pypi/v/zos-ftp-mcp.svg)](https://pypi.org/project/zos-ftp-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/zos-ftp-mcp.svg)](https://pypi.org/project/zos-ftp-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for interacting with z/OS mainframe systems via FTP.

## Features

- List datasets from mainframe catalog with pattern matching
- Download datasets in binary format
- Download members from partitioned datasets (PDS)
- Connection management via environment variables

## Installation

### For MCP Server Usage
No installation needed! The MCP configuration with `uvx` will automatically download and run the package.

### For Python Library Usage
```bash
pip install zos-ftp-mcp
```

## Configuration

Set environment variables for connection:

```bash
export ZFTP_HOST="your-mainframe-host"
export ZFTP_PORT="21"
export ZFTP_USER="your-username"
export ZFTP_PASSWORD="your-password"
export ZFTP_TIMEOUT="30.0"
export ZFTP_DOWNLOAD_PATH="/path/to/downloads"
```

## Usage

### As MCP Server

```json
{
  "mcpServers": {
    "zos-ftp-mcp": {
      "command": "uvx",
      "args": ["zos-ftp-mcp"],
      "env": {
        "ZFTP_HOST": "your-mainframe-host",
        "ZFTP_USER": "your-username",
        "ZFTP_PASSWORD": "your-password",
        "ZFTP_DOWNLOAD_PATH": "/path/to/downloads"
      }
    }
  }
}
```

### Direct Command Line
```bash
zos-ftp-mcp
```

## Tools Available

- `list_catalog(pattern)` - List datasets matching pattern
- `download_binary(source_dataset, target_file)` - Download dataset
- `download_pds_members(dataset, target_dir, members, retr_mode, ftp_threads, batch_size)` - Download PDS members
- `get_connection_info()` - Show current connection settings
- `set_connection_params(...)` - Update connection parameters

## Sample Usage Prompts

Once configured, you can use these prompts:

### Dataset Discovery
"List all datasets starting with SYS1 to explore system datasets"

"Show me all user datasets matching MYUSER.* pattern"

### Data Download
"Download the dataset MYUSER.COBOL.SOURCE to my local downloads folder"

"Download all members from the PDS MYUSER.COBOL.COPYLIB to a local directory"

### Connection Management
"Show me the current FTP connection settings"

"Update the download path to /Users/myname/mainframe-data"

## Dependencies

- [zosftplib](https://pypi.org/project/zosftplib/) - z/OS FTP operations
- [mcp](https://pypi.org/project/mcp/) - Model Context Protocol

## License

MIT License - see LICENSE file for details.
