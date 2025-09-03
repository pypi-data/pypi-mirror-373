from setuptools import setup, find_packages
import os

# 读取README.md内容作为long_description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

# 读取requirements.txt内容作为依赖列表
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="worth-calculator-mcp",
    version="0.1.0",
    author="Alvin",
    author_email="alvin@example.com",
    description="一个基于Zippland/worth-calculator的工作性价比计算工具，综合评估工作真实价值",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zippland/worth-calculator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "worth-calculator-mcp=worth_calculator_mcp:main",
        ],
    },
    py_modules=["worth_calculator_mcp"],
)