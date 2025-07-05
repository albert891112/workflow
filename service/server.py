# server.py
import asyncio
from enum import Enum
from zipfile import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)
import git
import subprocess
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

class WebApp_Deploy(BaseModel):
    """
    Model to deploys a provided artifact to Azure Web Apps.
    """
    resource_group: str = Field(..., description="Name of the resource group")
    name: str = Field(..., description="Name of the webapp to deploy to")
    slot_name: str | None = Field(..., description="The name of the slot")
    src_path: str = Field(..., description="Path of the artifact to be deployed")
    subscription: str = Field(..., description="Subscription for the Azure account")
    target_path: str = Field(..., description="Absolute path that the artifact should be deployed to")
    type: str = Field(..., description="Type of the deployment artifact")
    restart: bool | None = Field(False, description="Whether to restart the webapp after deployment")
    isasync: bool | None = Field(False, description="If true, the artifact is deployed asynchronously")

class Code_Publish(BaseModel):
    """
    Model to publish the code to the specified project repository.
    """
    code_path: str = Field(..., description="Path of the code to be published")
    publish_destinationpath: str = Field(..., description="Destination path for the published code")
    version: str = Field(..., description="Version of the code being published")

class Compress_Code(BaseModel):
    """
    Model to compress the code to the specified project repository.
    """
    publish_destinationpath: str = Field(..., description="Destination path for the published code")
    version: str = Field(..., description="Version of the code being published")


class WorkflowTools(str, Enum):
    COMMIT_PLAN = "commit_plan"
    GET_COMMIT_TITLE = "get_commit_title"
    WEBAPP_DEPLOY = "webapp_deploy"
    CODE_PUBLISH = "code_publish"
    COMPRESS_CODE = "compress_code"

# Get the commit title for the specified task
def get_commit_title(task_type : str , task_code : str ,task_title : str ) -> str:
    """
    Get the commit title for the specified task.
    """
    class Task_Type(str, Enum):
        FEATURE = "feature"
        BUGFIX = "bugfix"

    icon = ""

    if task_type == Task_Type.FEATURE:
        icon = "✨"
    elif task_type == Task_Type.BUGFIX:
        icon = "🐛"

    return f"{icon}{task_type}#{task_code} : {task_title}"

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

# Model to deploys a provided artifact to Azure Web Apps.
def webapp_deploy(resource_group: str, name: str, src_path: str, subscription: str, target_path: str, type: str, slot_name: str | None , restart: bool | None , isasync : bool | None ) -> str:
    """
    Model to deploys a provided artifact to Azure Web Apps.
    """
    command = [
        "az", "webapp", "deploy",
        "--resource-group", resource_group,
        "--name", name,
        "--src-path", src_path,
        "--subscription", subscription,
        "--target-path", target_path,
        "--type", type,
    ]

    # Add optional parameters if they are provided
    if slot_name is not None:
        command.append("--slot")
        command.append(slot_name)
    if isasync is not None:
        command.append("--async" )
        command.append(str(isasync).lower())
    if restart is not None:
        command.append("--restart")
        command.append(str(restart).lower())

    result =  subprocess.run(command, capture_output=True, text=True , shell=True)

    return result.stdout if result.returncode == 0 else result.stderr

def code_publish(code_path: str, publish_destinationpath: str , version : str) -> str:
    """
    Publish the code to the specified project repository.
    """
    command = [
        "dotnet", 
        "publish", code_path,
        "-c", "Release", 
        "-o", f"{publish_destinationpath}\{version}",
    ]

    return subprocess.run(command, capture_output=True, text=True, shell=True)

def compress_code(publish_destinationpath: str, version: str) -> str:
    """
    Compress the code to the specified project repository.
    """
    import shutil
    import os

    # Ensure the destination directory exists
    os.makedirs(publish_destinationpath, exist_ok=True)

    # Define the zip file name
    zip_file_name = f"{publish_destinationpath}/api.zip"

    # Create a zip file from the code path
    shutil.make_archive(zip_file_name.replace('.zip', ''), 'zip', f"{publish_destinationpath}/{version}")

    return f"Code compressed and saved to {zip_file_name}"
# mcp server entry point
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
                name=WorkflowTools.GET_COMMIT_TITLE,
                description="Get the commit title for the specified task.",
                inputSchema=Get_Commit_Title.model_json_schema(),
            ),
            Tool(
                name=WorkflowTools.COMMIT_PLAN,
                description="Commit plan that can follow the steps to commit changes to a local repository",
                inputSchema=Commit_Plan.model_json_schema(),
            ),
            Tool(
                name=WorkflowTools.WEBAPP_DEPLOY,
                description="Deploys a provided artifact to Azure Web Apps. This tool will take few minuts to complete.",
                inputSchema=WebApp_Deploy.model_json_schema(),
            ),
            Tool(
                name=WorkflowTools.CODE_PUBLISH,
                description="Publish the code to the specified project repository.",
                inputSchema=Code_Publish.model_json_schema(),
            ),
        ]
    
    @server.call_tool()
    async def call_tool(tool_name : str , argument : dict) -> list[TextContent]:
        """
        Call the prompt_branch_name tool with the provided parameters.
        """

        if(tool_name == WorkflowTools.GET_COMMIT_TITLE):
            return [TextContent(type="text", text=get_commit_title(argument["task_type"], argument["task_code"], argument["task_title"]))]
        
        if(tool_name == WorkflowTools.COMMIT_PLAN):
            return [TextContent(type="text", text=commit_plan(argument["commit_title"], argument["project_name"]))]
        
        if(tool_name == WorkflowTools.WEBAPP_DEPLOY):
            res = webapp_deploy(
                resource_group=argument["resource_group"],
                name=argument["name"],
                slot_name=argument.get("slot_name", None),
                src_path=argument["src_path"],
                subscription=argument["subscription"],
                target_path=argument["target_path"],
                type=argument["type"],
                restart=argument.get("restart", None),
                isasync=argument.get("isasync", None)

            )
            return [TextContent(type="text", text=res)]
        
        if(tool_name == WorkflowTools.CODE_PUBLISH):
            res = code_publish(
                code_path=argument["code_path"],
                publish_destinationpath=argument["publish_destinationpath"],
                version=argument["version"]
            )
            return [TextContent(type="text", text=res)]
        
        if(tool_name == WorkflowTools.COMPRESS_CODE):
            res = compress_code(
                publish_destinationpath=argument["publish_destinationpath"],
                version=argument["version"]
            )
            return [TextContent(type="text", text=res)]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run( read_stream, write_stream , options , raise_exceptions=True)
