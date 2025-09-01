from setuptools import setup, find_packages

setup(
    name="sniffcat",
    version="0.1.0",
    description="Python client for Sniffcat API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourusername/sniffcat.py",
    packages=find_packages(),
    install_requires=["requests"],
    license="MIT",
    python_requires=">=3.8",
)