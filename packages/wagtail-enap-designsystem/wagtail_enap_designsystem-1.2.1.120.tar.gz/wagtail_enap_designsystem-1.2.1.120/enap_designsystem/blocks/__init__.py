"""
Ponto de partida do módulo de blocos. Usado para limpar e organizar
os blocos em arquivos individuais baseados na proposta.
Mas fornece todos via o módulo "blocks"
"""

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks import StreamBlock
from .html_blocks import CarouselResponsivoSnippetBlock
from .layout_blocks import DepoimentosVideoSectionBlock
from .html_blocks import (
    SimpleDashboardChartBlock,
    SimpleKPICardBlock, 
    SimpleDashboardRowBlock,
    SimpleDashboardContainerBlock,
    HTMLCustomBlock,
    SuapCourseBlock,
    SuapEventsBlock,
    SuapCardCursoBlock,
    GaleriaImagensBlock,
    APISuapCourseBlock,
    APIRPSUltimaEdicaoBlock,
    APIRPSBuscaAcervoBlock,
    TimelineEtapaBlock,
    TimelineBlock,
    JobVacancyFilteredBlock,
    FormularioDinamicoBlock,
)

from .semana_blocks import (
    ImageBlock, ParticipanteBlock, StatBlock, GaleriaFotoBlock,
    FAQItemBlock, FAQTabBlock, AtividadeBlock, HospitalityCardBlock,
    VideoBlock, CertificadoBlock, NewsletterBlock, ContatoBlock, FooterBlock, BannerConcurso, MaterialApioBlock, SecaoPatrocinadoresBlock, SecaoApresentacaoBlock, SecaoCategoriasBlock, CronogramaBlock, SecaoPremiosBlock, SecaoFAQBlock, SecaoContatoBlock, MenuNavigationBlock, BannerResultadoBlock,
    PodcastSpotifyBlock,
    SecaoHeroBannerBlock,
    SecaoEstatisticasBlock,
    SecaoCardsBlock,
    SecaoTestemunhosBlock, SecaoTimelineBlock, GaleriaBlock, MenuNavigationBlock
)
from .html_blocks import OuvidoriaBlock
from .chatbot_blocks import ChatbotBlock
from .html_blocks import EnapSectionCarouselBlock
from .html_blocks import ProgramaCardsBlock
from .content_blocks import BreadcrumbBlock, AutoBreadcrumbBlock
from .layout_blocks import HeroBlock 
from .content_blocks import FormularioBlock
from .layout_blocks import GridBlock, TimelineContainerBlock
from .layout_blocks import DashboardGridWrapperBlock
from .layout_blocks import CardGridBlock
from .layout_blocks import EnapCardGridBlock
from .layout_blocks import EnapBannerBlock
from .layout_blocks import EnapFooterGridBlock
from .layout_blocks import EnapFooterSocialGridBlock
from .layout_blocks import EnapSectionBlock
from enap_designsystem.blocks.base_blocks import CarouselSlideBlock
from enap_designsystem.blocks.base_blocks import ButtonGroupBlock
from enap_designsystem.blocks.base_blocks import CarouselBlock
from .base_blocks import FormularioSnippetBlock, ButtonCenter

from .content_blocks import CardBlock
from .content_blocks import EnapBannerLogoBlock
from .content_blocks import EnapAccordionBlock
from .html_blocks import EnapCarouselImagesBlock
from .content_blocks import FeatureImageTextBlock
from .content_blocks import EnapFooterLinkBlock
from .content_blocks import EnapAccordionPanelBlock
from .content_blocks import EnapAccordionBlock
from .content_blocks import EnapNavbarLinkBlock
from .html_blocks import CourseIntroTopicsBlock
from .html_blocks import LegislacaoBlock
from .html_blocks import WhyChooseEnaptBlock
from .html_blocks import CourseFeatureBlock
from .html_blocks import CourseModulesBlock
from .html_blocks import ProcessoSeletivoBlock
from .html_blocks import TeamCarouselBlock
from .html_blocks import TestimonialsCarouselBlock
from .html_blocks import PreviewCoursesBlock
from .html_blocks import SectionCardTitleCenterBlock
from .html_blocks import SectionTabsCardsBlock
from .html_blocks import CTAImagemBlock
from .html_blocks import ContainerInfo
from .html_blocks import ContatoBlock
from .html_blocks import FormContato
from .html_blocks import SobreLinhas
from .html_blocks import EventoBlock
from .html_blocks import HeroAnimadaBlock
from .html_blocks import BannerSearchBlock
from .html_blocks import NavbarComponent
from .html_blocks import SecaoAdesaoBlock
from .html_blocks import TextoImagemBlock
from .html_blocks import CardCursoBlock
from .html_blocks import NavbarBlockv3
from .html_blocks import HeroBlockv3
from .html_blocks import AccordionItemBlock
from .html_blocks import AvisoBlock
from .html_blocks import GalleryModernBlock
from .html_blocks import TeamModern
from .html_blocks import CTA2Block
from .html_blocks import CarrosselCursosBlock
from .html_blocks import CitizenServerBlock
from .html_blocks import ServiceCardsBlock
from .html_blocks import FeatureListBlock
from .html_blocks import CarouselGreen
from .html_blocks import TopicLinksBlock
from .html_blocks import Banner_Image_cta
from .html_blocks import FeatureWithLinksBlock
from .html_blocks import QuoteBlockModern
from .html_blocks import BannerTopicsBlock
from .html_blocks import LocalizacaoBlock
from .html_blocks import CtaDestaqueBlock
from .html_blocks import ENAPNoticia
from .html_blocks import ENAPNoticiaImportada
from .html_blocks import HolofoteCarouselBlock
from .html_blocks import DestaqueMainTabBlock
from .html_blocks import DownloadBlock
from .html_blocks import ImageBlock
from .html_blocks import ImageLinkBlock
from .html_blocks import QuoteBlock
from .html_blocks import RichTextBlock
from .html_blocks import PageListBlock
from .html_blocks import NewsCarouselBlock
from .html_blocks import CoursesCarouselBlock
from .html_blocks import SuapCourseBlock
from .html_blocks import SuapEventsBlock
from .html_blocks import EventsCarouselBlock
from .html_blocks import DropdownBlock
from .html_blocks import ClientesBlock


