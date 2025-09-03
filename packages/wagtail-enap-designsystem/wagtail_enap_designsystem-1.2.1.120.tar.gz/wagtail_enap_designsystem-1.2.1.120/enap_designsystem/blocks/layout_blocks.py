"""
Os blocos de layout são essencialmente um wrapper em torno do conteúdo.
e.g. rows, columns, hero units, etc.
"""

from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from .html_blocks import (
    SimpleDashboardChartBlock,
    SimpleKPICardBlock, 
    SimpleDashboardRowBlock,
    TimelineBlock,
    DepoimentosVideoListBlock
)

from django.db import models

from coderedcms.settings import crx_settings
from wagtail import blocks


from .base_blocks import BaseLayoutBlock
from .base_blocks import CoderedAdvColumnSettings
from .content_blocks import EnapAccordionBlock
from .content_blocks import EnapBannerBlock

from .content_blocks import EnapAccordionBlock, EnapBannerBlock, EnapFooterLinkBlock, EnapFooterSocialBlock

from wagtail.blocks import StructBlock, CharBlock, ListBlock, ChoiceBlock
from wagtail.fields import StreamField


class ColumnBlock(BaseLayoutBlock):
    """
    Renders content in a column.
    """

    column_size = blocks.ChoiceBlock(
        choices=crx_settings.CRX_FRONTEND_COL_SIZE_CHOICES,
        default=crx_settings.CRX_FRONTEND_COL_SIZE_DEFAULT,
        required=False,
        label=_("Column size"),
    )

    advsettings_class = CoderedAdvColumnSettings

    class Meta:
        template = "coderedcms/blocks/column_block.html"
        icon = "placeholder"
        label = "Column"


class GridBlock(BaseLayoutBlock):
    """
    Renders a row of columns.
    """

    fluid = blocks.BooleanBlock(
        required=False,
        label=_("Full width"),
    )

    class Meta:
        template = "coderedcms/blocks/grid_block.html"
        icon = "cr-columns"
        label = _("Responsive Grid Row")

    def __init__(self, local_blocks=None, **kwargs):
        super().__init__(local_blocks=[("content", ColumnBlock(local_blocks))])


class EnapFooterGridBlock(BaseLayoutBlock):
    """
    Renders a row of cards.
    """

    title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Titulo"),
    )

    links = blocks.ListBlock(
		EnapFooterLinkBlock(),
		label=_("Links do Footer"),
	)
    class Meta:
        template = "enap_designsystem/blocks/footer_grid_block.html"
        icon = "cr-th-large"
        label = _("Footer Grid")


class EnapFooterSocialGridBlock(BaseLayoutBlock):
	"""
	Bloco para agrupar redes sociais no footer.
	"""

	social_links = blocks.ListBlock(
		EnapFooterSocialBlock(),
		label=_("Redes Sociais"),
	)

	class Meta:
		template = "enap_designsystem/blocks/footer/footer_social_grid_block.html"
		icon = "cr-site"
		label = _("Social Grid")


class CardGridBlock(BaseLayoutBlock):
    """
    Renders a row of cards.
    """

    fluid = blocks.BooleanBlock(
        required=False,
        label=_("Full width"),
    )
    class Meta:
        template = "coderedcms/blocks/cardgrid_deck.html"
        icon = "cr-th-large"
        label = _("Card Grid")

class EnapCardGridBlock(BaseLayoutBlock):
    """
    Renderiza uma linha de cards
    """
    grid = blocks.ChoiceBlock(
		choices=[
            ('cards-gri-1', '1 card por linha'),
			('cards-gri-2', 'Até 2 cards'),
			('cards-gri-3', 'Até 3 cards'),
			('cards-gri-4', 'Até 4 cards')
		],
		default='cards-gri-2',
		help_text="Escolha os limites de card por linha para essa grid.",
		label="Card por linha"
	)
    class Meta:
        template = "enap_designsystem/blocks/cardgrid_block.html"
        icon = "cr-th-large"
        label = _("Enap Card 1, 2, 3 ou 4 por linha")


