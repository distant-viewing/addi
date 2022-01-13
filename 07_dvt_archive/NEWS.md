## DVT 0.4.0

This version of the toolkit introduces a major change to the API. It
significantly simplifies the operation of the toolkit, particularly when
working with still images. The previous underlying algorithms are unchanged,
but user-facing functions have been entire re-organized. Some of the major
changes include:

- Making it possible to install without Keras and TensorFlow.
- Adding Detectron2 models, which are also given in a way that avoids needing
to install these.
- Annotators are now given in two different forms: batch annotators (these run
over a batch of images) and image annotators (these run on a single image). The
latter makes the toolkit easier to use for still image collections.
- Cycling over batches or over a corpus is now the responsibility of the user.
This simplifies a lot of the internal logic.
- The visualization engine is now in a seperate repository (dvtviz).

The best place to see the new API is in the Colab notebooks, which show working
versions of all the main algorithms.