from .html_blocks import ButtonBlock, ImageBlock, RichTextBlock, QuoteBlock
from .html_blocks import DownloadBlock, ImageLinkBlock, PageListBlock

# Depois: imports que dependem dos básicos
from .content_blocks import EnapCardBlock, CardBlock, BreadcrumbBlock

HTML_STREAMBLOCKS = [
    ("text", RichTextBlock(icon="cr-font")),
    ("button", ButtonBlock()),
    ("image", ImageBlock()),
    ("image_link", ImageLinkBlock()),
    (
        "html",
        blocks.RawHTMLBlock(
            icon="code",
            form_classname="monospace",
            label=_("HTML"),
        ),
    ),
    ("download", DownloadBlock()),
    ("quote", QuoteBlock()),
]


CONTENT_STREAMBLOCKS = HTML_STREAMBLOCKS + [
    ("accordion", EnapAccordionBlock()),
    ("card", CardBlock()),
    ("card2", EnapCardBlock()),

]

"""
Exemplo de estrutura no codered
    (
        "hero",
        HeroBlock(
            [
                ("row", GridBlock(CONTENT_STREAMBLOCKS)),
                (
                    "cardgrid",
                    CardGridBlock(
                        [
                            ("card", CardBlock()),
                        ]
                    ),
                ),
                (
                    "html",
                    blocks.RawHTMLBlock(
                        icon="code", form_classname="monospace", label=_("HTML")
                    ),
                ),
            ]
        ),
    ),
"""


# ===== 🎨 BANNERS E HEROES =====
class BannerStreamBlock(StreamBlock):
    """Componentes de Banners e Heroes"""
    
    enap_herobanner = EnapBannerBlock(label="🎯 Hero Banner ENAP")
    banner = EnapBannerBlock(label="🎨 Banner Padrão")
    banner_logo = EnapBannerLogoBlock(label="🏢 Banner com Logo")
    hero_banner = SecaoHeroBannerBlock(label="🚀 Hero Banner, Imagem e Fundo cor variavél")
    banner_search = BannerSearchBlock(label="🔍 Banner com Busca")
    bannertopics = BannerTopicsBlock(label="📑 Banner com Tópicos")
    banner_image_cta = Banner_Image_cta(label="🖼️ Banner Imagem + CTA")
    hero = HeroBlockv3(label="⭐ Hero Moderno")
    hero_animada = HeroAnimadaBlock(label="🎬 Hero Animado")

    class Meta:
        label = "🎨 Banners e Heroes"
        icon = "image"


# ===== 🖼️ GALERIAS E IMAGENS =====
class GalleryStreamBlock(StreamBlock):
    """Componentes de Galerias e Imagens"""
    
    galeria_imagens = GaleriaImagensBlock(label="🖼️ Galeria de Imagens")
    galeria_moderna = GalleryModernBlock(label="✨ Galeria Moderna")
    image = ImageBlock(label="📷 Imagem Simples")
    enap_carousel = EnapCarouselImagesBlock(label="🎠 Carrossel de Imagens")

    class Meta:
        label = "🖼️ Galerias e Imagens"
        icon = "image"


# ===== 🎠 CARROSSÉIS =====
class CarouselStreamBlock(StreamBlock):
    """Componentes de Carrosséis"""
    
    carousel_responsivo = CarouselResponsivoSnippetBlock(label="📱 Carrossel Responsivo")
    section_carousel = EnapSectionCarouselBlock(label="📋 Carrossel de Seção")
    carousel_option = CarouselSlideBlock(label="🎯 Slide de Carrossel")
    carousel = CarouselBlock(label="🎠 Carrossel Padrão")
    carousel_green = CarouselGreen(label="🟢 Carrossel Verde")
    carrossel_cursos = CarrosselCursosBlock(label="🎓 Carrossel de Cursos")
    team_carousel = TeamCarouselBlock(label="👥 Carrossel de Equipe")
    testimonials_carousel = TestimonialsCarouselBlock(label="💬 Carrossel de Depoimentos")
    courses_carousel = CoursesCarouselBlock(label="📚 Carrossel de Cursos")
    noticias_carousel = NewsCarouselBlock(label="📰 Carrossel de Notícias")
    eventos_carousel = EventsCarouselBlock(label="📅 Carrossel de Eventos")

    class Meta:
        label = "🎠 Carrosséis"
        icon = "arrows-up-down"


