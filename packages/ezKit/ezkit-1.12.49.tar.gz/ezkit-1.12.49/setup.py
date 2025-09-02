"""setup"""

from setuptools import find_packages, setup

setup(
    name="ezKit",
    version="1.12.49",
    author="septvean",
    author_email="septvean@gmail.com",
    description="Easy Kit",
    packages=find_packages(exclude=["documents", "tests"]),
    include_package_data=True,
    package_data={"ezKit": ["markdown_to_html.template"]},
    python_requires=">=3.12",
    install_requires=["loguru>=0.7"],
)
