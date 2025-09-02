from django.db import models
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import (
    CharBlock, TextBlock, RichTextBlock, URLBlock, 
    StructBlock, ListBlock, BooleanBlock, IntegerBlock, 
    DateBlock, EmailBlock
)
import uuid

from .form import BASE_FORM_FIELD_BLOCKS
# Cores principais da paleta
# Cores principais para inovação - sem duplicatas e com valores hexadecimais válidos
BRAND_INOVACAO_CHOICES = [
    ('enap-green', 'Verde ENAP'),
    ('enap-link', 'Verde Link ENAP'), 
    ('gnova-purple', 'Roxo Gnova'),
    ('gnova-light', 'Roxo Claro Gnova'),
    ('blue', 'Azul'),
    ('green', 'Verde'),
    ('red', 'Vermelho'),
    ('orange', 'Laranja'),
    ('purple', 'Roxo'),
    ('indigo', 'Índigo'),
    ('emerald', 'Esmeralda'),
    ('#FFFFFF', 'Branco (#FFFFFF)'),
    ('#132929', 'Verde Musgo Escuro'),
    ('#3A8A9C', 'Azul Petróleo'),
    ('#25552A', 'Verde Floresta Escuro'),
    ('#818C27', 'Verde Oliva'),
    ('#FF7A1B', 'Laranja Vibrante'),
    ('#FFEB31', 'Amarelo Canário'),
    ('#FFF0D9', 'Creme Suave'),
    ('#DB8C3F', 'Dourado Queimado'),
    ('#990005', 'Vermelho Bordô'),
    ('#EA1821', 'Vermelho Cereja'),
    ('#BAC946', 'Verdinho'),
]

# Cores para textos - removendo duplicatas e corrigindo valores
BRAND_TEXTS_CHOICES = [
    ('enap-green', 'Verde ENAP'),
    ('#FFF0D9', 'Creme Suave'),  # Corrigido de 'bg-white', '#fbebd8'
    ('enap-link', 'Verde Link ENAP'), 
    ('gnova-purple', 'Roxo Gnova'),
    ('gnova-light', 'Roxo Claro Gnova'),
    ('blue', 'Azul'),
    ('green', 'Verde'),
    ('red', 'Vermelho'),
    ('orange', 'Laranja'),
    ('purple', 'Roxo'),
    ('indigo', 'Índigo'),
    ('emerald', 'Esmeralda'),
    ('#FFFFFF', 'Branco (#FFFFFF)'),
    ('#132929', 'Verde Musgo Escuro'),
    ('#00777D', 'Enap'),
    ('#58606E', 'Enap Cinza'),
    ('#AFF0ED', 'Enap Azul'),
    ('#25552A', 'Verde Floresta Escuro'),
    ('#818C27', 'Verde Oliva'),
    ('#DB8C3F', 'Dourado Queimado'),
    ('#990005', 'Vermelho Bordô'),
    ('#000000', 'Preto'),
    ('#2F2F2F', 'Cinza Escuro'),
    ('#4A4A4A', 'Cinza Médio'),
    ('#383674', 'Roxo ENAP'),
    ('#BAC946', 'Verdinho'),
]

# Cores para backgrounds - removendo duplicatas
BRAND_BG_CHOICES = [
    ('#FFFFFF', 'Branco (#FFFFFF)'),
    ('#F8F9FA', 'Cinza Claro (#F8F9FA)'),
    ('#000000', 'Preto (#000000)'),
    ('enap-green', 'Verde ENAP'),
    ('enap-link', 'Verde Link ENAP'), 
    ('gnova-purple', 'Roxo Gnova'),
    ('gnova-light', 'Roxo Claro Gnova'),
    ('blue', 'Azul'),
    ('green', 'Verde'),
    ('red', 'Vermelho'),
    ('orange', 'Laranja'),
    ('purple', 'Roxo'),
    ('indigo', 'Índigo'),
    ('emerald', 'Esmeralda'),
    ('#132929', 'Verde Musgo Escuro'),
    ('#F5F7FA', 'Azul Enap'),
    ('#FCFCFC', 'Cinza Enap'),
    ('#3A8A9C', 'Azul Petróleo'),
    ('#25552A', 'Verde Floresta Escuro'),
    ('#818C27', 'Verde Oliva'),
    ('#FF7A1B', 'Laranja Vibrante'),
    ('#FFEB31', 'Amarelo Canário'),
    ('#FFF0D9', 'Creme Suave'),
    ('#DB8C3F', 'Dourado Queimado'),
    ('#990005', 'Vermelho Bordô'),
    ('#EA1821', 'Vermelho Cereja'),
    ('#F8F9FA', 'Cinza Muito Claro'),
    ('#BAC946', 'Verdinho'),
]

# Cores para botões e elementos interativos
BRAND_BUTTON_CHOICES = [
    ('enap-green', 'Verde ENAP'),
    ('enap-link', 'Verde Link ENAP'), 
    ('gnova-purple', 'Roxo Gnova'),
    ('gnova-light', 'Roxo Claro Gnova'),
    ('blue', 'Azul'),
    ('green', 'Verde'),
    ('red', 'Vermelho'),
    ('orange', 'Laranja'),
    ('purple', 'Roxo'),
    ('indigo', 'Índigo'),
    ('emerald', 'Esmeralda'),
    ('#FFFFFF', 'Branco (#FFFFFF)'),
    ('#FF7A1B', 'Laranja Vibrante'),
    ('#FFEB31', 'Amarelo Canário'),
    ('#3A8A9C', 'Azul Petróleo'),
    ('#818C27', 'Verde Oliva'),
    ('#DB8C3F', 'Dourado Queimado'),
    ('#EA1821', 'Vermelho Cereja'),
    ('#25552A', 'Verde Floresta Escuro'),
    ('#BAC946', 'Verdinho'),
]

# Cores para hover dos botões
BRAND_HOVER_CHOICES = [
    ('enap-green', 'Verde ENAP'),
    ('enap-link', 'Verde Link ENAP'), 
    ('gnova-purple', 'Roxo Gnova'),
    ('gnova-light', 'Roxo Claro Gnova'),
    ('blue', 'Azul'),
    ('green', 'Verde'),
    ('red', 'Vermelho'),
    ('orange', 'Laranja'),
    ('purple', 'Roxo'),
    ('indigo', 'Índigo'),
    ('emerald', 'Esmeralda'),
    ('#FFFFFF', 'Branco (#FFFFFF)'),
    ('#E6690F', 'Laranja Escuro'),
    ('#E6D220', 'Amarelo Escuro'),
    ('#2E7A8A', 'Azul Petróleo Escuro'),
    ('#6F7B22', 'Verde Oliva Escuro'),
    ('#C27B35', 'Dourado Escuro'),
    ('#D1141B', 'Vermelho Cereja Escuro'),
    ('#1E4420', 'Verde Floresta Muito Escuro'),
    ('#BAC946', 'Verdinho'),
]



# =============================================================================
# BLOCKS REUTILIZÁVEIS DA SEMANA DE INOVAÇÃO
# =============================================================================

class ImageBlock(StructBlock):
    """Block simples de imagem"""
    imagem = ImageChooserBlock(label="Imagem")
    alt_text = CharBlock(label="Texto Alternativo", required=False)

    class Meta:
        template = 'enap_designsystem/semana_inovacao/image_block.html'
        icon = 'image'
        label = 'Imagem'


class ParticipanteBlock(StructBlock):
    """Block de participante individual"""
    nome = CharBlock(label="Nome Completo")
    cargo = CharBlock(label="Cargo/Função", required=False)
    empresa = CharBlock(label="Empresa/Organização", required=False)
    foto = ImageChooserBlock(label="Foto do Participante", required=False)
    descricao = RichTextBlock(label="Biografia", required=False)
    
    # Redes sociais
    link_linkedin = URLBlock(label="LinkedIn", required=False, default="link.com")
    link_instagram = URLBlock(label="Instagram", required=False,  default="link.com")
    link_twitter = URLBlock(label="Twitter/X", required=False,  default="link.com")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/participantes.html'
        icon = 'user'
        label = 'Participante'


