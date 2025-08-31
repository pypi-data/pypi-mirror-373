from setuptools import setup, find_packages

setup(
    name="num2bangla",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Your Name",
    author_email="your.email@example.com",
    description="A package to convert numbers to Bengali/Bangla text and numerals with currency formatting support",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mamuntheprogrammer/num2bangla",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'num2bangla=num2bangla.cli:main',
        ],
    },
)
