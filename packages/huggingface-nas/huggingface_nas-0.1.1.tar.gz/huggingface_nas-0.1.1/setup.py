import shutil
from pathlib import Path

from setuptools import find_packages, setup


install_requires = [
    "tqdm>=4.27",
    "datasets>=3.1.0",
    "requests",
    "synology-api>=0.7.3",
]

setup(
    name="huggingface_nas",
    version="0.1.1",  # expected format is one of x.y.z.dev0, or x.y.z.rc1 or x.y.z (no to dashes, yes to dots)
    author="tony9402",
    author_email="tony9402@naver.com",
    description="Using NAS such as huggingface hub",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="huggingface nas synology",
    license="Apache 2.0 License",
    url="https://github.com/tony9402/huggingface-NAS",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    package_data={"": []},
    zip_safe=False,
    entry_points={},
    python_requires=">=3.8.0",
    install_requires=list(install_requires),
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
