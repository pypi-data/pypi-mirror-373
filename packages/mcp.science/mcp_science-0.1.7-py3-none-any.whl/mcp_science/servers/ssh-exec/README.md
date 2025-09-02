# MCP SSH Execution Server

A Model Context Protocol (MCP) server for executing command-line operations on remote Linux systems via SSH.

## Features

- Secure SSH command execution on remote systems
- Command and argument validation for security
- Path restriction to prevent unauthorized access
- Support for password, key-based, and SSH config authentication
- Automatic SSH config file support (~/.ssh/config)
- Cross-platform compatibility (Windows, Linux, macOS)
- FastAPI-based MCP server with Uvicorn

## Installation

### Using uv (recommended)

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install the package in development mode
uv pip install -e .
```

## Configuration

### Environment Variables

For security reasons, SSH credentials should be provided via environment variables:

- `SSH_HOST`: SSH host to connect to (required)
- `SSH_PORT`: SSH port (default: 22)
- `SSH_USERNAME`: SSH username (optional if specified in SSH config)
- `SSH_PRIVATE_KEY_FILE`: SSH private key file path (supports OpenSSH format)
- `SSH_PASSWORD`: SSH password
- `SSH_CONFIG_FILE`: Custom SSH config file path (optional, defaults to ~/.ssh/config)

**Authentication priority (first available is used):**
1. `SSH_PRIVATE_KEY_FILE` - Explicit private key file
2. `SSH_PASSWORD` - Password authentication  
3. SSH config identity files (from ~/.ssh/config)
4. System SSH agent and default keys

**SSH Config Support:**
- Automatically loads `~/.ssh/config` (or custom path via `SSH_CONFIG_FILE`)
- Supports hostname aliases, port overrides, username defaults, and identity files
- Makes deployment simpler - only `SSH_HOST` required if properly configured

Optional environment variables for security configuration:
- `SSH_ALLOWED_COMMANDS`: Comma-separated list of commands that are allowed to be executed
- `SSH_ALLOWED_PATHS`: Comma-separated list of paths that are allowed for command execution
- `SSH_COMMANDS_BLACKLIST`: Comma-separated list of commands that are not allowed (default: rm,mv,dd,mkfs,fdisk,format)
- `SSH_ARGUMENTS_BLACKLIST`: Comma-separated list of arguments that are not allowed (default: -rf,-fr,--force)

### Command-Line Arguments
#### SSH Connection Configuration
- `--ssh-host`, `-sh`: SSH host to connect to (overrides SSH_HOST environment variable)
- `--ssh-port`, `-sp`: SSH port to connect to (overrides SSH_PORT environment variable)
- `--ssh-username`, `-su`: SSH username (overrides SSH_USERNAME environment variable)

#### Security Configuration
- `--allowed-commands`, `-ac`: Comma-separated list of commands that are allowed to be executed
- `--allowed-paths`, `-ap`: Comma-separated list of paths that are allowed for command execution
- `--commands-blacklist`, `-cb`: Comma-separated list of commands that are not allowed (default: rm,mv,dd,mkfs,fdisk,format)
- `--arguments-blacklist`, `-ab`: Comma-separated list of arguments that are not allowed (default: -rf,-fr,--force)

## Usage

### Configuration Examples

#### Option 1: Simple SSH Config (Recommended)
If you have SSH config properly set up in `~/.ssh/config`:

```bash
# ~/.ssh/config
Host myserver
    HostName example.com
    User myuser
    Port 2222
    IdentityFile ~/.ssh/id_rsa
    
