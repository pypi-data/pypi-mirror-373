from pathlib import Path
from setuptools import setup, find_packages
import ast


def load_requirements():
    """Load requirements from requirements.txt, filtering out comments and empty lines."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []


def load_readme():
    readme_file = Path(__file__).parent / "readme.md"
    if readme_file.exists():
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def get_package_metadata():
    """Extract all metadata from __init__.py without importing it."""
    init_file = Path(__file__).parent / "src" / "nichi" / "__init__.py"
    with open(init_file, "r", encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content)

    metadata = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith("__"):
                    if isinstance(node.value, ast.Constant):  # Python 3.8+
                        metadata[target.id] = node.value.value
                    elif isinstance(node.value, ast.Str):  # Older Python versions
                        metadata[target.id] = node.value.s

    return metadata


# Get metadata from __init__.py
metadata = get_package_metadata()

setup(
    name="nichi",
    version=metadata["__version__"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=load_requirements(),
    entry_points={
        "console_scripts": [
            "nichi=nichi.main:main",
        ],
    },
    python_requires=">=3.8",
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    keywords="video, subtitles, translation, organization, vtt, srt, gemini",
    url=metadata["__url__"],
    description=metadata["__description__"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ],
    include_package_data=True,
    zip_safe=False,
)
