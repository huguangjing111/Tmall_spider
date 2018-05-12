# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TmailItem(scrapy.Item):
    # define the fields for your item here like:
    # 类型
    type = scrapy.Field()
    # 图片链接
    img_list = scrapy.Field()
    # 商品详情页面链接
    good_url = scrapy.Field()
    # 商品标题
    good_name = scrapy.Field()
    # 商品价格
    good_price = scrapy.Field()
    # 评论数目
    comment_count = scrapy.Field()
    # 商店信息
    good_store = scrapy.Field()
    # 月成交数
    data_year = scrapy.Field()
    # 商品页url
    url = scrapy.Field()