# Only SSH_HOST needed!
export SSH_HOST=myserver
export SSH_ALLOWED_COMMANDS="ls,ps,cat"
export SSH_ALLOWED_PATHS="/tmp,/home"
```

#### Option 2: Explicit Environment Variables

```bash
export SSH_HOST=example.com
export SSH_PORT=22
export SSH_USERNAME=user
export SSH_PRIVATE_KEY_FILE=~/.ssh/id_rsa
export SSH_ALLOWED_COMMANDS="ls,ps,cat"
export SSH_ALLOWED_PATHS="/tmp,/home"
export SSH_COMMANDS_BLACKLIST=rm,mv,dd,mkfs,fdisk,format
export SSH_ARGUMENTS_BLACKLIST=-rf,-fr,--force
```

#### Option 3: Custom SSH Config File

```bash
export SSH_HOST=myserver
export SSH_CONFIG_FILE=/path/to/custom/ssh_config
export SSH_ALLOWED_COMMANDS="ls,ps,cat"
```

### Configuration for MCP Client

Add the SSH execution server to your MCP client configuration file. There are two main ways to configure the server:

#### Option 1: Run from local repository

Use this option if you have the code checked out locally and want to run it directly:

```json
{
  "mcpServers": {
    "mcp-ssh-exec": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-servers",
        "run",
        "mcp-ssh-exec"
      ],
      "env": {
        "SSH_HOST": "myserver",
        "SSH_ALLOWED_COMMANDS": "ls,ps,cat,df,free",
        "SSH_ALLOWED_PATHS": "/tmp,/home,/var/log"
      }
    }
  }
}
```

**Note:** This minimal configuration assumes you have SSH config properly set up. For explicit configuration:

```json
{
  "mcpServers": {
    "mcp-ssh-exec": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-servers",
        "run",
        "mcp-ssh-exec"
      ],
      "env": {
        "SSH_HOST": "example.com",
        "SSH_PORT": "22",
        "SSH_USERNAME": "user",
        "SSH_PRIVATE_KEY_FILE": "~/.ssh/id_rsa",
        "SSH_ALLOWED_COMMANDS": "ls,ps,cat,df,free",
        "SSH_ALLOWED_PATHS": "/tmp,/home,/var/log",
        "SSH_COMMANDS_BLACKLIST": "rm,mv,dd,mkfs,fdisk,format",
        "SSH_ARGUMENTS_BLACKLIST": "-rf,-fr,--force"
      }
    }
  }
}
```

#### Option 2: Fetch and run from remote repository

Use this option to automatically fetch and run the latest version from GitHub:

```json
{
  "mcpServers": {
    "mcp-ssh-exec": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pathintegral-institute/mcp.science#subdirectory=servers/ssh-exec",
        "mcp-ssh-exec"
      ],
      "env": {
        "SSH_HOST": "myserver",
        "SSH_ALLOWED_COMMANDS": "ls,ps,cat,df,free",
        "SSH_ALLOWED_PATHS": "/tmp,/home,/var/log"
      }
    }
  }
}
```

## SSH Config Examples

### Basic SSH Config
```bash
# ~/.ssh/config
Host myserver
    HostName example.com
    User myuser
    Port 2222
    IdentityFile ~/.ssh/id_rsa
```

### Advanced SSH Config with Aliases
```bash
# ~/.ssh/config
Host prod
    HostName production.example.com
    User deploy
    Port 22
    IdentityFile ~/.ssh/prod_key

Host staging  
    HostName staging.example.com
    User deploy
    Port 2222
    IdentityFile ~/.ssh/staging_key
    
# Use either "prod" or "staging" as SSH_HOST
```

### Multiple Identity Files
```bash
# ~/.ssh/config  
Host myserver
    HostName example.com
    User myuser
    IdentityFile ~/.ssh/id_rsa
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

## MCP Tools

The server provides the following MCP tool:

### `ssh-exec`

Execute a command on the remote system.

**Parameters:**
- `command`: Command to execute (string, required)
- `arguments`: Arguments to pass to the command (string, optional)

**Returns:**
A tuple containing:
- `exit_code`: The command's exit code (integer)
- `stdout`: Standard output from the command (string)
- `stderr`: Standard error from the command (string)

## License

MIT
