from setuptools import setup, find_packages

VERSION = '2025.09.02'
DESCRIPTION = 'Multi-Agent System for Python (MASPY) with Machine Learning proprieties'
LONG_DESCRIPTION = 'A library for the devolopment of multi-agent systems with components of machine learning https://github.com/laca-is/MASPY'

# Setting up
setup(
    name="maspy-ml",
    version=VERSION,
    author="Alexandre Mellado",
    author_email="<melladoallm@gamil.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    include_package_data=True,
    package_data={"maspy": ["py.typed","*.pyi","logger_config.json"]},
    install_requires=['numpy','pandas','openpyxl','keyboard'],
    keywords=['python', 'autonomous agents', 'multi-agent system', 'machine learning'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
    ]
)