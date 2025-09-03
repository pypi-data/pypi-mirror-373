from setuptools import setup, find_packages

setup(
    name="yaokong",  # Name of your package
    version="0.2",   # Version number
    description="A Python package for yaokong functionality",  # Short description
    author="Kim Jarvis",  # Your name
    author_email="kim.jarvis@tpfsystems.com",  # Your email
    url="https://github.com/kimjarvis/yaokong",  # URL to the source code repository
    license="MIT",  # License type
    packages=find_packages(),  # Automatically find all packages in the directory
    install_requires=[
        "cryptography",
        "bcrypt",
        "asyncssh",
    ],  # List of dependencies with proper commas
    python_requires=">=3.6",  # Specify the minimum Python version required
)