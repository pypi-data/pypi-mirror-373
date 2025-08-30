from setuptools import find_packages, setup

package_name = "square_file_store"

setup(
    name=package_name,
    version="2.3.3",
    packages=find_packages(),
    package_data={
        package_name: ["data/*"],
    },
    install_requires=[
        "uvicorn>=0.24.0.post1",
        "fastapi>=0.104.1",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.3",
        "pytest>=8.0.0",
        "square_logger>=2.0.0",
        "square_database_helper>=2.3.0",
        "square_commons>=2.1.0",
        "square_database_structure>=2.5.1",
        "httpx>=0.27.2",
    ],
    author="Parth Mukesh Mangtani",
    author_email="thepmsquare@gmail.com",
    description="file storage layer for my personal server.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url=f"https://github.com/thepmsquare/{package_name}",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Framework :: FastAPI",
    ],
)
