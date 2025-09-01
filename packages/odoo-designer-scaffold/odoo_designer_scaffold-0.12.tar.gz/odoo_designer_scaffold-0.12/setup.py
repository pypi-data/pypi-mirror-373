from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()
setup(
    name="odoo_designer_scaffold",
    version="0.12",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "create-scaffold = odoo_designer_scaffold: create_scaffold",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)
