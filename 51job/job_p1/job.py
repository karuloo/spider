"""
     下载51job上的职位，处理后写入csv文件中
     写入csv的格式由于没处理之前就爬取了一份，所以
     格式部分大部分按照爬取下来的规律进行分析后写入进去的，
     表格csv为抓取的数据
"""

import requests
import re
import csv
from lxml import etree

#  cookies可填可不填，没有强校验，user-agent最好加上
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
    'Cookie': '',
}

# 打开csv,并将头写入进去
with open('./51job1.csv', 'a+', newline='')as f:
    writer = csv.writer(f)
    title = ['职位', '公司', '地点', '处理后的地址', '发布时间', '薪水', '最低薪水', '最高薪水', '学历', '处理后的学历']
    writer.writerow(title)


# 解析网页，获取职位的分类的url,此时是按照职位分类来获取的，当然，你也可以按照城市获取
def parse_job_url(url):
    job_urls = []
    content = requests.get(url, headers=HEADERS)
    content.encoding = 'gbk'
    content = content.text
    content = etree.HTML(content)
    job_lists = content.xpath('//div[@class="lkst"]//a/@href')
    if job_lists is not None:
        for item in job_lists:
            job_urls.append(item)
    return job_urls


# 解析地址，例如 深圳-南山区解析为深圳，深圳解析为深圳
def parse_location(location):
    temp = re.findall('-', location)
    if temp:
        location = location.split('-')[0]
    if location == '异地招聘':
        location = None
    return location


# 解析学历，学历要求：本科 解析为 本科
def parse_order(order):
    order = order.split('学历要求：')
    if len(order) == 2:
        return order[1]
    else:
        return None


# 解析月薪，万/月，千/月 分别拆分为最高薪资和最低薪资
def parse_money(money):
    temp_l = temp_h = 0
    if re.findall('万/月', money):
        temp_w = re.findall('\d+\.?\d?', money)
        if (len(temp_w) == 1):
            temp_l = temp_h = float(temp_w[0]) * 10000
        else:
            temp_l = float(temp_w[0]) * 10000
            temp_h = float(temp_w[1]) * 10000
    elif re.findall('千/月', money):
        temp_w = re.findall('\d+\.?\d?', money)
        if (len(temp_w) == 1):
            temp_l = temp_h = float(temp_w[0]) * 1000
        else:
            temp_l = float(temp_w[0]) * 1000
            temp_h = float(temp_w[1]) * 1000
    elif re.findall('万/年', money):
        temp_w = re.findall('\d+\.?\d?', money)
        if (len(temp_w) == 1):
            temp_l = temp_h = float(temp_w[0]) * 10000 / 12
        else:
            temp_l = float(temp_w[0]) * 10000 / 12
            temp_h = float(temp_w[1]) * 10000 / 12
    elif re.findall('元/天', money):
        temp_w = re.findall('\d+\.?\d?', money)
        if (len(temp_w) == 1):
            temp_l = temp_h = float(temp_w[0]) * 30
        else:
            temp_l = float(temp_w[0]) * 30
            temp_h = float(temp_w[1]) * 30

    return temp_l, temp_h


# 解析职位信息
def parse_job(url):
    content = requests.get(url, headers=HEADERS)
    content.encoding = 'gbk'
    content = content.text
    next_page = re.findall('<a href="(.*?)">下一页</a>', content)
    content = etree.HTML(content)
    job_lists = content.xpath('//div[@class="e "]')
    for job_list in job_lists:
        temp_dist = {}
        title = company = location = time = money = order = p_order = p_location = money_h = money_l = None
        if job_list.xpath('./p[@class="info"]/span[@class="title"]/a/text()'):
            title = job_list.xpath('./p[@class="info"]/span[@class="title"]/a/text()')[0]
        if job_list.xpath('./p[@class="info"]/a/@title'):
            company = job_list.xpath('./p[@class="info"]/a/@title')[0]
        if job_list.xpath('./p[@class="info"]/span[@class="location name"]/text()'):
            location = job_list.xpath('./p[@class="info"]/span[@class="location name"]/text()')[0]
        if job_list.xpath('./p[@class="info"]/span[@class="time"]/text()'):
            time = job_list.xpath('./p[@class="info"]/span[@class="time"]/text()')[0]
        if job_list.xpath('./p[@class="info"]/span[@class="location"]/text()'):
            money = job_list.xpath('./p[@class="info"]/span[@class="location"]/text()')[0]
        if job_list.xpath('./p[@class="order"]//text()')[0]:
            order = job_list.xpath('./p[@class="order"]//text()')[0]

        temp_dist['职位'] = title
        temp_dist['公司'] = company
        temp_dist['地点'] = location
        temp_dist['发布时间'] = time
        temp_dist['薪水'] = money
        temp_dist['学历'] = order
        if location is not None:
            p_location = parse_location(location)
        if order is not None:
            p_order = parse_order(order)
        if money is not None:
            money_l, money_h = parse_money(money)

        row = [title, company, location, p_location,
               time, money, money_l, money_h, order, p_order]
        print(row)
        with open('./51job1.csv', 'a+', newline='')as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)
    if next_page:
        parse_job(next_page[0])


if __name__ == '__main__':
    url = 'https://jobs.51job.com/'
    job_urls = parse_job_url(url)
    for url in job_urls:
        parse_job(url)
