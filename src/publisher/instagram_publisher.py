"""
Sistema de publicação automatizada no Instagram
"""
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, FeedbackRequired, TwoFactorRequired
from typing import List, Dict, Optional, Any
import logging
import time
import json
from pathlib import Path
from datetime import datetime

from config.settings import settings
from src.database import db_manager, InstagramPost, NewsArticle, PostStatus

logger = logging.getLogger(__name__)


class InstagramPublisher:
    """Sistema de publicação automatizada no Instagram"""

    def __init__(self):
        self.client = Client()
        self.session_file = "instagram_session.json"
        self.is_logged_in = False
        self._initialize_client()

    def _initialize_client(self):
        """Inicializa cliente Instagram"""
        try:
            # Tentar carregar sessão salva
            if Path(self.session_file).exists():
                logger.info("Loading saved Instagram session")
                self.client.load_settings(self.session_file)
                self.client.login(settings.instagram_username, settings.instagram_password)
            else:
                logger.info("Creating new Instagram session")
                self.client.login(settings.instagram_username, settings.instagram_password)
                self.client.dump_settings(self.session_file)

            self.is_logged_in = True
            logger.info("Instagram client initialized successfully")

        except (LoginRequired, ChallengeRequired, TwoFactorRequired) as e:
            logger.error(f"Instagram login failed: {e}")
            self.is_logged_in = False
        except Exception as e:
            logger.error(f"Instagram initialization failed: {e}")
            self.is_logged_in = False

    def publish_carousel_post(self, post_data: Dict) -> Dict[str, Any]:
        """Publica carrossel no Instagram"""
        if not self.is_logged_in:
            return {'success': False, 'error': 'Not logged in to Instagram'}

        try:
            logger.info(f"Publishing carousel post")

            # Preparar dados
            caption = self._prepare_caption(post_data)
            image_paths = post_data.get('carousel_images', [])

            if not image_paths:
                return {'success': False, 'error': 'No carousel images provided'}

            # Upload carrossel
            media = self.client.album_upload(
                paths=image_paths,
                caption=caption
            )

            if media:
                post_id = media.id
                post_url = f"https://instagram.com/p/{media.code}/"

                # Salvar no banco de dados
                db_post_id = self._save_post_to_db(post_data, post_id, post_url)

                logger.info(f"Carousel posted successfully: {post_url}")

                return {
                    'success': True,
                    'post_id': post_id,
                    'post_url': post_url,
                    'db_post_id': db_post_id,
                    'media_info': {
                        'id': media.id,
                        'code': media.code,
                        'media_type': media.media_type
                    }
                }

            else:
                return {'success': False, 'error': 'Failed to upload carousel'}

        except FeedbackRequired as e:
            logger.error(f"Instagram feedback required: {e}")
            return {'success': False, 'error': f'Instagram feedback required: {str(e)}'}

        except Exception as e:
            logger.error(f"Error publishing carousel: {e}")
            return {'success': False, 'error': str(e)}

    def publish_single_image_post(self, image_path: str, caption: str) -> Dict[str, Any]:
        """Publica imagem única no Instagram"""
        if not self.is_logged_in:
            return {'success': False, 'error': 'Not logged in to Instagram'}

        try:
            logger.info(f"Publishing single image post")

            media = self.client.photo_upload(
                path=image_path,
                caption=caption
            )

            if media:
                post_id = media.id
                post_url = f"https://instagram.com/p/{media.code}/"

                logger.info(f"Image posted successfully: {post_url}")

                return {
                    'success': True,
                    'post_id': post_id,
                    'post_url': post_url,
                    'media_info': {
                        'id': media.id,
                        'code': media.code
                    }
                }

            else:
                return {'success': False, 'error': 'Failed to upload image'}

        except Exception as e:
            logger.error(f"Error publishing image: {e}")
            return {'success': False, 'error': str(e)}

    def _prepare_caption(self, post_data: Dict) -> str:
        """Prepara caption combinando texto e hashtags"""
        caption_text = post_data.get('caption', '')
        hashtags = post_data.get('hashtags', [])

        # Combinar caption com hashtags
        full_caption = caption_text

        if hashtags:
            # Adicionar quebra de linha dupla antes das hashtags
            if not full_caption.endswith('\n\n'):
                full_caption += '\n\n'

            # Adicionar hashtags (máximo permitido pelo Instagram)
            hashtag_text = ' '.join(hashtags[:30])  # Instagram limit
            full_caption += hashtag_text

        # Verificar limite de caracteres do Instagram
        if len(full_caption) > 2200:
            # Truncar mantendo hashtags principais
            main_hashtags = hashtags[:10] if hashtags else []
            hashtag_text = ' '.join(main_hashtags)

            available_chars = 2200 - len(hashtag_text) - 4  # 4 para \n\n
            if available_chars > 0:
                truncated_caption = caption_text[:available_chars].rsplit(' ', 1)[0] + '...'
                full_caption = truncated_caption + '\n\n' + hashtag_text
            else:
                full_caption = hashtag_text

        return full_caption

    def _save_post_to_db(self, post_data: Dict, instagram_post_id: str, post_url: str) -> int:
        """Salva post no banco de dados"""
        with db_manager.get_session() as session:
            db_post = InstagramPost(
                post_id=instagram_post_id,
                caption=post_data.get('caption', ''),
                hashtags=post_data.get('hashtags', []),
                carousel_images=post_data.get('carousel_images', []),
                category=post_data.get('metadata', {}).get('category'),
                published_time=datetime.now(),
                status=PostStatus.PUBLISHED,
                source_article_id=post_data.get('source_article_id')
            )

            session.add(db_post)
            session.flush()  # Para obter o ID

            # Marcar artigo source como usado
            if post_data.get('source_article_id'):
                source_article = session.query(NewsArticle).filter(
                    NewsArticle.id == post_data.get('source_article_id')
                ).first()
                if source_article:
                    source_article.is_used = True

            return db_post.id

    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Obtém métricas de um post"""
        if not self.is_logged_in:
            return {'error': 'Not logged in'}

        try:
            # Obter informações do post
            media_info = self.client.media_info_by_shortcode(post_id)

            analytics = {
                'likes': media_info.like_count,
                'comments': media_info.comment_count,
                'views': getattr(media_info, 'view_count', 0),
                'reach': getattr(media_info, 'reach', 0),
                'impressions': getattr(media_info, 'impressions', 0),
                'saves': getattr(media_info, 'save_count', 0),
                'shares': getattr(media_info, 'share_count', 0),
                'engagement_rate': self._calculate_engagement_rate(media_info)
            }

            return analytics

        except Exception as e:
            logger.error(f"Error getting post analytics: {e}")
            return {'error': str(e)}

    def _calculate_engagement_rate(self, media_info) -> float:
        """Calcula taxa de engajamento"""
        try:
            likes = media_info.like_count or 0
            comments = media_info.comment_count or 0
            saves = getattr(media_info, 'save_count', 0)

            total_engagement = likes + comments + saves
            followers = self._get_follower_count()

            if followers > 0:
                return (total_engagement / followers) * 100
            else:
                return 0.0

        except:
            return 0.0

    def _get_follower_count(self) -> int:
        """Obtém número de seguidores"""
        try:
            user_info = self.client.user_info_by_username(settings.instagram_username)
            return user_info.follower_count
        except:
            return 1000  # Fallback

    def update_post_metrics(self, db_post_id: int) -> bool:
        """Atualiza métricas de um post no banco"""
        try:
            with db_manager.get_session() as session:
                post = session.query(InstagramPost).filter(
                    InstagramPost.id == db_post_id
                ).first()

                if not post or not post.post_id:
                    return False

                # Obter métricas atuais
                analytics = self.get_post_analytics(post.post_id)

                if 'error' not in analytics:
                    # Atualizar no banco
                    post.likes_count = analytics.get('likes', 0)
                    post.comments_count = analytics.get('comments', 0)
                    post.shares_count = analytics.get('shares', 0)
                    post.reach = analytics.get('reach', 0)
                    post.impressions = analytics.get('impressions', 0)

                    logger.info(f"Updated metrics for post {db_post_id}")
                    return True

                return False

        except Exception as e:
            logger.error(f"Error updating post metrics: {e}")
            return False

    def bulk_update_metrics(self) -> Dict[str, int]:
        """Atualiza métricas de todos os posts recentes"""
        updated_count = 0
        error_count = 0

        with db_manager.get_session() as session:
            # Posts dos últimos 30 dias
            recent_posts = session.query(InstagramPost).filter(
                InstagramPost.status == PostStatus.PUBLISHED,
                InstagramPost.published_time >= datetime.now() - timedelta(days=30)
            ).all()

            for post in recent_posts:
                try:
                    if self.update_post_metrics(post.id):
                        updated_count += 1
                    else:
                        error_count += 1

                    # Rate limiting
                    time.sleep(2)

                except Exception as e:
                    logger.error(f"Error updating metrics for post {post.id}: {e}")
                    error_count += 1

        return {
            'updated': updated_count,
            'errors': error_count,
            'total': len(recent_posts) if 'recent_posts' in locals() else 0
        }

    def get_account_insights(self) -> Dict[str, Any]:
        """Obtém insights da conta"""
        if not self.is_logged_in:
            return {'error': 'Not logged in'}

        try:
            # Informações básicas da conta
            user_info = self.client.user_info_by_username(settings.instagram_username)

            insights = {
                'followers': user_info.follower_count,
                'following': user_info.following_count,
                'posts': user_info.media_count,
                'bio': user_info.biography,
                'external_url': user_info.external_url,
                'is_verified': user_info.is_verified,
                'is_business': user_info.is_business
            }

            return insights

        except Exception as e:
            logger.error(f"Error getting account insights: {e}")
            return {'error': str(e)}

    def test_connection(self) -> Dict[str, Any]:
        """Testa conexão com Instagram"""
        try:
            if not self.is_logged_in:
                return {
                    'success': False,
                    'error': 'Not logged in'
                }

            # Tentar obter informações básicas
            user_info = self.client.user_info_by_username(settings.instagram_username)

            return {
                'success': True,
                'username': user_info.username,
                'followers': user_info.follower_count,
                'posts': user_info.media_count
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def logout(self):
        """Faz logout do Instagram"""
        try:
            self.client.logout()
            self.is_logged_in = False

            # Remover arquivo de sessão
            if Path(self.session_file).exists():
                Path(self.session_file).unlink()

            logger.info("Logged out from Instagram")

        except Exception as e:
            logger.error(f"Error during logout: {e}")


class PostScheduler:
    """Agendador de posts para publicação"""

    def __init__(self):
        self.publisher = InstagramPublisher()

    def schedule_post(self, post_data: Dict, scheduled_time: datetime) -> int:
        """Agenda um post para publicação"""
        with db_manager.get_session() as session:
            scheduled_post = InstagramPost(
                caption=post_data.get('caption', ''),
                hashtags=post_data.get('hashtags', []),
                carousel_images=post_data.get('carousel_images', []),
                category=post_data.get('metadata', {}).get('category'),
                scheduled_time=scheduled_time,
                status=PostStatus.SCHEDULED,
                source_article_id=post_data.get('source_article_id')
            )

            session.add(scheduled_post)
            session.flush()

            logger.info(f"Post scheduled for {scheduled_time}")
            return scheduled_post.id

    def publish_scheduled_posts(self) -> Dict[str, int]:
        """Publica posts agendados que chegaram na hora"""
        current_time = datetime.now()
        published_count = 0
        error_count = 0

        with db_manager.get_session() as session:
            # Buscar posts para publicar
            posts_to_publish = session.query(InstagramPost).filter(
                InstagramPost.status == PostStatus.SCHEDULED,
                InstagramPost.scheduled_time <= current_time
            ).all()

            for post in posts_to_publish:
                try:
                    # Preparar dados para publicação
                    post_data = {
                        'caption': post.caption,
                        'hashtags': post.hashtags,
                        'carousel_images': post.carousel_images,
                        'source_article_id': post.source_article_id,
                        'metadata': {'category': post.category}
                    }

                    # Publicar
                    result = self.publisher.publish_carousel_post(post_data)

                    if result.get('success'):
                        # Atualizar status
                        post.status = PostStatus.PUBLISHED
                        post.published_time = current_time
                        post.post_id = result.get('post_id')
                        published_count += 1

                        logger.info(f"Published scheduled post {post.id}")

                    else:
                        # Marcar como falha
                        post.status = PostStatus.FAILED
                        error_count += 1

                        logger.error(f"Failed to publish post {post.id}: {result.get('error')}")

                except Exception as e:
                    logger.error(f"Error publishing scheduled post {post.id}: {e}")
                    post.status = PostStatus.FAILED
                    error_count += 1

        return {
            'published': published_count,
            'errors': error_count
        }


if __name__ == "__main__":
    # Teste do publisher
    logging.basicConfig(level=logging.INFO)

    publisher = InstagramPublisher()

    # Teste de conexão
    connection_test = publisher.test_connection()
    print(f"Connection test: {connection_test}")

    if connection_test.get('success'):
        # Teste de insights
        insights = publisher.get_account_insights()
        print(f"Account insights: {insights}")
    else:
        print("Instagram not connected - skipping tests")