from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ugmm",
    version="1.0.0",
    author="Barrett Becker",
    author_email="barrettbecker@gmail.com",
    description="Universal Gun Mod Manager - A plugin-based mod manager for games",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ugmm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "customtkinter>=5.0.0",
        "CTkListbox>=0.5",
        "vdf>=3.4",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "ugmm=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md"],
    },
)
