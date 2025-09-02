from setuptools import setup, find_packages

setup(
    name="phiphadl",
    version="0.1.1",
    description="Deep learning training and testing pipelines",
    packages=find_packages(),  # automatically finds PhiPhaDL/
    install_requires=["torch", "numpy", "matplotlib", "seaborn", "scikit-learn"],
)
