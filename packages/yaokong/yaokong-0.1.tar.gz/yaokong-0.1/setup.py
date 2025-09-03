from setuptools import setup, find_packages

# Read the requirements from requirements.txt
with open("requirements.txt", "r") as f:
    install_requires = f.read().splitlines()

setup(
    name="yaokong",  # Name of your package
    version="0.1",   # Version number
    description="A Python package for yaokong functionality",  # Short description
    author="Kim Jarvis",  # Your name
    author_email="kim.jarvis@tpfsystems.com",  # Your email
    packages=find_packages(),  # Automatically find all packages in the directory
    install_requires=install_requires,  # Load dependencies from requirements.txt
    python_requires=">=3.6",  # Specify the minimum Python version required
)
