from setuptools import setup, find_packages

setup(
    name="mwutsdz",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "scikit-learn",
        "pandas",
        "matplotlib"
    ],
    author="Ton Nom",
    author_email="ton.email@example.com",
    description="MWUT-SDZ: Détection automatique de knee point dans les données de cycle de batteries",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/toncompte/mwutsdz",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

