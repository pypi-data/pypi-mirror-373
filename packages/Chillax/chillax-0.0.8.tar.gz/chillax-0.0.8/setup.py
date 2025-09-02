from setuptools import setup, find_packages

setup(
    name="Chillax",  # pip install Chillax
    version="0.0.8",
    description="A Python package for vibecoders.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Gowtham Jegathesan S",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.5.0",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.8",
)
