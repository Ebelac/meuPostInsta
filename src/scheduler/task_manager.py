"""
Gerenciador de tarefas automatizadas usando Celery
"""
from celery import Celery
from datetime import datetime, timedelta
import logging

from config.settings import settings
from src.scrapers import NewsAggregator
from src.curator import ContentCurator
from src.scheduler.intelligent_scheduler import IntelligentScheduler
from src.publisher import PostScheduler, InstagramPublisher
from src.database import db_manager, SystemLog, NewsArticle

logger = logging.getLogger(__name__)

# Configurar Celery
app = Celery('instagram_automation')
app.conf.update(
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
)

# Configurar schedules
app.conf.beat_schedule = {
    # Scraping de notícias a cada hora
    'scrape-news': {
        'task': 'src.scheduler.task_manager.scrape_news_task',
        'schedule': 60.0 * 60.0,  # 1 hora
    },

    # Curadoria a cada 2 horas
    'curate-content': {
        'task': 'src.scheduler.task_manager.curate_content_task',
        'schedule': 60.0 * 60.0 * 2,  # 2 horas
    },

    # Verificar posts agendados a cada 15 minutos
    'publish-scheduled-posts': {
        'task': 'src.scheduler.task_manager.publish_scheduled_posts_task',
        'schedule': 60.0 * 15.0,  # 15 minutos
    },

    # Atualizar métricas a cada 6 horas
    'update-metrics': {
        'task': 'src.scheduler.task_manager.update_metrics_task',
        'schedule': 60.0 * 60.0 * 6,  # 6 horas
    },

    # Otimizar schedule diariamente
    'optimize-schedule': {
        'task': 'src.scheduler.task_manager.optimize_schedule_task',
        'schedule': 60.0 * 60.0 * 24,  # 24 horas
    },
}


def log_task_execution(task_name: str, result: dict, level: str = 'INFO'):
    """Log execução de tarefa no banco de dados"""
    try:
        with db_manager.get_session() as session:
            log_entry = SystemLog(
                level=level,
                module='task_manager',
                message=f'Task {task_name} executed',
                details=result
            )
            session.add(log_entry)

    except Exception as e:
        logger.error(f"Error logging task execution: {e}")


@app.task
def scrape_news_task():
    """Tarefa de scraping de notícias"""
    try:
        logger.info("Starting news scraping task")

        aggregator = NewsAggregator()
        stats = aggregator.run_scraping_cycle()

        log_task_execution('scrape_news', stats)

        return {
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"News scraping task failed: {e}")
        log_task_execution('scrape_news', {'error': str(e)}, 'ERROR')

        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@app.task
