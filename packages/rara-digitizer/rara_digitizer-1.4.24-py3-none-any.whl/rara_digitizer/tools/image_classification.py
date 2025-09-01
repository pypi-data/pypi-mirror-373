import logging
from typing import List, Dict, Optional

import numpy as np
import torch

from ..factory.resource_manager import ResourceManager

logger = logging.getLogger("rara-digitizer")


class ImageClassificator:
    def __init__(self, resource_manager: ResourceManager, local_image_classifier_path: Optional[str] = None, ):
        """
        Image classification using a ViT model with batch processing.

        Parameters
        ----------
        resource_manager: ResourceManager
            Class that caches and returns statically used resources throughout different tools and handlers.
        """
        self.resource_manager = resource_manager
        if local_image_classifier_path:
            logger.info(f"Using custom image classifier: {local_image_classifier_path}")

        self.image_classifier = self.resource_manager.image_classifier(path=local_image_classifier_path)
        self.image_feature_extractor = self.resource_manager.image_feature_extractor(path=local_image_classifier_path)

    def classify_images(
            self, images: List[np.ndarray], batch_size: int = 16
    ) -> List[str]:
        """
        Classify a batch of input images and return the most likely label for each.

        Parameters
        ----------
        images : list[np.ndarray]
            List of input images as NumPy arrays.

        batch_size: int
            How much to process at a time, the more the faster but more resource intensive.

        Returns
        -------
        list[str]
            List of predicted labels for each image.
        """
        logger.info(f"Classifying images in {len(images) // batch_size + 1} batches")
        all_labels = []

        for i in range(0, len(images), batch_size):
            batch_images = images[i: i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}")
            inputs = self.image_feature_extractor(
                images=batch_images, return_tensors="pt", padding=True
            )
            outputs = self.image_classifier(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1).detach().numpy()
            batch_labels = [
                self.image_classifier.config.id2label[np.argmax(probs)]
                for probs in probabilities
            ]
            all_labels.extend(batch_labels)

        return all_labels

    def classify_extracted_images(
            self, extracted_images: List[Dict], allowed_labels: List[str] = None
    ) -> List[Dict]:
        """
        Classify the cropped images from the extracted image data and update their metadata.
        If a dictionary's "label" key contains an allowed label, it uses that label directly.

        Parameters
        ----------
        extracted_images : list[dict]
            List of dictionaries containing image metadata, including cropped images.

        allowed_labels : list[str]
            List of allowed labels to keep if they are already present in the metadata.

        Returns
        -------
        list[dict]
            The input list with updated metadata, including classification labels.
        """
        if allowed_labels is None:
            allowed_labels = ["tabel", "surmakuulutus"]

        images_to_classify = []
        indices_to_classify = []

        for idx, entry in enumerate(extracted_images):
            if "label" in entry and entry["label"] in allowed_labels:
                continue
            else:
                image = np.array(entry["cropped_image"])
                if image.ndim == 2:
                    image = np.stack((image,) * 3, axis=-1)
                images_to_classify.append(image)
                indices_to_classify.append(idx)

        if images_to_classify:
            logger.info(f"Total images to classify: {len(images_to_classify)}")
            labels = self.classify_images(images_to_classify)
            for idx, label in zip(indices_to_classify, labels):
                extracted_images[idx]["label"] = label

        return extracted_images
