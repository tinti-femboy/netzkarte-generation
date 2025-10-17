import importlib.metadata
import sys

def check_dependencies(required_packages):
    missing = []
    for package in required_packages:
        try:
            version = importlib.metadata.version(package)
            print(f"{package}=={version} is installed.")
        except importlib.metadata.PackageNotFoundError:
            missing.append(package)
            print(f"{package} is NOT installed.")

    if missing:
        print("\nMissing packages:")
        for package in missing:
            print(f"- {package}")
        sys.exit(1)
    else:
        print("\nAll dependencies are installed.")