class EnapSectionBlock(BaseLayoutBlock):
    """
    Renderiza uma seção com titulo-subtitulo permitindo componentes dentro
    """

    id_slug = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("#ID da seção"),
    )

    custom_class = blocks.ChoiceBlock(
        choices=[
            ('bg-enap-100', 'Verde ENAP 100 (#02333A)'),
            ('bg-enap-90', 'Verde ENAP 90 (#024248)'),
            ('bg-enap-80', 'Verde ENAP 80 (#025257)'),
            ('bg-enap-70', 'Verde ENAP 70 (#006969)'),
            ('bg-enap-50', 'Verde ENAP 50 (#10A39E)'),
            ('bg-enap-40', 'Verde ENAP 40 (#30BFBC)'),
            ('bg-enap-30', 'Verde ENAP 30 (#70E0DF)'),
            ('bg-enap-20', 'Verde ENAP 20 (#AFF0ED)'),
            ('bg-enap-10', 'Verde ENAP 10 (#D6F9F8)'),
            ('bg-white', 'Fundo branco (#FFFFFF)'),
            ('bg-blue', 'Fundo blue'),
            ('bg-gray', 'Fundo cinza'),
            ('bg-whitetwo', 'Fundo branco alternativo'),
            ('bg-darkgreen', 'Fundo verde escuro'),
            ('bg-gray-light', 'Cinza Claro (#F8F9FA)'),
            ('bg-gray-medium', 'Cinza Médio (#E9ECEF)'),
        ],
        default='bg-white',
        help_text="Escolha a cor de fundo para a seção",
        label="Cor de fundo"
    )

    spacing = blocks.ChoiceBlock(
        choices=[
            ('none', 'Sem espaçamento (0px)'),
            ('small', 'Pequeno (20px)'),
            ('medium', 'Médio (40px)'),
            ('large', 'Grande (60px)'),
            ('extra-large', 'Extra grande (80px)')
        ],
        default='medium',
        help_text="Escolha o espaçamento vertical da seção",
        label="Espaçamento vertical"
    )

    title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Titulo"),
    )

    subtitle = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "ol", "ul", "hr", "link", "document-link"],
        label=_("Subtitulo"),
    )
    
    class Meta:
        template = "enap_designsystem/blocks/section_block.html"
        icon = "cr-th-large"
        label = _("Enap Section Block")


        

class HeroBlock(BaseLayoutBlock):
    """
    Wrapper with color and image background options.
    """

    fluid = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Full width"),
    )
    is_parallax = blocks.BooleanBlock(
        required=False,
        label=_("Parallax Effect"),
        help_text=_(
            "Background images scroll slower than foreground images, creating an illusion of depth."
        ),
    )
    background_image = ImageChooserBlock(required=False)
    tile_image = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Tile background image"),
    )
    background_color = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Background color"),
        help_text=_("Hexadecimal, rgba, or CSS color notation (e.g. #ff0011)"),
    )
    foreground_color = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Text color"),
        help_text=_("Hexadecimal, rgba, or CSS color notation (e.g. #ff0011)"),
    )

    class Meta:
        template = "coderedcms/blocks/hero_block.html"
        icon = "cr-newspaper-o"
        label = "Bloco Hero"


class AccordionWrapperBlock(BaseLayoutBlock):
    """
    Wrapper for the AccordionBlock.
    """
    accordion = EnapAccordionBlock()

    class Meta:
        template = "enap_designsystem/blocks/accordions.html" 
        icon = "bars"

        label = "Accordion Wrapper"




class HeroBlock(BaseLayoutBlock):
    """
    Wrapper with color and image background options.
    """

    fluid = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Full width"),
    )
    is_parallax = blocks.BooleanBlock(
        required=False,
        label=_("Parallax Effect"),
        help_text=_(
            "Background images scroll slower than foreground images, creating an illusion of depth."
        ),
    )
    background_image = ImageChooserBlock(required=True) 
    tile_image = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Tile background image"),
    )
    content = blocks.StreamBlock([
        ('enap_banner', EnapBannerBlock()),
    ], label="Content")

    class Meta:
        template = "enap_designsystem/blocks/banner.html" 
        icon = "cr-newspaper-o"
        label = _("Banner Hero")




class HeroVideoBlock(BaseLayoutBlock):
    """
    Wrapper with color and image background options.
    """

    video_background = models.FileField(
        upload_to='media/videos',
        null=True, 
        blank=True, 
        verbose_name="Vídeo de Fundo"
    )
    content = blocks.StreamBlock([
        ('enap_banner', EnapBannerBlock()),
    ], label="Content")

    class Meta:
        template = "enap_designsystem/blocks/banner-video.html" 
        icon = "cr-newspaper-o"
        label = _("Banner video Hero")




