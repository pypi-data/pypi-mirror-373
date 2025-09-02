from setuptools import setup, find_packages

# Read the contents of requirements.txt with explicit encoding
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name='multimodal_sdk',
    version='0.0.6.67.10',
    packages=find_packages(),
    install_requires=requirements,
)
