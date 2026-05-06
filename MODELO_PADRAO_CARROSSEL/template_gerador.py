#!/usr/bin/env python3
"""
TEMPLATE GERADOR DE CARROSSEL - MODELO PADRÃO CalebeDigital

INSTRUÇÕES:
1. Copie este arquivo como: generate_[SEU_TEMA]_modelo_principal.py
2. Substitua [TEMA] pelo seu tema específico
3. Modifique apenas as seções marcadas com "# PERSONALIZAR AQUI"
4. NUNCA altere o layout, design ou estrutura base

EXEMPLO: generate_bitcoin_modelo_principal.py
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
        # PERSONALIZAR AQUI: Nome dos arquivos
        filename = f"[TEMA]_slide_{slide_index:02d}.png"  # ← SUBSTITUA [TEMA]
        file_path = os.path.join(self.output_dir, filename)

        image.save(file_path, 'PNG', quality=95, optimize=True)

        return file_path

    def _get_slide_image(self, slide_index: int) -> str:
        """Retorna caminho da imagem temática (já baixadas)"""

        # PERSONALIZAR AQUI: Nome das imagens temáticas
        thematic_filename = f'[TEMA]_slide_{slide_index}.jpg'  # ← SUBSTITUA [TEMA]
        thematic_path = os.path.join('assets/slide_images', thematic_filename)

        # Verificar se imagem temática existe
        if os.path.exists(thematic_path):
            print(f"✅ Usando imagem temática: {thematic_filename}")
            return thematic_path

        print(f"⚠️ Imagem temática não encontrada: {thematic_filename}")

        # PERSONALIZAR AQUI: URLs de fallback se imagens temáticas não existirem
        fallback_urls = {
            1: "https://images.unsplash.com/photo-XXXXX?w=800&h=600&fit=crop",  # ← SUBSTITUA
            2: "https://images.unsplash.com/photo-XXXXX?w=800&h=600&fit=crop",  # ← SUBSTITUA
            # ... adicione todas as 9 URLs
        }

        return None  # Implementar download de fallback se necessário

    def _get_slide_content(self, slide_index: int) -> dict:
        """Conteúdo específico para cada slide do carrossel único"""

        # PERSONALIZAR AQUI: Todo o conteúdo do seu tema
        content_map = {
            1: {
                'copy': '[TÍTULO IMPACTANTE DO SEU TEMA]!\n\n[Descrição que gera curiosidade sobre o problema/situação]\n\n[Call-to-action para continuar lendo]\n\n>>> Segue o fio...'
            },
            2: {
                'copy': '[SEGUNDO ASPECTO DO TEMA]\n\n[Desenvolvimento da situação]\n\n[Dados ou fatos impressionantes]'
            },
            3: {
                'copy': '[TERCEIRO ASPECTO]\n\n[Por que isso é importante]\n\n[Impacto na área/mercado]'
            },
            4: {
                'copy': '[QUARTO ASPECTO]\n\n[Detalhes técnicos ou análise]\n\n[Consequências práticas]'
            },
            5: {
                'copy': '[QUINTO ASPECTO]\n\n[Aprofundamento do tema]\n\n[Exemplos ou casos]'
            },
            6: {
                'copy': '[SEXTO ASPECTO]\n\n[Impactos futuros ou tendências]\n\n[O que esperar]'
            },
            7: {
                'copy': '[SÉTIMO ASPECTO]\n\n[Soluções ou cuidados]\n\n[Como lidar com a situação]'
            },
            8: {
                'copy': '[OITAVO ASPECTO]\n\n[Dicas práticas ou proteções]\n\n[Ações recomendadas]'
            },
            9: {
                'copy': '[CTA FINAL PARA COMPARTILHAMENTO]\n\n[Incentivar share para alertar outros]\n\n[Importância de espalhar a informação]'
            }
        }

        return content_map.get(slide_index, {})

    # ... resto dos métodos permanecem inalterados (não mexer)

if __name__ == "__main__":
    # PERSONALIZAR AQUI: Informações do seu carrossel
    print("🚨 Gerando CARROSSEL [SEU TEMA] com 9 Slides")  # ← PERSONALIZAR
    print("📰 Tema: [Descrição do seu tema]")  # ← PERSONALIZAR
    print("📱 Formato: 1080x1440px")
    print("🎯 9 aspectos diferentes do [tema] + CTA")  # ← PERSONALIZAR
    print("="*70)

    # PERSONALIZAR AQUI: Dados do carrossel
    carousel_data = {
        'id': '[tema]_carousel',  # ← PERSONALIZAR
        'title': '🚨 [TÍTULO DO SEU CARROSSEL]',  # ← PERSONALIZAR
        'approach': 'Carrossel Completo sobre [SEU TEMA] + CTA'  # ← PERSONALIZAR
    }

    print(f"\n📊 ESTRUTURA DO CARROSSEL:")
    # PERSONALIZAR AQUI: Títulos dos slides
    print(f"   1️⃣ Slide 1: [Título slide 1]")  # ← PERSONALIZAR
    print(f"   2️⃣ Slide 2: [Título slide 2]")  # ← PERSONALIZAR
    print(f"   3️⃣ Slide 3: [Título slide 3]")  # ← PERSONALIZAR
    print(f"   4️⃣ Slide 4: [Título slide 4]")  # ← PERSONALIZAR
    print(f"   5️⃣ Slide 5: [Título slide 5]")  # ← PERSONALIZAR
    print(f"   6️⃣ Slide 6: [Título slide 6]")  # ← PERSONALIZAR
    print(f"   7️⃣ Slide 7: [Título slide 7]")  # ← PERSONALIZAR
    print(f"   8️⃣ Slide 8: [Título slide 8]")  # ← PERSONALIZAR
    print(f"   9️⃣ Slide 9: 📚 CTA COMPARTILHAMENTO")  # ← Sempre igual

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
    print(f"📈 COBERTURA COMPLETA: [Resumo da cobertura do tema]")  # ← PERSONALIZAR