class StatBlock(StructBlock):
    """Block para estatísticas/números"""
    valor = CharBlock(label="Valor", help_text="Ex: 129, 500+", required=False, default="500+")
    descricao = CharBlock(label="Descrição", help_text="Ex: Atividades, Participantes")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/stat_block.html'
        icon = 'plus'
        label = 'Estatística'


class GaleriaFotoBlock(StructBlock):
    """Block para foto da galeria"""
    imagem = ImageChooserBlock(label="Imagem", required=False)
    descricao = CharBlock(label="Descrição", required=False)

    class Meta:
        template = 'enap_designsystem/semana_inovacao/galeria_foto_block.html'
        icon = 'image'
        label = 'Foto da Galeria'


class GaleriaBlock(blocks.StructBlock):
    """Bloco de galeria com 5 fotos"""
    titulo = blocks.CharBlock(
        required=True,
        default="Nossa Galeria",
        help_text="Título da galeria"
    )
    
    descricao = blocks.TextBlock(
        required=False,
        help_text="Descrição curta da galeria",
        max_length=200
    )
    
    # Definição simples para as 5 fotos
    foto_grande = blocks.StructBlock([
        ('imagem', ImageChooserBlock(required=True, label="Foto Grande")),
        ('descricao', blocks.CharBlock(required=False, label="Descrição", max_length=100)),
    ], label="Foto Grande (Esquerda)")
    
    foto_1 = blocks.StructBlock([
        ('imagem', ImageChooserBlock(required=True, label="Foto 1")),
        ('descricao', blocks.CharBlock(required=False, label="Descrição", max_length=100)),
    ], label="Foto 1 (Superior Direita)")
    
    foto_2 = blocks.StructBlock([
        ('imagem', ImageChooserBlock(required=True, label="Foto 2")),
        ('descricao', blocks.CharBlock(required=False, label="Descrição", max_length=100)),
    ], label="Foto 2 (Superior Direita)")
    
    foto_3 = blocks.StructBlock([
        ('imagem', ImageChooserBlock(required=True, label="Foto 3")),
        ('descricao', blocks.CharBlock(required=False, label="Descrição", max_length=100)),
    ], label="Foto 3 (Inferior Direita)")
    
    foto_4 = blocks.StructBlock([
        ('imagem', ImageChooserBlock(required=True, label="Foto 4")),
        ('descricao', blocks.CharBlock(required=False, label="Descrição", max_length=100)),
    ], label="Foto 4 (Inferior Direita)")
    
    ver_mais_url = blocks.URLBlock(
        required=False,
        label="Link 'Ver Mais'",
        help_text="URL para página com mais fotos"
    )
    
    quantidade_fotos = blocks.IntegerBlock(
        required=False,
        label="Quantidade de fotos adicionais",
        help_text="Número de fotos adicionais na galeria completa"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/secao_galeria_block.html'
        icon = 'image'
        label = 'Section Galeria de Fotos'


class FAQItemBlock(StructBlock):
    """Item individual de FAQ"""
    question = CharBlock(label="Pergunta")
    answer = RichTextBlock(label="Resposta")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/faq_item_block.html'
        icon = 'help'
        label = 'Item FAQ'


class FAQTabBlock(StructBlock):
    """Aba de FAQ com múltiplos itens"""
    tab_name = CharBlock(label="Nome da Aba")
    faq_items = ListBlock(FAQItemBlock(), label="Itens do FAQ")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/faq_tab_block.html'
        icon = 'folder-open-1'
        label = 'Aba FAQ'


class AtividadeBlock(StructBlock):
    """Block para atividade da programação"""
    horario_inicio = CharBlock(label="Horário de Início", help_text="Ex: 09:00")
    horario_fim = CharBlock(label="Horário de Fim", help_text="Ex: 10:00")
    titulo = CharBlock(label="Título da Atividade")
    descricao = TextBlock(label="Descrição", required=False)
    
    # Tipo de atividade
    TIPO_CHOICES = [
        ('online', 'Online'),
        ('presencial', 'Presencial'),
    ]
    tipo = CharBlock(label="Tipo", help_text="Digite: online ou presencial")
    
    # Local (para presencial) ou tag (para online)
    local_tag = CharBlock(label="Local/Tag", help_text="Ex: Sala 106, On-Line")
    
    # Data da atividade
    data = DateBlock(label="Data da Atividade")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/atividade_block.html'
        icon = 'time'
        label = 'Atividade'


class HospitalityCardBlock(StructBlock):
    """Card de hospitalidade/serviços"""
    title = CharBlock(label="Título")
    text = RichTextBlock(label="Texto")
    image = ImageChooserBlock(label="Imagem")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/hospitality_card_block.html'
        icon = 'home'
        label = 'Card de Hospitalidade'


class VideoBlock(StructBlock):
    """Block para vídeo"""
    titulo = CharBlock(label="Título do Vídeo", required=False, default="Vídeo")
    imagem_bg = ImageChooserBlock(label="Imagem", required=False)
    video_url = URLBlock(label="URL do Vídeo", default="https://www.youtube.com/watch?v=example", required=False)
    cor_badge = blocks.ChoiceBlock(
        label="Cor do Badge",
        choices=BRAND_BG_CHOICES,
        default="#2c3e50",
        help_text="Cor de fundo do badge do título",
        required=False
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/video_block.html'
        icon = 'media'
        label = 'Vídeo SI'


class CertificadoBlock(StructBlock):
    """Block para seção de certificado"""
    titulo = CharBlock(label="Título", default="Certificado de Participação", required=False),
    texto = RichTextBlock(label="Texto", default="Baixe seu certificado de participação na Semana de Inovação.", required=False)
    texto_botao = CharBlock(label="Texto do Botão", default="Baixar certificado", required=False)
    imagem = ImageChooserBlock(label="Imagem do Certificado", required=False)

    class Meta:
        template = 'enap_designsystem/semana_inovacao/certificado_block.html'
        icon = 'doc-full'
        label = 'Certificado'


class NewsletterBlock(blocks.StructBlock):
    """Block para newsletter"""
    titulo = blocks.CharBlock(label="Título", default="ASSINE NOSSA NEWSLETTER", required=False)
    texto = blocks.RichTextBlock(label="Texto", default="Fique por dentro das últimas novidades da Semana de Inovação.", required=False)
    texto_secundario = blocks.RichTextBlock(label="Texto Secundário", default="Inscreva-se da nossa newsletter e receba conteúdos em primeira mão.", required=False)
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#FFF0D9',
        label="Cor de Fundo",
        help_text="Selecione a cor de fundo da seção"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#132929',
        label="Cor do Título",
        help_text="Selecione a cor do título"
    )
    
    cor_texto = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#132929',
        label="Cor do Texto",
        help_text="Selecione a cor do texto"
    )
    
    cor_botao = blocks.ChoiceBlock(
        choices=BRAND_BUTTON_CHOICES,
        default='#990005',
        label="Cor do Botão",
        help_text="Selecione a cor do botão de inscrição"
    )
    
    cor_texto_botao = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#FFFFFF',
        label="Cor do Texto do Botão",
        help_text="Selecione a cor do texto do botão"
    )
    
    imagem = ImageChooserBlock(label="Imagem", required=False, help_text="Imagem decorativa para a seção")
    
    texto_botao = blocks.CharBlock(label="Texto do Botão", default="INSCREVA-SE", required=False)
    
    form_action = blocks.URLBlock(
        label="URL do Formulário", 
        required=False, 
        help_text="URL para onde o formulário será enviado (deixe em branco para usar o padrão)"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/newsletter_block.html'
        icon = 'mail'
        label = 'Newsletter Imagem e campo email'


class ContatoBlock(StructBlock):
    """Block para seção de contato"""
    titulo = CharBlock(label="Título", default="FALE CONOSCO")
    texto = RichTextBlock(label="Texto")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/contato_block.html'
        icon = 'mail'
        label = 'Contato'


class FooterBlock(StructBlock):
    """Block para footer"""
    logo = ImageChooserBlock(label="Logo")
    texto_evento = RichTextBlock(label="Texto do Evento")
    logo_hero_link = URLBlock(label="Link do Logo", required=False)

    class Meta:
        template = 'enap_designsystem/semana_inovacao/footer_block.html'
        icon = 'list-ul'
        label = 'Footer'


# =============================================================================
# SEMANA DE INOVAÇÃO - BLOCOS CUSTOMIZADOS
# =============================================================================

class BannerConcurso(blocks.StructBlock):
    """
    StructBlock para criar um banner de concurso
    """
    
    titulo = blocks.CharBlock(
        required=False,
        max_length=100,
        help_text="Título principal do banner"
    )
    
    subtitulo = blocks.CharBlock(
        required=False,
        max_length=200,
        help_text="Subtítulo ou descrição do banner"
    )
    
    imagem_fundo = ImageChooserBlock(
        required=False,
        help_text="Imagem de fundo do banner"
    )
    
    imagem_principal = ImageChooserBlock(
        required=False,
        help_text="Imagem principal do banner"
    )
    
    imagem_secundaria = ImageChooserBlock(
        required=False,
        help_text="Segunda imagem do banner"
    )
    
    link = blocks.URLBlock(
        required=False,
        help_text="URL para onde o banner deve direcionar (opcional)"
    )
    
    texto_link = blocks.CharBlock(
        required=False,
        max_length=50,
        help_text="Texto do botão/link (ex: 'Saiba mais')"
    )
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#FFF0D9',
        help_text="Cor de fundo do conteúdo do banner"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#132929',
        help_text="Cor do título"
    )
    
    cor_subtitulo = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#25552A',
        help_text="Cor do subtítulo"
    )
    
    cor_botao = blocks.ChoiceBlock(
        choices=BRAND_BUTTON_CHOICES,
        default='#FF7A1B',
        help_text="Cor do botão"
    )

    altura_banner = blocks.ChoiceBlock(
        choices=[
            ('50vh', 'Altura Reduzida (50vh)'),
            ('70vh', 'Altura Padrão (70vh)'),
        ],
        default='70vh',
        help_text="Escolha a altura do banner"
    )
    
    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_banner.html'
        icon = 'image'
        label = 'Banner de Concurso'
        help_text = 'Banner personalizado para concursos'


