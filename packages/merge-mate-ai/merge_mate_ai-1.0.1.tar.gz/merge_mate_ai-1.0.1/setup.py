from setuptools import setup, find_packages

# --- Helper to read README ---
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "An AI-powered co-pilot for resolving Git merge conflicts."

# --- Helper to read requirements ---
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        return [
            "python-dotenv",
            "google-generativeai",
            "rich",
            "textual",
        ]

setup(
    name="merge-mate-ai",  # PyPI / pip install name
    version="1.0.1",
    author="Shashank Chakraborty",
    author_email="shashankchakraborty712005@gmail.com",
    description="An AI-powered co-pilot for resolving Git merge conflicts.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Shashank0701-byte/GIT_MERGE",
    license="MIT",
    packages=find_packages(include=["merge_mate", "merge_mate.*"]),
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "merge-mate = merge_mate.main:main",        # CLI entry → merge_mate/main.py
            "merge-mate-tui = merge_mate.merge_mate_tui:main",  # CLI entry → merge_mate/merge_mate_tui.py
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
