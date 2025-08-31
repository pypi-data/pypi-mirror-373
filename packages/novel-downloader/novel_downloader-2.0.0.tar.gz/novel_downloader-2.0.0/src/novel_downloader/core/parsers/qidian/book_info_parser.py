#!/usr/bin/env python3
"""
novel_downloader.core.parsers.qidian.book_info_parser
-----------------------------------------------------

This module provides parsing of Qidian book info pages.

It extracts metadata such as title, author, cover URL, update
time, status, word count, summary, and volume-chapter structure.
"""

import logging
import re
from datetime import datetime

from lxml import html

from novel_downloader.models import BookInfoDict, ChapterInfoDict, VolumeInfoDict

logger = logging.getLogger(__name__)


def _chapter_url_to_id(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def parse_book_info(html_str: str) -> BookInfoDict | None:
    """
    Extract metadata: title, author, cover_url, update_time, status,
    word_count, summary, and volumes with chapters.

    :param html_str: Raw HTML of the book info page.
    :return: A dict containing book metadata.
    """
    doc = html.fromstring(html_str)

    book_name = doc.xpath('string(//h1[@id="bookName"])').strip()

    author = doc.xpath('string(//a[@class="writer-name"])').strip()

    book_id = doc.xpath('//a[@id="bookImg"]/@data-bid')[0]
    cover_url = f"https://bookcover.yuewen.com/qdbimg/349573/{book_id}/600.webp"

    ut = doc.xpath('string(//span[@class="update-time"])')
    ut = ut.replace("更新时间:", "").strip()
    if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", ut):
        update_time = ut
    else:
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    serial_status = doc.xpath('string(//p[@class="book-attribute"]/span[1])').strip()

    tags_elem = doc.xpath('//p[contains(@class,"all-label")]//a/text()')
    tags = [t.strip() for t in tags_elem if t.strip()]

    word_count = doc.xpath('string(//p[@class="count"]/em[1])').strip()

    summary_brief = doc.xpath('string(//p[@class="intro"])').strip()

    raw = doc.xpath('//p[@id="book-intro-detail"]//text()')
    summary = "\n".join(line.strip() for line in raw if line.strip())

    volumes: list[VolumeInfoDict] = []
    for vol in doc.xpath('//div[@id="allCatalog"]//div[@class="catalog-volume"]'):
        vol_name = vol.xpath('string(.//h3[@class="volume-name"])').strip()
        vol_name = vol_name.split(chr(183))[0].strip()
        chapters: list[ChapterInfoDict] = []
        for li in vol.xpath('.//ul[contains(@class,"volume-chapters")]/li'):
            a = li.xpath('.//a[@class="chapter-name"]')[0]
            title = a.text.strip()
            url = a.get("href")
            chapters.append(
                {"title": title, "url": url, "chapterId": _chapter_url_to_id(url)}
            )
        volumes.append({"volume_name": vol_name, "chapters": chapters})

    return {
        "book_name": book_name,
        "author": author,
        "cover_url": cover_url,
        "update_time": update_time,
        "word_count": word_count,
        "serial_status": serial_status,
        "tags": tags,
        "summary_brief": summary_brief,
        "summary": summary,
        "volumes": volumes,
        "extra": {},
    }
