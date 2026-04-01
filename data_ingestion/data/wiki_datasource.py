import re
from urllib.parse import unquote
from xml.dom.minidom import Element, Node, parseString

import requests
from unstructured.chunking.title import chunk_by_title
from unstructured.partition.html import partition_html

from data_ingestion.models.page_data import PageData

default_url = "https://pt.stardewvalleywiki.com"


def treat_html(html: str) -> str:
    """Treats HTML content to make it parseable."""
    html = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<style.*?>.*?</style>", "", html, flags=re.DOTALL)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"\s+", " ", html)
    html = re.sub(r"> <", ">\n<", html)
    html = re.sub(r"><", ">\n<", html)
    html = re.sub(r'<input(.*?)">', '<input\\1"/>', html)
    html = re.sub(r"<input(.*?) >", "<input\\1 />", html)
    html = re.sub(r"<img([^>]+) >", "<img\\1 />", html)
    html = re.sub(r'<img([^>]+)">', '<img\\1"/>', html)
    html = re.sub(r"&lrm;", "", html)
    html = re.sub(r"&gt;", ">", html)
    html = re.sub(r'>data-sort-value="(\d+)">', ">\\1 ouros", html)
    html = re.sub(r'>data-sort-value="(\d\s+)";', ">\\1 ouros", html)
    html = re.sub(r"<link(.*?)>", "", html)
    html = re.sub(r"<br>", "", html)
    return html


def treat_url(url: str) -> str:
    return unquote(url).lower()


def should_visit(url: str, urls: list[str]) -> bool:
    """Determines if a URL should be visited."""
    return (
        url.startswith("/")
        and url not in urls
        and "mediawiki" not in url
        and "ficheiro:" not in url
        and "#" not in url
        and "utilizador_discussão" not in url
        and "histórico_de_versões" not in url
        and "utilizadora_discussão" not in url
        and "utilizadora" not in url
        and "modificações" not in url
        and "pesquisar/" not in url
    )


def get_urls(content: Element, all_urls: list[str]) -> list[str]:
    """Gets all URLs from a page's content."""
    urls: list[str] = []
    if content.childNodes:
        for node in content.childNodes:
            if node.nodeType == Node.ELEMENT_NODE and node.tagName == "a":
                href = treat_url(node.getAttribute("href"))
                if href and should_visit(href, all_urls + urls):
                    print(f"  - Found new URL: {href}")
                    urls.append(href)
            urls.extend(get_urls(node, all_urls + urls))

    return urls


def get_content_from_page(html: str) -> Element:
    """Gets the main content from a page's HTML."""
    html = treat_html(html)

    try:
        html_parsed = parseString(html)

    except Exception as e:
        print("Error parsing HTML:", e)
        print(html)
        raise e
    body = html_parsed.childNodes[1].childNodes[3]
    if len(body.childNodes) > 5:
        content = (
            html_parsed.childNodes[1]
            .childNodes[3]
            .childNodes[5]
            .childNodes[9]
            .childNodes[13]
            .childNodes[1]
        )
        for child in content.childNodes:
            if '<h2 id="mw-toc-heading">Índice</h2>' in child.toxml():
                content.removeChild(child)
                break
    else:
        content = html_parsed.childNodes[1].childNodes[3].childNodes[1]

    return content


def compareable_url(url: str) -> str:
    return treat_url(url).lower().replace(".json", "").removeprefix("/")


def compareable_url_list(urls: list[str]) -> list[str]:
    new_list = []
    for url in urls:
        new_list.append(treat_url(url).lower().replace(".json", "").removeprefix("/"))
    return new_list


def get_data_from_url(url: str, all_urls: list[str]) -> PageData:
    """Gets data from a given URL."""
    html = requests.get(f"{default_url}{url}").text

    content = get_content_from_page(html)

    elements_for_chunking = partition_html(text=content.toxml())

    return PageData(
        urls=get_urls(content, all_urls),
        chunks=chunk_by_title(elements_for_chunking, max_characters=800, overlap=100),
    )
