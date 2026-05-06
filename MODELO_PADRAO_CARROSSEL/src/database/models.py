"""
Modelos de banco de dados para o sistema InstaCalebeDigital
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class ContentCategory(str, Enum):
    AI = "AI"
    MACHINE_LEARNING = "Machine Learning"
    WEB_DEVELOPMENT = "Web Development"
    MOBILE = "Mobile"
    CYBERSECURITY = "Cybersecurity"
    BLOCKCHAIN = "Blockchain"
    CLOUD = "Cloud"
    DEVOPS = "DevOps"


class NewsArticle(Base):
    """Artigos de notícias coletados"""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    url = Column(String(1000), nullable=False, unique=True)
    source = Column(String(100), nullable=False)
    author = Column(String(200))
    published_date = Column(DateTime)
    scraped_date = Column(DateTime, default=datetime.utcnow)

    # Conteúdo
    summary = Column(Text)
    content = Column(Text)
    category = Column(String(50))
    tags = Column(JSON)  # Lista de tags

    # Métricas de qualidade
    relevance_score = Column(Float, default=0.0)
    engagement_potential = Column(Float, default=0.0)
    readability_score = Column(Float, default=0.0)

    # Status
    is_curated = Column(Boolean, default=False)
    is_used = Column(Boolean, default=False)

    # Relacionamentos
    instagram_posts = relationship("InstagramPost", back_populates="source_article")

    def __repr__(self):
        return f"<NewsArticle(title='{self.title[:50]}...', source='{self.source}')>"


class InstagramPost(Base):
    """Posts do Instagram gerados"""
    __tablename__ = "instagram_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(100), unique=True)  # ID do Instagram após publicação

    # Conteúdo
    caption = Column(Text, nullable=False)
    hashtags = Column(JSON)  # Lista de hashtags
    carousel_images = Column(JSON)  # Paths das imagens do carrossel

    # Metadados
    category = Column(String(50))
    scheduled_time = Column(DateTime)
    published_time = Column(DateTime)

    # Status
    status = Column(String(20), default=PostStatus.DRAFT)

    # Relacionamentos
    source_article_id = Column(Integer, ForeignKey("news_articles.id"))
    source_article = relationship("NewsArticle", back_populates="instagram_posts")

    # Métricas (atualizadas após publicação)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<InstagramPost(id={self.id}, status='{self.status}')>"


class ContentTemplate(Base):
    """Templates para geração de conteúdo"""
    __tablename__ = "content_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)

    # Template de texto
    caption_template = Column(Text, nullable=False)
    hashtag_template = Column(JSON)  # Lista de hashtags padrão

    # Template de design
    design_template = Column(String(100))  # Nome do template de design
    color_scheme = Column(JSON)  # Cores específicas do template

    # Configurações
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ContentTemplate(name='{self.name}', category='{self.category}')>"


class ScheduleConfig(Base):
    """Configurações de agendamento"""
    __tablename__ = "schedule_configs"

    id = Column(Integer, primary_key=True, index=True)

    # Configurações de tempo
    post_times = Column(JSON)  # Lista de horários preferidos ['09:00', '14:00', '19:00']
    timezone = Column(String(50), default='America/Sao_Paulo')

    # Configurações de frequência
    posts_per_day = Column(Integer, default=3)
    posts_per_week = Column(Integer, default=21)
    min_interval_hours = Column(Integer, default=4)

    # Configurações de conteúdo
    preferred_categories = Column(JSON)  # Categorias preferidas
    category_distribution = Column(JSON)  # Distribuição percentual por categoria

    # Status
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EngagementMetrics(Base):
    """Métricas de engajamento consolidadas"""
    __tablename__ = "engagement_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)

    # Métricas diárias
    total_posts = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_reach = Column(Integer, default=0)
    total_impressions = Column(Integer, default=0)

    # Métricas por categoria
    category_performance = Column(JSON)  # Performance por categoria

    # Best performing content
    best_post_id = Column(Integer, ForeignKey("instagram_posts.id"))
    best_time_slot = Column(String(10))  # Melhor horário do dia

    created_at = Column(DateTime, default=datetime.utcnow)


class SystemLog(Base):
    """Logs do sistema"""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    module = Column(String(50), nullable=False)  # scraper, curator, publisher, etc
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Detalhes adicionais em JSON

    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SystemLog(level='{self.level}', module='{self.module}')>"