#coding: utf-8

import unittest
from hprc_spider.spider import HPRCSpider, IndexPageGenerator


class TestIndexPageGenerator(unittest.TestCase):
    def test_get_page_urls(self):
        generator = IndexPageGenerator("http://www.hprc.org.cn/gsgl/zyxw/", 63)
        for url in generator.page_urls:
            print(url)

class TestHPRCSpider(unittest.TestCase):
    def setUp(self):
        self.spider = HPRCSpider()
        self.generator = IndexPageGenerator("http://www.hprc.org.cn/gsgl/zyxw/", 1)
        self.list_urls = list(self.generator.page_urls)

    def test_get_article_links(self):
        self.spider.crawl_detail_url_list(self.list_urls)
        self.spider.crawl_detail_urls()

    def test_crawl_detail_urls(self):
        self.spider.crawl_detail_url_list(self.list_urls)
        self.spider.crawl_detail_urls()

    def test_process_one_detail_url(self):
        self.spider.crawl_detail_url_list(self.list_urls)
        detail_url = self.spider.detail_url_list[0]
        article = self.spider.process_one_detail_url(detail_url)
        print(article)
        print(article["title"])
        print(article["content"])
        print(article["author"])
        print(article["publish_time"])
        print(article["source"])
        print(article["url"])