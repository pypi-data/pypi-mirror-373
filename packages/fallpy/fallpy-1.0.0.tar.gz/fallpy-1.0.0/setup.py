from setuptools import setup, find_packages

setup(
    name="fallpy", 
    version="1.0.0", 
    description="fallpy is a python fallacy detector, it matches the entered statement with a fallacy in the list using openai and google search api",
    packages=find_packages(where="pyfallacy"),
    author="jamcha123", 
    author_email="jameschambers732@gmail.com"
)