import os
from setuptools import setup, find_packages

# Get the base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Path to requirements.txt
requirements_path = os.path.join(BASE_DIR, "requirements.txt")

# Path to README.md
readme_path = os.path.join(BASE_DIR, "README.md")

# Read requirements safely
with open(requirements_path, encoding="utf-8") as f:
    requirements = f.read().splitlines()

# Read long description safely
with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="llm_multiprovider",
    version="0.1.32",
    packages=find_packages(where="src"),  # Match the "src" directory structure
    package_dir={"": "src"},  # Set "src" as the root directory
    install_requires=requirements,
    include_package_data=True,
    author="José Ángel Morell", 
    author_email="jose@closeknit.ai",
    description="LLM API for multiple model providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jamorell/llm_multiprovider",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    license="AGPL-3.0",
)

