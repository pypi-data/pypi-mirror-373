import numpy as np
from PIL import Image
from ultralytics import YOLO


class YOLOImageDetector:

    def __init__(self, model_path: str):
        """
        Initialize the YOLO model for object detection (used for detecting images within documents).

        Parameters
        ----------
        model_path : str, optional
            Path to the YOLO model file. If not provided, a default model will be loaded.
        """
        self.yolo_model = YOLO(model_path)

    def detect_regions(
        self, input_image_file_path: str
    ) -> list[dict[str, Image.Image | str | int]]:
        """
        Detects regions in an image using YOLO, cuts them out, and returns them as a list of dictionaries,
        where each dictionary contains the label and the cropped image.

        Possible labels are:
            - Text: Regular paragraphs.
            - Picture: A graphic or photograph.
            - Caption: Special text outside a picture or table that introduces this picture or table.
            - Section-header: Any kind of heading in the text, except overall document title.
            - Footnote: Typically small text at the bottom of a page, with a number or symbol that is referred
                        to in the text above.
            - Formula: Mathematical equation on its own line.
            - Table: Material arranged in a grid alignment with rows and columns, often with separator lines.
            - List-item: One element of a list, in a hanging shape, i.e., from the second line onwards the paragraph
                         is indented more than the first line.
            - Page-header: Repeating elements like page number at the top, outside of the normal text flow.
            - Page-footer: Repeating elements like page number at the bottom, outside of the normal text flow.
            - Title: Overall title of a document, (almost) exclusively on the first page and typically
                     appearing in large font.

        Parameters
        ----------
        input_image_file_path : str
            The image file path to read in and in which to detect regions.

        Returns
        -------
        list[dict[str, Image | str | int]]
            A list of dictionaries, where each dictionary contains the label, the cropped image,
            and the region's position.
        """
        input_image = np.array(Image.open(input_image_file_path))

        result = self.yolo_model.predict(input_image, verbose=False)[0]
        height, width = input_image.shape[:2]

        bounding_boxes = [
            (
                int(box[0] * width),
                int(box[1] * height),
                int(box[2] * width),
                int(box[3] * height),
            )
            for box in result.boxes.xyxyn.tolist()
        ]
        labels = [
            self.yolo_model.names[int(label)] for label in result.boxes.cls.tolist()
        ]

        detected_labels_and_regions = []
        for box, label in zip(bounding_boxes, labels):
            x1, y1, x2, y2 = box
            cropped_image = Image.fromarray(input_image[y1:y2, x1:x2])

            detected_label_and_region = {
                "label": label,
                "cropped_image": cropped_image,
                "HPOS": x1,
                "VPOS": y1,
                "WIDTH": x2 - x1,
                "HEIGHT": y2 - y1,
            }

            detected_labels_and_regions.append(detected_label_and_region)

        return detected_labels_and_regions
