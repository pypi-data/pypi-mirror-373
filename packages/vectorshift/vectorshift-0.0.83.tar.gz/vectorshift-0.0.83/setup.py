from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="vectorshift",
    version="0.0.83",
    packages=find_packages(),
    author="Alex Leonardi, Pratham Goyal, Eric Shen",
    author_email="support@vectorshift.ai",
    description="VectorShift Python SDK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
