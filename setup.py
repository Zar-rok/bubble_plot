import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="bubble_plot-Zar",
    version="0.0.1",
    author="Zar",
    author_email="zar_rok@live.com",
    description="Generate the Latex source files for bubble plots.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/Zar-rok/bubble_plot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    test_suite='test_bubble_plot.py'
)
