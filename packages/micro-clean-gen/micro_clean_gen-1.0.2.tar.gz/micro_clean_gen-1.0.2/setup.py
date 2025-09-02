"""
微服务代码生成器 - 打包配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取版本信息
with open("VERSION", "r", encoding="utf-8") as fh:
    version = fh.read().strip()

# 读取requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="micro-clean-gen",
    version=version,
    author="Ray",
    author_email="ray@rayainfo.cn",
    description="基于整洁架构的事件驱动微服务代码生成器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DotNetAge/micro-gen",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "micro-gen=micro_gen.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "micro_gen": [
            "templates/*.tmpl",
            "templates/**/*.tmpl",
            "core/templates/*.tmpl",
            "core/templates/**/*.tmpl",
            "examples/*.yaml",
            "examples/*.yml",
        ],
    },
    keywords="microservice, clean-architecture, code-generator, event-driven, ddd",
    project_urls={
        "Bug Reports": "https://github.com/DotNetAge/micro-gen/issues",
        "Source": "https://github.com/DotNetAge/micro-gen",
        "Documentation": "https://micro-gen.readthedocs.io/",
    },
)