class MaterialApioBlock(blocks.StructBlock):
    """Bloco para Material de Apoio com layout personalizado"""
    
    # Configurações gerais
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#132929',
        help_text="Cor de fundo da seção"
    )

    cor_texto_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do título",
        required=False
    )
    
    # Conteúdo principal (lado esquerdo)
    titulo = blocks.CharBlock(
        max_length=100,
        help_text="Título principal da seção"
    )
    texto = blocks.TextBlock(
        help_text="Texto descritivo da seção"
    )
    email_contato = blocks.EmailBlock(
        required=False,
        help_text="Email de contato (opcional)"
    )
    
    cor_texto = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do texto",
        required=False
    )
    
    # Card com imagem (lado direito)
    imagem_card = ImageChooserBlock(
        help_text="Imagem do card lateral"
    )
    link_card = blocks.URLBlock(
        help_text="Link para onde a imagem deve direcionar"
    )
    alt_imagem = blocks.CharBlock(
        max_length=100,
        default="Imagem do material de apoio",
        help_text="Texto alternativo da imagem"
    )
    
    # StreamField de Botões
    botoes = blocks.StreamBlock([
        ('botao', blocks.StructBlock([
            ('texto', blocks.CharBlock(
                max_length=100,
                help_text="Texto do botão"
            )),
            ('link', blocks.URLBlock(
                help_text="URL para onde o botão deve direcionar"
            )),
            ('cor_fundo', blocks.ChoiceBlock(
                choices=BRAND_BUTTON_CHOICES,
                default='#FFEB31',
                help_text="Cor de fundo do botão"
            )),
            ('cor_hover', blocks.ChoiceBlock(
                choices=BRAND_HOVER_CHOICES,
                default='#E6D220',
                help_text="Cor do botão ao passar o mouse"
            )),
            ('cor_texto', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#132929',
                help_text="Cor do texto do botão"
            )),
        ], icon='link', label='Botão')),
    ], 
    min_num=1,
    help_text="Adicione quantos botões quiser"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_material_apoio.html'
        icon = 'doc-full'
        label = 'Material de Apoio'


class SecaoPatrocinadoresBlock(blocks.StructBlock):
    
    # Imagem de background
    imagem_background = ImageChooserBlock(
        help_text="Imagem de fundo da seção",
        required=False
    )
    
    # Título e cor
    titulo = blocks.CharBlock(
        max_length=200,
        help_text="Título principal da seção",
        default="Patrocinadores do Evento",
        required=False
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do título",
        required=False
    )
    
    # Imagem em destaque
    imagem_destaque = ImageChooserBlock(
        help_text="Imagem principal em destaque",
        required=False
    )
    
    # StreamField de fotos
    galeria_fotos = blocks.StreamBlock([
        ('foto', blocks.StructBlock([
            ('imagem', ImageChooserBlock(
                help_text="Imagem da galeria"
            )),
        ], icon='image', label='Foto')),
    ], 
    min_num=0,
    help_text="Adicione quantas fotos quiser na galeria",
    required=False
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_patrocinadores.html'
        icon = 'image'
        label = 'Seção com Destaque - Patrocinadores'


class SecaoApresentacaoBlock(blocks.StructBlock):
    """Bloco para seção de apresentação com título, subtítulo, foto e rich text"""
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#FFF0D9',
        help_text="Cor de fundo da seção"
    )
    
    posicao_imagem = blocks.ChoiceBlock(
        choices=[
            ('direita', 'Imagem à Direita'),
            ('esquerda', 'Imagem à Esquerda'),
        ],
        default='direita',
        help_text="Posição da imagem em relação ao texto"
    )
    
    # Título principal
    titulo = blocks.CharBlock(
        max_length=200,
        help_text="Título principal da seção"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#818C27',
        help_text="Cor do título principal",
        required=False
    )
    
    subtitulo = blocks.RichTextBlock(
    required=False,
    help_text="Subtítulo da seção (opcional)",
    features=[
        'bold', 'italic', 'link', 'ul', 'ol', 
        'h3', 'h4', 'hr', 'blockquote'
    ]
    )
    
    cor_subtitulo = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#132929',
        help_text="Cor do subtítulo"
    )
    
    # Foto circular
    imagem_circular = ImageChooserBlock(
        help_text="Imagem que aparecerá em formato circular"
    )
    
    alt_imagem = blocks.CharBlock(
        max_length=100,
        default="Imagem ilustrativa",
        help_text="Texto alternativo da imagem"
    )
    
    # Rich Text para conteúdo
    conteudo = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul', 'hr', 'document-link'],
        help_text="Conteúdo principal em rich text",
        required=False
    )
    
    cor_texto = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#25552A',
        help_text="Cor do texto do conteúdo"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_secao_apresentacao.html'
        icon = 'doc-full'
        label = 'Seção Apresentação'


