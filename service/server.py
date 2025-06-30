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

class Get_Commit_Title(BaseModel):
    """
    Model to get the commit title for a specific task.
    """
    task_type: str
    task_code: str
    task_title: str

class Commit_Plan(BaseModel):
    """
    Model to commit a plan to the git repository.
    """
    project_name: str = Field(..., description="Name of the project")
    commit_title: str = Field(..., description="Title for the commit")

class WorkflowTools(str, Enum):
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
    BRANCH = "git_branch"
    COMMIT_PLAN = "commit_plan"
    GET_COMMIT_TITLE = "get_commit_title"

# Get the commit title for the specified task
def get_commit_title(repo : git.Repo , task_type : str , task_code : str ,task_title : str ) -> str:
    """
    Get the commit title for the specified task.
    """
    return f"{task_type}#{task_code} : {task_title}"

#Return Commit Plan Prompt
def commit_plan(commit_title : str , project_name : str) -> str:
    """
    Commit the plan to the git repository.
    """
    commit_plan = f'''You are an expert developer assistant. Your task is to help the user commit changes to a local repository by following these steps:

                    1. **Get the local repository path:**
                    - Check the gist named `project_repo_path.json` for a mapping from the supplied `project_name` to its local path.
                    - If the mapping exists, use the path. If not, ask the user to provide the local path for the project, then update `project_repo_path.json` with this new mapping.

                    2. **Move to the repository directory:**
                    - Use the command: `cd "<repo path>"` to change to the repository directory.

                    3. **Check and summarize changes:**
                    - Use git commands to check for change(git -P diff) and Summarize the changes as a commit detail message.

                    4. **Commit the changes:**
                    - Use the supplied `commit_title` as the commit message title, and the summarized details as the commit body.
                    - Run the appropriate git commands to add, commit, and (optionally) push the changes.

                    **If the project repo path does not exist in `project_repo_path.json`, always prompt the user for the path and update the mapping.**

                    **Example interaction:**
                    - User: commit-plan project_name="MyApp" commit_title="Fix login bug"
                    - Model: Looks up `MyApp` in `project_repo_path.json`. If not found, asks: "Please provide the local path for project 'MyApp'."
                    - Once path is provided, updates the mapping, changes directory, checks changes, summarizes, and commits as described above.

                    ###
                    User : 
                    project_name : {{project_name}}
                    commit_title : {{commit_title}}
                    '''
    return commit_plan.format(project_name=project_name, commit_title=commit_title)

# mcp server entry point
async def ser(repository: Path | None) -> None:
    '''
    Run the MCP server
    
    '''
    server = Server("Specific workflow server")

    if repository is not None:
        try:
            git.Repo(repository)
        except git.InvalidGitRepositoryError:
            return

    @server.list_tools()
    async def tool_list() -> list[Tool]:
        """
        List all available tools in the MCP server.
        """
        return [
            Tool(
                name=WorkflowTools.GET_COMMIT_TITLE,
                description="Get the commit title for the specified task.",
                inputSchema=Get_Commit_Title.model_json_schema(),
            ),
            Tool(
                name=WorkflowTools.COMMIT_PLAN,
                description="Commit plan that can follow the steps to commit changes to a local repository",
                inputSchema=Commit_Plan.model_json_schema(),
            ),
        ]
    
    @server.call_tool()
    async def call_tool(tool_name : str , argument : dict) -> list[TextContent]:
        """
        Call the prompt_branch_name tool with the provided parameters.
        """

        repo = git.Repo(argument["repo_path"])

        if(tool_name == WorkflowTools.GET_COMMIT_TITLE):
            return TextContent(get_commit_title(argument["task_type"], argument["type_code"], argument["task_title"]))
        if(tool_name == WorkflowTools.COMMIT_PLAN):
            return TextContent(commit_plan(argument["commit_title"], argument["project_name"]))

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run( read_stream, write_stream , options , raise_exceptions=True)
