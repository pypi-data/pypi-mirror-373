from PIL import Image, ImageOps
from pathlib import Path
from typing import Optional, Union, Tuple


class PillowWrapper:
    """A wrapper class for Pillow to handle image format conversions and operations."""
    
    def __init__(self, image_file: Union[str, Path]):
        """Initialize the wrapper with an image file.
        
        Args:
            image_file (Union[str, Path]): Path to the image file.
        """
        self.image_file = Path(image_file)
        self._image = None
    
    @property
    def image(self) -> Image.Image:
        """Lazy load the PIL Image object."""
        if self._image is None:
            self._image = Image.open(str(self.image_file))
        return self._image
    
    def convert_to_format(
        self, 
        output_file: Union[str, Path], 
        format: str, 
        quality: Optional[int] = None,
        optimize: bool = False,
        **kwargs
    ) -> None:
        """Convert image to specified format.
        
        Args:
            output_file (Union[str, Path]): Path for the output file.
            format (str): Target image format (e.g., 'JPEG', 'PNG', 'WEBP').
            quality (Optional[int]): Quality for lossy formats (1-100, higher is better).
            optimize (bool): Whether to optimize the output file.
            **kwargs: Additional format-specific parameters.
        """
        img = self.image.copy()
        
        # Handle transparency for formats that don't support it
        if format.upper() in ['JPEG', 'BMP'] and img.mode in ['RGBA', 'LA']:
            # Create a white background for transparency
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        
        # Prepare save parameters
        save_params = {"format": format.upper(), "optimize": optimize}
        if quality is not None and format.upper() in ['JPEG', 'WEBP']:
            save_params["quality"] = quality
        save_params.update(kwargs)
        
        img.save(str(output_file), **save_params)
    
    def to_jpeg(
        self, 
        output_file: Union[str, Path], 
        quality: int = 95,
        optimize: bool = True
    ) -> None:
        """Convert image to JPEG format.
        
        Args:
            output_file (Union[str, Path]): Path for the output JPEG file.
            quality (int): JPEG quality (1-100, default: 95).
            optimize (bool): Whether to optimize the file (default: True).
        """
        self.convert_to_format(output_file, "JPEG", quality, optimize)
    
    def to_png(
        self, 
        output_file: Union[str, Path], 
        optimize: bool = True
    ) -> None:
        """Convert image to PNG format.
        
        Args:
            output_file (Union[str, Path]): Path for the output PNG file.
            optimize (bool): Whether to optimize the file (default: True).
        """
        self.convert_to_format(output_file, "PNG", optimize=optimize)
    
    def to_webp(
        self, 
        output_file: Union[str, Path], 
        quality: int = 90,
        optimize: bool = True,
        lossless: bool = False
    ) -> None:
        """Convert image to WebP format.
        
        Args:
            output_file (Union[str, Path]): Path for the output WebP file.
            quality (int): WebP quality (1-100, default: 90).
            optimize (bool): Whether to optimize the file (default: True).
            lossless (bool): Whether to use lossless compression (default: False).
        """
        if lossless:
            self.convert_to_format(output_file, "WEBP", optimize=optimize, lossless=True)
        else:
            self.convert_to_format(output_file, "WEBP", quality, optimize)
    
    def to_bmp(self, output_file: Union[str, Path]) -> None:
        """Convert image to BMP format.
        
        Args:
            output_file (Union[str, Path]): Path for the output BMP file.
        """
        self.convert_to_format(output_file, "BMP")
    
    def to_tiff(
        self, 
        output_file: Union[str, Path],
        compression: Optional[str] = None
    ) -> None:
        """Convert image to TIFF format.
        
        Args:
            output_file (Union[str, Path]): Path for the output TIFF file.
            compression (Optional[str]): Compression method ('lzw', 'jpeg', 'packbits', etc.).
        """
        kwargs = {}
        if compression:
            kwargs["compression"] = compression
        self.convert_to_format(output_file, "TIFF", **kwargs)
    
    def to_gif(self, output_file: Union[str, Path]) -> None:
        """Convert image to GIF format.
        
        Args:
            output_file (Union[str, Path]): Path for the output GIF file.
        """
        # Convert to palette mode for GIF
        img = self.image.copy()
        if img.mode not in ['P', 'L']:
            img = img.convert('P', palette=Image.ADAPTIVE)
        img.save(str(output_file), format="GIF")
    
    def to_ico(self, output_file: Union[str, Path], sizes: Optional[list] = None) -> None:
        """Convert image to ICO format.
        
        Args:
            output_file (Union[str, Path]): Path for the output ICO file.
            sizes (Optional[list]): List of sizes for multi-resolution ICO (e.g., [(16,16), (32,32)]).
        """
        if sizes:
            # Create multi-resolution ICO
            images = []
            for size in sizes:
                img_resized = self.image.copy().resize(size, Image.Resampling.LANCZOS)
                images.append(img_resized)
            images[0].save(str(output_file), format="ICO", sizes=[(img.width, img.height) for img in images])
        else:
            self.convert_to_format(output_file, "ICO")
    
    def resize(
        self, 
        size: Tuple[int, int], 
        resample: Image.Resampling = Image.Resampling.LANCZOS
    ) -> 'PillowWrapper':
        """Resize the image.
        
        Args:
            size (Tuple[int, int]): Target size as (width, height).
            resample (Image.Resampling): Resampling algorithm.
            
        Returns:
            PillowWrapper: New wrapper with resized image.
        """
        resized_img = self.image.resize(size, resample)
        new_wrapper = PillowWrapper.__new__(PillowWrapper)
        new_wrapper.image_file = self.image_file
        new_wrapper._image = resized_img
        return new_wrapper
    
    def crop(self, box: Tuple[int, int, int, int]) -> 'PillowWrapper':
        """Crop the image.
        
        Args:
            box (Tuple[int, int, int, int]): Crop box as (left, top, right, bottom).
            
        Returns:
            PillowWrapper: New wrapper with cropped image.
        """
        cropped_img = self.image.crop(box)
        new_wrapper = PillowWrapper.__new__(PillowWrapper)
        new_wrapper.image_file = self.image_file
        new_wrapper._image = cropped_img
        return new_wrapper
    
    def rotate(self, angle: float, expand: bool = False) -> 'PillowWrapper':
        """Rotate the image.
        
        Args:
            angle (float): Rotation angle in degrees (counter-clockwise).
            expand (bool): Whether to expand the image to fit the rotated content.
            
        Returns:
            PillowWrapper: New wrapper with rotated image.
        """
        rotated_img = self.image.rotate(angle, expand=expand)
        new_wrapper = PillowWrapper.__new__(PillowWrapper)
        new_wrapper.image_file = self.image_file
        new_wrapper._image = rotated_img
        return new_wrapper
    
    def flip_horizontal(self) -> 'PillowWrapper':
        """Flip the image horizontally.
        
        Returns:
            PillowWrapper: New wrapper with flipped image.
        """
        flipped_img = self.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        new_wrapper = PillowWrapper.__new__(PillowWrapper)
        new_wrapper.image_file = self.image_file
        new_wrapper._image = flipped_img
        return new_wrapper
    
    def flip_vertical(self) -> 'PillowWrapper':
        """Flip the image vertically.
        
        Returns:
            PillowWrapper: New wrapper with flipped image.
        """
        flipped_img = self.image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        new_wrapper = PillowWrapper.__new__(PillowWrapper)
        new_wrapper.image_file = self.image_file
        new_wrapper._image = flipped_img
        return new_wrapper
    
    def get_size(self) -> Tuple[int, int]:
        """Get the image size.
        
        Returns:
            Tuple[int, int]: Image size as (width, height).
        """
        return self.image.size
    
    def get_mode(self) -> str:
        """Get the image mode.
        
        Returns:
            str: Image mode (e.g., 'RGB', 'RGBA', 'L').
        """
        return self.image.mode
    
    def get_format(self) -> Optional[str]:
        """Get the original image format.
        
        Returns:
            Optional[str]: Original image format.
        """
        return self.image.format
    
    def has_transparency(self) -> bool:
        """Check if the image has transparency.
        
        Returns:
            bool: True if the image has transparency.
        """
        return self.image.mode in ['RGBA', 'LA'] or 'transparency' in self.image.info