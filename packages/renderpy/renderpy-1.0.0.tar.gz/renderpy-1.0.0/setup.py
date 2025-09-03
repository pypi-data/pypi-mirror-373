from setuptools import setup, find_packages

setup(
    name="renderpy",
    version="1.0.0",
    description="Render CLI in Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Arsan Codifire",
    url="https://github.com/ArsanCodifire/Render-PyCLI",  # replace with your repo link
    packages=find_packages(),
    install_requires=[
        "typer",
        "httpx",
        "rich",
        "textual"
    ],
    entry_points={
        "console_scripts": [
            "renderpy=renderpy.cli:app"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
