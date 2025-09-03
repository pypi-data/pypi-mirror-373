import requests
from urllib.parse import urlparse
from typing import Dict, Optional


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
        if result['confidence'] in ['unknown', 'medium']:
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

        return result

    def detect_file_type(self, url: str) -> str:
        """简单的文件类型检测，返回类型字符串"""
        info = self.get_detailed_info(url)
        return info.get('detected_type', 'Unknown')

    def get_file_category(self, file_type: str) -> str:
        """获取文件类别"""
        if not file_type or file_type == 'Unknown':
            return 'Unknown'

        image_types = {'PNG', 'JPEG', 'GIF', 'WEBP', 'BMP', 'TIFF', 'ICO', 'SVG', 'HEIC', 'AVIF'}
        video_types = {'MP4', 'AVI', 'MOV', 'WMV', 'FLV', 'WEBM', 'MKV', 'M4V', 'MPEG', '3GP', 'OGV', 'TS', 'MTS',
                       'VOB'}
        audio_types = {'MP3', 'WAV', 'FLAC', 'AAC', 'OGG', 'WMA', 'M4A', 'APE', 'OPUS', 'AIFF', 'AU'}

        if file_type in image_types:
            return 'Image'
        elif file_type in video_types:
            return 'Video'
        elif file_type in audio_types:
            return 'Audio'
        else:
            return 'Other'


# if __name__ == "__main__":
#     detector = FileTypeDetector()
#     result = detector.get_detailed_info("https://cdn.pixabay.com/user/2024/12/10/12-18-33-812_96x96.jpeg")
#     print(result)
