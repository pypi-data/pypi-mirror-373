
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.blocks import StructBlock, BooleanBlock, CharBlock
from wagtail.admin.panels import FieldPanel
from django.db import models
from .html_blocks import ButtonBlock
from .base_blocks import BaseBlock



from wagtail.snippets.models import register_snippet
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel 

class EnapNavbarBlock(blocks.StructBlock):
	"""
	Bloco para permitir a seleção de um snippet de Navbar.
	"""

	navbar = SnippetChooserBlock("enap_designsystem.EnapNavbarSnippet")

	class Meta:
		template = "enap_designsystem/blocks/navbar/navbar_block.html"
		icon = "menu"
		label = "Navbar ENAP"


class EnapAccordionBlock(BaseBlock):
    """
    Allows selecting an accordion snippet
    """

    accordion = SnippetChooserBlock("enap_designsystem.EnapAccordionSnippet")
    
    def get_searchable_content(self, value):
        content = []

        snippet = value.get("accordion")
        if snippet:
            for block in snippet.panels_content:
                if block.block_type == "accordion_item":
                    item = block.value
                    content.append(item.get("title", ""))
                    content.append(item.get("content", "").source if hasattr(item.get("content", ""), "source") else "")
        return content
    
    class Meta:
        template = "enap_designsystem/blocks/accordions.html"
        icon = "bars"
        label = _("Accordion ENAP")


class EnapFooterLinkBlock(BaseBlock):
    """
    Um componente com texto e link para footer
    """

    title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Nome amigável"),
    )
    link = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Link"),
    )
    class Meta:
        template = "enap_designsystem/blocks/footer_link_block.html"
        icon = "cr-list-alt"
        label = _("Footer link")


class EnapFooterSocialBlock(BaseBlock):
	"""
	Um componente individual de rede social no footer.
	"""

	social_network = blocks.ChoiceBlock(
		choices=[
			("facebook", "Facebook"),
			("instagram", "Instagram"),
			("whatsapp", "WhatsApp"),
			("twitter", "Twitter"),
			("linkedin", "LinkedIn"),
			("youtube", "YouTube"),
		],
		label=_("Rede Social"),
		required=True,
		help_text="Escolha a rede social."
	)

	url = blocks.URLBlock(
		required=True,
		label=_("Link da Rede Social"),
		help_text="Insira o link para o perfil ou página."
	)
	class Meta:
		template = "enap_designsystem/blocks/footer/footer_social_block.html"
		icon = "site"
		label = _("Rede Social")


class CardBlock(BaseBlock):
    """
    A component of information with image, text, and buttons.
    """
    
    image = ImageChooserBlock(
        required=False,
        max_length=255,
        label=_("Image"),
    )
    title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Title"),
    )
    subtitle = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Subtitle"),
    )
    description = blocks.RichTextBlock(
        features=["bold", "italic", "ol", "ul", "hr", "link", "document-link"],
        label=_("Body"),
    )
    
    @property
    def links(self):
        from .html_blocks import ButtonBlock
        return blocks.StreamBlock(
            [("Links", ButtonBlock())],
            blank=True,
            required=False,
            label=_("Links"),
        )

    class Meta:
        template = "coderedcms/blocks/card_foot.html"
        icon = "cr-list-alt"
        label = _("Card")


