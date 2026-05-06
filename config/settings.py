"""
Configurações centralizadas do InstaCalebeDigital
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações principais da aplicação"""

    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    news_api_key: Optional[str] = Field(None, env="NEWS_API_KEY")

    # Instagram
    instagram_username: str = Field(..., env="INSTAGRAM_USERNAME")
    instagram_password: str = Field(..., env="INSTAGRAM_PASSWORD")

    # Reddit API (para r/programming, r/technology)
    reddit_client_id: Optional[str] = Field(None, env="REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = Field(None, env="REDDIT_CLIENT_SECRET")

    # Database
    database_url: str = Field("sqlite:///./instagram_automation.db", env="DATABASE_URL")

    # Celery/Redis
    celery_broker_url: str = Field("redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field("redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")

    # Content Settings
    max_posts_per_day: int = Field(3, env="MAX_POSTS_PER_DAY")
    post_schedule_times: List[str] = Field(["09:00", "14:00", "19:00"], env="POST_SCHEDULE_TIMES")
    content_categories: List[str] = Field(
        ["AI", "Machine Learning", "Web Development", "Mobile", "Cybersecurity"],
        env="CONTENT_CATEGORIES"
    )

    # Design Settings
    brand_color_primary: str = Field("#1DA1F2", env="BRAND_COLOR_PRIMARY")
    brand_color_secondary: str = Field("#14171A", env="BRAND_COLOR_SECONDARY")
    brand_font: str = Field("Arial", env="BRAND_FONT")
    logo_path: str = Field("./assets/logo.png", env="LOGO_PATH")

    # Content Quality Settings
    min_article_score: float = Field(0.7, env="MIN_ARTICLE_SCORE")
    max_articles_per_source: int = Field(5, env="MAX_ARTICLES_PER_SOURCE")
    content_freshness_hours: int = Field(24, env="CONTENT_FRESHNESS_HOURS")

    # Instagram Settings
    carousel_slide_count: int = Field(5, env="CAROUSEL_SLIDE_COUNT")
    max_caption_length: int = Field(2200, env="MAX_CAPTION_LENGTH")
    hashtag_count: int = Field(25, env="HASHTAG_COUNT")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


class NewsSourceSettings(BaseSettings):
    """Configurações específicas para fontes de notícias"""

    # Tech News Sites
    tech_news_sources: List[str] = Field(default=[
        "https://techcrunch.com/feed/",
        "https://feeds.feedburner.com/oreilly/radar",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.feedburner.com/venturebeat/SZYF",
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.feedburner.com/Techcrunch",
        "https://feeds.arstechnica.com/arstechnica/index",
    ], env="TECH_NEWS_SOURCES")

    # Brazilian Tech Sources
    br_tech_sources: List[str] = Field(default=[
        "https://www.tecmundo.com.br/rss",
        "https://olhardigital.com.br/feed/",
        "https://www.terra.com.br/rss/tecnologia.xml",
    ], env="BR_TECH_SOURCES")

    # Developer Communities
    dev_communities: List[str] = Field(default=[
        "https://dev.to/feed",
        "https://hackernoon.com/feed",
        "https://medium.com/feed/tag/technology",
    ], env="DEV_COMMUNITIES")

    # Update intervals (in minutes)
    scraping_interval: int = Field(default=60, env="SCRAPING_INTERVAL")
    curation_interval: int = Field(default=120, env="CURATION_INTERVAL")

    model_config = {"env_file": ".env", "extra": "ignore"}


# Singleton instance
settings = Settings()
news_settings = NewsSourceSettings()