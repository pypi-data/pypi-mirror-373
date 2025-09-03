import importlib.resources


version = "0.0.0"

version_file = importlib.resources.files("h2o_mlops") / "VERSION"
if version_file.is_file():
    version = version_file.read_text().strip()
