from setuptools import setup, find_packages

setup(
    name="num2bangla",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    author="Md.Amanullah Al Mamun",
    author_email="pygemsbd@gmail.com",
    description="A package to convert numbers to Bengali/Bangla text and numerals with currency formatting support",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mamuntheprogrammer/num2bangla",
    keywords="bangla,bengali,numbers,num2words,currency,text,numerals",
    license="MIT",
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
    include_package_data=True,
    project_urls={
        "Source": "https://github.com/Mamuntheprogrammer/num2bangla",
        "Bug Tracker": "https://github.com/Mamuntheprogrammer/num2bangla/issues",
    },
)