# ===== 📊 DASHBOARDS E MÉTRICAS =====
class DashboardStreamBlock(StreamBlock):
    """Componentes de Dashboard e KPIs"""
    
    dashboard_chart = SimpleDashboardChartBlock(label="📈 Gráfico Dashboard")
    kpi_card = SimpleKPICardBlock(label="📊 Cartão KPI")
    dashboard_row = SimpleDashboardRowBlock(label="📋 Linha Dashboard")
    dashboard_container = SimpleDashboardContainerBlock(label="📦 Container Dashboard")
    cpnu_dashboard = DestaqueMainTabBlock(label="⭐ Dashboard Principal")
    dashboard_section = DashboardGridWrapperBlock([
        ("dashboard_chart", SimpleDashboardChartBlock()),
        ("kpi_card", SimpleKPICardBlock()),
        ("dashboard_row", SimpleDashboardRowBlock()),
        ("dashboard_container", SimpleDashboardContainerBlock()),
        ("heading", blocks.CharBlock(template='blocks/heading.html')),
        ("paragraph", blocks.RichTextBlock(template='blocks/paragraph.html')),
    ], label="🎯 Seção Dashboard Completa")

    class Meta:
        label = "📊 Dashboards e Métricas"
        icon = "bars"


# ===== 📝 FORMULÁRIOS =====
class FormStreamBlock(StreamBlock):
    """Componentes de Formulários"""
    
    formulario_snippet = FormularioSnippetBlock(label="📋 Formulário Snippet")
    formulario = FormularioBlock(label="📝 Formulário Padrão")
    formulario_dinamico = FormularioDinamicoBlock(label="⚡ Formulário Dinâmico")
    form_contato = FormContato(label="📞 Formulário de Contato")
    ouvidoria = OuvidoriaBlock(label="👂 Ouvidoria")

    class Meta:
        label = "📝 Formulários"
        icon = "form"


# ===== 🎓 CURSOS E EDUCAÇÃO =====
class CourseStreamBlock(StreamBlock):
    """Componentes de Cursos e Educação"""
    
    suap_courses = SuapCourseBlock(label="🎓 Cursos SUAP")
    api_suap_courses = APISuapCourseBlock(label="🔗 API Cursos SUAP")
    suap_card_curso = SuapCardCursoBlock(label="🎯 Card Curso SUAP")
    feature_course = CourseFeatureBlock(label="⭐ Destaque do Curso")
    preview_courses = PreviewCoursesBlock(label="👀 Preview de Cursos")
    course_intro_topics = CourseIntroTopicsBlock(label="📑 Tópicos do Curso")
    feature_estrutura = CourseModulesBlock(label="📚 Módulos do Curso")
    card_curso = CardCursoBlock(label="🎴 Card de Curso")

    class Meta:
        label = "🎓 Cursos e Educação"
        icon = "doc-full"


# ===== 📅 EVENTOS E CRONOGRAMAS =====
class EventStreamBlock(StreamBlock):
    """Componentes de Eventos"""
    
    suap_events = SuapEventsBlock(label="📅 Eventos SUAP")
    evento = EventoBlock(label="🎉 Evento")
    cronograma = CronogramaBlock(label="⏰ Cronograma")
    timeline = TimelineBlock(label="📈 Timeline")
    timeline_container = TimelineContainerBlock(label="📦 Container Timeline")

    class Meta:
        label = "📅 Eventos e Cronogramas"
        icon = "date"


# ===== 🧭 NAVEGAÇÃO =====
class NavigationStreamBlock(StreamBlock):
    """Componentes de Navegação"""
    
    navbar = NavbarComponent(label="🧭 Navbar")
    navbarflutuante = NavbarBlockv3(label="🌊 Navbar Flutuante")
    breadcrumb = BreadcrumbBlock(label="🍞 Breadcrumb")
    auto_breadcrumb = AutoBreadcrumbBlock(label="🤖 Breadcrumb Automático")

    class Meta:
        label = "🧭 Navegação"
        icon = "bars"


# ===== 🔘 BOTÕES E CTAs =====
class ButtonStreamBlock(StreamBlock):
    """Componentes de Botões e CTAs"""
    
    buttoncenter = ButtonCenter(label="🎯 Botão Centralizado")
    button = ButtonBlock(label="🔘 Botão Padrão")
    button_group = ButtonGroupBlock(label="🔘🔘 Grupo de Botões")
    cta_destaque = CtaDestaqueBlock(label="⭐ CTA Destaque")
    cta_imagem = CTAImagemBlock(label="🖼️ CTA com Imagem")
    cta_2 = CTA2Block(label="🎯 CTA Versão 2")

    class Meta:
        label = "🔘 Botões e CTAs"
        icon = "radio-full"


# ===== 📰 CONTEÚDO E TEXTO =====
class ContentStreamBlock(StreamBlock):
    """Componentes de Conteúdo e Texto"""
    
    richtext = RichTextBlock(label="📝 Texto Rico")
    quote = QuoteBlock(label="💭 Citação")
    QuoteModern = QuoteBlockModern(label="✨ Citação Moderna")
    texto_imagem = TextoImagemBlock(label="📝🖼️ Texto + Imagem")
    enap_herofeature = FeatureImageTextBlock(label="🎯 Feature Texto + Imagem")
    feature_list = FeatureListBlock(label="📋 Lista de Features")
    feature_list_text = FeatureWithLinksBlock(label="🔗 Features com Links")
    html = HTMLCustomBlock(label="🔧 HTML Customizado")

    class Meta:
        label = "📰 Conteúdo e Texto"
        icon = "doc-full"


