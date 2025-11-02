def get_version() -> str:
    """Get the version of the package."""
    with open("pyproject.toml") as f:
        for line in f:
            if line.startswith("version = "):
                return line.split(" = ")[1].strip().strip('"')
    return "0.0.0"
