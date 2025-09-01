from pydub import AudioSegment
from pathlib import Path
from typing import Optional, Union


class PydubWrapper:
    """A wrapper class for pydub to handle audio format conversions."""
    
    def __init__(self, audio_file: Union[str, Path]):
        """Initialize the wrapper with an audio file.
        
        Args:
            audio_file (Union[str, Path]): Path to the audio file.
        """
        self.audio_file = Path(audio_file)
        self._audio_segment = None
    
    @property
    def audio_segment(self) -> AudioSegment:
        """Lazy load the audio segment."""
        if self._audio_segment is None:
            self._audio_segment = AudioSegment.from_file(str(self.audio_file))
        return self._audio_segment
    
    def convert_to_format(
        self, 
        output_file: Union[str, Path], 
        format: str, 
        bitrate: Optional[str] = None, 
        channels: Optional[int] = None
    ) -> None:
        """Convert audio to specified format.
        
        Args:
            output_file (Union[str, Path]): Path for the output file.
            format (str): Target audio format (e.g., 'mp3', 'wav', 'aac').
            bitrate (Optional[str]): Bitrate for the output file (e.g., '192k').
            channels (Optional[int]): Number of channels for the output file.
        """
        audio = self.audio_segment
        
        if channels:
            audio = audio.set_channels(channels)
        
        export_params = {"format": format}
        if bitrate and format not in ["wav", "flac"]:
            export_params["bitrate"] = bitrate
        
        audio.export(str(output_file), **export_params)
    
    def to_mp3(
        self, 
        output_file: Union[str, Path], 
        bitrate: str = "192k", 
        channels: Optional[int] = None
    ) -> None:
        """Convert audio to MP3 format.
        
        Args:
            output_file (Union[str, Path]): Path for the output MP3 file.
            bitrate (str): Bitrate for the output file (default: "192k").
            channels (Optional[int]): Number of channels for the output file.
        """
        self.convert_to_format(output_file, "mp3", bitrate, channels)
    
    def to_wav(
        self, 
        output_file: Union[str, Path], 
        channels: Optional[int] = None
    ) -> None:
        """Convert audio to WAV format.
        
        Args:
            output_file (Union[str, Path]): Path for the output WAV file.
            channels (Optional[int]): Number of channels for the output file.
        """
        self.convert_to_format(output_file, "wav", None, channels)
    
    def to_aac(
        self, 
        output_file: Union[str, Path], 
        bitrate: str = "192k", 
        channels: Optional[int] = None
    ) -> None:
        """Convert audio to AAC format.
        
        Args:
            output_file (Union[str, Path]): Path for the output AAC file.
            bitrate (str): Bitrate for the output file (default: "192k").
            channels (Optional[int]): Number of channels for the output file.
        """
        self.convert_to_format(output_file, "aac", bitrate, channels)
    
    def to_m4a(
        self, 
        output_file: Union[str, Path], 
        bitrate: str = "192k", 
        channels: Optional[int] = None
    ) -> None:
        """Convert audio to M4A format.
        
        Args:
            output_file (Union[str, Path]): Path for the output M4A file.
            bitrate (str): Bitrate for the output file (default: "192k").
            channels (Optional[int]): Number of channels for the output file.
        """
        self.convert_to_format(output_file, "ipod", bitrate, channels)
    
    def to_flac(
        self, 
        output_file: Union[str, Path], 
        channels: Optional[int] = None
    ) -> None:
        """Convert audio to FLAC format.
        
        Args:
            output_file (Union[str, Path]): Path for the output FLAC file.
            channels (Optional[int]): Number of channels for the output file.
        """
        self.convert_to_format(output_file, "flac", None, channels)
    
    def to_ogg(
        self, 
        output_file: Union[str, Path], 
        bitrate: str = "192k", 
        channels: Optional[int] = None
    ) -> None:
        """Convert audio to OGG format.
        
        Args:
            output_file (Union[str, Path]): Path for the output OGG file.
            bitrate (str): Bitrate for the output file (default: "192k").
            channels (Optional[int]): Number of channels for the output file.
        """
        self.convert_to_format(output_file, "ogg", bitrate, channels)
    
    def to_wma(
        self, 
        output_file: Union[str, Path], 
        bitrate: str = "192k", 
        channels: Optional[int] = None
    ) -> None:
        """Convert audio to WMA format.
        
        Args:
            output_file (Union[str, Path]): Path for the output WMA file.
            bitrate (str): Bitrate for the output file (default: "192k").
            channels (Optional[int]): Number of channels for the output file.
        """
        self.convert_to_format(output_file, "wma", bitrate, channels)
    
    def get_duration_ms(self) -> float:
        """Get the duration of the audio in milliseconds.
        
        Returns:
            float: Duration in milliseconds.
        """
        return len(self.audio_segment)
    
    def get_frame_rate(self) -> int:
        """Get the frame rate of the audio.
        
        Returns:
            int: Frame rate in Hz.
        """
        return self.audio_segment.frame_rate
    
    def get_channels(self) -> int:
        """Get the number of channels in the audio.
        
        Returns:
            int: Number of channels.
        """
        return self.audio_segment.channels
    
    def get_sample_width(self) -> int:
        """Get the sample width of the audio.
        
        Returns:
            int: Sample width in bytes.
        """
        return self.audio_segment.sample_width