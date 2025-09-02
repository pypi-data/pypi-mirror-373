from setuptools import setup, find_packages

setup(
    name="mm-factory",
    version="0.1.1",
    description="Modular library to combine pretrained LLMs and vision encoders with adapters.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "datasets",
        "Pillow",
        "timm"
    ],
    python_requires=">=3.10",
)
