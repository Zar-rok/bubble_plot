import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="bubble_plot-Zar",
    version="0.0.1",
    author="Zar",
    author_email="zar_rok@live.fr",
    description=(
        "Automate the generation of the CSV file and the preparation"
        "of the Latex source file used to generate a bubble plot"
        "using [PGF/TikZ]"
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/Zar-rok/bubble_plot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    test_suite="test_bubble_plot.py",
    extras_require={"example": ["pybtex", "seaborn"]},
)
