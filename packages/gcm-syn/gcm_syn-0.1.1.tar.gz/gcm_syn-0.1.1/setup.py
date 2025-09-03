from setuptools import setup, find_packages

setup(
    name="gcm-syn",
    version="0.1.0",
    description="A package for generating synthetic data with preserved correlation structures.",
    author="Jens E. d'Hondt",
    author_email="jensdhondt7@gmail.com",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
    ],
)
