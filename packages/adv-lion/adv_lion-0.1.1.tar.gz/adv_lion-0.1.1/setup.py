from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="adv_lion",
    version="0.1.1",
    author="Koratahiu",
    author_email="hiuhonor@gmail.com",
    license='Apache 2.0',
    description="Pytorch Lion optimizer with updated and advanced features.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Koratahiu/Adv_Lion",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: Apache Software License',
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "torch>=2.0",
    ],
    python_requires=">=3.8",
    keywords=[
        "llm",
        "fine-tuning",
        "pytorch",
        "optimizer",
        "lion",
    ],
)