# ===== 📦 SEÇÕES E CONTAINERS =====
class SectionStreamBlock(StreamBlock):
    """Componentes de Seções e Containers"""
    
    section_card_title_center = SectionCardTitleCenterBlock(label="🎯 Seção Card Título Central")
    section_tabs_cards = SectionTabsCardsBlock(label="📑 Seção Tabs com Cards")
    container_info = ContainerInfo(label="📦 Container de Informações")
    sobre_linhas = SobreLinhas(label="📏 Sobre Linhas")
    grid = GridBlock(CONTENT_STREAMBLOCKS + HTML_STREAMBLOCKS, label="🔲 Grid")
    secao_adesao = SecaoAdesaoBlock(label="📝 Seção de Adesão")
    estatisticas = SecaoEstatisticasBlock(label="📊 Seção Estatísticas")
    patrocinadores = SecaoPatrocinadoresBlock(label="🏢 Seção Patrocinadores")

    class Meta:
        label = "📦 Seções e Containers"
        icon = "group"


# ===== 🎴 CARDS =====
class CardStreamBlock(StreamBlock):
    """Componentes de Cards"""
    
    enap_card = EnapCardBlock(label="🎴 Card ENAP")
    enap_cardgrid = EnapCardGridBlock([
        ("enap_card", EnapCardBlock()),
        ("card_curso", CardCursoBlock()),
    ], label="🎴🎴 Grid de Cards ENAP")
    service_cards = ServiceCardsBlock(label="⚙️ Cards de Serviços")
    programa_cards = ProgramaCardsBlock(label="📋 Cards de Programa")

    class Meta:
        label = "🎴 Cards"
        icon = "snippet"


# ===== 🎮 INTERATIVOS =====
class InteractiveStreamBlock(StreamBlock):
    """Componentes Interativos"""
    
    accordion = EnapAccordionBlock(label="📂 Accordion")
    enap_accordion = EnapAccordionBlock(label="📂 Accordion ENAP")
    dropdown = DropdownBlock(label="⬇️ Dropdown")
    chatbot_ia = ChatbotBlock(label="🤖 Chatbot IA")

    class Meta:
        label = "🎮 Interativos"
        icon = "cogs"


# ===== 🎬 MÍDIA =====
class MediaStreamBlock(StreamBlock):
    """Componentes de Mídia"""
    
    video = VideoBlock(label="📹 Vídeo")
    depoimentos_video_section = DepoimentosVideoSectionBlock(label="🎬 Seção Vídeo Depoimentos")
    podcast_spotify = PodcastSpotifyBlock(label="🎧 Podcast Spotify")

    class Meta:
        label = "🎬 Mídia"
        icon = "media"


# ===== ⚙️ ESPECIALIDADES =====
class SpecialtyStreamBlock(StreamBlock):
    """Componentes Especializados"""
    
    clientes = ClientesBlock(label="🏢 Clientes")
    edital = LegislacaoBlock(label="📜 Edital/Legislação")
    loc = LocalizacaoBlock(label="📍 Localização")
    topic_links = TopicLinksBlock(label="🔗 Links de Tópicos")
    citizen_server = CitizenServerBlock(label="👥 Cidadão Servidor")
    aviso = AvisoBlock(label="⚠️ Aviso")
    team_moderna = TeamModern(label="👥 Equipe Moderna")
    why_choose = WhyChooseEnaptBlock(label="❓ Por que Escolher")
    feature_processo_seletivo = ProcessoSeletivoBlock(label="📋 Processo Seletivo")
    job_vacancy_filtered = JobVacancyFilteredBlock(label="💼 Vagas Filtradas")
    download = DownloadBlock(label="⬇️ Download")
    newsletter = NewsletterBlock(label="📧 Newsletter")
    contato = ContatoBlock(label="📞 Contato")
    contato_secao = SecaoContatoBlock(label="📞 Seção de Contato")
    api_rps_ultima = APIRPSUltimaEdicaoBlock(label="API RPS Última Edição")
    api_rps_busca = APIRPSBuscaAcervoBlock(label="API RPS Busca Acervo")

    class Meta:
        label = "⚙️ Especialidades"
        icon = "cogs"


