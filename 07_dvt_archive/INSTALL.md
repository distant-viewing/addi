## Overview

The Distant Viewing Toolkit is a Python package released under an open-source
license. It is free to download and install, either from source through this
GitHub repository or as pre-built binaries through PyPI. We test and build the
toolkit using Python 3.8 on macOS and a Ubuntu linux distribution. It is likely
that the core functions will also work on any Python with version greater than
3.6.

Note that this software is intended to be run in a terminal and requires
some knowledge of how to run and structure code. If these are new to you, we
suggest first checking out a resource such as those provided by the
[Software Carpentry](https://software-carpentry.org/lessons/) project.
Alternatively, you may also use the pre-built Colab notebooks linked to from
the main README.md file. We are in the process of building a pre-built GUI to
allow for a greater range of users. Please be in touch if you are interested
in learning more about this proecss.

## Distant Viewing Toolkit

To install the toolkit, we recommend creating a virtual environment, activating
it, and the installing from PyPI:

```
python3 -m venv env
source env/bin/activate
python3 -m pip install dvt
```

This process will install all of the required dependencies. However, in order
to run deep learning algorithms included in the toolkit, you will need to
install Keras+TensorFlow and/or Detectron2+PyTorch. For this, see the following
sections.

## Keras and TensorFlow

Keras, TensorFlow, and mtcnn are needed to run the image embedding, face
detection, and face recognition algorithms in the toolkit. Usually, this can
be done with the following command:

```
python3 -m pip install tensorflow keras mtcnn
```

On macOS and Linux, we have found a majority of problems arise because of
different version mismatches. Using a fresh virtural environment usually
solves these issues. The process is known to be a bit more difficult on
Windows. For full instructions, see the
[TensorFlow](https://www.tensorflow.org/install/) documentation.

While we have generally found it possible to install these on UNIX-based
systems for running on a CPU, getting them setup for a GPU can be a
significantly more involved process. We suggest using sites such as
StackOverflow or contact your local support if you need to run code on a
GPU.

## Detectron2 and PyTorch

Detectron2 has been, in our experience, more difficult to install than Keras
and TensorFlow. However, it has fantastic models available for semantic
segementation that at the moment seems superior to anything else that is
available and well-documented. A good first place to start is looking at the
[Detectron2 Documentation](
  https://github.com/facebookresearch/detectron2/blob/master/INSTALL.md
). The Google Colab notebook linked on the main page shows the installation
code to getting Detectron2 running on the Colab servers.

On macOS, we were recently able to install Detectron2 for Python3.8 on a fresh
virtual environment using the following:

```
python -m pip install wheel
python -m pip install torch torchvision torchaudio

python -m pip install -U 'git+https://github.com/facebookresearch/fvcore'
CC=clang CXX=clang++ ARCHFLAGS="-arch x86_64" python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
python -m pip install --upgrade --force-reinstall numpy
```

The last line gives an error about incompatibility with TensorFlow
(numpy=1.20.2), but it still seems to run fine.

Please feel free to open an issue if you have trouble with the installation,
but it is likely we will not be able to offer significant assistance as this
is known to be difficult software to install.
