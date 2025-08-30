from setuptools import setup, find_packages

package_name = "square_logger"

setup(
    name=package_name,
    version="2.0.1",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.5.3",
    ],
    extras_require={
        "test": [
            "pytest>=8.0.0",
        ],
    },
    author="Parth Mukesh Mangtani, Amish Palkar",
    author_email="thepmsquare@gmail.com, amishpalkar302001@gmail.com",
    description="python logger for my personal use.",
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
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
