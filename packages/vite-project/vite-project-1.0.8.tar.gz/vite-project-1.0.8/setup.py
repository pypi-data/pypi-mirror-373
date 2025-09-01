from setuptools import setup
from pathlib import Path

cwd = Path(__file__).parent
long_description = (cwd / "README.md").read_text()
setup(
  name="vite-project",
  version="1.0.8",
  package_dir={"vite_project": "dist"},
  package_data={"vite_project": ["**/*.*"]},
  long_description=long_description,
  long_description_content_type="text/markdown"
)
