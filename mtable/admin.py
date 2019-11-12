from django.contrib import admin
from mtable import models
# Register your models here.
class yxlrAdmin(admin.ModelAdmin):
    list_display = ('s_date', 's_nameId', 's_title', 's_url','s_count','s_comment','s_gaizhang','s_device')

admin.site.register(models.yxlr,yxlrAdmin)