import io
import logging
import os
import time
import hashlib
import math
import re
from typing import Optional, Union
from datetime import timedelta
from pathlib import Path
import urllib3

from minio import Minio
from minio.error import S3Error
from minio.helpers import ObjectWriteResult
from minio.commonconfig import Tags, CopySource, COPY
from minio.deleteobjects import DeleteObject
from tqdm import tqdm


class EtagVerificationError(Exception):
    pass

class NumberOfPartEtagError(Exception):
    pass


class MinioS3:
    """Provides functionality for interacting with Minio S3"""

    def __init__(
        self,
        domain: str,
        access_key: str,
        secret_key: str,
        is_secure: bool,
        http_client: Optional[urllib3.PoolManager] = None,
    ):

        # Instantiate Minio client instance
        self.client = Minio(domain, access_key=access_key, secret_key=secret_key, secure=is_secure,
                            http_client=http_client)
        self.multipart_size_dict = {}

    @staticmethod
    def __check_etag_format__(etag, multipart=True):
        if multipart:
            match = re.match(r'^[a-fA-F0-9]{32}(-\d+)$', etag)
            assert match and int(match.group(1).strip("-")) > 1, f"Invalid multipart ETAG '{etag}'"
        else:
            assert re.match(r'^[a-fA-F0-9]{32}$', etag), f"Invalid ETAG '{etag}'"

    @staticmethod
    def get_working_part_sizes(
            file_size: int,
            number_of_parts: int,
            factor: int = 1024 * 1024) -> list[int]:
        # returns the closest factor of 1024 * 1024 (default)
        # e.g, 5767168 => 5 * 1024 * 1024; 7203757 => 7 * 1024 * 1024
        assert number_of_parts > 1, "number_of_parts must be greater than 1"
        assert file_size >= factor, "file size must be greater or equal than the factor (default is 1024 * 1024)"

        exact_part_size = file_size // number_of_parts
        raw_multiplier = exact_part_size / factor
        multiplier = math.ceil(raw_multiplier)
        if multiplier < 5:
            # 5 * 1024 * 1024, is the minimum multipart size allowd by the lib
            multiplier = 5
        multipart_size = multiplier * factor
        part_count = file_size / multipart_size
        if math.ceil(part_count) != number_of_parts:
            raise NumberOfPartEtagError(f"Incorrect number of parts for file size {file_size}. "
                                        f"{number_of_parts} parts provided but the closest factor is "
                                        f"{multiplier} * {factor}, leading to {math.ceil(part_count)} parts")
        working_part_sizes = []
        for i in range(10):
            i += multiplier
            multipart_size = i * factor
            new_part_count = file_size / multipart_size
            if math.ceil(new_part_count) != number_of_parts:
                break
            working_part_sizes.append(multipart_size)

        return working_part_sizes

    def reset_memorized_part_size(self, bucket_name: str = None):
        if bucket_name and bucket_name in self.multipart_size_dict:
            del self.multipart_size_dict[bucket_name]
        else:
            self.multipart_size_dict = {}

    @staticmethod
    def compute_etag(file_path_or_iobase: Union[str, Path, io.IOBase],
                     multipart_size: int = 0,
                     quiet: bool = False) -> str:

        """
        Compute the MD5 checksum (assuming that the S3 server uses the same hashing algorithm
        for computing ETAG) for a local file.

        :param file_path_or_iobase: The path to the file or io.IOBase
                                    (opened file stream, io.Bytes etc...)
        :param multipart_size: compute the MD5sum the same way the S3 bucket computes it
                               for multipart-uploaded files
        :param quiet: Turn logging off if True
        :return: The MD5 checksum as a hex string
        """

        if isinstance(file_path_or_iobase, str) or isinstance(file_path_or_iobase, Path):
            # assuming it's a file
            assert os.path.isfile(file_path_or_iobase)
            if not quiet:
                logging.info(f"Computing MD5 checksum for file: {file_path_or_iobase}")
            file_path_or_iobase = open(file_path_or_iobase, "rb")

        if multipart_size:
            md5s = []
            while True:
                data = file_path_or_iobase.read(multipart_size)
                if not data:
                    break
                md5s.append(hashlib.md5(data).digest())
            if len(md5s) <= 1:
                # the file size was smaller that the part size...
                # recompute the md5 hexdigest of the whole content...
                file_path_or_iobase.seek(0)
                return hashlib.md5(file_path_or_iobase.read()).hexdigest()

            hash_md5 = f"{hashlib.md5(b''.join(md5s)).hexdigest()}-{len(md5s)}"
        else:
            hash_md5 = hashlib.md5()
            for chunk in iter(lambda: file_path_or_iobase.read(8192), b""):
                hash_md5.update(chunk)
            hash_md5 = hash_md5.hexdigest()

        if not isinstance(file_path_or_iobase, str) and not isinstance(file_path_or_iobase, Path):
            # go to the beginning of the stream, to read it again during copy to the bucket
            file_path_or_iobase.seek(0)

        return hash_md5


    @staticmethod
    def _validate_str_dict_(tag_dict: dict) -> None:
        """
        Validate that the keys and values of the tag_dict are of type str.
        :param tag_dict: A dictionary of tags
        :return: None
        """
        assert isinstance(tag_dict, dict), "tag_dict is not of type dict"
        for k, v in tag_dict.items():
            assert isinstance(k, str), f'tag_dict key "{k}" is not of type str'
            assert isinstance(v, str), f'tag_dict value "{v}" (key "{k}") is not of type str'
            # trailing or leading space characters are trimmed off by the minio lib,
            # and cause SignatureDoesNotMatch error
            if k != k.strip():
                assert k.strip() not in tag_dict, (
                    f'tag_dict key "{k}" contains a leading or trailing space character'
                    f" The spacing character(s) cannot be trimmed, the trimmed key"
                    f" already exist)"
                )
            assert (
                k == k.strip()
            ), f'tag_dict key "{k}" contains a leading or trailing space character'
            assert (
                v == v.strip()
            ), f'tag_dict value "{k}" contains a leading or trailing space character'

    @staticmethod
    def _convert_to_tags(tag_dict: dict) -> Tags:
        """
        Convert a dictionary of tags to a Tags object.
        :param tag_dict: A dictionary of tags
        :return: A Tags object
        """
        assert tag_dict, "Invalid tag_dict, it must be non-empty dict"
        MinioS3._validate_str_dict_(tag_dict)
        new_tag_dict = Tags(for_object=True)
        new_tag_dict.update(tag_dict)
        return new_tag_dict

    def list_objects(self,
                     bucket_name: str,
                     prefix: Optional[str] = None,
                     recursive: bool = False,
                     include_version: bool = False) -> iter:
        """
        List objects and their metadata and tags. Filter using prefix.
        :param bucket_name: The name of the bucket
        :param prefix: The prefix to filter objects.
                       None or empty string means all files in the bucket
        :param recursive: If True, list objects recursively
        :param include_version: Flag to control whether include object
                                versions.
        :return: An iterator of objects
        """
        logging.info(f'Listing objects from bucket "{bucket_name}" (using prefix "{prefix}")...')
        gen_objects = self.client.list_objects(
            bucket_name, prefix=prefix, recursive=recursive, include_user_meta=True,
            include_version=include_version
        )
        logging.info("Success")
        return gen_objects

    def get_object(
            self,
            bucket_name: str,
            object_name: str,
            version_id: Optional[str] = None,
            quiet: bool = False
    ) -> bytes:
        """
        Get object_name from bucket bucket_name. Return the data (HTTPResponse.data bytes).
        Raise minio.error.S3Error is the object does not exist.
        :param bucket_name: The name of the bucket
        :param object_name: The name of the object
        :param version_id: The version ID of the object to get, or None to get the last version
        :param quiet: Turn logging off if True
        :return: The data of the object
        """
        if not quiet:
            logging.info(f'Getting "{object_name}" from bucket "{bucket_name}"...')
        response = self.client.get_object(bucket_name, object_name, version_id=version_id)
        return response.data

    def download_file(
            self,
            bucket_name: str,
            object_name: str,
            output_file: Path,
            version_id: Optional[str] = None,
            tmp_file_path: Optional[str] = None,
            overwrite: bool = False,
            skip_etag_verification: bool = False,
            multipart_size: Optional[int] = None,
            smart_multipart_size: bool = False,
            quiet: bool = False
    ) -> bool:
        """
        Fetch object_name and write it to output_file. Return True if the file was downloaded,
        False otherwise.

        The ETAG of the downloaded object is recalculated and compared against the
        ETAG on the bucket. This only works with MD% algorithm. If another algorithm is implemented
         on the bucket side, this verification can be skipped with the skip_etag_verification option.


        :param bucket_name: The name of the bucket
        :param object_name: The name of the object
        :param output_file: The path to the output file
        :param version_id: The version ID of the object to get, or None to get the last version
        :param tmp_file_path: Path to a temporary file
        :param overwrite: If True, overwrite the file if it already exists
        :param skip_etag_verification: Skip ETAG verification
        :param multipart_size: The multipart size needed to recompute the local ETAG, If None, this
                               value is estimated.
        :param smart_multipart_size: Try multiple possible multipart_sizes to validate the ETAG.
                                     The working multipart_size is reused for future download
                                     in the bucket. Only works when the multipart size is estimated
                                     (i.e., multipart_size is None)
        :param quiet: Turn logging off if True
        :return: True if the file was downloaded, False otherwise
        """

        if not overwrite and os.path.isfile(output_file):
            if not quiet:
                logging.info(f'Target file "{output_file}" already exist. Not downloaded')
            return False
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        if not quiet:
            logging.info(f'Getting "{object_name}" from bucket "{bucket_name}...')

        stat = self.client.fget_object(
            bucket_name,
            object_name,
            output_file,
            version_id=version_id,
            tmp_file_path=tmp_file_path
        )

        if not skip_etag_verification:
            # check if the etag is valid, skip the etag verification with a warning if not
            try:
                self.__check_etag_format__(stat.etag, multipart="-" in stat.etag)
            except AssertionError:
                logging.warning(
                    f'Cannot perform ETAG verification. The ETAG returned from the bucket'
                    f' does not look like MD5 hash"'
                )
            else:
                if "-" in stat.etag:
                    if multipart_size:
                        part_sizes = [multipart_size]
                    else:
                        try:
                            part_sizes = self.get_working_part_sizes(
                                stat.size,
                                int(stat.etag.split("-")[1])
                            )
                            if not smart_multipart_size:
                                part_sizes = part_sizes[:1]
                            else:
                                if len(part_sizes) > 1 and bucket_name in self.multipart_size_dict:
                                    part_sizes = [self.multipart_size_dict[bucket_name]]
                        except NumberOfPartEtagError:
                            # should not be possible,
                            # let's return a legit value
                            part_sizes = [5 * 1024 * 1024]
                else:
                    part_sizes = [0]

                for ps in part_sizes:
                    local_etag = self.compute_etag(output_file, ps)
                    if stat.etag == local_etag:
                        if smart_multipart_size:
                            self.multipart_size_dict[bucket_name] = ps
                        break
                else:
                    os.unlink(output_file)
                    raise EtagVerificationError(
                        f"The remote ETAG '{stat.etag}' != local ETAG '{local_etag}'"
                        f" (remote size: {stat.size}, multipart_size(s) used: {part_sizes})")

        if not quiet:
            logging.info(
                f'File "{object_name}" ("{output_file}") has been successfully'
                f' downloaded from bucket "{bucket_name}"'
            )
        return True

    def download_files(
        self,
        bucket_name: str,
        prefix: str,
        output_dir: Path,
        overwrite: bool = False,
        ignore_contains: list = None,
        skip_etag_verification: bool = False,
        multipart_size: Optional[int] = None,
        smart_multipart_size: bool = False,
        progress_bar: bool = True,
        log_each_file: bool = False
    ) -> int:
        """
        Fetch object_name starting with prefix, and write it to output_dir.
        :param bucket_name: The name of the bucket
        :param prefix: Look up for objects starting with PREFIX
        :param output_dir: The path to the output directory
        :param overwrite: If True, overwrite the file if it already exists
        :param ignore_contains: List of strings to filter out objects if one of them if found in
                                the object name
        :param skip_etag_verification: Skip ETAG verification
        :param multipart_size: The multipart size needed to recompute the local ETAG. If None, this
                               value is estimated.
        :param smart_multipart_size: Try multiple possible multipart_sizes to validate the ETAG.
                                     The working multipart_size is reused for future download
                                     in the bucket. Only works when the multipart size is estimated
                                     (i.e., multipart_size is None)
        :param progress_bar: Display a progress bar in stderr if True
        :param log_each_file: Log each file downloaded
        :return: The number of files downloaded
        """
        count = 0
        objects = [
            obj.object_name
            for obj in self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            if not (
                obj.object_name.endswith("/")
                or (ignore_contains and [p for p in ignore_contains if p in obj.object_name])
            )
        ]

        for obj_name in tqdm(objects, disable=not progress_bar):
            rel_obj_name = os.path.relpath(obj_name, prefix)
            success = self.download_file(
                bucket_name,
                obj_name,
                Path(os.path.join(output_dir, rel_obj_name)),
                overwrite=overwrite,
                skip_etag_verification=skip_etag_verification,
                multipart_size=multipart_size,
                smart_multipart_size=smart_multipart_size,
                quiet=not log_each_file
            )
            if success:
                count += 1
        logging.info(
            f'{count} file(s) with "{prefix}" have been successfully'
            f' downloaded from bucket "{bucket_name}"'
        )
        return count

    def put_object(
        self,
        bucket_name: str,
        object_name: str,
        data: io.IOBase,
        content_type: str = "application/octet-stream",
        length: int = -1,  # Data size; -1 for unknown size and set valid part_size.
        metadata_dict: dict = None,
        tag_dict: dict = None,
        multipart_size: int = 10 * 1024 * 1024,
        skip_exist: bool = True,
        skip_etag_verification: bool = False,
        max_retries: int = 1,
        quiet: bool = False
    ) -> Optional[ObjectWriteResult]:
        """
        Put an object in bucket. Set skip_exist to True to avoid
        copying the object if already in the bucket.
        Return ObjectWriteResult (includes the version_id) if save else returns None.
        :param bucket_name: The name of the bucket
        :param object_name: The name of the object
        :param data: The data to write
        :param content_type: The content type of the object
        :param length: The length of the object
        :param metadata_dict: The metadata of the object
        :param tag_dict: The tags of the object
        :param multipart_size: Multipart part size
        :param skip_exist: If True, skip copying the object if it already exists
        :param skip_etag_verification: skip computing MD5 of local file and the comparison with ETAG.
                                       Skipping this validation is not recommended.
        :param max_retries: number of retries if a S3Error or EtagVerificationError is raised.
                            '1' means one additional try (after 10 secondes)
        :param quiet: Turn logging off if True
        :return: ObjectWriteResult object if saved else None
        """
        assert not self.path_exist(bucket_name, object_name), \
            ("Error: cannot put object name corresponding to an existing path."
             " The path must be first explicitly deleted.")

        if skip_exist and self.object_exist(bucket_name, object_name):
            if not quiet:
                logging.info(
                    f'Skip putting "{object_name}" to bucket "{bucket_name}", object already exists'
                )
            return

        if metadata_dict:
            MinioS3._validate_str_dict_(metadata_dict)
        if tag_dict:
            tag_dict = MinioS3._convert_to_tags(tag_dict)

        if not quiet:
            logging.info(f'Putting "{object_name}" to bucket "{bucket_name}"...')

        if max_retries < 0:
            max_retries = 0
        for i in range(0+max_retries, -1, -1):
            try:
                # Store the part size that will be used for ETag verification
                result = self.client.put_object(
                    bucket_name,
                    object_name,
                    data,
                    length,
                    content_type=content_type,
                    metadata=metadata_dict,
                    tags=tag_dict,
                    part_size=multipart_size,
                )

                if not skip_etag_verification:
                    # compute local hash, and compare with hash calculated on the server.
                    data.seek(0)
                    local_etag = self.compute_etag(data, multipart_size=multipart_size)
                    if local_etag != result.etag:
                        # the file is copy but the content is diff from the source file
                        size = self.stat_object(bucket_name, object_name).size
                        raise EtagVerificationError(f"The remote ETAG '{result.etag}' != local ETAG '{local_etag}'"
                                                    f" (remote size: {size}, multipart_size: {multipart_size})")

                break
            except (S3Error, EtagVerificationError) as e:
                logging.info(f'Fail with error: "{e}"')
                if self.object_exist(bucket_name, object_name):
                    self.client.remove_object(bucket_name, object_name)
                    logging.info("Object deleted..")
                if i == 0:
                    raise e
                logging.info(f"Retrying in 10 second (#{max_retries - i})")
                time.sleep(10)

        if not quiet:
            logging.info("Success")
        return result

    def put_objects(
        self,
        bucket_name: str,
        file_list: list,
        multipart_size: int = 10 * 1024 * 1024,
        skip_exist: bool = True,
        progress_bar: bool = True,
        skip_etag_verification: bool = False,
        max_retries: int = 1,
        quiet: bool = False,
        log_each_file: bool = False
    ) -> list[ObjectWriteResult]:
        """
        Put a list of files as objects in storage.

        Set skip_exist to True to avoid copying object_name already in the bucket.
        The list of files must have the following structure:
        [
          [
            file_path: Path or str
            obj_name: destination on the bucket
            content_type: if None is set to 'application/octet-stream'
            length: number of bytes to write
            metadata_dict: metadata to include with the object
            tag_dict: tags to add to the object
          ]
        ]
        Return the list of ObjectWriteResult added to the bucket.
        :param bucket_name: The name of the bucket
        :param file_list: The list of files to put
        :param multipart_size: Multipart part size
        :param skip_exist: If True, skip copying the object if it already exists
        :param progress_bar: Displays a progress bar in stderr if True
        :param skip_etag_verification: Skip etag (MD5 hash) verification
        :param max_retries: number of retries for each file if a S3Error or EtagVerificationError is raised.
                            '1' means one additional try per file
        :param quiet: Turns logging off if True
        :param log_each_file: Logs each file uploaded, should not be used with param progress_bar
        :return: The list of ObjectWriteResult added to the bucket
        """
        saved_files = []
        assert isinstance(file_list, list), "Invalid file_list, it is not a list"
        for file_path, obj_name, content_type, length, metadata_dict, tag_dict in tqdm(
                file_list, disable=not progress_bar
        ):
            result = self.put_object(
                bucket_name,
                obj_name,
                open(file_path, "rb"),
                content_type=content_type,
                length=length,
                metadata_dict=metadata_dict,
                tag_dict=tag_dict,
                multipart_size=multipart_size,
                skip_etag_verification=skip_etag_verification,
                skip_exist=skip_exist,
                max_retries=max_retries,
                quiet=quiet or not log_each_file
            )
            if result:
                saved_files.append(result)
        if not quiet:
            logging.info(f'{len(saved_files)} file(s) uploaded to bucket "{bucket_name}"')
        return saved_files

    def put_folder(
        self,
        bucket_name: str,
        source_folder: str,
        destination: str,
        multipart_size: int = 10 * 1024 * 1024,
        skip_exist: bool = False,
        progress_bar: bool = True,
        skip_etag_verification: bool = False,
        max_retries: int = 1,
        quiet: bool = False,
        log_each_file: bool = False
    ) -> list[ObjectWriteResult]:
        """
        Put all folders/files from the source_folder in bucket destination (prefix).
        The source_folder itself is not copy to the bucket, its name won't be part
        of the object names

        Set skip_exist to True to avoid copying object_name already in the bucket.
        Return the list of ObjectWriteResult added to the bucket.

        :param bucket_name: The name of the bucket
        :param source_folder: The source folder to copy
        :param destination: The destination on the bucket
        :param multipart_size: Multipart part size
        :param skip_exist: If True, skip copying the object if it already exists
        :param progress_bar: Display a progress bar in stderr if True
        :param skip_etag_verification: Skip etag (MD5 hash) verification
        :param max_retries: number of retries for each file if a S3Error or EtagVerificationError is raised.
                            '1' means one additional try per file
        :param quiet: Turn logging off if True
        :param log_each_file: Log each file uploaded
        :return: The list of ObjectWriteResult added to the bucket
        """
        assert os.path.isdir(source_folder), (
            f'cannot send objects to bucket, source_folder "{source_folder}"' f" is not a directory"
        )
        assert len(os.listdir(source_folder)) != 0, (
            f'cannot send objects to bucket, source_folder "{source_folder}"' f" is empty"
        )
        assert destination.endswith("/"), 'Destination must end with "/"'
        files_to_send = []
        for root, folders, files in os.walk(source_folder):
            for name in files:
                file_path = os.path.join(root, name)
                rel_path = os.path.relpath(file_path, source_folder)
                files_to_send.append(
                    [file_path, os.path.join(destination, rel_path), None, -1, None, None]
                )

        return self.put_objects(
            bucket_name,
            files_to_send,
            multipart_size=multipart_size,
            skip_exist=skip_exist,
            progress_bar=progress_bar,
            skip_etag_verification=skip_etag_verification,
            max_retries=max_retries,
            quiet=quiet,
            log_each_file=log_each_file
        )

    def copy_object(
            self,
            source_bucket_name: str,
            source_object_name: str,
            destination_bucket_name: str,
            destination_object_name: str,
            quiet: bool = False
    ) -> ObjectWriteResult:
        """
        Copy an object from source bucket to destination bucket or within the same bucket.
        Metadata (added at object creation) and Tags are copied to the destination object.
        The names cannot be identical if the copy is performed in the same bucket.
        The object will be overwritten if it exists in the destination bucket.
        An error is raised if the destination_object_name is an existing path/prefix.
        :param source_bucket_name: The name of the source bucket
        :param source_object_name: The name of the source object
        :param destination_bucket_name: The name of the destination bucket
        :param destination_object_name: The name of the destination object
        :param quiet: Turns logging off if True
        :return The ObjectWriteResult copied
        """
        if source_bucket_name == destination_bucket_name:
            assert source_object_name != destination_object_name, \
                ("Error: destination_object_name cannot be identical to source_object_name"
                 " during copy within the same bucket")

        assert not self.path_exist(destination_bucket_name, destination_object_name), \
            ("Error: destination_object_name is an existing path."
             " The path must be first explicitly deleted.")

        if not quiet:
            logging.info(f"Copying object {source_object_name} from bucket {source_bucket_name} "
                         f"to bucket {destination_bucket_name} as {destination_object_name}...")
        stat = self.stat_object(source_bucket_name, source_object_name)
        # copy only if the source object matches the etag/md5sum
        copy_source = CopySource(source_bucket_name, source_object_name, match_etag=stat.etag)

        FIVE_GIB = 5 * 1024 * 1024 * 1024
        if stat.size > FIVE_GIB:
            # For large objects, fetch and pass metadata explicitly (REPLACE)
            metadata = getattr(stat, "metadata", None)
            result = self.client.copy_object(
                destination_bucket_name,
                destination_object_name,
                copy_source,
                metadata=metadata,
                metadata_directive="REPLACE"
            )
        else:
            # For small objects, use COPY directive
            result = self.client.copy_object(
                destination_bucket_name,
                destination_object_name,
                copy_source,
                metadata_directive="COPY"
            )

        # Skip ETag check for multipart objects or large objects
        if "-" in stat.etag or stat.size > FIVE_GIB:
            if not quiet:
                logging.warning(
                    f"Skipped ETag check for multipart or large object '{source_object_name}' "
                    f"(size: {stat.size}, source ETAG: {stat.etag}, dest ETAG: {result.etag})"
                )
        elif stat.etag != result.etag:
            # Only compare ETags for single-part, small objects
            self.client.remove_object(destination_bucket_name, destination_object_name)
            raise EtagVerificationError(f"The source ETAG '{stat.etag}' != destination ETAG {result.etag}"
                                        f" for object '{source_object_name}. "
                                        f"Destination object has been deleted.'")

        if not quiet:
            logging.info("Copy completed")
        return result

    def copy_objects(
            self,
            source_bucket_name: str,
            source_objects_prefix: Optional[str],
            destination_bucket_name: str,
            destination_objects_prefix: str,
            quiet: bool = False
    ) -> list[ObjectWriteResult]:
        """
        Copy objects starting by source_objects_prefix in source bucket to destination bucket
        or from one prefix to another in the same bucket.
        If the copy is performed in the same bucket, the source_objects_prefix cannot be a prefix
        the destination_objects_prefix e.g. copy "a" to "a/a/".
        An error is raised if one destination_object_name is an existing path/namespace.

        A copy can lead to data loss by overwriting existing files accidentally
        Or can lead to incomplete copy, exemple:
            "aaa", "b/file" et "a/b" in bucket
        with source_objects_prefix = "a" and destination_objects_prefix = "":
            first "aaa" is copied into aa, then a/b lead to b which raises the exception

         The user has the responsibility for verifying colliding names before starting the copy.
        :param source_bucket_name: The name of the source bucket
        :param source_objects_prefix: The prefix of the source objects to copy.
                                      None or empty string means copy all files in the bucket
        :param destination_bucket_name: The name of the destination bucket
        :param destination_objects_prefix: The prefix of the destination objects destination.
                                           Use an empty string to copy objects at the root of the
                                           destination bucket
        :param quiet: Turn logging off if True
        :return The list of ObjectWriteResult copied
        """
        if destination_objects_prefix is None:
            raise TypeError("Invalid type, destination_objects_prefix must be a string")

        if source_bucket_name == destination_bucket_name and source_objects_prefix:
            assert not destination_objects_prefix.startswith(source_objects_prefix), \
                "Error: destination_objects_prefix contains the source_objects_prefix"

        if not quiet:
            logging.info(f"Copying objects with prefix '{source_objects_prefix}' from bucket {source_bucket_name} "
                         f"to bucket {destination_bucket_name} with prefix '{destination_objects_prefix}'..")

        copy_files = []
        for obj in self.client.list_objects(
            source_bucket_name,
            source_objects_prefix,
            recursive=True
        ):
            if source_objects_prefix:
                dest_object_prefix = (destination_objects_prefix +
                                      obj.object_name.split(source_objects_prefix, 1)[1].strip("/"))
            else:
                dest_object_prefix = destination_objects_prefix + obj.object_name

            result = self.copy_object(
                source_bucket_name,
                obj.object_name,
                destination_bucket_name,
                dest_object_prefix,
                quiet=True
            )
            copy_files.append(result)
        if not quiet:
            logging.info("All objects have been copied")

        return copy_files

    def move_object(
            self,
            source_bucket_name: str,
            source_object_name: str,
            destination_bucket_name: str,
            destination_object_name: str,
            quiet: bool = False
    ) -> ObjectWriteResult:
        """
        Move an object from the source bucket to the destination bucket or from one directory to another in the same bucket.
        The object is copied first (with metadata and Tags) and then deleted from the source.
        The names cannot be identical if the move is performed in the same bucket.
        The object will be overwritten if it exists in the destination bucket.
        An error is raised if the destination_object_name is an existing path/namespace.
        :param source_bucket_name: The name of the source bucket
        :param source_object_name: The name of the source object
        :param destination_bucket_name: The name of the destination bucket
        :param destination_object_name: The name of the destination object
        :param quiet: Turns logging off if True
        :return The ObjectWriteResult of the object moved
        """

        if source_bucket_name == destination_bucket_name:
            assert source_object_name != destination_object_name, \
                ("Error: destination_object_name cannot be identical to source_object_name "
                 "during move within the same bucket")

        if not quiet:
            logging.info(f"Moving object {source_object_name} from bucket {source_bucket_name}"
                         f" to bucket {destination_bucket_name} (new name: {destination_object_name})")

        result = self.copy_object(
            source_bucket_name,
            source_object_name,
            destination_bucket_name,
            destination_object_name,
            quiet=quiet
        )
        assert result.object_name
        # After successfully copying, delete the original object from the source bucket
        self.delete_object(source_bucket_name, source_object_name)
        if not quiet:
            logging.info("Move completed")
        return result

    def move_objects(
            self,
            source_bucket_name: str,
            source_objects_prefix: Optional[str],
            destination_bucket_name: str,
            destination_objects_prefix: str,
            quiet: bool = False
    ) -> list[ObjectWriteResult]:
        """
        Move objects from the source bucket to the destination bucket or from one directory/prefix to another in the same bucket.
        The objects are copied first and then deleted from the source.
        The user has the responsibility for verifying colliding names before starting the move.
        :param source_bucket_name: The name of the source bucket
        :param source_objects_prefix: The prefix of the source objects to copy.
                                      None or empty string means move all files in the bucket
        :param destination_bucket_name: The name of the destination bucket
        :param destination_objects_prefix: The prefix of the destination objects destination.
                                           Use an empty string to move objects at the root of the
                                           destination bucket
        :param quiet: Turns logging off if True
        :return The list of ObjectWriteResult of the objects moved
        """
        if source_bucket_name == destination_bucket_name:
            assert not destination_bucket_name.startswith(source_objects_prefix), \
                "Error: destination_objects_prefix contains the source_objects_prefix"

        result_copy = self.copy_objects(
            source_bucket_name,
            source_objects_prefix,
            destination_bucket_name,
            destination_objects_prefix,
            quiet=quiet
        )

        # After successfully copying, delete the original object from the source bucket
        if result_copy:  # TODO remove if?
            assert self.delete_objects(
                source_bucket_name,
                source_objects_prefix,
                delete_prefix=True
            ) is True, "Error: during deletion of source objects moved"

        if not quiet:
            logging.info("All objects have been moved")
        return result_copy

    def delete_object(self, bucket_name: str, object_name: str, version_id: str = None) -> None:
        """
        Delete object_name from bucket_name.
        Use version_id to delete a specific version on the object.
        :param bucket_name: The name of the bucket to delete from
        :param object_name: The name of the object to delete
        :param version_id: The version ID on the object to delete. The object is deleted permanently
                           when the version ID is specified.
        :return:
        """
        logging.info(f'Removing "{object_name}" from bucket "{bucket_name}"...')
        self.client.remove_object(bucket_name, object_name, version_id=version_id)
        logging.info("Object deleted")

    def delete_objects(self, bucket_name: str,
                       objects_path: Optional[str],
                       delete_prefix: bool = False,
                       permanent_deletion: bool = False) -> bool:
        """
        Delete objects starting with path/namespace objects_path from bucket_name.
        If delete_prefix is True, all objects starting with objects_path (as prefix) are deleted.
        E.g., With a bucket containing two objects "a/f1" and "aa/f2"
            using objects_path = "a", only f1 is deleted
            with delete_prefix set to True, both files are deleted.
        :param bucket_name: The name of the bucket to delete from
        :param objects_path: The path/namespace of the objects to delete.
                             If an empty string or None is provided, everything is deleted.
        :param delete_prefix: Delete all files starting with "<objects_path>", instead of all files
                              starting with "<objects_path>/"
        :param permanent_deletion: Delete the all versions of each object, meaning the objects
                                   are permanently deleted. Delete markers are also deleted.
        :return True if all objects are deleted without errors, False otherwise
        """

        if not objects_path:
            objects_path = None
        else:
            if not delete_prefix:
                assert self.path_exist(bucket_name, objects_path), \
                    "Error: objects_path is not an existing path."
                objects_path = objects_path.rstrip("/") + "/"  # add "/" for safety

        if not delete_prefix:
            logging.info(
                f'Removing objects in path "{objects_path}" from bucket "{bucket_name}"...')
        else:
            logging.info(
                f'Removing objects prefixed "{objects_path}" from bucket "{bucket_name}"...')
        # Remove a prefix recursively.
        delete_object_list = map(
            lambda x: DeleteObject(x.object_name, x.version_id)
            if permanent_deletion else DeleteObject(x.object_name),
            self.client.list_objects(bucket_name, objects_path, recursive=True,
                                     include_version=permanent_deletion),
        )

        errors = [e for e in self.client.remove_objects(bucket_name, delete_object_list)]
        for error in errors:
            logging.error("error occurred when deleting object: %s" % error)

        if not errors:
            logging.info("All Objects have been deleted")
            return True
        return False

    def stat_object(self, bucket_name: str, object_name: str,
                    version_id: Optional[str] = None) -> object:
        """
        Get some metadata information on the designed object_name in bucket_name.
        Raise an error if the bucket or the object does not exist.
        :param bucket_name: The name of the bucket
        :param object_name: The name of the object
        :param version_id: Version ID of the object, or None for the last version
        :return Object(
            bucket_name,
            object_name,
            last_modified
            etag # md5sum hash
            size # content-length
            content_type
            metadata
            version_id # response.headers.get("x-amz-version-id")
        ).
        """
        logging.info(f'Stat object "{bucket_name}" from bucket "{object_name}"...')
        obj = self.client.stat_object(bucket_name, object_name, version_id)
        return obj

    def get_object_tags(self, bucket_name: str, object_name: str) -> dict:
        """
        Get tags for object_name in bucket_name.
        :param bucket_name: The name of the bucket
        :param object_name: The name of the object
        :return: A dictionary of tags
        """
        return self.client.get_object_tags(bucket_name, object_name)

    def set_object_tags(self, bucket_name: str, object_name: str, tag_dict: dict[str, str]) -> None:
        """
        Set tags (tag_dict) to existing object_name in bucket_name.
        :param bucket_name: The name of the bucket
        :param object_name: The name of the object
        :param tag_dict: The dictionary of tags to set
        :return: None
        """
        tags = self._convert_to_tags(tag_dict)
        self.client.set_object_tags(bucket_name, object_name, tags)

    def delete_object_tags(self, bucket_name: str, object_name: str) -> None:
        """
        Delete the tags assigned to the object_name in bucket_name.
        :param bucket_name: The name of the bucket
        :param object_name: The name of the object
        :return: None
        """
        self.client.delete_object_tags(bucket_name, object_name)

    def object_exist(self, bucket_name: str, object_name: str) -> bool:
        """
        Return True if object_name is in bucket bucket_name, False otherwise.
        Raise an error if the bucket does not exist.
        :param bucket_name: The name of the bucket
        :param object_name: The name of the object
        :return: True if object_name is in bucket bucket_name, False otherwise
        """
        try:
            self.get_object_tags(bucket_name, object_name)
        except S3Error as exc:
            if exc.code == "NoSuchTagSet":
                return True
            elif exc.code == "NoSuchKey":
                return False
            raise exc
        return True

    def path_exist(self, bucket_name: str, path: str) -> bool:

        """
        Return True if path is a path/namespace in bucket bucket_name, False otherwise.

        example: if the following object "aaaa/bbbb/cccc/file.txt" exist
            testing "aaaa/bbbb/cccc/" or "aaaa/bbbb/cccc" return True
            testing "aaaa/bbbb" or "aaaa" return True
            testing "aaaa/bbbb/cccc/file.txt" returns false (it's a object name not a path)
            testing "aaaa/bbbb/ccc returns false (incomplete path)

        Raise an error if the bucket does not exist.
        :param bucket_name: The name of the bucket
        :param path: The path to test existence
        :return: True if path is a path/namespace in bucket bucket_name, False otherwise
        """
        if path is None:
            raise TypeError("Invalid type, path must be a string")
        return path.rstrip("/") + "/" in [
            o.object_name for o in self.client.list_objects(
                                                    bucket_name,
                                                    path.rstrip("/"),
                                                    recursive=False
                                                )
        ]

    def get_presigned_url(
        self, bucket_name: str, object_name: str, expires: timedelta = timedelta(days=7)
    ) -> str:
        """
        Get presigned URL of an object to download its data with expiry time.
        :param bucket_name: The name of the bucket
        :param object_name: The name of the object
        :param expires: The expiry time of the URL, default is 7 days
        :return: The presigned URL
        """
        return self.client.get_presigned_url(
            "GET",
            bucket_name,
            object_name,
            expires=expires,
        )
