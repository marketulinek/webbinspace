from django.contrib import admin
from django.contrib.auth.models import User,Group
from .models import Report,Category,Visit


class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ['username']

class ReportAdmin(admin.ModelAdmin):
    model = Report
    list_display = ['__str__', 'created_at']
    readonly_fields = ['created_at']
    list_filter = ['cycle']

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Category)
admin.site.register(Visit)