# -*- coding: utf-8 -*-
"""Annotators that require installing keras and tensorflow.
"""

from importlib import import_module

import ssl
from cv2 import resize, cvtColor, COLOR_BGR2RGB
from numpy import float32, expand_dims, uint8
from pandas import DataFrame

from .abstract import ImageAnnotator


class FaceAnnotator(ImageAnnotator):
    """Annotator for detecting faces and embedding them as a face vector."""

    def __init__(self, detector, embedding=None):
        self.detector = detector
        self.embedding = embedding

    def annotate_image(self, img):
        """Annotate the batch of frames with the face annotator."""

        img_rgb = cvtColor(img, COLOR_BGR2RGB)
        f_faces = self.detector.detect(img_rgb)

        if self.embedding is not None and f_faces is not None:
            n_face = len(f_faces["top"])
            f_faces["embed"] = []
            for i in range(n_face):
                embed = self.embedding.embed(
                    img_rgb,
                    top=f_faces["top"][i],
                    right=f_faces["right"][i],
                    bottom=f_faces["bottom"][i],
                    left=f_faces["left"][i],
                )
                f_faces["embed"] += [embed]

        if not f_faces:
            f_faces = DataFrame(
                columns = ["top", "right", "bottom", "left", "confidence"]
            )

        return {"face": f_faces}


class FaceDetectMtcnn:
    """Detect faces using the Multi-task Cascaded CNN model.

    Attributes:
        cutoff (float): A cutoff value for which faces to include in the final
            output. Set to zero (default) to include all faces.
    """

    def __init__(self, cutoff=0):
        self.mtcnn = import_module("mtcnn.mtcnn")
        self.cutoff = cutoff
        self._mt = self.mtcnn.MTCNN(min_face_size=20)

    def detect(self, img):
        """Detect faces in an image.

        Args:
            img (numpy array): A single image stored as a three-dimensional
                numpy array.

        Returns:
            A list of dictionaries where each dictionary represents a detected
            face. Keys include the bounding box (top, left, bottom, right) as
            well as a confidence score.
        """
        dets = self._mt.detect_faces(img)

        if not dets:
            return

        faces = {
            "top": [],
            "right": [],
            "bottom": [],
            "left": [],
            "confidence": [],
        }
        for det in dets:
            if det["confidence"] >= self.cutoff:
                bbox = _trim_bbox(
                    (
                        det["box"][1],
                        det["box"][0] + det["box"][2],
                        det["box"][1] + det["box"][3],
                        det["box"][0],
                    ),
                    img.shape,
                )
                faces["top"] += [bbox[0]]
                faces["right"] += [bbox[1]]
                faces["bottom"] += [bbox[2]]
                faces["left"] += [bbox[3]]
                faces["confidence"] += [det["confidence"]]

        return faces


class FaceEmbedVgg2:
    """Embed faces using the VGGFace2 model.

    A face embedding with state-of-the-art results, particularly suitable when
    there are small or non-forward-facing examples in the dataset.
    """

    def __init__(self):
        from tensorflow.keras.models import load_model
        from tensorflow.keras.utils import get_file
        from tensorflow.keras import backend as K

        ssl._create_default_https_context = ssl._create_unverified_context
        mloc = get_file(
            "vggface2-resnet50.h5",
            origin="https://github.com/distant-viewing/dvt/"
            "releases/download/0.0.1/"
            "vggface2-resnet50.h5",
        )
        self._model = load_model(mloc)
        self._iformat = K.image_data_format()

    def embed(self, img, top, right, bottom, left):
        """Embed detected faces in an image."""

        iscale = self._proc_image(
            _sub_image(
                img=img,
                top=top,
                right=right,
                bottom=bottom,
                left=left,
                fct=1.3,
                output_shape=(224, 224),
            )
        )

        return self._model.predict(iscale)[0, 0, 0, :]

    def _proc_image(self, iscale):
        iscale = float32(iscale)
        iscale = expand_dims(iscale, axis=0)

        if self._iformat == "channels_first":  # pragma: no cover
            iscale = iscale[:, ::-1, ...]
            iscale[:, 0, :, :] -= 91.4953
            iscale[:, 1, :, :] -= 103.8827
            iscale[:, 2, :, :] -= 131.0912
        else:
            iscale = iscale[..., ::-1]
            iscale[..., 0] -= 91.4953
            iscale[..., 1] -= 103.8827
            iscale[..., 2] -= 131.0912

        return iscale


