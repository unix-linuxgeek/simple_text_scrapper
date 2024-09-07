from time import sleep
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import html2text
import os


def get_html(url, attempts=1, timeout=10, delay=1):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    html_converter = html2text.HTML2Text()
    html_converter.ignore_links = True
    html_converter.ignore_images = True

    for i in range(attempts):
        try:
            response = urlopen(url, timeout=timeout, context=ctx)

            # check OK code from web server
            if response.code != 200:
                sleep(delay)
                continue

            html_bytes = response.read()
            html_text = html_bytes.decode("utf8")
            html_tree = BeautifulSoup(html_text, 'html.parser')

            title_tag = html_tree.find("title")
            title_html = str(title_tag)
            title_text = html_converter.handle(title_html)

            chapter_name_tag = html_tree.find("h1")
            chapter_name_html = str(chapter_name_tag)
            chapter_name = html_converter.handle(chapter_name_html)

            article_tags = html_tree.find_all("p")
            article_text = ''
            for tag in article_tags:
                html = str(tag)
                text = html_converter.handle(html)
                article_text += text

            return title_text, chapter_name, article_text

        except Exception as e:
            print(e)
            sleep(delay)

    return None


def save_pages(file_name, url_template, first_page_id=19504, last_page_id=19515, step=1, delay=1):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    current_page_num = 1

    with open(file_path, "w", encoding="utf-8") as f:
        for i in range(first_page_id, last_page_id + 1, step):
            url = url_template.format(i)
            result = get_html(url)

            if result is None:
                print(url + '    Missed!')
            else:
                print(url + '    OK!')
                title_text, chapter_name, article_text = result
                f.write("page" + str(current_page_num) + "\n" + chapter_name + "\n" + article_text + "\n\n")

            current_page_num += 1
            sleep(delay)

file_name = 'file_name.txt'
url_template = 'https://example.com/{}.html'
save_pages(file_name, url_template, first_page_id=1, last_page_id=100, step=1)
