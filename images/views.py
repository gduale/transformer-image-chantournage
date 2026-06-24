from django.shortcuts import render

from .forms import StencilForm
from .services.stencil import StencilProcessingError, data_url_to_bytes, make_stencil


def transform_image(request):
    result = None
    source_data = ""

    if request.method == "POST":
        form = StencilForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                uploaded_image = form.cleaned_data.get("image")
                if uploaded_image:
                    image_bytes = uploaded_image.read()
                else:
                    image_bytes = data_url_to_bytes(form.cleaned_data["source_data"])

                result = make_stencil(image_bytes, form.get_settings())
                source_data = result.original_data_url
            except StencilProcessingError:
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
        },
    )
