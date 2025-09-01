import os
import json
import importlib.util
import importlib.resources
import inspect
from typing import Dict, Any


class JsonResourceLoader:
    """
    Loader for JSON configuration files.

    This class provides functionality to load JSON configuration files from the resources directory.
    It can load files from either a package, the file system, or absolute paths, with fallback behavior.
    By default, it will first look in the current working directory.

    Usage:
        # Create a JSON resource loader
        loader = JsonResourceLoader()

        # Load a JSON resource (will first look in current directory)
        config = loader.load_json_resource("config.json")

        # Load a JSON resource with an absolute path
        config = loader.load_json_resource("/path/to/my/config.json", is_absolute_path=True)

        # Load a JSON resource relative to caller
        config = loader.load_json_resource("config.json", relative_to_caller=True)
    """

    def __init__(self, resources_dir: str = None, package_name: str = None, resources_path: str = None,
                 check_current_dir_first: bool = True):
        """
        Initialize a new JsonResourceLoader.

        Args:
            resources_dir: Directory containing JSON resources. If None, defaults to 'resources'.
            package_name: Python package name containing resources. If None, defaults to 'shoebill_ai'.
            resources_path: Path within the package to resources. If None, defaults to 'resources'.
            check_current_dir_first: If True, look in the current working directory first before other locations.
        """
        # Get the base directory of the package
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Set default directories if not provided
        if resources_dir is None:
            resources_dir = os.path.join(base_dir, 'resources')
        if package_name is None:
            package_name = 'shoebill_ai'
        if resources_path is None:
            resources_path = 'resources'

        self.resources_dir = resources_dir
        self.package_name = package_name
        self.resources_path = resources_path
        self.check_current_dir_first = check_current_dir_first
        # Store project root directory for absolute path fallback
        self.project_root = os.path.dirname(os.path.dirname(base_dir))

    def load_json_resource(self, filename: str, is_absolute_path: bool = False,
                           relative_to_caller: bool = False) -> Dict[str, Any]:
        """
        Load a JSON resource file from package or file system.

        Args:
            filename: Name of the JSON file (with or without .json extension) or absolute path.
            is_absolute_path: If True, filename is treated as an absolute path.
            relative_to_caller: If True, path is treated as relative to the file that called this method.

        Returns:
            Dict[str, Any]: The loaded JSON data.

        Raises:
            ValueError: If the resource file cannot be found in any location.
        """
        original_filename = filename

        # Direct absolute path loading
        if is_absolute_path:
            if os.path.exists(filename) and os.path.isfile(filename):
                try:
                    with open(filename, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    raise ValueError(f"File is not valid JSON: {filename}")
            else:
                raise ValueError(f"Absolute path file not found: {filename}")

        # Add .json extension if not present and not an absolute path
        if not filename.endswith('.json') and not os.path.isabs(filename):
            filename_with_ext = f"{filename}.json"
        else:
            filename_with_ext = filename

        # Check current working directory first if enabled
        if self.check_current_dir_first:
            cwd_path = os.path.join(os.getcwd(), filename_with_ext)
            if os.path.exists(cwd_path) and os.path.isfile(cwd_path):
                try:
                    with open(cwd_path, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    raise ValueError(f"File is not valid JSON: {cwd_path}")

        # Relative to caller path loading
        if relative_to_caller:
            # Get the caller's frame (the method that called load_json_resource)
            caller_frame = inspect.currentframe().f_back
            caller_file = caller_frame.f_code.co_filename
            caller_dir = os.path.dirname(os.path.abspath(caller_file))

            # Create path relative to caller
            relative_path = os.path.join(caller_dir, filename_with_ext)
            if os.path.exists(relative_path):
                try:
                    with open(relative_path, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    raise ValueError(f"File is not valid JSON: {relative_path}")
            # We don't raise here because we want to try the other methods

        # First try to load from package
        try:
            # Construct the resource path within the package
            resource_path = os.path.join(self.resources_path, filename_with_ext)
            resource_path = resource_path.replace('\\', '/')  # Ensure forward slashes for package paths

            # Try to get the resource from the package
            package_spec = importlib.util.find_spec(self.package_name)
            if package_spec is not None:
                # Use importlib.resources to get the resource content
                resource_package = f"{self.package_name}.{os.path.dirname(resource_path)}"
                resource_name = os.path.basename(resource_path)

                # Handle different importlib.resources APIs based on Python version
                try:
                    # Python 3.9+
                    with importlib.resources.files(resource_package).joinpath(resource_name).open('r') as f:
                        return json.load(f)
                except (AttributeError, ImportError):
                    # Fallback for older Python versions
                    resource_text = importlib.resources.read_text(resource_package, resource_name)
                    return json.loads(resource_text)
        except (ImportError, ModuleNotFoundError, FileNotFoundError, ValueError):
            # If package loading fails, fall back to a file system
            pass

        # Fall back to a file system using resources_dir
        file_path = os.path.join(self.resources_dir, filename_with_ext)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                raise ValueError(f"File is not valid JSON: {file_path}")

        # Fall back to an absolute path from the project root
        try:
            absolute_path = os.path.join(self.project_root, 'resources', filename_with_ext)
            if os.path.exists(absolute_path):
                try:
                    with open(absolute_path, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    raise ValueError(f"File is not valid JSON: {absolute_path}")
        except Exception:
            # If the absolute path fallback fails, continue to the error
            pass

        # If we get here, the resource wasn't found in any location
        locations_tried = []

        if self.check_current_dir_first:
            locations_tried.append(f"current working directory '{os.getcwd()}'")

        if relative_to_caller:
            caller_frame = inspect.currentframe().f_back
            caller_file = caller_frame.f_code.co_filename
            caller_dir = os.path.dirname(os.path.abspath(caller_file))
            locations_tried.append(f"relative to caller '{caller_dir}'")

        locations_tried.extend([
            f"package '{self.package_name}'",
            f"directory '{self.resources_dir}'",
            f"absolute path from project root '{os.path.join(self.project_root, 'resources')}'"
        ])

        raise ValueError(
            f"Resource file not found: {original_filename} (tried {', '.join(locations_tried)})"
        )