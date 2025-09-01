import ast
import sys
import importlib.util
import importlib.metadata

def resolve_import(import_name) -> str:
    try:
        packages = importlib.metadata.packages_distributions()
        distributions = packages.get(import_name, [])
        return distributions[0] if distributions else import_name
    except Exception:
        return import_name

def resolve_package_version(package_name:str) -> None | str:
    try:
        version = importlib.metadata.version(package_name)
        return version
    except importlib.metadata.PackageNotFoundError:
        return None
    
def is_builtin_module(module_name:str) -> bool:
    if module_name in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        if spec.origin == 'built-in':
            return True
        if 'site-packages' in spec.origin or 'dist-packages' in spec.origin:
            return False
        return True
    except ModuleNotFoundError:
        return False


def guess_pip_packages(file:str, exclude:list[str] = []) -> list[str]:
    with open(file) as f:
        python_code = f.read()

    tree = ast.parse(python_code)

    imports:list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for direct_import in node.names:
                imports.append(direct_import.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)

    packages = []

    imports = set( [imprt.split('.', maxsplit=1)[0] for imprt in imports])

    for imprt in imports:
        package = resolve_import(imprt)
        if is_builtin_module(package) or any(package == exclusion.split('==', maxsplit=1)[0] for exclusion in exclude):
            continue

        version = resolve_package_version(package)
        if version is not None:
            package += f'=={version}'

        packages.append(package)
 
    return packages