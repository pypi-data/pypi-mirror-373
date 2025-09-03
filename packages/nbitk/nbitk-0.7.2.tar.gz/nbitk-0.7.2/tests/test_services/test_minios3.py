import os
import io
import shutil
import time
from pathlib import Path
import pytest
import requests
import minio
from nbitk.Services.MinioS3 import MinioS3, EtagVerificationError, NumberOfPartEtagError
from testcontainers.minio import MinioContainer
from minio.commonconfig import ENABLED
from minio.versioningconfig import VersioningConfig

class TestClass:
    @pytest.fixture()
    def minioc(self):
        with MinioContainer() as minioc:
            client = minioc.get_client()
            client.make_bucket("test-bucket")
            client.make_bucket("test-bucket-copy")
            client.set_bucket_versioning(
                'test-bucket', VersioningConfig(ENABLED),
            )
            test_content = b"test_content"
            for f in ["testfile1.txt", "testfile2.txt", "test_folder/testfile3.txt", "test_folder/testfile4.txt"]:
                client.put_object(
                    "test-bucket",
                    f,
                    io.BytesIO(test_content),
                    length=len(test_content),
                )

            yield minioc

    @pytest.fixture()
    def client(self, minioc):
        return minioc.get_client()

    @pytest.fixture()
    def minio_conn(self, minioc):
        conf = minioc.get_config()
        return MinioS3(
            conf['endpoint'],
            conf['access_key'],
            conf['secret_key'],
            False,  # is_secure
        )

    def test_get_working_part_sizes(self, minio_conn):
        value = minio_conn.get_working_part_sizes(7835098795, 1495)
        assert value == [5 * 1024 * 1024]

        value = minio_conn.get_working_part_sizes(7835098795, 1246)
        assert value == [6 * 1024 * 1024]

        with pytest.raises(NumberOfPartEtagError):
            minio_conn.get_working_part_sizes(7835098795, 1494)

        with pytest.raises(NumberOfPartEtagError):
            minio_conn.get_working_part_sizes(7835098795, 1245)

        with pytest.raises(NumberOfPartEtagError):
            minio_conn.get_working_part_sizes(20 * 1024 * 1024, 21)

        value = minio_conn.get_working_part_sizes(11 * 1024 * 1024, 2)
        assert value == [6 * 1024 * 1024, 7 * 1024 * 1024, 8 * 1024 * 1024, 9 * 1024 * 1024, 10 * 1024 * 1024]

        value = minio_conn.get_working_part_sizes(11 * 1024 * 1024, 3)
        assert value == [5 * 1024 * 1024]  # minimum part size allowed by the lib

    @pytest.mark.parametrize(
        "prefix, recursive, expected_files", [
            ("", False, ['test_folder/', 'testfile1.txt', 'testfile2.txt']),
            (None, False, ['test_folder/', 'testfile1.txt', 'testfile2.txt']),
            ("not_exist", False, []),
            ("test_folder", False, ['test_folder/']),
            ("test_folder/", False, ['test_folder/testfile3.txt', 'test_folder/testfile4.txt']),
            ("", True, ['test_folder/testfile3.txt', 'test_folder/testfile4.txt',
                        'testfile1.txt', 'testfile2.txt']),
            ("test_folder", True, ['test_folder/testfile3.txt', 'test_folder/testfile4.txt']),
        ])
    def test_list_objects(self, minio_conn, prefix, recursive, expected_files):
        res = [obj for obj in minio_conn.list_objects(
            'test-bucket',
            prefix,
            recursive  # recursive off
        )]
        assert sorted([e.object_name for e in res]) == expected_files

    def test_list_objects_version(self, minio_conn):
        minio_conn.put_object(
            "test-bucket",
            "testfile1.txt",
            io.BytesIO(b''),
            length=0,
            skip_exist=False
        )

        res = [obj for obj in minio_conn.list_objects(
            'test-bucket',
            'testfile1.txt',
            include_version=True
        )][0]

        assert res.version_id not in [None, 'null']
        res = [obj for obj in minio_conn.list_objects(
            'test-bucket',
            'testfile1.txt',
            include_version=False
        )][0]
        assert res.version_id in [None, 'null']

    def test_get_object_content(self, minio_conn):
        data = minio_conn.get_object(
            'test-bucket',
            'test_folder/testfile3.txt',
        )
        assert data == b'test_content'

    def test_download_file(self, tmp_path, minio_conn):
        output_file = Path(f'{tmp_path}/local_testfile3.test')
        success = minio_conn.download_file(
            'test-bucket',
            'test_folder/testfile3.txt',
            output_file
        )

        with open(output_file) as fh:
            assert fh.readlines() == ['test_content']
        assert success

        # download it again, same destination but without option overwrite
        success = minio_conn.download_file(
            'test-bucket',
            'test_folder/testfile3.txt',
            output_file,
            overwrite=False
        )
        assert not success
        os.unlink(output_file)

        # download a file that does not exist
        with pytest.raises(minio.error.S3Error):
            res = minio_conn.download_file(
                'test-bucket',
                'not_exist',
                output_file
            )
            assert res is False
        assert not os.path.isfile(output_file)

    def test_download_file_etag_multipart(self, tmp_path, minio_conn):
        # put a large file
        object_to_put = 'test_folder/largefile.txt'
        minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b"00000000000" * 1024 * 1024),  # 11MB
            multipart_size=10 * 1024 * 1024  # 10MB
        )

        output_file = Path(f'{tmp_path}/local_largefile1.test')
        success = minio_conn.download_file(
            'test-bucket',
            'test_folder/largefile.txt',
            output_file,
            multipart_size=10 * 1024 * 1024
        )
        assert success

        with pytest.raises(Exception) as e:
            minio_conn.download_file(
                'test-bucket',
                'test_folder/largefile.txt',
                Path(f'{tmp_path}/local_largefile2.test'),
                multipart_size=8 * 1024 * 1024
            )
        msg = getattr(e, 'message', repr(e))
        assert '!= local ETAG' in msg

        minio_conn.download_file(
            'test-bucket',
            'test_folder/largefile.txt',
            Path(f'{tmp_path}/local_largefile2.test'),
            multipart_size=8 * 1024 * 1024,
            skip_etag_verification=True
        )

        # smart_multipart_size is ignored if multipart_size is specified
        with pytest.raises(Exception) as e:
            minio_conn.download_file(
                'test-bucket',
                'test_folder/largefile.txt',
                Path(f'{tmp_path}/local_largefile2.test'),
                overwrite=True,
                multipart_size=8 * 1024 * 1024,
                smart_multipart_size=True
            )
        msg = getattr(e, 'message', repr(e))
        assert '!= local ETAG' in msg

        with pytest.raises(Exception) as e:
            minio_conn.download_file(
                'test-bucket',
                'test_folder/largefile.txt',
                Path(f'{tmp_path}/local_largefile2.test'),
                overwrite=True,
                multipart_size=None,
            )
        msg = getattr(e, 'message', repr(e))
        assert '!= local ETAG' in msg

        minio_conn.download_file(
            'test-bucket',
            'test_folder/largefile.txt',
            Path(f'{tmp_path}/local_largefile2.test'),
            overwrite=True,
            multipart_size=None,
            smart_multipart_size=True
        )

    @pytest.mark.parametrize(
        "prefix, ignore_list, count, folder_files", [
            ("", [], 4, ['testfile1.txt', 'testfile2.txt', 'testfile3.txt', 'testfile4.txt']),
            (None, [], 4, ['testfile1.txt', 'testfile2.txt', 'testfile3.txt', 'testfile4.txt']),
            ("test_folder/", [], 2, ['testfile3.txt', 'testfile4.txt']),
            ("not_exist", [], 0, []),
            ("", ['test_folder'], 2, ['testfile1.txt', 'testfile2.txt']),
            ("", ['not_exist'], 4, ['testfile1.txt', 'testfile2.txt', 'testfile3.txt', 'testfile4.txt']),
            ("", ['testfile'], 0, []),
        ])
    def test_download_files(self, tmp_path, minio_conn, prefix, ignore_list, count, folder_files):
        output_folder = Path(f'{tmp_path}/local_test_dir')
        df_count = minio_conn.download_files(
            'test-bucket',
            prefix,
            output_folder,
            overwrite=False,
            ignore_contains=ignore_list,
            progress_bar=False
        )
        assert df_count == count
        if folder_files:
            dfiles = []
            for _, _, files in os.walk(output_folder):
                dfiles += files
            assert sorted(dfiles) == folder_files
            # test the content of the first file
            with open(os.path.join(output_folder, dfiles[0])) as fh:
                assert fh.readlines() == ['test_content']
        else:
            assert not os.path.isdir(output_folder)

    def test_download_files_overwrite(self, tmp_path, minio_conn):
        output_folder = Path(f'{tmp_path}/local_test_dir')
        df_count = minio_conn.download_files(
            'test-bucket',
            'test_folder/',
            output_folder,
        )
        assert df_count == 2
        os.unlink(os.path.join(output_folder, 'testfile3.txt'))

        df_count = minio_conn.download_files(
            'test-bucket',
            'test_folder/',
            output_folder,
        )
        assert df_count == 1

        df_count = minio_conn.download_files(
            'test-bucket',
            'test_folder/',
            output_folder,
            overwrite=True
        )
        assert df_count == 2

    def test_download_files_etag_multipart(self, tmp_path, minio_conn):
        output_folder = Path(f'{tmp_path}/local_test_dir')
        object_to_put = 'largefile1_6mb_ps.txt'
        etag_largefile1 = minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b"00000000000" * 1024 * 1024),  # 11MB
            multipart_size=6 * 1024 * 1024  # 6MB
        ).etag

        object_to_put = 'test/largefile2_7mb_ps.txt'
        minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b"000000000000000" * 1024 * 1024),  # 15MB
            multipart_size=7 * 1024 * 1024  # 7MB
        )

        object_to_put = 'test/largefile3_7mb_ps.txt'
        minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b"0000000000000000" * 1024 * 1024),  # 16MB
            multipart_size=7 * 1024 * 1024  # 7MB
        )

        df_count = minio_conn.download_files(
            'test-bucket',
            'largefile1',
            output_folder,
            overwrite=True
        )
        assert df_count == 1

        with pytest.raises(Exception) as e:
            minio_conn.download_files(
                'test-bucket',
                'test/largefile2',
                output_folder,
                overwrite=True,
            )
        # the algo will guess wrong: 5mb part size instead of 7 mb
        msg = getattr(e, 'message', repr(e))
        assert '!= local ETAG' in msg

        with pytest.raises(Exception) as e:
            minio_conn.download_files(
                'test-bucket',
                'test/largefile3',
                output_folder,
                overwrite=True,
            )
        # the algo will guess wrong: 6mb part size instead of 7 mb
        msg = getattr(e, 'message', repr(e))
        assert '!= local ETAG' in msg

        # skip ETAG verif = no more error raised
        minio_conn.download_files(
            'test-bucket',
            'test/largefile2',
            output_folder,
            overwrite=True,
            skip_etag_verification=True
        )

        # download one file, and by specify the correct multipart_size
        minio_conn.download_files(
            'test-bucket',
            'test/largefile2',
            output_folder,
            overwrite=True,
            multipart_size=7 * 1024 * 1024  # correct part size used
        )

        # download the same file that raised the ETAG error, but with smart_multipart_size
        # multiple multipart_size are tested
        minio_conn.download_files(
            'test-bucket',
            'test/largefile2',
            output_folder,
            overwrite=True,
            smart_multipart_size=True
        )

        with pytest.raises(Exception) as e:
            # download both files with a fix multipart_size, it fails for largefile1
            # multiple multipart_size are tested
            minio_conn.download_files(
                'test-bucket',
                '/',
                output_folder,
                overwrite=True,
                multipart_size=7 * 1024 * 1024
            )
        msg = getattr(e, 'message', repr(e))
        assert f'\'{etag_largefile1}\' != local ETAG' in msg

        minio_conn.download_files(
            'test-bucket',
            'test/',
            output_folder,
            overwrite=True,
            smart_multipart_size=True
        )

        # it won't work to download largefile1 anymore because
        # the arg smart_multipart_size used previously made it
        # memorized the value 7 * 1024 * 1024 as multipart_size for that bucket
        with pytest.raises(Exception) as e:
            minio_conn.download_files(
                'test-bucket',
                'largefile1',
                output_folder,
                overwrite=True,
                smart_multipart_size=True
            )
        msg = getattr(e, 'message', repr(e))
        assert f'\'{etag_largefile1}\' != local ETAG' in msg

        # let reset that value and retry, it should work
        minio_conn.reset_memorized_part_size("test-bucket")
        minio_conn.download_files(
            'test-bucket',
            'largefile1',
            output_folder,
            overwrite=True,
            smart_multipart_size=True
        )

        # downloading multiple files from a bucket with multiple part_size_used will always fail!
        # todo: option to remove the memory?

    def test_delete_object(self, minio_conn):
        # This test depends on a method tested test_list_objects
        minio_conn.delete_object(
            'test-bucket',
            'test_folder/testfile4.txt',
        )
        assert [o.object_name for o in minio_conn.list_objects(
            'test-bucket',
            "",
            recursive=True
        )] == ['test_folder/testfile3.txt', 'testfile1.txt', 'testfile2.txt']

        # test permanent deletion, using version_id
        for name, version_id in [[o.object_name, o.version_id] for o in minio_conn.list_objects(
                'test-bucket',
                "",
                recursive=True,
                include_version=True)]:
            if name == "test_folder/testfile3.txt":
                minio_conn.delete_object(
                    'test-bucket',
                    name,
                    version_id=version_id)
                break

        assert "test_folder/testfile3.txt" not in [o.object_name for o in minio_conn.list_objects(
                'test-bucket',
                "",
                recursive=True,
                include_version=True
            )]



    @pytest.mark.parametrize(
        "objects_prefix, expected_files, delete_prefix, assert_msg", [
            ("test_folder/", ['testfile1.txt', 'testfile2.txt'], False, None),
            ("test_folder", ['testfile1.txt', 'testfile2.txt'], False, None),
            ("test_folder/", ['testfile1.txt', 'testfile2.txt'], True, None),
            ("testfile1.txt", [], False, "objects_path is not an existing path"),
            ("testfile1.txt", ['test_folder/testfile3.txt', 'test_folder/testfile4.txt',
                               'testfile2.txt'], True, None),
            ("test", [], False, "objects_path is not an existing path"),
            ("test", [], True, None),  # everything deleted, all objects start with "test"
            (None, [], False, None),  # everything deleted
            ("", [], False, None),  # equivalent to None, everything deleted
            (" /", [], False, "objects_path is not an existing path")
    ])
    def test_delete_objects(self, minio_conn, objects_prefix, expected_files, delete_prefix,
                            assert_msg):
        # This test depends on a method tested test_list_objects
        if assert_msg:
            with pytest.raises(Exception) as e:
                minio_conn.delete_objects(
                    'test-bucket',
                    objects_prefix,
                    delete_prefix=delete_prefix
                )
            msg = getattr(e, 'message', repr(e))
            assert assert_msg in msg
        else:
            minio_conn.delete_objects(
                'test-bucket',
                objects_prefix,
                delete_prefix=delete_prefix
            )
            assert [o.object_name for o in minio_conn.list_objects(
                'test-bucket',
                "",
                recursive=True
            )] == expected_files

    def test_delete_objects_permanently(self, minio_conn):
        minio_conn.delete_objects(
            "test-bucket",
            "test_folder/",
            delete_prefix=False,
        )
        assert len(list(minio_conn.list_objects(
                'test-bucket',
                "",
                recursive=True,
                include_version=True))) == 6  # 4 initial objects + 2 delete markers

        minio_conn.delete_objects(
            "test-bucket",
            "test_folder/",
            delete_prefix=False,
            permanent_deletion=True
        )
        assert [o.object_name for o in minio_conn.list_objects(
                'test-bucket',
                "",
                recursive=True,
                include_version=True)
                ] == ['testfile1.txt', 'testfile2.txt']

    def test_stat_object(self, minio_conn):
        stats = minio_conn.stat_object(
            'test-bucket',
            'test_folder/testfile4.txt',
        )
        assert stats.object_name == 'test_folder/testfile4.txt'

    def test_object_tags(self, minio_conn):
        tags = {'key': 'value'}
        minio_conn.set_object_tags(
            'test-bucket',
            'testfile1.txt', tags
        )

        fetched_tags = minio_conn.get_object_tags(
            'test-bucket',
            'testfile1.txt'
        )
        assert fetched_tags == tags
        # note that stat.tags is always None!?

        minio_conn.delete_object_tags(
            'test-bucket',
            'testfile1.txt'
        )

        fetched_tags = minio_conn.get_object_tags(
            'test-bucket',
            'testfile1.txt'
        )
        assert fetched_tags is None

    def test_object_exist(self, minio_conn):
        assert minio_conn.object_exist('test-bucket', 'testfile1.txt') is True
        assert minio_conn.object_exist('test-bucket', 'not_exist.txt') is False
        with pytest.raises(minio.error.S3Error):
            minio_conn.object_exist('not_exist', 'testfile1.txt')

    def test_path_exist(self, minio_conn):
        assert minio_conn.path_exist('test-bucket', 'testfile1.txt') is False
        assert minio_conn.path_exist('test-bucket', 'test/folder') is False
        assert minio_conn.path_exist('test-bucket', 'test_folder/') is True
        assert minio_conn.path_exist('test-bucket', 'test_folder') is True
        assert minio_conn.path_exist('test-bucket', '/test_folder/') is False
        assert minio_conn.path_exist('test-bucket', '') is False
        with pytest.raises(TypeError):
            assert minio_conn.path_exist('test-bucket', None) is False
        with pytest.raises(minio.error.S3Error):
            minio_conn.path_exist('not_exist', 'test_folder')

    def test_get_presigned_url(self, tmp_path, minio_conn):
        url = minio_conn.get_presigned_url(
            'test-bucket',
            'testfile1.txt'
        )
        r = requests.get(url)
        dest_file = os.path.join(tmp_path, 'local_testfile1.txt')
        with open(dest_file, 'wb') as f:
            f.write(r.content)
        with open(dest_file) as fh:
            assert fh.readlines() == ['test_content']

    def test_put_object(self, minio_conn):
        # This test depends on methods tested test_stat_object and test_object_tags
        object_to_put = 'test_folder/testfile5.txt'
        tag_dict = {'tag_key1': 'tag_value1', 'tag_key2': 'tag_value2'}
        result = minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b'test_put_object'),
            metadata_dict={'meta_key': "meta_value"},
            tag_dict=tag_dict,
        )
        assert result is not None and result.object_name == object_to_put

        stat = minio_conn.stat_object(
            'test-bucket',
            object_to_put
        )

        assert stat.object_name == object_to_put
        assert stat.metadata['x-amz-meta-meta_key'] == 'meta_value'
        assert stat.metadata['x-amz-tagging-count'] == '2'
        # stat.tags is None!

        fetched_tags = minio_conn.get_object_tags(
            'test-bucket',
            object_to_put
        )
        assert fetched_tags == tag_dict

        # try to put the same object
        result = minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b'test_put_object')
            # skip_exist is True by default
        )
        assert result is None

        # try to put the same object one last time
        result = minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b'test_put_object'),
            skip_exist=False
        )
        assert result is not None and result.object_name == object_to_put

        # try to put an existing path/folder as object_name
        with pytest.raises(AssertionError) as e:
            minio_conn.put_object(
                'test-bucket',
                "test_folder",
                io.BytesIO(b'test_put_object'),
                skip_exist=False
            )
        msg = getattr(e, 'message', repr(e))
        assert 'The path must be first explicitly deleted' in msg

        # try to put an object with invalid size
        with pytest.raises(EtagVerificationError) as e:
            minio_conn.put_object(
                'test-bucket',
                "test.file",
                io.BytesIO(b'test_put_object'),
                length=0,
                max_retries=0,
            )
        msg = getattr(e, 'message', repr(e))
        assert '!= local ETAG' in msg

        # try to put an object with invalid size, with max_retries (+10 second)
        start = time.time()
        with pytest.raises(EtagVerificationError) as e:
            minio_conn.put_object(
                'test-bucket',
                "test.file",
                io.BytesIO(b'test_put_object'),
                length=0,
                max_retries=1,
            )
        msg = getattr(e, 'message', repr(e))
        assert '!= local ETAG' in msg
        end = time.time()
        assert end - start > 10

        # try to put an object with invalid size but skip the MD5 validation
        # this time the Md5sumValidationError should not raise
        minio_conn.put_object(
            'test-bucket',
            "test.file2",
            io.BytesIO(b'test_put_object'),
            length=0,
            skip_etag_verification=True
        )

        # test put empty object
        minio_conn.put_object(
            'test-bucket',
            "emptyfile",
            io.BytesIO(b''),
            content_type="application/octet-stream",
        )

        # try to put an empty name
        with pytest.raises(ValueError) as e:
            minio_conn.put_object(
                'test-bucket',
                "",
                io.BytesIO(b''),
                length=0
            )

    def test_put_object_multipart(self, minio_conn):
        object_to_put = 'test_folder/testfile5.txt'
        result = minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b"00000000000"*1024*1024),  # 11MB
            multipart_size=10*1024*1024  # 10MB
        )
        assert result.etag.endswith("-2")
        object_to_put = 'test_folder/testfile5.txt'
        result = minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b"00000000000"*1024*1024),  # 11MB
            multipart_size=5*1024*1024,  # 5MB
            skip_exist=False
        )
        assert result.etag.endswith("-3")

    def test_put_objects(self, tmp_path, minio_conn):
        # This test depends on methods tested test_stat_object and test_object_tags
        files_to_send = []
        # create 3 files
        for i in range(1, 4):
            f_name = f'test_put_file{i}.txt'
            input_file = os.path.join(tmp_path, f_name)
            with open(os.path.join(tmp_path, f_name), 'w') as fw:
                fw.write(str(i))

            files_to_send.append(
                [
                    input_file,  # source
                    f'new_folder/{f_name}',  # dest
                    None,  # content_type
                    -1,  # length
                    {f'meta_key{i}': f'meta_value{i}'},
                    {f'tag_key{i}-1': f'tag_value{i}-1', f'tag_key{i}-2': f'tag_value{i}-2'}
                ]
            )

        save_result = minio_conn.put_objects(
            'test-bucket',
            files_to_send[:2],  # send the first 2 files
            progress_bar=False
        )
        assert isinstance(save_result, list) and len(save_result) == 2

        objects = minio_conn.list_objects(
            'test-bucket',
            'new_folder',
            True
        )
        assert sorted([o.object_name for o in objects]) == [
            'new_folder/test_put_file1.txt',
            'new_folder/test_put_file2.txt'
        ]

        stat = minio_conn.stat_object(
            'test-bucket',
            'new_folder/test_put_file2.txt'
        )

        assert stat.object_name == 'new_folder/test_put_file2.txt'
        assert stat.metadata['x-amz-meta-meta_key2'] == 'meta_value2'
        assert stat.metadata['x-amz-tagging-count'] == '2'
        # stat.tags is None!

        fetched_tags = minio_conn.get_object_tags(
            'test-bucket',
            'new_folder/test_put_file2.txt'
        )
        assert fetched_tags == {'tag_key2-1': 'tag_value2-1', 'tag_key2-2': 'tag_value2-2'}

        # test skip_exist, send the last 2 files
        save_result = minio_conn.put_objects(
            'test-bucket',
            files_to_send[1:],
            skip_exist=True,
            progress_bar=False
        )

        assert isinstance(save_result, list) and len(save_result) == 1
        assert save_result[0].object_name == 'new_folder/test_put_file3.txt'

    def test_put_folder(self, tmp_path, minio_conn):
        # This test depends on methods tested in test_stat_object and test_get_object
        test_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'minio_test_folder')
        copied_test_data_folder = shutil.copytree(test_data_path, os.path.join(tmp_path, 'minio_test_folder'))

        save_result = minio_conn.put_folder(
            'test-bucket',
            copied_test_data_folder,
            'DEST/',
            skip_exist=False,
            progress_bar=False
        )
        assert len(save_result) == 4

        objects = minio_conn.list_objects(
            'test-bucket',
            'DEST/',
            True
        )
        assert sorted([o.object_name for o in objects]) == [
            'DEST/sub_folder/sub_sub_folder/test_put_file4.txt',
            'DEST/sub_folder/test_put_file3.txt',
            'DEST/test_put_file1.txt',
            'DEST/test_put_file2.txt'
        ]

        # check the content of one file
        data = minio_conn.get_object(
            'test-bucket',
            'DEST/sub_folder/sub_sub_folder/test_put_file4.txt'
        )
        assert data == b'content4'

        # add a large file to the input folder and resend it with skip_exist = True
        with open(os.path.join(copied_test_data_folder, 'sub_folder', 'test_put_file5.txt'), 'w') as fw:
            fw.write('00000000000' * 1024 * 1024)

        save_result = minio_conn.put_folder(
            'test-bucket',
            copied_test_data_folder,
            'DEST/',
            skip_exist=True,
            progress_bar=False
        )
        assert len(save_result) == 1
        assert save_result[0].object_name == 'DEST/sub_folder/test_put_file5.txt'

    def test_copy_object(self, minio_conn):
        # This test depends on methods tested test_stat_object and test_object_tags

        # add a new object in the bucket with metadata and tags
        object_to_put = 'test_folder/testfile5.txt'
        tag_dict = {'tag_key1': 'tag_value1', 'tag_key2': 'tag_value2'}
        minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b'test_put_object'),
            metadata_dict={'meta_key': "meta_value"},
            tag_dict=tag_dict,
        )

        minio_conn.copy_object(
            "test-bucket",
            "test_folder/testfile5.txt",
            "test-bucket-copy",
            "test_folder/testfile5.txt"
        )
        assert minio_conn.object_exist(
            "test-bucket-copy",
            "test_folder/testfile5.txt"
        )

        # check that metadata and tags are also copied
        stat = minio_conn.stat_object(
            "test-bucket-copy", "test_folder/testfile5.txt")
        assert stat.metadata['x-amz-meta-meta_key'] == 'meta_value'
        assert stat.metadata['x-amz-tagging-count'] == '2'

        tags = minio_conn.get_object_tags(
            "test-bucket-copy", "test_folder/testfile5.txt")
        assert tag_dict == tags

    @pytest.mark.parametrize(
        "source_object, dest_object, assert_msg", [
            ("test_folder/testfile4.txt", "test_folder/testfile4.txt",
             "destination_object_name cannot be identical to source_object_name"),
            ("test_folder/testfile4.txt", "test_folder",
             "destination_object_name is an existing path"),
            ("test_folder/", "new_folder",
             "Object does not exist"),  # source is a path, raise "Object does not exist" error
            # ("", " ", "no_message"),  "" or " " raise ValueError
    ])
    def test_copy_object_same_bucket(self, minio_conn, source_object, dest_object, assert_msg):
        # This test depends on methods tested test_stat_object and test_object_tags
        if assert_msg:
            with pytest.raises(Exception) as e:
                minio_conn.copy_object(
                    "test-bucket",
                    source_object,
                    "test-bucket",
                    dest_object
                )
            msg = getattr(e, 'message', repr(e))
            assert assert_msg in msg
        else:
            # except valid copy
            result = minio_conn.copy_object(
                "test-bucket",
                source_object,
                "test-bucket",
                dest_object
            )

            assert result.object_name == dest_object
            assert minio_conn.object_exist(
                "test-bucket",
                dest_object
            )

    def test_copy_multipart_file(self, minio_conn):
        # put a large file
        object_to_put = 'test_folder/largefile.txt'
        minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b"00000000000" * 1024 * 1024),  # 11MB
            multipart_size=5 * 1024 * 1024  # 5MB
        )

        res = minio_conn.copy_object('test-bucket',
                                     'test_folder/largefile.txt',
                                     'test-bucket',
                                     'test_folder/largefile2.txt'
                                     )
        assert res

    @pytest.mark.skipif(
        True,
        reason="Skipped on GitLab runner"
    )
    def test_copy_multipart_large_file_w_metadata(self, minio_conn):
        object_to_put = 'test_folder/largefile.txt'
        dest_object = 'test_folder/largefile2.txt'
        file_size = 6 * 1024 * 1024 * 1024  # 6 GiB
        metadata = {"x-amz-meta-testkey": "testvalue"}

        minio_conn.put_object(
            'test-bucket',
            object_to_put,
            io.BytesIO(b"000000" * 1024 * 1024 * 1024),  # 11MB
            length=file_size,
            metadata_dict=metadata
        )

        # Perform the copy (should skip ETag check for large file)
        res = minio_conn.copy_object(
            'test-bucket',
            object_to_put,
            'test-bucket',
            dest_object
        )
        assert res

        # Check that the destination object exists and has the correct size
        stat = minio_conn.stat_object('test-bucket', dest_object)
        assert stat.size == file_size

        # Check that metadata is preserved
        for k, v in metadata.items():
            assert stat.metadata.get(k) == v

    @pytest.mark.parametrize(
        "source_prefix, dest_prefix, expected_files, assert_msg", [
            ("test_folder", "", ['testfile3.txt', 'testfile4.txt'], None),
            ("test_folder", None, [], "Invalid type, destination_objects_prefix must be a string"),
            ("test_folder/", "", ['testfile3.txt', 'testfile4.txt'], None),
            ("test_folder//", "", [], "Object name contains unsupported characters"),
            ("no_exist", "", [], None),
            ("test_folder", "test//", [], "Object name contains unsupported characters"),
            ("test_folder", "test/", ['test/testfile3.txt', 'test/testfile4.txt'], None),
            ("test_folder", "test_", ['test_testfile3.txt', 'test_testfile4.txt'], None),
            ("test", "test", ['test_folder/testfile3.txt', 'test_folder/testfile4.txt',
                              'testfile1.txt', 'testfile2.txt'], None),  # everything start with 'test', identical copy
            ("test", "foo/", ['foo/_folder/testfile3.txt', 'foo/_folder/testfile4.txt',
                              'foo/file1.txt', 'foo/file2.txt'], None),  # remove the 'test' and replace with 'foo/'
        ])
    def test_copy_objects(self, minio_conn, source_prefix, dest_prefix, expected_files, assert_msg):
        if assert_msg:
            with pytest.raises(Exception) as e:
                minio_conn.copy_objects(
                    "test-bucket",
                    source_prefix,
                    "test-bucket-copy",
                    dest_prefix
                )
            msg = getattr(e, 'message', repr(e))
            assert assert_msg in msg
        else:
            minio_conn.copy_objects(
                "test-bucket",
                source_prefix,
                "test-bucket-copy",
                dest_prefix
            )

            dest_objects = sorted([o.object_name for o in minio_conn.list_objects(
                "test-bucket-copy",
                None,
                recursive=True)])

            assert dest_objects == expected_files

    @pytest.mark.parametrize(
        "dest_prefix, expected_files", [
            ("", ['test_folder/testfile3.txt', 'test_folder/testfile4.txt', 'testfile1.txt', 'testfile2.txt']),
            ("_", ['_test_folder/testfile3.txt', '_test_folder/testfile4.txt', '_testfile1.txt', '_testfile2.txt']),
            ("_/", ['_/test_folder/testfile3.txt', '_/test_folder/testfile4.txt', '_/testfile1.txt', '_/testfile2.txt']),
            ("_//", []),  # invalid characters
        ])
    def test_copy_all_objects(self, minio_conn, dest_prefix, expected_files):
        if not expected_files:
            with pytest.raises(minio.error.S3Error):
                minio_conn.copy_objects(
                    "test-bucket",
                    None,
                    "test-bucket-copy",
                    dest_prefix
                )
        else:
            minio_conn.copy_objects(
                "test-bucket",
                None,
                "test-bucket-copy",
                dest_prefix
            )

            dest_objects = sorted([o.object_name for o in minio_conn.list_objects(
                "test-bucket-copy",
                None,
                recursive=True)])

            assert dest_objects == expected_files

    @pytest.mark.parametrize(
        # bucket objects list is ['b/z.f', 'z.f', 'z/a', 'z/b']
        "source_prefix, dest_prefix, expected_files, assert_msg", [
            ("a", "a", [],
             "destination_objects_prefix contains the source_objects_prefix"),
            ("a", "a/a", [],
             "destination_objects_prefix contains the source_objects_prefix"),
            ("b", "", ['b/z.f', 'z.f', 'z/a', 'z/b'], None),
            # """
            # the case above will lead to data loss because 'b/z.f' is replacing z.f
            # """
            ("z/", "", ['z.f', 'b/z.f', 'z/a', 'z/b'], "destination_object_name is an existing path"),
            # """
            # the case above will lead incomplete copy, because before the exception is raised
            # object 'a' is created
            # """
            # ("z.f", "", [], "?"), raise ValueError 'cause object "z.f" becomes ""
        ])
    def test_copy_objects_same_bucket(self, minio_conn, source_prefix, dest_prefix, expected_files, assert_msg):
        # re setup bucket =====
        minio_conn.delete_objects("test-bucket", None)
        # add some files
        minio_conn.put_object(
            "test-bucket",
            "z/a",  # object name
            io.BytesIO(b"test"),
            length=4
        )
        minio_conn.put_object(
            "test-bucket",
            "z/b",  # object name
            io.BytesIO(b"test"),
            length=4
        )
        minio_conn.put_object(
            "test-bucket",
            "z.f",
            io.BytesIO(b""),
            length=0
        )
        minio_conn.put_object(
            "test-bucket",
            "b/z.f",
            io.BytesIO(b"test"),
            length=4
        )
        # ======================

        if assert_msg:
            with pytest.raises(Exception) as e:
                minio_conn.copy_objects(
                    "test-bucket",
                    source_prefix,
                    "test-bucket",
                    dest_prefix
                )
            msg = getattr(e, 'message', repr(e))
            assert assert_msg in msg
        else:
            result = minio_conn.copy_objects(
                "test-bucket",
                source_prefix,
                "test-bucket",
                dest_prefix
            )
            assert result
            dest_objects = sorted([o.object_name for o in minio_conn.list_objects(
                "test-bucket",
                None,
                recursive=True)])

            assert dest_objects == expected_files

    @pytest.mark.parametrize(
        "source_object, dest_object, assert_msg", [
            ("testfile1.txt", "testfile1copy.txt", None),
            ("testfile1.txt", "testfile1.txt", None),
            # ("", "test", None),  # raise ValueError
            #  ("testfile1.txt", "", None),  # raise ValueError
            ("test_folder", "test", "Object does not exist"),  # is a path
        ])
    def test_move_object(self, minio_conn, source_object, dest_object, assert_msg):
        if assert_msg:
            with pytest.raises(Exception) as e:
                minio_conn.copy_object(
                    "test-bucket",
                    source_object,
                    "test-bucket-copy",
                    dest_object
                )
            msg = getattr(e, 'message', repr(e))
            assert assert_msg in msg
        else:
            minio_conn.move_object(
                "test-bucket",
                source_object,
                "test-bucket-copy",
                dest_object
            )
            assert minio_conn.object_exist(
                "test-bucket-copy",
                dest_object
            )
            assert not minio_conn.object_exist(
                "test-bucket",
                source_object
            )

    @pytest.mark.parametrize(
        "source_object, dest_object, assert_msg", [
            ("testfile1.txt", "testfile1copy.txt", None),
            ("testfile1.txt", "testfile1.txt", "destination_object_name cannot be identical"),
            ("testfile1.txt", "test_folder", "destination_object_name is an existing path"),
            ("testfile1.txt", "testfile2.txt", None)  # overwrite
        ])
    def test_move_object_same_bucket(self, minio_conn, source_object, dest_object, assert_msg):
        if assert_msg:
            with pytest.raises(Exception) as e:
                minio_conn.copy_object(
                    "test-bucket",
                    source_object,
                    "test-bucket",
                    dest_object
                )
            msg = getattr(e, 'message', repr(e))
            assert assert_msg in msg
        else:
            minio_conn.move_object(
                "test-bucket",
                source_object,
                "test-bucket",
                dest_object
            )
            assert minio_conn.object_exist(
                "test-bucket",
                dest_object
            )
            assert not minio_conn.object_exist(
                "test-bucket",
                source_object
            )

    @pytest.mark.parametrize(
        "source_prefix, dest_prefix, expected_files, assert_msg", [
            ("test_folder", "", ['testfile3.txt', 'testfile4.txt'], None),
            ("test_folder", None, [],
             "Invalid type, destination_objects_prefix must be a string"),
            ("test_folder/", "", ['testfile3.txt', 'testfile4.txt'], None),
            ("test_folder//", "", [], "Object name contains unsupported characters"),
            ("no_exist", "", [], None),
            (None, "", ['test_folder/testfile3.txt', 'test_folder/testfile4.txt', 'testfile1.txt', 'testfile2.txt'], None),  # move everything
            ("test_folder", "test//", [], "Object name contains unsupported characters"),
            ("test_folder", "test/", ['test/testfile3.txt', 'test/testfile4.txt'], None),
            ("test_folder", "test_", ['test_testfile3.txt', 'test_testfile4.txt'], None),
            ("test", "test", ['test_folder/testfile3.txt', 'test_folder/testfile4.txt',
                              'testfile1.txt', 'testfile2.txt'], None),  # everything start with 'test', move everything
            ("test", "foo/", ['foo/_folder/testfile3.txt', 'foo/_folder/testfile4.txt',
                              'foo/file1.txt', 'foo/file2.txt'], None),  # move and replace 'test' with 'foo/'
        ])
    def test_move_objects(self, minio_conn, source_prefix, dest_prefix, expected_files, assert_msg):
        if assert_msg:
            with pytest.raises(Exception) as e:
                minio_conn.move_objects(
                    "test-bucket",
                    source_prefix,
                    "test-bucket-copy",
                    dest_prefix
                )
            msg = getattr(e, 'message', repr(e))
            assert assert_msg in msg
        else:
            result = minio_conn.move_objects(
                "test-bucket",
                source_prefix,
                "test-bucket-copy",
                dest_prefix
            )

        if expected_files:
            assert result
            dest_objects = sorted([o.object_name for o in minio_conn.list_objects(
                "test-bucket-copy",
                dest_prefix,
                recursive=True)])
            assert dest_objects == expected_files

            assert len(sorted([o.object_name for o in minio_conn.list_objects(
                "test-bucket",
                source_prefix,
                recursive=True)])) == 0

    @pytest.mark.parametrize(
        # bucket objects list is ['b/z.f', 'z.f', 'z/a', 'z/b']
        "source_prefix, dest_prefix, expected_dfiles, expected_sfiles, assert_msg", [
            ("a", "a", [], [],
             "destination_objects_prefix contains the source_objects_prefix"),
            ("a", "a/a", [], [],
             "destination_objects_prefix contains the source_objects_prefix"),
            ("b", "", ['z.f', 'z/a', 'z/b'], [], None),
            # """
            # the case above will lead to data loss because 'b/z.f' is replacing z.f
            # """
            ("z/", "", ['a', 'b/z.f', 'z.f', 'z/a', 'z/b'], ['z/a', 'z/b'],
             "destination_object_name is an existing path"),
            # """
            # the case above will lead incomplete copy, because before the exception is raised
            # object 'a' is created. Note that 'z/a' is not deleted because of the exception
            # """
            # ("z.f", "", [], "?"), raise ValueError because object "z.f" becomes ""
        ])
    def test_move_objects_same_bucket(self, minio_conn, source_prefix, dest_prefix, expected_dfiles,
                                      expected_sfiles, assert_msg):
        # re setup bucket =====
        minio_conn.delete_objects("test-bucket", None)
        # add some files
        minio_conn.put_object(
            "test-bucket",
            "z/a",  # object name
            io.BytesIO(b"test"),
            length=4
        )
        minio_conn.put_object(
            "test-bucket",
            "z/b",  # object name
            io.BytesIO(b"test"),
            length=4
        )
        minio_conn.put_object(
            "test-bucket",
            "z.f",
            io.BytesIO(b""),
            length=0
        )
        minio_conn.put_object(
            "test-bucket",
            "b/z.f",
            io.BytesIO(b"test"),
            length=4
        )
        # ======================

        if assert_msg:
            with pytest.raises(Exception) as e:
                minio_conn.move_objects(
                    "test-bucket",
                    source_prefix,
                    "test-bucket",
                    dest_prefix
                )
            msg = getattr(e, 'message', repr(e))
            assert assert_msg in msg
        else:
            result = minio_conn.move_objects(
                "test-bucket",
                source_prefix,
                "test-bucket",
                dest_prefix
            )
            assert result
        if expected_dfiles:
            dest_objects = sorted([o.object_name for o in minio_conn.list_objects(
                "test-bucket",
                dest_prefix,
                recursive=True)])
            assert dest_objects == expected_dfiles
            assert sorted([o.object_name for o in minio_conn.list_objects(
                "test-bucket",
                source_prefix,
                recursive=True)]) == expected_sfiles
