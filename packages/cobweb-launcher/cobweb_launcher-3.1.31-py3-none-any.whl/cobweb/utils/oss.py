#
# from cobweb import setting
# from requests import Response
# from oss2 import Auth, Bucket, models, PartIterator
# from cobweb.exceptions import oss_db_exception
# from cobweb.utils.decorators import decorator_oss_db
#
#
# class OssUtil:
#
#     def __init__(
#         self,
#         bucket=None,
#         endpoint=None,
#         access_key=None,
#         secret_key=None,
#         chunk_size=None,
#         min_upload_size=None,
#         **kwargs
#     ):
#         self.bucket = bucket or setting.OSS_BUCKET
#         self.endpoint = endpoint or setting.OSS_ENDPOINT
#         self.chunk_size = int(chunk_size or setting.OSS_CHUNK_SIZE)
#         self.min_upload_size = int(min_upload_size or setting.OSS_MIN_UPLOAD_SIZE)
#
#         self.failed_count = 0
#         self._kw = kwargs
#
#         self._auth = Auth(
#             access_key_id=access_key or setting.OSS_ACCESS_KEY,
#             access_key_secret=secret_key or setting.OSS_SECRET_KEY
#         )
#         self._client = Bucket(
#             auth=self._auth,
#             endpoint=self.endpoint,
#             bucket_name=self.bucket,
#             **self._kw
#         )
#
#     def failed(self):
#         self.failed_count += 1
#         if self.failed_count >= 5:
#             self._client = Bucket(
#                 auth=self._auth,
#                 endpoint=self.endpoint,
#                 bucket_name=self.bucket,
#                 **self._kw
#             )
#
#     def exists(self, key: str) -> bool:
#         try:
#             result = self._client.object_exists(key)
#             self.failed_count = 0
#             return result
#         except Exception as e:
#             self.failed()
#             raise e
#
#     def head(self, key: str) -> models.HeadObjectResult:
#         return self._client.head_object(key)
#
#     @decorator_oss_db(exception=oss_db_exception.OssDBInitPartError)
#     def init_part(self, key) -> models.InitMultipartUploadResult:
#         """初始化分片上传"""
#         return self._client.init_multipart_upload(key)
#
#     @decorator_oss_db(exception=oss_db_exception.OssDBPutObjError)
#     def put(self, key, data) -> models.PutObjectResult:
#         """文件上传"""
#         return self._client.put_object(key, data)
#
#     @decorator_oss_db(exception=oss_db_exception.OssDBPutPartError)
#     def put_part(self, key, upload_id, position, data) -> models.PutObjectResult:
#         """分片上传"""
#         return self._client.upload_part(key, upload_id, position, data)
#
#     def list_part(self, key, upload_id):  # -> List[models.ListPartsResult]:
#         """获取分片列表"""
#         return [part_info for part_info in PartIterator(self._client, key, upload_id)]
#
#     @decorator_oss_db(exception=oss_db_exception.OssDBMergeError)
#     def merge(self, key, upload_id, parts=None) -> models.PutObjectResult:
#         """合并分片"""
#         headers = None if parts else {"x-oss-complete-all": "yes"}
#         return self._client.complete_multipart_upload(key, upload_id, parts, headers=headers)
#
#     @decorator_oss_db(exception=oss_db_exception.OssDBAppendObjError)
#     def append(self, key, position, data) -> models.AppendObjectResult:
#         """追加上传"""
#         return self._client.append_object(key, position, data)
#
#     def iter_data(self, data, chunk_size=None):
#         chunk_size = chunk_size or self.chunk_size
#         if isinstance(data, Response):
#             for part_data in data.iter_content(chunk_size):
#                 yield part_data
#         if isinstance(data, bytes):
#             for i in range(0, len(data), chunk_size):
#                 yield data[i:i + chunk_size]
#
#     def assemble(self, ready_data, data, chunk_size=None):
#         upload_data = b""
#         ready_data = ready_data + data
#         chunk_size = chunk_size or self.chunk_size
#         if len(ready_data) >= chunk_size:
#             upload_data = ready_data[:chunk_size]
#             ready_data = ready_data[chunk_size:]
#         return ready_data, upload_data
#
#     def content_length(self, key: str) -> int:
#         head = self.head(key)
#         return head.content_length
#
