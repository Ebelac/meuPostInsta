"""
Agregador de notícias que coordena múltiplos scrapers
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_scraper import Article, RSSFeedScraper, TechCrunchScraper
from .reddit_scraper import RedditScraper
from config.settings import settings
from src.database import db_manager, NewsArticle

logger = logging.getLogger(__name__)


class NewsAggregator:
    """Agregador principal de notícias tech"""

    def __init__(self):
        self.scrapers = self._initialize_scrapers()

    def _initialize_scrapers(self) -> Dict[str, object]:
        """Inicializa todos os scrapers configurados"""
        scrapers = {}

        # RSS Feeds
        rss_sources = {
            "TechCrunch": "https://techcrunch.com/feed/",
            "The Verge": "https://www.theverge.com/rss/index.xml",
            "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
            "VentureBeat": "https://feeds.feedburner.com/venturebeat/SZYF",
            "O'Reilly Radar": "https://feeds.feedburner.com/oreilly/radar",
            "Hacker News": "https://hnrss.org/frontpage",
            "Dev.to": "https://dev.to/feed",
            "Medium Tech": "https://medium.com/feed/tag/technology",
            "TecMundo": "https://www.tecmundo.com.br/rss",
            "Olhar Digital": "https://olhardigital.com.br/feed/"
        }

        for name, url in rss_sources.items():
            scrapers[name] = RSSFeedScraper(name, url, delay=1.5)

        # Scrapers específicos
        scrapers["TechCrunch_Web"] = TechCrunchScraper(
            "TechCrunch",
            "https://techcrunch.com/",
            delay=2.0
        )

        # Reddit
        if settings.reddit_client_id and settings.reddit_client_secret:
            scrapers["Reddit"] = RedditScraper()

        logger.info(f"Initialized {len(scrapers)} scrapers")
        return scrapers

    def scrape_all_sources(self, articles_per_source: int = 10) -> List[Article]:
        """Scrape artigos de todas as fontes em paralelo"""
        all_articles = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submeter tarefas
            future_to_scraper = {
                executor.submit(scraper.scrape_articles, articles_per_source): name
                for name, scraper in self.scrapers.items()
            }

            # Coletar resultados
            for future in as_completed(future_to_scraper):
                scraper_name = future_to_scraper[future]
                try:
                    articles = future.result(timeout=60)  # 1 minute timeout
                    all_articles.extend(articles)
                    logger.info(f"{scraper_name}: {len(articles)} articles")
                except Exception as e:
                    logger.error(f"Error in {scraper_name}: {e}")

        # Remover duplicatas e filtrar
        unique_articles = self._remove_duplicates(all_articles)
        filtered_articles = self._filter_articles(unique_articles)

        logger.info(f"Total: {len(filtered_articles)} unique articles after filtering")
        return filtered_articles

    def _remove_duplicates(self, articles: List[Article]) -> List[Article]:
        """Remove artigos duplicados baseado na URL"""
        seen_urls = set()
        unique_articles = []

        for article in articles:
            if article.url and article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        return unique_articles

    def _filter_articles(self, articles: List[Article]) -> List[Article]:
        """Filtra artigos por relevância e qualidade"""
        filtered = []

        # Palavras-chave tech relevantes
        tech_keywords = {
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'python', 'javascript', 'react', 'nodejs', 'docker', 'kubernetes',
            'cloud', 'aws', 'azure', 'gcp', 'devops', 'cybersecurity',
            'blockchain', 'cryptocurrency', 'web development', 'mobile',
            'ios', 'android', 'flutter', 'react native', 'api',
            'database', 'sql', 'nosql', 'mongodb', 'postgresql',
            'frontend', 'backend', 'fullstack', 'framework',
            'agile', 'scrum', 'git', 'github', 'open source',
            'startup', 'tech news', 'programming', 'coding',
            'software', 'hardware', 'innovation', 'technology'
        }

        for article in articles:
            if self._is_tech_relevant(article, tech_keywords):
                filtered.append(article)

        return filtered

    def _is_tech_relevant(self, article: Article, keywords: set) -> bool:
        """Verifica se o artigo é relevante para tech"""
        text_to_check = f"{article.title} {article.summary or ''} {article.content or ''}".lower()

        # Verificar se contém palavras-chave tech
        for keyword in keywords:
            if keyword in text_to_check:
                return True

        # Verificar categorias
        if article.category:
            tech_categories = ['technology', 'tech', 'programming', 'ai', 'software']
            if any(cat in article.category.lower() for cat in tech_categories):
                return True

        return False

    def save_articles_to_db(self, articles: List[Article]) -> int:
        """Salva artigos no banco de dados"""
        saved_count = 0

        with db_manager.get_session() as session:
            for article in articles:
                try:
                    # Verificar se já existe
                    existing = session.query(NewsArticle).filter_by(url=article.url).first()
                    if existing:
                        continue

                    # Criar novo registro
                    db_article = NewsArticle(
                        title=article.title,
                        url=article.url,
                        source=article.source,
                        author=article.author,
                        published_date=article.published_date,
                        summary=article.summary,
                        content=article.content,
                        category=article.category,
                        tags=article.tags
                    )

                    session.add(db_article)
                    saved_count += 1

                except Exception as e:
                    logger.error(f"Error saving article {article.url}: {e}")

        logger.info(f"Saved {saved_count} new articles to database")
        return saved_count

    def run_scraping_cycle(self) -> Dict[str, int]:
        """Executa ciclo completo de scraping"""
        start_time = datetime.now()
        logger.info("Starting scraping cycle")

        try:
            # Scrape articles
            articles = self.scrape_all_sources(articles_per_source=15)

            # Save to database
            saved_count = self.save_articles_to_db(articles)

            # Statistics
            duration = datetime.now() - start_time
            stats = {
                'total_scraped': len(articles),
                'new_articles': saved_count,
                'duration_seconds': duration.total_seconds(),
                'sources_scraped': len(self.scrapers)
            }

            logger.info(f"Scraping cycle completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error in scraping cycle: {e}")
            return {'error': str(e)}

    def get_recent_articles(self, hours: int = 24, limit: int = 50) -> List[NewsArticle]:
        """Recupera artigos recentes do banco de dados"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with db_manager.get_session() as session:
            articles = session.query(NewsArticle).filter(
                NewsArticle.scraped_date >= cutoff_time
            ).order_by(
                NewsArticle.scraped_date.desc()
            ).limit(limit).all()

            return articles

    def get_articles_by_category(self, category: str, limit: int = 20) -> List[NewsArticle]:
        """Recupera artigos por categoria"""
        with db_manager.get_session() as session:
            articles = session.query(NewsArticle).filter(
                NewsArticle.category.ilike(f'%{category}%')
            ).filter(
                NewsArticle.is_used == False
            ).order_by(
                NewsArticle.scraped_date.desc()
            ).limit(limit).all()

            return articles


if __name__ == "__main__":
    # Teste do agregador
    logging.basicConfig(level=logging.INFO)

    aggregator = NewsAggregator()
    stats = aggregator.run_scraping_cycle()
    print(f"Scraping completed: {stats}")