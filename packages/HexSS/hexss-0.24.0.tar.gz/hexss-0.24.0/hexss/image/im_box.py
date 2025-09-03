from pathlib import Path
from typing import Union, Optional

from hexss.box import Box
from hexss.image import Image, ImageFont
from hexss.image.classifier import Classifier
from hexss.image.detector import Detector


class Models:
    def __init__(self, model_path: Union[Path, str]):
        self.classifiers = {}
        self.detectors = {}
        self.model_path = Path(model_path)
        self.classifier_model_path = self.model_path / 'classifier'
        self.detector_model_path = self.model_path / 'detector'

    def add_model(self, model_name: str, type_: str):
        if type_ == 'classifier':
            if model_name not in self.classifiers:
                model_file = self.classifier_model_path / model_name / 'model' / f'{model_name}.keras'
                self.classifiers[model_name] = Classifier(model_file)
                if self.classifiers[model_name].model is None:
                    try:
                        self.classifiers[model_name].train(
                            self.model_path / fr'classifier/{model_name}/datasets',
                            epochs=200
                        )
                    except:
                        ...
        elif type_ == 'detector':
            if model_name not in self.detectors:
                last_model = list((self.detector_model_path / model_name / 'model').iterdir())[-1]
                model_file = last_model / 'weights/best.pt'
                if model_file.exists():
                    self.detectors[model_name] = Detector(model_file)

    def load_all(self, root_dict: dict):
        def recurse(node):
            if isinstance(node, dict):
                cls = node.get('classifier')
                if isinstance(cls, dict) and cls.get('name'):
                    self.add_model(cls['name'], 'classifier')
                det = node.get('detector')
                if isinstance(det, dict) and det.get('name'):
                    self.add_model(det['name'], 'detector')
                for value in node.values():
                    recurse(value)
            elif isinstance(node, list):
                for item in node:
                    recurse(item)

        recurse(root_dict)


class ImageBox:
    def __init__(self, name: str, box: Box):
        self.name = name
        self.box = box
        self.color = (255, 255, 0)
        self.width = 5
        self.text_color = 'black'
        self.text_stroke_color = 'white'
        self.show_name = True
        self.font = ImageFont.truetype('arial.ttf', 20)

        self.image = None
        self.boxes = {}

        self.detector_name = None
        self.detections = []
        self.detector_should_count = 0
        self.detector_classifier_name = None
        self.detector_boxes = []

        self.classifier_name = None
        self.classification = None
        self.classifier_ok_group = []
        self.classifier_ng_group = []

    def add(self, box: 'ImageBox'):
        self.boxes[box.name] = box

    def set_image(self, image: Image):
        self.image = image
        self.box.set_size(image.size)
        for name, child in self.boxes.items():
            child.box.set_size(self.box.xywh[2:])
            child.box.set_size(self.box.xywh[2:])
            child.set_image(image.crop(child.box).copy())

    def predict(self, models: Optional[Models] = None):
        print(f'predict {self.name}', self.classifier_name, self.detector_name)
        if self.image is None or models is None:
            return

        if self.detector_name in models.detectors:
            print('  detect...')
            self.detections = models.detectors[self.detector_name].detect(self.image)
            print(f'    {self.detections}')
            self.detector_boxes = []  # reset old data
            for i, detection in enumerate(self.detections):
                imbox = ImageBox(f'd{i}', Box(xywhn=detection.xywhn))
                imbox.classifier_name = self.detector_classifier_name
                imbox.image = self.image.crop(xywhn=detection.xywhn).copy()
                imbox.show_name = False
                self.detector_boxes.append(imbox)
            print(f'    {len(self.detections)} detections')

        if self.classifier_name in models.classifiers:
            print('  classify...')
            if models.classifiers[self.classifier_name].model is not None:
                self.classification = models.classifiers[self.classifier_name].classify(self.image)
                if self.classification.name == 'ok':
                    self.color = 'green'
                elif self.classification.name == 'ng':
                    self.color = 'red'
                else:
                    self.color = '#22f'
                print(f'    classified as: {self.classification}')

        for child in self.detector_boxes:
            child.predict(models)
        for child in self.boxes.values():
            child.predict(models)

    def save(self, path: Union[str, Path]):
        if self.image:
            self.image.save(path)

    def draw_all(self, image: Image):
        draw = image.draw()
        self.box.set_size(image.size)

        if self.box.type == 'polygon':
            draw.polygon(self.box, outline=self.color, width=self.width)
            if self.show_name:
                draw.text(self.box.points[0], self.name, font=self.font, fill=self.text_color,
                          stroke_width=self.width, stroke_fill=self.text_stroke_color)
        elif self.box.type == 'box':
            draw.rectangle(self.box.xyxy, outline=self.color, width=self.width)
            if self.show_name:
                draw.text(self.box.x1y1, self.name, font=self.font, fill=self.text_color,
                          stroke_width=self.width, stroke_fill=self.text_stroke_color)

        cropped = image.crop(self.box.xyxy).copy()
        for child in self.boxes.values():
            child.draw_all(cropped)
        for child in self.detector_boxes:
            child.draw_all(cropped)
        image.overlay(cropped, self.box.x1y1.astype(int).tolist())

    @classmethod
    def from_dict(cls, data: dict) -> 'ImageBox':
        def create_box(name: str, box_data: dict) -> 'ImageBox':
            box = cls(name, Box(
                xywhn=box_data.get('xywhn'),
                pointsn=box_data.get('pointsn')
            ))

            image_data = box_data.get('image')
            if image_data is not None:
                boxes_data = image_data.get('boxes')
                classifier_data = image_data.get('classifier')
                detector_data = image_data.get('detector')

                if boxes_data is not None:
                    for child_name, child_data in boxes_data.items():
                        child_box = create_box(child_name, child_data)
                        box.add(child_box)
                if classifier_data is not None:
                    box.classifier_name = classifier_data.get('name')
                    box.classifier_ok_group = classifier_data.get('ok_group')
                    box.classifier_ng_group = classifier_data.get('ng_group')

                if detector_data is not None:
                    box.detector_name = detector_data.get('name')
                    box.detector_should_count = detector_data.get('should_count')
                    _classifier = detector_data.get('classifier')
                    if _classifier:
                        box.detector_classifier_name = _classifier.get('name')

            return box

        root = cls("root", Box(xywhn=[0.5, 0.5, 1.0, 1.0]))
        root_data = data.get('boxes', {})
        for name, box_data in root_data.items():
            root.add(create_box(name, box_data))
        return root
