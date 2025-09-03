from setuptools import setup, find_packages

setup(
    name="notion-to-markdown",
    version="0.1.5",
    packages=find_packages(),
    install_requires=[
        "httpx",
        "pytablewriter",
        "notion-client",
    ],
    extras_require={
        "async": [
            "asyncio",
        ]
    },
    description="A package to convert Notion content into Markdown format",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/atb00ker/notion-to-markdown",
    author="Ajay Tripathi",
    author_email="ajay39in@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="Convert,Notion,Markdown",
    project_urls={
        "Bug Tracker": "https://github.com/atb00ker/notion-to-markdown/issues",
        "Source Code": "https://github.com/atb00ker/notion-to-markdown",
    },
)
