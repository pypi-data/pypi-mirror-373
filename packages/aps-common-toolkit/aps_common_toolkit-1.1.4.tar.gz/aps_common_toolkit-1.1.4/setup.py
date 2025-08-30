from setuptools import setup, find_packages

setup(
    name="aps_common_toolkit",
    version="1.1.4",
    author="Abhay Pratap Singh",
    description="Common services and utilities used across projects",
    packages=find_packages(exclude=["*test*", ".venv*"]),
    install_requires=[
        "argon2-cffi==25.1.0",
        "SQLAlchemy==2.0.43",
    ],
    python_requires=">=3.12",
    include_package_data=True,
    package_data={"aps_common_toolkit": ["py.typed"]},
)
