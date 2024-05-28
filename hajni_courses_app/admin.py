from django.contrib import admin

from .models import CustomUser, Course


admin.site.register(CustomUser)
admin.site.register(Course)
