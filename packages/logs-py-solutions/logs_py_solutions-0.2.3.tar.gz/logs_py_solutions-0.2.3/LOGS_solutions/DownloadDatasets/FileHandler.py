import re
import os


class FileHandler:
    @staticmethod
    def clean_filename(name: str) -> str:
        """Prepare the name as a file name. Remove unwanted special characters
        and replace a space with _.

        :param name: The name to be used as the file name.
        :return: The prepared filename.
        """

        pattern_unwanted_chars = r'[\[\]/\t\\:*?"<>|\x00-\x1F]'
        filename = re.sub(pattern_unwanted_chars, "", name)
        pattern_space = r"[\s]"
        return re.sub(pattern_space, "_", filename)

    def clean_foldername(name: str) -> str:
        """Prepare the name as a folder name. Remove unwanted special characters
        and replace a space with _.

        :param name: The name to be used as the folder name.
        :return: The prepared foldername.
        """

        name_without_extension = os.path.splitext(name)[0]
        pattern_unwanted_chars = r'[\[\]/\t\\:*?"<>|\x00-\x1F\.]'
        foldername = re.sub(pattern_unwanted_chars, "", name_without_extension)
        pattern_space = r"[\s]"
        return re.sub(pattern_space, "_", foldername)