class EmbedAnnotator(ImageAnnotator):
    """Annotator for embedding frames into an ambient space."""

    def __init__(self, embedding):
        self.embedding = embedding

    def annotate_image(self, img):
        """Annotate the images."""

        obj = self.embedding.embed(img)

        return {"embed": obj}


class EmbedImageKeras:
    """A generic class for applying an embedding to frames.

    Applies a keras model to a batch of frames. The input of the model is
    assumed to be an image with three channels. The class automatically
    handles resizing the images to the required input shape.

    Attributes:
        model: A keras model to apply to the frames.
        preprocess_input: An optional function to preprocess the images. Set to
            None (the default) to not apply any preprocessing.
        outlayer: Name of the output layer. Set to None (the default) to use
            the final layer predictions as the embedding.
    """

    def __init__(self, model, preprocess_input=None, outlayer=None):
        from keras.models import Model

        if outlayer is not None:
            model = Model(
                inputs=model.input, outputs=model.get_layer(outlayer).output
            )

        self.input_shape = (model.input_shape[1], model.input_shape[2])
        self.model = model
        self.preprocess_input = preprocess_input
        super().__init__()

    def embed(self, img):
        """Embed a batch of images.

        Args:
            img: A four dimensional numpy array to embed using the keras model.

        Returns:
            A numpy array, with a first dimension matching the first dimension
            of the input image.
        """

        img = cvtColor(img, COLOR_BGR2RGB)
        img = resize(img, self.input_shape)
        img = expand_dims(img, axis=0)

        # process the inputs image
        if self.preprocess_input:
            img = self.preprocess_input(img)

        # produce embeddings
        embed = self.model.predict(img)

        return {"embed": embed}


class EmbedImageKerasResNet50(EmbedImageKeras):
    """Example embedding using ResNet50.

    Provides an example of how to use an embedding annotator and provides
    easy access to one of the most popular models for computing image
    similarity metrics in an embedding space. See the (very minimal) source
    code for how to extend this function to other pre-built keras models.

    Attributes:
        model: The ResNet-50 model, tuned to produce the penultimate layer as
            an output.
        preprocess_input: Default processing function for an image provided as
            an array in RGB format.
    """

    def __init__(self):
        import tensorflow.keras.applications.resnet50

        ssl._create_default_https_context = ssl._create_unverified_context
        model = tensorflow.keras.applications.resnet50.ResNet50(weights="imagenet")
        ppobj = tensorflow.keras.applications.resnet50.preprocess_input

        super().__init__(model, ppobj, outlayer="avg_pool")


def _sub_image(img, top, right, bottom, left, fct=1, output_shape=None):
    """Take a subset of an input image and return a (resized) subimage.

    Args:
        img (numpy array): Image stored as a three-dimensional image (rows,
            columns, and color channels).
        top (int): Top coordinate of the new image.
        right (int): Right coordinate of the new image.
        bottom (int): Bottom coordinate of the new image.
        left (int): Left coordinate of the new image.
        fct (float): Percentage to expand the bounding box by. Defaults to
            1, using the input coordinates as given.
        output_shape (tuple): Size to scale the output image, in pixels. Set
            to None (default) to keep the native resolution.

    Returns:
        A three-dimensional numpy array describing the new image.
    """

    # convert to center, height and width:
    center = [int((top + bottom) / 2), int((left + right) / 2)]
    height = int((bottom - top) / 2 * fct)
    width = int((right - left) / 2 * fct)
    box = [
        center[0] - height,
        center[0] + height,
        center[1] - width,
        center[1] + width,
    ]

    # crop the image as an array
    box[0] = max(0, box[0])
    box[2] = max(0, box[2])
    box[1] = min(img.shape[0], box[1])
    box[3] = min(img.shape[1], box[3])
    crop_img = img[box[0] : box[1], box[2] : box[3], :]

    if output_shape:
        img_scaled = resize(crop_img, output_shape)
    else:
        img_scaled = crop_img

    return uint8(img_scaled)


def _trim_bbox(css, image_shape):
    """Given a bounding box and image size, returns a new trimmed bounding box.

    Some algorithms produce bounding boxes that extend over the edges of the
    source image. This function takes such a box and returns a new bounding
    box trimmed to the source.

    Args:
        css (array): An array of dimension four.
        image_shape (array): An array of dimension two.

    Returns:
        An updated bounding box trimmed to the extend of the image.
    """
    return (
        max(css[0], 0),
        min(css[1], image_shape[1]),
        min(css[2], image_shape[0]),
        max(css[3], 0),
    )
