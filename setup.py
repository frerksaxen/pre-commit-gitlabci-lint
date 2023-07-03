from setuptools import setup


setup(
    name="pre-commit-gitlabci-lint",
    version="0.0.0",
    packages=["gitlabci_lint"],
    entry_points={"console_scripts": ["gitlabci-lint = gitlabci_lint:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
