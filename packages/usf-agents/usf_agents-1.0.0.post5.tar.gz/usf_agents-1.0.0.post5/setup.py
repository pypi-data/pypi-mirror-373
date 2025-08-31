from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="usf-agents",
    version="1.0.0.post4",
    description="A lightweight multi-agent orchestration framework with better control, easy to use for complex to simple use cases. Developer friendly with more visibility and supports all models with OpenAI compatible API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="UltraSafe AI Team",
    license="USF Agents SDK License",
    homepage="https://us.inc",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "aiohttp>=3.8.0",
    ],
    keywords=[
        "multi-agent",
        "orchestration", 
        "framework",
        "lightweight",
        "agent",
        "developer-friendly",
        "visibility",
        "control",
        "complex-usecase",
        "simple-usecase",
        "all-models",
        "openai-compatible",
        "llm",
        "ai-agent",
        "tool-calling",
        "streaming",
        "usf",
        "planning",
        "UltraSafe",
        "UltraSafe AI",
        "usf-agents"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
