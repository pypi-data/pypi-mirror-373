from setuptools import setup, find_packages

setup(
    name="volute-xls",
    version="1.4.0",
    description="MCP server for Excel integration and local file manipulation in AI applications",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Coritan",
    author_email="your-email@example.com",
    url="https://gitlab.com/coritan/volute-xls",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastmcp>=2.0.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "openpyxl>=3.0.0",
        "Pillow>=9.0.0",
        "xlwings>=0.30.0",
        "pywin32>=306;platform_system=='Windows'",
    ],
    extras_require={
        "windows": [
            "xlwings>=0.30.0",
            "pywin32>=306;platform_system=='Windows'",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
        "full": [
            "xlwings>=0.30.0",
            "pywin32>=306;platform_system=='Windows'",
        ]
    },
    entry_points={
        "console_scripts": [
            "volute-xls-server=volute_xls.server:main",
            "volute-xls-local=volute_xls.server_local:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux", 
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    keywords="mcp excel ai agents desktop automation xlwings multimodal openpyxl",
)
