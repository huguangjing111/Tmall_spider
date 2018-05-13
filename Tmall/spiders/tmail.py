# -*- coding: utf-8 -*-

import scrapy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from Tmall.items import TmailItem


class TmailSpider(scrapy.Spider):
    name = 'tmail'
    allowed_domains = ['tmall.com']

    # 请求头部信息
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, sdch",
        "accept-language": "zh-CN,zh;q=0.8",
        "cookie": "cna=6lBwExRTvWwCAbfpWd7N9VEj; enc=k5OJpwpCvy48lbSy8%2F2XW3KrZJREu5mSdTDWmuAvioKN8p5GO8FEGBSa3hEMGD9A%2BIga6ku%2BSDKL7r4FfogAoQ%3D%3D; t=9bb504119aa719b2319f4f73766227a1; _tb_token_=7e7874be5b35e; cookie2=1786a09ee35f40a6b0420bba82570daa; tk_trace=1; cq=ccp%3D1; _m_h5_tk=c6f607029f9429a0305b192cdf892e93_1526031514713; _m_h5_tk_enc=bebe89c28090b8c2f757c5fb8d430096; isg=BC0t6bFnC3kHw--TJadsSl9UPMCnimFcKmM0Xm8yN0S-5k-YN9oeLOzV1LoA5nkU",
        "if-none-match": 'W/"zeb2tOwwo8auZShIK36BEA == ',
        "upgrade-insecure-requests": "1",
        # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    # 登录cookies信息
    cookies = {

    }

    def start_requests(self):
        # 重写start_requests方法增加cookies信息和头部信心
        start_url = 'https://tmall.com/'
        print u'[INFO]  正在初始化请求首页%s' % start_url
        yield scrapy.Request(
            url=start_url,
            cookies=self.cookies,
            callback=self.parse_index,
            headers=self.headers
        )

    def parse_index(self, response):
        print u'[INFO]  正在解析提取首页%s' % response.url
        # 所有大类的链接列表
        # 爬取女装/内衣/男装商品信息
        hrefs_a = response.xpath('//div[@class="category-tab-content"]//ul/li/a/@href')[:1]
        # 女鞋/男鞋/箱包
        hrefs_b = response.xpath('//div[@class="category-tab-content"]//ul/li/a/@href')[4:5]
        # 列表相加拼接
        hrefs = hrefs_a + hrefs_b
        # 遍历列表取出每个链接
        for href in hrefs:
            # 跳转大类首页url地址
            url = 'https:' + href.extract()
            print u'[INFO]  正在请求大类地址%s' % url
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "accept-encoding": "gzip, deflate, sdch",
                "accept-language": "zh-CN,zh;q=0.8",
                "cache-control": "max-age=0",
                "if-none-match": 'W/"wbIVPvRiP7f05SIu9Wv/gw=="',
                "upgrade-insecure-requests": "1",
            }
            yield scrapy.Request(
                url=url,
                callback=self.parse_page,
                headers=headers,
            )

    def parse_page(self, response):
        print u'[INFO]  正在解析大类地址%s' % response.url

        # 大类中的每个中类列表
        node_list = response.xpath('//ul[@class="cate-nav"]/li')[0:1]
        for node in node_list:
            # 小类列表
            little_list = node.xpath('ul/li')[:1]
            for little in little_list:
                # （商品类列表）链接
                url = 'https:' + little.xpath('a/@href').extract_first()
                print u'[INFO]  正在请求商品页地址%s' % url
                # https://list.tmall.com/search_product.htm?tbpm=1&promo=43906&spm=a220m.1000858.0.0.oeFR13&cat=50037918&active=1&acm=lb-zebra-7499-292762.1003.4.427962&style=g&from=sn_1_rightnav&shopType=any&sort=s&search_condition=23&scm=1003.4.lb-zebra-7499-292762.OTHER_14748228333621_427962&industryCatId=50026245
                # https://list.tmall.com/search_product.htm?promo=43906&spm=a220m.1000858.0.0.oeFR13&cat=50037918&active=1&acm=lb-zebra-7499-292762.1003.4.427962&style=g&from=sn_1_rightnav&shopType=any&sort=s&search_condition=23&scm=1003.4.lb-zebra-7499-292762.OTHER_14748228333621_427962&industryCatId=50026245
                headers = {
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "accept-encoding": "gzip, deflate, sdch",
                    "accept-language": "zh-CN,zh;q=0.8",
                    "upgrade-insecure-requests": "1",
                }
                yield scrapy.Request(
                    url=url,
                    headers=headers,
                    callback=self.parse_good_list
                )

    def parse_good_list(self, response):
        print u'[INFO]  正在解析商品页地址%s' % response.url
        # 所有的商品信息列表框
        node_list = response.xpath('//div[@class="product  "]')
        for node in node_list:
            item = TmailItem()
            title = response.xpath('//title//text()').extract_first()
            title_list = title.split('-')
            # 商品类型
            item['type'] = title_list[0] + '-' + title_list[1]
            item['url'] = response.url
            # 图片链接列表
            img_list = node.xpath('div//div[@class="proThumb-wrap"]/p/b/img/@src')
            if not img_list:
                img_list = node.xpath('div//div[@class="proThumb-wrap"]/p/b/img/@data-ks-lazyload')
            img_list_data = img_list.extract()
            # 遍历列表更换图片url地址
            new_img_list = []
            for img in img_list_data:
                # 更换参数改为大图，并修改为完整的url地址
                img_url = 'https:' + img.replace('30x30','b')
                new_img_list.append(img_url)
            item['img_list'] = new_img_list
            # 商品详情链接
            good_link = 'https:' + node.xpath('div/div[@class="productImg-wrap"]/a/@href').extract_first()
            item['good_url'] = good_link
            # 商品价格
            price = node.xpath('div/p[@class="productPrice"]/em/text()').extract_first()
            item['good_price'] = price
            # 商品标题
            title = node.xpath('div/p[@class="productTitle"]/a/text()').extract_first().strip()
            if '/' in title:
                title = title.replace('/', '')
            # 去掉标题中的-
            if '-' in title:
                title = title.replace('-', '')
            # 将空格去掉
            title = title.replace(' ', '')
            item['good_name'] = title
            # 商店名称
            store = node.xpath('div/div[@class="productShop"]/a/text()').extract_first().strip()
            item['good_store'] = store
            # 月成交数
            try:
                data_year = node.xpath('div/p[@class="productStatus"]/span[1]/text()').extract_first() + node.xpath(
                    'div/p[@class="productStatus"]/span[1]/em/text()').extract_first()
                item['data_year'] = data_year
            except Exception as e:
                item['data_year'] = u'暂无月成交数'
            # 评论数量
            comment_count = node.xpath('div/p[@class="productStatus"]/span[2]/a/text()').extract_first()
            item['comment_count'] = comment_count
            yield item
        # 下一页链接
        next_link = 'https://list.tmall.com/search_product.htm' + response.xpath(
            '//a[@class="ui-page-next"]/@href').extract_first()
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, sdch",
            "accept-language": "zh-CN,zh;q=0.8",
            "cookie": "cna=6lBwExRTvWwCAbfpWd7N9VEj; enc=k5OJpwpCvy48lbSy8%2F2XW3KrZJREu5mSdTDWmuAvioKN8p5GO8FEGBSa3hEMGD9A%2BIga6ku%2BSDKL7r4FfogAoQ%3D%3D; _med=dw:1366&dh:768&pw:1366&ph:768&ist:0; t=9bb504119aa719b2319f4f73766227a1; _tb_token_=7e7874be5b35e; cookie2=1786a09ee35f40a6b0420bba82570daa; pnm_cku822=098%23E1hvQ9vUvbpvUvCkvvvvvjiPPFdvAjEmRs5U1jnEPmPytj38nLqZ6jYPP2MhsjlHiQhvCvvv9UUtvpvhvvvvvvGCvvpvvPMMuphvmvvv9bhRXpMZkphvC99vvpHlBfyCvm9vvvvWphvvCpvv9I3vpvLdvvmm8ZCvmE6vvU8UphvUPpvv9I3vpv9YmphvLv9OYvvjcW3lYnVGRmx8eOmxfXeKfvDrsjc6hLwl7UexAOkJ556Ofw3l%2Bb8rJmc6D7zWd3ODN%2B3lYE7rjC61D7z9aXTAVADl%2B8c6%2Bu6CvpvVvvpvvhCv; res=scroll%3A1282*6094-client%3A1282*506-offset%3A1282*6094-screen%3A1362*615; cq=ccp%3D1; tk_trace=1; _m_h5_tk=c6f607029f9429a0305b192cdf892e93_1526031514713; _m_h5_tk_enc=bebe89c28090b8c2f757c5fb8d430096; isg=BCMjEXpRff-_rDHNv_XajBUGsm7NGLdaMHEK4FWAeQL5lEO23ehHqgHuimSaNA9S",
            "upgrade-insecure-requests": "1",
            # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }
        if '&s=' in next_link:
            yield scrapy.Request(
                url=next_link,
                headers=headers,
                callback=self.parse_good_list
            )


