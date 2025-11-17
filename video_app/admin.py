from django.contrib import admin
from .models import Video
# Register your models here.
admin.site.register(Video)

class VideoAdmin(admin.ModelAdmin):
    # readonly_fields = ('thumbnail',)
    exclude = ('thumbnail_url',)