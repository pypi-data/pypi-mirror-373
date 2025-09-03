import random
import logging
import time

import requests

from urllib.parse import urlparse
from typing import Any, Set, Dict, Optional
from requests.exceptions import RequestException


class FileTypeDetector:

    def __init__(self):
        self.file_signatures = {
            # 图片格式
            b'\x89PNG\r\n\x1a\n': 'PNG',
            b'\xff\xd8\xff': 'JPEG',
            b'GIF87a': 'GIF',
            b'GIF89a': 'GIF',
            b'RIFF': 'WEBP',  # 需要进一步检查
            b'BM': 'BMP',
            b'II*\x00': 'TIFF',
            b'MM\x00*': 'TIFF',
            b'\x00\x00\x01\x00': 'ICO',
            b'\x00\x00\x02\x00': 'CUR',

            # 视频格式
            b'\x00\x00\x00\x18ftypmp4': 'MP4',
            b'\x00\x00\x00\x20ftypM4V': 'M4V',
            b'FLV\x01': 'FLV',
            b'\x1aE\xdf\xa3': 'WEBM',
            b'RIFF': 'AVI',  # 需要进一步检查
            b'\x00\x00\x01\xba': 'MPEG',
            b'\x00\x00\x01\xb3': 'MPEG',
            b'OggS': 'OGV',

            # 音频格式
            b'ID3': 'MP3',
            b'\xff\xfb': 'MP3',
            b'\xff\xf3': 'MP3',
            b'\xff\xf2': 'MP3',
            b'fLaC': 'FLAC',
            b'RIFF': 'WAV',  # 需要进一步检查
            b'OggS': 'OGG',  # 需要进一步检查
            b'ftypM4A': 'M4A',
            b'MAC ': 'APE',

            # 其他格式
            b'%PDF': 'PDF',
            b'PK\x03\x04': 'ZIP',
            b'Rar!\x1a\x07\x00': 'RAR',
            b'\x37\x7a\xbc\xaf\x27\x1c': '7Z',
        }

        # 扩展名映射
        self.extension_map = {
            # 图片
            '.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.gif': 'GIF',
            '.webp': 'WEBP', '.bmp': 'BMP', '.tiff': 'TIFF', '.tif': 'TIFF',
            '.ico': 'ICO', '.svg': 'SVG', '.heic': 'HEIC', '.avif': 'AVIF',

            # 视频
            '.mp4': 'MP4', '.avi': 'AVI', '.mov': 'MOV', '.wmv': 'WMV',
            '.flv': 'FLV', '.webm': 'WEBM', '.mkv': 'MKV', '.m4v': 'M4V',
            '.mpg': 'MPEG', '.mpeg': 'MPEG', '.3gp': '3GP', '.ogv': 'OGV',
            '.ts': 'TS', '.mts': 'MTS', '.vob': 'VOB',

            # 音频
            '.mp3': 'MP3', '.wav': 'WAV', '.flac': 'FLAC', '.aac': 'AAC',
            '.ogg': 'OGG', '.wma': 'WMA', '.m4a': 'M4A', '.ape': 'APE',
            '.opus': 'OPUS', '.aiff': 'AIFF', '.au': 'AU',
        }

        # MIME类型映射
        self.mime_type_map = {
            # 图片
            'image/jpeg': 'JPEG', 'image/png': 'PNG', 'image/gif': 'GIF',
            'image/webp': 'WEBP', 'image/bmp': 'BMP', 'image/tiff': 'TIFF',
            'image/svg+xml': 'SVG', 'image/x-icon': 'ICO',

            # 视频
            'video/mp4': 'MP4', 'video/avi': 'AVI', 'video/quicktime': 'MOV',
            'video/x-msvideo': 'AVI', 'video/webm': 'WEBM', 'video/x-flv': 'FLV',
            'video/3gpp': '3GP', 'video/ogg': 'OGV',

            # 音频
            'audio/mpeg': 'MP3', 'audio/wav': 'WAV', 'audio/flac': 'FLAC',
            'audio/aac': 'AAC', 'audio/ogg': 'OGG', 'audio/x-ms-wma': 'WMA',
            'audio/mp4': 'M4A', 'audio/opus': 'OPUS',
        }

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_file_extension(self, url: str) -> str:
        """从URL获取文件扩展名"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        site = parsed.netloc

        # 移除查询参数
        if '?' in path:
            path = path.split('?')[0]

        # 获取扩展名
        if '.' in path:
            return '.' + path.split('.')[-1], site
        return '', site

    def detect_by_extension(self, url: str) -> Optional[str]:
        """通过文件扩展名检测类型"""
        ext, site = self.get_file_extension(url)
        return self.extension_map.get(ext)

    def detect_by_mime_type(self, content_type: str) -> Optional[str]:
        """通过MIME类型检测"""
        if not content_type:
            return None

        # 清理content-type，移除参数
        mime_type = content_type.split(';')[0].strip().lower()
        return self.mime_type_map.get(mime_type)

    def get_partial_content(self, url: str, max_bytes: int = 64) -> Optional[bytes]:
        """获取文件的前几个字节"""
        try:
            headers = {'Range': f'bytes=0-{max_bytes - 1}'}
            response = self.session.get(url, headers=headers, timeout=10)

            if response.status_code in [200, 206]:
                return response.content
        except Exception as e:
            print(f"获取内容失败: {e}")
        return None

    def detect_by_signature(self, data: bytes) -> Optional[str]:
        """通过文件签名检测类型"""
        if not data:
            return None

        # 检查各种文件签名
        for signature, file_type in self.file_signatures.items():
            if data.startswith(signature):
                # 特殊处理需要进一步检查的格式
                if signature == b'RIFF' and len(data) >= 12:
                    # 检查是WEBP、AVI还是WAV
                    if data[8:12] == b'WEBP':
                        return 'WEBP'
                    elif data[8:12] == b'AVI ':
                        return 'AVI'
                    elif data[8:12] == b'WAVE':
                        return 'WAV'
                elif signature == b'OggS' and len(data) >= 32:
                    # 检查是OGG音频还是OGV视频
                    if b'vorbis' in data[:64].lower():
                        return 'OGG'
                    elif b'theora' in data[:64].lower():
                        return 'OGV'
                    else:
                        return 'OGG'
                else:
                    return file_type

        # 检查MP4相关格式
        if len(data) >= 12 and data[4:8] == b'ftyp':
            brand = data[8:12]
            if brand in [b'mp41', b'mp42', b'isom', b'avc1']:
                return 'MP4'
            elif brand == b'M4A ':
                return 'M4A'
            elif brand == b'M4V ':
                return 'M4V'
            elif brand == b'qt  ':
                return 'MOV'

        return None

    def get_detailed_info(self, url, content_type, data) -> Dict:
        """获取详细的文件信息"""
        result = {
            'url': url,
            'site': None,
            'detected_type': None,
            'confidence': 'unknown',
            'methods_used': [],
            'content_type': content_type,
            'extension': None
        }

        # 1. 先尝试HEAD请求获取HTTP头信息
        try:
            result['content_type'] = content_type
            # result['file_size'] = content_length

            # 通过MIME类型检测
            mime_detected = self.detect_by_mime_type(content_type)
            if mime_detected:
                result['detected_type'] = mime_detected
                result['confidence'] = 'high'
                result['methods_used'].append('mime_type')
        except Exception as e:
            print(f"HEAD请求失败: {e}")

        # 2. 通过扩展名检测
        ext_detected = self.detect_by_extension(url)
        result['extension'], result['site'] = self.get_file_extension(url)

        if ext_detected:
            if not result['detected_type']:
                result['detected_type'] = ext_detected
                result['confidence'] = 'medium'
            elif result['detected_type'] == ext_detected:
                result['confidence'] = 'very_high'  # MIME和扩展名一致
            result['methods_used'].append('extension')

        # 3. 如果前两种方法不确定，使用文件签名检测
        if data and result['confidence'] in ['unknown', 'medium']:
            signature_detected = self.detect_by_signature(data)
            if signature_detected:
                if not result['detected_type']:
                    result['detected_type'] = signature_detected
                    result['confidence'] = 'high'
                elif result['detected_type'] == signature_detected:
                    result['confidence'] = 'very_high'
                else:
                    # 冲突时，优先相信文件签名
                    result['detected_type'] = signature_detected
                    result['confidence'] = 'high'
                result['methods_used'].append('file_signature')

        result['cate'] = self.get_file_category(result['detected_type'])
        return result

    def get_file_category(self, file_type: str) -> str:
        """获取文件类别"""
        if not file_type or file_type == 'Unknown':
            return 'Unknown'

        image_types = {'PNG', 'JPEG', 'GIF', 'WEBP', 'BMP', 'TIFF', 'ICO', 'SVG', 'HEIC', 'AVIF'}
        video_types = {'MP4', 'AVI', 'MOV', 'WMV', 'FLV', 'WEBM', 'MKV', 'M4V', 'MPEG', '3GP', 'OGV', 'TS', 'MTS',
                       'VOB'}
        audio_types = {'MP3', 'WAV', 'FLAC', 'AAC', 'OGG', 'WMA', 'M4A', 'APE', 'OPUS', 'AIFF', 'AU'}

        if file_type in image_types:
            return 'image'
        elif file_type in video_types:
            return 'video'
        elif file_type in audio_types:
            return 'audio'
        else:
            return 'other'


class Request:
    """
    HTTP 请求封装类，提供统一的请求接口和相关功能。

    Features:
    - 自动 User-Agent 生成
    - 灵活的请求参数配置
    - 文件类型检测
    - 错误处理和状态码检查
    """

    # 支持的 requests 库参数
    _REQUEST_ATTRS: Set[str] = frozenset({
        "params", "headers", "cookies", "data", "json", "files",
        "auth", "timeout", "proxies", "hooks", "stream", "verify",
        "cert", "allow_redirects"
    })

    # 默认超时时间
    _DEFAULT_TIMEOUT = 30

    # User-Agent 模板和版本范围
    _UA_TEMPLATE = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{v1}_{v2}) "
        "AppleWebKit/{v4}.{v3} (KHTML, like Gecko) "
        "Chrome/105.0.0.0 Safari/{v4}.{v3} Edg/105.0.{v5}.{v6}"
    )
    _UA_VERSION_RANGES = {
        'v1': (4, 15), 'v2': (3, 11), 'v3': (1, 16),
        'v4': (533, 605), 'v5': (1000, 6000), 'v6': (10, 80)
    }

    def __init__(
            self,
            url: str,
            seed: Any = None,
            method: Optional[str] = None,
            random_ua: bool = True,
            check_status_code: bool = True,
            **kwargs
    ):
        """
        初始化请求对象。

        Args:
            url: 请求的 URL
            seed: 种子对象或标识符
            method: HTTP 方法，如果不指定则自动推断
            random_ua: 是否使用随机 User-Agent
            check_status_code: 是否检查响应状态码
            **kwargs: 其他请求参数

        Raises:
            ValueError: 当 URL 格式无效时
        """
        self.scheme = None
        self.netloc = None
        self.detector_info = None
        self.content_length = None
        self._validate_url(url)

        self.url = url
        self.seed = seed
        self.check_status_code = check_status_code
        self.request_settings: Dict[str, Any] = {}

        # 分离请求参数和实例属性
        self._process_kwargs(kwargs)

        self.method = self._determine_method(method)

        # 设置默认超时
        if 'timeout' not in self.request_settings:
            self.request_settings['timeout'] = self._DEFAULT_TIMEOUT

        # 构建请求头
        if random_ua:
            self._setup_headers()

    def _validate_url(self, url: str) -> None:
        """验证 URL 格式"""
        try:
            result = urlparse(url)
            self.scheme = result.scheme
            self.netloc = result.netloc
            if not all([self.scheme, self.netloc]):
                raise ValueError(f"无效的 URL 格式: {url}")
        except Exception as e:
            raise ValueError(f"URL 解析失败: {e}")

    def _process_kwargs(self, kwargs: Dict[str, Any]) -> None:
        """处理关键字参数，分离请求参数和实例属性"""
        for key, value in kwargs.items():
            if key in self._REQUEST_ATTRS:
                self.request_settings[key] = value
            else:
                setattr(self, key, value)

    def _determine_method(self, method: Optional[str]) -> str:
        if method:
            return method.upper()

        has_body = bool(
            self.request_settings.get("data") or
            self.request_settings.get("json") or
            self.request_settings.get("files")
        )
        return "POST" if has_body else "GET"

    def _generate_random_ua(self) -> str:
        """生成随机 User-Agent"""
        versions = {
            key: random.randint(*range_tuple)
            for key, range_tuple in self._UA_VERSION_RANGES.items()
        }
        return self._UA_TEMPLATE.format(**versions)

    def _setup_headers(self) -> None:
        """设置请求头，包括随机 User-Agent"""
        headers = self.request_settings.setdefault("headers", {})

        # 使用小写键名进行检查，保持一致性
        ua_keys = ['user-agent', 'User-Agent']
        if not any(headers.get(key) for key in ua_keys):
            headers["User-Agent"] = self._generate_random_ua()

    def execute(self) -> requests.Response:
        """
        执行 HTTP 请求。

        Returns:
            requests.Response: 响应对象

        Raises:
            RequestException: 请求执行失败
            requests.HTTPError: HTTP 状态码错误（当 check_status_code=True 时）
        """
        try:
            response = requests.request(
                method=self.method,
                url=self.url,
                **self.request_settings
            )

            if self.check_status_code:
                response.raise_for_status()

            return response

        except RequestException as e:
            logging.error(f"请求执行失败 - URL: {self.url}, 错误: {e}")
            raise

    # 保持向后兼容性
    def download(self) -> requests.Response:
        """下载方法，为了向后兼容性保留"""
        return self.execute()

    def normal_download(self, file_type_detect: bool = True) -> bytes:
        """普通下载模式"""
        detect_settings = self.request_settings.copy()
        detect_settings.pop('stream', None)

        response = requests.request(
            method=self.method,
            url=self.url,
            **detect_settings
        )

        if self.check_status_code:
            response.raise_for_status()

        content_type = response.headers.get('content-type')
        result = response.content
        response.close()

        if file_type_detect and not self.detector_info:
            head_data = result[:64]
            detector = FileTypeDetector()
            self.detector_info = detector.get_detailed_info(
                url=self.url, content_type=content_type, data=head_data
            )

        return result

    def range_download(self, start: int = 0, chunk_size: int = 1024, file_type_detect: bool = True) -> iter(bytes):
        # 分块下载
        downloaded = start
        retry_count = 0
        max_retries = 3

        detect_settings = self.request_settings.copy()
        detect_settings.pop('stream', None)

        if file_type_detect and not self.detector_info:
            detect_settings.setdefault("headers", {})['Range'] = "bytes=0-63"
            test_response = requests.request(
                method=self.method,
                url=self.url,
                **detect_settings
            )
            content_type = test_response.headers.get("Content-Type")
            head_data = test_response.content
            test_response.close()

            detector = FileTypeDetector()
            self.detector_info = detector.get_detailed_info(
                url=self.url, content_type=content_type, data=head_data
            )

        while downloaded < self.content_length:
            _start = downloaded
            _end = min(downloaded + chunk_size - 1, self.total_size - 1)
            detect_settings.setdefault("headers", {})['Range'] = f"bytes={_start}-{_end}"

            response = requests.request(
                method=self.method,
                url=self.url,
                **detect_settings
            )

            if response.status_code == 206:
                chunk_data = response.content
                yield chunk_data
                downloaded += len(chunk_data)
                retry_count = 0  # 重置重试计数
                logging.info(f"下载进度: {downloaded}/{self.total_size} ({downloaded / self.total_size * 100:.1f}%)")

            elif response.status_code == 416:  # Range Not Satisfiable
                logging.info("Range请求超出范围")
                break

            else:
                logging.debug(f"Range请求失败: {response.status_code}")
                if retry_count < max_retries:
                    retry_count += 1
                    time.sleep(0.5)
                    continue

            response.close()

    def detect_accept_ranges(self) -> bool:
        detect_settings = self.request_settings.copy()
        detect_settings.pop('stream', None)

        head_response = requests.head(self.url, **detect_settings)
        if head_response.status_code not in [200, 206]:
            logging.error(f"HEAD请求失败: {head_response.status_code}")
            raise ValueError("HTTP状态码错误")

        self.content_length = int(head_response.headers.get('content-length', 0))
        accept_ranges = str(head_response.headers.get('accept-ranges')).lower()

        supports_range = True

        # 根据检测结果使用不同下载方式
        if accept_ranges == 'none' or not self.content_length:
            supports_range = False
        else:
            test_range_settings = detect_settings.copy()
            test_range_settings.setdefault("headers", {})['Range'] = "bytes=0-63"
            test_response = requests.request(
                method=self.method,
                url=self.url,
                **test_range_settings
            )
            if test_response.status_code == 206:
                actual_length = len(test_response.content)
                if actual_length != 64:
                    logging.debug(f"⚠️ Range请求返回长度不匹配: 期望64, 实际{actual_length}")
                    supports_range = False
            else:
                supports_range = False

        return supports_range

    def detect_file_type(self) -> Dict[str, Any]:
        """
        检测文件类型。

        Returns:
            Dict[str, Any]: 文件类型信息

        Raises:
            RequestException: 请求执行失败
            ImportError: FileTypeDetector 未找到
        """
        try:
            # 创建检测请求的配置
            detect_settings = self.request_settings.copy()

            # 设置 Range 头获取文件前64字节
            headers = detect_settings.setdefault("headers", {}).copy()
            headers['Range'] = "bytes=0-63"
            detect_settings["headers"] = headers

            # 移除 stream 参数避免冲突
            detect_settings.pop('stream', None)

            # 执行检测请求
            response = requests.request(
                method=self.method,
                url=self.url,
                **detect_settings
            )

            content_type = response.headers.get("Content-Type")
            detector = FileTypeDetector()

            return detector.get_detailed_info(
                url=self.url,
                content_type=content_type,
                data=response.content
            )

        except RequestException as e:
            logging.error(f"文件类型检测失败 - URL: {self.url}, 错误: {e}")

    @property
    def to_dict(self) -> Dict[str, Any]:
        excluded_keys = {"request_settings", "url", "seed", "method", "check_status_code"}
        result = {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_') and key not in excluded_keys
        }
        result['request_settings'] = self.request_settings.copy()
        return result

    def __repr__(self) -> str:
        return f"Request(method='{self.method}', url='{self.url}')"

    def __str__(self) -> str:
        return f"{self.method} {self.url}"
