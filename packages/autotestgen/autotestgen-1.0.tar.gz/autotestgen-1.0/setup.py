from setuptools import setup, find_packages

setup(
    name="autotestgen",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "autotestgen=autotestgen.cli:main"
        ]
    },
)
