"""
Configuração e gerenciamento do banco de dados
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

from config.settings import settings
from .models import Base


class DatabaseManager:
    """Gerenciador de conexão com banco de dados"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.init_database()

    def init_database(self):
        """Inicializa conexão com banco de dados"""
        # Configurações específicas para SQLite
        if settings.database_url.startswith("sqlite"):
            self.engine = create_engine(
                settings.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False  # Set to True for SQL debugging
            )
        else:
            # Para PostgreSQL ou outros bancos
            self.engine = create_engine(settings.database_url, echo=False)

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Cria todas as tabelas no banco de dados"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Remove todas as tabelas (usado em testes)"""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager para sessões do banco"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_sync(self) -> Session:
        """Retorna uma nova sessão (deve ser fechada manualmente)"""
        return self.SessionLocal()


# Singleton instance
db_manager = DatabaseManager()


def get_database_session():
    """Função helper para obter sessão do banco (usado em FastAPI)"""
    return db_manager.get_session_sync()


def init_database():
    """Inicializa o banco de dados com dados padrão"""
    from .models import ContentTemplate, ScheduleConfig

    db_manager.create_tables()

    with db_manager.get_session() as session:
        # Verificar se já existe configuração de schedule
        existing_schedule = session.query(ScheduleConfig).first()
        if not existing_schedule:
            default_schedule = ScheduleConfig(
                post_times=["09:00", "14:00", "19:00"],
                posts_per_day=3,
                posts_per_week=21,
                min_interval_hours=4,
                preferred_categories=["AI", "Machine Learning", "Web Development"],
                category_distribution={
                    "AI": 30,
                    "Machine Learning": 25,
                    "Web Development": 20,
                    "Mobile": 15,
                    "Cybersecurity": 10
                }
            )
            session.add(default_schedule)

        # Templates padrão de conteúdo
        existing_templates = session.query(ContentTemplate).count()
        if existing_templates == 0:
            templates = [
                ContentTemplate(
                    name="Tech News Standard",
                    category="AI",
                    caption_template="""🚀 {title}

{summary}

💡 Principais destaques:
{key_points}

🔗 O que você acha dessa tecnologia? Compartilha nos comentários!

#tech #tecnologia #inovacao""",
                    hashtag_template=[
                        "#tech", "#tecnologia", "#inovacao", "#AI",
                        "#machinelearning", "#futuro", "#digitalTransformation"
                    ],
                    design_template="tech_standard",
                    color_scheme={"primary": "#1DA1F2", "secondary": "#14171A"}
                ),
                ContentTemplate(
                    name="AI/ML Focus",
                    category="AI",
                    caption_template="""🤖 {title}

{summary}

🧠 Por que isso importa:
{why_matters}

🎯 Impacto na indústria: {impact}

#AI #MachineLearning #tech""",
                    hashtag_template=[
                        "#AI", "#MachineLearning", "#DeepLearning", "#DataScience",
                        "#tech", "#innovation", "#future", "#automation"
                    ],
                    design_template="ai_focus",
                    color_scheme={"primary": "#FF6B6B", "secondary": "#4ECDC4"}
                ),
                ContentTemplate(
                    name="Dev Community",
                    category="Web Development",
                    caption_template="""💻 {title}

{summary}

👨‍💻 Para devs:
{dev_insights}

🔧 Tecnologias: {technologies}

Quem já testou? Conta a experiência! 👇

#webdev #programming #javascript""",
                    hashtag_template=[
                        "#webdev", "#programming", "#javascript", "#react",
                        "#nodejs", "#frontend", "#backend", "#fullstack"
                    ],
                    design_template="dev_community",
                    color_scheme={"primary": "#61DAFB", "secondary": "#20232A"}
                )
            ]

            for template in templates:
                session.add(template)


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")