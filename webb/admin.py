from django.contrib import admin
from django.contrib.auth.models import User,Group
from .models import Report,Category,Visit


class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ['username']

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Report)
admin.site.register(Category)
admin.site.register(Visit)