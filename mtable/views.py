# _*_ encoding: utf-8__*_
import datetime
import os
import re
import threading
from time import sleep

import numpy as np
import path
import requests
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import FileResponse, HttpResponse
from django.shortcuts import render
from openpyxl.styles import Font

from mtable import models, forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from pandas import DataFrame
import pandas as pd
from pyquery import PyQuery as py
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as col

from mtable.ExcelHandle import ExcelHandle
from mtabledjango import settings

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['axes.unicode_minus'] = False
header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Host': 'club.huawei.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
}


def s_plot(request):
    x = []
    y = []
    df = pd.DataFrame(list(models.yxlr.objects.all().values()))
    df['s_date'] = pd.to_datetime(df['s_date'])
    df = df.set_index('s_date')
    if request.method == 'GET':
        get_form = forms.plotForm(request.GET)
        if get_form.is_valid():
            s_one = get_form.cleaned_data['s_checkbox']
            s_two = get_form.cleaned_data['s_name']
            if s_one == 's_one':
                data = df[df['s_nameId'] == s_two].resample('M').count().reset_index(drop=False)
                for index, row in data.iterrows():
                    y.append(row['s_url'])
                    x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
                plot_test(x, y, title=U'每月发帖量走势图')
            elif s_one == 's_two':
                data = df[df['s_nameId'] == s_two].resample('M').sum().reset_index(drop=False)
                for index, row in data.iterrows():
                    y.append(row['s_count'])
                    x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
                plot_test(x, y, title=U'每月总浏览量走势图')
            elif s_one == 's_three':
                data = df[df['s_nameId'] == s_two].resample('M').sum().reset_index(drop=False)
                for index, row in data.iterrows():
                    y.append(row['s_comment'])
                    x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
                plot_test(x, y, title=U'每月总评论量走势图')
            elif s_one == 's_four':
                data = df[df['s_nameId'] == s_two].resample('M')['s_count'].max().reset_index(drop=False)
                for index, row in data.iterrows():
                    if pd.isnull(row['s_count']):
                        y.append(0)
                    else:
                        y.append(row['s_count'])
                    x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
                plot_test(x, y, title=U'每月单帖最高浏览量柱形图', type=2)
            elif s_one == 's_five':
                data = df[df['s_nameId'] == s_two].resample('M')['s_comment'].max().reset_index(drop=False)
                for index, row in data.iterrows():
                    if pd.isnull(row['s_comment']):
                        y.append(0)
                    else:
                        y.append(row['s_comment'])
                    x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
                plot_test(x, y, title=U'每月单帖最高评论量柱形图', type=2)
        else:
            data = df[df['s_nameId'] == '云月静'].resample('M').count().reset_index(drop=False)
            for index, row in data.iterrows():
                y.append(row['s_url'])
                x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
            plot_test(x, y, title=U'每月发帖量走势图')
    else:
        get_form = forms.plotForm()
    return render(request, 'plot.html', locals())


def plot_test(x, y, title=U'每月发帖量走势图', xlabel=u'年份日期（年，月）', ylabel=u'数据量（个）', type=1):
    plt.figure(figsize=(12, 8))
    if type == 1:
        plt.plot(x, y, 'r', linestyle='--', marker='o')
        for i, j in zip(x, y):
            plt.annotate('%s' % (j), xy=(i, j), xytext=(0, 15), textcoords='offset points', ha='center')
        plt.grid()
        plt.title(title, fontsize='large', fontweight='bold')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tick_params(axis='x', labelsize=7, rotation=45, colors='red')
    else:
        patterns = {'-', '+', 'x', '\\', '*', 'o', '0', '.', 'v', '^', '1', '2', '3', '4', '8', 's', 'p', 'h'}
        camp1 = cm.ScalarMappable(col.Normalize(min(y), max(y) + 20), cm.hot)
        bars = plt.bar(x, y, alpha=0.5, color=camp1.to_rgba(y), edgecolor='red', label=u'柱形图')
        for bar, pattern in zip(bars, patterns):
            bar.set_hatch(pattern)
        for i, j in zip(x, y):
            plt.annotate('%s' % (j), xy=(i, j), xytext=(0, 25), textcoords='offset points', ha='center',
                         arrowprops=dict(facecolor='black', shrink=0.15), fontsize=7)
        plt.grid()
        plt.title(title, fontsize='large', fontweight='bold')
        plt.xlabel(xlabel, fontsize=15)
        plt.ylabel(ylabel, fontsize=15)
        plt.legend(loc='upper left')
        plt.tick_params(axis='x', labelsize=7, rotation=45, colors='red')
    ax = plt.gca()
    ax.patch.set_alpha(0.5)
    plt.rcParams['savefig.facecolor'] = '#6DDCBD'
    plt.rcParams['axes.facecolor'] = '#6DDCBD'
    plt.savefig('./static/pictures/two.png')
    plt.clf()


