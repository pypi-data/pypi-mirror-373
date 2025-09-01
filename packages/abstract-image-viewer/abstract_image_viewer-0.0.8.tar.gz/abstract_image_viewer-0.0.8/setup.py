from time import time
import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name="abstract-image-viewer",
    version='0.0.1',
    author="putkoff",
    author_email="partners@abstractendeavors.com",
    description="This module, part of the `abstract_essentials` package, provides utility functions for working with images and PDFs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbstractEndeavors/abstract_image_viewer",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],

    install_requires=[
        "pyscreenshot",
        "abstract_utilities",
        "numpy",
        "PyPDF2",
        "pdf2image",
        "abstract_gui",
        "abstract_webtools",
        "pytesseract",
        "Pillow",
        "scipy",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    # Add this line to include wheel format in your distribution
    setup_requires=['wheel'],
)
