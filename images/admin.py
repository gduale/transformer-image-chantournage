from django.contrib import admin

from .models import ImageTransformationLog, ImageTransformationStats


@admin.register(ImageTransformationLog)
class ImageTransformationLogAdmin(admin.ModelAdmin):
    list_display = ("image_name", "transformed_at", "status", "error_message")
    list_filter = ("status", "transformed_at")
    search_fields = ("image_name", "error_message")
    readonly_fields = ("image_name", "transformed_at", "status", "error_message")
    date_hierarchy = "transformed_at"
    ordering = ("-transformed_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ImageTransformationStats)
class ImageTransformationStatsAdmin(admin.ModelAdmin):
    list_display = ("successful_transformations", "updated_at")
    readonly_fields = ("successful_transformations", "updated_at")

    def has_add_permission(self, request):
        return not ImageTransformationStats.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
