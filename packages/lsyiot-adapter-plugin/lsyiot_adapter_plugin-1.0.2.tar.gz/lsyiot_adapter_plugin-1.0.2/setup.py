from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lsyiot_adapter_plugin",
    version="1.0.2",
    author="fhp",
    author_email="chinafengheping@outlook.com",
    description="为lsyiot_adapter_hub提供适配器插件",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/9kl/lsyiot_adapter_plugin",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["pyyaml"],
)