class SecaoCategoriasBlock(blocks.StructBlock):
    """Bloco para seção com imagem no topo e duas colunas de categorias"""
    
    # Configurações de fundo
    imagem_fundo = ImageChooserBlock(
        required=False,
        help_text="Imagem de fundo da seção (opcional)"
    )
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#FFFFFF',
        help_text="Cor de fundo da seção"
    )
    
    # Imagem no topo
    imagem_topo = ImageChooserBlock(
        help_text="Imagem que ocupará toda a largura no topo"
    )
    
    alt_imagem = blocks.CharBlock(
        max_length=100,
        default="Imagem ilustrativa",
        help_text="Texto alternativo da imagem"
    )
    
    # Primeira coluna
    titulo_coluna_1 = blocks.CharBlock(
        max_length=200,
        help_text="Título da primeira coluna"
    )
    
    cor_titulo_1 = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#132929',
        help_text="Cor do título da primeira coluna",
        required=False
    )
    
    conteudo_coluna_1 = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul', 'hr'],
        help_text="Conteúdo da primeira coluna"
    )
    
    cor_texto_1 = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#25552A',
        help_text="Cor do texto da primeira coluna"
    )
    
    # Segunda coluna
    titulo_coluna_2 = blocks.CharBlock(
        max_length=200,
        help_text="Título da segunda coluna"
    )
    
    cor_titulo_2 = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#132929',
        help_text="Cor do título da segunda coluna",
        required=False
    )
    
    conteudo_coluna_2 = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul', 'hr'],
        help_text="Conteúdo da segunda coluna"
    )
    
    cor_texto_2 = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#25552A',
        help_text="Cor do texto da segunda coluna"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_secao_categorias.html'
        icon = 'doc-full-inverse'
        label = 'Seção Categorias'


class CronogramaBlock(blocks.StructBlock):
    """Bloco para cronograma com steps flexíveis"""
    
    # Configurações de fundo
    imagem_fundo = ImageChooserBlock(
        required=False,
        help_text="Imagem de fundo da seção (opcional)"
    )

    imagem_ladotexto = ImageChooserBlock(
        required=False,
        help_text="Imagem ao lado do texto"
    )
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#FFF0D9',
        help_text="Cor de fundo da seção"
    )
    
    # Título da seção
    titulo = blocks.CharBlock(
        max_length=200,
        help_text="Título do cronograma (ex: De olho no cronograma)"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#132929',
        help_text="Cor do título",
        required=False
    )
    
    # StreamField para os steps
    steps = blocks.StreamBlock([
        ('step', blocks.StructBlock([
            ('data', blocks.CharBlock(
                max_length=50,
                help_text="Data do step (ex: 05 MAI)"
            )),
            ('cor_data', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#132929',
                help_text="Cor do texto da data"
            )),
            ('cor_circulo', blocks.ChoiceBlock(
                choices=BRAND_INOVACAO_CHOICES,
                default='#818C27',
                help_text="Cor do círculo",
                required=False
            )),
            ('descricao', blocks.TextBlock(
                max_length=300,
                help_text="Descrição do step"
            )),
            ('cor_descricao', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#25552A',
                help_text="Cor do texto da descrição"
            )),
        ], icon='date', label='Step do Cronograma')),
    ], 
    min_num=2,
    max_num=10,
    help_text="Adicione entre 2 e 10 steps no cronograma"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_cronograma.html'
        icon = 'time'
        label = 'Steps'


