from setuptools import setup, find_packages
import os

# Handle README.md safely
long_description = "Professional Cisco Network Analysis & Simulation Toolkit by Karpagam"
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    pass  # Use default description if README.md not found

setup(
    name="cisco-network-simulation-by-karpagam",
    version="1.0.6",
    author="Karpagam",
    author_email="karpagam@college.edu",
    description="🌐 Professional Cisco Network Analysis & Simulation Toolkit by Karpagam",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Networking",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
                "Programming Language :: Python :: 3.12",

        "Programming Language :: Python :: 3.13",

        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "matplotlib>=3.5.0",
        "networkx>=2.8.0",
        "simpy>=4.0.0", 
        "pandas>=1.4.0",
        "numpy>=1.21.0",
    ],
    entry_points={
        "console_scripts": [
            "cisco-sim-karpagam=cisco_netsim_by_KARPAGAM.main:main",
        ],
    },
    include_package_data=True,
    keywords=["cisco", "network", "simulation", "analysis", "karpagam"],
)
