from setuptools import find_packages, setup

package_name = "square_common_bl"

setup(
    name=package_name,
    version="5.0.1",
    packages=find_packages(),
    package_data={
        package_name: ["data/*"],
    },
    install_requires=[
        "uvicorn>=0.24.0.post1",
        "fastapi>=0.104.1",
        "pydantic>=2.5.3",
        "requests>=2.32.3",
        "pytest>=8.0.0",
        "httpx>=0.27.2",
        "square_commons>=2.1.0",
        "square_logger>=2.0.0",
        "square_database_helper>=2.0.0",
        "square_database_structure>=1.0.0",
        "square_authentication_helper>=2.5.2",
        "square_file_store_helper>=3.0.0",
        "python-multipart>=0.0.16",
    ],
    extras_require={},
    author="Parth Mukesh Mangtani",
    author_email="thepmsquare@gmail.com",
    description="common business layer for my personal server.",
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
