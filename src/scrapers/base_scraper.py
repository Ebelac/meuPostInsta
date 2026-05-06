"""
Base scraper class para diferentes fontes de notícias
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin, urlparse
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Estrutura de dados para artigos"""
    title: str
    url: str
    source: str
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None


class BaseScraper(ABC):
    """Classe base para scrapers de notícias"""

    def __init__(self, source_name: str, base_url: str, delay: float = 1.0):
        self.source_name = source_name
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    @abstractmethod
    def scrape_articles(self, limit: int = 10) -> List[Article]:
        """Método abstrato para scraping de artigos"""
        pass

    def make_request(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """Faz requisição HTTP com tratamento de erros"""
        try:
            time.sleep(self.delay)  # Rate limiting
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_text_content(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Extrai conteúdo de texto usando múltiplos seletores"""
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                return ' '.join([elem.get_text(strip=True) for elem in elements])
        return ""

    def clean_text(self, text: str) -> str:
        """Limpa e formata texto extraído"""
        if not text:
            return ""

        # Remove múltiplas quebras de linha
        text = ' '.join(text.split())

        # Remove caracteres especiais desnecessários
        text = text.replace('\xa0', ' ')
        text = text.replace('\u2013', '-')
        text = text.replace('\u2014', '--')

        return text.strip()

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse de diferentes formatos de data"""
        if not date_str:
            return None

        # Formatos comuns
        formats = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError):
                continue

        logger.warning(f"Could not parse date: {date_str}")
        return None


class RSSFeedScraper(BaseScraper):
    """Scraper para feeds RSS"""

    def __init__(self, source_name: str, rss_url: str, delay: float = 1.0):
        super().__init__(source_name, rss_url, delay)
        self.rss_url = rss_url

    def scrape_articles(self, limit: int = 10) -> List[Article]:
        """Scrape articles from RSS feed"""
        try:
            feed = feedparser.parse(self.rss_url)
            articles = []

            for entry in feed.entries[:limit]:
                article = Article(
                    title=self.clean_text(entry.get('title', '')),
                    url=entry.get('link', ''),
                    source=self.source_name,
                    author=entry.get('author', ''),
                    published_date=self._parse_feed_date(entry),
                    summary=self.clean_text(entry.get('summary', '')),
                    category=self._extract_category(entry)
                )

                # Tentar extrair conteúdo completo
                if article.url:
                    full_content = self._extract_full_content(article.url)
                    if full_content:
                        article.content = full_content

                articles.append(article)

            logger.info(f"Scraped {len(articles)} articles from {self.source_name}")
            return articles

        except Exception as e:
            logger.error(f"Error scraping RSS feed {self.rss_url}: {e}")
            return []

    def _parse_feed_date(self, entry) -> Optional[datetime]:
        """Parse date from RSS entry"""
        date_fields = ['published_parsed', 'updated_parsed']

        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    return datetime(*time_struct[:6])
                except (TypeError, ValueError):
                    continue

        # Try string dates
        string_dates = ['published', 'updated']
        for field in string_dates:
            if hasattr(entry, field):
                parsed_date = self.parse_date(getattr(entry, field))
                if parsed_date:
                    return parsed_date

        return None

    def _extract_category(self, entry) -> Optional[str]:
        """Extract category from RSS entry"""
        if hasattr(entry, 'tags') and entry.tags:
            return entry.tags[0].term if entry.tags[0].term else None

        if hasattr(entry, 'category'):
            return entry.category

        return None

    def _extract_full_content(self, url: str) -> Optional[str]:
        """Extract full article content from URL"""
        response = self.make_request(url)
        if not response:
            return None

        try:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Common content selectors
            content_selectors = [
                'article .content',
                '.post-content',
                '.entry-content',
                '.article-content',
                '.story-body',
                'main article',
                '[data-module="ArticleBody"]',
                '.article-wrap p'
            ]

            content = self.extract_text_content(soup, content_selectors)
            return self.clean_text(content) if content else None

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None


class WebScraper(BaseScraper):
    """Scraper para sites web que não têm RSS"""

    def __init__(self, source_name: str, base_url: str, delay: float = 2.0):
        super().__init__(source_name, base_url, delay)

    def scrape_articles(self, limit: int = 10) -> List[Article]:
        """Scrape articles from website"""
        response = self.make_request(self.base_url)
        if not response:
            return []

        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self._extract_articles_from_page(soup, limit)

            logger.info(f"Scraped {len(articles)} articles from {self.source_name}")
            return articles

        except Exception as e:
            logger.error(f"Error scraping {self.base_url}: {e}")
            return []

    @abstractmethod
    def _extract_articles_from_page(self, soup: BeautifulSoup, limit: int) -> List[Article]:
        """Método específico para cada site"""
        pass


class TechCrunchScraper(WebScraper):
    """Scraper específico para TechCrunch"""

    def _extract_articles_from_page(self, soup: BeautifulSoup, limit: int) -> List[Article]:
        articles = []

        # TechCrunch specific selectors
        article_elements = soup.select('.post-block')[:limit]

        for element in article_elements:
            try:
                title_elem = element.select_one('h2 a, .post-block__title a')
                if not title_elem:
                    continue

                title = self.clean_text(title_elem.get_text())
                url = title_elem.get('href', '')
                if url and not url.startswith('http'):
                    url = urljoin(self.base_url, url)

                # Extract summary
                summary_elem = element.select_one('.post-block__content, .excerpt')
                summary = self.clean_text(summary_elem.get_text()) if summary_elem else ""

                # Extract author
                author_elem = element.select_one('.post-block__author, .author')
                author = self.clean_text(author_elem.get_text()) if author_elem else None

                article = Article(
                    title=title,
                    url=url,
                    source=self.source_name,
                    author=author,
                    summary=summary,
                    category="Technology"
                )

                articles.append(article)

            except Exception as e:
                logger.warning(f"Error extracting article: {e}")
                continue

        return articles