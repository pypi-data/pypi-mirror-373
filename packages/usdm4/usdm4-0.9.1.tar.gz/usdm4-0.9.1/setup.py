import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

package_info = {}
with open("src/usdm4/__info__.py") as fp:
    exec(fp.read(), package_info)

setuptools.setup(
    name="usdm4",
    version=package_info["__package_version__"],
    author="D Iberson-Hurst",
    author_email="",
    description="A python package for using the CDISC TransCelerate USDM, version 4",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "usdm3==0.12.1",
        "simple_error_log>=0.6.0",
        "python-dateutil==2.9.0.post0",
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "usdm4": [
            "ct/cdisc/library_cache/library_cache_all.yaml",
            "ct/cdisc/library_cache/library_cache_usdm.yaml",
            "ct/cdisc/config/ct_config.yaml",
            "ct/cdisc/missing/missing_ct.yaml",
            "ct/iso/iso3166/iso3166.json",
            "bc/cdisc/library_cache/library_cache.yaml",
            "rules/library/schema/usdm_v4-0-0.json",
        ]
    },
    tests_require=["pytest", "pytest-cov", "pytest-mock", "python-dotenv"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
)
