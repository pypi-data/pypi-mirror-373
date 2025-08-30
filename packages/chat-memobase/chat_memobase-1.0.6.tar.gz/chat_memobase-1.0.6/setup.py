import setuptools
from setuptools import find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()


deps = []
with open("memobase/requirements.txt") as f:
    for line in f.readlines():
        if not line.strip():
            continue
        deps.append(line.strip())


setuptools.setup(
    name="chat_memobase",
    version='1.0.6',
    author='Allison',
    license='Apache license 2.0',
    description="Client library of memory based on Memobase: manage user memory for my LLM applications",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    package_dir={"": "memobase/src/client"},
    packages=find_packages(where="memobase/src/client", exclude=["tests"]),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
