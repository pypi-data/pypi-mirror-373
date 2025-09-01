import setuptools


def load_long_description():
    with open("README.md", "r") as f:
        long_description = f.read()
    return long_description


setuptools.setup(
    name="skt",
    version="1.0.8.rc3",
    author="SKT",
    author_email="all@sktai.io",
    description="SKT package",
    long_description=load_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/sktaiflow/skt",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "PyGithub",
        "click",
        "db_dtypes",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "google-cloud-bigquery",
        "google-cloud-bigquery-storage",
        "google-cloud-iam",
        "google-cloud-storage",
        "hmsclient",
        "httplib2",
        "hvac",
        "numpy",
        "packaging",
        "pandas",
        "pandas-gbq",
        "pyarrow",
        "pydata-google-auth",
        "tabulate",
        "tqdm",
        "trino[sqlalchemy]",
        "jupysql",
    ],
    extras_require={
        "dev": ["pytest"],
        "spark": [
            "pyspark[sql]<4.0.0",
        ],
    },
    entry_points={"console_scripts": ["nes = skt.nes:nes_cli"]},
)