class SecaoPremiosBlock(blocks.StructBlock):
    """Bloco para seção de prêmios com imagem de fundo e lista de tópicos"""
    
    # Configurações de fundo
    imagem_fundo = ImageChooserBlock(
        required=False,
        help_text="Imagem de fundo da seção (opcional)"
    )

    imagem_grande_lateral = ImageChooserBlock(
        required=False,
        help_text="Imagem de fundo da seção (opcional)"
    )
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#FFFFFF',
        help_text="Cor de fundo da seção"
    )
    
    # Título da seção
    titulo = blocks.CharBlock(
        max_length=200,
        help_text="Título da seção (ex: Quais são os prêmios?)"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#132929',
        help_text="Cor do título",
        required=False
    )
    
    cor_topicos = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#25552A',
        help_text="Cor do texto dos tópicos"
    )
    
    topicos = blocks.StreamBlock([
        ('topico', blocks.TextBlock(
            max_length=500,
            help_text="Texto do tópico/prêmio"
        )),
    ], 
    min_num=1,
    max_num=15,
    help_text="Adicione os tópicos/prêmios (até 15 itens)"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_secao_premios.html'
        icon = 'trophy'
        label = 'Seção Prêmios'

class SecaoFAQBlock(blocks.StructBlock):
    """Bloco para seção de FAQ com accordion"""
    
    # Configurações de fundo
    imagem_fundo = ImageChooserBlock(
        required=False,
        help_text="Imagem de fundo da seção (opcional)"
    )
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#FFF0D9',
        help_text="Cor de fundo da seção"
    )
    
    # Título da seção
    titulo = blocks.CharBlock(
        max_length=200,
        help_text="Título da seção (ex: Perguntas Frequentes)"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#132929',
        help_text="Cor do título",
        required=False
    )
    
    # Cor das perguntas
    cor_perguntas = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#132929',
        help_text="Cor do texto das perguntas"
    )
    
    # Cor das respostas
    cor_respostas = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#25552A',
        help_text="Cor do texto das respostas"
    )
    
    # Cor do accordion
    cor_accordion = blocks.ChoiceBlock(
        choices=BRAND_BUTTON_CHOICES,
        default='#FF7A1B',
        help_text="Cor de destaque do accordion"
    )
    
    # StreamField para as FAQs
    faqs = blocks.StreamBlock([
        ('faq', blocks.StructBlock([
            ('pergunta', blocks.CharBlock(
                max_length=300,
                help_text="Pergunta do FAQ"
            )),
            ('resposta', blocks.RichTextBlock(
                features=['bold', 'italic', 'link', 'ol', 'ul', 'table'],
                help_text="Resposta da pergunta (suporte a tabelas incluído)"
            )),
        ], icon='help', label='FAQ')),
    ], 
    min_num=1,
    max_num=20,
    help_text="Adicione as perguntas e respostas (até 20 itens)"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_secao_faq.html'
        icon = 'help'
        label = 'Seção FAQ'



class SecaoContatoBlock(blocks.StructBlock):
    """Bloco para seção de contato com imagem e formulário dinâmico"""
    
    # Configurações de fundo
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#132929',
        help_text="Cor de fundo da seção"
    )
    
    # Imagem lateral
    imagem = ImageChooserBlock(
        help_text="Imagem que ficará na lateral esquerda",
        required=False
    )
    
    alt_imagem = blocks.CharBlock(
        max_length=100,
        default="Imagem ilustrativa",
        help_text="Texto alternativo da imagem"
    )
    
    # Títulos da seção
    titulo_principal = blocks.CharBlock(
        max_length=100,
        help_text="Título principal da seção (ex: Fale Conosco)",
        default="Fale Conosco",
        required=False
    )
    
    cor_titulo_principal = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do título principal",
        required=False
    )
    
    subtitulo = blocks.CharBlock(
        max_length=200,
        help_text="Subtítulo da seção (ex: Envie sua mensagem)",
        default="Envie sua mensagem",
        required=False
    )
    
    cor_subtitulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#818C27',
        help_text="Cor do subtítulo",
        required=False
    )
    
    # FORMULÁRIO DINÂMICO - definido inline para evitar importação circular
    formulario = blocks.StructBlock([
        ('titulo', blocks.CharBlock(
            required=False,
            default="Formulário de Contato",
            help_text="Título do formulário (deixe vazio para usar o título principal)"
        )),
        
        ('descricao', blocks.TextBlock(
            required=False,
            help_text="Descrição ou instruções do formulário"
        )),
        
        # Campos do formulário - definindo inline para evitar problemas de importação
        ('campos', blocks.StreamBlock([
            ('texto', blocks.StructBlock([
                ('nome', blocks.CharBlock(max_length=50, help_text="Nome do campo (sem espaços)")),
                ('label', blocks.CharBlock(max_length=100, help_text="Texto do rótulo")),
                ('placeholder', blocks.CharBlock(max_length=100, required=False, help_text="Texto de exemplo")),
                ('obrigatorio', blocks.BooleanBlock(required=False, help_text="Campo obrigatório?")),
                ('ajuda', blocks.CharBlock(max_length=200, required=False, help_text="Texto de ajuda")),
            ], label="Campo de Texto", icon="edit")),
            
            ('email', blocks.StructBlock([
                ('nome', blocks.CharBlock(max_length=50, help_text="Nome do campo (sem espaços)")),
                ('label', blocks.CharBlock(max_length=100, help_text="Texto do rótulo")),
                ('placeholder', blocks.CharBlock(max_length=100, required=False, help_text="Texto de exemplo")),
                ('obrigatorio', blocks.BooleanBlock(required=False, help_text="Campo obrigatório?")),
                ('ajuda', blocks.CharBlock(max_length=200, required=False, help_text="Texto de ajuda")),
            ], label="Campo de E-mail", icon="mail")),
            
            ('telefone', blocks.StructBlock([
                ('nome', blocks.CharBlock(max_length=50, help_text="Nome do campo (sem espaços)")),
                ('label', blocks.CharBlock(max_length=100, help_text="Texto do rótulo")),
                ('placeholder', blocks.CharBlock(max_length=100, required=False, help_text="Texto de exemplo")),
                ('obrigatorio', blocks.BooleanBlock(required=False, help_text="Campo obrigatório?")),
                ('ajuda', blocks.CharBlock(max_length=200, required=False, help_text="Texto de ajuda")),
            ], label="Campo de Telefone", icon="phone")),
            
            ('textarea', blocks.StructBlock([
                ('nome', blocks.CharBlock(max_length=50, help_text="Nome do campo (sem espaços)")),
                ('label', blocks.CharBlock(max_length=100, help_text="Texto do rótulo")),
                ('placeholder', blocks.CharBlock(max_length=100, required=False, help_text="Texto de exemplo")),
                ('obrigatorio', blocks.BooleanBlock(required=False, help_text="Campo obrigatório?")),
                ('linhas', blocks.IntegerBlock(default=5, min_value=3, max_value=10, help_text="Número de linhas")),
                ('ajuda', blocks.CharBlock(max_length=200, required=False, help_text="Texto de ajuda")),
            ], label="Área de Texto", icon="doc-full")),
            
            ('select', blocks.StructBlock([
                ('nome', blocks.CharBlock(max_length=50, help_text="Nome do campo (sem espaços)")),
                ('label', blocks.CharBlock(max_length=100, help_text="Texto do rótulo")),
                ('placeholder', blocks.CharBlock(max_length=100, required=False, help_text="Texto da primeira opção")),
                ('obrigatorio', blocks.BooleanBlock(required=False, help_text="Campo obrigatório?")),
                ('opcoes', blocks.StreamBlock([
                    ('opcao', blocks.StructBlock([
                        ('label', blocks.CharBlock(max_length=100, help_text="Texto da opção")),
                        ('value', blocks.CharBlock(max_length=100, help_text="Valor da opção")),
                    ], label="Opção"))
                ], min_num=1, help_text="Opções do select")),
                ('ajuda', blocks.CharBlock(max_length=200, required=False, help_text="Texto de ajuda")),
            ], label="Campo de Seleção", icon="list-ul")),
            
            ('checkbox', blocks.StructBlock([
                ('nome', blocks.CharBlock(max_length=50, help_text="Nome do campo (sem espaços)")),
                ('label', blocks.CharBlock(max_length=100, help_text="Texto do rótulo")),
                ('obrigatorio', blocks.BooleanBlock(required=False, help_text="Campo obrigatório?")),
                ('ajuda', blocks.CharBlock(max_length=200, required=False, help_text="Texto de ajuda")),
            ], label="Checkbox", icon="tick")),
            
            ('radio', blocks.StructBlock([
                ('nome', blocks.CharBlock(max_length=50, help_text="Nome do campo (sem espaços)")),
                ('label', blocks.CharBlock(max_length=100, help_text="Texto do rótulo")),
                ('obrigatorio', blocks.BooleanBlock(required=False, help_text="Campo obrigatório?")),
                ('opcoes', blocks.StreamBlock([
                    ('opcao', blocks.StructBlock([
                        ('label', blocks.CharBlock(max_length=100, help_text="Texto da opção")),
                        ('value', blocks.CharBlock(max_length=100, help_text="Valor da opção")),
                    ], label="Opção"))
                ], min_num=2, help_text="Opções do radio button")),
                ('ajuda', blocks.CharBlock(max_length=200, required=False, help_text="Texto de ajuda")),
            ], label="Radio Buttons", icon="radio-full")),
            
            ('numero', blocks.StructBlock([
                ('nome', blocks.CharBlock(max_length=50, help_text="Nome do campo (sem espaços)")),
                ('label', blocks.CharBlock(max_length=100, help_text="Texto do rótulo")),
                ('placeholder', blocks.CharBlock(max_length=100, required=False, help_text="Texto de exemplo")),
                ('obrigatorio', blocks.BooleanBlock(required=False, help_text="Campo obrigatório?")),
                ('min', blocks.IntegerBlock(required=False, help_text="Valor mínimo")),
                ('max', blocks.IntegerBlock(required=False, help_text="Valor máximo")),
                ('ajuda', blocks.CharBlock(max_length=200, required=False, help_text="Texto de ajuda")),
            ], label="Campo Numérico", icon="plus")),
            
            ('data', blocks.StructBlock([
                ('nome', blocks.CharBlock(max_length=50, help_text="Nome do campo (sem espaços)")),
                ('label', blocks.CharBlock(max_length=100, help_text="Texto do rótulo")),
                ('obrigatorio', blocks.BooleanBlock(required=False, help_text="Campo obrigatório?")),
                ('ajuda', blocks.CharBlock(max_length=200, required=False, help_text="Texto de ajuda")),
            ], label="Campo de Data", icon="date")),
            
        ], 
        label="Campos do Formulário",
        help_text="Adicione e configure os campos do formulário",
        min_num=1
        )),
        
        # Configurações do formulário
        ('email_notificacao', blocks.EmailBlock(
            required=False,
            help_text="E-mail para receber notificações (opcional)"
        )),
        
        ('mensagem_sucesso', blocks.TextBlock(
            required=False,
            default="Obrigado! Seu formulário foi enviado com sucesso.",
            help_text="Mensagem exibida após envio bem-sucedido"
        )),
        
        # Estilo do botão
        ('texto_botao', blocks.CharBlock(
            max_length=50,
            default="Enviar",
            help_text="Texto do botão de envio"
        )),
        
        ('cor_botao', blocks.ChoiceBlock(
            choices=BRAND_BUTTON_CHOICES,
            default='#FFEB31',
            help_text="Cor do botão de enviar"
        )),
        
        ('cor_hover_botao', blocks.ChoiceBlock(
            choices=BRAND_HOVER_CHOICES,
            default='#E6D220',
            help_text="Cor do botão ao passar o mouse"
        )),
        
        ('cor_texto_botao', blocks.ChoiceBlock(
            choices=BRAND_TEXTS_CHOICES,
            default='#132929',
            help_text="Cor do texto do botão"
        )),
    ], 
    label="Configurações do Formulário",
    help_text="Configure o formulário de contato"
    )
    
    # Botões adicionais (opcional)
    botoes_adicionais = blocks.StreamBlock([
        ('botao', blocks.StructBlock([
            ('texto', blocks.CharBlock(
                max_length=100,
                help_text="Texto do botão"
            )),
            ('link', blocks.URLBlock(
                help_text="URL para onde o botão deve direcionar"
            )),
            ('cor_fundo', blocks.ChoiceBlock(
                choices=BRAND_BUTTON_CHOICES,
                default='#FFEB31',
                help_text="Cor de fundo do botão"
            )),
            ('cor_hover', blocks.ChoiceBlock(
                choices=BRAND_HOVER_CHOICES,
                default='#E6D220',
                help_text="Cor do botão ao passar o mouse"
            )),
            ('cor_texto', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#132929',
                help_text="Cor do texto do botão"
            )),
        ], icon='link', label='Botão')),
    ], 
    min_num=0,
    required=False,
    help_text="Botões adicionais além do botão de envio do formulário"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_secao_contato.html'
        icon = 'mail'
        label = 'Seção Contato - Formulário Dinâmico'
    
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        
        # ID único para o formulário
        context['form_id'] = f"form_contato_{uuid.uuid4().hex[:8]}"
        
        # Página atual
        if parent_context:
            context['page'] = parent_context.get('page')
        
        return context


