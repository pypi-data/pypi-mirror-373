import logging
import os
import subprocess
import uuid

from rara_digitizer.exceptions import ConversionFailed

logger = logging.getLogger("rara-digitizer")


class DOCToDOCXConverter:
    @staticmethod
    def convert(input_doc: str) -> str | None:
        """
        Converts a .doc file to a .docx file using LibreOffice's lowriter, with the output file
        named as a random UUID.

        Parameters
        ----------
        input_doc : str
            The path to the input .doc file.

        Returns
        -------
        str | None
            The path to the converted .docx file with a random UUID name, or None if the conversion fails.
        """
        try:
            output_dir = os.path.dirname(input_doc)

            # Use lowriter to convert .doc to .docx
            subprocess.run(
                ["lowriter", "--convert-to", "docx", "--outdir", output_dir, input_doc],
                check=True,
            )

            original_docx = os.path.splitext(input_doc)[0] + ".docx"
            output_docx = os.path.join(output_dir, f"{uuid.uuid4()}.docx")
            if os.path.exists(original_docx):
                os.rename(original_docx, output_docx)
                return output_docx
            else:
                raise ConversionFailed(f"Conversion failed: {input_doc}")

        except subprocess.CalledProcessError as e:
            logger.info(f"Error converting DOC to DOCX: {e}")
            return None
