"""Video file handler with format conversion capabilities.

This module provides comprehensive video file handling including reading, writing,
and conversion between various video formats using minimal dependencies.
"""
import os
import subprocess
import json
from typing import Any, Dict, List
from novus_pytils.models.models import BaseFileHandler, FileManagerMixin
from novus_pytils.exceptions import ConversionError
from novus_pytils.globals import SUPPORTED_VIDEO_EXTENSIONS, VIDEO_CONVERSION_MAP


class FFmpegWrapper:
    """Wrapper class to isolate FFmpeg dependency."""
    
    def __init__(self):
        self._ffmpeg_available = False
        self._ffprobe_available = False
        
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            self._ffmpeg_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        try:
            subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
            self._ffprobe_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    @property
    def available(self) -> bool:
        return self._ffmpeg_available
    
    @property
    def probe_available(self) -> bool:
        return self._ffprobe_available
    
    def run_ffmpeg(self, args: List[str]) -> subprocess.CompletedProcess:
        if not self._ffmpeg_available:
            raise ConversionError("FFmpeg is required for video operations. Please install FFmpeg.")
        return subprocess.run(['ffmpeg'] + args, capture_output=True, text=True)
    
    def run_ffprobe(self, args: List[str]) -> subprocess.CompletedProcess:
        if not self._ffprobe_available:
            raise ConversionError("FFprobe is required for video metadata. Please install FFmpeg.")
        return subprocess.run(['ffprobe'] + args, capture_output=True, text=True)