class EnapCardBlock(blocks.StructBlock):
    """
    A component of information with image, text, and buttons.
    
    """

    type = blocks.ChoiceBlock(
        choices=[
            ('card-primary', 'Tipo primário'),
            ('card-secondary', 'Tipo secundário'),
            ('card-terciary', 'Tipo terciário'),
            ('card-bgimage', 'Tipo BG Image'),
            ('card-horizontal', 'Tipo Horizontal'),
            ('card-horizontal-reverse', 'Tipo Horizontal Invertido'),
            
        ],
        default='card-primary',
        help_text="Escolha o tipo/cor do card",
        label="Tipo de card"
    )

    image = ImageChooserBlock(
        required=False,
        label=_("Image"),
    )
    
    title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Title"),
    )
    
    description = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "ol", "ul", "hr", "link", "document-link"],
        label=_("Body"),
    )
    

    links = blocks.StreamBlock(
        [
            ("button", ButtonBlock()),
        ],
        max_num=3,
        blank=True,
        required=False,
        label="Botões (links)",
        help_text="Adicione até 3 botões para o card"
    )

    class Meta:
        template = "enap_designsystem/blocks/card_block.html"
        icon = "cr-list-alt"
        label = "Enap Card"


class EnapBannerBlock(blocks.StructBlock):
    """
    Bloco para o Hero Banner com imagem de fundo, título e descrição.
    """
    background_image = ImageChooserBlock(
        required=False, 
        label=_("Background Image"),
    )
    title = blocks.CharBlock(
    required=True,
    max_length=200,
    label=_("Title"),
    help_text=_("Título do banner"),
    )
    
    description = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "ol", "ul", "hr", "link", "document-link"],
        label=_("Description"),
        default="Descrição do banner. Edite este texto para personalizar o conteúdo.",
    )

    overlay = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Enable Overlay"),
        help_text=_("Adiciona uma sobreposição escura sobre a imagem de fundo para melhorar a legibilidade do texto"),
    )

    def get_searchable_content(self, value):
        return [
            value.get("title", ""),
            value.get("description", "").source if hasattr(value.get("description", ""), "source") else ""
        ]
    
    class Meta:
        template = "enap_designsystem/blocks/banner.html"
        icon = "image"
        label = _("Hero Banner")
        initialized = True





class EnapBannerLogoBlock(blocks.StructBlock):
    """
    Bloco para o Hero Banner com imagem de fundo, título e descrição.
    """
    background_image = ImageChooserBlock(
        required=False, 
        label=_("Background Image"),
    )
    logo_image = ImageChooserBlock(
        required=False, 
        label=_("Logo Image"),
    )
    title = blocks.CharBlock(
        required=True,
        max_length=255,
        label=_("Title"),
        default="Título do Banner",
    )
    description = blocks.RichTextBlock(
        required=True,
        features=["bold", "italic", "ol", "ul", "hr", "link", "document-link"],
        label=_("Description"),
        default="Descrição do banner. Edite este texto para personalizar o conteúdo.",
    )

    def get_searchable_content(self, value):
        return [
            value.get("title", ""),
            value.get("description", "").source if hasattr(value.get("description", ""), "source") else ""
        ]

    class Meta:
        template = "enap_designsystem/blocks/banner_logo.html"
        icon = "image"
        label = _("Hero Banner com logo")
        initialized = True


class EnapBannerVideoBlock(blocks.StructBlock):
    """
    Bloco para o Hero Banner com imagem de fundo, título e descrição.
    """
    video_background = models.FileField(
        upload_to='media/imagens', 
        null=True, 
        blank=True, 
        verbose_name="Vídeo de Fundo"
    )
    title = blocks.CharBlock(
        required=True,
        max_length=255,
        label=_("Title"),
    )
    description = blocks.RichTextBlock(
        required=True,
        features=["bold", "italic", "ol", "ul", "hr", "link", "document-link"],
        label=_("Description"),
    )

    class Meta:
        template = "enap_designsystem/blocks/banner-video.html"
        icon = "image"
        label = _("Video Banner")



class FeatureImageTextBlock(blocks.StructBlock):
   background_image = ImageChooserBlock(required=True)
   image_position = blocks.ChoiceBlock(
       choices=[
           ('left', 'Imagem à Esquerda'),
           ('right', 'Imagem à Direita'),
       ],
       default='left',
       help_text='Escolha a posição da imagem'
   )
   title = blocks.CharBlock(required=True, max_length=255)
   description = blocks.RichTextBlock(required=True)

   def get_searchable_content(self, value):
       return [
           value.get("title", ""),
           value.get("description", "").source if hasattr(value.get("description", ""), "source") else ""
       ]
   
   class Meta:
       template = "enap_designsystem/blocks/feature-img-texts.html"
       label = _("Seção Duas Colunas Imagem e Card Colorido Título Texto")


