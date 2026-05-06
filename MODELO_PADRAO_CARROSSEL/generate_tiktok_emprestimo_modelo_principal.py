#!/usr/bin/env python3
"""
Gera UM ÚNICO carrossel com 9 slides sobre TikTok solicitando aprovação para empréstimos
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
    """Gerador para carrossel único de 9 slides - MODELO PADRÃO"""

    def generate_complete_9_slide_carousel(self, carousel_data: dict) -> list:
        """Gera carrossel completo com 9 slides únicos com imagens reais + CTA"""
        slides = []

        # Baixar todas as imagens primeiro
        print("📥 Preparando imagens para os slides...")
        for slide_index in range(1, 10):  # 9 slides
            self._get_slide_image(slide_index)

        for slide_index in range(1, 10):  # 9 slides
            slide_path = self.generate_carousel_with_images(carousel_data, slide_index)
            slides.append(slide_path)

        return slides

    def generate_carousel_with_images(self, carousel_data: dict, slide_index: int = 1) -> str:
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
                visual_height = self.visual_height
                target_width = self.carousel_size[0]  # Full width
                target_height = visual_height

                # Redimensionar mantendo aspecto e preenchendo área
                img_width, img_height = slide_image.size
                scale_w = target_width / img_width
                scale_h = target_height / img_height
                scale = max(scale_w, scale_h)  # Usar maior escala para preencher

                new_width = int(img_width * scale)
                new_height = int(img_height * scale)

                slide_image = slide_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Centralizar e cortar se necessário
                paste_x = (target_width - new_width) // 2
                paste_y = visual_start_y + (target_height - new_height) // 2

                # Se imagem for maior que área, cortar
                if new_width > target_width or new_height > target_height:
                    crop_x = max(0, (new_width - target_width) // 2)
                    crop_y = max(0, (new_height - target_height) // 2)
                    slide_image = slide_image.crop((
                        crop_x, crop_y,
                        crop_x + min(new_width, target_width),
                        crop_y + min(new_height, target_height)
                    ))
                    paste_x = 0
                    paste_y = visual_start_y

                # Aplicar overlay escuro para melhor contraste
                overlay = Image.new('RGBA', slide_image.size, (0, 0, 0, 80))
                if slide_image.mode != 'RGBA':
                    slide_image = slide_image.convert('RGBA')
                slide_image = Image.alpha_composite(slide_image, overlay)
                slide_image = slide_image.convert('RGB')

                # Colar na área visual
                image.paste(slide_image, (paste_x, paste_y))
                print(f"✅ Imagem FULL-WIDTH integrada no slide {slide_index}")

            except Exception as e:
                print(f"⚠️ Erro ao carregar imagem do slide {slide_index}: {e}")

        # 2. Criar draw DEPOIS de adicionar imagem
        draw = ImageDraw.Draw(image)

        # 3. Adicionar header com foto de perfil
        header_area = (0, 0, self.carousel_size[0], self.header_height)
        self._draw_header_with_profile_photo(draw, header_area)

        # 4. Adicionar conteúdo do slide
        content_area = (0, self.header_height, self.carousel_size[0], self.header_height + self.content_height)
        self._draw_slide_specific_content(draw, content_area, slide_index)

        # 5. Adicionar footer
        footer_area = (0, self.carousel_size[1] - self.footer_height, self.carousel_size[0], self.carousel_size[1])
        self._draw_footer(draw, footer_area)

        # Salvar slide
        filename = f"tiktok_emprestimo_slide_{slide_index:02d}.png"
        file_path = os.path.join(self.output_dir, filename)

        image.save(file_path, 'PNG', quality=95, optimize=True)

        return file_path

    def _get_slide_image(self, slide_index: int) -> str:
        """Retorna caminho da imagem temática TikTok (já baixadas)"""

        thematic_filename = f'tiktok_emprestimo_slide_{slide_index}.jpg'
        thematic_path = os.path.join('assets/slide_images', thematic_filename)

        # Verificar se imagem temática existe
        if os.path.exists(thematic_path):
            print(f"✅ Usando imagem temática: {thematic_filename}")
            return thematic_path

        print(f"⚠️ Imagem temática não encontrada: {thematic_filename}")
        return None

    def _get_slide_content(self, slide_index: int) -> dict:
        """Conteúdo específico para cada slide do carrossel TikTok empréstimos"""

        content_map = {
            1: {
                'copy': 'BOMBA: TikTok quer VIRAR BANCO no Brasil!\n\nAplicativo de DANÇA agora quer EMPRESTAR DINHEIRO! Banco Central recebeu pedido OFICIAL da ByteDance para operar como instituição financeira.\n\nEsta pode ser a MAIOR DISRUPÇÃO do mercado bancário!'
            },
            2: {
                'copy': 'Banco Central CONFIRMA: Pedido OFICIAL protocolado!\n\nTikTok submeteu documentação COMPLETA para oferecer empréstimos, financiamentos e serviços bancários. Reguladores em ALERTA MÁXIMO.\n\nChineses querem DOMINAR nosso sistema financeiro!'
            },
            3: {
                'copy': 'Por que isso é uma REVOLUÇÃO TOTAL?\n\nTikTok = 150 MILHÕES de usuários brasileiros. Acesso a dados financeiros de MEIO PAÍS! Empréstimos via algoritmo de vídeo.\n\nBancos tradicionais em PÂNICO ABSOLUTO!'
            },
            4: {
                'copy': 'A ESTRATÉGIA CHINESA revelada!\n\nEmpresa CHINESA controlando dinheiro de brasileiros. Dados bancários + comportamento de consumo + perfil social TUDO nas mãos da ByteDance.\n\nSoberania financeira em RISCO!'
            },
            5: {
                'copy': 'Mercado TRADICIONAL em DESESPERO!\n\nItaú, Bradesco, Santander vendo MILHÕES de clientes migrando. TikTok oferece crédito INSTANTÂNEO baseado no seu perfil de vídeos.\n\nBancos podem PERDER TUDO!'
            },
            6: {
                'copy': 'Reguladores DIVIDIDOS sobre aprovação!\n\nLobby bancário PRESSIONANDO contra. Governo preocupado com segurança nacional. Usuários ANSIOSOS por crédito mais fácil.\n\nDecisão pode MUDAR o Brasil!'
            },
            7: {
                'copy': 'CUIDADO: Seus dados em RISCO TOTAL!\n\nTikTok JÁ coleta TUDO sobre você. Agora quer saber quanto ganha, gasta e deve! Empresa chinesa com acesso ao seu EXTRATO BANCÁRIO.\n\nPrivacidade ACABOU!'
            },
            8: {
                'copy': 'Como SE PROTEGER desta revolução?\n\nREVISE políticas de privacidade AGORA! Configure dados bancários com máxima segurança. NÃO vincule contas antes da regulamentação.\n\nSua segurança financeira está em jogo!'
            },
            9: {
                'copy': 'COMPARTILHE este ALERTA urgente!\n\nTodo brasileiro precisa saber DESTA REVOLUÇÃO! O futuro dos empréstimos pode mudar PARA SEMPRE!\n\nSua família precisa estar PREPARADA para esta mudança!'
            }
        }

        return content_map.get(slide_index, {})

    def _draw_specific_content(self, draw, current_y: int, slide_content: dict) -> int:
        """Desenha conteúdo como copy fluido com espaçamento estilo Tiago"""

        if 'copy' in slide_content:
            # Quebrar o texto em parágrafos (separar por quebras de linha duplas)
            paragraphs = self._break_into_paragraphs(slide_content['copy'])

            for paragraph in paragraphs:
                if paragraph.strip():  # Se não for vazio
                    # Usar largura com margem direita de 40px
                    text_width = 960 - 40  # Margem direita de 40px
                    copy_lines = self._wrap_text(paragraph, text_width, 'body_medium')

                    for line in copy_lines:
                        draw.text((self.margin + 30, current_y), line,
                                 font=self.fonts['body_medium'], fill=self.colors['text_primary'])
                        current_y += self.fonts_height['body_medium']

                    current_y += 15  # Espaço entre parágrafos

        return current_y

    def _break_into_paragraphs(self, text: str) -> list:
        """Quebra texto em parágrafos usando quebras de linha"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]

    def _wrap_text(self, text: str, max_width: int, font_key: str) -> list:
        """Quebra texto em linhas respeitando largura máxima"""
        font = self.fonts[font_key]
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Palavra muito longa, adicionar mesmo assim
                    lines.append(word)

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _draw_slide_specific_content(self, draw, content_area, slide_index):
        """Desenha o conteúdo específico de cada slide"""

        slide_content = self._get_slide_content(slide_index)

        # Posição inicial do conteúdo (deixar espaço no topo)
        current_y = content_area[1] + 40

        # Desenhar conteúdo
        current_y = self._draw_specific_content(draw, current_y, slide_content)

        return current_y

