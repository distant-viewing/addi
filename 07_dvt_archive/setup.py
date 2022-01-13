from setuptools import setup
from setuptools import find_packages

long_description= """
The Distant Viewing Toolkit is a Python package designed to facilitate the
computational analysis of visual culture. It contains low-level architecture
for applying state-of-the-art computer vision algorithms to still and moving
images. Extracted information can be visualized for search and discovery or
aggregated and analyzed to find patterns across a corpus.

The Distant Viewing Toolkit is supported by the National Endowment for the
Humanities through a Digital Humanities Advancement Grant. It is released under
the open-source GNU General Public License (GPLv2).
"""

required = [
    "numpy",
    "pandas",
    "opencv-python"
]

extras = {
    "tests": [
        "pytest",
        "pytest-pep8",
        "pytest-xdist",
        "pytest-cov",
        "codecov"
    ],
    "keras": ["keras", "tensorflow", "mtcnn"],
    "detectron2": ["detectron2", "torch", "torchvision", "torchaudio"],
}

setup(
    name="dvt",
    version="0.4.0",
    description="Computational Analysis of Visual Culture",
    long_description=long_description,
    author="Taylor Anold, Lauren Tilton",
    author_email="tbarnold@protonmail.ch",
    url="https://github.com/distant-viewing/dvt",
    license="GPL-2",
    install_requires=required,
    extras_require=extras,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3.8",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
)