class EnapAccordionPanelBlock(blocks.StructBlock):
	"""
	Bloco individual de uma seção de accordion dentro do snippet.
	"""

	title = blocks.CharBlock(
		required=True,
		max_length=255,
		label="Pergunta / Titulo"
	)

	content = blocks.RichTextBlock(
		required=True,
		label="Resposta",
		features=["bold", "italic", "link"]
	)

	class Meta:
		icon = "list-ul"
		label = "Item do Accordion"


class EnapNavbarLinkBlock(blocks.StructBlock):
	"""
	Bloco para representar um link na Navbar.
	"""

	label = blocks.CharBlock(required=True, max_length=255, label="Texto do Link")
	url = blocks.URLBlock(required=True, label="URL do Link")
	style = blocks.ChoiceBlock(
		choices=[
			("default", "Padrão"),
			("button", "Botão"),
			("icon", "Ícone"),
		],
		default="default",
		label="Estilo do Link"
	)

	class Meta:
		icon = "link"
		label = "Link da Navbar"






class FormularioBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=False, help_text="Título do formulário")
    
    class Meta:
        template = 'enap_designsystem/blocks/contato_page.html'
        icon = 'form'
        label = 'Formulário'






class BreadcrumbBlock(StructBlock):
    """Bloco de breadcrumb que usa seu template existente"""
    
    dark_theme = BooleanBlock(
        label="Tema Escuro",
        help_text="Aplicar estilo escuro ao breadcrumb",
        default=False,
        required=False
    )
    
    home_url = CharBlock(
        label="URL da Página Inicial",
        help_text="URL para o link da casa (padrão: /)",
        default="/",
        max_length=200,
        required=False
    )
    
    class Meta:
        icon = "list-ul"
        label = "Breadcrumb"
        template = "enap_designsystem/blocks/breadcrumbs.html"


class AutoBreadcrumbBlock(StructBlock):
    """Breadcrumb automático baseado na hierarquia de páginas"""
    
    dark_theme = BooleanBlock(
        label="Tema Escuro",
        help_text="Aplicar estilo escuro ao breadcrumb",
        default=False,
        required=False
    )
    
    home_url = CharBlock(
        label="URL da Página Inicial",
        default="/",
        max_length=200,
        required=False
    )
    
    class Meta:
        icon = "site"
        label = "Breadcrumb Automático"
        template = "enap_designsystem/blocks/auto_breadcrumb_block.html"







# StructBlock para os slides (usando ImageChooserBlock)
class CarouselSlideBlock(blocks.StructBlock):
    """Slide individual com ImageChooserBlock"""
    
    titulo = blocks.CharBlock(
        label="Título",
        max_length=200,
        required=True,
        help_text="Título principal do slide"
    )
    
    subtitulo = blocks.CharBlock(
        label="Subtítulo",
        max_length=300,
        required=False,
        help_text="Subtítulo ou descrição do slide"
    )
    
    texto = blocks.RichTextBlock(
        label="Texto",
        required=False,
        help_text="Conteúdo do slide (opcional)"
    )
    
    imagem_desktop = ImageChooserBlock(
        label="Imagem Desktop",
        required=True,
        help_text="Imagem otimizada para telas desktop (recomendado: 1920x600px)"
    )
    
    imagem_mobile = ImageChooserBlock(
        label="Imagem Mobile",
        required=True,
        help_text="Imagem otimizada para telas mobile (recomendado: 768x600px)"
    )
    
    link_texto = blocks.CharBlock(
        label="Texto do Link",
        max_length=50,
        required=False,
        help_text="Texto do botão/link (ex: 'Saiba mais')"
    )
    
    link_url = blocks.URLBlock(
        label="URL do Link",
        required=False,
        help_text="URL de destino do botão"
    )
    
    link_interno = blocks.PageChooserBlock(
        label="Página Interna",
        required=False,
        help_text="Ou escolha uma página interna do site"
    )
    
    posicao_texto = blocks.ChoiceBlock(
        label="Posição do Texto",
        choices=[
            ('left', 'Esquerda'),
            ('center', 'Centro'),
            ('right', 'Direita'),
        ],
        default='left'
    )
    
    cor_tema = blocks.ChoiceBlock(
        label="Cor do Tema",
        choices=[
            ('primary', 'Primária (Azul ENAP)'),
            ('secondary', 'Secundária'),
            ('light', 'Clara'),
            ('dark', 'Escura'),
        ],
        default='primary'
    )

    class Meta:
        icon = 'image'
        label = 'Slide'


