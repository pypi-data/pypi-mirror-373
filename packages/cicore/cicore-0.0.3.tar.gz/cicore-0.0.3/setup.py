from setuptools import setup, find_packages

long_description = "The core of a CA Library IDE project."

setup(
    name="cicore",
    version="0.0.3",
    author="地灯dideng",
    author_email="3483434955@qq.com",
    description="A core utility library for daily Python tasks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    url="https://github.com/bilibili-dideng/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
    ],
    install_requires=[
        "wtfami>=0.1.0",
        "PyQt5",
        "jsonschema"
    ],
)