# 评论详情url
"""
https://rate.tmall.com/list_detail_rate.htm?itemId=567966639294&spuId=957503765&sellerId=272205633&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&ua=098%23E1hv0pvWvR9vUvCkvvvvvjiPPFdh1jinRsSvlj1VPmP9QjYnRFMvQjrnPFsy1jDC2QhvCvvvMMGCvpvVvvpvvhCvKphv8vvvvvCvpvvvvvmCyZCvmR6vvUUdphvWvvvv9krvpv3Fvvmm86CvmVRivpvUvvmv%2BBn81IkEvpvVmvvC9jXCmphvLvCTZ9vj7SoUzXZBHkx%2FQjc6D46OjL4UkXjErCH%2Bm7zvaNoAdcvrdUFXDLyBfvDrzjc6KqpKodzafX7rVClv%2BExrQ8TJnDeDyO2vHdUtvpvhvvvvv8wCvvpvvUmm3QhvCvvhvvmrvpvpjvkV9aqJChDrFfwznHVt6OhCvv147lSzWY147DKK5rGtvpvhvvvvvv%3D%3D&isg=BOzsM2-HmkncQY5xJ3Zbce7kvcoUW5VCL2aMH0Ytvxc6UY1bbLQM3wyDdRlpWcin&needFold=0&_ksTS=1526111865344_866&callback=jsonp867
https://rate.tmall.com/list_detail_rate.htm?itemId=567404329805&spuId=953623534&sellerId=1044264726&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&ua=098%23E1hvX9vnvPOvUvCkvvvvvjiPPFdh1jDUn2d9ljEUPmPy6j3RPFLUAjEHPssW6j1EdphvmpmvHCwNvv2vFOhCvCB47zdMOY147DdO%2F%2FNGvHi%2B7dMNo86CvvyvvLwsi9vvRjR5vpvhvvCCB2yCvvpvvhCv2QhvCvvvMMGCvpvVvUCvpvvvmphvLU2zL6GaiXg4eBDAcreYr2UpVj%2BO3w0AhEkwJ9kx6fItn1vFJWFZdiTQdox%2Fgj7KHdoJay2wACOqrqpyCW2%2B%2Bfmt%2BeCoQR9t%2BFuTWDAtvpvIvvCv7vvvv8vvvhxpvvvCApvvBBWvvUhvvvCHZvvvvcpvvhxpvvvCaUyCvvOCvhEvlWmivpvUvvCCUylY%2FPJjvpvhvUCvp2yCvvpvvhCv&isg=BEBANBGEDvXpQfL0kIQJdWLnEccSySSTB3CJ-brRbtvlNeFfYtigIw5nSZ31hdxr&needFold=0&_ksTS=1526112221943_2220&callback=jsonp2221
https://rate.tmall.com/list_detail_rate.htm?itemId=554112479694&spuId=858920460&sellerId=1044264726&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&ua=098%23E1hvb9vWvRyvUvCkvvvvvjiPPFdh1j3URFzOgj3mPmPytjEbPLcv0jn8n2zyljEjRphvCvvvvvmCvpvW7D%2BsY1jw7Di4ukcNdphvhovhOIjazpvtUoeS8kH2mOcE3QhvCvvhvvvEvpCWhn7kvvakfwClMCy4ahqOtRLvHF%2BSBiVvQRA1%2B2n79WFvT2eAnhjEKOmxdXIaUExr1jZ7%2B3%2BSaNoxfXeKfvDr0jc6d4t%2Bm7zyaNop%2BdyCvm9vvvvWphvvCpvv9Iivpv3Rvvmm86Cv2vvvvU88phvUIQvv9IivpvkFkphvC99vvpHlB4yCvv9vvUm1hzgrlvhCvvOvCvvvphvPvpvhvv2MMsyCvvpvvvvviQhvCvvv9UU%3D&isg=BF5e68A3iH9HaNyewhJPrzBZr_2gHyKZdT4nEwjngqGQK_8FcK4ZqXypJzcnExqx&needFold=0&_ksTS=1526113084636_2616&callback=jsonp2617
"""
