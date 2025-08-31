from setuptools import setup, find_packages

setup(
    name="lisq",
    version="2025.9.1",
    description="A single file note-taking app that work with .txt files",
    author="funnut",
    author_email="essdoem@yahoo.com",
    project_urls={
        "Bug Tracker": "https://github.com/funnut/Lisq/issues",
        "Source Code": "https://github.com/funnut/Lisq",
    },
    url="https://github.com/funnut/Lisq",
    license="Non-Commercial",
    license_files=["LICENSE"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "lisq = src.lisq:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "cryptography==45.0.6",
    ]
)