@register_snippet
class CarouselResponsivo(models.Model):
    """
    Snippet de carrossel responsivo reutilizável
    """
    nome = models.CharField(
        max_length=100,
        help_text="Nome para identificar o carrossel no admin"
    )
    
    titulo_secao = models.CharField(
        max_length=200,
        blank=True,
        help_text="Título opcional para a seção do carrossel"
    )
    
    # StreamField com os slides usando ImageChooserBlock
    slides = StreamField([
        ('slide', CarouselSlideBlock()),
    ], use_json_field=True, blank=True, help_text="Slides do carrossel")
    
    # Configurações do carrossel
    autoplay = models.BooleanField(
        default=True,
        help_text="Ativar mudança automática de slides"
    )
    
    intervalo_autoplay = models.PositiveIntegerField(
        default=5,
        help_text="Tempo entre mudanças automáticas (em segundos)"
    )
    
    mostrar_indicators = models.BooleanField(
        default=True,
        help_text="Exibir pontos indicadores na parte inferior"
    )
    
    mostrar_navegacao = models.BooleanField(
        default=True,
        help_text="Exibir setas de navegação lateral"
    )
    
    altura_desktop = models.CharField(
        max_length=20,
        choices=[
            ('400px', 'Baixa (400px)'),
            ('500px', 'Média (500px)'),
            ('600px', 'Alta (600px)'),
            ('700px', 'Extra Alta (700px)'),
        ],
        default='600px',
        help_text="Altura do carrossel em telas desktop"
    )
    
    altura_mobile = models.CharField(
        max_length=20,
        choices=[
            ('300px', 'Baixa (300px)'),
            ('400px', 'Média (400px)'),
            ('500px', 'Alta (500px)'),
            ('600px', 'Extra Alta (600px)'),
        ],
        default='400px',
        help_text="Altura do carrossel em telas mobile"
    )
    
    efeito_transicao = models.CharField(
        max_length=20,
        choices=[
            ('slide', 'Deslizar'),
            ('fade', 'Fade'),
        ],
        default='slide',
        help_text="Tipo de transição entre slides"
    )

    panels = [
        FieldPanel('nome'),
        FieldPanel('titulo_secao'),
        FieldPanel('slides'),
        MultiFieldPanel([
            FieldPanel('autoplay'),
            FieldPanel('intervalo_autoplay'),
        ], heading="Configurações de Autoplay"),
        MultiFieldPanel([
            FieldPanel('altura_desktop'),
            FieldPanel('altura_mobile'),
        ], heading="Dimensões"),
        MultiFieldPanel([
            FieldPanel('mostrar_navegacao'),
            FieldPanel('mostrar_indicators'),
            FieldPanel('efeito_transicao'),
        ], heading="Controles e Efeitos"),
    ]

    class Meta:
        verbose_name = "Carrossel Responsivo"
        verbose_name_plural = "Carrosseis Responsivos"

    def __str__(self):
        return self.nome