"""
Sistema principal de curadoria de conteúdo
"""
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
import logging
from collections import defaultdict

from .content_scorer import ContentScorer
from src.database import db_manager, NewsArticle, InstagramPost, ScheduleConfig
from config.settings import settings

logger = logging.getLogger(__name__)


class ContentCurator:
    """Sistema principal de curadoria inteligente de conteúdo"""

    def __init__(self):
        self.scorer = ContentScorer()
        self.min_score_threshold = settings.min_article_score
        self.max_articles_per_source = settings.max_articles_per_source

    def curate_daily_content(self, target_posts: int = 3) -> List[Dict]:
        """Seleciona e cura conteúdo para o dia"""
        logger.info(f"Starting daily curation for {target_posts} posts")

        # 1. Obter artigos candidatos
        candidate_articles = self._get_candidate_articles()
        logger.info(f"Found {len(candidate_articles)} candidate articles")

        if not candidate_articles:
            logger.warning("No candidate articles found")
            return []

        # 2. Pontuar e rankear artigos (converter para lista para evitar problemas de sessão)
        articles_list = list(candidate_articles)
        ranked_articles = self.scorer.rank_articles(articles_list)

        # 3. Filtrar por pontuação mínima
        filtered_articles = [
            (article, scores) for article, scores in ranked_articles
            if scores['final_score'] >= self.min_score_threshold
        ]
        logger.info(f"After score filtering: {len(filtered_articles)} articles")

        # 4. Aplicar diversidade de categoria
        diverse_articles = self._ensure_category_diversity(filtered_articles)

        # 5. Evitar duplicação de fonte
        final_articles = self._avoid_source_duplication(diverse_articles, target_posts)

        # 6. Marcar artigos como curados
        self._mark_articles_as_curated([article for article, _ in final_articles])

        # 7. Preparar dados para geração de conteúdo
        curated_content = []
        for article, scores in final_articles:
            content_data = self._prepare_content_data(article, scores)
            curated_content.append(content_data)

        logger.info(f"Final curation: {len(curated_content)} articles selected")
        return curated_content

    def _get_candidate_articles(self) -> List[NewsArticle]:
        """Obtém artigos candidatos para curadoria"""
        cutoff_time = datetime.now() - timedelta(hours=settings.content_freshness_hours)

        with db_manager.get_session() as session:
            articles = session.query(NewsArticle).filter(
                NewsArticle.scraped_date >= cutoff_time,
                NewsArticle.is_curated == False,
                NewsArticle.is_used == False
            ).all()

            # Fazer expunge para desvinculat da sessão
            for article in articles:
                session.expunge(article)

        return articles

    def _ensure_category_diversity(self, ranked_articles: List[tuple]) -> List[tuple]:
        """Garante diversidade de categorias"""
        if not ranked_articles:
            return []

        # Configuração de distribuição desejada
        target_distribution = None
        with db_manager.get_session() as session:
            schedule_config = session.query(ScheduleConfig).filter(
                ScheduleConfig.is_active == True
            ).first()

            if schedule_config and schedule_config.category_distribution:
                target_distribution = schedule_config.category_distribution

        if not target_distribution:
            # Distribuição padrão
            target_distribution = {
                'AI': 30, 'Machine Learning': 25, 'Web Development': 20,
                'Mobile': 15, 'Cybersecurity': 10
            }

        # Agrupar por categoria
        by_category = defaultdict(list)
        for article, scores in ranked_articles:
            category = article.category or 'Technology'
            by_category[category].append((article, scores))

        # Selecionar proporcionalmente
        diverse_articles = []
        total_articles_needed = min(20, len(ranked_articles))  # Máximo 20 para próxima fase

        for category, percentage in target_distribution.items():
            target_count = int((percentage / 100) * total_articles_needed)
            if category in by_category:
                selected = by_category[category][:target_count]
                diverse_articles.extend(selected)

        # Preencher restante com artigos top-rated
        remaining_slots = total_articles_needed - len(diverse_articles)
        if remaining_slots > 0:
            used_articles = {article.id for article, _ in diverse_articles}
            for article, scores in ranked_articles:
                if len(diverse_articles) >= total_articles_needed:
                    break
                if article.id not in used_articles:
                    diverse_articles.append((article, scores))

        return diverse_articles

    def _avoid_source_duplication(self, articles: List[tuple], target_count: int) -> List[tuple]:
        """Evita muitos artigos da mesma fonte"""
        source_count = defaultdict(int)
        final_articles = []

        for article, scores in articles:
            if len(final_articles) >= target_count:
                break

            source = article.source
            if source_count[source] < self.max_articles_per_source:
                final_articles.append((article, scores))
                source_count[source] += 1

        return final_articles

    def _mark_articles_as_curated(self, articles: List[NewsArticle]):
        """Marca artigos como curados"""
        with db_manager.get_session() as session:
            for article in articles:
                db_article = session.query(NewsArticle).filter(
                    NewsArticle.id == article.id
                ).first()
                if db_article:
                    db_article.is_curated = True

    def _prepare_content_data(self, article: NewsArticle, scores: Dict[str, float]) -> Dict:
        """Prepara dados do artigo para geração de conteúdo"""
        # Determinar template baseado na categoria
        template_mapping = {
            'AI': 'AI/ML Focus',
            'Machine Learning': 'AI/ML Focus',
            'Web Development': 'Dev Community',
            'Programming': 'Dev Community',
            'Mobile': 'Tech News Standard',
            'Cybersecurity': 'Tech News Standard'
        }

        template_name = template_mapping.get(article.category, 'Tech News Standard')

        # Extrair pontos-chave do conteúdo
        key_points = self._extract_key_points(article)

        # Sugerir hashtags baseadas no conteúdo
        suggested_hashtags = self._suggest_hashtags(article)

        content_data = {
            'article_id': article.id,
            'title': article.title,
            'original_url': article.url,
            'source': article.source,
            'author': article.author,
            'published_date': article.published_date,
            'summary': article.summary,
            'content': article.content,
            'category': article.category,
            'scores': scores,
            'template_name': template_name,
            'key_points': key_points,
            'suggested_hashtags': suggested_hashtags,
            'content_type': self._determine_content_type(article, scores),
            'priority': self._calculate_priority(scores),
            'estimated_engagement': self._estimate_engagement(scores)
        }

        return content_data

    def _extract_key_points(self, article: NewsArticle) -> List[str]:
        """Extrai pontos-chave do artigo"""
        content = article.content or article.summary or ""
        if not content:
            return []

        # Simples extração baseada em estrutura
        points = []

        # Procurar por listas
        import re
        list_patterns = [
            r'(?:^|\n)[-•*]\s*([^\n]+)',  # Bullet points
            r'(?:^|\n)\d+\.\s*([^\n]+)',  # Numbered lists
        ]

        for pattern in list_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            points.extend([match.strip() for match in matches[:3]])

        # Se não encontrar listas, usar primeiras frases
        if not points:
            sentences = content.split('.')[:5]
            points = [s.strip() for s in sentences if len(s.strip()) > 20]

        return points[:4]  # Máximo 4 pontos

    def _suggest_hashtags(self, article: NewsArticle) -> List[str]:
        """Sugere hashtags baseadas no conteúdo"""
        text = f"{article.title} {article.summary or ''}".lower()
        hashtags = set()

        # Hashtags básicas por categoria
        category_hashtags = {
            'AI': ['#AI', '#ArtificialIntelligence', '#MachineLearning', '#Tech'],
            'Machine Learning': ['#MachineLearning', '#AI', '#DataScience', '#Tech'],
            'Web Development': ['#WebDev', '#Programming', '#JavaScript', '#Tech'],
            'Mobile': ['#MobileDev', '#iOS', '#Android', '#Apps'],
            'Cybersecurity': ['#Cybersecurity', '#InfoSec', '#Security', '#Tech']
        }

        # Adicionar hashtags da categoria
        category = article.category or 'Technology'
        if category in category_hashtags:
            hashtags.update(category_hashtags[category])

        # Hashtags baseadas em palavras-chave
        keyword_hashtags = {
            'python': '#Python',
            'javascript': '#JavaScript',
            'react': '#React',
            'nodejs': '#NodeJS',
            'docker': '#Docker',
            'kubernetes': '#Kubernetes',
            'aws': '#AWS',
            'azure': '#Azure',
            'gcp': '#GCP',
            'blockchain': '#Blockchain',
            'cryptocurrency': '#Crypto',
            'startup': '#Startup',
            'iot': '#IoT',
            'cloud': '#Cloud',
            'devops': '#DevOps'
        }

        for keyword, hashtag in keyword_hashtags.items():
            if keyword in text:
                hashtags.add(hashtag)

        # Hashtags gerais para engagement
        general_hashtags = ['#Tech', '#Innovation', '#Technology', '#Programming', '#Developer']
        hashtags.update(general_hashtags[:2])  # Adicionar 2 gerais

        return list(hashtags)[:15]  # Máximo 15 hashtags

    def _determine_content_type(self, article: NewsArticle, scores: Dict[str, float]) -> str:
        """Determina o tipo de conteúdo a ser criado"""
        text = f"{article.title} {article.summary or ''}".lower()

        if 'tutorial' in text or 'how to' in text:
            return 'tutorial'
        elif 'review' in text or 'comparison' in text:
            return 'review'
        elif scores['engagement_potential'] > 7.0:
            return 'viral'
        elif scores['virality'] > 6.0:
            return 'trending'
        else:
            return 'news'

    def _calculate_priority(self, scores: Dict[str, float]) -> str:
        """Calcula prioridade do conteúdo"""
        final_score = scores['final_score']

        if final_score >= 8.5:
            return 'high'
        elif final_score >= 7.0:
            return 'medium'
        else:
            return 'low'

    def _estimate_engagement(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Estima métricas de engajamento"""
        engagement_score = scores['engagement_potential']
        virality_score = scores['virality']

        base_likes = 100
        base_comments = 10
        base_shares = 5

        # Multiplicadores baseados nas pontuações
        likes_multiplier = 1 + (engagement_score / 10) * 3
        comments_multiplier = 1 + (engagement_score / 10) * 2
        shares_multiplier = 1 + (virality_score / 10) * 4

        return {
            'estimated_likes': int(base_likes * likes_multiplier),
            'estimated_comments': int(base_comments * comments_multiplier),
            'estimated_shares': int(base_shares * shares_multiplier)
        }

    def get_curation_stats(self) -> Dict:
        """Retorna estatísticas de curadoria"""
        with db_manager.get_session() as session:
            # Artigos por status
            total_articles = session.query(NewsArticle).count()
            curated_articles = session.query(NewsArticle).filter(
                NewsArticle.is_curated == True
            ).count()
            used_articles = session.query(NewsArticle).filter(
                NewsArticle.is_used == True
            ).count()

            # Artigos recentes
            last_24h = datetime.now() - timedelta(hours=24)
            recent_articles = session.query(NewsArticle).filter(
                NewsArticle.scraped_date >= last_24h
            ).count()

            # Por categoria
            category_stats = self.scorer.get_category_distribution(
                session.query(NewsArticle).filter(
                    NewsArticle.scraped_date >= last_24h
                ).all()
            )

        return {
            'total_articles': total_articles,
            'curated_articles': curated_articles,
            'used_articles': used_articles,
            'recent_articles': recent_articles,
            'category_distribution': category_stats,
            'curation_rate': (curated_articles / total_articles * 100) if total_articles > 0 else 0
        }


if __name__ == "__main__":
    # Teste da curadoria
    logging.basicConfig(level=logging.INFO)

    curator = ContentCurator()
    curated_content = curator.curate_daily_content(target_posts=5)

    print(f"Curated {len(curated_content)} articles:")
    for content in curated_content:
        print(f"\n- {content['title']}")
        print(f"  Score: {content['scores']['final_score']:.2f}")
        print(f"  Category: {content['category']}")
        print(f"  Priority: {content['priority']}")
        print(f"  Template: {content['template_name']}")

    stats = curator.get_curation_stats()
    print(f"\nCuration Stats: {stats}")