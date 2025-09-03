from setuptools import setup, find_packages

setup(
    name="modu-muse",
    version="0.1.5",
    packages=find_packages(),
    install_requires=[
        "transformers",
        "torch",
        "Pillow"
    ],
    author="Wissem Elkarous",
    author_email="karouswissem@gmail.com",
    description="Modular multimodal pipeline for vision-to-LLM integration",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ELkarousWissem/ModuMuse",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