class MenuNavigationBlock(blocks.StructBlock):
    """Bloco para menu de navegação customizado"""
    
    items_menu = blocks.ListBlock(
        blocks.StructBlock([
            ('texto', blocks.CharBlock(max_length=50, help_text="Texto do menu")),
            ('url', blocks.URLBlock(required=False, help_text="URL externa")),
            ('pagina_interna', blocks.PageChooserBlock(required=False, help_text="Ou escolha uma página interna")),
            ('ativo', blocks.BooleanBlock(required=False, default=False, help_text="Marcar como item ativo")),
        ]),
        min_num=1,
        max_num=10,
        help_text="Itens do menu de navegação"
    )
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#132929',
        help_text="Cor de fundo do menu"
    )
    
    cor_texto = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do texto do menu",
        required=False
    )
    
    cor_ativo = blocks.ChoiceBlock(
        choices=BRAND_BUTTON_CHOICES,
        default='#FF7A1B',
        help_text="Cor do item ativo"
    )
    
    cor_hover = blocks.ChoiceBlock(
        choices=BRAND_BUTTON_CHOICES,
        default='#FFEB31',
        help_text="Cor do hover nos itens"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/blocks_menu_navigation.html'
        icon = 'list-ul'
        label = 'Menu de Navegação'


class SecaoTestemunhosBlock(blocks.StructBlock):
    """Bloco para seção de testemunhos/depoimentos"""
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#FFF0D9',
        help_text="Cor de fundo da seção"
    )
    
    titulo = blocks.CharBlock(
        max_length=200,
        help_text="Título da seção (ex: O que dizem sobre nós)"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#132929',
        help_text="Cor do título",
        required=False
    )
    
    testemunhos = blocks.StreamBlock([
        ('testemunho', blocks.StructBlock([
            ('nome', blocks.CharBlock(
                max_length=100,
                help_text="Nome da pessoa"
            )),
            ('cargo', blocks.CharBlock(
                max_length=150,
                help_text="Cargo/posição da pessoa"
            )),
            ('foto', ImageChooserBlock(
                help_text="Foto da pessoa"
            )),
            ('depoimento', blocks.TextBlock(
                help_text="Texto do depoimento"
            )),
            ('cor_nome', blocks.ChoiceBlock(
                choices=BRAND_INOVACAO_CHOICES,
                default='#132929',
                help_text="Cor do nome",
                required=False
            )),
            ('cor_cargo', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#25552A',
                help_text="Cor do cargo"
            )),
            ('cor_depoimento', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#25552A',
                help_text="Cor do texto do depoimento"
            )),
        ], icon='user', label='Testemunho')),
    ], 
    min_num=1,
    max_num=6,
    help_text="Adicione até 6 testemunhos"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_testemunhos.html'
        icon = 'openquote'
        label = 'Seção Testemunhos'


class SecaoEstatisticasBlock(blocks.StructBlock):
    """Bloco para seção de estatísticas/números importantes"""
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#132929',
        help_text="Cor de fundo da seção"
    )
    
    titulo = blocks.CharBlock(
        max_length=200,
        required=False,
        help_text="Título da seção (opcional)"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do título",
        required=False
    )

    cor_line = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do título",
        required=False
    )
    
    estatisticas = blocks.StreamBlock([
        ('estatistica', blocks.StructBlock([
            ('numero', blocks.CharBlock(
                max_length=20,
                help_text="Número/valor (ex: 500+, 95%)"
            )),
            ('descricao', blocks.CharBlock(
                max_length=500,
                help_text="Descrição do número"
            )),
        ], icon='plus', label='Estatística')),
    ], 
    min_num=2,
    max_num=8,
    help_text="Adicione entre 2 e 8 estatísticas"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_estatisticas.html'
        icon = 'snippet'
        label = 'Seção Estatísticas'


class SecaoCardsBlock(blocks.StructBlock):
    """Bloco para seção com cards flexíveis"""
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#FFFFFF',
        help_text="Cor de fundo da seção"
    )
    
    titulo = blocks.CharBlock(
        max_length=200,
        required=False,
        help_text="Título da seção (opcional)"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#132929',
        help_text="Cor do título",
        required=False
    )
    
    cards = blocks.StreamBlock([
        ('card', blocks.StructBlock([
            ('imagem', ImageChooserBlock(
                help_text="Imagem do card"
            )),
            ('titulo_card', blocks.CharBlock(
                max_length=100,
                help_text="Título do card"
            )),
            ('texto', blocks.TextBlock(
                help_text="Texto descritivo do card"
            )),
            ('link', blocks.URLBlock(
                required=False,
                help_text="Link do card (opcional)"
            )),
            ('texto_link', blocks.CharBlock(
                max_length=50,
                required=False,
                default="Saiba mais",
                help_text="Texto do link"
            )),
            ('cor_titulo_card', blocks.ChoiceBlock(
                choices=BRAND_INOVACAO_CHOICES,
                default='#132929',
                help_text="Cor do título do card",
                required=False
            )),
            ('cor_texto', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#25552A',
                help_text="Cor do texto"
            )),
            ('cor_link', blocks.ChoiceBlock(
                choices=BRAND_BUTTON_CHOICES,
                default='#FF7A1B',
                help_text="Cor do link"
            )),
            ('cor_fundo_card', blocks.ChoiceBlock(
                choices=BRAND_BG_CHOICES,
                default='#FFF0D9',
                help_text="Cor de fundo do card"
            )),
        ], icon='doc-full', label='Card')),
    ], 
    min_num=1,
    max_num=12,
    help_text="Adicione até 12 cards"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_cards.html'
        icon = 'grip'
        label = 'Seção Cards'


class SecaoTimelineBlock(blocks.StructBlock):
    """Bloco para seção de timeline/linha do tempo"""
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#FFFFFF',
        help_text="Cor de fundo da seção"
    )
    
    titulo = blocks.CharBlock(
        max_length=200,
        help_text="Título da seção"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#132929',
        help_text="Cor do título",
        required=False
    )
    
    cor_linha = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#3A8A9C',
        help_text="Cor da linha do tempo",
        required=False
    )
    
    eventos = blocks.StreamBlock([
        ('evento', blocks.StructBlock([
            ('data', blocks.CharBlock(
                max_length=50,
                help_text="Data do evento (ex: Jan 2024)"
            )),
            ('titulo_evento', blocks.CharBlock(
                max_length=150,
                help_text="Título do evento"
            )),
            ('descricao', blocks.TextBlock(
                help_text="Descrição do evento"
            )),
            ('cor_data', blocks.ChoiceBlock(
                choices=BRAND_INOVACAO_CHOICES,
                default='#FF7A1B',
                help_text="Cor da data"
            )),
            ('cor_titulo_evento', blocks.ChoiceBlock(
                choices=BRAND_INOVACAO_CHOICES,
                default='#132929',
                help_text="Cor do título do evento",
                required=False
            )),
            ('cor_descricao', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#25552A',
                help_text="Cor da descrição"
            )),
            ('cor_circulo', blocks.ChoiceBlock(
                choices=BRAND_BUTTON_CHOICES,
                default='#FFEB31',
                help_text="Cor do círculo na linha"
            )),
        ], icon='date', label='Evento')),
    ], 
    min_num=2,
    max_num=15,
    help_text="Adicione entre 2 e 15 eventos na timeline"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_timeline.html'
        icon = 'time'
        label = 'Seção Timeline'


