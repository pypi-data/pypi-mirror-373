import os
import re
import json
import requests
from bs4 import BeautifulSoup, NavigableString
from typing import List, Dict, Optional, Any
from pathlib import Path
import markdown
import pdfkit
from slugify import slugify
from urllib.parse import urljoin
import time


class IndexPageGenerator:
    def __init__(self, index_url: str, page_count: int):

        self.index_url = index_url
        self.page_count = page_count

    @property
    def page_urls(self) -> List[str]:
        for page in range(0, self.page_count):
            if page == 0:
                yield self.index_url + "index.html"
            else:
                yield f"{self.index_url}index_{page}.html"


class HPRCSpider:
    def __init__(self, output_dir: str = "articles", interval: int = 1):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.history_file = self.output_dir / "history.json"
        self.processed_urls = self._load_history()
        self.detail_url_list = []
        self.interval = interval

    def _load_history(self) -> set:
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def _save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(list(self.processed_urls), f)

    def _get_page(self, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text

    def get_article_links(self, list_url: str) -> List[str]:
        base_url = list_url.rsplit("/", 1)[0] + "/"
        html = self._get_page(list_url)
        soup = BeautifulSoup(html, "html.parser")
        links = []
        # Adjust selector based on actual HTML structure
        for a in soup.select("table.sanjixi_zi2 a"):
            href = a.get("href", "")
            if href and href.endswith(".html"):
                full_url = urljoin(base_url, href)
                links.append(full_url)
        return links

    def parse_article(self, url: str) -> Dict[str, Any]:
        html = self._get_page(url)
        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("span.huang16c").get_text(strip=True)

        metadata_text = soup.select_one("td.huang12_h").get_text()
        author = ""
        publish_time = ""
        source = ""

        author_match = re.search(r"作者：\s*([^\s]+)", metadata_text)
        if author_match:
            author = author_match.group(1).strip()

        time_match = re.search(r"发布时间：\s*([^\s]+)", metadata_text)
        if time_match:
            publish_time = time_match.group(1).strip()

        source_match = re.search(r"来源：\s*([^\s]+)", metadata_text)
        if source_match:
            source = source_match.group(1).strip()

        # Extract content including images
        content_parts = []
        content_p_list = soup.select("div.TRS_Editor p")

        for element in content_p_list:
            text = element.text.strip()
            if text and not any(meta in text for meta in ["作者：", "发布时间：", "来源：", "字体：", "关闭窗口"]):
                content_parts.append(text) 
        content = "\n".join(filter(None, content_parts))

        return {
            "title": title,
            "content": content,
            "author": author,
            "publish_time": publish_time,
            "source": source,
            "url": url
        }

    def save_article(self, article: Dict[str, str], formats: List[str] = ["markdown", "txt"]):
        # title_slug = slugify(article["title"])
        title_slug = article["title"]
        for fmt in formats:
            dir_path = self.output_dir / fmt
            dir_path.mkdir(exist_ok=True)
            output_path = dir_path / f"{title_slug}.{fmt}"

            if fmt == "markdown":
                content = f"# {article['title']}\n\n{article['content']}\n\nSource: {article['url']}"
                output_path.write_text(content, encoding="utf-8")

            elif fmt == "txt":
                content = f"{article['title']}\n\n{article['content']}\n\nSource: {article['url']}"
                output_path.write_text(content, encoding="utf-8")

            elif fmt == "pdf":
                html_content = f"<h1>{article['title']}</h1><div>{article['content']}</div><p>Source: {article['url']}</p>"
                try:
                    pdfkit.from_string(html_content, str(output_path))
                except Exception as e:
                    print(
                        f"Failed to generate PDF for {article['title']}: {e}")

    def crawl_detail_url_list(self, list_urls: List[str]):
        for list_url in list_urls:
            print(f"Processing list page: {list_url}")
            article_links = self.get_article_links(list_url)
            self.detail_url_list.extend(article_links)

    def crawl_detail_urls(self):
        for idx, detail_url in enumerate(self.detail_url_list):
            if detail_url in self.processed_urls:
                print(f"{idx+1}/{len(self.detail_url_list)} 跳过已处理的文章: {detail_url}")
                continue
            try:
                print(f"{idx+1}/{len(self.detail_url_list)} 处理文章: {detail_url}")
                article = self.process_one_detail_url(detail_url)
                print(
                    f"{idx+1}/{len(self.detail_url_list)} 成功保存文章: {article['title']}")
            except Exception as e:
                print(
                    f"{idx+1}/{len(self.detail_url_list)} 处理文章失败: {detail_url}: {e}")
            finally:
                time.sleep(self.interval)

    def process_one_detail_url(self, detail_url: str):
        article = self.parse_article(detail_url)
        self.save_article(article)
        self.processed_urls.add(detail_url)
        self._save_history()
        return article


def main():
    spider = HPRCSpider()
    list_urls = [
        "http://www.hprc.org.cn/gsgl/zyxw/",
        # Add more list URLs as needed
    ]
    spider.crawl_detail_url_list(list_urls)
    spider.crawl_detail_urls()


if __name__ == "__main__":
    main()
