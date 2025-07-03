import subprocess

def webapp_deploy(resource_group: str, name: str, slot_name: str, src_path: str, subscription: str, target_path: str, type: str, restart: bool) -> str:
    """
    Model to deploys a provided artifact to Azure Web Apps.
    """
    command = [
        "az", "webapp", "deploy",
        "--resource-group", resource_group,
        "--name", name,
        "--slot", slot_name,
        "--src-path", src_path,
        "--subscription", subscription,
        "--target-path", target_path,
        "--type", type,
        "--restart", str(restart).lower()
    ]

    result = subprocess.run(command, capture_output=True, text=True , shell=True)

    return result.stdout if result.returncode == 0 else result.stderr




resource_group = "Component_RG_UAT"
name="ComponentAPIUAT"
slot_name="api-staging"
src_path="C:\承儒\GitRepo\MSD\Web_Component\publish\\api.zip"
subscription="3dace775-459d-446d-9471-020705d62c12"
target_path="v0.0.0.0"
type="zip"
restart = False

res = webapp_deploy(resource_group , name, slot_name, src_path, subscription, target_path, type, restart)

print(res)


