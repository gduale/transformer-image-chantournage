from django import forms

from .services.stencil import StencilSettings


MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class StencilForm(forms.Form):
    image = forms.ImageField(required=False)
    source_data = forms.CharField(required=False, widget=forms.HiddenInput)
    source_name = forms.CharField(required=False, widget=forms.HiddenInput)
    brightness = forms.IntegerField(min_value=-100, max_value=100, initial=0)
    contrast = forms.IntegerField(min_value=-100, max_value=100, initial=25)
    threshold = forms.IntegerField(min_value=0, max_value=255, initial=130)
    detail = forms.IntegerField(min_value=0, max_value=100, initial=45)
    denoise = forms.IntegerField(min_value=0, max_value=100, initial=50)
    invert = forms.BooleanField(required=False, initial=False)

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image is None:
            return image

        if image.size > MAX_IMAGE_SIZE:
            raise forms.ValidationError("L'image ne doit pas dépasser 10 Mo.")

        content_type = getattr(image, "content_type", "").lower()
        extension = _get_file_extension(image.name)
        if content_type not in ALLOWED_CONTENT_TYPES and extension not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError("Formats acceptés : JPG, JPEG, PNG ou WebP.")

        return image

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        source_data = cleaned_data.get("source_data")

        if not image and not source_data and "image" not in self.errors:
            self.add_error("image", "Ajoutez une image pour lancer la transformation.")

        return cleaned_data

    def get_settings(self) -> StencilSettings:
        return StencilSettings(
            brightness=self.cleaned_data["brightness"],
            contrast=self.cleaned_data["contrast"],
            threshold=self.cleaned_data["threshold"],
            detail=self.cleaned_data["detail"],
            denoise=self.cleaned_data["denoise"],
            invert=self.cleaned_data["invert"],
        )


def _get_file_extension(filename: str) -> str:
    if "." not in filename:
        return ""

    return f".{filename.rsplit('.', 1)[1].lower()}"
