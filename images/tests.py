from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .services.stencil import (
    StencilSettings,
    data_url_to_bytes,
    make_stencil,
)


def create_test_image(size=(120, 80), color=(220, 220, 220)):
    image = Image.new("RGB", size, color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def create_jpeg_test_image(size=(120, 80), color=(220, 220, 220)):
    image = Image.new("RGB", size, color)
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


class StencilServiceTests(TestCase):
    def test_make_stencil_returns_png_images(self):
        image_bytes = create_test_image()
        result = make_stencil(image_bytes, StencilSettings())

        self.assertEqual(result.width, 120)
        self.assertEqual(result.height, 80)
        self.assertTrue(result.original_png.startswith(b"\x89PNG"))
        self.assertTrue(result.stencil_png.startswith(b"\x89PNG"))

    def test_threshold_changes_output(self):
        image_bytes = create_test_image(color=(140, 140, 140))

        low_threshold = make_stencil(image_bytes, StencilSettings(threshold=80))
        high_threshold = make_stencil(image_bytes, StencilSettings(threshold=200))

        self.assertNotEqual(low_threshold.stencil_png, high_threshold.stencil_png)

    def test_data_url_round_trip(self):
        image_bytes = create_test_image()
        result = make_stencil(image_bytes, StencilSettings())

        self.assertEqual(data_url_to_bytes(result.original_data_url), result.original_png)


class TransformImageViewTests(TestCase):
    def test_get_page(self):
        response = self.client.get(reverse("images:transform"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Transform Image")

    def test_post_valid_image_displays_result(self):
        upload = SimpleUploadedFile(
            "test.png",
            create_test_image(),
            content_type="image/png",
        )

        response = self.client.post(
            reverse("images:transform"),
            {
                "image": upload,
                "brightness": 0,
                "contrast": 25,
                "threshold": 130,
                "detail": 45,
                "denoise": 20,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Télécharger")
        self.assertContains(response, "data:image/png;base64")

    def test_post_jpg_image_displays_result(self):
        upload = SimpleUploadedFile(
            "test.jpg",
            create_jpeg_test_image(),
            content_type="image/jpeg",
        )

        response = self.client.post(
            reverse("images:transform"),
            {
                "image": upload,
                "brightness": 0,
                "contrast": 25,
                "threshold": 130,
                "detail": 45,
                "denoise": 20,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Télécharger")
        self.assertContains(response, "data:image/png;base64")

    def test_post_jpg_image_with_image_jpg_mime_displays_result(self):
        upload = SimpleUploadedFile(
            "test.jpg",
            create_jpeg_test_image(),
            content_type="image/jpg",
        )

        response = self.client.post(
            reverse("images:transform"),
            {
                "image": upload,
                "brightness": 0,
                "contrast": 25,
                "threshold": 130,
                "detail": 45,
                "denoise": 20,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Télécharger")
        self.assertContains(response, "data:image/png;base64")

    def test_post_jpg_image_with_generic_mime_displays_result(self):
        upload = SimpleUploadedFile(
            "Sans titre.jpg",
            create_jpeg_test_image(),
            content_type="application/octet-stream",
        )

        response = self.client.post(
            reverse("images:transform"),
            {
                "image": upload,
                "brightness": 0,
                "contrast": 25,
                "threshold": 130,
                "detail": 45,
                "denoise": 20,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Télécharger")
        self.assertContains(response, "data:image/png;base64")

    def test_invalid_upload_does_not_show_missing_image_error(self):
        upload = SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain",
        )

        response = self.client.post(
            reverse("images:transform"),
            {
                "image": upload,
                "brightness": 0,
                "contrast": 25,
                "threshold": 130,
                "detail": 45,
                "denoise": 20,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Ajoutez une image pour lancer la transformation.")
