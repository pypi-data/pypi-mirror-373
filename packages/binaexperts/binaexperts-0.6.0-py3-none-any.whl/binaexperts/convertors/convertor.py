import io
import logging
import os
import zipfile
from io import BytesIO
from typing import Any, Union, IO
from binaexperts.convertors import const
from binaexperts.convertors.base import YOLOConvertor, COCOConvertor, BinaExpertsConvertor
from binaexperts.common.utils import detect_format

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Convertor:
    """
    A class responsible for converting datasets between different formats (YOLO, COCO, BinaExperts).

    This class facilitates the conversion of datasets by using the appropriate convertor based on the detected
    format of the dataset. It supports loading data from different sources (file paths, in-memory objects),
    normalizing it, and converting it to the target format.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_convertor(format_type: str):
        """
        Get the appropriate convertor class based on the detected format type.

        :param format_type: The type of dataset format (e.g., 'yolo', 'coco', 'binaexperts', 'yolov8-obb').
        :return: An instance of the corresponding convertor class.
        :raises ValueError: If the provided format type is not supported.
        """
        if format_type == const.CONVERTOR_FORMAT_YOLO or format_type == const.CONVERTOR_FORMAT_YOLOv8_obb:
            return YOLOConvertor()
        elif format_type == const.CONVERTOR_FORMAT_COCO:
            return COCOConvertor()
        elif format_type == const.CONVERTOR_FORMAT_BINAEXPERTS:
            return BinaExpertsConvertor()
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def convert(
            self,
            target_format: str,
            source: Union[str, IO[bytes]],
            destination: Union[str, IO[bytes]] = None
    ) -> Union[None, IO[bytes]]:
        """
        Convert a dataset to the target format and save the output.

        This method detects the format of the source dataset, then converts it to the specified target format.
        The converted dataset can either be saved to a file (specified in `destination`) or returned as an
        in-memory object if no destination is provided.

        :param target_format: The format of the target dataset (e.g., 'yolo', 'coco', 'binaexperts', 'yolov8-obb').
        :param source: The source dataset, either as a file path or an in-memory object (BytesIO).
        :param destination: (Optional) The destination to save the converted dataset. Can be a directory path,
                            file path, or an in-memory object (BytesIO).
        :return: None if saved to disk, or an in-memory IO object containing the converted dataset.
        :raises ValueError: If the target format is unsupported or the format detection fails.
        """
        temp_zip_file_obj = None  # To hold a zipfile.ZipFile object if created from BytesIO

        try:
            effective_source_for_detection = source
            if isinstance(source, io.BytesIO):
                source.seek(0)  # Ensure the BytesIO cursor is at the beginning
                try:
                    # Create a zipfile.ZipFile object from BytesIO for consistent handling
                    temp_zip_file_obj = zipfile.ZipFile(source, 'r')
                    effective_source_for_detection = temp_zip_file_obj
                except zipfile.BadZipFile as e:
                    # If BytesIO is not a valid zip, raise an error immediately
                    raise ValueError(
                        f"In-memory source is not a valid zip file: {e}")

            # Detect source format using the potentially wrapped source (zipfile.ZipFile, path, etc.)
            source_format = detect_format(effective_source_for_detection)
            logger.info(
                f"Detected source format: {source_format}. Converting to {target_format}...")

            # Get the correct convertors based on the detected source and target formats
            source_convertor = self.get_convertor(source_format)
            target_convertor = self.get_convertor(target_format)

            # Re-ensure original BytesIO source is at the beginning if a temp_zip_file_obj was created
            # This is important for the `load` method to correctly read from the original stream.
            if temp_zip_file_obj:
                source.seek(0)
                # Pass the original BytesIO to load
                source_data = source_convertor.load(source)
            elif isinstance(source, str):
                # If source is a string path, determine if it's a zip or directory
                if zipfile.is_zipfile(source):
                    with zipfile.ZipFile(source, 'r') as zip_ref:
                        source_data = source_convertor.load(zip_ref)
                elif os.path.isdir(source):
                    source_data = source_convertor.load(source)
                else:
                    raise ValueError(
                        f"Source path '{source}' is not a valid zip file or directory.")
            else:  # This path is for other IO types that are not BytesIO, or already open ZipFile objects
                source.seek(0)  # Ensure IO object is at the beginning
                source_data = source_convertor.load(source)

            # Convert to the normalized format
            normalized_data = source_convertor.normalize(source_data)

            # Convert normalized data to target format.
            # Pass the actual target_format to the target_convertor's convert method
            target_data = target_convertor.convert(
                normalized_data, target_format)

            # If destination is specified, save the output to it
            if destination:
                # The save method for each convertor handles how to save to the specific destination type (path or BytesIO)
                target_convertor.save(target_data, destination)
                logger.info(
                    f"Conversion completed! Output saved to: {destination}.")
                return None  # No need to return anything when saved to disk

            else:
                # No destination provided, output the result as an in-memory IO object
                in_memory_output = BytesIO()
                # Save to in-memory object
                target_convertor.save(target_data, in_memory_output)
                # Reset pointer to the beginning of the BytesIO object
                in_memory_output.seek(0)
                logger.info(
                    "Conversion completed! Output returned as in-memory BytesIO object.")
                return in_memory_output

        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise
        finally:
            # Ensure the temporary zipfile.ZipFile object is closed if it was created
            if temp_zip_file_obj:
                temp_zip_file_obj.close()
