from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hyperllm",
    version="1.0.0",
    author="Swe",
    author_email="swe@hyperswe.com",
    description="A unified interface for multiple LLM providers with caching and interactive development mode to get massive cost savings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hyper-swe/hyperllm",
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.20.0"],
        "clipboard": ["pyperclip>=1.8.0"],
        "all": ["openai>=1.0.0", "anthropic>=0.20.0", "pyperclip>=1.8.0"],
    },
    keywords="llm, llmproxy, ai, openai, anthropic, claude, ollama, cost-saving, caching, interactive-mode, genai",
    project_urls={
        "Bug Reports": "https://github.com/hyper-swe/hyperllm/issues",
        "Source": "https://github.com/hyper-swe/hyperllm",
        "Documentation": "https://github.com/hyper-swe/hyperllm#readme",
    },
)