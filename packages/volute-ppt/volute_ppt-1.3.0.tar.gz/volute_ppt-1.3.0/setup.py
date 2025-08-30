from setuptools import setup, find_packages

setup(
    name="volute-ppt",
    version="1.3.0",
    description="MCP server for PowerPoint integration and local file manipulation in AI applications",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Coritan",
    author_email="your-email@example.com",
    url="https://gitlab.com/coritan/volute-ppt",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastmcp>=2.0.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "python-pptx>=0.6.21",
        "Pillow>=9.0.0",
        "pywin32>=306;platform_system=='Windows'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "volute-ppt-server=volute_ppt.server:main",
            "volute-ppt-local=volute_ppt.server_local:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    keywords="mcp powerpoint ai agents desktop automation com",
)
