from setuptools import setup, find_packages

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
