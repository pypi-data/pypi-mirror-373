from setuptools import setup, find_packages
import os
from pathlib import Path

def prepare_init_files():
    # Determine source and destination paths
    init_path = Path(__file__).parent / "package" / "uurest" / "init" 
    init_files_path = init_path / "init_files"
    init_files_script_path = init_path / "init_files.py"
    # list files in source directory
    source_files = os.listdir(init_files_path)
    result = {}
    # create dictionary of file names and their content
    for file in source_files:
        source_file = init_files_path / file
        pure_file_name = os.path.basename(file)
        if source_file.is_file():
            with open(source_file, "rb") as fsrc:
                result[pure_file_name] = fsrc.read().decode('utf-8')
    # write the dictionary to init_files.py
    with open(init_files_script_path, "w", encoding="utf-8") as fdst:
        fdst.write(f'init_files = {result}\n')

prepare_init_files() 

with open(f'./package/readme.md', f'r') as f:
    long_description = f.read()
long_description = f'\n' + long_description.replace('\r', '')

# increment version
with open("./version.txt", "r") as file:
    version = file.read()

version = int(version) + 1

with open("./version.txt", "w") as file:
    file.write(str(version))

setup(
    name='uurest',
    version=f'1.0.{version}',
    package_dir={"": "package"},
    long_description=long_description,
    long_description_content_type="text/markdown",
    description='uuRest library and its two main functions "call" and "fetch" are designed '
                'to allow users to rapidly scrape/automate web applications designed and developed by Unicorn Systems (Unicorn.com).',
    author='Jaromir Sivic',
    author_email='unknown@unknown.com',
    license="MIT",
    packages=find_packages(where="package"),
    keywords=['python', 'uuRest', 'Unicorn Systems', 'UAF', 'Unicorn Application Framework'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'requests'
    ],
    extras_require={
        "dev": ["twine>=4.0.2"]
    },
    python_requires=">=3.8"
)
