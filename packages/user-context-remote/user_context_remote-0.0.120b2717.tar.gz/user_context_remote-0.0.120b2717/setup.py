import setuptools  # type: ignore

PACKAGE_NAME = "user-context-remote"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.120b2717',  # https://pypi.org/project/user-context-remote/
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles User Context Local/Remote Python",
    long_description="This is a package for sharing common user-context-remote functions used in different repositories",
    long_description_content_type="text/markdown",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'language-remote>=0.0.15',
        'url-remote>=0.0.124',
        'requests>=2.31.0',
        'python-sdk-remote>=0.0.44',
    ],
)
