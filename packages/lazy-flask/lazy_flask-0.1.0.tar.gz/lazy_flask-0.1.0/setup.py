import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    'flask>=1.0.0'
]

setuptools.setup(
    name="lazy_flask",
    version="0.1.0",
    author="wrl96",
    author_email="ruilin.wang96@gmail.com",
    description="A simple function framework on flask for lazy developers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wrl96/lazy_flask",
    packages=setuptools.find_packages(),
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
