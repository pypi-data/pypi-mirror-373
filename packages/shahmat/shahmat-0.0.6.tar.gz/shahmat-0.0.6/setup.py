from pathlib import Path
from setuptools import setup, find_packages

ROOT = Path(__file__).parent
README = (ROOT / "README.md").read_text(encoding="utf-8")

setup(
    name="shahmat",
    version="0.0.6",
    description="Analyze your Chess.com games: fetch, stats (hour, Elo diff), and clean visualizations.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Anthony Gocmen",
    author_email="anthony.gocmen@gmail.com",
    url="https://ag-algolab.github.io/",
    project_urls={
        "Source": "https://github.com/ag-algolab/ShahMat",
    },
    license="MIT",
    license_files=("LICENSE",),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.3",
        "numpy>=1.21",
        "matplotlib>=3.5",
        "tqdm>=4.64",
        "requests>=2.28",
    ],
    keywords=[
        "chess", "chess.com", "analytics", "elo", "visualization", "data-science"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
)
