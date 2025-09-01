import json
from .json_resource_loader import JsonResourceLoader


class PromptLoader:
    """
    Loader for prompt configuration files.

    This class provides functionality to load prompt configuration files from JSON resources.
    It uses JsonResourceLoader to handle loading from various locations.
    By default, it will first look in the current working directory.

    Usage:
        # Create a prompt loader for a specific file (will look in current dir first)
        loader = PromptLoader("prompt_config.json")

        # Get a specific config value
        system_prompt = loader.get_config_value("system_prompt")

        # Get the entire config as a JSON string
        config_json = loader.get_entire_config()

        # Create a prompt loader with an absolute path
        loader = PromptLoader("/path/to/my/config.json", is_absolute_path=True)

        # Create a prompt loader with a path relative to the file that calls PromptLoader
        loader = PromptLoader("configs/prompt_config.json", relative_to_caller=True)

        # Disable checking current directory first
        loader = PromptLoader("prompt_config.json", check_current_dir_first=False)
    """

    def __init__(self, resource_name, is_absolute_path: bool = False, relative_to_caller: bool = False,
                 resources_dir: str = None, package_name: str = None, resources_path: str = None,
                 check_current_dir_first: bool = True):
        """
        Initialize a new PromptLoader.

        Args:
            resource_name: Name of the JSON resource file (with or without .json extension) or path.
            is_absolute_path: If True, resource_name is treated as an absolute path.
            relative_to_caller: If True, resource_name is treated as relative to the file that called this method.
            resources_dir: Directory containing JSON resources. If None, JsonResourceLoader uses its default.
            package_name: Python package name containing resources. If None, JsonResourceLoader uses its default.
            resources_path: Path within the package to resources. If None, JsonResourceLoader uses its default.
            check_current_dir_first: If True, look in the current working directory first before other locations.
        """
        # Use JsonResourceLoader to load the resource with the specified loading strategy
        json_loader = JsonResourceLoader(
            resources_dir=resources_dir,
            package_name=package_name,
            resources_path=resources_path,
            check_current_dir_first=check_current_dir_first
        )

        # Pass along the loading strategy parameters
        self.config = json_loader.load_json_resource(
            resource_name,
            is_absolute_path=is_absolute_path,
            relative_to_caller=relative_to_caller
        )

    def get_config_value(self, key):
        """
        Get a specific value from the config.

        Args:
            key: The key to look up in the config.

        Returns:
            The value associated with the key, or None if the key doesn't exist.
        """
        return self.config.get(key)

    def get_entire_config(self):
        """
        Get the entire config as a JSON string.

        Returns:
            str: The entire config as a formatted JSON string.
        """
        return json.dumps(self.config, indent=2)