class SecaoHeroBannerBlock(blocks.StructBlock):
    """Bloco para hero banner principal"""
    
    imagem_fundo = ImageChooserBlock(
        help_text="Imagem de fundo do hero banner",
        required=False,
    )
    
    titulo_principal = blocks.CharBlock(
        max_length=150,
        help_text="Título principal do banner",
        default="SEMINÁRIO DE INOVAÇÃO 2025",
        required=False,
    )
    
    tag = blocks.CharBlock(
        max_length=300,
        required=False,
        help_text="Texto da tag",
        default="RESULTADO",
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do título principal",
        required=False
    )

    cor_bg_section = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do título principal",
        required=False
    )

    cor_bg_tag = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do título principal",
        required=False
    )
    
    cor_subtitulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFEB31',
        help_text="Cor do subtítulo",
        required=False
    )
    
    cor_texto = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do texto descritivo",
        required=False
    )
    
    # Botões do hero
    botoes_hero = blocks.StreamBlock([
        ('botao_hero', blocks.StructBlock([
            ('texto_botao', blocks.CharBlock(
                max_length=50,
                help_text="Texto do botão"
            )),
            ('link_botao', blocks.URLBlock(
                help_text="Link do botão"
            )),
            ('tipo_botao', blocks.ChoiceBlock(
                choices=[
                    ('primario', 'Primário'),
                    ('secundario', 'Secundário'),
                    ('outline', 'Outline'),
                ],
                default='primario',
                help_text="Tipo/estilo do botão"
            )),
            ('cor_fundo_botao', blocks.ChoiceBlock(
                choices=BRAND_BUTTON_CHOICES,
                default='#FF7A1B',
                help_text="Cor de fundo do botão"
            )),
            ('cor_texto_botao', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#132929',
                help_text="Cor do texto do botão"
            )),
            ('cor_hover_botao', blocks.ChoiceBlock(
                choices=BRAND_HOVER_CHOICES,
                default='#E6690F',
                help_text="Cor do hover do botão"
            )),
        ], icon='link', label='Botão Hero')),
    ], 
    min_num=0,
    max_num=3,
    help_text="Adicione até 3 botões no hero banner",
    required=False
    )
    
    # Overlay/sobreposição
    overlay_opacity = blocks.ChoiceBlock(
        choices=[
            ('0', 'Sem overlay'),
            ('0.3', 'Overlay leve'),
            ('0.5', 'Overlay médio'),
            ('0.7', 'Overlay forte'),
        ],
        default='0.5',
        help_text="Opacidade do overlay escuro sobre a imagem"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/block_hero_banner.html'
        icon = 'image'
        label = 'Hero Banner Destaque SI'





class BannerResultadoBlock(blocks.StructBlock):
    """
    Banner de Resultado com StreamField de botões flexíveis
    Baseado no design da Semana de Inovação 2025
    """
    
    # ========================================================================
    # CONFIGURAÇÕES DE FUNDO
    # ========================================================================
    imagem_fundo = ImageChooserBlock(
        required=False,
        help_text="Imagem de fundo do banner (recomendado: 1920x600px)"
    )
    

    
    # ========================================================================
    # CONTEÚDO DO BANNER
    # ========================================================================
    
    
    # Título do evento
    titulo_evento = blocks.CharBlock(
        max_length=100,
        default="SEMANA DE INOVAÇÃO",
        help_text="Nome do evento (ex: SEMANA DE INOVAÇÃO)",
        required=False,
    )
    
    cor_titulo_evento = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#2F2F2F',
        help_text="Cor do título do evento",
        required=False
    )
    
    # Tag central (ex: "RESULTADO")
    tag_central = blocks.CharBlock(
        max_length=50,
        default="RESULTADO",
        help_text="Tag que aparece no centro (ex: RESULTADO, NOVIDADE, IMPORTANTE)",
        required=False,
    )
    
    cor_fundo_tag = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#132929',
        help_text="Cor de fundo da tag central",
        required=False
    )
    
    cor_texto_tag = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do texto da tag central",
        required=False
    )
    
    # Título principal
    titulo_principal = blocks.CharBlock(
        max_length=200,
        default="CHAMADA PÚBLICA PARA ATIVIDADES",
        help_text="Título principal do banner",
        required=False,
    )
    
    cor_titulo_principal = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#990005',
        help_text="Cor do título principal",
        required=False
    )
    
    # ========================================================================
    # STREAMFIELD DE BOTÕES
    # ========================================================================
    botoes = blocks.StreamBlock([
        ('botao', blocks.StructBlock([
            ('texto', blocks.CharBlock(
                max_length=100,
                help_text="Texto do botão (ex: Resultado Atividades Online)"
            )),
            ('link', blocks.URLBlock(
                required=False,
                help_text="URL para onde o botão deve direcionar (opcional)"
            )),
            ('pagina_interna', blocks.PageChooserBlock(
                required=False,
                help_text="Ou escolha uma página interna do site"
            )),
            ('tipo_botao', blocks.ChoiceBlock(
                choices=[
                    ('preenchido', 'Preenchido'),
                    ('outline', 'Outline (apenas borda)'),
                    ('texto', 'Apenas texto'),
                ],
                default='preenchido',
                help_text="Estilo visual do botão"
            )),
            ('cor_fundo', blocks.ChoiceBlock(
                choices=BRAND_BUTTON_CHOICES,
                default='#FFEB31',
                help_text="Cor de fundo do botão (para tipo preenchido)"
            )),
            ('cor_texto', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#132929',
                help_text="Cor do texto do botão"
            )),
            ('cor_borda', blocks.ChoiceBlock(
                choices=BRAND_BUTTON_CHOICES,
                default='#132929',
                help_text="Cor da borda do botão (para tipo outline)"
            )),
            ('cor_hover_fundo', blocks.ChoiceBlock(
                choices=BRAND_HOVER_CHOICES,
                default='#E6D220',
                help_text="Cor do fundo no hover"
            )),
            ('cor_hover_texto', blocks.ChoiceBlock(
                choices=BRAND_TEXTS_CHOICES,
                default='#132929',
                help_text="Cor do texto no hover"
            )),
            ('abrir_nova_aba', blocks.BooleanBlock(
                required=False,
                default=False,
                help_text="Abrir link em nova aba?"
            )),
            ('icone', blocks.ChoiceBlock(
                choices=[
                    ('', 'Sem ícone'),
                    ('download', 'Download'),
                    ('external-link', 'Link externo'),
                    ('file-text', 'Documento'),
                    ('calendar', 'Calendário'),
                    ('users', 'Usuários'),
                    ('award', 'Prêmio'),
                    ('info', 'Informação'),
                    ('play', 'Play'),
                    ('mail', 'Email'),
                ],
                default='',
                required=False,
                help_text="Ícone do botão (opcional)"
            )),
        ], icon='link', label='Botão')),
    ], 
    min_num=1,
    max_num=6,
    help_text="Adicione de 1 a 6 botões. Recomendado: máximo 3 botões para melhor visual.",
    required=False
    )
    
    # ========================================================================
    # CONFIGURAÇÕES DE LAYOUT
    # ========================================================================
    altura_banner = blocks.ChoiceBlock(
        choices=[
            ('pequeno', 'Pequeno (400px)'),
            ('medio', 'Médio (500px)'),
            ('grande', 'Grande (600px)'),
            ('extra-grande', 'Extra Grande (700px)'),
            ('auto', 'Automático (baseado no conteúdo)'),
        ],
        default='medio',
        help_text="Altura do banner"
    )
    
    alinhamento_conteudo = blocks.ChoiceBlock(
        choices=[
            ('esquerda', 'Alinhado à esquerda'),
            ('centro', 'Centralizado'),
            ('direita', 'Alinhado à direita'),
        ],
        default='esquerda',
        help_text="Alinhamento do conteúdo de texto"
    )
    
    espacamento_botoes = blocks.ChoiceBlock(
        choices=[
            ('compacto', 'Compacto'),
            ('normal', 'Normal'),
            ('espaçoso', 'Espaçoso'),
        ],
        default='normal',
        help_text="Espaçamento entre os botões"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/banner_resultado.html'
        icon = 'image'
        label = 'Banner de Resultado'
        help_text = 'Banner com fundo, título e botões flexíveis'


# =============================================================================
# STREAMFIELD CHOICES PARA USO EM PÁGINAS
# =============================================================================

SEMANA_INOVACAO_STREAMFIELD_CHOICES = [
    # Blocos principais
    ('hero_banner', SecaoHeroBannerBlock()),
    ('banner_concurso', BannerConcurso()),
    ('galeria_fotos', GaleriaBlock()),
    
    # Blocos de conteúdo
    ('secao_apresentacao', SecaoApresentacaoBlock()),
    ('secao_categorias', SecaoCategoriasBlock()),
    ('secao_cards', SecaoCardsBlock()),
    ('material_apoio', MaterialApioBlock()),
    
    # Blocos informativos
    ('cronograma', CronogramaBlock()),
    ('secao_premios', SecaoPremiosBlock()),
    ('secao_faq', SecaoFAQBlock()),
    ('timeline', SecaoTimelineBlock()),
    
    # Blocos de engajamento
    ('secao_testemunhos', SecaoTestemunhosBlock()),
    ('secao_estatisticas', SecaoEstatisticasBlock()),
    ('secao_contato', SecaoContatoBlock()),
    
    # Blocos utilitários
    ('secao_patrocinadores', SecaoPatrocinadoresBlock()),
    ('menu_navigation', MenuNavigationBlock()),
    
    # Blocos básicos reutilizáveis
    ('imagem', ImageBlock()),
    ('participante', ParticipanteBlock()),
    ('galeria_foto', GaleriaFotoBlock()),
    ('video', VideoBlock()),
    ('certificado', CertificadoBlock()),
    ('newsletter', NewsletterBlock()),
    ('contato', ContatoBlock()),
    ('footer', FooterBlock()),
]





class PodcastSpotifyBlock(blocks.StructBlock):
    """
    Bloco para seção de podcast com embed do Spotify
    Layout: Texto à esquerda + Player Spotify à direita
    """
    
    # ========================================================================
    # CONFIGURAÇÕES DE FUNDO E LAYOUT
    # ========================================================================
    imagem_fundo = ImageChooserBlock(
        required=False,
        help_text="Imagem de fundo da seção (opcional)"
    )
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BRAND_BG_CHOICES,
        default='#132929',
        help_text="Cor de fundo da seção"
    )
    
    layout_tipo = blocks.ChoiceBlock(
        choices=[
            ('texto-esquerda', 'Texto à esquerda, Spotify à direita'),
            ('texto-direita', 'Texto à direita, Spotify à esquerda'),
            ('texto-topo', 'Texto no topo, Spotify embaixo'),
        ],
        default='texto-esquerda',
        help_text="Layout da seção"
    )
    
    # ========================================================================
    # CONTEÚDO DE TEXTO
    # ========================================================================
    titulo = blocks.CharBlock(
        max_length=200,
        default="INOVAR NO GOVERNO PODE? PODE!",
        help_text="Título principal da seção"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFEB31',
        help_text="Cor do título",
        required=False
    )
    
    descricao = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        help_text="Descrição do podcast em rich text",
        default="O InovaPod é o podcast oficial da ENAP, produzido pela Gnova - laboratório de inovação da ENAP. Ouça entrevistas e debates com especialistas e líderes, discutindo tendências e práticas inovadoras na administração pública."
    )
    
    cor_descricao = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do texto da descrição",
        required=False
    )
    
    # ========================================================================
    # BOTÃO DE AÇÃO
    # ========================================================================
    mostrar_botao = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Mostrar botão de ação?"
    )
    
    texto_botao = blocks.CharBlock(
        max_length=100,
        default="OUÇA AGORA",
        help_text="Texto do botão"
    )
    
    link_botao = blocks.URLBlock(
        required=False,
        help_text="URL para onde o botão deve direcionar"
    )
    
    pagina_interna_botao = blocks.PageChooserBlock(
        required=False,
        help_text="Ou escolha uma página interna do site"
    )
    
    tipo_botao = blocks.ChoiceBlock(
        choices=[
            ('preenchido', 'Preenchido'),
            ('outline', 'Outline (apenas borda)'),
            ('texto', 'Apenas texto'),
        ],
        default='preenchido',
        help_text="Estilo visual do botão"
    )
    
    cor_fundo_botao = blocks.ChoiceBlock(
        choices=BRAND_BUTTON_CHOICES,
        default='#FFEB31',
        help_text="Cor de fundo do botão"
    )
    
    cor_texto_botao = blocks.ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#132929',
        help_text="Cor do texto do botão"
    )
    
    cor_borda_botao = blocks.ChoiceBlock(
        choices=BRAND_BUTTON_CHOICES,
        default='#FFEB31',
        help_text="Cor da borda do botão (para tipo outline)"
    )
    
    cor_hover_fundo_botao = blocks.ChoiceBlock(
        choices=BRAND_HOVER_CHOICES,
        default='#E6D220',
        help_text="Cor do fundo no hover"
    )
    
    abrir_nova_aba_botao = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Abrir link em nova aba?"
    )
    
    # ========================================================================
    # EMBED DO SPOTIFY
    # ========================================================================
    spotify_embed_code = blocks.TextBlock(
        help_text="Código embed do Spotify (cole o código HTML completo do iframe)",
        default='<iframe style="border-radius:12px" src="https://open.spotify.com/embed/show/..." width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
    )
    
    spotify_titulo = blocks.CharBlock(
        max_length=200,
        required=False,
        help_text="Título do player Spotify (opcional, aparece acima do player)",
        default="Ouça o InovaPod",
    )
    
    cor_titulo_spotify = blocks.ChoiceBlock(
        choices=BRAND_INOVACAO_CHOICES,
        default='#FFF0D9',
        help_text="Cor do título do Spotify",
        required=False
    )
    
    # ========================================================================
    # CONFIGURAÇÕES VISUAIS
    # ========================================================================
    espacamento_secao = blocks.ChoiceBlock(
        choices=[
            ('pequeno', 'Pequeno (2rem)'),
            ('medio', 'Médio (4rem)'),
            ('grande', 'Grande (6rem)'),
            ('extra-grande', 'Extra Grande (8rem)'),
        ],
        default='grande',
        help_text="Espaçamento interno da seção"
    )
    
    border_radius_player = blocks.ChoiceBlock(
        choices=[
            ('0', 'Sem bordas arredondadas'),
            ('8px', 'Bordas suaves'),
            ('12px', 'Bordas médias'),
            ('16px', 'Bordas arredondadas'),
            ('24px', 'Bordas muito arredondadas'),
        ],
        default='12px',
        help_text="Bordas arredondadas do player"
    )
    
    sombra_player = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Adicionar sombra ao player do Spotify?"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/podcast_spotify.html'
        icon = 'media'
        label = 'Podcast + Spotify'
        help_text = 'Seção com texto e embed do Spotify'