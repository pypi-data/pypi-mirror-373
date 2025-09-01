import os

from PIL import Image


class ImageToPDFConverter:
    @staticmethod
    def convert(image_path: str) -> str:
        """
        Convert a single image file (JPG, JPEG, PNG) to a PDF and return the path to the created PDF file.

        Parameters
        ----------
        image_path : str
            The path to the image file.

        Returns
        -------
        str
            The path to the created PDF file.
        """
        output_pdf_path = os.path.splitext(image_path)[0] + ".pdf"

        try:
            # Open the image and convert to RGB (if necessary)
            image = Image.open(image_path).convert("RGB")

            # Save the image as a PDF with 300 DPI
            image.save(output_pdf_path, format="PDF", dpi=(300, 300))

            return output_pdf_path
        except Exception as e:
            raise RuntimeError(f"Error converting image to PDF: {e}")