def querydata(request):
    if request.method == 'GET':
        get_form = forms.QueryForm(request.GET)
        if get_form.is_valid():
            s_title = get_form.cleaned_data['s_title']
            s_nameId = get_form.cleaned_data['s_nameId']
            s_device = get_form.cleaned_data['s_device']
            s_year = get_form.cleaned_data['s_year']
            s_month = get_form.cleaned_data['s_month']
            s_date = ''
            if '不选' != s_year and '不选' != s_month and '' != s_month:
                if int(s_month) < 10:
                    s_date = s_year + '-0' + s_month
                else:
                    s_date = s_year + '-' + s_month
            elif '不选' != s_year and '不选' == s_month:
                s_date = s_year
            else:
                s_date = ''
            print(s_date)
            if '' != s_title or '' != s_nameId or '' != s_device or '' != s_date:
                yxlr_data = models.yxlr.objects.filter(s_title__contains=s_title, s_nameId__contains=s_nameId,
                                                       s_device__contains=s_device, s_date__contains=s_date).order_by(
                    '-s_date')
        else:
            get_form = forms.QueryForm()
    else:
        get_form = forms.QueryForm()
    return render(request, 'query.html', locals())


def yxlrIndex(request):
    articles = models.yxlr.objects.all().order_by('-s_date')  # 导入的Article模型
    p = Paginator(articles, 20)  # 分页，22篇文章一页
    if p.num_pages <= 1:  # 如果文章不足一页
        article_list = articles  # 直接返回所有文章
        data = ''  # 不需要分页按钮
    else:
        page = int(request.GET.get('page', 1))  # 获取请求的文章页码，默认为第一页
        article_list = p.page(page)  # 返回指定页码的页面
        left = []  # 当前页左边连续的页码号，初始值为空
        right = []  # 当前页右边连续的页码号，初始值为空
        left_has_more = False  # 标示第 1 页页码后是否需要显示省略号
        right_has_more = False  # 标示最后一页页码前是否需要显示省略号
        first = False  # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        last = False  # 标示是否需要显示最后一页的页码号。
        total_pages = p.num_pages
        page_range = p.page_range
        if page == 1:  # 如果请求第1页
            right = page_range[page:page + 2]  # 获取右边连续号码页
            print(total_pages)
            if right[-1] < total_pages - 1:  # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
                # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
                right_has_more = True
            if right[-1] < total_pages:  # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
                # 所以需要显示最后一页的页码号，通过 last 来指示
                last = True
        elif page == total_pages:  # 如果请求最后一页
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
            if left[0] > 2:
                left_has_more = True  # 如果最左边的号码比2还要大，说明其与第一页之间还有其他页码，因此需要显示省略号，通过 left_has_more 来指示
            if left[0] > 1:  # 如果最左边的页码比1要大，则要显示第一页，否则第一页已经被包含在其中
                first = True
        else:  # 如果请求的页码既不是第一页也不是最后一页
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
            right = page_range[page:page + 2]  # 获取右边连续号码页
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
        data = {  # 将数据包含在data字典中
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
            'total_pages': total_pages,
            'page': page
        }
    return render(request, 'index.html', context={
        'article_list': article_list, 'data': data})


