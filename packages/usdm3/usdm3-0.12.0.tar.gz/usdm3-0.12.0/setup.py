import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

package_info = {}
with open("src/usdm3/__info__.py") as fp:
    exec(fp.read(), package_info)

setuptools.setup(
    name="usdm3",
    version=package_info["__package_version__"],
    author="D Iberson-Hurst",
    author_email="",
    description="A python package for using the CDISC TransCelerate USDM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "pydantic==2.7.3",
        "beautifulsoup4==4.12.3",
        "pyyaml==6.0.1",
        "simple_error_log>=0.5.0",
        "jsonschema==4.23.0",
        "python-dotenv==1.0.1",
        "requests==2.32.3",
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "usdm3": [
            "ct/cdisc/library_cache/library_cache_all.yaml",
            "ct/cdisc/library_cache/library_cache_usdm.yaml",
            "ct/cdisc/config/ct_config.yaml",
            "ct/cdisc/missing/missing_ct.yaml",
            "rules/library/schema/usdm_v3.json",
            "bc/cdisc/library_cache/library_cache.yaml",
        ]
    },
    tests_require=["pytest", "pytest-cov", "pytest-mock", "python-dotenv", "ruff"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
)
