from setuptools import setup, find_packages
import os

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nipd-framework",
    version="1.0.0",
    author="maximusjwl",
    author_email="max.lams99@gmail.com",
    description="Network Iterated Prisoner's Dilemma Framework for Multi-Agent Learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maximusJWL/nipd-framework",
    packages=find_packages(),
    license="CC BY-NC 4.0",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.13",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    include_package_data=True,
    package_data={
        "nipd": ["*.json", "*.yaml", "*.yml"],
    },
    entry_points={
        "console_scripts": [
            "nipd-simulate=nipd.agent_simulator:main",
        ],
    },
    keywords="multi-agent, prisoner-dilemma, reinforcement-learning, game-theory, networks, cooperation, defection, social-dilemmas",
    project_urls={
        "Bug Reports": "https://github.com/maximusJWL/nipd-framework/issues",
        "Source": "https://github.com/maximusJWL/nipd-framework",
        "Documentation": "https://github.com/maximusJWL/nipd-framework#readme",
    },
)

