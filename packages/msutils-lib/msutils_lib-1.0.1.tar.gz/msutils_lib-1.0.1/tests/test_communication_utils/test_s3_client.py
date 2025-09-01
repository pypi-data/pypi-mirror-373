from io import BytesIO

from ms_utils.communication_utils import S3BucketClient


def test_s3_client():
    # Remplacez par vos propres clés et nom de bucket
    client = S3BucketClient(
        bucket_type="scaleway",
        endpoint_url="https://bucket-ai-platform.s3.fr-par.scw.cloud",
    )

    assert client.test_connection()
    assert client.upload_file(
        "./tests/data/test.txt",
        bucket_name="test",
        object_name="test/test.txt",
    )
    assert isinstance(
        client.download_file(bucket_name="test", object_name="test/test.txt"),
        BytesIO,
    )
    assert (
        client.get_file_metadata(
            bucket_name="test", object_name="test/test.txt"
        )
        is not None
    )
    assert (
        client.get_file_metadata(
            bucket_name="test", object_name="test/test.txt"
        )["filename"]
        == "test.txt"
    )
    assert client.delete_file(bucket_name="test", object_name="test/test.txt")


if __name__ == "__main__":
    test_s3_client()
