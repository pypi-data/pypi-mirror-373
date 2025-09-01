import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="blackduck_results_test",
    version="1.0.23",
    metadata_version="2.3",
    author="Fabio Arciniegas",
    author_email="fabio_arciniegas@trendmicro.com",
    description="Recursively traverse subprojects and report libraries with vulnerable components in a format suitable for integration with other tools and human consumption.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://https://adc.trendmicro.com/fabioa/blackduck-results",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts':
        ['bd-results=blackduck_results.cli:cli'],
    },
    test_suite='nose.collector',
    tests_require=['nose'],
    python_requires='>=3.6',
    install_requires=[
        'blackduck',
        'pandas',
    ]
)
