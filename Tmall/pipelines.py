# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

import scrapy
from scrapy.exporters import CsvItemExporter
from scrapy.pipelines.images import ImagesPipeline

from Tmall.settings import IMAGES_STORE
import pymongo


# 存储CSV文件
class TmallPipeline(object):
    def open_spider(self, spider):
        self.f = open('/home/python/Desktop/Tmail_info/Tmail_goods.csv', 'w')
        self.csv_writer = CsvItemExporter(self.f)
        self.csv_writer.start_exporting()
        # 创建数据去重集合
        self.add_name = set()

    def process_item(self, item, spider):
        if item['good_name'] in self.add_name:
            raise Exception(u'该数据已存在文件中')
        else:
            self.add_name.add(item['good_name'])
            print u'[INFO]  正在将商品信息写入文件'
            self.csv_writer.export_item(dict(item))
        return item

    def close_spider(self, spider):
        self.csv_writer.finish_exporting()
        self.f.close()


# 存储图片到指定目录下
class TmailImagePipline(ImagesPipeline):
    # 保存图片到默认位置
    def get_media_requests(self, item, info):
        img_list = item['img_list']
        for img_url in img_list:
            print u'[INFO]  正在保存图片%s' % img_url
            yield scrapy.Request(img_url)

    def item_completed(self, results, item, info):
        print u'[INFO]  正在修改图片路径'
        """
        results = [
            (True, {'url': 'https://img.alicdn.com/bao/uploaded/i4/1836310089/TB2IPRMg.R1BeNjy0FmXXb0wVXa_!!1836310089.jpg_30x30.jpg', 'path': 'full/16cabf17ee6b9cf62a72aac84deeffd72bd00b69.jpg', 'checksum': 'a7477c1e15062d6f1970e902652291fb'}), (True, {'url': 'https://img.alicdn.com/bao/uploaded/i3/1836310089/TB28r3wgKuSBuNjSsplXXbe8pXa_!!1836310089.jpg_30x30.jpg', 'path': 'full/a714a3309f53fa01bc83863d45c45c384094d71f.jpg', 'checksum': '3081d5ce896ab4d847a71dc53cf8091b'}), (True, {'url': 'https://img.alicdn.com/bao/uploaded/i2/1836310089/TB2XPIcmeySBuNjy1zdXXXPxFXa_!!1836310089.jpg_30x30.jpg', 'path': 'full/3446669fcbb7c63fb8f8921b9de1b6400069f0a8.jpg', 'checksum': '146743696df6de231cb0d93e9bd4de5f'})
        ]
        """

        # 原来图片存储路径列表
        img_list = [x['path'] for ok, x in results if ok]
        for index, img_path in enumerate(img_list):
            # 原来图片存储路径
            path_old = img_path
            # 现在图片路径
            path_now = IMAGES_STORE + 'images/' + item['good_name'] + str(index + 1) + path_old[-4:]
            # 修改名字
            try:
                os.rename(
                    IMAGES_STORE + path_old,
                    path_now
                )
                print u'[INFO]  修改图片路径成功%s' % path_now
            except Exception as e:
                print e
                print u'[ERROR] 修改图片路径失败或图片已经保存%s' % path_now
        return item


# 存储到mongoDB中
class TmailMongodDBPipeline(object):
    def open_spider(self,spider):
        self.client = pymongo.MongoClient(host='127.0.0.1',port=27017)
        self.db = self.client['Tamil']
        self.collection = self.db['tmail']
        self.add_name = set()

    def process_item(self,item,spider):
        if item['good_name'] in set:
            raise Exception(u'数据已经保存在数据库中，请勿重复保存')
        else:
            self.add_name.add(item['good_name'])
            self.collection.insert(dict(item))
        return item


