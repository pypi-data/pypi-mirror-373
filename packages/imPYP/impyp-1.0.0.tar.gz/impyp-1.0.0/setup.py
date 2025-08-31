from setuptools import setup, find_packages

setup(
    name="imPYP",
    version="1.0.0",
    description="Python library installer/uninstaller",
    author="KsDev",
    packages=find_packages(),
    install_requires=[
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "impyp=impyp.core:start",
        ],
    },
    python_requires=">=3.8",
)