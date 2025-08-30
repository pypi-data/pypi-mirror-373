from setuptools import setup, find_packages

setup(
    name="vlm-memory",
    version="0.2.1",
    description="Video-Language Memory library with Qdrant and flexible chunking, supports any Hugging Face VLM",
    author="Wissem Karous",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "qdrant-client",
        "decord",
        "numpy",
        "Pillow"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "vlm-memory=vlm_memory.cli:main",
        ],
    },
)
