# _*_ encoding: utf-8__*_
import calendar
import datetime
from functools import reduce

from captcha.fields import CaptchaField
from django import forms
from mtable import models


def list_dict_duplicate_removal(data_list):
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + data_list)


def get_data_list():
    com_list = []
    now = datetime.datetime.now()
    for i in range(2017, now.year + 1):
        if i == now.year:
            for j in range(1, now.month + 1):
                flaglist = calendar.monthrange(i, j)
                data = str(i) + '-' + str(j) + '-' + str(flaglist[1])
                com_list.append([data, data])
        elif i == 2017:
            for j in range(10, now.month + 1):
                flaglist = calendar.monthrange(i, j)
                data = str(i) + '-' + str(j) + '-' + str(flaglist[1])
                com_list.append([data, data])
        else:
            for j in range(1, 13):
                flaglist = calendar.monthrange(i, j)
                data = str(i) + '-' + str(j) + '-' + str(flaglist[1])
                com_list.append([data, data])
    return com_list


class ExportExcelForm(forms.Form):
    s_file = forms.FileField(label='选择链接文件数据')
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super(ExportExcelForm, self).__init__(*args, **kwargs)
        self.fields['s_file'].required = False
        self.fields['captcha'].label = '验证码'


class QueryForm(forms.Form):
    year_list = [
        ['不选', '不选'],
        ['2017', '2017'],
        ['2018', '2018'],
        ['2019', '2019'],
    ]
    month_list = [
        ['不选', '不选'],
        ['1', '1'], ['2', '2'], ['3', '3'],
        ['4', '4'], ['5', '5'], ['6', '6'],
        ['7', '7'], ['8', '8'], ['9', '9'],
        ['10', '10'], ['11', '11'], ['12', '12'],
    ]
    s_title = forms.CharField(label='标题', max_length=255)
    s_nameId = forms.CharField(label='昵称', max_length=150)
    s_device = forms.CharField(label='设备', max_length=150)
    s_year = forms.ChoiceField(label='年', choices=year_list)
    s_month = forms.ChoiceField(label='月', choices=month_list)

    def __init__(self, *args, **kwargs):
        super(QueryForm, self).__init__(*args, **kwargs)
        self.fields['s_title'].required = False
        self.fields['s_nameId'].required = False
        self.fields['s_device'].required = False
        self.fields['s_year'].required = False
        self.fields['s_month'].required = False


class PieForm(forms.Form):
    CONTENT = [
        ['s_nameId', '用户组输出内容占比图'],
        ['s_device', '各板块内容占比图'],
    ]
    s_checkbox = forms.ChoiceField(label='选择导出百分比图类型', choices=CONTENT)
    com_list = get_data_list()
    s_date = forms.ChoiceField(label='选择导出月份', choices=com_list)

    def __init__(self, *args, **kwargs):
        super(PieForm, self).__init__(*args, **kwargs)
        self.fields['s_checkbox'].required = False
        self.fields['s_date'].required = False


class plotForm(forms.Form):
    CONTENT = [
        ['s_one', '每月发帖量走势图'],
        ['s_two', '每月总浏览量走势图'],
        ['s_three', '每月总评论量走势图'],
        ['s_four', '每月单帖最高浏览量柱形图'],
        ['s_five', '每月单帖最高评论量柱形图'],
    ]
    list = [i[0] for i in models.yxlr.objects.distinct().values_list('s_nameId')]
    name_list = []
    for dict in list:
        flaglist = []
        flaglist.append(dict)
        flaglist.append(dict)
        name_list.append(flaglist)
    s_checkbox = forms.ChoiceField(label='选择走势图类型', choices=CONTENT)
    s_name = forms.ChoiceField(label='选择导出月份', choices=name_list)

    def __init__(self, *args, **kwargs):
        super(plotForm, self).__init__(*args, **kwargs)
        self.fields['s_checkbox'].required = False
        self.fields['s_name'].required = False


'''
class QueryForm(forms.ModelForm):
    class Meta:
        model = models.yxlr
        fields = ['s_date', 's_nameId', 's_title', 's_url', 's_count', 's_comment', 's_gaizhang', 's_device']
'''
