from django.db import transaction
from django.shortcuts import render

from .forms import StencilForm
from .models import ImageTransformationLog, ImageTransformationStats
from .services.stencil import StencilProcessingError, data_url_to_bytes, make_stencil


def transform_image(request):
    result = None
    source_data = ""
    source_name = ""

    if request.method == "POST":
        form = StencilForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.cleaned_data.get("image")
            image_name = _get_image_name(uploaded_image, form.cleaned_data.get("source_name"))

            try:
                if uploaded_image:
                    image_bytes = uploaded_image.read()
                else:
                    image_bytes = data_url_to_bytes(form.cleaned_data["source_data"])

                result = make_stencil(image_bytes, form.get_settings())
                source_data = result.original_data_url
                source_name = image_name
                with transaction.atomic():
                    ImageTransformationLog.objects.create(
                        image_name=image_name,
                        status=ImageTransformationLog.Status.SUCCESS,
                    )
                    ImageTransformationStats.increment_successful_transformations()
            except StencilProcessingError:
                ImageTransformationLog.objects.create(
                    image_name=image_name,
                    status=ImageTransformationLog.Status.ERROR,
                    error_message="Impossible de traiter cette image.",
                )
                form.add_error("image", "Impossible de traiter cette image.")
    else:
        form = StencilForm()

    return render(
        request,
        "images/transform.html",
        {
            "form": form,
            "result": result,
            "source_data": source_data,
            "source_name": source_name,
        },
    )


def _get_image_name(uploaded_image, source_name: str | None) -> str:
    if uploaded_image:
        return uploaded_image.name

    if source_name:
        return source_name

    return "Image sans nom"
