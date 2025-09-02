# coding: utf-8

from hprc_spider.spider import HPRCSpider, IndexPageGenerator
import argparse


class Args:
    def __init__(self):
        args = argparse.ArgumentParser()
        args.add_argument("--index_url", type=str,
                          default="http://www.hprc.org.cn/gsgl/zyxw/")
        args.add_argument("--page_count", type=int, default=1)
        args.add_argument("--output_dir", type=str, default="articles")
        args.add_argument("--interval", type=int, default=1)
        args.add_argument("--formats", type=list,
                          default=["markdown", "txt", "pdf"])
        args.add_argument("-a", "--article", type=int, default=0)
        self.args = args.parse_args()


def main():
    args = Args().args
    spider = HPRCSpider(args.output_dir, args.interval)
    generator = IndexPageGenerator(args.index_url, args.page_count)
    list_urls = list(generator.page_urls)
    spider.crawl_detail_url_list(list_urls)
    article = spider.process_one_detail_url(
        spider.detail_url_list[args.article])
    print(article["title"])
    print(article["content"])
    print("\nSource: " + article["url"])

    return 0


if __name__ == "__main__":
    main()