class VideoHandler(BaseFileHandler, FileManagerMixin):
    """Handler for video files with conversion capabilities."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = SUPPORTED_VIDEO_EXTENSIONS
        self.conversion_map = VIDEO_CONVERSION_MAP
        self.ffmpeg_wrapper = FFmpegWrapper()
    
    def read(self, file_path: str) -> Dict[str, Any]:
        """Read video file metadata and information."""
        if not self.validate_file(file_path):
            raise ConversionError(f"Unsupported file format: {file_path}")
        
        return self.get_video_info(file_path)
    
    def write(self, file_path: str, content: Any, **kwargs) -> bool:
        """Create empty video file or copy from content."""
        try:
            os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
            
            if isinstance(content, str) and os.path.exists(content):
                return self.copy(content, file_path)
            elif isinstance(content, dict) and 'source' in content:
                return self.copy(content['source'], file_path)
            else:
                raise ConversionError("Video write requires source file path")
        
        except Exception as e:
            raise ConversionError(f"Failed to write video {file_path}: {str(e)}")
    
    def convert(self, input_path: str, output_path: str, target_format: str, **kwargs) -> bool:
        """Convert video from one format to another."""
        if not self.validate_file(input_path):
            raise ConversionError(f"Unsupported input file format: {input_path}")
        
        input_ext = os.path.splitext(input_path)[1].lower()
        target_ext = target_format if target_format.startswith('.') else f'.{target_format}'
        
        if target_ext not in self.get_supported_conversions(input_ext):
            raise ConversionError(f"Cannot convert from {input_ext} to {target_ext}")
        
        if not self.ffmpeg_wrapper.available:
            raise ConversionError("FFmpeg is required for video conversion")
        
        try:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            args = ['-i', input_path]
            
            if kwargs.get('video_codec'):
                args.extend(['-c:v', kwargs['video_codec']])
            elif target_ext == '.mp4':
                args.extend(['-c:v', 'libx264'])
            elif target_ext == '.webm':
                args.extend(['-c:v', 'libvpx-vp9'])
            
            if kwargs.get('audio_codec'):
                args.extend(['-c:a', kwargs['audio_codec']])
            elif target_ext == '.mp4':
                args.extend(['-c:a', 'aac'])
            elif target_ext == '.webm':
                args.extend(['-c:a', 'libopus'])
            
            if kwargs.get('quality'):
                args.extend(['-crf', str(kwargs['quality'])])
            
            if kwargs.get('bitrate'):
                args.extend(['-b:v', kwargs['bitrate']])
            
            if kwargs.get('audio_bitrate'):
                args.extend(['-b:a', kwargs['audio_bitrate']])
            
            if kwargs.get('resolution'):
                args.extend(['-s', kwargs['resolution']])
            
            if kwargs.get('fps'):
                args.extend(['-r', str(kwargs['fps'])])
            
            args.extend(['-y', output_path])
            
            result = self.ffmpeg_wrapper.run_ffmpeg(args)
            
            if result.returncode != 0:
                raise ConversionError(f"FFmpeg error: {result.stderr}")
            
            return os.path.exists(output_path)
        
        except Exception as e:
            raise ConversionError(f"Conversion failed from {input_path} to {output_path}: {str(e)}")
    
    def trim(self, input_path: str, output_path: str, start_time: str, duration: str = None, end_time: str = None, **kwargs) -> bool:
        """Trim video to specified time range."""
        if not self.ffmpeg_wrapper.available:
            raise ConversionError("FFmpeg is required for video trimming")
        
        try:
            args = ['-i', input_path, '-ss', start_time]
            
            if duration:
                args.extend(['-t', duration])
            elif end_time:
                args.extend(['-to', end_time])
            
            args.extend(['-c', 'copy', '-y', output_path])
            
            result = self.ffmpeg_wrapper.run_ffmpeg(args)
            
            if result.returncode != 0:
                raise ConversionError(f"FFmpeg error: {result.stderr}")
            
            return os.path.exists(output_path)
        
        except Exception as e:
            raise ConversionError(f"Failed to trim video: {str(e)}")
    
    def concatenate(self, input_paths: List[str], output_path: str, **kwargs) -> bool:
        """Concatenate multiple video files."""
        if not self.ffmpeg_wrapper.available:
            raise ConversionError("FFmpeg is required for video concatenation")
        
        if len(input_paths) < 2:
            raise ConversionError("At least 2 video files required for concatenation")
        
        try:
            concat_file = f"{output_path}.concat"
            
            with open(concat_file, 'w') as f:
                for path in input_paths:
                    f.write(f"file '{os.path.abspath(path)}'\n")
            
            args = ['-f', 'concat', '-safe', '0', '-i', concat_file, '-c', 'copy', '-y', output_path]
            
            result = self.ffmpeg_wrapper.run_ffmpeg(args)
            
            os.remove(concat_file)
            
            if result.returncode != 0:
                raise ConversionError(f"FFmpeg error: {result.stderr}")
            
            return os.path.exists(output_path)
        
        except Exception as e:
            if os.path.exists(concat_file):
                os.remove(concat_file)
            raise ConversionError(f"Failed to concatenate videos: {str(e)}")
    
    def extract_audio(self, input_path: str, output_path: str, **kwargs) -> bool:
        """Extract audio from video file."""
        if not self.ffmpeg_wrapper.available:
            raise ConversionError("FFmpeg is required for audio extraction")
        
        try:
            args = ['-i', input_path, '-vn']
            
            if kwargs.get('audio_codec'):
                args.extend(['-c:a', kwargs['audio_codec']])
            
            if kwargs.get('audio_bitrate'):
                args.extend(['-b:a', kwargs['audio_bitrate']])
            
            args.extend(['-y', output_path])
            
            result = self.ffmpeg_wrapper.run_ffmpeg(args)
            
            if result.returncode != 0:
                raise ConversionError(f"FFmpeg error: {result.stderr}")
            
            return os.path.exists(output_path)
        
        except Exception as e:
            raise ConversionError(f"Failed to extract audio: {str(e)}")
    
    def extract_frames(self, input_path: str, output_dir: str, fps: float = 1.0, **kwargs) -> List[str]:
        """Extract frames from video as images."""
        if not self.ffmpeg_wrapper.available:
            raise ConversionError("FFmpeg is required for frame extraction")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_pattern = os.path.join(output_dir, f"{base_name}_frame_%04d.png")
            
            args = ['-i', input_path, '-vf', f'fps={fps}', '-y', output_pattern]
            
            result = self.ffmpeg_wrapper.run_ffmpeg(args)
            
            if result.returncode != 0:
                raise ConversionError(f"FFmpeg error: {result.stderr}")
            
            frame_files = []
            for file in os.listdir(output_dir):
                if file.startswith(f"{base_name}_frame_") and file.endswith('.png'):
                    frame_files.append(os.path.join(output_dir, file))
            
            return sorted(frame_files)
        
        except Exception as e:
            raise ConversionError(f"Failed to extract frames: {str(e)}")
    
    def add_watermark(self, input_path: str, output_path: str, watermark_path: str, position: str = 'bottom-right', **kwargs) -> bool:
        """Add watermark to video."""
        if not self.ffmpeg_wrapper.available:
            raise ConversionError("FFmpeg is required for watermarking")
        
        position_map = {
            'top-left': '10:10',
            'top-right': 'main_w-overlay_w-10:10',
            'bottom-left': '10:main_h-overlay_h-10',
            'bottom-right': 'main_w-overlay_w-10:main_h-overlay_h-10',
            'center': '(main_w-overlay_w)/2:(main_h-overlay_h)/2'
        }
        
        try:
            pos = position_map.get(position, position_map['bottom-right'])
            
            args = ['-i', input_path, '-i', watermark_path, 
                   '-filter_complex', f'overlay={pos}', 
                   '-y', output_path]
            
            result = self.ffmpeg_wrapper.run_ffmpeg(args)
            
            if result.returncode != 0:
                raise ConversionError(f"FFmpeg error: {result.stderr}")
            
            return os.path.exists(output_path)
        
        except Exception as e:
            raise ConversionError(f"Failed to add watermark: {str(e)}")
    
    def resize_video(self, input_path: str, output_path: str, width: int, height: int, **kwargs) -> bool:
        """Resize video to specified dimensions."""
        if not self.ffmpeg_wrapper.available:
            raise ConversionError("FFmpeg is required for video resizing")
        
        try:
            args = ['-i', input_path, '-vf', f'scale={width}:{height}', '-y', output_path]
            
            result = self.ffmpeg_wrapper.run_ffmpeg(args)
            
            if result.returncode != 0:
                raise ConversionError(f"FFmpeg error: {result.stderr}")
            
            return os.path.exists(output_path)
        
        except Exception as e:
            raise ConversionError(f"Failed to resize video: {str(e)}")
    
    def get_video_info(self, file_path: str) -> Dict[str, Any]:
        """Get video metadata and information."""
        base_info = self.get_metadata(file_path)
        
        if not self.ffmpeg_wrapper.probe_available:
            return base_info
        
        try:
            args = ['-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path]
            result = self.ffmpeg_wrapper.run_ffprobe(args)
            
            if result.returncode == 0:
                probe_data = json.loads(result.stdout)
                
                format_info = probe_data.get('format', {})
                base_info.update({
                    'duration': float(format_info.get('duration', 0)),
                    'bitrate': int(format_info.get('bit_rate', 0)),
                    'format_name': format_info.get('format_name', ''),
                    'format_long_name': format_info.get('format_long_name', '')
                })
                
                for stream in probe_data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        base_info.update({
                            'width': stream.get('width'),
                            'height': stream.get('height'),
                            'video_codec': stream.get('codec_name'),
                            'video_codec_long': stream.get('codec_long_name'),
                            'fps': eval(stream.get('avg_frame_rate', '0/1')),
                            'video_bitrate': stream.get('bit_rate'),
                            'pixel_format': stream.get('pix_fmt')
                        })
                    elif stream.get('codec_type') == 'audio':
                        base_info.update({
                            'audio_codec': stream.get('codec_name'),
                            'audio_codec_long': stream.get('codec_long_name'),
                            'sample_rate': stream.get('sample_rate'),
                            'channels': stream.get('channels'),
                            'audio_bitrate': stream.get('bit_rate')
                        })
        except Exception:
            pass
        
        return base_info
    
    def create_thumbnail(self, input_path: str, output_path: str, time_position: str = '00:00:01', **kwargs) -> bool:
        """Create thumbnail image from video at specified time."""
        if not self.ffmpeg_wrapper.available:
            raise ConversionError("FFmpeg is required for thumbnail creation")
        
        try:
            args = ['-i', input_path, '-ss', time_position, '-vframes', '1', '-y', output_path]
            
            result = self.ffmpeg_wrapper.run_ffmpeg(args)
            
            if result.returncode != 0:
                raise ConversionError(f"FFmpeg error: {result.stderr}")
            
            return os.path.exists(output_path)
        
        except Exception as e:
            raise ConversionError(f"Failed to create thumbnail: {str(e)}")
    
    def apply_filter(self, input_path: str, output_path: str, filter_name: str, **kwargs) -> bool:
        """Apply video filter."""
        if not self.ffmpeg_wrapper.available:
            raise ConversionError("FFmpeg is required for video filtering")
        
        filter_map = {
            'blur': 'boxblur=5:1',
            'brightness': f"eq=brightness={kwargs.get('value', 0.1)}",
            'contrast': f"eq=contrast={kwargs.get('value', 1.2)}",
            'saturation': f"eq=saturation={kwargs.get('value', 1.2)}",
            'grayscale': 'colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3',
            'flip_horizontal': 'hflip',
            'flip_vertical': 'vflip',
            'rotate_90': 'transpose=1',
            'rotate_180': 'transpose=2,transpose=2',
            'rotate_270': 'transpose=2'
        }
        
        if filter_name not in filter_map:
            raise ConversionError(f"Unsupported filter: {filter_name}")
        
        try:
            args = ['-i', input_path, '-vf', filter_map[filter_name], '-y', output_path]
            
            result = self.ffmpeg_wrapper.run_ffmpeg(args)
            
            if result.returncode != 0:
                raise ConversionError(f"FFmpeg error: {result.stderr}")
            
            return os.path.exists(output_path)
        
        except Exception as e:
            raise ConversionError(f"Failed to apply filter: {str(e)}")
    
    def merge_audio_video(self, video_path: str, audio_path: str, output_path: str, **kwargs) -> bool:
        """Merge separate audio and video files."""
        if not self.ffmpeg_wrapper.available:
            raise ConversionError("FFmpeg is required for audio/video merging")
        
        try:
            args = ['-i', video_path, '-i', audio_path, '-c:v', 'copy', '-c:a', 'aac', '-y', output_path]
            
            result = self.ffmpeg_wrapper.run_ffmpeg(args)
            
            if result.returncode != 0:
                raise ConversionError(f"FFmpeg error: {result.stderr}")
            
            return os.path.exists(output_path)
        
        except Exception as e:
            raise ConversionError(f"Failed to merge audio and video: {str(e)}")