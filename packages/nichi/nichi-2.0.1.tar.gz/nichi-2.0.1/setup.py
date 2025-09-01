from setuptools import setup, find_packages
from pathlib import Path


def load_requirements():
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []


def load_readme():
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return "A comprehensive tool for organizing video files, converting VTT subtitles to SRT format, and translating SRT files using Google Gemini AI."


setup(
    name="nichi",
    version="2.0.1",
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
    url="https://github.com/hdytrfli/nichi",
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
