import tempfile
import os

"""
Writes the given data to file_loc. Ensures that the directory exists
and uses a temporary file to ensure that the file is written atomically.
"""


def safe_write_to_disk(file_loc, data):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_loc), exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "w", dir=os.path.dirname(file_loc), delete=False
    ) as f:
        f.write(data)
        tmp_file = f.name
    os.rename(tmp_file, file_loc)
