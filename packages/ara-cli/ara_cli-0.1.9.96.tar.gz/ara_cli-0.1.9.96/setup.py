from setuptools import setup, find_packages

# Import version number
version = {}
with open("./ara_cli/version.py") as fp:
    exec(fp.read(), version)

with open("./docker/base/requirements.txt", "r", encoding="utf-8") as pip_reqs_file:
    reqs = [line.strip() for line in pip_reqs_file.readlines()]

setup(
    name="ara_cli",
    version=version['__version__'],
    packages=find_packages(),
    include_package_data=True,
    description='Powerful, open source command-line tool for managing, structuring and automating software development artifacts in line with Business-Driven Development (BDD) and AI-assisted processes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    entry_points={
        "console_scripts": [
            "ara = ara_cli.__main__:cli",
        ],
    },
    install_requires=reqs,
)
