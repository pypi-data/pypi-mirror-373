"""
Template management for Mini Control Arena.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def copy_template(
    template_name: str,
    destination: str,
    overwrite: bool = False
) -> None:
    """Copy a template environment to a user-specified directory.
    
    This function copies a pre-configured evaluation environment template
    to a destination directory where users can customize it for their
    specific evaluation needs.
    
    Args:
        template_name: Name of the template to copy (e.g., "apps")
        destination: Path where the template should be copied
        overwrite: If True, overwrite existing directory. If False, raise error if directory exists
        
    Raises:
        ValueError: If the template doesn't exist
        FileExistsError: If destination exists and overwrite=False
        
    Examples:
        ```python
        copy_template("apps", "./my-custom-apps")
        # Output: Copied template 'apps' to my-custom-apps
        # You can now customize the files and run:
        # run_eval(environment_dir="./my-custom-apps", model="gpt-4", environment_mode="honest")
        
        # To overwrite existing directory
        copy_template("apps", "./my-custom-apps", overwrite=True)
        ```
    """
    # Get the templates directory
    # __file__ is in src/mini_control_arena/, we need to go up 2 more levels
    package_dir = Path(__file__).parent.parent.parent
    template_dir = package_dir / "templates" / template_name
    
    if not template_dir.exists():
        raise ValueError(f"Template '{template_name}' not found")
    
    # Create destination directory
    dest_path = Path(destination)
    
    # Check if destination exists
    if dest_path.exists() and not overwrite:
        print(f"Directory '{destination}' already exists. Skipping copy.")
        return
    
    # If overwrite is True and directory exists, remove it first
    if dest_path.exists() and overwrite:
        shutil.rmtree(dest_path)
        print(f"Removed existing directory: {dest_path}")
    
    # Copy the entire template directory
    # For APPS, exclude data (will be downloaded), but bash needs its data
    def ignore_files(
        dir_path,
        names
    ):
        """Ignore data directory only for apps template."""
        if template_name == "apps" and Path(dir_path).name == template_name:
            return ['data']
        return []
    
    shutil.copytree(template_dir, dest_path, dirs_exist_ok=False, ignore=ignore_files)
    
    print(f"Copied template '{template_name}' to {dest_path}")
    
    # Check if prepare_dataset.py exists
    prepare_script = dest_path / "prepare_dataset.py"
    if prepare_script.exists():
        print(f"\nPreparing dataset...")
        try:
            # Run prepare_dataset.py in the destination directory
            result = subprocess.run(
                [sys.executable, "prepare_dataset.py"],
                cwd=dest_path,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode == 0:
                # Show the output from prepare_dataset.py which includes statistics
                if result.stdout:
                    print(result.stdout)
                else:
                    print("Dataset prepared successfully!")
            else:
                print(f"Warning: Dataset preparation failed with error:")
                print(result.stderr)
                print(f"\nYou can manually prepare the dataset by running:")
                print(f"  cd {destination}")
                print(f"  python prepare_dataset.py")
        except subprocess.TimeoutExpired:
            print("Dataset preparation timed out.")
            print(f"You can manually prepare the dataset by running:")
            print(f"  cd {destination}")
            print(f"  python prepare_dataset.py")
        except Exception as e:
            print(f"Could not automatically prepare dataset: {e}")
            print(f"You can manually prepare the dataset by running:")
            print(f"  cd {destination}")
            print(f"  python prepare_dataset.py")