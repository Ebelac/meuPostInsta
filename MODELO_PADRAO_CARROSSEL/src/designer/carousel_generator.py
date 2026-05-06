"""
Gerador de carrosséis visuais para Instagram
"""
from PIL import Image, ImageDraw, ImageFont
import io
import os
import textwrap
import requests
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

from config.settings import settings

logger = logging.getLogger(__name__)


class CarouselGenerator:
    """Gerador de carrosséis visuais para Instagram"""

    def __init__(self):
        self.output_dir = "assets/generated_carousels"
        self.templates_dir = "templates/carousel_templates"
        self.fonts_dir = "assets/fonts"

        # Dimensões padrão Instagram
        self.carousel_size = (1080, 1080)  # 1:1 aspect ratio
        self.safe_area = (100, 100, 980, 980)  # Área segura para texto

        # Cores padrão
        self.brand_colors = {
            'primary': settings.brand_color_primary,
            'secondary': settings.brand_color_secondary,
            'white': '#FFFFFF',
            'black': '#000000',
            'gray': '#6B7280',
            'light_gray': '#F3F4F6',
            'accent': '#3B82F6'
        }

        self._ensure_directories()
        self._load_fonts()

    def _ensure_directories(self):
        """Cria diretórios necessários"""
        for directory in [self.output_dir, self.templates_dir, self.fonts_dir]:
            os.makedirs(directory, exist_ok=True)

    def _load_fonts(self):
        """Carrega fontes para uso"""
        self.fonts = {}

        # Fontes padrão do sistema
        font_paths = {
            'title': None,  # Will use default
            'subtitle': None,
            'body': None,
            'caption': None
        }

        # Tamanhos de fonte
        font_sizes = {
            'title': 48,
            'subtitle': 32,
            'body': 24,
            'caption': 18
        }

        for font_type, size in font_sizes.items():
            try:
                # Tentar carregar fonte customizada
                custom_path = os.path.join(self.fonts_dir, f"{font_type}.ttf")
                if os.path.exists(custom_path):
                    self.fonts[font_type] = ImageFont.truetype(custom_path, size)
                else:
                    # Usar fonte padrão
                    self.fonts[font_type] = ImageFont.load_default()
                    logger.info(f"Using default font for {font_type}")

            except Exception as e:
                logger.warning(f"Could not load font for {font_type}: {e}")
                self.fonts[font_type] = ImageFont.load_default()

    def generate_carousel(self, carousel_data: List[Dict], post_metadata: Dict) -> List[str]:
        """Gera carrossel completo baseado nos dados"""
        logger.info(f"Generating carousel with {len(carousel_data)} slides")

        carousel_id = f"carousel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        slide_paths = []

        for i, slide_data in enumerate(carousel_data, 1):
            try:
                slide_path = self._generate_slide(
                    slide_data,
                    slide_number=i,
                    total_slides=len(carousel_data),
                    carousel_id=carousel_id,
                    metadata=post_metadata
                )
                slide_paths.append(slide_path)

            except Exception as e:
                logger.error(f"Error generating slide {i}: {e}")
                # Criar slide de erro
                error_slide = self._create_error_slide(i, carousel_id)
                slide_paths.append(error_slide)

        logger.info(f"Generated carousel: {len(slide_paths)} slides")
        return slide_paths

    def _generate_slide(self, slide_data: Dict, slide_number: int, total_slides: int,
                       carousel_id: str, metadata: Dict) -> str:
        """Gera um slide individual"""

        # Determinar template baseado no tipo de slide
        template_type = self._determine_template_type(slide_data, slide_number, total_slides)

        # Criar imagem base
        image = Image.new('RGB', self.carousel_size, color=self.brand_colors['white'])
        draw = ImageDraw.Draw(image)

        # Aplicar template
        if template_type == 'cover':
            self._apply_cover_template(image, draw, slide_data, metadata)
        elif template_type == 'content':
            self._apply_content_template(image, draw, slide_data, slide_number)
        elif template_type == 'cta':
            self._apply_cta_template(image, draw, slide_data, metadata)
        else:
            self._apply_default_template(image, draw, slide_data, slide_number)

        # Adicionar elementos comuns
        self._add_slide_number(draw, slide_number, total_slides)
        self._add_brand_elements(draw, metadata.get('category'))

        # Salvar slide
        slide_filename = f"{carousel_id}_slide_{slide_number:02d}.png"
        slide_path = os.path.join(self.output_dir, slide_filename)
        image.save(slide_path, "PNG", quality=95)

        logger.info(f"Generated slide {slide_number}: {slide_path}")
        return slide_path

    def _determine_template_type(self, slide_data: Dict, slide_number: int, total_slides: int) -> str:
        """Determina tipo de template para o slide"""
        if slide_number == 1:
            return 'cover'
        elif slide_number == total_slides:
            return 'cta'
        else:
            return 'content'

    def _apply_cover_template(self, image: Image, draw: ImageDraw, slide_data: Dict, metadata: Dict):
        """Aplica template de capa"""
        # Background gradiente
        self._create_gradient_background(image,
                                       self.brand_colors['primary'],
                                       self.brand_colors['secondary'])

        # Título principal
        title = slide_data.get('title', 'Tech News')
        title_lines = self._wrap_text(title, self.fonts['title'], 800)

        y_position = 300
        for line in title_lines:
            text_width = draw.textlength(line, font=self.fonts['title'])
            x_position = (self.carousel_size[0] - text_width) // 2

            # Sombra do texto
            draw.text((x_position + 3, y_position + 3), line,
                     font=self.fonts['title'], fill=self.brand_colors['black'])
            # Texto principal
            draw.text((x_position, y_position), line,
                     font=self.fonts['title'], fill=self.brand_colors['white'])

            y_position += 60

        # Categoria/tag
        category = metadata.get('category', 'TECH')
        self._draw_tag(draw, category, (540, 450), self.brand_colors['accent'])

        # Ícone ou emoji relacionado
        emoji = self._get_category_emoji(metadata.get('category'))
        if emoji:
            draw.text((540, 520), emoji, font=self.fonts['title'],
                     fill=self.brand_colors['white'], anchor="mm")

    def _apply_content_template(self, image: Image, draw: ImageDraw, slide_data: Dict, slide_number: int):
        """Aplica template de conteúdo"""
        # Background limpo com destaque
        self._create_content_background(image, slide_number)

        # Título do slide
        title = slide_data.get('title', f'Slide {slide_number}')
        title_lines = self._wrap_text(title, self.fonts['subtitle'], 800)

        y_position = 180
        for line in title_lines:
            text_width = draw.textlength(line, font=self.fonts['subtitle'])
            x_position = (self.carousel_size[0] - text_width) // 2

            draw.text((x_position, y_position), line,
                     font=self.fonts['subtitle'], fill=self.brand_colors['primary'])
            y_position += 50

        # Conteúdo principal
        content = slide_data.get('content', '')
        content_lines = self._wrap_text(content, self.fonts['body'], 700)

        y_position += 50
        for line in content_lines:
            text_width = draw.textlength(line, font=self.fonts['body'])
            x_position = (self.carousel_size[0] - text_width) // 2

            draw.text((x_position, y_position), line,
                     font=self.fonts['body'], fill=self.brand_colors['black'])
            y_position += 35

        # Elemento visual decorativo
        self._add_decorative_elements(draw, slide_data)

    def _apply_cta_template(self, image: Image, draw: ImageDraw, slide_data: Dict, metadata: Dict):
        """Aplica template de call-to-action"""
        # Background chamativo
        self._create_cta_background(image)

        # Título CTA
        title = slide_data.get('title', '🤔 E você?')
        text_width = draw.textlength(title, font=self.fonts['title'])
        x_position = (self.carousel_size[0] - text_width) // 2

        draw.text((x_position, 300), title,
                 font=self.fonts['title'], fill=self.brand_colors['white'])

        # Mensagem CTA
        cta_message = slide_data.get('content', 'Comenta aí o que você achou!')
        cta_lines = self._wrap_text(cta_message, self.fonts['subtitle'], 700)

        y_position = 400
        for line in cta_lines:
            text_width = draw.textlength(line, font=self.fonts['subtitle'])
            x_position = (self.carousel_size[0] - text_width) // 2

            draw.text((x_position, y_position), line,
                     font=self.fonts['subtitle'], fill=self.brand_colors['white'])
            y_position += 40

        # Botões visuais
        self._draw_engagement_buttons(draw)

    def _apply_default_template(self, image: Image, draw: ImageDraw, slide_data: Dict, slide_number: int):
        """Template padrão para slides não categorizados"""
        # Background simples
        draw.rectangle([(0, 0), self.carousel_size], fill=self.brand_colors['light_gray'])

        # Título
        title = slide_data.get('title', f'Slide {slide_number}')
        text_width = draw.textlength(title, font=self.fonts['subtitle'])
        x_position = (self.carousel_size[0] - text_width) // 2

        draw.text((x_position, 300), title,
                 font=self.fonts['subtitle'], fill=self.brand_colors['black'])

        # Conteúdo
        content = slide_data.get('content', '')
        content_lines = self._wrap_text(content, self.fonts['body'], 700)

        y_position = 400
        for line in content_lines:
            text_width = draw.textlength(line, font=self.fonts['body'])
            x_position = (self.carousel_size[0] - text_width) // 2

            draw.text((x_position, y_position), line,
                     font=self.fonts['body'], fill=self.brand_colors['gray'])
            y_position += 35

    def _create_gradient_background(self, image: Image, color1: str, color2: str):
        """Cria background com gradiente"""
        # Converter hex para RGB
        rgb1 = self._hex_to_rgb(color1)
        rgb2 = self._hex_to_rgb(color2)

        for y in range(self.carousel_size[1]):
            ratio = y / self.carousel_size[1]
            r = int(rgb1[0] * (1 - ratio) + rgb2[0] * ratio)
            g = int(rgb1[1] * (1 - ratio) + rgb2[1] * ratio)
            b = int(rgb1[2] * (1 - ratio) + rgb2[2] * ratio)

            draw = ImageDraw.Draw(image)
            draw.line([(0, y), (self.carousel_size[0], y)], fill=(r, g, b))

    def _create_content_background(self, image: Image, slide_number: int):
        """Cria background para slides de conteúdo"""
        draw = ImageDraw.Draw(image)

        # Background branco com destaque colorido
        draw.rectangle([(0, 0), self.carousel_size], fill=self.brand_colors['white'])

        # Barra lateral colorida
        bar_color = self._get_slide_accent_color(slide_number)
        draw.rectangle([(0, 0), (20, self.carousel_size[1])], fill=bar_color)

        # Elementos decorativos sutis
        draw.rectangle([(50, 100), (1030, 110)], fill=self.brand_colors['light_gray'])

    def _create_cta_background(self, image: Image):
        """Cria background para slide CTA"""
        draw = ImageDraw.Draw(image)

        # Background com padrão geométrico
        base_color = self._hex_to_rgb(self.brand_colors['primary'])

        for i in range(0, self.carousel_size[0], 40):
            for j in range(0, self.carousel_size[1], 40):
                alpha = 0.1 if (i // 40 + j // 40) % 2 == 0 else 0.05
                overlay_color = tuple(int(c * (1 - alpha) + 255 * alpha) for c in base_color)
                draw.rectangle([(i, j), (i + 40, j + 40)], fill=overlay_color)

    def _wrap_text(self, text: str, font: ImageFont, max_width: int) -> List[str]:
        """Quebra texto em linhas para caber na largura"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.getlength(test_line) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)  # Palavra muito longa

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _draw_tag(self, draw: ImageDraw, text: str, center: Tuple[int, int], color: str):
        """Desenha tag/badge"""
        text_width = draw.textlength(text, font=self.fonts['caption'])
        padding = 20

        # Background da tag
        tag_rect = [
            center[0] - text_width // 2 - padding,
            center[1] - 15,
            center[0] + text_width // 2 + padding,
            center[1] + 15
        ]

        draw.rounded_rectangle(tag_rect, radius=15, fill=color)

        # Texto da tag
        text_x = center[0] - text_width // 2
        draw.text((text_x, center[1] - 8), text,
                 font=self.fonts['caption'], fill=self.brand_colors['white'])

    def _add_slide_number(self, draw: ImageDraw, slide_number: int, total_slides: int):
        """Adiciona numeração do slide"""
        indicator_text = f"{slide_number}/{total_slides}"
        text_width = draw.textlength(indicator_text, font=self.fonts['caption'])

        # Posição no canto inferior direito
        x_position = self.carousel_size[0] - text_width - 30
        y_position = self.carousel_size[1] - 40

        # Background semi-transparente
        draw.rounded_rectangle([
            x_position - 10, y_position - 10,
            x_position + text_width + 10, y_position + 20
        ], radius=10, fill=self.brand_colors['gray'])

        # Texto
        draw.text((x_position, y_position), indicator_text,
                 font=self.fonts['caption'], fill=self.brand_colors['white'])

    def _add_brand_elements(self, draw: ImageDraw, category: Optional[str] = None):
        """Adiciona elementos de marca"""
        # Logo/marca no canto superior direito
        brand_text = "@instacalebe"
        text_width = draw.textlength(brand_text, font=self.fonts['caption'])

        x_position = self.carousel_size[0] - text_width - 30
        y_position = 30

        draw.text((x_position, y_position), brand_text,
                 font=self.fonts['caption'], fill=self.brand_colors['gray'])

    def _add_decorative_elements(self, draw: ImageDraw, slide_data: Dict):
        """Adiciona elementos decorativos baseados no conteúdo"""
        visual_suggestion = slide_data.get('visual_suggestion', '')

        if 'diagram' in visual_suggestion.lower():
            # Desenhar diagrama simples
            self._draw_simple_diagram(draw)
        elif 'chart' in visual_suggestion.lower():
            # Desenhar gráfico simples
            self._draw_simple_chart(draw)
        elif 'icon' in visual_suggestion.lower():
            # Adicionar ícone representativo
            self._draw_tech_icon(draw)

    def _draw_simple_diagram(self, draw: ImageDraw):
        """Desenha diagrama simples"""
        center_x, center_y = 540, 700

        # Círculos conectados
        circles = [
            (center_x - 100, center_y, 30),
            (center_x, center_y, 30),
            (center_x + 100, center_y, 30)
        ]

        for x, y, radius in circles:
            draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                        outline=self.brand_colors['primary'], width=3)

        # Conectores
        draw.line([(center_x - 70, center_y), (center_x - 30, center_y)],
                 fill=self.brand_colors['primary'], width=3)
        draw.line([(center_x + 30, center_y), (center_x + 70, center_y)],
                 fill=self.brand_colors['primary'], width=3)

    def _draw_simple_chart(self, draw: ImageDraw):
        """Desenha gráfico simples"""
        base_y = 800
        bar_width = 40
        bars = [60, 80, 100, 75, 90]

        for i, height in enumerate(bars):
            x = 400 + i * 60
            draw.rectangle([x, base_y - height, x + bar_width, base_y],
                          fill=self.brand_colors['primary'])

    def _draw_tech_icon(self, draw: ImageDraw):
        """Desenha ícone tech simples"""
        center_x, center_y = 540, 700

        # Ícone de código < />
        draw.text((center_x - 40, center_y - 20), "<",
                 font=self.fonts['title'], fill=self.brand_colors['primary'])
        draw.text((center_x - 10, center_y - 20), "/",
                 font=self.fonts['title'], fill=self.brand_colors['accent'])
        draw.text((center_x + 20, center_y - 20), ">",
                 font=self.fonts['title'], fill=self.brand_colors['primary'])

    def _draw_engagement_buttons(self, draw: ImageDraw):
        """Desenha botões de engajamento visuais"""
        buttons = [
            ("👍", 400, 600),
            ("💬", 540, 600),
            ("↗️", 680, 600)
        ]

        for emoji, x, y in buttons:
            # Background do botão
            draw.rounded_rectangle([x - 30, y - 25, x + 30, y + 25],
                                  radius=25, fill=self.brand_colors['white'])
            # Emoji
            draw.text((x - 15, y - 20), emoji, font=self.fonts['subtitle'])

    def _get_category_emoji(self, category: Optional[str]) -> str:
        """Retorna emoji baseado na categoria"""
        emoji_map = {
            'AI': '🤖',
            'Machine Learning': '🧠',
            'Web Development': '💻',
            'Mobile': '📱',
            'Cybersecurity': '🔒',
            'Blockchain': '⛓️',
            'Cloud': '☁️',
            'DevOps': '⚙️'
        }
        return emoji_map.get(category, '🚀')

    def _get_slide_accent_color(self, slide_number: int) -> str:
        """Retorna cor de destaque para o slide"""
        colors = [
            self.brand_colors['primary'],
            self.brand_colors['accent'],
            '#10B981',  # Green
            '#F59E0B',  # Yellow
            '#EF4444'   # Red
        ]
        return colors[slide_number % len(colors)]

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Converte cor hex para RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _create_error_slide(self, slide_number: int, carousel_id: str) -> str:
        """Cria slide de erro"""
        image = Image.new('RGB', self.carousel_size, color=self.brand_colors['light_gray'])
        draw = ImageDraw.Draw(image)

        error_text = f"Erro ao gerar slide {slide_number}"
        text_width = draw.textlength(error_text, font=self.fonts['subtitle'])
        x_position = (self.carousel_size[0] - text_width) // 2

        draw.text((x_position, 500), error_text,
                 font=self.fonts['subtitle'], fill=self.brand_colors['gray'])

        # Salvar
        slide_filename = f"{carousel_id}_error_{slide_number:02d}.png"
        slide_path = os.path.join(self.output_dir, slide_filename)
        image.save(slide_path, "PNG")

        return slide_path


if __name__ == "__main__":
    # Teste do gerador
    generator = CarouselGenerator()

    test_carousel = [
        {
            "slide_number": 1,
            "title": "🚀 Python 3.12 Chegou!",
            "content": "Nova versão traz performance incrível",
            "visual_suggestion": "Logo Python"
        },
        {
            "slide_number": 2,
            "title": "💡 O que mudou?",
            "content": "Performance 15% melhor e novas funcionalidades para async/await",
            "visual_suggestion": "Gráfico de performance"
        },
        {
            "slide_number": 3,
            "title": "🤔 E você?",
            "content": "Já testou o Python 3.12? Conta nos comentários!",
            "visual_suggestion": "Call to action"
        }
    ]

    test_metadata = {
        'category': 'Programming',
        'brand': 'InstaCalebeDigital'
    }

    slides = generator.generate_carousel(test_carousel, test_metadata)
    print(f"Generated {len(slides)} slides:")
    for slide in slides:
        print(f"- {slide}")