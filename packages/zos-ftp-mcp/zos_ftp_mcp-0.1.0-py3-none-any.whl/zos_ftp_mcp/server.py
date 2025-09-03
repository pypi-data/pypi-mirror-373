"""
Mainframe z/OS FTP MCP Server

This MCP server provides tools for interacting with z/OS mainframe systems via FTP.
"""

import os
import ftplib
import fnmatch
import zosftplib
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("MainframeZOS")

def _get_connection_params():
    """Get connection parameters from environment variables."""
    return {
        'host': os.environ.get('ZFTP_HOST', ''),
        'port': int(os.environ.get('ZFTP_PORT', '21')),
        'user': os.environ.get('ZFTP_USER', ''),
        'password': os.environ.get('ZFTP_PASSWORD', ''),
        'timeout': float(os.environ.get('ZFTP_TIMEOUT', '30.0')),
        'download_path': os.environ.get('ZFTP_DOWNLOAD_PATH', '/tmp')
    }

def _validate_connection(params):
    """Validate required connection parameters."""
    if not params['host']:
        return "Host is required. Set ZFTP_HOST environment variable."
    if not params['user']:
        return "Username is required. Set ZFTP_USER environment variable."
    if not params['password']:
        return "Password is required. Set ZFTP_PASSWORD environment variable."
    return None

@mcp.tool(description="List datasets from mainframe catalog matching a pattern")
def list_catalog(pattern: str = 'SYS1.*') -> list:
    """Lists datasets from mainframe catalog matching the specified pattern."""
    params = _get_connection_params()
    error = _validate_connection(params)
    if error:
        return [f"Error: {error}"]
    
    ftplib.FTP.port = params['port']
    
    try:
        zftp = zosftplib.Zftp(params['host'], params['user'], params['password'], 
                             timeout=params['timeout'])
        entries = zftp.list_catalog(pattern)
        return entries if entries else []
    except Exception as e:
        return [f"Error listing catalog: {str(e)}"]

@mcp.tool(description="Download a dataset from mainframe in binary format")
def download_binary(source_dataset: str, target_file: Optional[str] = None) -> dict:
    """Downloads a dataset from the mainframe in binary format."""
    params = _get_connection_params()
    error = _validate_connection(params)
    if error:
        return {"success": False, "error": error}
    
    # Determine target file path
    if not target_file:
        target_file = os.path.join(params['download_path'], f"{source_dataset}.dat")
    elif os.path.isdir(target_file):
        target_file = os.path.join(target_file, f"{source_dataset}.dat")
    
    ftplib.FTP.port = params['port']
    
    try:
        zftp = zosftplib.Zftp(params['host'], params['user'], params['password'], 
                             timeout=params['timeout'])
        zftp.download_binary(source_dataset, target_file)
        
        return {
            "success": True, 
            "source": source_dataset, 
            "target": target_file,
            "port_used": params['port']
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool(description="Download members from a partitioned dataset (PDS)")
def download_pds_members(dataset: str, target_dir: Optional[str] = None, 
                        members: str = '*', retr_mode: str = 'binary', 
                        ftp_threads: int = 1, batch_size: int = 5) -> dict:
    """Downloads members from a partitioned dataset (PDS) to a local directory."""
    params = _get_connection_params()
    error = _validate_connection(params)
    if error:
        return {"success": False, "error": error}
    
    if retr_mode not in ['binary', 'ascii']:
        return {"success": False, "error": "Invalid retr_mode. Must be 'binary' or 'ascii'."}
    
    target_dir = target_dir or params['download_path']
    os.makedirs(target_dir, exist_ok=True)
    
    ftplib.FTP.port = params['port']
    
    try:
        zftp = zosftplib.Zftp(params['host'], params['user'], params['password'], 
                             timeout=params['timeout'])
        
        pds_dir = zftp.get_pds_directory(dataset)
        member_list = list(pds_dir.keys())
        
        if members != '*':
            member_list = [m for m in member_list if fnmatch.fnmatch(m, members)]
        
        total_members = len(member_list)
        downloaded_members = []
        retr_param = 'BINARY' if retr_mode.lower() == 'binary' else 'LINES'
        
        for i in range(0, total_members, batch_size):
            batch = member_list[i:i+batch_size]
            zftp.get_members(dataset, target_dir, lmembers=batch, 
                           retr=retr_param, ftp_threads=ftp_threads)
            downloaded_members.extend(batch)
        
        return {
            "success": True, 
            "source": dataset,
            "target_dir": target_dir,
            "total_members": total_members,
            "downloaded_members": downloaded_members
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool(description="Get current connection information for the mainframe")
def get_connection_info() -> dict:
    """Returns the current connection information from environment variables."""
    params = _get_connection_params()
    return {
        "host": params['host'],
        "port": params['port'],
        "user": params['user'],
        "timeout": params['timeout'],
        "download_path": params['download_path'],
        "password_set": bool(params['password'])
    }

@mcp.tool(description="Set connection parameters for mainframe FTP")
def set_connection_params(host: str = None, port: int = None, 
                         user: str = None, password: str = None, 
                         timeout: float = None, download_path: str = None) -> dict:
    """Sets environment variables for mainframe FTP connection."""
    if host:
        os.environ['ZFTP_HOST'] = host
    if port:
        os.environ['ZFTP_PORT'] = str(port)
    if user:
        os.environ['ZFTP_USER'] = user
    if password:
        os.environ['ZFTP_PASSWORD'] = password
    if timeout:
        os.environ['ZFTP_TIMEOUT'] = str(timeout)
    if download_path:
        os.environ['ZFTP_DOWNLOAD_PATH'] = download_path
    
    return get_connection_info()

def run_server():
    """Start the MCP server."""
    params = _get_connection_params()
    
    print("Starting MainframeZOS MCP server...")
    print("Current connection settings:")
    print(f"  Host: {params['host'] or 'Not set'}")
    print(f"  Port: {params['port']}")
    print(f"  User: {params['user'] or 'Not set'}")
    print(f"  Password: {'Set' if params['password'] else 'Not set'}")
    print(f"  Timeout: {params['timeout']} seconds")
    print(f"  Download path: {params['download_path']}")
    print("Configure connection using set_connection_params tool or environment variables")
    
    mcp.run()

if __name__ == "__main__":
    run_server()
