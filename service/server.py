# server.py
from enum import Enum
from zipfile import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)
import git
from pydantic import BaseModel, Field

class Git_NewBranch(BaseModel):
    """
    Model to check out a git branch.
    """
    task_type: str 
    task_code: str 
    task_title: str
    
class GitTools(str, Enum):
    STATUS = "git_status"
    DIFF_UNSTAGED = "git_diff_unstaged"
    DIFF_STAGED = "git_diff_staged"
    DIFF = "git_diff"
    COMMIT = "git_commit"
    ADD = "git_add"
    RESET = "git_reset"
    LOG = "git_log"
    CREATE_BRANCH = "git_create_branch"
    CHECKOUT = "git_checkout"
    SHOW = "git_show"
    INIT = "git_init"
    BRANCH = "git_newbranch"


def checkout(task_type : str , task_code : str ,task_title : str ) -> str:
    """
    Check out the specified git branch.
    """
    branch_name = f"{task_type}#{task_code} : {task_title}"
    
    repo = git.Repo()
    repo.git.checkout(branch_name)
    return f"Checked out branch: {branch_name}"

async def ser(repository: Path | None) -> None:
    '''
    Run the MCP server
    '''
    server = Server("Specific workflow server")

    @server.list_tools()
    async def tool_list() -> list[Tool]:
        """
        List all available tools in the MCP server.
        """
        return [
            Tool(
                name=GitTools.CHECKOUT,
                description="Create a new git branch with the specified task type, code, and title",
                inputSchema=Git_NewBranch.model_json_schema(),
            ),
        ]
    
    @server.call_tool()
    async def call_tool(tool_name : str , argument : dict) -> list[TextContent]:
        """
        Call the prompt_branch_name tool with the provided parameters.
        """
        return TextContent(checkout(argument["task_type"], argument["type_code"], argument["task_title"]))

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run( read_stream, write_stream , options , raise_exceptions=True)
