# -*- coding: utf-8 -*-
"""Annotators that require installing keras and tensorflow.
"""

from numpy import array, repeat, sum as np_sum, vstack
from pandas import DataFrame

from .abstract import ImageAnnotator


class InstanceAnnotator(ImageAnnotator):
    """Annotator for detecting instances of objects."""

    def __init__(self, model_name="mask_rcnn_R_50_FPN_3x", device="cpu"):
        mname = "COCO-InstanceSegmentation/" + model_name + ".yaml"
        self.predictor, self.mdata = _load_detectron_model(mname, device)
        self.predictions = None

    def annotate_image(self, img):
        """Annotate the batch of frames with the face annotator."""
        self.predictions = self.predictor(img)
        instances = self.predictions["instances"]
        if not len(instances):
            return {"instance": DataFrame(columns = [
                "index",
                "height",
                "width",
                "class",
                "prob",
                "x0",
                "y0",
                "x1",
                "y1"
            ])}

        boxes = instances.get("pred_boxes").tensor.cpu().numpy()
        cls = [
            self.mdata.thing_classes[x]
            for x in instances.get("pred_classes").cpu().numpy()
        ]
        scores = instances.get("scores").cpu().numpy()

        output = {
            "index": list(range(len(cls))),
            "height": img.shape[0],
            "width": img.shape[1],
            "class": cls,
            "prob": scores,
            "x0": boxes[:, 0],
            "y0": boxes[:, 1],
            "x1": boxes[:, 2],
            "y1": boxes[:, 3],
        }

        return {"instance": output}

    def get_last_predictions(self):
        """Get last predictions as a Detectron classed object."""
        return self.predictions

    def visualize_last_predictions(self, img):
        """Return annotated image"""
        from detectron2.utils.visualizer import Visualizer

        viz = Visualizer(img[:, :, ::-1], self.mdata)
        out = viz.draw_instance_predictions(
            self.predictions["instances"].to("cpu")
        )
        return out.get_image()[:, :, ::-1]


class LVISAnnotator(ImageAnnotator):
    """Annotator for performing Large Vocabulary Instance Segmentation."""

    def __init__(
        self, model_name="mask_rcnn_X_101_32x8d_FPN_1x", device="cpu"
    ):
        mname = "LVISv0.5-InstanceSegmentation/" + model_name + ".yaml"
        self.predictor, self.mdata = _load_detectron_model(mname, device)
        self.predictions = None

    def annotate_image(self, img):
        """Annotate the batch of frames with the annotator."""
        self.predictions = self.predictor(img)
        instances = self.predictions["instances"]
        if not len(instances):
            return {"lvis": DataFrame(columns = [
                "index",
                "height",
                "width",
                "class",
                "prob",
                "x0",
                "y0",
                "x1",
                "y1"
            ])}

        boxes = instances.get("pred_boxes").tensor.cpu().numpy()
        cls = [
            self.mdata.thing_classes[x]
            for x in instances.get("pred_classes").cpu().numpy()
        ]
        scores = instances.get("scores").cpu().numpy()

        output = {
            "index": list(range(len(cls))),
            "height": img.shape[0],
            "width": img.shape[1],
            "class": cls,
            "prob": scores,
            "x0": boxes[:, 0],
            "y0": boxes[:, 1],
            "x1": boxes[:, 2],
            "y1": boxes[:, 3],
        }

        return {"lvis": output}

    def get_last_predictions(self):
        """Get last predictions as a Detectron classed object."""
        return self.predictions

    def visualize_last_predictions(self, img):
        """Return annotated image"""
        from detectron2.utils.visualizer import Visualizer

        viz = Visualizer(img[:, :, ::-1], self.mdata)
        out = viz.draw_instance_predictions(
            self.predictions["instances"].to("cpu")
        )
        return out.get_image()[:, :, ::-1]


class CityscapesAnnotator(ImageAnnotator):
    """Annotator for performing Cityscape Instance Segmentation."""

    def __init__(self, model_name="mask_rcnn_R_50_FPN", device="cpu"):
        mname = "Cityscapes/" + model_name + ".yaml"
        self.predictor, self.mdata = _load_detectron_model(mname, device)
        self.predictions = None

    def annotate_image(self, img):
        """Annotate the batch of frames with the annotator."""
        self.predictions = self.predictor(img)
        instances = self.predictions["instances"]
        if not len(instances):
            return {"cityscape": DataFrame(columns = [
                "index",
                "height",
                "width",
                "class",
                "prob",
                "x0",
                "y0",
                "x1",
                "y1"
            ])}

        boxes = instances.get("pred_boxes").tensor.cpu().numpy()
        cls = [
            self.mdata.thing_classes[x]
            for x in instances.get("pred_classes").cpu().numpy()
        ]
        scores = instances.get("scores").cpu().numpy()

        output = {
            "index": list(range(len(cls))),
            "height": img.shape[0],
            "width": img.shape[1],
            "class": cls,
            "prob": scores,
            "x0": boxes[:, 0],
            "y0": boxes[:, 1],
            "x1": boxes[:, 2],
            "y1": boxes[:, 3],
        }

        return {"cityscape": output}

    def get_last_predictions(self):
        """Get last predictions as a Detectron classed object."""
        return self.predictions

    def visualize_last_predictions(self, img):
        """Return annotated image"""
        from detectron2.utils.visualizer import Visualizer

        viz = Visualizer(img[:, :, ::-1], self.mdata)
        out = viz.draw_instance_predictions(
            self.predictions["instances"].to("cpu")
        )
        return out.get_image()[:, :, ::-1]