# ===== 📦 LAYOUT PRINCIPAL ORGANIZADO =====
LAYOUT_STREAMBLOCKS = [
    # ===== CATEGORIAS ORGANIZADAS =====
    ("banners", BannerStreamBlock()),
    ("galerias", GalleryStreamBlock()),
    ("carousels", CarouselStreamBlock()),
    ("dashboards", DashboardStreamBlock()),
    ("formularios", FormStreamBlock()),
    ("cursos", CourseStreamBlock()),
    ("eventos", EventStreamBlock()),
    ("navegacao", NavigationStreamBlock()),
    ('menus', MenuNavigationBlock()),
    ("botoes", ButtonStreamBlock()),
    ("conteudo", ContentStreamBlock()),
    ("secoes", SectionStreamBlock()),
    ("cards", CardStreamBlock()),
    ("interativos", InteractiveStreamBlock()),
    ("midia", MediaStreamBlock()),
    ("especialidades", SpecialtyStreamBlock()),
    ("banner_concurso", BannerConcurso()),
    ("patrocinadores", SecaoPatrocinadoresBlock()),
    
    # ===== SEÇÃO COMPLEXA (MANTIDA PARA COMPATIBILIDADE) =====
    ("enap_section", EnapSectionBlock([
         ("button", ButtonBlock()),
        ("image", ImageBlock()),
        ("richtext", RichTextBlock()),
        ("quote", QuoteBlock()),
        ('menus', MenuNavigationBlock()),
        ('buttoncenter', ButtonCenter()),
        ("enap_accordion", EnapAccordionBlock()),
        ("timeline", TimelineBlock()),
        ("timeline_container", TimelineContainerBlock()),
        ("cronograma", CronogramaBlock()),
        ("job_vacancy_filtered", JobVacancyFilteredBlock()),
        ("preview_courses", PreviewCoursesBlock()),
        ("api_suap_courses", APISuapCourseBlock()),
        ("api_rps_ultima", APIRPSUltimaEdicaoBlock()),
        ("api_rps_busca", APIRPSBuscaAcervoBlock()),
        ("noticias_carousel", NewsCarouselBlock()),
        ("enap_herofeature", FeatureImageTextBlock()),
        ('feature_course', CourseFeatureBlock()),
        ('feature_estrutura', CourseModulesBlock()),
        ("section_card_title_center", SectionCardTitleCenterBlock()),
        ("section_tabs_cards", SectionTabsCardsBlock()),
        ('cta_imagem', CTAImagemBlock()),
        ('container_info', ContainerInfo()),
        ('sobre_linhas', SobreLinhas()),
        ('contato', ContatoBlock()),
        ('form_contato', FormContato()),
        ('evento', EventoBlock()),
        ('hero_animada', HeroAnimadaBlock()),
        ('banner_search', BannerSearchBlock()),
        ('texto_imagem', TextoImagemBlock()),
        ('hero', HeroBlockv3()),
        ('accordion', AccordionItemBlock()),
        ('aviso', AvisoBlock()),
        ('galeria_moderna', GalleryModernBlock()),
        ("enap_cardgrid", EnapCardGridBlock([
            ("enap_card", EnapCardBlock()),
            ('card_curso', CardCursoBlock()),
            ("richtext", RichTextBlock()),
            ("enap_accordion", EnapAccordionBlock()),
        
        ("richtext", RichTextBlock()),
        ("button", ButtonBlock()),
        ("image", ImageBlock()),
        ("quote", QuoteBlock()),
        ('buttoncenter', ButtonCenter()),
        ("timeline", TimelineBlock()),
        ("timeline_container", TimelineContainerBlock()),
        ("cronograma", CronogramaBlock()),
        ("job_vacancy_filtered", JobVacancyFilteredBlock()),
        ("preview_courses", PreviewCoursesBlock()),
        ("api_suap_courses", APISuapCourseBlock()),
        ("api_rps_ultima", APIRPSUltimaEdicaoBlock()),
        ("api_rps_busca", APIRPSBuscaAcervoBlock()),
        ("noticias_carousel", NewsCarouselBlock()),
        ("enap_herofeature", FeatureImageTextBlock()),
        ('feature_course', CourseFeatureBlock()),
        ('feature_estrutura', CourseModulesBlock()),
        ("section_card_title_center", SectionCardTitleCenterBlock()),
        ("section_tabs_cards", SectionTabsCardsBlock()),
        ('cta_imagem', CTAImagemBlock()),
        ('container_info', ContainerInfo()),
        ('sobre_linhas', SobreLinhas()),
        ('contato', ContatoBlock()),
        ('form_contato', FormContato()),
        ('evento', EventoBlock()),
        ('hero_animada', HeroAnimadaBlock()),
        ('banner_search', BannerSearchBlock()),
        ('texto_imagem', TextoImagemBlock()),
        ('hero', HeroBlockv3()),
        ('accordion', AccordionItemBlock()),
        ('aviso', AvisoBlock()),
        ('galeria_moderna', GalleryModernBlock()),
        ('team_moderna', TeamModern()),
        ('cta_2', CTA2Block()),
        ("navbar", NavbarComponent()),
        ("secao_adesao", SecaoAdesaoBlock()),
        ("feature_list", FeatureListBlock()),
        ("feature_list_text", FeatureWithLinksBlock()),
        ("service_cards", ServiceCardsBlock()),
        ("topic_links", TopicLinksBlock()),
        ("citizen_server", CitizenServerBlock()),
        ("carrossel_cursos", CarrosselCursosBlock()),
        ("section_carousel", EnapSectionCarouselBlock()),
        ("programa_cards", ProgramaCardsBlock()),
        ("accordion", EnapAccordionBlock()),
        ("cta_destaque", CtaDestaqueBlock()),
        ("loc", LocalizacaoBlock()),
        ("carousel", CarouselBlock()),
        ("navbarflutuante", NavbarBlockv3()),
        ("bannertopics", BannerTopicsBlock()),
        ("QuoteModern", QuoteBlockModern()),
        ("carousel_green", CarouselGreen()),
        ("banner_image_cta", Banner_Image_cta()),
        ("feature_processo_seletivo", ProcessoSeletivoBlock()),
        ("team_carousel", TeamCarouselBlock()),
        ("testimonials_carousel", TestimonialsCarouselBlock()),
        ("why_choose", WhyChooseEnaptBlock()),
        ("button_group", ButtonGroupBlock()),
        ("dropdown", DropdownBlock()),
        ("courses_carousel", CoursesCarouselBlock()),
        ("course_intro_topics", CourseIntroTopicsBlock()),
        ("breadcrumb", BreadcrumbBlock()),
        ("auto_breadcrumb", AutoBreadcrumbBlock()),
        ("hero_banner", SecaoHeroBannerBlock()),
        ("banner_resultado", BannerResultadoBlock()),
        ("video", VideoBlock()),
        ("estatisticas", SecaoEstatisticasBlock()),
        ("newsletter", NewsletterBlock()),
        ("podcast_spotify", PodcastSpotifyBlock()),
        ("patrocinadores", SecaoPatrocinadoresBlock()),
        ("carousel_option", CarouselSlideBlock()),
        ("download", DownloadBlock()),
        ("eventos_carousel", EventsCarouselBlock()),
        ("html", HTMLCustomBlock()),
        ("grid", GridBlock(CONTENT_STREAMBLOCKS + HTML_STREAMBLOCKS)),
        ("edital", LegislacaoBlock()),
        ("ouvidoria", OuvidoriaBlock()),
        ("clientes", ClientesBlock()),
        ("depoimentos_video_section", DepoimentosVideoSectionBlock()),
        ("banner_logo", EnapBannerLogoBlock()),
        ("suap_events", SuapEventsBlock()),
        ("suap_card_curso", SuapCardCursoBlock()),
        ("galeria_imagens", GaleriaImagensBlock()),
        ("carousel_responsivo", CarouselResponsivoSnippetBlock()),
        ("suap_courses", SuapCourseBlock()),
        ("banner", EnapBannerBlock()),
        ("chatbot_ia", ChatbotBlock()),
        ("formulario_dinamico", FormularioDinamicoBlock()),
        ("formulario_snippet", FormularioSnippetBlock()),
        ("formulario", FormularioBlock()),
        ("dashboard_chart", SimpleDashboardChartBlock()),
        ("kpi_card", SimpleKPICardBlock()),
        ("dashboard_row", SimpleDashboardRowBlock()),
        ("dashboard_container", SimpleDashboardContainerBlock()),
        ("dashboard_section", DashboardGridWrapperBlock([
            ("dashboard_chart", SimpleDashboardChartBlock()),
            ("kpi_card", SimpleKPICardBlock()),
            ("dashboard_row", SimpleDashboardRowBlock()),
            ("dashboard_container", SimpleDashboardContainerBlock()),
            ("heading", blocks.CharBlock(template='blocks/heading.html')),
            ("paragraph", blocks.RichTextBlock(template='blocks/paragraph.html')),
        ])),
        ])),
    ], required=False, blank=True, label="🏗️ Seção ENAP Completa")),

    ("enap_accordion", EnapAccordionBlock()),
        ("richtext", RichTextBlock()),
        ("button", ButtonBlock()),
        ("image", ImageBlock()),
        ("quote", QuoteBlock()),
        ('buttoncenter', ButtonCenter()),
        ("timeline", TimelineBlock()),
        ("timeline_container", TimelineContainerBlock()),
        ("cronograma", CronogramaBlock()),
        ("job_vacancy_filtered", JobVacancyFilteredBlock()),
        ("preview_courses", PreviewCoursesBlock()),
        ("api_suap_courses", APISuapCourseBlock()),
        ("api_rps_ultima", APIRPSUltimaEdicaoBlock()),
        ("api_rps_busca", APIRPSBuscaAcervoBlock()),
        ("noticias_carousel", NewsCarouselBlock()),
        ("enap_herofeature", FeatureImageTextBlock()),
        ('feature_course', CourseFeatureBlock()),
        ('feature_estrutura', CourseModulesBlock()),
        ("section_card_title_center", SectionCardTitleCenterBlock()),
        ("section_tabs_cards", SectionTabsCardsBlock()),
        ('cta_imagem', CTAImagemBlock()),
        ('container_info', ContainerInfo()),
        ('sobre_linhas', SobreLinhas()),
        ('contato', ContatoBlock()),
        ('form_contato', FormContato()),
        ('evento', EventoBlock()),
        ('hero_animada', HeroAnimadaBlock()),
        ('banner_search', BannerSearchBlock()),
        ('texto_imagem', TextoImagemBlock()),
        ('hero', HeroBlockv3()),
        ('accordion', AccordionItemBlock()),
        ('aviso', AvisoBlock()),
        ('galeria_moderna', GalleryModernBlock()),
        ('team_moderna', TeamModern()),
        ('cta_2', CTA2Block()),
        ("navbar", NavbarComponent()),
        ("secao_adesao", SecaoAdesaoBlock()),
        ("feature_list", FeatureListBlock()),
        ("feature_list_text", FeatureWithLinksBlock()),
        ("service_cards", ServiceCardsBlock()),
        ("topic_links", TopicLinksBlock()),
        ("citizen_server", CitizenServerBlock()),
        ("carrossel_cursos", CarrosselCursosBlock()),
        ("section_carousel", EnapSectionCarouselBlock()),
        ("programa_cards", ProgramaCardsBlock()),
        ("accordion", EnapAccordionBlock()),
        ("cta_destaque", CtaDestaqueBlock()),
        ("loc", LocalizacaoBlock()),
        ("carousel", CarouselBlock()),
        ("navbarflutuante", NavbarBlockv3()),
        ("bannertopics", BannerTopicsBlock()),
        ("QuoteModern", QuoteBlockModern()),
        ("carousel_green", CarouselGreen()),
        ("banner_image_cta", Banner_Image_cta()),
        ("feature_processo_seletivo", ProcessoSeletivoBlock()),
        ("team_carousel", TeamCarouselBlock()),
        ("testimonials_carousel", TestimonialsCarouselBlock()),
        ("why_choose", WhyChooseEnaptBlock()),
        ("button_group", ButtonGroupBlock()),
        ("dropdown", DropdownBlock()),
        ("courses_carousel", CoursesCarouselBlock()),
        ("course_intro_topics", CourseIntroTopicsBlock()),
        ("breadcrumb", BreadcrumbBlock()),
        ("auto_breadcrumb", AutoBreadcrumbBlock()),
        ("hero_banner", SecaoHeroBannerBlock()),
        ("banner_resultado", BannerResultadoBlock()),
        ("video", VideoBlock()),
        ("estatisticas", SecaoEstatisticasBlock()),
        ("newsletter", NewsletterBlock()),
        ("podcast_spotify", PodcastSpotifyBlock()),
        ("patrocinadores", SecaoPatrocinadoresBlock()),
        ("carousel_option", CarouselSlideBlock()),
        ("download", DownloadBlock()),
        ("eventos_carousel", EventsCarouselBlock()),
        ("html", HTMLCustomBlock()),
        ("grid", GridBlock(CONTENT_STREAMBLOCKS + HTML_STREAMBLOCKS)),
        ("edital", LegislacaoBlock()),
        ("ouvidoria", OuvidoriaBlock()),
        ("clientes", ClientesBlock()),
        ("depoimentos_video_section", DepoimentosVideoSectionBlock()),
        ("banner_logo", EnapBannerLogoBlock()),
        ("suap_events", SuapEventsBlock()),
        ("suap_card_curso", SuapCardCursoBlock()),
        ("galeria_imagens", GaleriaImagensBlock()),
        ("carousel_responsivo", CarouselResponsivoSnippetBlock()),
        ("suap_courses", SuapCourseBlock()),
        ("banner", EnapBannerBlock()),
        ("chatbot_ia", ChatbotBlock()),
        ("formulario_dinamico", FormularioDinamicoBlock()),
        ("formulario_snippet", FormularioSnippetBlock()),
        ("formulario", FormularioBlock()),
        ("dashboard_chart", SimpleDashboardChartBlock()),
        ("kpi_card", SimpleKPICardBlock()),
        ("dashboard_row", SimpleDashboardRowBlock()),
        ("dashboard_container", SimpleDashboardContainerBlock()),
        ("dashboard_section", DashboardGridWrapperBlock([
            ("dashboard_chart", SimpleDashboardChartBlock()),
            ("kpi_card", SimpleKPICardBlock()),
            ("dashboard_row", SimpleDashboardRowBlock()),
            ("dashboard_container", SimpleDashboardContainerBlock()),
            ("heading", blocks.CharBlock(template='blocks/heading.html')),
            ("paragraph", blocks.RichTextBlock(template='blocks/paragraph.html')),
        ])),
]



