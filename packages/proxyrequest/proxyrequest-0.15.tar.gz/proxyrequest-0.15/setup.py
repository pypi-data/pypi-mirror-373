from setuptools import setup, find_packages

setup(
    name="proxyrequest",  # Name of your package
    version="0.15",  # Initial version
    install_requires=[
        "requests==2.31.0",
        # "UnicodeDammit",  # Remove if it's incorrectly added
    ],
    author="Ramesh Chandra",
    author_email="rameshsofter@gmail.com",
    description="A Python package for making HTTP requests with proxy support and fetching HTML content using requests or Selenium.",
    long_description=open('README.md').read(),  # Optional: include a README
    long_description_content_type="text/markdown",
    packages=find_packages(),  # This will find all the packages in your project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
