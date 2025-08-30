import importlib


def get_import(full_path_of_import):
    """Dynamically imports an object from a module given its full path.

    Args:
        full_path_of_import (str): The full path of the import (e.g., 'module.submodule.ClassName').

    Returns:
        object: The imported object.

    Raises:
        ImportError: If the module cannot be imported.
        AttributeError: If the attribute does not exist in the module.
    """
    if not full_path_of_import:
        raise ValueError("The import path cannot be empty.")

    parts = full_path_of_import.split('.')
    import_name = parts[-1]
    module_name = ".".join(parts[:-1]) if len(parts) > 1 else ""

    try:
        module = importlib.import_module(module_name)
        return getattr(module, import_name)
    except ModuleNotFoundError as e:
        raise ImportError(f"Module '{module_name}' could not be found.") from e
    except AttributeError as e:
        raise AttributeError(
            f"'{module_name}' has no attribute '{import_name}'") from e