DYNAMIC_CARD_STREAMBLOCKS = [
    (
        "enap_section", EnapSectionBlock([
            ("enap_cardgrid", EnapCardGridBlock([
                ("enap_card", EnapCardBlock()),
            ])),
            ('holofote_carousel', HolofoteCarouselBlock()),
        ])
    ),

    ("page_list", PageListBlock()),
]


CARD_CARDS_STREAMBLOCKS = [
    (
        "enap_section", EnapSectionBlock([
            ("enap_cardgrid", EnapCardGridBlock([
                ("enap_card", EnapCardBlock()),
                ("richtext", RichTextBlock()),
                ("button", ButtonBlock()),
                ("image", ImageBlock()),
                ("quote", QuoteBlock()),
                ('buttoncenter', ButtonCenter()),
                ]))
        ])
    )
]




SEMANA_INOVACAO_STREAMBLOCKS = [
    
    ("hero_banner", SecaoHeroBannerBlock()),
    ('galeria_fotos', GaleriaBlock()),
    ("banner_concurso", BannerConcurso()),
    ("secao_apresentacao", SecaoApresentacaoBlock()),
    ("secao_categorias", SecaoCategoriasBlock()),
    ("material_apoio", MaterialApioBlock()),
    ("cronograma", CronogramaBlock()),
    ("secao_premios", SecaoPremiosBlock()),
    ("secao_faq", SecaoFAQBlock()),
    ("secao_contato", SecaoContatoBlock()),
    ("banner_resultado", BannerResultadoBlock()),
    ("podcast_spotify", PodcastSpotifyBlock()),
    ("secao_hero_banner", SecaoHeroBannerBlock()),
    ("secao_apresentacao", SecaoApresentacaoBlock()),
    ("secao_cards", SecaoCardsBlock()),
    ("secao_testemunhos", SecaoTestemunhosBlock()),
    ("secao_estatisticas", SecaoEstatisticasBlock()),
    ("secao_timeline", SecaoTimelineBlock()),
    ("secao_contato", SecaoContatoBlock()),
    ("newsletter", NewsletterBlock()),
    ("hero_banner", SecaoHeroBannerBlock()),
    ("cronograma", CronogramaBlock()),
    ("participantes", ParticipanteBlock()),
    ("atividades", AtividadeBlock()),
    ("hospitality", HospitalityCardBlock()),
    ("galeria", GaleriaFotoBlock()),
    ("certificado", CertificadoBlock()),
    ("image_block", ImageBlock()),
    ("participante", ParticipanteBlock()),
    ("stat_block", StatBlock()),
    ("galeria_foto", GaleriaFotoBlock()),
    ("video_block", VideoBlock()),
    ("certificado", CertificadoBlock()),
    ("newsletter", NewsletterBlock()),
    ("contato", ContatoBlock()),
    ("footer_block", FooterBlock()),
    
    # =============================================================================
    # COMPONENTES DE FAQ E NAVEGAÇÃO
    # =============================================================================
    ("faq_item", FAQItemBlock()),
    ("faq_tab", FAQTabBlock()),
    ("menu_navigation", MenuNavigationBlock()),
    
    # =============================================================================
    # COMPONENTES DE ATIVIDADES E EVENTOS
    # =============================================================================
    ("atividade", AtividadeBlock()),
    ("hospitality_card", HospitalityCardBlock()),
    
    # =============================================================================
    # SEMANA DE INOVAÇÃO - COMPONENTES ESPECIALIZADOS
    # =============================================================================
    ("banner_concurso", BannerConcurso()),
    ("material_apoio", MaterialApioBlock()),
    ("secao_patrocinadores", SecaoPatrocinadoresBlock()),
    ("secao_apresentacao", SecaoApresentacaoBlock()),
    ("secao_categorias", SecaoCategoriasBlock()),
    ("cronograma", CronogramaBlock()),
    ("secao_premios", SecaoPremiosBlock()),
    ("secao_faq", SecaoFAQBlock()),
    ("secao_contato", SecaoContatoBlock()),
    ("banner_resultado", BannerResultadoBlock()),
    ("podcast_spotify", PodcastSpotifyBlock()),
    
    # =============================================================================
    # COMPONENTES DE LAYOUT E ORGANIZAÇÃO
    # =============================================================================
    ("secao_hero_banner", SecaoHeroBannerBlock()),
    ("secao_estatisticas", SecaoEstatisticasBlock()),
    ("secao_cards", SecaoCardsBlock()),
    ("secao_testemunhos", SecaoTestemunhosBlock()),
    ("secao_timeline", SecaoTimelineBlock()),
    
    # =============================================================================
    # COMPONENTES PARA SNIPPETS E REUTILIZAÇÃO
    # =============================================================================
    # Nota: Estes são snippets registrados, mas podem ser usados em StreamFields
    # através de SnippetChooserBlock quando necessário
    
    # =============================================================================
    # SEÇÃO EXEMPLO DE USO ANINHADO
    # =============================================================================
    (
        "enap_section", 
        EnapSectionBlock([
            ("enap_cardgrid", EnapCardGridBlock([
                ("enap_card", EnapCardBlock()),
                ("participante_card", ParticipanteBlock()),
                ("stat_card", StatBlock()),
                ("hospitality_card", HospitalityCardBlock()),
            ]))
        ])
    ),
    
    # =============================================================================
    # COMPONENTES DE ALTA COMPLEXIDADE
    # =============================================================================
    (
        "semana_inovacao_completa",
        SecaoHeroBannerBlock()  # Pode conter outros blocks aninhados
    ),
    
    (
        "material_apoio_completo",
        MaterialApioBlock()  # Com botões e configurações avançadas
    ),
    
    (
        "banner_resultado_completo", 
        BannerResultadoBlock()  # Com StreamField de botões flexíveis
    ),
    
    # =============================================================================
    # COMPONENTES PARA DIFERENTES CONTEXTOS
    # =============================================================================
    
    # Para páginas de eventos
    ("cronograma_evento", CronogramaBlock()),
    ("secao_premios_evento", SecaoPremiosBlock()),
    
    # Para páginas institucionais
    ("secao_apresentacao_institucional", SecaoApresentacaoBlock()),
    ("secao_testemunhos_institucional", SecaoTestemunhosBlock()),
    
    # Para páginas de conteúdo
    ("secao_cards_conteudo", SecaoCardsBlock()),
    ("secao_timeline_conteudo", SecaoTimelineBlock()),
    
    # Para podcasts e mídia
    ("podcast_spotify_completo", PodcastSpotifyBlock()),
    ("video_completo", VideoBlock()),
    
    # =============================================================================
    # COMPONENTES DE FORMULÁRIOS E INTERAÇÃO
    # =============================================================================
    ("formulario_contato", SecaoContatoBlock()),
    ("newsletter_inscricao", NewsletterBlock()),
    
    # =============================================================================
    # COMPONENTES DE BRANDING E IDENTIDADE
    # =============================================================================
    ("banner_branded", BannerConcurso()),
    ("secao_patrocinadores_branded", SecaoPatrocinadoresBlock()),
    
    # =============================================================================
    # COMPONENTES PARA DIFERENTES TIPOS DE PÁGINA
    # =============================================================================
    
    # Para home pages
    ("hero_home", SecaoHeroBannerBlock()),
    ("estatisticas_home", SecaoEstatisticasBlock()),
    ("testemunhos_home", SecaoTestemunhosBlock()),
    
    # Para páginas de sobre
    ("apresentacao_sobre", SecaoApresentacaoBlock()),
    ("timeline_sobre", SecaoTimelineBlock()),
    
    # Para páginas de FAQ
    ("faq_completo", SecaoFAQBlock()),
    ("faq_simples", FAQTabBlock()),
    
    # Para páginas de contato
    ("contato_completo", SecaoContatoBlock()),
    ("contato_simples", ContatoBlock()),
]
