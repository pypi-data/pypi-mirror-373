from setuptools import setup, find_packages
import os
import sys
import ast
import importlib.util
from pathlib import Path

# -------------------------------
# Configuración general
# -------------------------------
VERSION = "3.0.0"
PACKAGE_NAME = "pyhelper-tools-jbhm"
DESCRIPTION = "A centralized toolkit for Python developers"
AUTHOR = "Juan Braian Hernandez Morani"

# Leer README principal desde la carpeta readme
readme_dir = Path("readme")
main_readme_path = readme_dir / "README.md"
try:
    with open(main_readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Helper - A centralized toolkit for Python developers"

# -------------------------------
# Definir lenguajes soportados
# -------------------------------
LANGUAGES = [
    "af","sq","am","ar","hy","as","ay","az","bm","eu","be","bn","bho","bs","bg","ca","ceb","ny","zh","co","hr","cs","da","dv",
    "doi","nl","en","eo","et","ee","tl","fi","fr","fy","gl","ka","de","el","gn","gu","ht","ha","haw","iw","hi","hmn","hu","is",
    "ig","ilo","id","ga","it","ja","jw","kn","kk","km","rw","gom","ko","kri","ku","ckb","ky","lo","la","lv","ln","lt","lg","lb",
    "mk","mai","mg","ms","ml","mt","mi","mr","lus","mn","my","ne","no","or","om","ps","fa","pl","pt","pa","qu","ro","ru","sm",
    "sa","gd","nso","sr","st","sn","sd","si","sk","sl","so","es","su","sw","sv","tg","ta","tt","te","th","ti","ts","tr","tk",
    "ak","uk","ur","ug","uz","vi","cy","xh","yi","yo","zu"
]
lang_files = [f"lang/{lang}.json" for lang in LANGUAGES]

# -------------------------------
# Recolector de dependencias
# -------------------------------
STD_LIB = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else {
    "sys","os","re","math","ast","json","time","typing","threading","subprocess","csv","datetime","inspect","struct","pathlib"
}

NAME_MAP = {
    "sklearn": "scikit-learn",
    "cpuinfo": "py-cpuinfo",
    "IPython": "ipython",
    "sqlalchemy": "SQLAlchemy",
}

INTERNAL_MODULES = {
    "core","submodules","helper","shared","statics","timer","manager","graph","caller","checker",
    "DBManager","pyswitch","progress_bar","complexity_analyzer"
}

def find_imports_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()

    try:
        tree = ast.parse(src, filename=filepath)
    except SyntaxError:
        imports = set()
        for line in src.splitlines():
            line = line.lstrip()
            if line.startswith("import ") or line.startswith("from "):
                parts = line.split()
                if parts[0] == "import":
                    imports.add(parts[1].split(".")[0])
                elif parts[0] == "from":
                    imports.add(parts[1].split(".")[0])
        return imports, []

    imports = set()
    conditional = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node): return
        def visit_ClassDef(self, node): return

        def visit_If(self, node):
            test_src = ast.unparse(node.test) if hasattr(ast, "unparse") else ""
            platforms = []
            if any(x in test_src for x in ["platform.system", "sys.platform", "os.name"]):
                for n in ast.walk(node.test):
                    if isinstance(n, ast.Constant) and isinstance(n.value, str):
                        platforms.append(n.value)
            for subnode in node.body:
                if isinstance(subnode, ast.Import):
                    for alias in subnode.names:
                        pkg = alias.name.split(".")[0]
                        if platforms:
                            conditional.append((pkg, platforms))
                        else:
                            imports.add(pkg)
                elif isinstance(subnode, ast.ImportFrom) and subnode.module:
                    pkg = subnode.module.split(".")[0]
                    if platforms:
                        conditional.append((pkg, platforms))
                    else:
                        imports.add(pkg)
            self.generic_visit(node)

        def visit_Import(self, node):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])

        def visit_ImportFrom(self, node):
            if node.module:
                imports.add(node.module.split(".")[0])

    Visitor().visit(tree)
    return imports, conditional

def collect_all_imports(target_dir="helper"):
    raw_imports = set()
    conditional_map = {}
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                imports, conditionals = find_imports_in_file(path)
                raw_imports.update(imports)
                for pkg, platforms in conditionals:
                    conditional_map.setdefault(pkg, set()).update(platforms)
    return sorted(raw_imports), conditional_map

raw_deps, conditional_map = collect_all_imports("helper")

base_requires = []
for pkg in raw_deps:
    if pkg in STD_LIB or pkg in INTERNAL_MODULES:
        continue
    base_requires.append(NAME_MAP.get(pkg, pkg))

platform_marker_deps = []
for pkg, platforms in conditional_map.items():
    if pkg in STD_LIB or pkg in INTERNAL_MODULES:
        continue
    pip_name = NAME_MAP.get(pkg, pkg)
    platforms = [p.lower() for p in platforms]
    if "linux" in platforms:
        platform_marker_deps.append(f"{pip_name}; sys_platform == 'linux'")
    if "windows" in platforms:
        platform_marker_deps.append(f"{pip_name}; sys_platform == 'win32'")
    if "darwin" in platforms:
        platform_marker_deps.append(f"{pip_name}; sys_platform == 'darwin'")

if "psycopg2" in base_requires:
    base_requires = ["psycopg2-binary" if p == "psycopg2" else p for p in base_requires]

install_requires = sorted(set(base_requires + platform_marker_deps))

extras_require = {
    "linux": ["pyamdgpuinfo"],
    "windows": ["wmi"],
    "macos": []
}

# -------------------------------
# Pre-flight check (warnings)
# -------------------------------
all_pip_names = set(NAME_MAP.values()) | set(install_requires)
unknowns = []
for dep in base_requires:
    if dep not in all_pip_names:
        unknowns.append(dep)

if unknowns:
    print("\n[WARNING] The following dependencies were detected but not confirmed in NAME_MAP or install_requires:")
    for dep in unknowns:
        print(f"   - {dep}")
    print("Make sure these are valid PyPI package names before uploading.\n")

# -------------------------------
# Archivos adicionales
# -------------------------------
readme_files = []
if readme_dir.exists():
    for file in readme_dir.iterdir():
        if file.is_file() and file.suffix in [".md", ".txt", ".rst"]:
            readme_files.append(f"readme/{file.name}")

# -------------------------------
# Setup final
# -------------------------------
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        "helper": lang_files + readme_files
    },
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires=">=3.8"
)
