"""
Sistema de pontuação e rankeamento de conteúdo
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re
import math
import logging
from textstat import flesch_reading_ease, flesch_kincaid_grade

from src.database.models import NewsArticle
from config.settings import settings

logger = logging.getLogger(__name__)


class ContentScorer:
    """Sistema de pontuação de qualidade de conteúdo"""

    def __init__(self):
        self.tech_keywords = self._load_tech_keywords()
        self.trending_keywords = self._load_trending_keywords()
        self.engagement_keywords = self._load_engagement_keywords()

    def _load_tech_keywords(self) -> Dict[str, float]:
        """Carrega palavras-chave tech com pesos"""
        return {
            # AI/ML (alto peso)
            'artificial intelligence': 5.0,
            'machine learning': 5.0,
            'deep learning': 4.5,
            'neural network': 4.0,
            'chatgpt': 4.5,
            'gpt': 4.0,
            'openai': 4.0,
            'llm': 3.5,
            'transformer': 3.5,

            # Programming (peso médio-alto)
            'python': 3.0,
            'javascript': 3.0,
            'react': 3.5,
            'nextjs': 3.5,
            'nodejs': 3.0,
            'typescript': 3.0,
            'vue': 2.5,
            'angular': 2.5,
            'svelte': 2.8,

            # Cloud/Infrastructure
            'aws': 3.5,
            'azure': 3.0,
            'gcp': 3.0,
            'docker': 3.5,
            'kubernetes': 4.0,
            'serverless': 3.0,
            'microservices': 3.5,
            'devops': 3.0,

            # Mobile
            'ios': 2.5,
            'android': 2.5,
            'flutter': 3.0,
            'react native': 3.0,
            'swift': 2.5,
            'kotlin': 2.5,

            # Web3/Crypto
            'blockchain': 3.0,
            'cryptocurrency': 2.5,
            'nft': 2.0,
            'web3': 3.5,
            'ethereum': 2.5,
            'bitcoin': 2.0,

            # Emerging Tech
            'quantum': 4.0,
            'augmented reality': 3.5,
            'virtual reality': 3.5,
            'metaverse': 2.5,
            'iot': 3.0,
            '5g': 2.5,

            # Cybersecurity
            'cybersecurity': 4.0,
            'security': 3.0,
            'vulnerability': 3.5,
            'encryption': 3.0,
            'zero trust': 3.5,

            # Business Tech
            'startup': 3.0,
            'unicorn': 2.5,
            'ipo': 2.5,
            'funding': 2.0,
            'venture capital': 2.0,
        }

    def _load_trending_keywords(self) -> Dict[str, float]:
        """Palavras-chave que estão em alta (atualizadas dinamicamente)"""
        return {
            'ai tools': 4.5,
            'github copilot': 4.0,
            'claude': 4.0,
            'midjourney': 3.5,
            'stable diffusion': 3.5,
            'edge computing': 3.5,
            'sustainability tech': 3.0,
            'green tech': 3.0,
        }

    def _load_engagement_keywords(self) -> Dict[str, float]:
        """Palavras que geram engajamento no Instagram"""
        return {
            # Ação/Tutorial
            'tutorial': 2.0,
            'guide': 2.0,
            'how to': 2.5,
            'step by step': 2.0,
            'tips': 2.5,
            'tricks': 2.0,
            'hack': 2.0,

            # Novidade/Urgência
            'new': 1.5,
            'latest': 1.5,
            'breaking': 2.0,
            'announced': 1.5,
            'released': 1.8,
            'launch': 2.0,

            # Comparação
            'vs': 1.5,
            'comparison': 1.5,
            'better': 1.5,
            'faster': 1.8,
            'best': 2.0,
            'top': 1.8,

            # Experiência
            'review': 1.5,
            'experience': 1.5,
            'tested': 1.8,
            'real world': 1.8,
        }

    def score_article(self, article: NewsArticle) -> Dict[str, float]:
        """Calcula pontuação completa de um artigo"""
        scores = {
            'relevance': self._score_relevance(article),
            'quality': self._score_quality(article),
            'engagement_potential': self._score_engagement_potential(article),
            'freshness': self._score_freshness(article),
            'readability': self._score_readability(article),
            'virality': self._score_virality(article)
        }

        # Pontuação final ponderada
        weights = {
            'relevance': 0.25,
            'quality': 0.20,
            'engagement_potential': 0.20,
            'freshness': 0.15,
            'readability': 0.10,
            'virality': 0.10
        }

        final_score = sum(scores[key] * weights[key] for key in scores)
        scores['final_score'] = min(final_score, 10.0)  # Cap at 10

        return scores

    def _score_relevance(self, article: NewsArticle) -> float:
        """Pontuação baseada em relevância tech (0-10)"""
        text = f"{article.title} {article.summary or ''} {article.content or ''}".lower()

        total_score = 0
        matched_keywords = 0

        # Score tech keywords
        for keyword, weight in self.tech_keywords.items():
            if keyword in text:
                total_score += weight
                matched_keywords += 1

        # Score trending keywords (bonus)
        for keyword, weight in self.trending_keywords.items():
            if keyword in text:
                total_score += weight * 1.2  # 20% bonus for trending

        # Normalize based on text length and keyword diversity
        if matched_keywords == 0:
            return 0.0

        # Bonus for keyword diversity
        diversity_bonus = min(matched_keywords * 0.5, 3.0)
        final_score = (total_score / matched_keywords) + diversity_bonus

        return min(final_score, 10.0)

    def _score_quality(self, article: NewsArticle) -> float:
        """Pontuação baseada na qualidade do conteúdo (0-10)"""
        score = 5.0  # Base score

        # Title quality
        if article.title:
            title_len = len(article.title)
            if 30 <= title_len <= 100:  # Ideal title length
                score += 1.0
            elif title_len < 20 or title_len > 120:
                score -= 1.0

        # Content length
        content_text = article.content or article.summary or ""
        if content_text:
            word_count = len(content_text.split())
            if 200 <= word_count <= 1000:  # Good content length
                score += 1.5
            elif word_count < 50:
                score -= 2.0
            elif word_count > 2000:
                score -= 0.5

        # Source credibility
        credible_sources = [
            'techcrunch', 'theverge', 'arstechnica', 'wired',
            'venturebeat', 'engadget', 'gizmodo', 'dev.to',
            'medium', 'hackernoon'
        ]
        if any(source in article.source.lower() for source in credible_sources):
            score += 1.0

        # Has author
        if article.author and len(article.author.strip()) > 0:
            score += 0.5

        # Recent publication
        if article.published_date:
            days_old = (datetime.now() - article.published_date).days
            if days_old <= 1:
                score += 1.0
            elif days_old <= 7:
                score += 0.5

        return min(max(score, 0.0), 10.0)

    def _score_engagement_potential(self, article: NewsArticle) -> float:
        """Pontuação baseada no potencial de engajamento (0-10)"""
        text = f"{article.title} {article.summary or ''}".lower()
        score = 3.0  # Base score

        # Engagement keywords
        for keyword, weight in self.engagement_keywords.items():
            if keyword in text:
                score += weight

        # Question in title (gera curiosidade)
        if '?' in article.title:
            score += 1.5

        # Numbers in title (listicles performam bem)
        if re.search(r'\d+', article.title):
            score += 1.0

        # Controversy/debate words
        controversy_words = ['controversial', 'debate', 'opinion', 'why', 'problem']
        if any(word in text for word in controversy_words):
            score += 0.8

        # Visual potential (mentions of images, demos, etc)
        visual_words = ['demo', 'screenshot', 'video', 'visual', 'example', 'showcase']
        if any(word in text for word in visual_words):
            score += 1.2

        return min(score, 10.0)

    def _score_freshness(self, article: NewsArticle) -> float:
        """Pontuação baseada na atualidade (0-10)"""
        if not article.published_date:
            return 5.0  # Neutral score if no date

        now = datetime.now()
        if article.published_date.tzinfo:
            now = now.replace(tzinfo=article.published_date.tzinfo)

        hours_old = (now - article.published_date).total_seconds() / 3600

        if hours_old < 1:
            return 10.0  # Very fresh
        elif hours_old < 6:
            return 9.0
        elif hours_old < 24:
            return 7.5
        elif hours_old < 72:
            return 6.0
        elif hours_old < 168:  # 1 week
            return 4.0
        else:
            return 2.0  # Old news

    def _score_readability(self, article: NewsArticle) -> float:
        """Pontuação baseada na legibilidade (0-10)"""
        content = article.content or article.summary
        if not content or len(content) < 50:
            return 5.0

        try:
            # Flesch Reading Ease (higher = easier)
            ease_score = flesch_reading_ease(content)

            # Convert to 0-10 scale
            if ease_score >= 80:
                return 9.0  # Very easy
            elif ease_score >= 70:
                return 8.0  # Easy
            elif ease_score >= 60:
                return 7.0  # Standard
            elif ease_score >= 50:
                return 6.0  # Fairly difficult
            elif ease_score >= 40:
                return 4.0  # Difficult
            else:
                return 3.0  # Very difficult

        except:
            # Fallback: simple metrics
            words = content.split()
            avg_word_len = sum(len(word) for word in words) / len(words)

            if avg_word_len <= 4.5:
                return 8.0
            elif avg_word_len <= 6.0:
                return 6.0
            else:
                return 4.0

    def _score_virality(self, article: NewsArticle) -> float:
        """Pontuação baseada no potencial viral (0-10)"""
        text = f"{article.title} {article.summary or ''}".lower()
        score = 3.0

        # Emotion-triggering words
        emotion_words = {
            'shocking': 2.0, 'amazing': 1.5, 'incredible': 1.5,
            'breakthrough': 2.0, 'revolutionary': 1.8, 'game-changer': 1.8,
            'disaster': 1.5, 'crisis': 1.2, 'failure': 1.0,
            'success': 1.0, 'winner': 1.0, 'genius': 1.2
        }

        for word, weight in emotion_words.items():
            if word in text:
                score += weight

        # Superlatives
        superlatives = ['best', 'worst', 'first', 'last', 'only', 'never', 'always']
        superlative_count = sum(1 for word in superlatives if word in text)
        score += min(superlative_count * 0.5, 2.0)

        # Big tech companies (people love/hate them)
        big_tech = ['apple', 'google', 'microsoft', 'amazon', 'facebook', 'meta', 'twitter', 'tesla']
        if any(company in text for company in big_tech):
            score += 1.0

        return min(score, 10.0)

    def rank_articles(self, articles: List[NewsArticle], limit: Optional[int] = None) -> List[Tuple[NewsArticle, Dict[str, float]]]:
        """Rankeia artigos por pontuação"""
        scored_articles = []

        for article in articles:
            scores = self.score_article(article)
            scored_articles.append((article, scores))

        # Sort by final score
        scored_articles.sort(key=lambda x: x[1]['final_score'], reverse=True)

        if limit:
            scored_articles = scored_articles[:limit]

        return scored_articles

    def get_category_distribution(self, articles: List[NewsArticle]) -> Dict[str, int]:
        """Analisa distribuição de categorias"""
        categories = {}
        for article in articles:
            category = article.category or 'Uncategorized'
            categories[category] = categories.get(category, 0) + 1
        return categories


if __name__ == "__main__":
    # Teste do scorer
    from src.database import db_manager, NewsArticle

    scorer = ContentScorer()

    with db_manager.get_session() as session:
        articles = session.query(NewsArticle).limit(10).all()

        if articles:
            ranked = scorer.rank_articles(articles, limit=5)

            print("Top 5 Articles:")
            for article, scores in ranked:
                print(f"\nTitle: {article.title}")
                print(f"Score: {scores['final_score']:.2f}")
                print(f"Relevance: {scores['relevance']:.2f}")
                print(f"Quality: {scores['quality']:.2f}")
                print(f"Engagement: {scores['engagement_potential']:.2f}")
        else:
            print("No articles found in database")