class FeatureImageTextBlock(blocks.StructBlock):
    background_image = ImageChooserBlock(required=True)
    title = blocks.CharBlock(required=True, max_length=255)
    description = blocks.RichTextBlock(required=True)

    class Meta:
        template = "enap_designsystem/blocks/feature-img-texts.html"
        label = _("Feature Image and Text")





class SimpleDashboardChartBlock(blocks.StructBlock):
    """Gráfico simples com dados manuais"""
    
    CHART_TYPES = [
        ('card', 'Card com Número'),
        ('donut', 'Gráfico Donut'),
        ('bar', 'Gráfico de Barras'),
        ('pie', 'Gráfico de Pizza'),
        ('line', 'Gráfico de Linha'),
    ]
    
    title = blocks.CharBlock(
        label="Título do Gráfico",
        max_length=100,
        help_text="Ex: Matriculados por Curso"
    )
    
    chart_type = blocks.ChoiceBlock(
        choices=CHART_TYPES,
        label="Tipo de Gráfico",
        default='card'
    )
    
    chart_data = blocks.ListBlock(
        blocks.StructBlock([
            ('label', blocks.CharBlock(label="Rótulo", max_length=50)),
            ('value', blocks.IntegerBlock(label="Valor")),
            ('color', blocks.CharBlock(label="Cor", max_length=7, required=False)),
        ]),
        label="Dados do Gráfico",
        help_text="Adicione os dados que aparecerão no gráfico"
    )
    
    width = blocks.ChoiceBlock(
        choices=[
            ('col-12', 'Largura Total'),
            ('col-6', 'Meia Largura'),
            ('col-4', 'Um Terço'),
            ('col-3', 'Um Quarto'),
        ],
        label="Largura",
        default='col-6'
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/simple_dashboard_chart.html'
        icon = 'view'
        label = "Gráfico Dashboard"


class SimpleKPICardBlock(blocks.StructBlock):
    """Card simples de KPI"""
    
    ICONS = [
        ('users', 'Usuários'),
        ('user-check', 'Usuário Verificado'),
        ('trending-up', 'Crescimento'),
        ('activity', 'Atividade'),
        ('target', 'Meta'),
        ('graduation-cap', 'Formação'),
    ]
    
    title = blocks.CharBlock(
        label="Título",
        max_length=50,
        help_text="Ex: Total de Matriculados"
    )
    
    value = blocks.CharBlock(
        label="Valor Principal",
        max_length=20,
        help_text="Ex: 1.186, 15%, R$ 25.000"
    )
    
    icon = blocks.ChoiceBlock(
        choices=ICONS,
        label="Ícone",
        default='activity'
    )
    
    color = blocks.ChoiceBlock(
        choices=[
            ('primary', 'Azul Primário'),
            ('success', 'Verde'),
            ('info', 'Azul Claro'),
            ('warning', 'Amarelo'),
            ('danger', 'Vermelho'),
        ],
        label="Cor do Card",
        default='primary'
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/simple_kpi_card.html'
        icon = 'doc-full-inverse'
        label = "Card KPI"


class SimpleDashboardRowBlock(blocks.StructBlock):
    """Linha para organizar múltiplos gráficos"""
    
    row_title = blocks.CharBlock(
        label="Título da Seção",
        max_length=100,
        required=False,
        help_text="Título para agrupar os gráficos (opcional)"
    )
    
    charts = blocks.StreamBlock([
        ('chart', SimpleDashboardChartBlock()),
        ('kpi', SimpleKPICardBlock()),
    ], 
    label="Gráficos e KPIs",
    help_text="Adicione os gráficos que ficarão nesta linha")
    
    class Meta:
        template = 'enap_designsystem/blocks/simple_dashboard_row.html'
        icon = 'grip'
        label = "Linha de Gráficos"


# ===== VERSÕES SIMPLES DAS CLASSES COMPLEXAS =====

class DashboardContainerBlock(blocks.StructBlock):
    """Container principal para dashboards - VERSÃO SIMPLES"""
    
    dashboard_title = blocks.CharBlock(
        label="Título do Dashboard",
        max_length=200,
        help_text="Título principal do dashboard"
    )
    
    description = blocks.TextBlock(
        label="Descrição",
        required=False,
        help_text="Descrição do dashboard"
    )
    
    # KPIs de destaque no topo
    highlight_kpis = blocks.ListBlock(
        SimpleKPICardBlock(),
        label="KPIs de Destaque",
        required=False,
        help_text="KPIs principais que aparecerão no topo"
    )
    
    # Linhas de gráficos - AGORA FUNCIONA!
    dashboard_rows = blocks.ListBlock(
        SimpleDashboardRowBlock(),
        label="Linhas do Dashboard",
        help_text="Organize seus gráficos em linhas"
    )
    
    show_last_update = blocks.BooleanBlock(
        label="Mostrar Última Atualização",
        default=True,
        required=False
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/simple_dashboard_container.html'
        icon = 'view'
        label = "Container Dashboard"


class KPISectionBlock(blocks.StructBlock):
    """Seção específica para KPIs - VERSÃO SIMPLES"""
    
    section_title = blocks.CharBlock(
        label="Título da Seção",
        required=False,
        help_text="Título da seção de KPIs"
    )
    
    # AGORA FUNCIONA - usa a classe simples!
    kpi_cards = blocks.ListBlock(
        SimpleKPICardBlock(),
        label="Cards KPI",
        help_text="Adicione os cards de KPI"
    )
    
    cards_per_row = blocks.ChoiceBlock(
        choices=[
            ('2', '2 por linha'),
            ('3', '3 por linha'),
            ('4', '4 por linha'),
            ('6', '6 por linha'),
        ],
        label="Cards por Linha",
        default='4'
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/kpi_section.html'
        icon = 'doc-full-inverse'
        label = "Seção de KPIs"


class FilterBarBlock(blocks.StructBlock):
    """Barra de filtros para dashboards - MANTÉM IGUAL"""
    
    FILTER_TYPES = [
        ('select', 'Lista de Seleção'),
        ('date', 'Data'),
        ('text', 'Texto Livre'),
    ]
    
    filters = blocks.ListBlock(
        blocks.StructBlock([
            ('label', blocks.CharBlock(label="Rótulo do Filtro")),
            ('filter_type', blocks.ChoiceBlock(
                choices=FILTER_TYPES,
                label="Tipo de Filtro"
            )),
        ]),
        label="Filtros Disponíveis"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/dashboard_filters.html'
        icon = 'list-ul'
        label = "Barra de Filtros"


class ResponsiveDashboardBlock(blocks.StructBlock):
    """Dashboard responsivo - VERSÃO SIMPLES"""
    
    title = blocks.CharBlock(
        label="Título",
        max_length=200
    )
    
    subtitle = blocks.CharBlock(
        label="Subtítulo",
        required=False,
        max_length=300
    )
    
    # Conteúdo simplificado - SEM DEPENDÊNCIAS PROBLEMÁTICAS
    dashboard_content = blocks.StreamBlock([
        ('row', SimpleDashboardRowBlock()),
        ('kpi_section', KPISectionBlock()),
        ('single_chart', SimpleDashboardChartBlock()),
    ], 
    label="Conteúdo do Dashboard",
    required=False)
    
    class Meta:
        template = 'enap_designsystem/blocks/responsive_dashboard.html'
        icon = 'view'
        label = "Dashboard Responsivo"


class DashboardPageBlock(blocks.StructBlock):
    """Página de dashboard - VERSÃO SIMPLES"""
    
    page_title = blocks.CharBlock(
        label="Título da Página",
        help_text="Título principal da página"
    )
    
    # Conteúdo simplificado - AGORA FUNCIONA!
    dashboard_content = blocks.StreamBlock([
        ('container', DashboardContainerBlock()),
        ('responsive', ResponsiveDashboardBlock()),
        ('kpi_section', KPISectionBlock()),
        ('single_row', SimpleDashboardRowBlock()),
    ])
    
    class Meta:
        template = 'enap_designsystem/blocks/dashboard_page.html'
        icon = 'doc-full'
        label = "Página de Dashboard Completa"





class DashboardGridWrapperBlock(blocks.StructBlock):
    """
    Grid wrapper que recebe blocks como parâmetro
    Igual ao EnapCardGridBlock mas para dashboards
    """
    
    def __init__(self, local_blocks=None, **kwargs):
        # Se não passar blocks, usa os padrão
        if local_blocks is None:
            local_blocks = [
                ("dashboard_chart", SimpleDashboardChartBlock()),
                ("kpi_card", SimpleKPICardBlock()),
                ("dashboard_row", SimpleDashboardRowBlock()),
            ]
        
        # Cria o StreamBlock com os blocks passados como parâmetro
        self.child_blocks = blocks.StreamBlock(local_blocks)
        
        super().__init__([
            ('grid_title', blocks.CharBlock(
                label="Título da Seção",
                max_length=100,
                required=False,
                help_text="Título opcional para esta seção em grid"
            )),
            
            ('grid_type', blocks.ChoiceBlock(
                choices=[
                    ('grid-1', '1 coluna'),
                    ('grid-2', '2 colunas (1fr 1fr)'),
                    ('grid-3', '3 colunas (1fr 1fr 1fr)'),
                    ('grid-4', '4 colunas (1fr 1fr 1fr 1fr)'),
                ],
                default='grid-2',
                help_text="Escolha quantas colunas o grid terá",
                label="Colunas do Grid"
            )),
            
            ('gap', blocks.ChoiceBlock(
                choices=[
                    ('gap-1', 'Espaço Pequeno'),
                    ('gap-2', 'Espaço Médio'),
                    ('gap-3', 'Espaço Grande'),
                ],
                label="Espaçamento",
                default='gap-2'
            )),
            
            ('background_color', blocks.ChoiceBlock(
                choices=[
                    ('', 'Transparente'),
                    ('bg-light', 'Fundo Claro'),
                    ('bg-white', 'Fundo Branco'),
                ],
                label="Cor de Fundo",
                default='',
                required=False
            )),
            
            # Aqui é onde ficam os blocks que foram passados como parâmetro
            ('grid_content', self.child_blocks),
            
        ], **kwargs)
    
    class Meta:
        template = "enap_designsystem/blocks/dashboard_grid_wrapper.html"
        icon = "grip"
        label = "Dashboard Grid"








class TimelineContainerBlock(blocks.StructBlock):
    """
    Container wrapper para Timeline com opções de layout avançadas
    """
    timeline = TimelineBlock(label="Timeline de Etapas")
    
    container_class = blocks.ChoiceBlock(
        choices=[
            ('container', 'Container Padrão'),
            ('container-fluid', 'Container Fluido'),
            ('container-sm', 'Container Pequeno'),
            ('container-lg', 'Container Grande'),
        ],
        default='container',
        required=False,
        help_text="Tipo de container Bootstrap",
        label="Tipo de Container"
    )
    
    # Cores do Brand Design System
    cor_fundo = blocks.ChoiceBlock(
        choices=[
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
            ('#BAC946', 'Verdinho'),
            ('transparent', 'Transparente'),
        ],
        default='#FFFFFF',
        required=False,
        help_text="Escolha a cor de fundo para a timeline",
        label="Cor de fundo"
    )
    
    espacamento_vertical = blocks.ChoiceBlock(
        choices=[
            ('none', 'Sem espaçamento (0px)'),
            ('small', 'Pequeno (20px)'),
            ('medium', 'Médio (40px)'),
            ('large', 'Grande (60px)'),
            ('extra-large', 'Extra grande (80px)'),
        ],
        default='medium',
        required=False,
        help_text="Espaçamento vertical do componente",
        label="Espaçamento Vertical"
    )
    
    mostrar_decoracao = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Mostrar elementos decorativos (gradientes, sombras, etc.)",
        label="Mostrar Decoração"
    )
    
    animacao_entrada = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Ativar animação de entrada dos cards",
        label="Animação de Entrada"
    )

    class Meta:
        icon = 'timeline'
        label = 'Timeline Container'
        template = 'enap_designsystem/blocks/timeline_container.html'








class DepoimentosVideoSectionBlock(blocks.StructBlock):
    """
    Wrapper para seção de depoimentos com container e espaçamento
    """
    container_type = blocks.ChoiceBlock(
        label="Tipo de container",
        choices=[
            ('container', 'Container padrão'),
            ('container-fluid', 'Container fluido'),
            ('container-lg', 'Container grande')
        ],
        default='container'
    )
    
    background_color = blocks.ChoiceBlock(
        label="Cor de fundo",
        choices=[
            ('', 'Sem cor de fundo'),
            ('bg-light', 'Cinza claro'),
            ('bg-primary', 'Azul primário'),
            ('bg-secondary', 'Cinza secundário')
        ],
        default='bg-light',
        required=False
    )
    
    padding_top = blocks.ChoiceBlock(
        label="Espaçamento superior",
        choices=[
            ('py-3', 'Pequeno'),
            ('py-4', 'Médio'),
            ('py-5', 'Grande')
        ],
        default='py-4'
    )
    
    depoimentos_content = DepoimentosVideoListBlock(
        label="Conteúdo dos depoimentos"
    )

    class Meta:
        template = 'enap_designsystem/blocks/depoimentos_video_section.html'
        icon = 'doc-full'
        label = 'Seção de Depoimentos'

