from setuptools import setup, find_packages

setup(
    name="Chillax",  # pip install funai
    version="0.0.5",
    description="A python package suitable for vibecoders where every function call is mapped to a Gemini API call.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.5.0",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.8",
)
