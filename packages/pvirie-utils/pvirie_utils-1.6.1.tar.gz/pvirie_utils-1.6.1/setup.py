try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

import os
import shutil
# copy js/src directory into package js directory

# if os.path.exists("build/lib/vulcan_annotation/js"):
#     shutil.rmtree("build/lib/vulcan_annotation/js")
# shutil.copytree("js/src", "build/lib/vulcan_annotation/js")

setup(
    name="pvirie-utils",
    version="1.6.1",
    author="Chatavut Viriyasuthee",
    author_email="p.virie@gmail.com",
    description="PVirie's python utility functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PVirie/python-utils",
    packages=["pvirie_gcp"],
    package_data={
        # "": ["js/*"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        "google-api-python-client",
        "google-cloud-storage",
        "google-cloud-secret-manager",
        "pydantic"
    ]
)
