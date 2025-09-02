import os

import pytest
from rara_tools.exceptions import (S3ConnectionException, S3InitException,
                                   S3InputException)
from rara_tools.s3 import S3Files

TEST_URL = os.getenv("S3_URL", "s3.eu-central-003.backblazeb2.com")
TEST_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
TEST_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
TEST_BUCKET = os.getenv("S3_TEST_BUCKET", "rara-test")


def test_s3_missing_init_params():
    """Tests class init with missing params.
    """
    # Missing URL
    with pytest.raises(S3InitException) as exception_info:
        S3Files()
    assert "URL" in str(exception_info.value)
    # Missing access key
    with pytest.raises(S3InitException) as exception_info:
        S3Files(url="asd")
    assert "access key" in str(exception_info.value)
    # MIssing secret key
    with pytest.raises(S3InitException) as exception_info:
        S3Files(url="asd", access_key="asd")
    assert "secret key" in str(exception_info.value)
    # Missing bucket
    with pytest.raises(S3InitException) as exception_info:
        S3Files(url="asd", access_key="asd", secret_key="asd")
    assert "Bucket" in str(exception_info.value)

def test_s3_incorrect_init_params():
    """Tests class init with incorrect params.
    """
    # Incorrect URL
    with pytest.raises(S3ConnectionException) as exception_info:
        S3Files(
            url="kuhuiganes.com",
            access_key="asd",
            secret_key="asd",
            bucket="asd"
        )
    assert "Error connecting to bucket" in str(exception_info.value)
    assert "Max retries exceeded" in str(exception_info.value)
    # Incorrect access key
    with pytest.raises(S3ConnectionException) as exception_info:
        S3Files(
            url=TEST_URL,
            access_key="asd",
            secret_key="asd",
            bucket="asd"
        )
    assert "Error connecting to bucket" in str(exception_info.value)
    assert "InvalidAccessKeyId" in str(exception_info.value)
    # Incorrect secret key
    with pytest.raises(S3ConnectionException) as exception_info:
        S3Files(
            url=TEST_URL,
            access_key=TEST_ACCESS_KEY,
            secret_key="asd",
            bucket="asd"
        )
    assert "Error connecting to bucket" in str(exception_info.value)
    assert "SignatureDoesNotMatch" in str(exception_info.value)
    # Incorrect bucket
    with pytest.raises(S3ConnectionException) as exception_info:
        S3Files(
            url=TEST_URL,
            access_key=TEST_ACCESS_KEY,
            secret_key=TEST_SECRET_KEY,
            bucket="asd"
        )
    assert "Error connecting to bucket" in str(exception_info.value)
    assert "AccessDenied" in str(exception_info.value)


def test_s3_incorrect_path():
    """Tests class methods with incorrect input paths.
    """
    s3 = S3Files(
            url=TEST_URL,
            access_key=TEST_ACCESS_KEY,
            secret_key=TEST_SECRET_KEY,
            bucket=TEST_BUCKET
    )
    # incorrect upload path
    with pytest.raises(S3InputException) as exception_info:
        s3.upload("alksje")
    assert "does not exist" in str(exception_info.value)
