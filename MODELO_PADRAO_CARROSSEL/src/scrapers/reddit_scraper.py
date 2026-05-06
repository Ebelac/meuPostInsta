"""
Scraper para Reddit (r/programming, r/technology, etc.)
"""
import praw
from typing import List, Optional
from datetime import datetime
import logging

from .base_scraper import Article, BaseScraper
from config.settings import settings

logger = logging.getLogger(__name__)


class RedditScraper(BaseScraper):
    """Scraper para subreddits de tecnologia"""

    def __init__(self):
        super().__init__("Reddit", "https://reddit.com", delay=1.0)
        self.reddit = None
        self._initialize_reddit()

    def _initialize_reddit(self):
        """Inicializa cliente Reddit"""
        try:
            if not (settings.reddit_client_id and settings.reddit_client_secret):
                logger.warning("Reddit credentials not configured")
                return

            self.reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent="InstaCalebeDigital:v1.0 (by /u/instacalebe)"
            )

            # Test connection
            self.reddit.user.me()
            logger.info("Reddit client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            self.reddit = None

    def scrape_articles(self, limit: int = 10) -> List[Article]:
        """Scrape articles from tech subreddits"""
        if not self.reddit:
            logger.warning("Reddit client not available")
            return []

        all_articles = []
        subreddits = [
            'programming',
            'technology',
            'MachineLearning',
            'artificial',
            'webdev',
            'javascript',
            'Python',
            'reactjs',
            'node',
            'cybersecurity',
            'datascience',
            'devops',
            'startups'
        ]

        for subreddit_name in subreddits:
            try:
                articles = self._scrape_subreddit(subreddit_name, limit=5)
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error scraping r/{subreddit_name}: {e}")

        return all_articles[:limit]

    def _scrape_subreddit(self, subreddit_name: str, limit: int = 5) -> List[Article]:
        """Scrape específico subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            articles = []

            # Get hot posts
            for submission in subreddit.hot(limit=limit):
                # Skip stickied posts and self posts without external links
                if submission.stickied:
                    continue

                # For self posts, use Reddit URL
                url = submission.url
                if submission.is_self:
                    url = f"https://reddit.com{submission.permalink}"

                # Skip if it's just an image or video
                if any(url.lower().endswith(ext) for ext in ['.jpg', '.png', '.gif', '.mp4', '.webm']):
                    continue

                article = Article(
                    title=self.clean_text(submission.title),
                    url=url,
                    source=f"Reddit r/{subreddit_name}",
                    author=str(submission.author) if submission.author else None,
                    published_date=datetime.fromtimestamp(submission.created_utc),
                    summary=self.clean_text(submission.selftext[:500]) if submission.selftext else None,
                    category=self._map_subreddit_to_category(subreddit_name),
                    tags=[subreddit_name]
                )

                # Add Reddit-specific metadata
                article.reddit_score = submission.score
                article.reddit_comments = submission.num_comments

                articles.append(article)

            logger.info(f"Scraped {len(articles)} articles from r/{subreddit_name}")
            return articles

        except Exception as e:
            logger.error(f"Error scraping r/{subreddit_name}: {e}")
            return []

    def _map_subreddit_to_category(self, subreddit_name: str) -> str:
        """Mapeia subreddit para categoria"""
        category_mapping = {
            'programming': 'Programming',
            'technology': 'Technology',
            'MachineLearning': 'AI',
            'artificial': 'AI',
            'webdev': 'Web Development',
            'javascript': 'Web Development',
            'Python': 'Programming',
            'reactjs': 'Web Development',
            'node': 'Web Development',
            'cybersecurity': 'Cybersecurity',
            'datascience': 'Data Science',
            'devops': 'DevOps',
            'startups': 'Startups'
        }

        return category_mapping.get(subreddit_name, 'Technology')

    def get_trending_topics(self, subreddit_name: str = 'programming') -> List[str]:
        """Obtém tópicos em alta de um subreddit"""
        if not self.reddit:
            return []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            topics = []

            for submission in subreddit.hot(limit=20):
                if submission.stickied:
                    continue

                # Extract keywords from title
                words = submission.title.lower().split()
                tech_words = [
                    word for word in words
                    if len(word) > 3 and word.isalpha()
                ]
                topics.extend(tech_words[:3])  # First 3 relevant words

            # Count frequency and return most common
            from collections import Counter
            common_topics = Counter(topics).most_common(10)
            return [topic for topic, count in common_topics if count > 1]

        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []


if __name__ == "__main__":
    # Teste do scraper Reddit
    logging.basicConfig(level=logging.INFO)

    scraper = RedditScraper()
    if scraper.reddit:
        articles = scraper.scrape_articles(limit=20)
        print(f"Found {len(articles)} articles")

        for article in articles[:5]:
            print(f"- {article.title}")
            print(f"  Source: {article.source}")
            print(f"  URL: {article.url}")
            print(f"  Category: {article.category}")
            print()
    else:
        print("Reddit client not configured")