import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rebrandly_otel",
    version="0.1.2",
    author="Antonio Romano",
    author_email="antobio@rebrandly.com",
    description="Python OTEL wrapper by Rebrandly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rebrandly/rebrandly-otel-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
