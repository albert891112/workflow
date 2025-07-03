

code_path = "C:\\承儒\\GitRepo\\MSD\\Web_Component\\MSD_API\\MsdAPI.csproj"
publish_destinationpath = "C:\\承儒\\GitRepo\\MSD\\Web_Component\\publish\\"
version = "v0.0.0.0"


def compress_code(publish_destinationpath: str, version: str) -> str:
    """
    Compress the code to the specified project repository.
    """
    import shutil
    import os

    # Ensure the destination directory exists
    os.makedirs(publish_destinationpath, exist_ok=True)

    # Define the zip file name
    zip_file_name = f"{publish_destinationpath}/ipa.zip"

    # Create a zip file from the code path
    shutil.make_archive(zip_file_name.replace('.zip', ''), 'zip', f"{publish_destinationpath}/{version}")

    return f"Code compressed and saved to {zip_file_name}"


print(compress_code(publish_destinationpath , version))