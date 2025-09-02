from setuptools import setup, find_packages

setup(
    name="esek",
    use_scm_version=True,
    setup_requires=["setuptools-scm"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
