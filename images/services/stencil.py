import base64
from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError


MAX_PROCESSING_SIDE = 1800
PNG_MIME_TYPE = "image/png"


@dataclass(frozen=True)
class StencilSettings:
    brightness: int = 0
    contrast: int = 25
    threshold: int = 130
    detail: int = 45
    denoise: int = 50
    invert: bool = False


@dataclass(frozen=True)
class StencilResult:
    original_png: bytes
    stencil_png: bytes
    width: int
    height: int

    @property
    def original_data_url(self) -> str:
        return bytes_to_data_url(self.original_png)

    @property
    def stencil_data_url(self) -> str:
        return bytes_to_data_url(self.stencil_png)


class StencilProcessingError(ValueError):
    pass


def bytes_to_data_url(image_bytes: bytes, mime_type: str = PNG_MIME_TYPE) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def data_url_to_bytes(data_url: str) -> bytes:
    if not data_url.startswith("data:image/"):
        raise StencilProcessingError("Invalid image data.")

    try:
        header, encoded = data_url.split(",", 1)
    except ValueError as exc:
        raise StencilProcessingError("Invalid image data.") from exc

    if ";base64" not in header:
        raise StencilProcessingError("Invalid image encoding.")

    try:
        return base64.b64decode(encoded, validate=True)
    except ValueError as exc:
        raise StencilProcessingError("Invalid image encoding.") from exc


def make_stencil(image_bytes: bytes, settings: StencilSettings) -> StencilResult:
    image = _load_image(image_bytes)
    image = _resize_for_processing(image)
    original_png = _save_png(image)

    grayscale = ImageOps.grayscale(image)
    grayscale = _adjust_tone(grayscale, settings)
    grayscale = _apply_detail(grayscale, settings.detail)
    grayscale = _apply_denoise(grayscale, settings.denoise)

    stencil = _threshold(grayscale, settings.threshold)
    stencil = _clean_artifacts(stencil, settings.denoise)

    if settings.invert:
        stencil = ImageOps.invert(stencil.convert("L")).convert("1")

    stencil_png = _save_png(stencil.convert("L"))

    return StencilResult(
        original_png=original_png,
        stencil_png=stencil_png,
        width=image.width,
        height=image.height,
    )


def _load_image(image_bytes: bytes) -> Image.Image:
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image = ImageOps.exif_transpose(image)
            return image.convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise StencilProcessingError("The uploaded file is not a valid image.") from exc


def _resize_for_processing(image: Image.Image) -> Image.Image:
    if max(image.size) <= MAX_PROCESSING_SIDE:
        return image.copy()

    resized = image.copy()
    resized.thumbnail((MAX_PROCESSING_SIDE, MAX_PROCESSING_SIDE), Image.Resampling.LANCZOS)
    return resized


def _save_png(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _adjust_tone(image: Image.Image, settings: StencilSettings) -> Image.Image:
    brightness_factor = max(0.1, 1 + settings.brightness / 100)
    contrast_factor = max(0.1, 1 + settings.contrast / 100)
    image = ImageEnhance.Brightness(image).enhance(brightness_factor)
    return ImageEnhance.Contrast(image).enhance(contrast_factor)


def _apply_detail(image: Image.Image, detail: int) -> Image.Image:
    if detail <= 0:
        return image.filter(ImageFilter.GaussianBlur(radius=0.8))

    percent = 40 + detail * 3
    radius = 1 + detail / 100
    return image.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=3))


def _apply_denoise(image: Image.Image, denoise: int) -> Image.Image:
    if denoise <= 0:
        return image

    radius = denoise / 45
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


def _threshold(image: Image.Image, threshold: int) -> Image.Image:
    threshold = min(255, max(0, threshold))
    return image.point(lambda pixel: 255 if pixel >= threshold else 0, mode="1")


def _clean_artifacts(image: Image.Image, denoise: int) -> Image.Image:
    if denoise < 25:
        return image

    size = 3 if denoise < 70 else 5
    return image.convert("L").filter(ImageFilter.MedianFilter(size=size)).convert("1")
