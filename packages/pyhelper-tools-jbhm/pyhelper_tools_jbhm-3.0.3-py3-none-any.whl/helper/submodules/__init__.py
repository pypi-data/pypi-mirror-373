import os
import importlib
import inspect
from typing import Set, Dict, Any
from .shared import t

__version__ = "3.0.3"

_submodules_dir = os.path.dirname(__file__)

_EXCLUDED_FUNCTIONS = {}

def _is_exportable(name: str, obj: Any) -> bool:
    return (
        callable(obj)
        and not name.startswith("_")
        and name not in _EXCLUDED_FUNCTIONS
        and inspect.getmodule(obj) is not None
    )

def package_info():
    
    # Obtener la configuración de módulos desde las traducciones
    modules_config = t("package_info", return_raw=True).get("modules", {})
    
    # Construir la lista de módulos
    modules_list = "\n".join([
        f"- {module_name}: {module_desc}"
        for module_name, module_desc in modules_config.items()
    ])
    
    # Usar la plantilla con variables
    return t("package_info", 
        package=__package__,
        version=__version__,
        description=t("package_info", return_raw=True).get("description", ""),
        modules_list=modules_list,
        function_count=len(__all__)
    )


_exported_functions: Dict[str, Any] = {}

for filename in os.listdir(_submodules_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        try:
            module = importlib.import_module(f".{module_name}", package=__package__)

            for name, obj in vars(module).items():
                if _is_exportable(name, obj):
                    _exported_functions[name] = obj

        except ImportError as e:
            print(f"Warning: Could not import module {module_name}: {str(e)}")
            continue

globals().update(_exported_functions)

__all__ = sorted(_exported_functions.keys())