def chart(request):
    groupby = 's_nameId'
    s_date = '2018-1-31'
    if request.method == 'GET':
        get_form = forms.PieForm(request.GET)
        if get_form.is_valid():
            s_one = get_form.cleaned_data['s_checkbox']
            s_two = get_form.cleaned_data['s_date']
            print(s_one, s_two)
            if s_one == '' or s_two == '':
                groupby = 's_nameId'
                s_date = '2018-1-31'
            else:
                groupby = s_one
                s_date = s_two
        else:
            groupby = 's_nameId'
            s_date = '2018-1-31'
    else:
        get_form = forms.PieForm()
    s_dataframe = pd.DataFrame(list(models.yxlr.objects.all().values()))
    plt.figure(figsize=(12, 8))
    x = []
    y = []
    df = s_dataframe.copy()
    df['s_date'] = pd.to_datetime(df['s_date'])
    df = df.set_index('s_date')
    name_df = df.groupby(groupby, as_index=False)
    for name, group in name_df:
        data = group.resample('M').count().reset_index(drop=False)  # 每个总帖子数
        data2 = data[data['s_date'] == s_date]
        if len(data2.values.tolist()) <= 0 or data2.values.tolist()[0][3] <= 0:
            continue
        else:
            x.append(data2.values.tolist()[0][3])
            y.append(name)
    for i in range(0, len(x)):
        y[i] += '(' + str(x[i]) + '篇)'
    plt.pie(x, labels=y, autopct='%1.1f%%', textprops={'fontsize': 8, 'color': 'blue'})
    plt.legend(loc='best', bbox_to_anchor=(1.1, 1.05), fontsize=8, borderaxespad=0.3)
    ax = plt.gca()
    ax.patch.set_alpha(0.5)
    plt.rcParams['savefig.facecolor'] = '#6DDCBD'
    plt.savefig('./static/pictures/one.png')
    plt.clf()
    return render(request, 'chart.html', locals())


