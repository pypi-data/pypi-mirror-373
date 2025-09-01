from setuptools import setup, find_packages

setup(
    name="pyhealthify",  # Package name on PyPI
    version="0.1.0",  # Initial release version
    author="Arpit Chhabra",
    author_email="arpitchhabra2704@gmail.com",
    description="A simple health & fitness utility library (BMI, calories, macros, hydration).",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/pyhealthify",  
    packages=find_packages(),  # Automatically find all modules inside pyhealthify/
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.7",
    install_requires=[],  # No external dependencies yet
)
