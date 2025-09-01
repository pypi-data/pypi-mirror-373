from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo MCP Server", version="0.1.0")

# ---------------------------
# Tools
# ---------------------------

@mcp.tool()
def add(a: int, b: int) -> int:
    """Return a + b."""
    return a + b

class Echo(BaseModel):
    text: str = Field(..., description="Arbitrary text")
    upper: bool = Field(False, description="Return uppercase if true")

@mcp.tool()
def echo(payload: Echo) -> str:
    """Echo back your text; uppercase if requested."""
    return payload.text.upper() if payload.upper else payload.text

@mcp.tool()
def list_dir(path: str = ".") -> List[str]:
    """List files and folders at a path."""
    p = Path(path).expanduser().resolve()
    return sorted([c.name for c in p.iterdir()])

@mcp.tool()
def read_file(path: str) -> str:
    """Read a small UTF-8 text file."""
    p = Path(path).expanduser().resolve()
    return p.read_text(encoding="utf-8")

# ---------------------------
# Resources (URI-addressable)
# ---------------------------

@mcp.resource("file://{path}")
def file_resource(path: str) -> str:
    """
    Expose a file as a resource, e.g. file:///etc/hosts or file://~/notes.txt
    """
    p = Path(path).expanduser().resolve()
    return p.read_text(encoding="utf-8")

# ---------------------------
# Prompts (templated snippets)
# ---------------------------

@mcp.prompt("greet")
def greet_prompt(name: str = "world") -> str:
    """
    A small prompt snippet the client can insert into a chat.
    """
    return f"Please greet {name} in a friendly, concise way."
