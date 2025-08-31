import os
from pathlib import Path

def _safe_copy_files():
    """
    Copies files from the init_files directory to the current working directory
    without overwriting existing files.
    """
    # Determine source and destination paths
    source_path = Path(__file__).parent / "init_files"
    source_path = source_path.resolve()
    dest_path = Path.cwd().resolve()
    print(f'\nInitializing directory "{dest_path}" from "{source_path}"')
    # list files in source directory
    source_files = os.listdir(source_path)
    # copy files
    for file in source_files:
        source_file = source_path / file
        dest_file = dest_path / file
        try:
            pure_file_name = os.path.basename(file)
            if not dest_file.exists():
                if source_file.is_file():
                    with open(source_file, "rb") as fsrc:
                        with open(dest_file, "wb") as fdst:
                            fdst.write(fsrc.read())
                            print(f'[OK]    file "{pure_file_name}" copied successfully.')
            else:
                print(f'[SKIP]  File "{pure_file_name}" already exists, skipping copy.')
        except Exception as err:
            print(f'[ERROR] Could not copy file "{source_file}" to "{dest_file}": {err}')   

def init():
    """
    Initializes the current working directory by copying necessary files from the
    init_files directory. Existing files are not overwritten.
    """
    try:
        _safe_copy_files()
        print("")
        print('[INFO]  Now you can start "02_jupyter.bat" (Windows) or')
        print('[INFO]  02_jupyter.sh (Linux/Mac) and open attached tutorials.')
        print('[INFO]  Or you can run main.py to see other usage examples.')
        print('[INFO]  Or simply start a shell/terminal and import and use')
        print('[INFO]  the package. type: "from uurest import *", then use')
        print('[INFO] fetch("https://www.example.com") to get started.')
        print("")
        print('[DONE]  Initialization completed successfully.')
    except Exception as err:
        print(f'\n[ERROR] Initialization failed: {err}')
        print("")
        raise
    #print(f"\n\nPreparing directory\n\n{os.getcwd()}\n{os.path.realpath(__file__)}\n\n")


init()
