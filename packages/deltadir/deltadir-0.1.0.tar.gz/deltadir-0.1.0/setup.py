from setuptools import setup, find_packages

# Читаем версию напрямую из __version__.py
def read_version():
    ns = {}
    with open("deltadir/__version__.py") as f:
        exec(f.read(), ns)
    return ns["__version__"]

setup(
    name="deltadir",
    version=read_version(),
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": ["deltadir = deltadir.cli:main"],
    },
    description="Compare directories. Source (src) never modified, dst can be updated with -s/--sync",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    license="MIT",
    install_requires=[],
)
