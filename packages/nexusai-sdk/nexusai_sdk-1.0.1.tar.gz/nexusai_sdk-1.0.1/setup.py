"""
NexusAI Python SDK
AI Agent Platform for Businesses
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nexusai-sdk",
    version="1.0.1",
    author="NexusAI",
    author_email="support@nexusai.com",
    description="Python SDK for NexusAI - AI Agent Platform for Businesses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cruso003/Nexux-Docs",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    keywords="ai, agents, nlp, voice, vision, multimodal, business, africa",
    project_urls={
        "Bug Reports": "https://github.com/cruso003/Nexux-Docs/issues",
        "Source": "https://github.com/cruso003/Nexux-Docs",
        "Documentation": "https://nexus-docs.bits-innovate.com",
    },
)