if __name__ == "__main__":
    print("🚨 Gerando CARROSSEL TIKTOK EMPRÉSTIMOS com 9 Slides")
    print("📰 Tema: TikTok solicita aprovação para empréstimos no Brasil")
    print("📱 Formato: 1080x1440px")
    print("🎯 9 aspectos da disrupção financeira + CTA")
    print("="*70)

    carousel_data = {
        'id': 'tiktok_emprestimos',
        'title': '🚨 BOMBA: TikTok Quer Virar BANCO no Brasil!',
        'approach': 'Carrossel Completo sobre TikTok Empréstimos + CTA'
    }

    print(f"\n📊 ESTRUTURA DO CARROSSEL:")
    print(f"   1️⃣ Slide 1: TikTok quer virar banco no Brasil")
    print(f"   2️⃣ Slide 2: Banco Central confirma pedido oficial")
    print(f"   3️⃣ Slide 3: Por que é revolução total")
    print(f"   4️⃣ Slide 4: Estratégia chinesa revelada")
    print(f"   5️⃣ Slide 5: Mercado tradicional em desespero")
    print(f"   6️⃣ Slide 6: Reguladores divididos")
    print(f"   7️⃣ Slide 7: Cuidado - dados em risco")
    print(f"   8️⃣ Slide 8: Como se proteger")
    print(f"   9️⃣ Slide 9: 📚 CTA COMPARTILHAMENTO")

    # Gerar carrossel
    generator = SingleCarouselGenerator()
    slides = generator.generate_complete_9_slide_carousel(carousel_data)

    print(f"\n✅ CARROSSEL GERADO COM SUCESSO!")
    print(f"   🎨 {len(slides)} slides criados")
    print(f"   📁 Local: assets/generated_carousels/")

    # Listar arquivos
    print(f"\n📄 ARQUIVOS GERADOS:")
    for i, slide_path in enumerate(slides, 1):
        if os.path.exists(slide_path):
            filename = os.path.basename(slide_path)
            size = os.path.getsize(slide_path)
            size_kb = size // 1024
            print(f"   {i}. {filename} ({size_kb} KB)")

    print(f"\n🚀 CARROSSEL ÚNICO PRONTO PARA INSTAGRAM!")
    print(f"📈 COBERTURA COMPLETA: Disrupção → Regulação → Riscos → Proteção → CTA")