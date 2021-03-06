import json
import tempfile
import unittest

import boto3
import moto

from altimeter.core.artifact_io.exceptions import InvalidS3URIException
from altimeter.core.artifact_io.reader import FileArtifactReader, S3ArtifactReader, parse_s3_uri


class TestFileArtifactReader(unittest.TestCase):
    def test_with_valid_file(self):
        data = {"foo": "boo"}
        artifact_reader = FileArtifactReader()
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(json.dumps(data).encode("utf-8"))
            temp.flush()
            read_data = artifact_reader.read_artifact(temp.name)
        self.assertDictEqual(data, read_data)

    def test_with_invalid_file(self):
        data = "foo"
        artifact_reader = FileArtifactReader()
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(data.encode("utf-8"))
            temp.flush()
            with self.assertRaises(json.JSONDecodeError):
                artifact_reader.read_artifact(temp.name)


class TestS3ArtifactReader(unittest.TestCase):
    @moto.mock_s3
    def test_with_valid_object(self):
        data = {"foo": "boo"}
        s3_client = boto3.Session().client("s3")
        s3_client.create_bucket(Bucket="test_bucket")
        s3_client.put_object(Bucket="test_bucket", Key="key", Body=json.dumps(data).encode("utf-8"))
        artifact_reader = S3ArtifactReader()
        read_data = artifact_reader.read_artifact("s3://test_bucket/key")
        self.assertDictEqual(data, read_data)


class TestParseS3URI(unittest.TestCase):
    def test_invalid_uri(self):
        uri = "bucket/key"
        with self.assertRaises(InvalidS3URIException):
            parse_s3_uri(uri)

    def test_valid_simple_key(self):
        uri = "s3://bucket/key"
        bucket, key = parse_s3_uri(uri)
        self.assertEqual(bucket, "bucket")
        self.assertEqual(key, "key")

    def test_valid_long_key(self):
        uri = "s3://bucket/key/foo/boo/goo"
        bucket, key = parse_s3_uri(uri)
        self.assertEqual(bucket, "bucket")
        self.assertEqual(key, "key/foo/boo/goo")

    def test_without_bucket(self):
        uri = "s3:///key/path"
        with self.assertRaises(InvalidS3URIException):
            parse_s3_uri(uri)

    def test_without_key(self):
        uri = "s3://bucket/"
        with self.assertRaises(InvalidS3URIException):
            parse_s3_uri(uri)

    def test_bad_key(self):
        uri = "s3://bucket/key//goo"
        with self.assertRaises(InvalidS3URIException):
            parse_s3_uri(uri)
