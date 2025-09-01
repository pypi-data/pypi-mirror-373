from setuptools import find_packages, setup

setup(
    name="markitdown-pro",
    version="1.1.1",
    author="Developer",
    description="A package that converts almost any file format to Markdown.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(
        exclude=["tests", "tests/*", ".venv", ".venv/*", ".vscode", ".vscode/*"]
    ),
    python_requires=">=3.12.2",
    install_requires=[
        "aiohttp",
        "requests",
        "httpx",
        "python-dotenv",
        "ffmpeg",
        "pandoc",
        "PyMuPDF",
        "whisper",
        "markitdown[all]",
        "huggingface_hub[hf_xet]",
        "unstructured[all-docs]",
        "langchain-core==0.3.74",
        "langchain-openai==0.3.29",
        "azure-ai-documentintelligence==1.0.2",
        "azure-cognitiveservices-speech==1.42.0",
        "chardet==5.2.0",
        "nbformat",
        "youtube-transcript-api",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
