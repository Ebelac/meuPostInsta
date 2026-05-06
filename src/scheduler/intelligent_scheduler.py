"""
Sistema de agendamento inteligente baseado em dados de engajamento
"""
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta, time
import logging
from collections import defaultdict
import numpy as np

from src.database import db_manager, InstagramPost, ScheduleConfig, EngagementMetrics
from src.publisher import PostScheduler
from config.settings import settings

logger = logging.getLogger(__name__)


class IntelligentScheduler:
    """Agendador inteligente que otimiza horários baseado em engajamento"""

    def __init__(self):
        self.post_scheduler = PostScheduler()
        self.engagement_data = {}
        self._load_historical_data()

    def _load_historical_data(self):
        """Carrega dados históricos de engajamento"""
        with db_manager.get_session() as session:
            # Buscar posts dos últimos 90 dias
            cutoff_date = datetime.now() - timedelta(days=90)

            posts = session.query(InstagramPost).filter(
                InstagramPost.published_time >= cutoff_date,
                InstagramPost.likes_count.isnot(None)
            ).all()

            # Organizar por horário e dia da semana
            self.engagement_data = {
                'hourly': defaultdict(list),
                'daily': defaultdict(list),
                'category': defaultdict(list)
            }

            for post in posts:
                if post.published_time:
                    hour = post.published_time.hour
                    day_of_week = post.published_time.weekday()

                    # Calcular engagement rate
                    engagement_rate = self._calculate_engagement_rate(post)

                    self.engagement_data['hourly'][hour].append(engagement_rate)
                    self.engagement_data['daily'][day_of_week].append(engagement_rate)

                    if post.category:
                        self.engagement_data['category'][post.category].append({
                            'hour': hour,
                            'day': day_of_week,
                            'engagement': engagement_rate
                        })

        logger.info(f"Loaded engagement data from {len(posts)} posts")

    def _calculate_engagement_rate(self, post: InstagramPost) -> float:
        """Calcula taxa de engajamento de um post"""
        try:
            likes = post.likes_count or 0
            comments = post.comments_count or 0
            shares = post.shares_count or 0

            total_engagement = likes + comments + (shares * 2)  # Shares valem mais
            followers = 1000  # Fallback - idealmente pegar do Instagram

            return (total_engagement / followers) * 100

        except Exception:
            return 0.0

    def get_optimal_posting_times(self, num_slots: int = 3) -> List[time]:
        """Retorna horários ótimos para postagem baseado no histórico"""
        if not self.engagement_data['hourly']:
            # Fallback para horários padrão se não houver dados
            return [time(9, 0), time(14, 0), time(19, 0)]

        # Calcular média de engajamento por hora
        hourly_averages = {}
        for hour, engagement_rates in self.engagement_data['hourly'].items():
            if engagement_rates:
                hourly_averages[hour] = np.mean(engagement_rates)

        # Selecionar top horários
        sorted_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)
        optimal_hours = [hour for hour, _ in sorted_hours[:num_slots]]

        # Converter para objetos time
        optimal_times = [time(hour, 0) for hour in sorted(optimal_hours)]

        logger.info(f"Optimal posting times: {[t.strftime('%H:%M') for t in optimal_times]}")
        return optimal_times

    def get_best_days_for_category(self, category: str) -> List[int]:
        """Retorna melhores dias da semana para uma categoria"""
        if category not in self.engagement_data['category']:
            return [1, 2, 3, 4]  # Terça a sexta (padrão)

        category_data = self.engagement_data['category'][category]
        daily_performance = defaultdict(list)

        for data in category_data:
            daily_performance[data['day']].append(data['engagement'])

        # Calcular média por dia
        daily_averages = {}
        for day, engagement_rates in daily_performance.items():
            if engagement_rates:
                daily_averages[day] = np.mean(engagement_rates)

        # Retornar top 4 dias
        sorted_days = sorted(daily_averages.items(), key=lambda x: x[1], reverse=True)
        best_days = [day for day, _ in sorted_days[:4]]

        return best_days

    def schedule_content_intelligently(self, curated_content: List[Dict]) -> Dict[str, Any]:
        """Agenda conteúdo de forma inteligente"""
        logger.info(f"Scheduling {len(curated_content)} pieces of content")

        scheduled_posts = []
        scheduling_errors = []

        # Obter configuração de agendamento
        with db_manager.get_session() as session:
            schedule_config = session.query(ScheduleConfig).filter(
                ScheduleConfig.is_active == True
            ).first()

        if not schedule_config:
            return {'error': 'No active schedule configuration found'}

        # Obter horários ótimos
        optimal_times = self.get_optimal_posting_times(schedule_config.posts_per_day)

        # Distribuir conteúdo ao longo dos próximos dias
        start_date = datetime.now().date() + timedelta(days=1)  # Começar amanhã
        current_date = start_date
        time_index = 0

        for content in curated_content:
            try:
                # Determinar melhor horário para esta categoria
                category = content.get('category', 'Technology')
                best_days = self.get_best_days_for_category(category)

                # Encontrar próximo dia útil para a categoria
                while current_date.weekday() not in best_days:
                    current_date += timedelta(days=1)

                # Combinar data e horário
                posting_time = datetime.combine(current_date, optimal_times[time_index])

                # Verificar se não está muito próximo de outro post
                if self._is_time_slot_available(posting_time, scheduled_posts):
                    # Criar post completo (usando writer e designer)
                    post_data = self._create_complete_post(content)

                    # Agendar post
                    post_id = self.post_scheduler.schedule_post(post_data, posting_time)

                    scheduled_posts.append({
                        'post_id': post_id,
                        'scheduled_time': posting_time,
                        'category': category,
                        'title': content.get('title', 'Unknown')
                    })

                    logger.info(f"Scheduled post for {posting_time}: {content.get('title', 'Unknown')[:50]}")

                else:
                    # Tentar próximo horário
                    time_index = (time_index + 1) % len(optimal_times)
                    if time_index == 0:
                        current_date += timedelta(days=1)

                    posting_time = datetime.combine(current_date, optimal_times[time_index])
                    post_data = self._create_complete_post(content)
                    post_id = self.post_scheduler.schedule_post(post_data, posting_time)

                    scheduled_posts.append({
                        'post_id': post_id,
                        'scheduled_time': posting_time,
                        'category': category,
                        'title': content.get('title', 'Unknown')
                    })

                # Avançar para próximo slot
                time_index = (time_index + 1) % len(optimal_times)
                if time_index == 0:
                    current_date += timedelta(days=1)

                # Respeitar limite de posts por dia
                if len([p for p in scheduled_posts if p['scheduled_time'].date() == current_date]) >= schedule_config.posts_per_day:
                    current_date += timedelta(days=1)
                    time_index = 0

            except Exception as e:
                logger.error(f"Error scheduling content: {e}")
                scheduling_errors.append({
                    'content_title': content.get('title', 'Unknown'),
                    'error': str(e)
                })

        return {
            'success': True,
            'scheduled_posts': scheduled_posts,
            'total_scheduled': len(scheduled_posts),
            'errors': scheduling_errors,
            'next_posting_date': min([p['scheduled_time'] for p in scheduled_posts]) if scheduled_posts else None
        }

    def _is_time_slot_available(self, proposed_time: datetime, existing_posts: List[Dict],
                               min_interval_hours: int = 4) -> bool:
        """Verifica se horário está disponível (não muito próximo de outros posts)"""
        for post in existing_posts:
            existing_time = post['scheduled_time']
            time_diff = abs((proposed_time - existing_time).total_seconds() / 3600)

            if time_diff < min_interval_hours:
                return False

        return True

    def _create_complete_post(self, content_data: Dict) -> Dict:
        """Cria post completo com texto e imagens"""
        from src.writer import AIContentWriter
        from src.designer import CarouselGenerator

        # Gerar conteúdo de texto
        writer = AIContentWriter()
        post_content = writer.generate_instagram_post(content_data)

        # Gerar carrossel visual
        designer = CarouselGenerator()
        carousel_images = designer.generate_carousel(
            post_content['carousel_topics'],
            post_content['metadata']
        )

        # Combinar tudo
        complete_post = {
            'caption': post_content['caption'],
            'hashtags': post_content['hashtags'],
            'carousel_images': carousel_images,
            'source_article_id': content_data.get('article_id'),
            'metadata': post_content['metadata']
        }

        return complete_post

    def optimize_schedule_based_on_performance(self) -> Dict[str, Any]:
        """Otimiza horários de postagem baseado na performance recente"""
        logger.info("Optimizing schedule based on recent performance")

        # Recarregar dados históricos
        self._load_historical_data()

        # Calcular novos horários ótimos
        new_optimal_times = self.get_optimal_posting_times()

        # Atualizar configuração no banco
        with db_manager.get_session() as session:
            schedule_config = session.query(ScheduleConfig).filter(
                ScheduleConfig.is_active == True
            ).first()

            if schedule_config:
                # Converter times para strings
                time_strings = [t.strftime('%H:%M') for t in new_optimal_times]
                schedule_config.post_times = time_strings

                logger.info(f"Updated optimal posting times to: {time_strings}")

                return {
                    'success': True,
                    'old_times': schedule_config.post_times,
                    'new_times': time_strings,
                    'improvement_expected': self._estimate_improvement()
                }
            else:
                return {'error': 'No active schedule configuration found'}

    def _estimate_improvement(self) -> float:
        """Estima melhoria percentual esperada na performance"""
        if not self.engagement_data['hourly']:
            return 0.0

        # Comparar performance dos horários atuais vs novos ótimos
        current_performance = []
        optimal_performance = []

        # Usar dados históricos para simular
        for hour, rates in self.engagement_data['hourly'].items():
            if rates:
                avg_rate = np.mean(rates)
                current_performance.append(avg_rate)

                # Top 3 horários teriam performance melhor
                if hour in sorted(self.engagement_data['hourly'].keys(),
                                key=lambda h: np.mean(self.engagement_data['hourly'][h]) if self.engagement_data['hourly'][h] else 0,
                                reverse=True)[:3]:
                    optimal_performance.append(avg_rate * 1.2)  # 20% boost estimado
                else:
                    optimal_performance.append(avg_rate)

        if current_performance and optimal_performance:
            current_avg = np.mean(current_performance)
            optimal_avg = np.mean(optimal_performance)

            improvement = ((optimal_avg - current_avg) / current_avg) * 100
            return max(0, improvement)

        return 0.0

    def get_schedule_analytics(self) -> Dict[str, Any]:
        """Retorna análises do sistema de agendamento"""
        with db_manager.get_session() as session:
            # Posts agendados
            scheduled_count = session.query(InstagramPost).filter(
                InstagramPost.status == 'scheduled'
            ).count()

            # Posts dos últimos 30 dias
            last_month = datetime.now() - timedelta(days=30)
            recent_posts = session.query(InstagramPost).filter(
                InstagramPost.published_time >= last_month
            ).all()

            # Calcular estatísticas
            if recent_posts:
                total_engagement = sum(
                    (post.likes_count or 0) + (post.comments_count or 0)
                    for post in recent_posts
                )
                avg_engagement = total_engagement / len(recent_posts)

                # Performance por horário
                hourly_performance = defaultdict(list)
                for post in recent_posts:
                    if post.published_time:
                        hour = post.published_time.hour
                        engagement = (post.likes_count or 0) + (post.comments_count or 0)
                        hourly_performance[hour].append(engagement)

                best_hour = max(hourly_performance.keys(),
                              key=lambda h: np.mean(hourly_performance[h]) if hourly_performance[h] else 0)
            else:
                avg_engagement = 0
                best_hour = 14  # Fallback

            return {
                'scheduled_posts': scheduled_count,
                'posts_last_30_days': len(recent_posts),
                'average_engagement': avg_engagement,
                'best_performing_hour': best_hour,
                'optimal_times': [t.strftime('%H:%M') for t in self.get_optimal_posting_times()],
                'data_points': len(self.engagement_data.get('hourly', {}))
            }

    def reschedule_failed_posts(self) -> Dict[str, int]:
        """Reagenda posts que falharam na publicação"""
        rescheduled_count = 0

        with db_manager.get_session() as session:
            failed_posts = session.query(InstagramPost).filter(
                InstagramPost.status == 'failed'
            ).all()

            optimal_times = self.get_optimal_posting_times()

            for post in failed_posts:
                try:
                    # Agendar para próximo horário ótimo
                    next_time = datetime.now() + timedelta(hours=2)  # 2 horas a partir de agora
                    next_time = next_time.replace(
                        hour=optimal_times[0].hour,
                        minute=optimal_times[0].minute,
                        second=0,
                        microsecond=0
                    )

                    post.scheduled_time = next_time
                    post.status = 'scheduled'
                    rescheduled_count += 1

                    logger.info(f"Rescheduled failed post {post.id} for {next_time}")

                except Exception as e:
                    logger.error(f"Error rescheduling post {post.id}: {e}")

        return {'rescheduled': rescheduled_count}


if __name__ == "__main__":
    # Teste do scheduler
    logging.basicConfig(level=logging.INFO)

    scheduler = IntelligentScheduler()

    # Testar análises
    analytics = scheduler.get_schedule_analytics()
    print("Schedule Analytics:")
    for key, value in analytics.items():
        print(f"  {key}: {value}")

    # Testar horários ótimos
    optimal_times = scheduler.get_optimal_posting_times()
    print(f"\nOptimal posting times: {[t.strftime('%H:%M') for t in optimal_times]}")

    # Testar otimização
    optimization = scheduler.optimize_schedule_based_on_performance()
    print(f"\nSchedule optimization: {optimization}")