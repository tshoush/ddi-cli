import sys
import os
import subprocess
from pathlib import Path

def is_in_virtualenv():
    """Check if running in a virtual environment."""
    return sys.prefix != sys.base_prefix

def main_cli():
    """The actual main function of the application."""
    from ddi.cli import main
    main()

if __name__ == "__main__":
    if is_in_virtualenv():
        main_cli()
    else:
        default_venv_path = Path.home() / "DDI-Apps" / "ddi-cli"
        
        # Prompt for Python executable
        python_executable_str = input(f"Enter Python executable path [{sys.executable}]: ")
        python_executable = python_executable_str if python_executable_str else sys.executable

        # Prompt for virtual environment path
        venv_path_str = input(f"Enter path for virtual environment [{default_venv_path}]: ")
        venv_path = Path(venv_path_str) if venv_path_str else default_venv_path
        
        venv_path.mkdir(parents=True, exist_ok=True)

        if not (venv_path / "bin" / "python").exists():
            print(f"Creating virtual environment in {venv_path} using {python_executable}...")
            subprocess.run([python_executable, "-m", "venv", str(venv_path)], check=True)
        
        print("Installing/updating dependencies...")
        pip_executable = str(venv_path / "bin" / "pip")
        subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True)
        
        print("Relaunching in virtual environment...")
        
        # On Windows, the executable is in Scripts/python.exe
        if sys.platform == "win32":
            venv_python = venv_path / "Scripts" / "python.exe"
        else:
            venv_python = venv_path / "bin" / "python"

        os.execv(venv_python, [str(venv_python), __file__] + sys.argv[1:])
