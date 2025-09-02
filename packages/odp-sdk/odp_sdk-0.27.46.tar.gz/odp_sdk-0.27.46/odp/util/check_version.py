import importlib.metadata
import importlib.util


def check_library_version(library_name: str):
    # Check if the library is present
    spec = importlib.util.find_spec(library_name)
    if spec is not None:
        # If present, get the version
        try:
            version = importlib.metadata.version(library_name)
            return version
        except importlib.metadata.PackageNotFoundError:
            pass