class KeypointsAnnotator(ImageAnnotator):
    """Annotator for detecting human body keypoints."""

    def __init__(self, model_name="keypoint_rcnn_R_50_FPN_3x", device="cpu"):
        mname = "COCO-Keypoints/" + model_name + ".yaml"
        self.predictor, self.mdata = _load_detectron_model(mname, device)
        self.predictions = None

    def annotate_image(self, img):
        """Annotate the batch of frames with the face annotator."""
        self.predictions = self.predictor(img)
        instances = self.predictions["instances"]

        cls = [
            self.mdata.thing_classes[x]
            for x in instances.get("pred_classes").cpu().numpy()
        ]

        keypoints = instances.get("pred_keypoints").cpu().numpy()
        if not len(keypoints):
            return {"keypoint": DataFrame(columns = [
                "index",
                "kpname",
                "x",
                "y",
                "score"
            ])}

        keypoints = vstack([x for x in keypoints])

        output = {
            "index": repeat(array(range(len(cls))), 17),
            "kpname": self.mdata.keypoint_names * len(cls),
            "x": keypoints[:, 0],
            "y": keypoints[:, 1],
            "score": keypoints[:, 2],
        }

        return {"keypoint": output}

    def get_last_predictions(self):
        """Get last predictions as a Detectron classed object."""
        return self.predictions

    def visualize_last_predictions(self, img):
        """Return annotated image"""
        from detectron2.utils.visualizer import Visualizer

        viz = Visualizer(img[:, :, ::-1], self.mdata)
        keypoints = (
            self.predictions["instances"].get("pred_keypoints").to("cpu")
        )

        if not len(keypoints):
            return img
        for keyp in keypoints:
            out = viz.draw_and_connect_keypoints(keyp)

        return out.get_image()[:, :, ::-1]


class PanopticAnnotator(ImageAnnotator):
    """Annotator for detecting things and stuff."""

    def __init__(self, model_name="panoptic_fpn_R_50_3x", device="cpu"):
        mname = "COCO-PanopticSegmentation/" + model_name + ".yaml"
        self.predictor, self.mdata = _load_detectron_model(mname, device)
        self.predictions = None

    def annotate_image(self, img):
        """Annotate the batch of frames with the face annotator."""
        self.predictions = self.predictor(img)
        panseg = self.predictions["panoptic_seg"]
        if not len(panseg):
            return {"panoptic": DataFrame(columns = [
                "index",
                "height",
                "width",
                "score",
                "is_thing",
                "class",
                "area"
            ])}

        is_thing = [x.get("isthing") for x in panseg[1]]
        score = [x.get("score", 0) for x in panseg[1]]
        category_id = [x.get("category_id") for x in panseg[1]]
        area = [
            np_sum(panseg[0].cpu().numpy().flatten() == (k + 1))
            for k in range(len(panseg[1]))
        ]
        category_name = []
        for cat, thing in zip(category_id, is_thing):
            if thing:
                category_name += [self.mdata.thing_classes[cat]]
            else:
                category_name += [self.mdata.stuff_classes[cat]]

        output = {
            "index": list(range(len(category_name))),
            "height": img.shape[0],
            "width": img.shape[1],
            "score": score,
            "is_thing": is_thing,
            "class": category_name,
            "area": area,
        }

        return {"panoptic": output}

    def get_last_predictions(self):
        """Get last predictions as a Detectron classed object."""
        return self.predictions

    def visualize_last_predictions(self, img):
        """Return annotated image"""
        from detectron2.utils.visualizer import Visualizer

        panoptic_seg, segments_info = self.predictions["panoptic_seg"]
        viz = Visualizer(img[:, :, ::-1], self.mdata)
        out = viz.draw_panoptic_seg(panoptic_seg.to("cpu"), segments_info)
        return out.get_image()[:, :, ::-1]


def _load_detectron_model(mname, device="cpu"):
    import ssl
    from detectron2 import model_zoo
    from detectron2.config import get_cfg
    from detectron2.data import MetadataCatalog
    from detectron2.engine import DefaultPredictor

    ssl._create_default_https_context = ssl._create_unverified_context

    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(mname))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    cfg.MODEL.DEVICE = device
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(mname)
    predictor = DefaultPredictor(cfg)
    mdata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])
    return predictor, mdata
