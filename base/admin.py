from django.contrib import admin
from .models import CustomUser
from .models import UserSubscription
from .models import Advertisement
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserSubscription)
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_url')  # ✅ Show in admin list
    fields = ('title', 'description', 'image_url', 'target_url')  # ✅ Explicitly define form fields
