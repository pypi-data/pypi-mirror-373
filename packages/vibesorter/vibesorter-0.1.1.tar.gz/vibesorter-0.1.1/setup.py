from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="vibesorter",
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="Sort arrays using LLMs with structured output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yazan-Hamdan/vibesorter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    keywords="llm, sorting, langchain, ai, structured-output",
    project_urls={
        "Bug Reports": "https://github.com/Yazan-Hamdan/vibesorter/issues",
        "Source": "https://github.com/Yazan-Hamdan/vibesorter",
        "Documentation": "https://github.com/Yazan-Hamdan/vibesorter#readme",
    },
)