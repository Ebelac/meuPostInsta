"""
Gerador de carrosséis no formato profissional (estilo Tiago Guitián)
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import requests
import textwrap
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ProfessionalCarouselGenerator:
    """Gerador de carrosséis no formato profissional para Instagram"""

    def __init__(self):
        self.output_dir = "assets/generated_carousels"

        # Dimensões atualizadas do Instagram (nova proporção)
        self.carousel_size = (1080, 1440)  # Nova proporção Instagram 2024

        # Layout sections (percentuais da altura)
        self.header_height = int(self.carousel_size[1] * 0.10)      # 10% - Header com perfil
        self.content_height = int(self.carousel_size[1] * 0.55)     # 55% - Texto principal
        self.visual_height = int(self.carousel_size[1] * 0.25)      # 25% - Gráfico/imagem
        self.footer_height = self.carousel_size[1] - self.header_height - self.content_height - self.visual_height  # 10% - Footer

        # Cores do tema
        self.colors = {
            'background': '#FFFFFF',
            'primary': '#1DA1F2',
            'secondary': '#14171A',
            'text_primary': '#14171A',
            'text_secondary': '#657786',
            'accent': '#1DA1F2',
            'light_gray': '#F7F9FA'
        }

        # Margens de segurança do Instagram (zona segura)
        self.margin = 60  # Margens laterais maiores para zona segura
        self.top_margin = 80  # Margem superior para evitar corte
        self.bottom_margin = 80  # Margem inferior para evitar corte
        self.padding = 30

        self._ensure_directories()
        self._load_fonts()

    def _ensure_directories(self):
        """Cria diretórios necessários"""
        os.makedirs(self.output_dir, exist_ok=True)

    def _load_fonts(self):
        """Carrega fontes otimizadas para cada seção"""
        self.fonts = {}

        # Tamanhos maiores para melhor ocupação do espaço
        font_sizes = {
            'profile_name': 44,     # Nome do perfil
            'profile_handle': 34,   # @handle
            'title': 68,           # Título principal
            'subtitle': 52,        # Subtítulos
            'body_large': 48,      # Texto corpo grande
            'body_medium': 42,     # Texto corpo médio (MAIOR para ocupar espaço)
            'body_small': 36,      # Texto corpo pequeno
            'caption': 28,         # Legendas e detalhes
            'number_large': 120,   # Números de destaque
            'number_medium': 72    # Números secundários
        }

        for font_type, size in font_sizes.items():
            try:
                # Prioridade para Helvetica Neue (mais próxima do Tiago)
                font_paths = [
                    f"/System/Library/Fonts/HelveticaNeue.ttc",  # Helvetica Neue - principal
                    f"/System/Library/Fonts/Helvetica.ttc",     # Helvetica fallback
                    f"/System/Library/Fonts/Avenir Next.ttc",   # Avenir Next - moderna
                    f"/Library/Fonts/Arial.ttf",                # Arial
                    f"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                    f"C:\\Windows\\Fonts\\segoeui.ttf"          # Windows - Segoe UI
                ]

                font_loaded = False
                for font_path in font_paths:
                    try:
                        if os.path.exists(font_path):
                            self.fonts[font_type] = ImageFont.truetype(font_path, size)
                            font_loaded = True
                            logger.info(f"Loaded system font {font_path} for {font_type} (size {size})")
                            break
                    except Exception:
                        continue

                if not font_loaded:
                    # Fallback para fonte padrão
                    self.fonts[font_type] = ImageFont.load_default()
                    logger.info(f"Using default font for {font_type}")

            except Exception as e:
                logger.warning(f"Could not load font for {font_type}: {e}")
                self.fonts[font_type] = ImageFont.load_default()

    def generate_quantum_carousel(self, carousel_data: Dict, slide_index: int = 1) -> str:
        """Gera um slide do carrossel sobre criptografia quântica"""

        # Criar imagem base
        image = Image.new('RGB', self.carousel_size, color=self.colors['background'])
        draw = ImageDraw.Draw(image)

        current_y = 0

        # 1. HEADER (10%) - Perfil
        current_y = self._draw_header_section(draw, current_y)

        # 2. CONTENT (55%) - Texto principal
        current_y = self._draw_content_section(draw, current_y, carousel_data, slide_index)

        # 3. VISUAL (25%) - Gráfico/imagem
        current_y = self._draw_visual_section(draw, current_y, carousel_data, slide_index)

        # 4. FOOTER (10%) - Informações extras
        self._draw_footer_section(draw, current_y, slide_index)

        # Salvar imagem
        slide_filename = f"professional_{carousel_data['id']}_slide_{slide_index:02d}.png"
        slide_path = os.path.join(self.output_dir, slide_filename)
        image.save(slide_path, "PNG", quality=95)

        logger.info(f"Generated professional slide: {slide_path}")
        return slide_path

    def _draw_header_section(self, draw: ImageDraw, start_y: int) -> int:
        """Desenha seção do header com perfil real"""

        # Background do header
        header_rect = [0, start_y, self.carousel_size[0], start_y + self.header_height]
        draw.rectangle(header_rect, fill=self.colors['light_gray'])

        # Posição do círculo da foto (AINDA MAIOR) - SEM CORTE
        profile_size = 100  # Aumentado de 80 para 100

        # CALCULAR POSIÇÃO PARA GARANTIR ESPAÇO SUFICIENTE
        min_space_needed = profile_size + 300  # foto + espaço para handle + badge
        if min_space_needed > self.carousel_size[0] - (self.margin * 2):
            # Se não couber, reduzir ligeiramente
            profile_size = 95

        profile_x = self.margin + 15  # Espaço seguro da margem esquerda
        profile_y = start_y + (self.header_height - profile_size) // 2

        # VERIFICAÇÃO FINAL para evitar corte
        max_x_allowed = self.carousel_size[0] - self.margin - profile_size - 250  # espaço para texto
        if profile_x > max_x_allowed:
            profile_x = max_x_allowed

        # Desenhar círculo de fundo para a foto (será coberto pela foto real se houver)
        profile_circle = [
            profile_x, profile_y,
            profile_x + profile_size, profile_y + profile_size
        ]
        draw.ellipse(profile_circle, fill=self.colors['primary'], outline=self.colors['background'], width=3)

        # Adicionar "CD" como fallback se a foto não carregar
        cd_x = profile_x + profile_size // 2
        cd_y = profile_y + profile_size // 2
        draw.text((cd_x, cd_y), "CD", font=self.fonts['profile_name'],
                 fill=self.colors['background'], anchor="mm")

        # Apenas @handle + badge verificado (sem nome) - MUITO MAIOR
        handle_x = profile_x + profile_size + 25  # Espaço adequado
        handle_y = profile_y + (profile_size // 2) - 45  # Subir mais o texto (era -35, agora -45)

        # Desenhar @handle MUITO MAIOR
        draw.text((handle_x, handle_y), "@seuhandle",
                 font=self.fonts['title'], fill=self.colors['text_primary'])  # Usar fonte title (68px)

        # Calcular posição do badge verificado (mesmo nível e tamanho do @)
        handle_width = draw.textlength("@seuhandle", font=self.fonts['title'])
        verified_x = handle_x + handle_width + 12
        verified_y = handle_y + 6  # Ajuste para alinhar com o texto muito maior

        # Desenhar badge verificado do MESMO TAMANHO da tipografia
        self._draw_verified_badge_typography_size(draw, verified_x, verified_y)

        return start_y + self.header_height

    def _get_profile_photo(self) -> str:
        """Busca foto de perfil na pasta assets/profile"""
        profile_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'profile')

        # Tentar diferentes formatos
        for filename in ['profile_photo.jpg', 'profile_photo.png', 'profile_photo.jpeg']:
            photo_path = os.path.join(profile_dir, filename)
            if os.path.exists(photo_path):
                return photo_path

        return None

    def _draw_profile_fallback(self, draw, profile_x, profile_y, profile_size):
        """Desenha círculo com iniciais como fallback"""
        # Círculo para foto de perfil
        profile_circle = [
            profile_x, profile_y,
            profile_x + profile_size, profile_y + profile_size
        ]
        draw.ellipse(profile_circle, fill=self.colors['primary'], outline=self.colors['background'], width=3)

        # Adicionar "CD" como placeholder da foto
        cd_x = profile_x + profile_size // 2
        cd_y = profile_y + profile_size // 2
        draw.text((cd_x, cd_y), "CD", font=self.fonts['profile_name'],
                 fill=self.colors['background'], anchor="mm")

    def _draw_verified_badge_typography_size(self, draw, x, y):
        """Desenha badge verificado do MESMO TAMANHO da tipografia (68px)"""
        # Tamanho proporcional à fonte title (68px) - aproximadamente metade da altura
        badge_size = 32

        # Círculo azul verificado
        draw.ellipse([x, y, x + badge_size, y + badge_size],
                    fill="#1DA1F2", outline="white", width=2)

        # Checkmark branco proporcional
        check_points = [
            (x + 8, y + 16),
            (x + 13, y + 21),
            (x + 24, y + 10)
        ]

        # Desenhar checkmark bem grosso
        draw.line([check_points[0], check_points[1]], fill="white", width=4)
        draw.line([check_points[1], check_points[2]], fill="white", width=4)

    def _draw_content_section(self, draw: ImageDraw, start_y: int, carousel_data: Dict, slide_index: int) -> int:
        """Desenha seção de conteúdo principal (55%)"""

        content_area = [self.margin, start_y + 20,
                       self.carousel_size[0] - self.margin, start_y + self.content_height]

        current_y = start_y + 40

        if slide_index == 1:
            # Slide de capa
            current_y = self._draw_cover_content(draw, current_y, carousel_data)
        else:
            # Slides de conteúdo
            current_y = self._draw_regular_content(draw, current_y, carousel_data, slide_index)

        return start_y + self.content_height

    def _draw_cover_content(self, draw: ImageDraw, start_y: int, carousel_data: Dict) -> int:
        """Desenha conteúdo da capa (slide 1)"""
        current_y = start_y

        # Título principal grande
        title_lines = self._wrap_text(carousel_data['title'], 800, 'title')
        for line in title_lines:
            text_width = draw.textlength(line, font=self.fonts['title'])
            x_position = (self.carousel_size[0] - text_width) // 2

            draw.text((x_position, current_y), line,
                     font=self.fonts['title'], fill=self.colors['text_primary'])
            current_y += 85  # Maior espaçamento

        current_y += 30

        # Subtítulo/resumo
        subtitle_text = "Computação quântica ameaça segurança das criptomoedas até 2029"
        subtitle_lines = self._wrap_text(subtitle_text, 700, 'subtitle')

        for line in subtitle_lines:
            text_width = draw.textlength(line, font=self.fonts['subtitle'])
            x_position = (self.carousel_size[0] - text_width) // 2

            draw.text((x_position, current_y), line,
                     font=self.fonts['subtitle'], fill=self.colors['text_secondary'])
            current_y += 65  # Maior espaçamento

        return current_y

    def _draw_regular_content(self, draw: ImageDraw, start_y: int, carousel_data: Dict, slide_index: int) -> int:
        """Desenha conteúdo de slides regulares"""
        current_y = start_y

        # Definir conteúdo baseado no tipo de carrossel e slide
        content_map = {
            1: {  # Alerta de Segurança
                2: {
                    'title': '⚡ Velocidade Quântica',
                    'primary': 'Computadores quânticos são',
                    'highlight': '100 MILHÕES',
                    'secondary': 'de vezes mais rápidos que computadores atuais'
                },
                3: {
                    'title': '🎯 Principais Alvos',
                    'primary': 'Criptomoedas em risco:',
                    'list': ['• Bitcoin (SHA-256)', '• Ethereum (Keccak-256)', '• Todas as principais altcoins']
                },
                4: {
                    'title': '⏰ Timeline Crítico',
                    'primary': 'Estimativa dos especialistas:',
                    'highlight': '2029',
                    'secondary': 'Ano em que a criptografia atual pode ser quebrada'
                },
                5: {
                    'title': '🛡️ Como se Proteger',
                    'primary': 'Ações recomendadas:',
                    'list': ['• Acompanhar criptografia pós-quântica', '• Diversificar investimentos', '• Ficar atento a atualizações']
                }
            },
            2: {  # Explicação Técnica
                2: {
                    'title': '💻 Bits vs Qubits',
                    'primary': 'Computador clássico:',
                    'highlight': '0 ou 1',
                    'secondary': 'Computador quântico: 0, 1 ou AMBOS simultaneamente'
                },
                3: {
                    'title': '⚡ Superposição Quântica',
                    'primary': 'Permite processar',
                    'highlight': 'MILHÕES',
                    'secondary': 'de possibilidades ao mesmo tempo'
                },
                4: {
                    'title': '🔐 Algoritmo de Shor',
                    'primary': 'Criado especificamente para quebrar:',
                    'list': ['• RSA', '• Criptografia de curva elíptica', '• Sistemas atuais de blockchain']
                },
                5: {
                    'title': '🏭 Estado Atual',
                    'primary': 'Empresas com computadores quânticos:',
                    'list': ['• Google (Sycamore)', '• IBM (Eagle)', '• Microsoft (Azure Quantum)']
                }
            },
            3: {  # Bitcoin vs Quântico
                2: {
                    'title': '🔐 SHA-256 em Risco',
                    'primary': 'Algoritmo do Bitcoin pode ser quebrado em:',
                    'highlight': '10 MINUTOS',
                    'secondary': 'por um computador quântico avançado'
                },
                3: {
                    'title': '💰 Valor em Risco',
                    'primary': 'Mercado total de criptos:',
                    'highlight': 'US$ 1,3 TRI',
                    'secondary': 'Toda essa riqueza pode estar vulnerável'
                },
                4: {
                    'title': '⏱️ Mineração Obsoleta',
                    'primary': 'Mineração atual:',
                    'highlight': '10 MIN',
                    'secondary': 'Computador quântico: INSTANTÂNEO'
                },
                5: {
                    'title': '🔄 Adaptação Urgente',
                    'primary': 'Bitcoin precisa implementar:',
                    'list': ['• Algoritmos pós-quânticos', '• Novo sistema de assinaturas', '• Consenso da comunidade']
                }
            }
        }

        # Obter conteúdo específico
        carousel_id = carousel_data.get('id', 1)
        slide_content = content_map.get(carousel_id, {}).get(slide_index, {
            'title': f'Slide {slide_index}',
            'primary': 'Conteúdo em desenvolvimento...',
            'secondary': 'Mais informações em breve.'
        })

        # Desenhar título do slide (MAIOR)
        if 'title' in slide_content:
            draw.text((self.margin + 20, current_y), slide_content['title'],
                     font=self.fonts['subtitle'], fill=self.colors['primary'])  # Fonte maior
            current_y += 75  # Maior espaçamento

        # Desenhar texto principal (MAIOR)
        if 'primary' in slide_content:
            primary_lines = self._wrap_text(slide_content['primary'], 900, 'body_large')  # Largura maior
            for line in primary_lines:
                draw.text((self.margin + 20, current_y), line,
                         font=self.fonts['body_large'], fill=self.colors['text_primary'])  # Fonte maior
                current_y += 55  # Maior espaçamento
            current_y += 35

        # Desenhar destaque numérico
        if 'highlight' in slide_content:
            text_width = draw.textlength(slide_content['highlight'], font=self.fonts['number_large'])
            x_position = (self.carousel_size[0] - text_width) // 2

            draw.text((x_position, current_y), slide_content['highlight'],
                     font=self.fonts['number_large'], fill=self.colors['accent'])
            current_y += 140  # Muito mais espaço para números grandes

        # Desenhar texto secundário (MAIOR)
        if 'secondary' in slide_content:
            secondary_lines = self._wrap_text(slide_content['secondary'], 900, 'body_medium')  # Fonte e largura maior
            for line in secondary_lines:
                text_width = draw.textlength(line, font=self.fonts['body_medium'])
                x_position = (self.carousel_size[0] - text_width) // 2

                draw.text((x_position, current_y), line,
                         font=self.fonts['body_medium'], fill=self.colors['text_secondary'])  # Fonte maior
                current_y += 50  # Maior espaçamento

        # Desenhar lista (MAIOR)
        if 'list' in slide_content:
            for item in slide_content['list']:
                draw.text((self.margin + 20, current_y), item,
                         font=self.fonts['body_medium'], fill=self.colors['text_primary'])  # Fonte maior
                current_y += 50  # Maior espaçamento

        return current_y

    def _draw_visual_section(self, draw: ImageDraw, start_y: int, carousel_data: Dict, slide_index: int) -> int:
        """Desenha seção visual/gráfico (25%)"""

        visual_area = [self.margin, start_y,
                      self.carousel_size[0] - self.margin, start_y + self.visual_height]

        # Background da área visual
        draw.rectangle([visual_area[0], visual_area[1], visual_area[2], visual_area[3]],
                      fill=self.colors['light_gray'])

        if slide_index == 1:
            # Slide de capa - mostrar emoji/ícone grande
            icon_text = "🔐"
            icon_size = 120
            icon_x = (self.carousel_size[0]) // 2
            icon_y = start_y + self.visual_height // 2

            # Usar fonte grande para emoji (simulado com texto)
            draw.text((icon_x, icon_y), icon_text,
                     font=self.fonts['number_large'], fill=self.colors['primary'], anchor="mm")

        elif slide_index <= 3:
            # Slides com gráfico simples
            self._draw_simple_chart(draw, start_y, slide_index)

        else:
            # Slides finais com call-to-action visual
            cta_text = "📊 Acompanhe mais\nnovas tech"
            cta_x = (self.carousel_size[0]) // 2
            cta_y = start_y + self.visual_height // 2

            lines = cta_text.split('\n')
            line_height = 35
            total_height = len(lines) * line_height
            current_y = cta_y - total_height // 2

            for line in lines:
                text_width = draw.textlength(line, font=self.fonts['body_medium'])
                x_position = (self.carousel_size[0] - text_width) // 2
                draw.text((x_position, current_y), line,
                         font=self.fonts['body_medium'], fill=self.colors['text_secondary'])
                current_y += line_height

        return start_y + self.visual_height

    def _draw_simple_chart(self, draw: ImageDraw, start_y: int, slide_type: int):
        """Desenha gráfico simples na seção visual"""
        chart_area = [
            self.margin + 50, start_y + 20,
            self.carousel_size[0] - self.margin - 50, start_y + self.visual_height - 20
        ]

        if slide_type == 2:
            # Gráfico de barras comparativo
            bar_width = 40
            bar_gap = 60
            base_y = chart_area[3] - 40

            # Barra 1 - Computador clássico (baixa)
            bar1_height = 30
            bar1_rect = [chart_area[0] + 100, base_y - bar1_height,
                        chart_area[0] + 100 + bar_width, base_y]
            draw.rectangle(bar1_rect, fill=self.colors['text_secondary'])

            # Label
            draw.text((chart_area[0] + 120, base_y + 10), "Clássico",
                     font=self.fonts['caption'], fill=self.colors['text_secondary'], anchor="mm")

            # Barra 2 - Computador quântico (alta)
            bar2_height = 120
            bar2_rect = [chart_area[0] + 100 + bar_width + bar_gap, base_y - bar2_height,
                        chart_area[0] + 100 + bar_width + bar_gap + bar_width, base_y]
            draw.rectangle(bar2_rect, fill=self.colors['primary'])

            # Label
            draw.text((chart_area[0] + 120 + bar_width + bar_gap, base_y + 10), "Quântico",
                     font=self.fonts['caption'], fill=self.colors['primary'], anchor="mm")

        elif slide_type == 3:
            # Timeline visual
            timeline_y = start_y + self.visual_height // 2
            timeline_start = chart_area[0] + 50
            timeline_end = chart_area[2] - 50

            # Linha principal
            draw.line([(timeline_start, timeline_y), (timeline_end, timeline_y)],
                     fill=self.colors['text_secondary'], width=3)

            # Marcos na timeline
            years = ['2024', '2026', '2028', '2029']
            segment_width = (timeline_end - timeline_start) // (len(years) - 1)

            for i, year in enumerate(years):
                x = timeline_start + i * segment_width

                # Ponto na linha
                draw.ellipse([x-8, timeline_y-8, x+8, timeline_y+8],
                           fill=self.colors['accent'] if year == '2029' else self.colors['text_secondary'])

                # Ano
                draw.text((x, timeline_y + 25), year,
                         font=self.fonts['caption'], fill=self.colors['text_primary'], anchor="mm")

    def _draw_footer_section(self, draw: ImageDraw, start_y: int, slide_index: int):
        """Desenha seção do footer"""
        # Linha separadora
        draw.line([(self.margin, start_y + 10), (self.carousel_size[0] - self.margin, start_y + 10)],
                 fill=self.colors['light_gray'], width=2)

        # Informações do footer
        footer_y = start_y + 30

        # Data/fonte à esquerda
        draw.text((self.margin + 20, footer_y), "Fonte: Análise TechCrunch, IBM Research",
                 font=self.fonts['caption'], fill=self.colors['text_secondary'])

        # Slide number à direita
        slide_text = f"{slide_index}/5"
        text_width = draw.textlength(slide_text, font=self.fonts['caption'])
        draw.text((self.carousel_size[0] - self.margin - 20 - text_width, footer_y), slide_text,
                 font=self.fonts['caption'], fill=self.colors['text_secondary'])

    def _wrap_text(self, text: str, max_width: int, font_type: str) -> List[str]:
        """Quebra texto em linhas"""
        font = self.fonts[font_type]
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
                    lines.append(word)

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def generate_complete_carousel(self, carousel_data: Dict) -> List[str]:
        """Gera carrossel completo com 5 slides"""
        slides = []

        for slide_index in range(1, 6):
            slide_path = self.generate_quantum_carousel(carousel_data, slide_index)
            slides.append(slide_path)

        return slides


if __name__ == "__main__":
    # Teste do gerador
    generator = ProfessionalCarouselGenerator()

    test_carousel = {
        'id': 1,
        'title': '🚨 ALERTA: Suas Criptos Estão em Risco!',
        'approach': 'Alerta de Segurança'
    }

    slides = generator.generate_complete_carousel(test_carousel)
    print(f"Generated {len(slides)} professional slides:")
    for slide in slides:
        print(f"- {slide}")