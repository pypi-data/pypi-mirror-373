import os

import pytest
from rara_tools.s3 import S3Files

S3_FILES = S3Files(
    url = os.getenv("S3_URL", "s3.eu-central-003.backblazeb2.com"),
    access_key = os.getenv("S3_ACCESS_KEY", ""),
    secret_key = os.getenv("S3_SECRET_KEY", ""),
    bucket = os.getenv("S3_TEST_BUCKET", "rara-test")
)
TEST_PREFIX = "test/"
TEST_FILE = "./tests/test_data/test.txt"
TEST_FOLDER = "./tests/test_data/test_folder"
TEST_FILE_S3 = None
TEST_FOLDER_S3 = None


@pytest.mark.order(1)
def test_s3_listing():
    """Tests the file listing feature.
    """
    # test full_listing
    file_list = S3_FILES.list()
    assert len(file_list) > 1
    # test prefix listing
    file_list_eesti = S3_FILES.list(prefix="eesti")
    assert len(file_list_eesti) == 1
    file_list_mets_alto = S3_FILES.list(prefix="mets_alto")
    assert len(file_list_mets_alto) > 1

@pytest.mark.order(2)
def test_s3_file_upload():
    """Tests uploading a file to S3.
    """
    uploaded = S3_FILES.upload(TEST_FILE, prefix=TEST_PREFIX)
    assert uploaded in S3_FILES.list()
    # update global variable to reflect the actual file name given by the package
    global TEST_FILE_S3
    TEST_FILE_S3 = uploaded

@pytest.mark.order(3)
def test_s3_file_download():
    """Tests downloading a file from S3.
    """
    downloaded = list(S3_FILES.download(TEST_FILE_S3))
    assert f"./{TEST_FILE_S3}" in downloaded
    assert os.path.exists(TEST_FILE_S3)
    # remove downloaded files
    for f in downloaded:
        os.remove(f)
    # remove test dir
    os.rmdir("test")

@pytest.mark.order(4)
def test_s3_file_delete():
    """Tests deleting files from S3 bucket.
    """
    S3_FILES.delete(TEST_FILE_S3)
    assert TEST_FILE_S3 not in S3_FILES.list()

@pytest.mark.order(5)
def test_s3_folder_upload():
    """Tests uploading folders to S3 bucket.
    """
    uploaded = S3_FILES.upload(TEST_FOLDER, prefix=TEST_PREFIX)
    assert len(S3_FILES.list(prefix=uploaded)) == 3
    # update global variable to reflect the actual folder name given by the package
    global TEST_FOLDER_S3
    TEST_FOLDER_S3 = uploaded

@pytest.mark.order(6)
def test_s3_folder_download():
    """Tests downloading folders from S3 bucket.
    """
    downloaded = list(S3_FILES.download(TEST_FOLDER_S3))
    for dl_file in downloaded:
        assert dl_file.startswith(f"./{TEST_FOLDER_S3}")
    assert os.path.exists(TEST_FOLDER_S3)
    # remove downloaded files
    for f in downloaded:
        os.remove(f)
    # remove test dir
    os.rmdir(TEST_FOLDER_S3)
    os.rmdir("test")

@pytest.mark.order(7)
def test_s3_folder_delete():
    """Tests deleting folders from S3 bucket.
    """
    S3_FILES.delete(TEST_FOLDER_S3)
    assert len(S3_FILES.list(prefix=TEST_FOLDER_S3)) == 0