def curate_content_task():
    """Tarefa de curadoria de conteúdo"""
    try:
        logger.info("Starting content curation task")

        curator = ContentCurator()
        curated_content = curator.curate_daily_content(target_posts=5)

        if curated_content:
            # Agendar conteúdo usando scheduler inteligente
            scheduler = IntelligentScheduler()
            scheduling_result = scheduler.schedule_content_intelligently(curated_content)

            result = {
                'curated_articles': len(curated_content),
                'scheduling_result': scheduling_result
            }
        else:
            result = {
                'curated_articles': 0,
                'message': 'No content to curate'
            }

        log_task_execution('curate_content', result)

        return {
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Content curation task failed: {e}")
        log_task_execution('curate_content', {'error': str(e)}, 'ERROR')

        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@app.task
def publish_scheduled_posts_task():
    """Tarefa de publicação de posts agendados"""
    try:
        logger.info("Checking for scheduled posts to publish")

        post_scheduler = PostScheduler()
        result = post_scheduler.publish_scheduled_posts()

        if result['published'] > 0:
            logger.info(f"Published {result['published']} scheduled posts")

        log_task_execution('publish_scheduled_posts', result)

        return {
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Scheduled posts publishing task failed: {e}")
        log_task_execution('publish_scheduled_posts', {'error': str(e)}, 'ERROR')

        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@app.task
def update_metrics_task():
    """Tarefa de atualização de métricas"""
    try:
        logger.info("Updating Instagram metrics")

        publisher = InstagramPublisher()
        if publisher.is_logged_in:
            result = publisher.bulk_update_metrics()
            log_task_execution('update_metrics', result)
        else:
            result = {'error': 'Instagram not connected'}
            log_task_execution('update_metrics', result, 'WARNING')

        return {
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Metrics update task failed: {e}")
        log_task_execution('update_metrics', {'error': str(e)}, 'ERROR')

        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@app.task
def optimize_schedule_task():
    """Tarefa de otimização de horários"""
    try:
        logger.info("Optimizing posting schedule")

        scheduler = IntelligentScheduler()
        result = scheduler.optimize_schedule_based_on_performance()

        log_task_execution('optimize_schedule', result)

        return {
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Schedule optimization task failed: {e}")
        log_task_execution('optimize_schedule', {'error': str(e)}, 'ERROR')

        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@app.task
def cleanup_old_data_task():
    """Tarefa de limpeza de dados antigos"""
    try:
        logger.info("Cleaning up old data")

        deleted_count = 0

        with db_manager.get_session() as session:
            # Remover artigos muito antigos (> 90 dias)
            cutoff_date = datetime.now() - timedelta(days=90)

            old_articles = session.query(NewsArticle).filter(
                NewsArticle.scraped_date < cutoff_date,
                NewsArticle.is_used == False
            ).all()

            for article in old_articles:
                session.delete(article)
                deleted_count += 1

            # Remover logs antigos (> 30 dias)
            log_cutoff = datetime.now() - timedelta(days=30)

            old_logs = session.query(SystemLog).filter(
                SystemLog.timestamp < log_cutoff
            ).all()

            for log in old_logs:
                session.delete(log)
                deleted_count += 1

        result = {'deleted_records': deleted_count}
        log_task_execution('cleanup_old_data', result)

        return {
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Data cleanup task failed: {e}")
        log_task_execution('cleanup_old_data', {'error': str(e)}, 'ERROR')

        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@app.task
def emergency_post_task(content_data: dict):
    """Tarefa de post de emergência (manual)"""
    try:
        logger.info("Publishing emergency post")

        # Criar post completo
        scheduler = IntelligentScheduler()
        post_data = scheduler._create_complete_post(content_data)

        # Publicar imediatamente
        publisher = InstagramPublisher()
        result = publisher.publish_carousel_post(post_data)

        log_task_execution('emergency_post', result)

        return {
            'success': result.get('success', False),
            'result': result,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Emergency post task failed: {e}")
        log_task_execution('emergency_post', {'error': str(e)}, 'ERROR')

        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


class TaskManager:
    """Gerenciador de tarefas para interface Python"""

    def __init__(self):
        self.app = app

    def run_scraping_now(self):
        """Executa scraping imediatamente"""
        return scrape_news_task.delay()

    def run_curation_now(self):
        """Executa curadoria imediatamente"""
        return curate_content_task.delay()

    def publish_emergency_post(self, content_data: dict):
        """Publica post de emergência"""
        return emergency_post_task.delay(content_data)

    def get_task_status(self, task_id: str):
        """Obtém status de uma tarefa"""
        result = self.app.AsyncResult(task_id)
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None
        }

    def get_recent_task_logs(self, hours: int = 24):
        """Obtém logs recentes de tarefas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with db_manager.get_session() as session:
            logs = session.query(SystemLog).filter(
                SystemLog.module == 'task_manager',
                SystemLog.timestamp >= cutoff_time
            ).order_by(SystemLog.timestamp.desc()).all()

            return [{
                'timestamp': log.timestamp.isoformat(),
                'level': log.level,
                'message': log.message,
                'details': log.details
            } for log in logs]

    def pause_automation(self):
        """Pausa automação (revoga tarefas agendadas)"""
        try:
            # Revogar tarefas ativas
            self.app.control.revoke_by_pattern('*', terminate=True)

            # Log da pausa
            log_task_execution('pause_automation', {'status': 'paused'}, 'WARNING')

            return {'success': True, 'message': 'Automation paused'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def resume_automation(self):
        """Resume automação"""
        try:
            # Restart beat scheduler
            # Nota: Em produção, isso requereria restart do serviço
            log_task_execution('resume_automation', {'status': 'resumed'}, 'INFO')

            return {'success': True, 'message': 'Automation resumed'}

        except Exception as e:
            return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    # Para desenvolvimento - executar worker
    app.worker_main()