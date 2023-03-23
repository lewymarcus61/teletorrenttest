import os
import zipfile
import rarfile


async def extract_archive(archive_path, output_dir=None):
    """
    Extracts the contents of a ZIP or RAR archive to the specified output directory.
    If output directory is not specified, the contents are extracted to the same directory as the input file.

    :param archive_path: Path to the archive file to extract.
    :param output_dir: Optional output directory. If not specified, the contents are extracted to the same directory as the input file.
    """
    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"Archive file not found: {archive_path}")

    if output_dir is None:
        output_dir = os.path.dirname(archive_path)
    elif not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path, 'r') as zip_file:
            zip_file.extractall(output_dir)
    elif rarfile.is_rarfile(archive_path):
        with rarfile.RarFile(archive_path, 'r') as rar_file:
            rar_file.extractall(output_dir)
    else:
        raise ValueError(f"Unsupported archive format: {archive_path}")


#extract_archive('download/mg-001/Tsukimichi Moonlit Fantasy Op.zip', None)

