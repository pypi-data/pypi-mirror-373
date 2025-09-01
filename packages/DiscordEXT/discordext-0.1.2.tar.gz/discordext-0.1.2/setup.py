from setuptools import setup, find_packages

setup(
    name="DiscordEXT",
    version="0.1.2",
    packages=find_packages(),
    install_requires=["requests"],
    description="Discord-themed Python installer module",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ned.Dev382",
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)