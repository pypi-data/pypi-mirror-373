from setuptools import setup, find_packages

setup(
    name="ianotech-webchecker",
    version="1.0.3", 
    description="A Django app to check website status with screenshots",
    author="IanoTech",
    packages=find_packages(),
    install_requires=["Django>=4.0", "requests>=2.25.0"],
    entry_points={"console_scripts": ["website-checker=website_checker.cli:main"]},
    include_package_data=True,
    package_data={
        'website_checker': ['checker/templates/checker/*.html'],
    },
)