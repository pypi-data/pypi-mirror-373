from setuptools import setup, find_packages

setup(
    name="pasgen",
    version="0.5",
    author="ahmetyavuzkanat@outlook.com",
    description="Password Generator For Python",
    long_description=open("README.md",encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yavuzkanat/PasGen",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
    
)