def downExcel(request):
    file = open('./upload/游戏猎人用户组数据.xlsx', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = 'attachment;filename="yxlr.xls"'
    t = threading.Thread(target=delete_file, args=())  # 创建线程
    t.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
    t.start()  # 开启线程
    return response


def delete_file():
    sleep(10)
    os.remove('./upload/游戏猎人用户组数据.xlsx')


def exportexcel(request):
    urlList = []
    flag = os.path.exists('./upload/游戏猎人用户组数据.xlsx')
    if request.method == 'POST':
        get_form = forms.ExportExcelForm(request.POST)
        if get_form.is_valid():
            s_file = request.FILES.get('s_file')
            f = open(os.path.join(settings.MEDIA_ROOT, '', s_file.name), 'wb')
            for chunk in s_file.chunks():
                f.write(chunk)
            f.close()
            a = np.loadtxt(os.path.join(settings.MEDIA_ROOT, '', s_file.name), dtype=str).tolist()
            for list in a:
                if re.match(r'^https?:/{2}\w.+$', list) and list.find(
                        'club.huawei.com') >= 0:
                    urlList.append(list)
            print(urlList)
            t = threading.Thread(target=get_data, args=(urlList,))  # 创建线程
            t.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
            t.start()  # 开启线程
            '''
            for line in s_file:
                urlStr = str(line, 'UTF-8')
                if re.match(r'^https?:/{2}\w.+$', urlStr) and urlStr.find(
                        'club.huawei.com') >= 0:
                    urlList.append(urlStr)
            print(urlList)
            '''
        else:
            print('')
    else:
        get_form = forms.ExportExcelForm()
    return render(request, 'exportExcel.html', locals())


def get_data(urlList):
    excelHandle = ExcelHandle()
    excelHandle.create_excel()
    for index, urlHtml in enumerate(urlList):
        req = requests.get(url=urlHtml, headers=header)
        pageDoc = py(req.text)
        s_nameId = pageDoc('.authi').children('.xi2').eq(1).text().strip()  # 用户昵称
        s_title = pageDoc('#thread_subject').text()  # 帖子标题
        s_date = pageDoc('.authi').children('em').eq(1).children('span').attr('title')  # 帖子发表时间
        if s_date is None:
            s_date = getTimePage(pageDoc('.authi').children('em').eq(1).text()).strip()  # 发表时间
        if len(s_date) > 15:
            s_date = datetime.datetime.strptime(s_date, '%Y-%m-%d %H:%M:%S')
        else:
            s_date = datetime.datetime.strptime(s_date, '%Y-%m-%d')
        s_date = s_date.strftime('%Y-%m-%d')
        s_count = pageDoc('.hbw-ico.hbwi-view14')('span').text()  # 浏览量
        s_comment = pageDoc('.hbw-ico.hbwi-reply14')('span').text()  # 评论数
        s_gaizhang = pageDoc('#threadstamp')
        if s_gaizhang is not None:
            s_gaizhang = pageDoc('#threadstamp').children('img').eq(0).attr('title')  # 盖章
            if s_gaizhang == '' or s_gaizhang is None:
                s_gaizhang = '没有盖章'
        else:
            s_gaizhang = '没有盖章'
        excelHandle.add_excle('A' + str(index + 1), s_date)
        excelHandle.add_excle('B' + str(index + 1), s_nameId)
        excelHandle.add_excle('C' + str(index + 1), s_title)
        excelHandle.add_excle('D' + str(index + 1), '=HYPERLINK("%s","%s")' % (urlHtml, urlHtml))
        font = Font(name='微软雅黑', size=10, bold=False, italic=False, vertAlign=None,
                    underline='none', strike=False, color='FF000000')
        excelHandle.setFont('D' + str(index + 1), font)
        excelHandle.add_excle('E' + str(index + 1), s_count)
        excelHandle.add_excle('F' + str(index + 1), s_comment)
        excelHandle.add_excle('G' + str(index + 1), s_gaizhang)
    excelHandle.save_excel('./upload')
    excelHandle.close_excel()


def getTimePage(timepage):
    drawDigit = re.sub("\D", "", timepage)
    if len(drawDigit) == 1:
        return getDayTime(-int(drawDigit))
    elif timepage.find('前天') >= 0:
        return getDayTime(-2)
    elif timepage.find('昨天') >= 0:
        return getDayTime(-1)
    elif timepage.find('小时前') >= 0:
        f1 = re.findall('(\d+)', drawDigit)
        return (datetime.datetime.now() - datetime.timedelta(minutes=int(f1[0]) * 60)).strftime("%Y-%m-%d");
    else:
        mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", timepage)
        dt = datetime.datetime.strptime(mat.group(0), '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    return timepage


def getDayTime(days):
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=days)
    n_days = now + delta
    return n_days.strftime('%Y-%m-%d')


def isNetwork():
    exit_code = os.system('ping www.baidu.com')
    if exit_code:
        return False
    else:
        return True


def androidpieimage(request):
    groupby = 's_nameId'
    s_date = '2018-1-31'
    if request.method == 'GET':
        get_form = forms.PieForm(request.GET)
        if get_form.is_valid():
            s_one = get_form.cleaned_data['s_checkbox']
            s_two = get_form.cleaned_data['s_date']
            print(s_one, s_two)
            if s_one == '' or s_two == '':
                groupby = 's_nameId'
                s_date = '2018-1-31'
            else:
                groupby = s_one
                s_date = s_two
        else:
            groupby = 's_nameId'
            s_date = '2018-1-31'
    else:
        get_form = forms.PieForm()
    s_dataframe = pd.DataFrame(list(models.yxlr.objects.all().values()))
    plt.figure(figsize=(12, 8))
    x = []
    y = []
    df = s_dataframe.copy()
    df['s_date'] = pd.to_datetime(df['s_date'])
    df = df.set_index('s_date')
    name_df = df.groupby(groupby, as_index=False)
    for name, group in name_df:
        data = group.resample('M').count().reset_index(drop=False)  # 每个总帖子数
        data2 = data[data['s_date'] == s_date]
        if len(data2.values.tolist()) <= 0 or data2.values.tolist()[0][3] <= 2:
            continue
        else:
            x.append(data2.values.tolist()[0][3])
            y.append(name)
    for i in range(0, len(x)):
        y[i] += '(' + str(x[i]) + '篇)'
    plt.pie(x, labels=y, autopct='%1.1f%%', textprops={'fontsize': 8, 'color': 'blue'})
    plt.legend(loc='best', bbox_to_anchor=(1.1, 1.05), fontsize=8, borderaxespad=0.3)
    ax = plt.gca()
    ax.patch.set_alpha(0.5)
    plt.rcParams['savefig.facecolor'] = '#6DDCBD'
    plt.savefig('./static/pictures/one.png')
    plt.clf()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = base_dir
    imagepath = os.path.join(d, "static/pictures/one.png")
    print("imagepath=" + str(imagepath))
    image_data = open(imagepath, "rb").read()
    return HttpResponse(image_data, content_type="image/png")


def androidplotimage(request):
    x = []
    y = []
    df = pd.DataFrame(list(models.yxlr.objects.all().values()))
    df['s_date'] = pd.to_datetime(df['s_date'])
    df = df.set_index('s_date')
    if request.method == 'GET':
        get_form = forms.plotForm(request.GET)
        if get_form.is_valid():
            s_one = get_form.cleaned_data['s_checkbox']
            s_two = get_form.cleaned_data['s_name']
            if s_one == 's_one':
                data = df[df['s_nameId'] == s_two].resample('M').count().reset_index(drop=False)
                for index, row in data.iterrows():
                    y.append(row['s_url'])
                    x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
                plot_test(x, y, title=U'每月发帖量走势图')
            elif s_one == 's_two':
                data = df[df['s_nameId'] == s_two].resample('M').sum().reset_index(drop=False)
                for index, row in data.iterrows():
                    y.append(row['s_count'])
                    x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
                plot_test(x, y, title=U'每月总浏览量走势图')
            elif s_one == 's_three':
                data = df[df['s_nameId'] == s_two].resample('M').sum().reset_index(drop=False)
                for index, row in data.iterrows():
                    y.append(row['s_comment'])
                    x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
                plot_test(x, y, title=U'每月总评论量走势图')
            elif s_one == 's_four':
                data = df[df['s_nameId'] == s_two].resample('M')['s_count'].max().reset_index(drop=False)
                for index, row in data.iterrows():
                    if pd.isnull(row['s_count']):
                        y.append(0)
                    else:
                        y.append(row['s_count'])
                    x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
                plot_test(x, y, title=U'每月单帖最高浏览量柱形图', type=2)
            elif s_one == 's_five':
                data = df[df['s_nameId'] == s_two].resample('M')['s_comment'].max().reset_index(drop=False)
                for index, row in data.iterrows():
                    if pd.isnull(row['s_comment']):
                        y.append(0)
                    else:
                        y.append(row['s_comment'])
                    x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
                plot_test(x, y, title=U'每月单帖最高评论量柱形图', type=2)
        else:
            data = df[df['s_nameId'] == '云月静'].resample('M').count().reset_index(drop=False)
            for index, row in data.iterrows():
                y.append(row['s_url'])
                x.append(str(row['s_date'].year)[-2:] + str(row['s_date'].month))
            plot_test(x, y, title=U'每月发帖量走势图')
    else:
        get_form = forms.plotForm()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = base_dir
    imagepath = os.path.join(d, "static/pictures/two.png")
    print("imagepath=" + str(imagepath))
    image_data = open(imagepath, "rb").read()
    return HttpResponse(image_data, content_type="image/png")


def img(request):
    with open('static/pictures/two.png', 'rb') as f:
        data = f.read()
    return HttpResponse(data)

def question(request):
    result = {}  # 所有的文件
    for maindir, subdir, file_name_list in os.walk(os.path.abspath('static/question')):
        print("1:", maindir)  # 当前主目录
        print("2:", subdir)  # 当前主目录下的所有目录
        print("3:", file_name_list)  # 当前主目录下的所有文件
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)  # 合并成一个完整路径
            result['question/'+filename]=filename	
    result = sorted(result.items(), key=lambda d: d[1], reverse=True)
    return render(request, 'question.html', locals())

def clubshop(request):
    result = {}  # 所有的文件
    for maindir, subdir, file_name_list in os.walk(os.path.abspath('static/shop')):
        print("1:", maindir)  # 当前主目录
        print("2:", subdir)  # 当前主目录下的所有目录
        print("3:", file_name_list)  # 当前主目录下的所有文件
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)  # 合并成一个完整路径
            result['shop/'+filename]=filename
    result = sorted(result.items(), key=lambda d: d[1], reverse=True)
    return render(request, 'clubshop.html', locals())