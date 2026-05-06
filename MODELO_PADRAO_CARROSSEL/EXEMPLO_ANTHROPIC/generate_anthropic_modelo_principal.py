#!/usr/bin/env python3
"""
Gera UM ÚNICO carrossel com 8 slides cobrindo todos os aspectos da criptografia quântica
"""
import sys
import os
import requests
from PIL import Image, ImageDraw
import urllib.parse

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.designer.professional_carousel import ProfessionalCarouselGenerator


class SingleCarouselGenerator(ProfessionalCarouselGenerator):
    """Gerador para carrossel único de 8 slides"""

    def generate_complete_9_slide_carousel(self, carousel_data: dict) -> list:
        """Gera carrossel completo com 9 slides únicos com imagens reais + CTA"""
        slides = []

        # Baixar todas as imagens primeiro
        print("📥 Preparando imagens para os slides...")
        for slide_index in range(1, 10):  # Agora são 9 slides
            self._get_slide_image(slide_index)

        for slide_index in range(1, 10):  # 9 slides
            slide_path = self.generate_quantum_carousel_with_images(carousel_data, slide_index)
            slides.append(slide_path)

        return slides

    def generate_quantum_carousel_with_images(self, carousel_data: dict, slide_index: int = 1) -> str:
        """Gera um slide do carrossel com imagem real integrada"""

        # Criar imagem base
        image = Image.new('RGB', self.carousel_size, color=self.colors['background'])

        # 1. Adicionar imagem real na seção visual ANTES de criar o draw
        visual_start_y = self.header_height + self.content_height
        image_path = self._get_slide_image(slide_index)

        if image_path and os.path.exists(image_path):
            try:
                # Carregar imagem
                slide_image = Image.open(image_path)

                # PREENCHER TODA A ÁREA GRÁFICA (pode vazar das margens como Tiago)
                # Usar toda a largura do carrossel (sem margens)
                target_width = self.carousel_size[0]  # Largura total
                target_height = self.visual_height    # Altura da seção visual

                # Redimensionar para preencher completamente a área (crop se necessário)
                img_ratio = slide_image.width / slide_image.height
                target_ratio = target_width / target_height

                if img_ratio > target_ratio:
                    # Imagem mais larga - ajustar pela altura
                    new_height = target_height
                    new_width = int(new_height * img_ratio)
                else:
                    # Imagem mais alta - ajustar pela largura
                    new_width = target_width
                    new_height = int(new_width / img_ratio)

                # Redimensionar imagem
                slide_image = slide_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Centralizar e fazer crop se necessário para preencher exatamente a área
                if new_width > target_width:
                    # Crop horizontal
                    crop_x = (new_width - target_width) // 2
                    slide_image = slide_image.crop((crop_x, 0, crop_x + target_width, new_height))

                if new_height > target_height:
                    # Crop vertical
                    crop_y = (new_height - target_height) // 2
                    slide_image = slide_image.crop((0, crop_y, slide_image.width, crop_y + target_height))

                # Posicionar imagem para ocupar toda a largura (sem margens)
                img_x = 0  # Começar do zero (vaza das margens)
                img_y = visual_start_y

                # Colar imagem preenchendo toda a área
                image.paste(slide_image, (img_x, img_y))

                print(f"✅ Imagem FULL-WIDTH integrada no slide {slide_index}")

            except Exception as e:
                print(f"❌ Erro ao integrar imagem no slide {slide_index}: {e}")

        # 2. Criar draw e adicionar elementos base
        draw = ImageDraw.Draw(image)

        current_y = 0

        # Header (com círculo de fundo)
        current_y = self._draw_header_section(draw, current_y)

        # 3. DEPOIS do header, adicionar foto por cima
        self._add_profile_photo_to_image(image)

        # Content
        current_y = self._draw_content_section(draw, current_y, carousel_data, slide_index)

        # Pular visual section (já foi adicionada)
        current_y += self.visual_height

        # Footer
        self._draw_footer_section(draw, current_y, slide_index)

        # Salvar slide
        filename = f"anthropic_vazamento_slide_{slide_index:02d}.png"
        file_path = os.path.join(self.output_dir, filename)

        image.save(file_path, "PNG", quality=95, optimize=True)

        return file_path

    def _add_profile_photo_to_image(self, base_image):
        """Adiciona foto de perfil circular ao header"""
        try:
            # Buscar foto de perfil
            profile_dir = "assets/profile"
            profile_photo_path = None

            print(f"🔍 Procurando foto em: {os.path.abspath(profile_dir)}")

            for filename in ['profile_photo.jpg', 'profile_photo.png', 'profile_photo.jpeg']:
                path = os.path.join(profile_dir, filename)
                print(f"   Testando: {path} -> Existe: {os.path.exists(path)}")
                if os.path.exists(path):
                    profile_photo_path = path
                    print(f"✅ Foto encontrada: {profile_photo_path}")
                    break

            if not profile_photo_path:
                print("⚠️ Foto de perfil não encontrada - usando placeholder")
                return

            # Carregar foto
            profile_img = Image.open(profile_photo_path).convert('RGB')

            # Configurações da posição (igual ao header) - MAIOR
            profile_size = 100  # Mesmo tamanho do header

            # CALCULAR POSIÇÃO IGUAL AO HEADER (sem corte)
            min_space_needed = profile_size + 300  # foto + espaço para texto + badge
            if min_space_needed > self.carousel_size[0] - (self.margin * 2):
                profile_size = 95  # Reduzir se necessário

            profile_x = self.margin + 15  # Mesmo do header
            profile_y = (self.header_height - profile_size) // 2

            # VERIFICAÇÃO FINAL
            max_x_allowed = self.carousel_size[0] - self.margin - profile_size - 250
            if profile_x > max_x_allowed:
                profile_x = max_x_allowed

            # Fazer crop quadrado se necessário
            width, height = profile_img.size
            if width != height:
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                profile_img = profile_img.crop((left, top, left + size, top + size))

            # REDIMENSIONAR EM ALTA QUALIDADE (4x maior para suavização)
            high_res_size = profile_size * 4  # 400px para melhor qualidade
            profile_img = profile_img.resize((high_res_size, high_res_size), Image.Resampling.LANCZOS)

            # CRIAR MÁSCARA CIRCULAR EM ALTA RESOLUÇÃO com antialiasing
            mask = Image.new('L', (high_res_size, high_res_size), 0)
            mask_draw = ImageDraw.Draw(mask)

            # Desenhar círculo com bordas suaves (antialiasing)
            mask_draw.ellipse([0, 0, high_res_size, high_res_size], fill=255)

            # APLICAR MÁSCARA EM ALTA RESOLUÇÃO
            circular_img = Image.new('RGBA', (high_res_size, high_res_size), (0, 0, 0, 0))
            circular_img.paste(profile_img, (0, 0))
            circular_img.putalpha(mask)

            # REDIMENSIONAR PARA TAMANHO FINAL (com suavização automática)
            circular_img = circular_img.resize((profile_size, profile_size), Image.Resampling.LANCZOS)

            # COLAR NA POSIÇÃO CORRETA
            base_image.paste(circular_img, (profile_x, profile_y), circular_img)

            print(f"✅ Foto de perfil real integrada: {profile_photo_path}")

        except Exception as e:
            print(f"❌ Erro ao integrar foto de perfil: {e}")
            import traceback
            traceback.print_exc()

    def _draw_content_section(self, draw, start_y: int, carousel_data: dict, slide_index: int) -> int:
        """Conteúdo personalizado para cada um dos 9 slides"""
        current_y = start_y + 50  # ESPAÇAMENTO PADRONIZADO para todos os slides

        # Definir conteúdo específico para cada slide
        slide_content = self._get_slide_content(slide_index)

        # TODOS os slides usam o mesmo método agora (sem diferenciação especial para slide 1)
        current_y = self._draw_specific_content(draw, current_y, slide_content)

        return start_y + self.content_height

    def _draw_visual_section(self, draw, start_y: int, carousel_data: dict, slide_index: int) -> int:
        """Desenha seção visual com imagens reais para cada slide"""

        visual_area = [self.margin, start_y,
                      self.carousel_size[0] - self.margin, start_y + self.visual_height]

        # Background da área visual
        draw.rectangle([visual_area[0], visual_area[1], visual_area[2], visual_area[3]],
                      fill=self.colors['light_gray'])

        # Carregar e inserir imagem real para cada slide
        image_path = self._get_slide_image(slide_index)
        if image_path and os.path.exists(image_path):
            try:
                # Carregar imagem
                slide_image = Image.open(image_path)

                # Redimensionar para caber na área visual
                area_width = visual_area[2] - visual_area[0] - 40  # margem interna
                area_height = visual_area[3] - visual_area[1] - 40

                slide_image.thumbnail((area_width, area_height), Image.Resampling.LANCZOS)

                # Calcular posição para centralizar
                img_x = visual_area[0] + (area_width - slide_image.width) // 2 + 20
                img_y = visual_area[1] + (area_height - slide_image.height) // 2 + 20

                # Integrar imagem no draw atual
                # Como estamos usando ImageDraw, precisamos integrar diferente
                # Por ora, vamos sobrescrever a área com uma cor que representa a imagem
                draw.rectangle([img_x, img_y, img_x + slide_image.width, img_y + slide_image.height],
                              fill="#4A90E2")  # Cor placeholder para imagem

                # Adicionar texto sobre a "imagem"
                text_y = img_y + slide_image.height + 10
                slide_labels = {
                    1: "VAZAMENTO MASSIVO",
                    2: "CÓDIGO EXPOSTO",
                    3: "IMPACTO GIGANTE",
                    4: "FALHA HUMANA",
                    5: "DAMAGE CONTROL",
                    6: "MERCADO ABALADO",
                    7: "ALERTA LEGAL",
                    8: "PREVENÇÃO ATIVA",
                    9: "COMPARTILHE"
                }

                label_text = slide_labels.get(slide_index, "IMAGEM")
                text_width = draw.textlength(label_text, font=self.fonts['caption'])
                text_x = img_x + (slide_image.width - text_width) // 2

                draw.text((text_x, text_y), label_text,
                         font=self.fonts['caption'], fill=self.colors['text_primary'])

                return start_y + self.visual_height

            except Exception as e:
                print(f"Erro ao carregar imagem para slide {slide_index}: {e}")

        # Fallback: texto simples se não conseguir carregar imagem
        center_x = (visual_area[0] + visual_area[2]) // 2
        center_y = (visual_area[1] + visual_area[3]) // 2

        slide_texts = {
            1: "🚨 VAZAMENTO",
            2: "💻 GITHUB",
            3: "⚡ ANTHROPIC",
            4: "🔓 FALHA",
            5: "⚖️ DMCA",
            6: "📈 MERCADO",
            7: "🚨 ALERTA",
            8: "🛡️ SEGURANÇA",
            9: "📱 SHARE"
        }

        draw.text((center_x, center_y), slide_texts.get(slide_index, "📊"),
                 font=self.fonts['number_large'], fill=self.colors['primary'], anchor="mm")

        return start_y + self.visual_height

    def _get_slide_image(self, slide_index: int) -> str:
        """Retorna caminho da imagem temática Anthropic (já baixadas)"""

        # Usar imagens temáticas específicas do Anthropic já baixadas
        thematic_filename = f'anthropic_slide_{slide_index}.jpg'
        thematic_path = os.path.join('assets/slide_images', thematic_filename)

        # Verificar se imagem temática existe
        if os.path.exists(thematic_path):
            print(f"✅ Usando imagem temática: {thematic_filename}")
            return thematic_path

        print(f"⚠️ Imagem temática não encontrada: {thematic_filename}")

        # URLs de fallback (se imagens temáticas não existirem)
        fallback_urls = {
            1: "https://images.unsplash.com/photo-1556075798-4825dfaaf498?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # GitHub code interface
            2: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Code on screens
            3: "https://images.unsplash.com/photo-1563013544-824ae1b704d3?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # AI/tech crisis
            4: "https://images.unsplash.com/photo-1563986768609-322da13575f3?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Security breach/hack
            5: "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Legal documents/lawyers
            6: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Market crash/panic
            7: "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Cybersecurity protection
            8: "https://images.unsplash.com/photo-1519389950473-47ba0277781c?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Future technology/action
            9: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?ixlib=rb-4.0.3&w=500&h=300&fit=crop"   # Sharing/social media CTA
        }

        # Criar diretório para imagens se não existir
        images_dir = "assets/slide_images"
        os.makedirs(images_dir, exist_ok=True)

        # Caminho local da imagem
        image_filename = f"slide_{slide_index}.jpg"
        image_path = os.path.join(images_dir, image_filename)

        # Se a imagem já existe localmente, usar ela
        if os.path.exists(image_path):
            return image_path

        # URLs alternativas SUPER APURADAS para cada tema
        fallback_urls = {
            1: "https://images.unsplash.com/photo-1555949963-aa79dcee981c?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Warning/alert screen
            2: "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Quantum particles/lab
            3: "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Speed lines/fast tech
            4: "https://images.unsplash.com/photo-1621761191319-c6fb62004040?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Golden Bitcoin
            5: "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Stack of money
            6: "https://images.unsplash.com/photo-1501139083538-0139583c060f?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Alarm clock
            7: "https://images.unsplash.com/photo-1563206767-5b18f218e8de?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Digital shield
            8: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Space/cosmic future
            9: "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?ixlib=rb-4.0.3&w=500&h=300&fit=crop"   # Social sharing/community
        }

        # URLs temáticas ULTRA ESPECÍFICAS para máxima precisão
        ultra_specific_urls = {
            1: "https://images.unsplash.com/photo-1571171637578-41bc2dd41cd2?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Digital security warning
            2: "https://images.unsplash.com/photo-1667372335962-5fd503b73e03?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Quantum physics visual
            3: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # High-speed data
            4: "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Bitcoin physical coin
            5: "https://images.unsplash.com/photo-1560472355-536de3962603?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Money risk concept
            6: "https://images.unsplash.com/photo-1565520651525-2c4b3bc2e387?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Countdown timer
            7: "https://images.unsplash.com/photo-1606868306217-dbf5046868d2?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Cryptographic protection
            8: "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?ixlib=rb-4.0.3&w=500&h=300&fit=crop",  # Future preparation
            9: "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?ixlib=rb-4.0.3&w=500&h=300&fit=crop"   # People connecting/sharing
        }

        # Tentar baixar a imagem (principal + fallback + ultra específica)
        if slide_index in image_urls:
            # Lista completa de URLs para tentar
            urls_to_try = [
                image_urls[slide_index],
                fallback_urls.get(slide_index),
                ultra_specific_urls.get(slide_index)
            ]

            # Remover URLs None
            urls_to_try = [url for url in urls_to_try if url]

            for url_index, url in enumerate(urls_to_try):
                try:
                    source_names = ["principal", "alternativa", "ultra-específica"]
                    source = source_names[url_index] if url_index < len(source_names) else f"opção {url_index + 1}"
                    print(f"📥 Baixando imagem {source} para slide {slide_index}...")

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }

                    response = requests.get(url, headers=headers, timeout=15)
                    response.raise_for_status()

                    with open(image_path, 'wb') as f:
                        f.write(response.content)

                    print(f"✅ Imagem {source} salva: {image_path}")
                    return image_path

                except Exception as e:
                    print(f"❌ Erro com imagem {source} para slide {slide_index}: {e}")
                    continue

        # Se nenhuma imagem funcionou, usar uma imagem genérica
        try:
            print(f"📥 Usando imagem genérica para slide {slide_index}...")
            generic_url = f"https://via.placeholder.com/400x250/4A90E2/FFFFFF?text=Slide+{slide_index}"

            response = requests.get(generic_url, timeout=10)
            response.raise_for_status()

            with open(image_path, 'wb') as f:
                f.write(response.content)

            print(f"✅ Imagem genérica salva: {image_path}")
            return image_path

        except Exception as e:
            print(f"❌ Erro até com imagem genérica para slide {slide_index}: {e}")

        return None

    def _draw_threat_visual(self, draw, area):
        """Visual para slide 1 - Ameaça com gráficos reais"""
        center_x = (area[0] + area[2]) // 2
        center_y = (area[1] + area[3]) // 2

        # Triângulo de alerta
        triangle_size = 60
        points = [
            (center_x - 60, center_y - 20 + triangle_size//2),
            (center_x - 60 + triangle_size, center_y - 20 + triangle_size//2),
            (center_x - 60 + triangle_size//2, center_y - 20 - triangle_size//2)
        ]
        draw.polygon(points, fill="#FF4444", outline="#CC0000", width=3)

        # Ponto de exclamação no triângulo
        draw.text((center_x - 60 + triangle_size//2, center_y - 20), "!",
                 font=self.fonts['body_large'], fill="white", anchor="mm")

        # Cadeado quebrado (retângulo + linha diagonal)
        lock_x = center_x + 40
        lock_y = center_y - 30
        draw.rectangle([lock_x, lock_y, lock_x + 40, lock_y + 50],
                      fill="#666666", outline="#333333", width=2)
        # Linha diagonal para mostrar "quebrado"
        draw.line([(lock_x, lock_y + 50), (lock_x + 40, lock_y)],
                 fill="#FF0000", width=4)

        # Texto "VULNERÁVEL"
        draw.text((center_x, center_y + 50), "VULNERÁVEL",
                 font=self.fonts['body_medium'], fill="#FF4444", anchor="mm")

    def _draw_quantum_computer_visual(self, draw, area):
        """Visual para slide 2 - Computador quântico com gráficos reais"""
        center_x = (area[0] + area[2]) // 2
        center_y = (area[1] + area[3]) // 2

        # Átomo quântico (círculos concêntricos + elipses orbitais)
        atom_center_x = center_x - 70
        atom_center_y = center_y - 10

        # Núcleo
        draw.ellipse([atom_center_x - 15, atom_center_y - 15,
                     atom_center_x + 15, atom_center_y + 15],
                    fill=self.colors['primary'], outline=self.colors['primary'])

        # Órbitas
        for i, size in enumerate([40, 60]):
            draw.ellipse([atom_center_x - size, atom_center_y - size//2,
                         atom_center_x + size, atom_center_y + size//2],
                        outline=self.colors['accent'], width=2)

        # Seta de transformação
        arrow_y = center_y - 10
        draw.polygon([
            (center_x - 20, arrow_y),
            (center_x + 20, arrow_y),
            (center_x + 15, arrow_y - 8),
            (center_x + 20, arrow_y),
            (center_x + 15, arrow_y + 8)
        ], fill=self.colors['text_primary'])

        # Computador (retângulo + tela)
        comp_x = center_x + 50
        comp_y = center_y - 25
        draw.rectangle([comp_x, comp_y, comp_x + 60, comp_y + 50],
                      fill=self.colors['light_gray'], outline=self.colors['text_primary'], width=2)
        draw.rectangle([comp_x + 5, comp_y + 5, comp_x + 55, comp_y + 35],
                      fill=self.colors['primary'], outline=self.colors['primary'])

        draw.text((center_x, center_y + 40), "FÍSICA QUÂNTICA",
                 font=self.fonts['body_small'], fill=self.colors['text_secondary'], anchor="mm")

    def _draw_speed_comparison_visual(self, draw, area):
        """Visual para slide 3 - Velocidade com barras comparativas"""
        center_x = (area[0] + area[2]) // 2
        center_y = (area[1] + area[3]) // 2

        # Barra pequena (computador normal)
        bar1_width = 20
        bar1_height = 30
        bar1_x = center_x - 80
        draw.rectangle([bar1_x, center_y - bar1_height//2,
                       bar1_x + bar1_width, center_y + bar1_height//2],
                      fill="#CCCCCC", outline="#999999", width=1)
        draw.text((bar1_x + bar1_width//2, center_y + 25), "Normal",
                 font=self.fonts['caption'], fill=self.colors['text_secondary'], anchor="mm")

        # VS
        draw.text((center_x, center_y - 5), "VS",
                 font=self.fonts['body_medium'], fill=self.colors['text_primary'], anchor="mm")

        # Barra gigante (computador quântico)
        bar2_width = 60
        bar2_height = 80
        bar2_x = center_x + 40
        draw.rectangle([bar2_x, center_y - bar2_height//2,
                       bar2_x + bar2_width, center_y + bar2_height//2],
                      fill=self.colors['primary'], outline=self.colors['accent'], width=2)
        draw.text((bar2_x + bar2_width//2, center_y + 50), "Quântico",
                 font=self.fonts['caption'], fill=self.colors['text_primary'], anchor="mm")

        # Multiplicador
        draw.text((center_x, center_y + 65), "100 MILHÕES X",
                 font=self.fonts['body_medium'], fill=self.colors['accent'], anchor="mm")

    def _draw_bitcoin_attack_visual(self, draw, area):
        """Visual para slide 4 - Bitcoin sob ataque"""
        center_x = (area[0] + area[2]) // 2
        center_y = (area[1] + area[3]) // 2

        # Bitcoin (círculo laranja com B)
        bitcoin_radius = 35
        bitcoin_x = center_x - 60
        draw.ellipse([bitcoin_x - bitcoin_radius, center_y - 20 - bitcoin_radius,
                     bitcoin_x + bitcoin_radius, center_y - 20 + bitcoin_radius],
                    fill="#F7931A", outline="#D2691E", width=3)
        draw.text((bitcoin_x, center_y - 20), "₿",
                 font=self.fonts['body_large'], fill="white", anchor="mm")

        # Raios de ataque (linhas pontilhadas vindas da direita)
        attack_x = center_x + 60
        for i, offset in enumerate([-15, 0, 15]):
            start_x = attack_x
            end_x = bitcoin_x + bitcoin_radius - 10
            start_y = center_y - 20 + offset
            end_y = center_y - 20 + offset

            # Linha de ataque
            draw.line([(start_x, start_y), (end_x, end_y)],
                     fill="#FF0000", width=3)
            # Ponta da seta
            draw.polygon([
                (end_x, end_y),
                (end_x - 10, end_y - 5),
                (end_x - 10, end_y + 5)
            ], fill="#FF0000")

        # Cronômetro
        draw.text((center_x, center_y + 40), "10 MINUTOS",
                 font=self.fonts['body_medium'], fill="#FF0000", anchor="mm")

    def _draw_money_risk_visual(self, draw, area):
        """Visual para slide 5 - Dinheiro em risco com gráfico"""
        center_x = (area[0] + area[2]) // 2
        center_y = (area[1] + area[3]) // 2

        # Pilha de moedas (círculos empilhados)
        coin_radius = 25
        for i in range(3):
            coin_y = center_y - 20 + i * 15
            draw.ellipse([center_x - coin_radius, coin_y - coin_radius,
                         center_x + coin_radius, coin_y + coin_radius],
                        fill="#FFD700", outline="#FFA500", width=2)
            draw.text((center_x, coin_y), "$",
                     font=self.fonts['body_medium'], fill="#B8860B", anchor="mm")

        # Seta descendente (indicando risco)
        arrow_x = center_x + 50
        draw.polygon([
            (arrow_x, center_y - 30),
            (arrow_x, center_y + 10),
            (arrow_x - 10, center_y),
            (arrow_x, center_y + 10),
            (arrow_x + 10, center_y)
        ], fill="#FF0000")

        # Triângulo de alerta
        triangle_x = center_x - 60
        points = [
            (triangle_x, center_y - 15),
            (triangle_x + 20, center_y - 15),
            (triangle_x + 10, center_y - 35)
        ]
        draw.polygon(points, fill="#FF4444")
        draw.text((triangle_x + 10, center_y - 25), "!",
                 font=self.fonts['body_small'], fill="white", anchor="mm")

        draw.text((center_x, center_y + 50), "US$ 1,3 TRILHÃO",
                 font=self.fonts['body_small'], fill="#FF0000", anchor="mm")

    def _draw_timeline_visual(self, draw, area):
        """Visual para slide 6 - Timeline com relógio"""
        center_x = (area[0] + area[2]) // 2
        center_y = (area[1] + area[3]) // 2

        # Relógio circular
        clock_radius = 35
        draw.ellipse([center_x - clock_radius, center_y - 30 - clock_radius,
                     center_x + clock_radius, center_y - 30 + clock_radius],
                    fill="white", outline=self.colors['text_primary'], width=3)

        # Ponteiros do relógio (indicando urgência - quase meia-noite)
        # Ponteiro das horas (curto)
        draw.line([(center_x, center_y - 30), (center_x + 15, center_y - 45)],
                 fill="#FF0000", width=4)
        # Ponteiro dos minutos (longo)
        draw.line([(center_x, center_y - 30), (center_x, center_y - 60)],
                 fill="#FF0000", width=3)

        # Centro do relógio
        draw.ellipse([center_x - 3, center_y - 33, center_x + 3, center_y - 27],
                    fill="#FF0000")

        # Marcadores das horas (12, 3, 6, 9)
        for hour in range(0, 12, 3):
            angle = hour * 30 * 3.14159 / 180  # Converter para radianos
            mark_x = center_x + 25 * (0 if hour % 6 == 0 else 1 if hour < 6 else 0)
            mark_y = center_y - 30 + 25 * (-1 if hour < 3 else 0 if hour < 9 else 1)
            draw.ellipse([mark_x - 2, mark_y - 2, mark_x + 2, mark_y + 2],
                        fill=self.colors['text_primary'])

        draw.text((center_x, center_y + 25), "2029",
                 font=self.fonts['number_medium'], fill="#FF0000", anchor="mm")

        draw.text((center_x, center_y + 55), "PRAZO LIMITE",
                 font=self.fonts['body_small'], fill=self.colors['text_secondary'], anchor="mm")

    def _draw_solution_visual(self, draw, area):
        """Visual para slide 7 - Escudo protetor"""
        center_x = (area[0] + area[2]) // 2
        center_y = (area[1] + area[3]) // 2

        # Escudo (formato clássico)
        shield_width = 60
        shield_height = 70
        shield_top = center_y - 35

        # Corpo do escudo
        points = [
            (center_x, shield_top),  # Topo
            (center_x - shield_width//2, shield_top + 20),  # Lateral esquerda
            (center_x - shield_width//2, shield_top + 40),
            (center_x, shield_top + shield_height),  # Ponta inferior
            (center_x + shield_width//2, shield_top + 40),
            (center_x + shield_width//2, shield_top + 20),  # Lateral direita
        ]
        draw.polygon(points, fill=self.colors['primary'], outline=self.colors['accent'], width=3)

        # Cruz no escudo (simbolizando proteção)
        line_offset = 15
        draw.line([(center_x, shield_top + line_offset),
                  (center_x, shield_top + shield_height - line_offset)],
                 fill="white", width=4)
        draw.line([(center_x - line_offset, shield_top + 25),
                  (center_x + line_offset, shield_top + 25)],
                 fill="white", width=4)

        # Elementos quânticos ao redor (órbitas)
        for angle in [0, 120, 240]:
            orbit_x = center_x + 40 * (1 if angle == 0 else -0.5 if angle == 120 else -0.5)
            orbit_y = center_y + 40 * (0 if angle == 0 else -0.866 if angle == 120 else 0.866)
            draw.ellipse([orbit_x - 8, orbit_y - 8, orbit_x + 8, orbit_y + 8],
                        fill=self.colors['accent'], outline=self.colors['accent'])

        draw.text((center_x, center_y + 55), "CRIPTOGRAFIA PÓS-QUÂNTICA",
                 font=self.fonts['caption'], fill=self.colors['text_primary'], anchor="mm")

    def _draw_action_visual(self, draw, area):
        """Visual para slide 8 - Call to action com foguete"""
        center_x = (area[0] + area[2]) // 2
        center_y = (area[1] + area[3]) // 2

        # Foguete (forma simples)
        rocket_width = 30
        rocket_height = 60
        rocket_top = center_y - 40

        # Corpo do foguete
        draw.rectangle([center_x - rocket_width//2, rocket_top + 15,
                       center_x + rocket_width//2, rocket_top + rocket_height],
                      fill=self.colors['accent'], outline=self.colors['primary'], width=2)

        # Ponta do foguete (triângulo)
        points = [
            (center_x, rocket_top),
            (center_x - rocket_width//2, rocket_top + 15),
            (center_x + rocket_width//2, rocket_top + 15)
        ]
        draw.polygon(points, fill=self.colors['primary'])

        # Propulsão (triângulos na base)
        flame_points = [
            (center_x - 10, rocket_top + rocket_height),
            (center_x, rocket_top + rocket_height + 15),
            (center_x + 10, rocket_top + rocket_height)
        ]
        draw.polygon(flame_points, fill="#FF4444")

        # Ícones ao redor (representando preparação)
        # Gráfico à esquerda
        chart_x = center_x - 60
        chart_y = center_y + 10
        draw.rectangle([chart_x, chart_y, chart_x + 20, chart_y + 20],
                      fill=self.colors['light_gray'], outline=self.colors['text_primary'])
        for i in range(3):
            bar_height = (i + 1) * 5
            draw.rectangle([chart_x + 2 + i*5, chart_y + 20 - bar_height,
                           chart_x + 6 + i*5, chart_y + 20],
                          fill=self.colors['primary'])

        # Lâmpada à direita (ideia)
        bulb_x = center_x + 60
        bulb_y = center_y + 10
        draw.ellipse([bulb_x - 10, bulb_y - 10, bulb_x + 10, bulb_y + 10],
                    fill="#FFD700", outline="#FFA500", width=2)
        draw.rectangle([bulb_x - 5, bulb_y + 5, bulb_x + 5, bulb_y + 15],
                      fill="#999999", outline="#666666")

        draw.text((center_x, center_y + 55), "PREPARE-SE",
                 font=self.fonts['body_medium'], fill=self.colors['primary'], anchor="mm")

    def _get_slide_content(self, slide_index: int) -> dict:
        """Conteúdo específico para cada slide do carrossel único"""

        content_map = {
            1: {
                'copy': 'ESCÂNDALO que pode DESTRUIR a Anthropic!\n\nMais de 8.000 repositórios no GitHub continham TODOS os segredos do Claude Code. O código que vale BILHÕES estava disponível para QUALQUER PESSOA baixar.\n\nEste pode ser o MAIOR VAZAMENTO da história da IA!'
            },
            2: {
                'copy': 'O PESADELO começou com um erro DEVASTADOR!\n\n8 mil+ repositórios EXPLODIRAM no GitHub com código-fonte ULTRA SECRETO. Anthropic entrou em PÂNICO total e começou uma operação de "APAGAR TUDO".\n\nConcorrentes já BAIXARAM anos de desenvolvimento!'
            },
            3: {
                'copy': 'Por que isso é uma CATÁSTROFE ABSOLUTA?\n\nClaude Code = ferramenta que DOMINA o mercado. MILHÕES de usuários em RISCO TOTAL. Segredos comerciais de BILHÕES nas mãos ERRADAS.\n\nConcorrentes agora podem COPIAR TUDO!'
            },
            4: {
                'copy': 'A FALHA mais BURRA da história da tech!\n\nDesenvolvedores POSTARAM código TOP SECRET em repos PÚBLICOS sem saber. Commits VAZARAM informações que poderiam QUEBRAR a empresa.\n\nGitHub virou um BUFFET GRÁTIS para hackers!'
            },
            5: {
                'copy': 'Anthropic em DESESPERO TOTAL!\n\nDMCA takedowns DESESPERADOS enviados em MASSA. Advogados trabalhando 24/7 em modo PÂNICO. Descobrindo NOVOS vazamentos a cada hora.\n\nMas já pode ser TARDE DEMAIS!'
            },
            6: {
                'copy': 'O mercado de IA pode ENTRAR EM COLAPSO!\n\nConcorrentes podem ROUBAR recursos únicos. Hackers podem EXPLORAR vulnerabilidades. Anthropic pode PERDER TUDO.\n\nInvestidores já estão em PÂNICO!'
            },
            7: {
                'copy': 'URGENTE: Se você baixou, DELETE AGORA!\n\nRISCO REAL de processo MILIONÁRIO. Lei de propriedade intelectual é IMPLACÁVEL. Anthropic está CAÇANDO quem baixou.\n\nAdvogados já estão INVESTIGANDO downloads!'
            },
            8: {
                'copy': 'Como PROTEGER sua empresa deste PESADELO?\n\nREVISE TUDO antes de postar. Use .gitignore como sua VIDA dependesse disso. Auditoria de segurança é QUESTÃO DE SOBREVIVÊNCIA.\n\nUm erro pode QUEBRAR sua startup!'
            },
            9: {
                'copy': 'ALERTE TODA A COMUNIDADE AGORA!\n\nSe você conhece QUALQUER desenvolvedor ou empresa tech, esta informação pode SALVAR a carreira deles!\n\nEste DESASTRE pode acontecer com QUALQUER EMPRESA. COMPARTILHE antes que seja tarde!'
            }
        }

        return content_map.get(slide_index, {})

    def _draw_specific_content(self, draw, current_y: int, slide_content: dict) -> int:
        """Desenha conteúdo como copy fluido com espaçamento estilo Tiago"""

        if 'copy' in slide_content:
            # Quebrar o texto em parágrafos (separar por ".")
            paragraphs = self._break_into_paragraphs(slide_content['copy'])

            for paragraph in paragraphs:
                if paragraph.strip():  # Se não for vazio
                    # Usar largura com margem direita de 40px
                    text_width = 960 - 40  # Margem direita de 40px
                    copy_lines = self._wrap_text(paragraph, text_width, 'body_medium')

                    for line in copy_lines:
                        draw.text((self.margin + 30, current_y), line,
                                 font=self.fonts['body_medium'], fill=self.colors['text_primary'])
                        current_y += 52  # Espaçamento maior para fonte 42px

                    current_y += 36  # Espaço entre parágrafos proporcional

        return current_y

    def _break_into_paragraphs(self, text: str) -> list:
        """Quebra texto respeitando quebras de linha explícitas (\n\n)"""
        # Primeiro quebrar por \n\n (parágrafos explícitos)
        explicit_paragraphs = text.split('\n\n')

        # Limpar espaços e quebras de linha simples
        paragraphs = []
        for paragraph in explicit_paragraphs:
            clean_paragraph = paragraph.replace('\n', ' ').strip()
            if clean_paragraph:
                paragraphs.append(clean_paragraph)

        return paragraphs

    def _draw_cover_content(self, draw, start_y: int, carousel_data: dict) -> int:
        """Conteúdo da capa como copy fluido com espaçamento Tiago"""
        current_y = start_y + 50  # Margem otimizada

        # Copy do slide 1 - usar mesmo método dos outros slides
        slide_content = self._get_slide_content(1)

        if 'copy' in slide_content:
            # Usar o mesmo método de quebra de parágrafos
            paragraphs = self._break_into_paragraphs(slide_content['copy'])

            for paragraph in paragraphs:
                if paragraph.strip():
                    # Usar largura com margem direita de 40px
                    text_width = 960 - 40  # Margem direita de 40px
                    copy_lines = self._wrap_text(paragraph, text_width, 'body_medium')

                    for line in copy_lines:
                        draw.text((self.margin + 30, current_y), line,
                                 font=self.fonts['body_medium'], fill=self.colors['text_primary'])
                        current_y += 52  # Espaçamento igual aos outros slides

                    current_y += 36  # Espaço entre parágrafos

        return current_y

    def _draw_footer_section(self, draw, start_y: int, slide_index: int):
        """Footer personalizado com numeração de 8 slides e fontes específicas"""
        # Linha separadora
        draw.line([(self.margin, start_y + 10), (self.carousel_size[0] - self.margin, start_y + 10)],
                 fill=self.colors['light_gray'], width=2)

        footer_y = start_y + 30

        # Fontes específicas para cada slide
        slide_sources = {
            1: "GitHub, TechCrunch, The Verge",
            2: "GitHub Security, Anthropic Blog",
            3: "Hacker News, Stack Overflow",
            4: "InfoSec Magazine, SANS Institute",
            5: "Legal Tech News, DMCA.com",
            6: "AI Business, VentureBeat",
            7: "Cybersecurity Law, EFF.org",
            8: "DevOps Security, OWASP Foundation",
            9: "[tagline]"  # Referência bíblica para o slide CTA
        }

        # Para o slide 9, usar formato diferente
        if slide_index == 9:
            source_text = slide_sources.get(slide_index, '[tagline]')
        else:
            source_text = f"Fonte: {slide_sources.get(slide_index, 'Pesquisa Própria')}"
        draw.text((self.margin + 20, footer_y), source_text,
                 font=self.fonts['caption'], fill=self.colors['text_secondary'])

        # Slide number à direita
        slide_text = f"{slide_index}/9"  # Agora são 9 slides
        text_width = draw.textlength(slide_text, font=self.fonts['caption'])
        draw.text((self.carousel_size[0] - self.margin - 20 - text_width, footer_y), slide_text,
                 font=self.fonts['caption'], fill=self.colors['text_secondary'])


def main():
    """Gera UM carrossel com 8 slides"""

    print("🚨 Gerando CARROSSEL VAZAMENTO ANTHROPIC com 9 Slides")
    print("📰 Tema: 8 Mil Repositórios do Claude Code Vazados")
    print("📱 Formato: 1080x1440px")
    print("🎯 9 aspectos diferentes do vazamento + CTA")
    print("="*70)

    carousel_data = {
        'id': 'anthropic_vazamento',
        'title': '🚨 VAZAMENTO HISTÓRICO: 8 Mil Repositórios do Claude Code Expostos',
        'approach': 'Carrossel Completo sobre Vazamento Anthropic + CTA'
    }

    print(f"\n📊 ESTRUTURA DO CARROSSEL:")
    print(f"   1️⃣ Slide 1: Escândalo que pode destruir Anthropic")
    print(f"   2️⃣ Slide 2: O pesadelo começou com erro devastador")
    print(f"   3️⃣ Slide 3: Por que isso é catástrofe absoluta")
    print(f"   4️⃣ Slide 4: A falha mais burra da história da tech")
    print(f"   5️⃣ Slide 5: Anthropic em desespero total")
    print(f"   6️⃣ Slide 6: Mercado de IA pode entrar em colapso")
    print(f"   7️⃣ Slide 7: Urgente - se baixou, delete agora")
    print(f"   8️⃣ Slide 8: Como proteger sua empresa")
    print(f"   9️⃣ Slide 9: 📚 CTA COMPARTILHAMENTO (Alerte a comunidade)")

    try:
        generator = SingleCarouselGenerator()
        slides = generator.generate_complete_9_slide_carousel(carousel_data)

        print(f"\n✅ CARROSSEL GERADO COM SUCESSO!")
        print(f"   🎨 {len(slides)} slides criados")
        print(f"   📁 Local: assets/generated_carousels/")

        print(f"\n📄 ARQUIVOS GERADOS:")
        for i, slide_path in enumerate(slides, 1):
            filename = os.path.basename(slide_path)
            file_size = os.path.getsize(slide_path) // 1024
            print(f"   {i}. {filename} ({file_size} KB)")

        print(f"\n🚀 CARROSSEL ÚNICO PRONTO PARA INSTAGRAM!")
        print(f"📈 COBERTURA COMPLETA: Alerta → Explicação → Impacto → Timeline → Soluções → CTA")

    except Exception as e:
        print(f"\n❌ Erro durante geração: {e}")


if __name__ == "__main__":
    main()