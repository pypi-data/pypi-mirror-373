from setuptools import find_packages, setup


# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# 读取requirements.txt
def read_requirements():
    try:
        with open("requirements-minimal.txt", "r", encoding="utf-8") as fh:
            return [
                line.strip()
                for line in fh
                if line.strip() and not line.strip().startswith("#")
            ]
    except FileNotFoundError:
        # 如果找不到最小化版本，回退到原始版本
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [
                line.strip()
                for line in fh
                if (
                    line.strip()
                    and not line.strip().startswith("#")
                    and not line.strip().startswith("-e")
                )
            ]


setup(
    name="astroinsight",
    version="0.1.0",
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
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
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
    },
    entry_points={
        "console_scripts": [
            "astroinsight=astroinsight.cli:main",
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
