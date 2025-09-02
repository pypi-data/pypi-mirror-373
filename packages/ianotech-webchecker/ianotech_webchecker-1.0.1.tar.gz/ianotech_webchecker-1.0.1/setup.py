from setuptools import setup, find_packages

setup(
    name="ianotech-webchecker",
    version="1.0.1",
    packages=find_packages(),
    install_requires=["Django>=4.0", "requests>=2.25.0"],
    entry_points={"console_scripts": ["website-checker=website_checker.cli:main"]},
    include_package_data=True,
)