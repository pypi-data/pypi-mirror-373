from setuptools import find_packages, setup


# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# 依赖现在由 pyproject.toml 管理
def read_requirements():
    return []


setup(
    name="astroinsight",
    version="0.1.1",
    author="AstroInsight Team",
    author_email="contact@astroinsight.com",
    description=("AI-powered research paper assistant with multi-agent collaboration"),
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/astroinsight",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    license="MIT",
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=24.10.0",
            "flake8>=7.1.1",
            "mypy>=1.0.0",
            "twine>=4.0.0",
            "wheel>=0.40.0",
        ],
        "mcp": [
            "mcp>=1.0.0",
            "asyncio-mqtt>=0.16.0",
            "aiohttp>=3.8.0",
            "websockets>=11.0.0",
        ],
        "full": [
            "mcp>=1.0.0",
            "asyncio-mqtt>=0.16.0",
            "aiohttp>=3.8.0",
            "websockets>=11.0.0",
            "pytest>=7.0.0",
            "black>=24.10.0",
            "flake8>=7.1.1",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "astroinsight=astroinsight.cli:main",
            "astroinsight-mcp=astroinsight.mcp_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "astroinsight": ["templates/**/*", "config/*.yaml"],
    },
    keywords="ai, research, paper, multi-agent, collaboration, astroinsight",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/astroinsight/issues",
        "Source": "https://github.com/yourusername/astroinsight",
        "Documentation": "https://astroinsight.readthedocs.io/",
    },
)
