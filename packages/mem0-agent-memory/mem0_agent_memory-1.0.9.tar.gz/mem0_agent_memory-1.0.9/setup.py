from setuptools import setup, find_packages

setup(
    name="mem0-agent-memory",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
)
