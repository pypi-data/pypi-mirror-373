import os

import requests

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(TEST_DIR)
TEST_DATA_DIR = os.path.join(TEST_DIR, "test_data")
TEST_OUTPUT_DIR = os.path.join(TEST_DIR, "test_output")


def get_file_by_pdb_id(pdb_id, ext="cif", data_dir=TEST_DATA_DIR):
    pdb_id = pdb_id.lower()
    assert len(pdb_id) == 4, f"Invalid PDB ID: {pdb_id}"
    path = os.path.join(data_dir, f"{pdb_id}.{ext}")
    if not os.path.exists(path):
        path = download_pdb_file(pdb_id, ext=ext, data_dir=data_dir)
    return path


def download_pdb_file(pdb_id, ext="cif", data_dir=TEST_DATA_DIR):
    """Download PDB file from RCSB PDB."""
    url = f"https://files.rcsb.org/download/{pdb_id}.{ext}"
    response = requests.get(url)

    outpath = os.path.join(data_dir, f"{pdb_id}.{ext}")
    if response.status_code == 200:
        with open(outpath, "w") as file:
            file.write(response.text)
    else:
        print(
            f"Failed to download PDB file for {pdb_id}. Status code: {response.status_code}"
        )
        return None

    return outpath


if __name__ == "__main__":
    download_pdb_file("4wqs", ext="cif")
