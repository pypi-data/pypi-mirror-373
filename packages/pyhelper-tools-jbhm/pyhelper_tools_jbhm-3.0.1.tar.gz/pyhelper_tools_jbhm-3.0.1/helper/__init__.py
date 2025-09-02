import importlib
import pkgutil

__version__ = "3.0.1"

# Mapeo de nombres ya cargados (para cache)
_loaded_attrs = {}

# --- Descubrir todos los submódulos (core y submodules) ---
# Esto recorre helper/ y helper/submodules/
_package_name = __name__
_package_path = __path__[0]

_all_symbols = set()

def _discover_symbols():
    """
    Descubre todas las funciones, clases y variables públicas de core y submodules
    para ofrecer autocompletado y acceso directo.
    """
    # Primero cargar core
    try:
        core = importlib.import_module(f"{_package_name}.core")
        for name in getattr(core, "__all__", dir(core)):
            if not name.startswith("_"):
                _all_symbols.add(name)
                _loaded_attrs[name] = getattr(core, name)
    except ImportError:
        pass

    # Luego recorrer submodules dinámicamente
    try:
        submodules_pkg = f"{_package_name}.submodules"
        pkg = importlib.import_module(submodules_pkg)
        if hasattr(pkg, "__path__"):
            for _, modname, _ in pkgutil.iter_modules(pkg.__path__, pkg.__name__ + "."):
                try:
                    mod = importlib.import_module(modname)
                    for name in getattr(mod, "__all__", dir(mod)):
                        if not name.startswith("_"):
                            _all_symbols.add(name)
                            _loaded_attrs[name] = getattr(mod, name)
                except ImportError:
                    # Si no se puede importar un submódulo (dependencia opcional faltante), se omite
                    continue
    except ImportError:
        pass

# Descubrimos una vez (no fuerza a importar todo, solo explora)
_discover_symbols()

def __getattr__(name):
    """
    Permite acceder a cualquier símbolo (función, clase, variable) desde helper directamente.
    Lazy load real: si alguien accede a un nombre no cacheado, intentamos cargarlo dinámicamente.
    """
    if name in _loaded_attrs:
        return _loaded_attrs[name]

    # Intentar carga perezosa (por si se agregaron nuevos submódulos)
    for modname in [_package_name + ".core", _package_name + ".submodules"]:
        try:
            mod = importlib.import_module(modname)
            if hasattr(mod, name):
                obj = getattr(mod, name)
                _loaded_attrs[name] = obj
                return obj
        except ImportError:
            continue

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__():
    """
    Ayuda al autocompletado de IDEs.
    """
    return sorted(list(globals().keys()) + list(_all_symbols))
