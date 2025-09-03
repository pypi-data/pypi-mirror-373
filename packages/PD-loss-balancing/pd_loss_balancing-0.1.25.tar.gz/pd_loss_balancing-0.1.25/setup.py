from setuptools import setup, find_packages

setup(
    name="PD_loss_balancing",
    version="0.1.25",
    author="Addie Foote",
    author_email="addiefoote8@gmail.com",
    description="A package for stabalizing and controllolling loss with feedback control",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/yourusername/my-package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["torch", "numpy", "wandb"],
)
