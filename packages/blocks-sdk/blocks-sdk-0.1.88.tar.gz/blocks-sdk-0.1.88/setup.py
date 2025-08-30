from setuptools import setup, find_packages

# get requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="blocks-sdk",  
    version="0.1.88", 
    packages=find_packages(),
    include_package_data=True,  # Include files specified in MANIFEST.in 
    install_requires=requirements,  
    description="Write custom AI-enabled codebase automations in Python. Leverage a full codebase-aware API. Automatically trigger automations from Github, Slack, and other providers.",
    author="BlocksOrg",
    license="AGPL",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author_email="dev@blocksorg.com",
    url="https://github.com/BlocksOrg/sdk",  
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.9',  
)
