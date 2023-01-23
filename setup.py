import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "agent-bdi",
    version = "1.1.3",
    author = "Ming Fang Shiu",
    author_email='avatar.xu@gmail.com',
    description='Agent BDI framework',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/mfshiu/abdi.git",
    project_urls = {
        "Bug Tracker": "https://bugtracker.zoho.com/portal/avatardotxugmaildotcom#allprojects/1982079000000043717/",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.9"
)