# _*_ encoding: utf-8__*_
from django.db import models


# Create your models here.
class yxlr(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='索引')
    s_date = models.CharField(max_length=100, verbose_name='发布时间')
    s_nameId = models.CharField(max_length=50, verbose_name='昵称')
    s_title = models.CharField(max_length=255, verbose_name='标题')
    s_url = models.CharField(max_length=255, verbose_name='链接')
    s_count = models.PositiveIntegerField(default=0, verbose_name='阅读量')
    s_comment = models.PositiveIntegerField(default=0, verbose_name='评论量')
    s_gaizhang = models.CharField(max_length=20, verbose_name='盖章')
    s_device = models.CharField(max_length=150, verbose_name='设备')


class fileModel(models.Model):
    file_name = models.CharField(max_length=30)
    file_path = models.FileField(upload_to='./upload/')
