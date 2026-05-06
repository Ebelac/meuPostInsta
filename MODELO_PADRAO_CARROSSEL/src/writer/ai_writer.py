"""
Sistema de geração de conteúdo com IA
"""
import openai
import anthropic
from typing import Dict, List, Optional, Any
import logging
import json
import re

from config.settings import settings
from src.database import db_manager, ContentTemplate

logger = logging.getLogger(__name__)


class AIContentWriter:
    """Sistema de geração de conteúdo com múltiplas IAs"""

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._init_clients()

    def _init_clients(self):
        """Inicializa clientes das APIs de IA"""
        try:
            if settings.openai_api_key:
                self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")

        try:
            if settings.anthropic_api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
                logger.info("Anthropic client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic: {e}")

    def generate_instagram_post(self, content_data: Dict, template_name: str = None) -> Dict[str, Any]:
        """Gera post completo para Instagram"""
        logger.info(f"Generating Instagram post for: {content_data.get('title', 'Unknown')}")

        # Obter template
        template = self._get_template(template_name or content_data.get('template_name', 'Tech News Standard'))

        # Gerar caption
        caption = self._generate_caption(content_data, template)

        # Gerar hashtags
        hashtags = self._generate_hashtags(content_data, template)

        # Gerar tópicos para carrossel
        carousel_topics = self._generate_carousel_topics(content_data)

        # Metadados adicionais
        metadata = {
            'tone': self._determine_tone(content_data),
            'target_audience': self._determine_audience(content_data),
            'estimated_performance': content_data.get('estimated_engagement', {}),
            'content_type': content_data.get('content_type', 'news')
        }

        post_content = {
            'caption': caption,
            'hashtags': hashtags,
            'carousel_topics': carousel_topics,
            'metadata': metadata,
            'source_article_id': content_data.get('article_id'),
            'template_used': template_name,
            'generation_timestamp': 'now'
        }

        return post_content

    def _get_template(self, template_name: str) -> ContentTemplate:
        """Obtém template do banco de dados"""
        with db_manager.get_session() as session:
            template = session.query(ContentTemplate).filter(
                ContentTemplate.name == template_name,
                ContentTemplate.is_active == True
            ).first()

            if not template:
                # Template padrão
                template = session.query(ContentTemplate).filter(
                    ContentTemplate.name == 'Tech News Standard',
                    ContentTemplate.is_active == True
                ).first()

        return template

    def _generate_caption(self, content_data: Dict, template: ContentTemplate) -> str:
        """Gera caption usando IA"""
        prompt = self._build_caption_prompt(content_data, template)

        # Tentar Anthropic primeiro, depois OpenAI
        if self.anthropic_client:
            return self._generate_with_anthropic(prompt, 'caption')
        elif self.openai_client:
            return self._generate_with_openai(prompt, 'caption')
        else:
            return self._generate_fallback_caption(content_data, template)

    def _build_caption_prompt(self, content_data: Dict, template: ContentTemplate) -> str:
        """Constrói prompt para geração de caption"""
        title = content_data.get('title', '')
        summary = content_data.get('summary', '')
        category = content_data.get('category', '')
        key_points = content_data.get('key_points', [])
        content_type = content_data.get('content_type', 'news')

        prompt = f'''
Crie uma caption envolvente para Instagram sobre tecnologia baseada nesta notícia:

TÍTULO: {title}
CATEGORIA: {category}
RESUMO: {summary}

PONTOS-CHAVE:
{chr(10).join(f"- {point}" for point in key_points)}

INSTRUÇÕES:
1. Tom: Profissional mas acessível, entusiástico sobre tech
2. Público: Desenvolvedores, profissionais de tech, entusiastas
3. Estilo: Brasileiro, informal mas informativo
4. Tamanho: Máximo 1500 caracteres
5. Tipo de conteúdo: {content_type}

ESTRUTURA DESEJADA:
- Gancho inicial chamativo (emoji + frase impactante)
- Explicação clara do que é a tecnologia/novidade
- Por que isso importa para o público
- Call-to-action para engajamento

DIRETRIZES:
- Use emojis relevantes (máximo 5)
- Evite jargões muito técnicos
- Foque nos benefícios práticos
- Inclua pergunta para gerar comentários
- Seja positivo e empolgante sobre inovação

Não inclua hashtags na caption (elas serão adicionadas separadamente).
'''
        return prompt

    def _generate_with_anthropic(self, prompt: str, content_type: str) -> str:
        """Gera conteúdo usando Anthropic Claude"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()
            logger.info(f"Generated {content_type} with Anthropic")
            return content

        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            return ""

    def _generate_with_openai(self, prompt: str, content_type: str) -> str:
        """Gera conteúdo usando OpenAI GPT"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em criar conteúdo para redes sociais sobre tecnologia. Seu estilo é envolvente, informativo e otimizado para o público brasileiro de tech."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()
            logger.info(f"Generated {content_type} with OpenAI")
            return content

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return ""

    def _generate_fallback_caption(self, content_data: Dict, template: ContentTemplate) -> str:
        """Gera caption usando template sem IA"""
        try:
            caption_template = template.caption_template

            # Substituir variáveis no template
            replacements = {
                '{title}': content_data.get('title', ''),
                '{summary}': content_data.get('summary', ''),
                '{key_points}': '\n'.join([f"• {point}" for point in content_data.get('key_points', [])]),
                '{category}': content_data.get('category', ''),
                '{source}': content_data.get('source', '')
            }

            caption = caption_template
            for placeholder, value in replacements.items():
                caption = caption.replace(placeholder, value)

            return caption

        except Exception as e:
            logger.error(f"Fallback caption generation failed: {e}")
            return f"🚀 {content_data.get('title', 'Tech News')}\n\nConfira essa novidade incrível da tecnologia!\n\n#tech #inovacao"

    def _generate_hashtags(self, content_data: Dict, template: ContentTemplate) -> List[str]:
        """Gera hashtags otimizadas"""
        # Combinar hashtags sugeridas com hashtags do template
        suggested = content_data.get('suggested_hashtags', [])
        template_hashtags = template.hashtag_template if template else []

        # Hashtags obrigatórias
        mandatory_hashtags = ['#tech', '#tecnologia', '#inovacao']

        # Combinar todas
        all_hashtags = set()
        all_hashtags.update(suggested)
        all_hashtags.update(template_hashtags or [])
        all_hashtags.update(mandatory_hashtags)

        # Filtrar e limitar
        filtered_hashtags = [tag for tag in all_hashtags if self._is_valid_hashtag(tag)]

        return filtered_hashtags[:settings.hashtag_count]

    def _is_valid_hashtag(self, hashtag: str) -> bool:
        """Valida hashtag"""
        if not hashtag or not hashtag.startswith('#'):
            return False

        # Remove caracteres especiais
        clean_tag = re.sub(r'[^a-zA-Z0-9#_]', '', hashtag)
        return len(clean_tag) > 2

    def _generate_carousel_topics(self, content_data: Dict) -> List[Dict[str, str]]:
        """Gera tópicos para slides do carrossel"""
        title = content_data.get('title', '')
        summary = content_data.get('summary', '')
        key_points = content_data.get('key_points', [])
        category = content_data.get('category', '')

        prompt = f'''
Crie {settings.carousel_slide_count} slides para um carrossel do Instagram sobre:

TÍTULO: {title}
CATEGORIA: {category}
RESUMO: {summary}

PONTOS-CHAVE: {', '.join(key_points)}

Para cada slide, forneça:
1. Um título chamativo (máximo 40 caracteres)
2. Texto principal (máximo 150 caracteres)
3. Sugestão de elemento visual

FORMATO DE RESPOSTA (JSON):
[
  {{
    "slide_number": 1,
    "title": "Título do slide",
    "content": "Conteúdo principal",
    "visual_suggestion": "Descrição do visual"
  }}
]

DIRETRIZES:
- Slide 1: Introdução/gancho
- Slides intermediários: Explicação técnica simplificada
- Último slide: Call-to-action/conclusão
- Use linguagem acessível
- Foque em benefícios práticos
'''

        if self.anthropic_client:
            response_text = self._generate_with_anthropic(prompt, 'carousel')
        elif self.openai_client:
            response_text = self._generate_with_openai(prompt, 'carousel')
        else:
            return self._generate_fallback_carousel(content_data)

        try:
            # Extrair JSON da resposta
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                carousel_data = json.loads(json_match.group())
                return carousel_data
            else:
                return self._generate_fallback_carousel(content_data)

        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Failed to parse carousel JSON: {e}")
            return self._generate_fallback_carousel(content_data)

    def _generate_fallback_carousel(self, content_data: Dict) -> List[Dict[str, str]]:
        """Gera carrossel básico sem IA"""
        title = content_data.get('title', 'Tech News')
        summary = content_data.get('summary', '')
        key_points = content_data.get('key_points', [])

        slides = [
            {
                "slide_number": 1,
                "title": "🚀 Novidade Tech!",
                "content": title[:100],
                "visual_suggestion": "Logo da tecnologia ou ícone relevante"
            },
            {
                "slide_number": 2,
                "title": "💡 O que é?",
                "content": summary[:150] if summary else "Uma nova tecnologia que pode revolucionar o mercado.",
                "visual_suggestion": "Diagrama explicativo simples"
            }
        ]

        # Adicionar slides para pontos-chave
        for i, point in enumerate(key_points[:3], 3):
            slides.append({
                "slide_number": i,
                "title": f"📌 Ponto {i-1}",
                "content": point[:150],
                "visual_suggestion": "Ícone relacionado ao ponto"
            })

        # Slide final
        slides.append({
            "slide_number": len(slides) + 1,
            "title": "🤔 E você?",
            "content": "O que acha dessa inovação? Comenta aí!",
            "visual_suggestion": "Call-to-action visual"
        })

        return slides[:settings.carousel_slide_count]

    def _determine_tone(self, content_data: Dict) -> str:
        """Determina tom do conteúdo"""
        category = content_data.get('category', '').lower()
        content_type = content_data.get('content_type', '')

        if 'security' in category or 'cybersecurity' in category:
            return 'serious'
        elif content_type == 'tutorial':
            return 'educational'
        elif content_type == 'viral':
            return 'exciting'
        else:
            return 'informative'

    def _determine_audience(self, content_data: Dict) -> str:
        """Determina público-alvo"""
        category = content_data.get('category', '').lower()

        if 'ai' in category or 'machine learning' in category:
            return 'data_scientists'
        elif 'web development' in category:
            return 'web_developers'
        elif 'mobile' in category:
            return 'mobile_developers'
        else:
            return 'tech_professionals'

    def optimize_for_engagement(self, post_content: Dict) -> Dict:
        """Otimiza conteúdo para engajamento"""
        # Analisar performance histórica
        optimized = post_content.copy()

        # Otimizar caption
        caption = optimized.get('caption', '')
        if caption:
            # Adicionar call-to-action se não houver
            if '?' not in caption[-100:]:  # Últimos 100 caracteres
                caption += "\n\n🤔 E você, o que acha? Comenta aí!"
                optimized['caption'] = caption

        # Otimizar hashtags baseado em performance
        hashtags = optimized.get('hashtags', [])
        if hashtags:
            # Reordenar hashtags por performance (mock)
            high_performance_tags = ['#tech', '#AI', '#programming', '#innovation']
            reordered = []

            # Adicionar hashtags de alta performance primeiro
            for tag in high_performance_tags:
                if tag in hashtags:
                    reordered.append(tag)
                    hashtags.remove(tag)

            # Adicionar restante
            reordered.extend(hashtags)
            optimized['hashtags'] = reordered

        # Adicionar sugestões de timing
        optimized['metadata']['suggested_posting_times'] = ['09:00', '14:00', '19:00']
        optimized['metadata']['optimization_applied'] = True

        return optimized


if __name__ == "__main__":
    # Teste do writer
    logging.basicConfig(level=logging.INFO)

    writer = AIContentWriter()

    # Dados de exemplo
    test_content = {
        'article_id': 1,
        'title': 'Nova versão do Python 3.12 revoluciona desenvolvimento',
        'summary': 'Python 3.12 traz melhorias significativas em performance e novas funcionalidades para desenvolvedores.',
        'category': 'Programming',
        'key_points': [
            'Performance 15% melhor que versão anterior',
            'Novas funcionalidades para async/await',
            'Melhor suporte para type hints'
        ],
        'content_type': 'news',
        'template_name': 'Dev Community'
    }

    post = writer.generate_instagram_post(test_content)

    print("Generated Post:")
    print("=" * 50)
    print("CAPTION:")
    print(post['caption'])
    print("\nHASHTAGS:")
    print(' '.join(post['hashtags']))
    print("\nCAROUSSEL TOPICS:")
    for slide in post['carousel_topics']:
        print(f"Slide {slide['slide_number']}: {slide['title']}")
        print(f"  {slide['content']}")
        print()