import shutil
from setuptools import (
    find_packages,
    setup,
)


shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("pgcopylib.egg-info", ignore_errors=True)

with open(file="README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pgcopylib",
    version="0.1.3",
    packages=find_packages(),
    author="0xMihalich",
    author_email="bayanmobile87@gmail.com",
    description="PGCopy bynary dump parser.",
    url="https://github.com/0xMihalich/pgcopylib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    zip_safe=False,
)
