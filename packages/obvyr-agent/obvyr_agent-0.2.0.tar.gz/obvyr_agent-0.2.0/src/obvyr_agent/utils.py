import toml


def get_project_config(pyproject_path: str = "pyproject.toml") -> dict:
    try:
        with open(pyproject_path, "r") as file:
            config = toml.load(file)
            return config["tool"]["poetry"]
    except (KeyError, FileNotFoundError) as e:
        raise RuntimeError(
            "Could not fetch project version from pyproject.toml"
        ) from e
