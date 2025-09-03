
from django.utils.translation import gettext_lazy as _
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail import blocks
import uuid 
from types import SimpleNamespace
from wagtail import blocks
from wagtail.fields import StreamField
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.utils import timezone
from wagtail.fields import RichTextField
from enap_designsystem.blocks.base_blocks import CarouselBlock
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index
from wagtail import blocks
from datetime import datetime, date, time
import warnings
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import StructBlock, CharBlock, TextBlock, URLBlock, ListBlock, BooleanBlock, ChoiceBlock, StreamBlock, IntegerBlock
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import StructBlock, CharBlock, RichTextBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images import get_image_model_string
from django.utils.html import strip_tags
import re
import requests
from .base_blocks import BaseBlock
from .base_blocks import BaseLinkBlock
from .base_blocks import ButtonMixin
from .base_blocks import CoderedAdvTrackingSettings
from .base_blocks import LinkStructValue
from .form import BASE_FORM_FIELD_BLOCKS
from .base_blocks import BaseBlock, ButtonMixin, BaseLinkBlock, LinkStructValue, CoderedAdvTrackingSettings
from wagtail.blocks import PageChooserBlock, CharBlock, StructBlock
from wagtail.snippets.blocks import SnippetChooserBlock

BRAND_COLOR_CHOICES = [
    ('#024248', 'Verde ENAP (#024248)'),
    ('#007D7A', 'Verde Link ENAP (#007D7A)'),
    ('#AD6BFC', 'Roxo Gnova (#AD6BFC)'),
    ('#B396FC', 'Roxo Claro Gnova (#B396FC)'),
    ('#FFFFFF', 'Branco (#FFFFFF)'),
]

ENAP_GREEN_COLORS = [
    ('#02333A', 'Verde ENAP 100 (#02333A)'),
    ('#024248', 'Verde ENAP 90 (#024248)'),
    ('#025257', 'Verde ENAP 80 (#025257)'),
    ('#006969', 'Verde ENAP 70 (#006969)'),
    ('#10A39E', 'Verde ENAP 50 (#10A39E)'),
    ('#30BFBC', 'Verde ENAP 40 (#30BFBC)'),
    ('#70E0DF', 'Verde ENAP 30 (#70E0DF)'),
    ('#AFF0ED', 'Verde ENAP 20 (#AFF0ED)'),
    ('#D6F9F8', 'Verde ENAP 10 (#D6F9F8)'),
    ('#FFFFFF', 'Branco (#FFFFFF)'),
    ('#F8F9FA', 'Cinza Claro (#F8F9FA)'),
    ('#E9ECEF', 'Cinza Médio (#E9ECEF)'),
]

BACKGROUND_COLOR_CHOICES = [
    ('#FFFFFF', 'Branco (#FFFFFF)'),
    ('#F8F9FA', 'Cinza Claro (#F8F9FA)'),
    ('#000000', 'Preto (#000000)'),
    ('#FFFFFF', 'Branco (#FFFFFF)'),
] + BRAND_COLOR_CHOICES


from .semana_blocks import (
    BRAND_INOVACAO_CHOICES, 
    BRAND_TEXTS_CHOICES,
    BRAND_BG_CHOICES, 
    BRAND_BUTTON_CHOICES, 
    BRAND_HOVER_CHOICES
)

GRADIENT_COLOR_CHOICES = [
    ('enap-green', 'Verde ENAP'),
    ('enap-link', 'Verde Link ENAP'),
    ('gnova-purple', 'Roxo Gnova'),
    ('gnova-light', 'Roxo Claro Gnova'),
    ('blue', 'Azul'),
    ('red', 'Vermelho'),
    ('orange', 'Laranja'),
    ('emerald', 'Verde Esmeralda'),
    ('#FFFFFF', 'Branco (#FFFFFF)'),
]

# Cores para badges e botões
ACCENT_COLOR_CHOICES = [
    ('enap-green', 'Verde ENAP'),
    ('enap-link', 'Verde Link ENAP'), 
    ('enap-60', 'Verde ENAP 60 (#007D7A)'),
    ('enap-90', 'Verde ENAP 90 (#024248)'),
    ('enap-cinza', 'ENAP Cinza (#F5F7FA)'),
    ('gnova-purple', 'Roxo Gnova'),
    ('gnova-light', 'Roxo Claro Gnova'),
    ('gnova', 'Gnova (#AD6BFC)'),
    ('purple', 'Roxo'),
    ('#FFFFFF', 'Branco (#FFFFFF)'),
]


FONTAWESOME_ICON_CHOICES = [
    ('', 'Sem ícone'),
    ('fa-solid fa-1', '1 (Número)'),
    ('fa-solid fa-2', '2 (Número)'),
    ('fa-solid fa-3', '3 (Número)'),
    ('fa-solid fa-4', '4 (Número)'),
    ('fa-solid fa-5', '5 (Número)'),
    ('fa-solid fa-clipboard', 'Prancheta'),
    ('fa-solid fa-file-lines', 'Documento'),
    ('fa-solid fa-graduation-cap', 'Formatura'),
    ('fa-solid fa-book', 'Livro'),
    ('fa-solid fa-user-graduate', 'Estudante'),
    ('fa-solid fa-award', 'Prêmio'),
    ('fa-solid fa-certificate', 'Certificado'),
    ('fa-solid fa-trophy', 'Troféu'),
    ('fa-solid fa-star', 'Estrela'),
    ('fa-solid fa-check-circle', 'Check'),
    ('fa-solid fa-exclamation-triangle', 'Aviso'),
    ('fa-solid fa-info-circle', 'Informação'),
    ('fa-solid fa-calendar', 'Calendário'),
    ('fa-solid fa-clock', 'Relógio'),
    ('fa-solid fa-users', 'Usuários'),
    ('fa-solid fa-user', 'Usuário'),
    ('fa-solid fa-cog', 'Configuração'),
    ('fa-solid fa-chart-bar', 'Gráfico'),
    ('fa-solid fa-briefcase', 'Maleta'),
    ('fa-solid fa-building', 'Prédio'),
    ('fa-solid fa-home', 'Casa'),
    ('fa-solid fa-envelope', 'Email'),
    ('fa-solid fa-phone', 'Telefone'),
    ('fa-solid fa-map-marker-alt', 'Localização'),
    ('fa-solid fa-download', 'Download'),
    ('fa-solid fa-upload', 'Upload'),
    ('fa-solid fa-search', 'Busca'),
    ('fa-solid fa-heart', 'Coração'),
    ('fa-solid fa-thumbs-up', 'Like'),
    ('fa-solid fa-rocket', 'Foguete'),
    ('fa-solid fa-lightbulb', 'Lâmpada'),
    ('fa-solid fa-target', 'Alvo'),
]

class ButtonBlock(ButtonMixin, BaseLinkBlock):
    """
    A link styled as a button.
    """
    
    type_class = blocks.ChoiceBlock(
		choices=[
			('primary', 'Tipo primário'),
			('secondary', 'Tipo secundário'),
			('terciary', 'Tipo terciário'),
		],
		default='primary',
		help_text="Escolha o tipo do botão",
		label="Tipo de botão"
	)

    size_class = blocks.ChoiceBlock(
		choices=[
			('small', 'Pequeno'),
			('medium', 'Médio'),
			('large', 'Grande'),
			('extra-large', 'Extra grande'),
		],
		default='small',
		help_text="Escolha o tamanho do botão",
		label="Tamanho"
	)

    icone_bool = blocks.BooleanBlock(
        required=False,
        label=_("Icone"),
    )


    icone_posicao = blocks.ChoiceBlock(
        choices=[
            ('antes', 'Antes do texto'),
            ('depois', 'Depois do texto'),
        ],
        default='depois',
        help_text="Escolha onde posicionar o ícone",
        label="Posição do Ícone"
    )

    # Tentando remover campos herdados do codered
    button_style = None
    button_size = None
    page = None
    document = None
    downloadable_file = None
    class Meta:
        template = "enap_designsystem/blocks/button_block.html"
        icon = "cr-hand-pointer-o"
        label = _("Button Link")
        value_class = LinkStructValue

class DownloadBlock(ButtonMixin, BaseBlock):
    """
    Link to a file that can be downloaded.
    """

    downloadable_file = DocumentChooserBlock(
        required=False,
        label=_("Document link"),
    )

    class Meta:
        template = "enap_designsystem/blocks/download_block.html"
        icon = "download"
        label = _("Download")
    
class ImageBlock(BaseBlock):
    """
    An <img>, by default styled responsively to fill its container.
    """

    image = ImageChooserBlock(
        label=_("Image"),
    )

    class Meta:
        template = "coderedcms/blocks/image_block.html"
        icon = "image"
        label = _("Image")

class ImageLinkBlock(BaseLinkBlock):
    """
    An <a> with an image inside it, instead of text.
    """

    image = ImageChooserBlock(
        label=_("Image"),
    )
    alt_text = blocks.CharBlock(
        max_length=255,
        required=True,
        help_text=_("Alternate text to show if the image doesn’t load"),
    )

    class Meta:
        template = "coderedcms/blocks/image_link_block.html"
        icon = "image"
        label = _("Image Link")
        value_class = LinkStructValue

class QuoteBlock(BaseBlock):
    """
    A <blockquote>.
    """

    text = blocks.TextBlock(
        required=True,
        rows=4,
        label=_("Quote Text"),
    )
    author = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Author"),
    )

    class Meta:
        template = "coderedcms/blocks/quote_block.html"
        icon = "openquote"
        label = _("Quote")


class RichTextBlock(blocks.RichTextBlock):
    class Meta:
        template = "coderedcms/blocks/rich_text_block.html"

class PagePreviewBlock(BaseBlock):
    """
    Renders a preview of a specific page.
    """

    page = blocks.PageChooserBlock(
        required=True,
        label=_("Page to preview"),
        help_text=_("Show a mini preview of the selected page."),
    )

    class Meta:
        template = "enap_designsystem/blocks/pagepreview_block.html"
        icon = "doc-empty-inverse"
        label = _("Page Preview")



class PreviewCoursesBlock(BaseBlock):
    """
    Renders a preview of a specific page.
    """

    page = blocks.PageChooserBlock(
        required=False,
        label=_("Pagina de Formações"),
        help_text=_("Show a mini preview of the selected page."),
    )

    class Meta:
        template = "enap_designsystem/blocks/preview_courses.html"
        icon = "doc-empty-inverse"
        label = _("Preview de outras paginas com cards bg-image")





class PageListBlock(BaseBlock):
    """
    Renders a preview of selected pages.
    """

    indexed_by = blocks.PageChooserBlock(
        required=True,
        label=_("Parent page"),
        help_text=_(
            "Show a preview of pages that are children of the selected page. "
            "Uses ordering specified in the page’s LAYOUT tab."
        ),
    )
    
    # DEPRECATED: Remove in 3.0
    show_preview = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show body preview"),
    )
    num_posts = blocks.IntegerBlock(
        default=3,
        label=_("Number of pages to show"),
    )

    class Meta:
        template = "enap_designsystem/blocks/page/pagelist_block.html"
        icon = "list-ul"
        label = _("Preview ultimas paginas")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        indexer = value["indexed_by"].specific
        if hasattr(indexer, "get_index_children"):
            pages = indexer.get_index_children()
        else:
            pages = indexer.get_children().live()

        # SOLUÇÃO: Converter para objetos específicos
        context["pages"] = [p.specific for p in pages[: value["num_posts"]]]
        
        return context





class JobVacancyFilteredBlock(BaseBlock):
    """
    Advanced job vacancy block with dynamic filtering capabilities.
    """

    indexed_by = blocks.PageChooserBlock(
        required=True,
        label=_("Página pai das vagas"),
    )
    
    num_posts = blocks.IntegerBlock(
        default=6,
        label=_("Número máximo de vagas"),
    )

    # Filtros múltiplos para maior flexibilidade
    allowed_status = blocks.MultipleChoiceBlock(
        choices=[
            ('aberta', _('Abertas')),
            ('em_andamento', _('Em Andamento')),
            ('encerrada', _('Encerradas')),
        ],
        default=['aberta'],
        label=_("Status permitidos"),
        help_text=_("Selecione quais status de vagas podem ser exibidos")
    )

    allowed_areas = blocks.MultipleChoiceBlock(
        choices=[
            ('professores_facilitadores', _('Professores e Facilitadores')),
            ('servicos_tecnicos', _('Contratação de Serviços Técnicos')),
            ('licitacoes', _('Licitações')),
            ('outros', _('Outros')),
        ],
        required=False,
        label=_("Áreas permitidas"),
        help_text=_("Deixe vazio para mostrar todas as áreas")
    )

    # Filtros por data
    show_only_open_registrations = blocks.BooleanBlock(
        default=False,
        required=False,
        label=_("Apenas com inscrições abertas"),
        help_text=_("Mostrar apenas vagas cujas inscrições ainda estão dentro do prazo")
    )

    exclude_expired = blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Excluir vagas expiradas"),
        help_text=_("Não mostrar vagas cujas inscrições já encerraram")
    )

    class Meta:
        template = "enap_designsystem/blocks/job_vacancy_filtered_block.html"
        icon = "snippet"
        label = _("Vagas de Emprego Filtradas")

    def get_context(self, value, parent_context=None):
        from datetime import date
        from django.apps import apps
        
        context = super().get_context(value, parent_context=parent_context)

        indexer = value["indexed_by"].specific
        
        if hasattr(indexer, "get_index_children"):
            pages = indexer.get_index_children()
        else:
            pages = indexer.get_children().live()

        # ✅ CORREÇÃO: Primeiro filtrar apenas JobVacancyPage usando o content_type
        pages = pages.filter(content_type__model='jobvacancypage')

        # ✅ CORREÇÃO: Converter para QuerySet específico do JobVacancyPage
        try:
            # Tentar obter o modelo JobVacancyPage
            JobVacancyPage = apps.get_model('enap_designsystem', 'JobVacancyPage')
            
            # Obter IDs das páginas filtradas
            page_ids = list(pages.values_list('id', flat=True))
            
            # Criar QuerySet específico do JobVacancyPage
            job_pages = JobVacancyPage.objects.filter(id__in=page_ids).live()
            
        except LookupError:
            # Se não conseguir importar o modelo, usar abordagem alternativa
            context["pages"] = []
            context["total_available"] = 0
            return context

        # Aplicar filtros de status
        allowed_status = value.get("allowed_status", ['aberta'])
        if allowed_status:
            job_pages = job_pages.filter(status__in=allowed_status)

        # Aplicar filtros de área
        allowed_areas = value.get("allowed_areas", [])
        if allowed_areas:
            job_pages = job_pages.filter(area__in=allowed_areas)

        # Filtros por data
        today = date.today()
        
        if value.get("show_only_open_registrations", False):
            job_pages = job_pages.filter(
                registration_start__lte=today,
                registration_end__gte=today
            )
        
        if value.get("exclude_expired", True):
            job_pages = job_pages.exclude(registration_end__lt=today)

        # Ordenar por proximidade do fim das inscrições
        job_pages = job_pages.order_by('registration_end', '-first_published_at')
        
        # Aplicar limite
        limited_pages = job_pages[: value["num_posts"]]
        
        context["pages"] = limited_pages
        context["total_available"] = job_pages.count()
        
        return context




class NewsCarouselBlock(BaseBlock):
    """
    Renders a carousel of selected news pages.
    """

    indexed_by = blocks.PageChooserBlock(
        required=True,
        label=_("Parent page"),
        help_text=_(
            "Show a preview of pages that are children of the selected page. "
            "Uses ordering specified in the page's LAYOUT tab."
        ),
    )
    
    num_posts = blocks.IntegerBlock(
        default=3,
        label=_("Number of pages to show"),
    )

    class Meta:
        template = "enap_designsystem/blocks/page/pagenoticias_block.html"
        icon = "list-ul"
        label = _("Carrossel escolher outras paginas")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        indexer = value["indexed_by"].specific
        num_posts = value["num_posts"]
        
        # pages = indexer.get_index_children()
        # pages = indexer.get_children().live()
        pages = indexer.get_children().live().order_by("-first_published_at")[:50]
        
        # Função personalizada para obter a data correta dependendo do tipo de página
        def get_page_date(page):
            return getattr(page.specific, "date_display", None) or page.first_published_at.date()

        # Ordenar as páginas com base na data correta
        pages_ordered = sorted(pages, key=get_page_date, reverse=True)[:num_posts]

        # Limitar o número de páginas a ser exibido, conforme o valor de `num_posts`
        context["pages"] = pages_ordered
        return context

class CoursesCarouselBlock(BaseBlock):
    """
    Renders a carousel of selected news pages.
    """

    title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Título"),
        help_text=_("Título do carrossel de cursos"),
    )
    
    description = blocks.RichTextBlock(
        required=False,
        label=_("Descrição"),
        help_text=_("Descrição do carrossel de cursos"),
        features=['bold', 'italic', 'link']
    )


    indexed_by = blocks.PageChooserBlock(
        required=True,
        label=_("Parent page"),
        help_text=_(
            "Show a preview of pages that are children of the selected page. "
            "Uses ordering specified in the page’s LAYOUT tab."
        ),
    )
    
    num_posts = blocks.IntegerBlock(
        default=3,
        label=_("Number of pages to show"),
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)        
        indexed_by = value.get("indexed_by")
        if indexed_by is None:
            context["pages"] = []
            return context        
        
        indexer = indexed_by.specific        
        if hasattr(indexer, "get_index_children"):
            pages = indexer.get_index_children()
        else:
            pages = indexer.get_children().live()
        
        # Lista para armazenar dados de páginas
        pages_data = []
        
        # Importar o modelo de imagem do Wagtail
        from wagtail.images.models import Image
        import logging
        logger = logging.getLogger(__name__)
        
        # Limite de posts a exibir
        limit = value.get("num_posts", 5)
        
        # Obtendo as páginas e adicionando imagens
        for page in pages[:limit]:
            page_data = {"page": page}
            page_specific = page.specific
            found_image = None
            
            # 1. Procurar imagens dentro de blocos de conteúdo (como no exemplo funcionando)
            if hasattr(page_specific, 'content'):
                try:
                    for block in page_specific.content:
                        # Verificar se é um bloco de banner com imagem
                        if block.block_type == 'banner' and hasattr(block.value, 'background_image'):
                            if block.value.background_image:
                                found_image = block.value.background_image
                                break
                        # Verificar outros tipos de blocos com imagens
                        elif block.block_type == 'image' and hasattr(block.value, 'image'):
                            if block.value.image:
                                found_image = block.value.image
                                break
                        # Tentar acessar qualquer atributo do bloco que possa conter uma imagem
                        elif hasattr(block.value, 'image'):
                            if block.value.image:
                                found_image = block.value.image
                                break
                except Exception as e:
                    logger.error(f"Erro ao processar conteúdo da página: {e}")
            
            # 2. Se não encontrou nos blocos, tentar outros campos comuns
            if not found_image:
                # Campos comuns que podem conter imagens
                image_fields = ['header_image', 'featured_image', 'banner_image', 'cover_image', 'image']
                for field_name in image_fields:
                    if hasattr(page_specific, field_name):
                        field_value = getattr(page_specific, field_name)
                        if field_value and isinstance(field_value, Image):
                            found_image = field_value
                            break
            
            # 3. Ainda sem imagem? Verificar qualquer campo que seja uma imagem
            if not found_image:
                for field in page_specific._meta.get_fields():
                    if hasattr(page_specific, field.name):
                        try:
                            field_value = getattr(page_specific, field.name)
                            if isinstance(field_value, Image):
                                found_image = field_value
                                break
                        except Exception:
                            continue
            
            # Definir a imagem encontrada
            page_data["first_image"] = found_image
            pages_data.append(page_data)
        
        context["pages"] = pages_data
        return context
    class Meta:
        template = "enap_designsystem/blocks/card_courses.html"
        icon = "list-ul"
        label = _("Carrossel de cards primary")

class SuapCourseBlock(StructBlock):
    title = CharBlock(required=False, label="Título")
    description = CharBlock(required=False, label="Descrição")
    num_items = blocks.IntegerBlock(default=3,label=_("Máximo de cursos apresentados"),)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        num = value.get("num_items", 3)
        cursos_suap = self.get_destaques(num)
        context.update({
            "bloco_suap": value,
            "cursos_suap": cursos_suap
        })

        return context

    def get_destaques(self, limit=None):

        try:
            resp = requests.get("https://bff-portal.enap.gov.br/v1/home/destaques", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if limit:
                data = data[: limit]
            return [SimpleNamespace(**item) for item in data]
        except Exception as e:
            print('erro:', e)
            return []
    class Meta:
        template = "enap_designsystem/blocks/suap/suap_courses_block.html"
        icon = "list-ul"
        label = "Cursos do SUAP"




class APISuapCourseBlock(StructBlock):
    title = CharBlock(required=False, label="Título")
    description = CharBlock(required=False, label="Descrição")
    button = CharBlock(required=False, label="Titulo do Botão")
    url_button = URLBlock(required=False, label="Link do Botão")
    api_url = blocks.URLBlock(
        default="https://suap.enap.gov.br/portal/api/v3/cursosAltosExecutivos?format=json",
        label="URL da API",
        help_text="URL da API para buscar os cursos/eventos"
    )
    num_items = blocks.IntegerBlock(default=3, label=_("Máximo de cursos apresentados"))

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        num = value.get("num_items", 3)
        api_url = value.get("api_url")
        cursos_suap = self.get_destaques(api_url, num)
        context.update({
            "bloco_suap": value,
            "cursos_suap": cursos_suap
        })
        return context

    def get_destaques(self, api_url, limit=None):

        try:
            resp = requests.get(api_url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            data = data.get('results', [])
            
            # Aplicar limite se especificado
            if limit:
                data = data[:limit]
            
            # Processar os dados para converter datas
            processed_data = []
            for item in data:
                # Converter data_inicio de string para datetime se existir
                try:
                    # Assumindo formato YYYY-MM-DD
                    item['data_inicio'] = datetime.strptime(item['data_inicio'], '%Y-%m-%d').date()
                    item['data_inicio_aula'] = datetime.strptime(item['data_inicio_aula'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    # Se não conseguir converter, mantém como string
                    pass
                
                processed_data.append(SimpleNamespace(**item))
                
            return processed_data
        except Exception as e:
            # Log do erro para debug (opcional)
            print(f"Erro ao buscar eventos de {api_url}: {e}")
            return []

    class Meta:
        template = "enap_designsystem/blocks/suap/apisuap_courses_block.html"
        icon = "list-ul"
        label = "Cursos do SUAP com API"
        
class APIRPSUltimaEdicaoBlock(StructBlock):
    title = CharBlock(required=False, label="Título")
    description = CharBlock(required=False, label="Descrição")
    api_url = blocks.URLBlock(
        default="https://revista.enap.gov.br/index.php/RSP/api/v1/issues/current",
        label="URL da API",
        help_text="URL da API",
        required=True
    )
    api_token = blocks.CharBlock(
        label="Token da API",
        help_text="Token da API",
        required=True
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        api_url = value.get("api_url")
        api_token = value.get("api_token")
        dados_api  = self.get_api_articles(api_url, api_token)
        context.update({
            "bloco_rps": value,
            "dados_api": dados_api
        })
        return context

    def get_api_articles(self, url, token):
        full_url = f"{url}?apiToken={token}"

        try:
            resp = requests.get(full_url)
            data = resp.json()

            return data
        
        except Exception as e:
            print(f"Erro ao buscar eventos de {full_url}: {e}")
            return []

    class Meta:
        template = "enap_designsystem/blocks/rps/apirps_ultima_block.html"
        icon = "list-ul"
        label = "Ultima edição do RPS com API"


class APIRPSBuscaAcervoBlock(StructBlock):
    title = CharBlock(required=False, label="Título")
    description = CharBlock(required=False, label="Descrição")
    api_url = blocks.URLBlock(
        default="https://revista.enap.gov.br/index.php/RSP/api/v1/issues",
        label="URL da API",
        help_text="URL da API",
        required=True
    )
    api_token = blocks.CharBlock(
        label="Token da API",
        help_text="Token da API",
        required=True
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        api_url = value.get("api_url")
        api_token = value.get("api_token")
        edicoes = self.get_api_articles(api_url, api_token)
        
        for edicao in edicoes:
            date_str = edicao.get('datePublished')
            if isinstance(date_str, str):
                try:
                    edicao['datePublished'] = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    edicao['datePublished'] = None
        
        ano_atual = datetime.now().year
        anos = [ano_atual - i for i in range(85)]
        
        context.update({
            "bloco_rps": value,
            "edicoes": edicoes,
            "anos": anos,
        })
        return context

    def get_api_articles(self, url, token):
        full_url = f"{url}?count=24offset=24&apiToken={token}"

        try:
            response = requests.get(full_url)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])

            # Remove itens com 'datePublished' vazio
            filtrados = [item for item in items if item.get("datePublished")]

            # Ordenar por datePublished decrescente
            filtrados.sort(key=lambda x: x.get("datePublished", ""), reverse=True)

            return filtrados
        
        except Exception as e:
            print(f"Erro ao buscar eventos de {full_url}: {e}")
            return []

    class Meta:
        template = "enap_designsystem/blocks/rps/apirps_busca_block.html"
        icon = "list-ul"
        label = "Busca com filtro do RPS com API"



class SuapCardCursoBlock(BaseBlock):
    """
    Componente que exibe cards de cursos em carrossel usando dados da API do SUAP
    """
    
    title = blocks.CharBlock(
        required=False, 
        label="Título da Seção",
        help_text="Título opcional para a seção de cursos",
        max_length=255
    )
    
    description = blocks.RichTextBlock(
        features=["bold", "italic", "ol", "ul", "hr", "link"],
        required=False,
        label="Descrição da Seção",
        help_text="Descrição opcional para a seção de cursos"
    )
    
    num_items = blocks.IntegerBlock(
        default=6,
        label="Máximo de cursos apresentados",
        help_text="Quantos cursos exibir da API (recomendado: 6-12 para carrossel)"
    )
    
    # Configurações visuais dos cards
    highlight_color = ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque dos Cards", 
        help_text="Cor que será aplicada nos cards de curso",
        default="#024248"
    )
    
    # Opção para status personalizado
    force_status = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Automático (da API)'),
            ('card-curso-em-breve', 'Forçar: Em breve'),
            ('card-curso-aberto', 'Forçar: Aberto'),
            ('card-curso-andamento', 'Forçar: Em andamento'),
            ('card-curso-encerrado', 'Forçar: Encerrado'),
        ],
        default='auto',
        label="Status dos Cards",
        help_text="Usar status da API ou forçar um status específico"
    )
    
    # Configurações do carrossel
    velocidade_carrossel = blocks.ChoiceBlock(
        choices=[
            ('lento', 'Lento (0.5s)'),
            ('normal', 'Normal (0.3s)'),
            ('rapido', 'Rápido (0.2s)'),
        ],
        default='normal',
        label="Velocidade da Transição",
        help_text="Velocidade da animação do carrossel"
    )
    
    mostrar_controles = blocks.BooleanBlock(
        required=False,
        default=True,
        label="Mostrar Controles de Navegação",
        help_text="Exibir setas de navegação do carrossel"
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        num = value.get("num_items", 6)
        cursos_suap = self.get_cursos_suap(num)
        
        # Processa os cursos para o formato do card
        cursos_processados = []
        for curso in cursos_suap:
            curso_card = self.processar_curso_para_card(curso, value)
            cursos_processados.append(curso_card)
        
        context.update({
            "bloco_config": value,
            "cursos_suap": cursos_processados,
            "total_cursos": len(cursos_processados)
        })

        return context

    def get_cursos_suap(self, limit=None):
        """Busca cursos da API do SUAP"""

        from types import SimpleNamespace
        
        try:
            resp = requests.get(
                "https://bff-portal.enap.gov.br/v1/home/destaques", 
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            
            if limit:
                data = data[:limit]
                
            return [SimpleNamespace(**item) for item in data]
            
        except Exception as e:
            # Log do erro em produção
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao buscar cursos do SUAP: {e}")
            return []

    def processar_curso_para_card(self, curso, config):
        """
        Converte dados da API do SUAP para o formato esperado pelo CardCurso
        """
        # Mapear status da API para classes CSS
        status_mapping = {
            'inscricoes_abertas': 'card-curso-aberto',
            'em_andamento': 'card-curso-andamento', 
            'encerrado': 'card-curso-encerrado',
            'em_breve': 'card-curso-em-breve',
        }
        
        # Determinar status do card
        if config.get('force_status') != 'auto':
            status_class = config.get('force_status')
        else:
            # Tentar mapear da API ou usar padrão
            api_status = getattr(curso, 'status', 'em_breve')
            status_class = status_mapping.get(api_status, 'card-curso-em-breve')
        
        # Mapear modalidade
        modalidade_mapping = {
            'EAD': 'online',
            'PRESENCIAL': 'presencial', 
            'SEMIPRESENCIAL': 'hibrido',
        }
        
        api_modalidade = getattr(curso, 'modalidade', 'PRESENCIAL')
        modalidade = modalidade_mapping.get(api_modalidade, 'presencial')
        
        return {
            'type': status_class,
            'title': getattr(curso, 'titulo', 'Curso sem título'),
            'description': getattr(curso, 'descricao', 'Descrição não disponível'),
            'carga_horaria': getattr(curso, 'carga_horaria', 'Não informado'),
            'modalidade': modalidade,
            'highlight_color': config.get('highlight_color', '#024248'),
            'link_url': getattr(curso, 'link', '#'),
            'link_text': 'Saiba mais',
            # Dados extras da API
            'data_inicio': getattr(curso, 'data_inicio', None),
            'data_fim': getattr(curso, 'data_fim', None),
            'vagas': getattr(curso, 'vagas', None),
            'instrutor': getattr(curso, 'instrutor', None),
        }

    class Meta:
        template = "enap_designsystem/blocks/suap_card_curso_block.html"
        icon = "cr-list-alt"
        label = "Carrossel de Cursos SUAP"


class DropdownBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=True)
    options = blocks.ListBlock(blocks.StructBlock([
        ('title', blocks.CharBlock(required=True)),
        ('page', blocks.PageChooserBlock(required=True))
    ]))

    class Meta:
        template = 'enap_designsystem/pages/mini/dropdown-holofote_blocks.html'
        icon = 'arrow_drop_down'
        label = 'Dropdown'



class EventsCarouselBlock(BaseBlock):
    """
    Renders a carousel of selected event pages.
    """

    indexed_by = blocks.PageChooserBlock(
        required=True,
        label=_("Parent page"),
        help_text=_(
            "Show a preview of pages that are children of the selected page. "
            "Uses ordering specified in the page's LAYOUT tab."
        ),
    )

    num_posts = blocks.IntegerBlock(
        default=3,
        label=_("Number of pages to show"),
    )

    class Meta:
        template = "enap_designsystem/pages/mini/eventos.html"
        icon = "date"
        label = _("Events Carousel escolhendo paginas")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        indexer = value["indexed_by"].specific
        
        if hasattr(indexer, "get_index_children"):
            pages = indexer.get_index_children()
        else:
            pages = indexer.get_children().live()

        pages = pages.order_by('-first_published_at')

        context["pages"] = pages[:value["num_posts"]]
        return context
    



class SuapEventsBlock(StructBlock):
	title = CharBlock(required=False, label="Título")
	description = CharBlock(required=False, label="Descrição")
	num_items = blocks.IntegerBlock(default=3,label=_("Máximo de cursos apresentados"),)

	def get_context(self, value, parent_context=None):
		context = super().get_context(value, parent_context)
		num = value.get("num_items", 3)
		events_suap = self.get_destaques(num)
		context.update({
			"bloco_suap": value,
			"events_suap": events_suap
		})

		return context

	def get_destaques(self, limit=None):
		try:
			resp = requests.get("https://suap.enap.gov.br/portal/api/v3/destaqueEventos?format=json", timeout=5)
			resp.raise_for_status()
			data = resp.json()
			# print('EVENTOS:', data.get('results', []))
			data = data.get('results', [])

			for item in data:
				# Convertendo data_inicio para objeto date
				if isinstance(item.get('data_inicio'), str):
					try:
						item['data_inicio'] = datetime.strptime(item['data_inicio'], "%Y-%m-%d").date()
					except ValueError:
						pass  # ignora se estiver mal formatado

				# Cortando horário para formato "HH:MM"
				if isinstance(item.get('horario'), str):
					item['horario'] = item['horario'][:5]

			if limit:
				data = data[:limit]

			return [SimpleNamespace(**item) for item in data]

		except Exception as e:
			print('erro:', e)
			return []

	class Meta:
		template = "enap_designsystem/blocks/suap/suap_events_block.html"
		icon = "list-ul"
		label = "Eventos do SUAP"


class CourseFeatureBlock(blocks.StructBlock):
    title_1 = blocks.CharBlock(required=True, help_text="Primeiro título da feature", default="Título da feature")
    description_1 = blocks.TextBlock(required=True, help_text="Primeira descrição da feature", default="Descrição da feature")
    title_2 = blocks.CharBlock(required=False, help_text="Segundo título da feature", default="Título da feature")
    description_2 = blocks.TextBlock(required=False, help_text="Segunda descrição da feature", default="Descrição da feature")
    image = ImageChooserBlock(required=False, help_text="Imagem da feature do curso")
    
    class Meta:
        template = "enap_designsystem/blocks/feature_course.html"
        icon = "placeholder"
        label = "2 titulos, 2 descrições e uma imagem"
        initialized = True



class CourseModulesBlock(blocks.StructBlock):
    """Bloco de estrutura do curso com múltiplos dropdowns."""
    title = blocks.CharBlock(required=True, default="Estrutura do curso", help_text="Título da seção")
    
    modules = blocks.ListBlock(
        blocks.StructBlock([
            # Ordem invertida - module_title é o primeiro campo agora
            ("module_title", blocks.CharBlock(required=True, help_text="Título do módulo (ex: 1º Módulo)", default="1º Módulo")),
            ("module_description", blocks.RichTextBlock(
                required=True, 
                help_text="Descrição breve do módulo (suporta formatação)", 
                default="<p>Descreva o módulo</p>",
                features=['bold', 'italic', 'link']  # Funcionalidades básicas
            )),
            ("module_items", blocks.ListBlock(
                blocks.CharBlock(required=False, help_text="Item da lista de conteúdo do módulo")
            )),
        ]),
        min_num=1,
        help_text="Adicione os módulos do curso"
    )
    
    class Meta:
        template = "enap_designsystem/blocks/feature_estrutura.html"
        icon = "list-ol"
        label = "Dropdowns com Módulos - Estrutura de Curso"
        initialized = True




class CourseIntroTopicsBlock(StructBlock):
    """Componente com introdução e tópicos fixos do curso."""
    title = CharBlock(label="Título do Curso", required=True, help_text="Título principal sobre o curso", default="Título do Curso")
    description = RichTextBlock(label="Descrição do Curso", required=True, help_text="Descrição geral do curso", default="Descreva o curso")
    image = ImageChooserBlock(label="Imagem", required=False, help_text="Imagem para destacar o curso")
    
    # Tópicos fixos com apenas descrições editáveis
    modalidade_description = RichTextBlock(label="Descrição da Modalidade", required=True, help_text="Descreva a modalidade do curso", default="Descreva a modalidade do curso")
    curso_description = RichTextBlock(label="Descrição do Curso", required=True, help_text="Descreva o conteúdo do curso", default="Descreva o conteúdo do curso")
    metodologia_description = RichTextBlock(label="Descrição da Metodologia", required=True, help_text="Descreva a metodologia do curso", default="Descreva a metodologia do curso")
    
    class Meta:
        template = 'enap_designsystem/blocks/course_intro_topics.html'
        icon = 'doc-full'
        label = 'Introdução e Tópicos de Curso'




class WhyChooseEnaptBlock(blocks.StructBlock):
    """Seção 'Por que escolher a Enap?'"""
    # Título e descrição principal
    title = blocks.CharBlock(required=True, label=_("Título principal"), default="Titulo do beneficio")
    description = blocks.TextBlock(required=False, label=_("Descrição principal"), default="Titulo do beneficio")
    
    # Benefício 1
    image_1 = ImageChooserBlock(required=False, label=_("Imagem do benefício 1"))
    title_1 = blocks.CharBlock(required=True, label=_("Título do benefício 1"), default="Metodologia ensino–aplicação")
    
    # Benefício 2
    image_2 = ImageChooserBlock(required=False, label=_("Imagem do benefício 2"))
    title_2 = blocks.CharBlock(required=True, label=_("Título do benefício 2"), default="Desenvolvimento de competências de forma inovadora")
    
    # Benefício 3
    image_3 = ImageChooserBlock(required=False, label=_("Imagem do benefício 3"))
    title_3 = blocks.CharBlock(required=True, label=_("Título do benefício 3"), default="Desenvolvimento de competências de forma inovadora")
    
    # Benefício 4
    image_4 = ImageChooserBlock(required=False, label=_("Imagem do benefício 4"))
    title_4 = blocks.CharBlock(required=True, label=_("Título do benefício 4"), default="Desenvolvimento de competências de forma inovadora")

    class Meta:
        template = 'enap_designsystem/blocks/why_choose.html'
        icon = 'placeholder'
        label = _("4 beneficios, icones e texto")





class ProcessoSeletivoBlock(blocks.StructBlock):
    """Bloco para exibir informações sobre o processo seletivo com 3 módulos."""
    title = blocks.CharBlock(required=True, default="Processo seletivo", help_text="Título da seção")
    description = blocks.TextBlock(required=True, default="Sobre o processo seletivo", help_text="Descrição do processo seletivo")
    
    # Módulo 1
    module1_title = blocks.CharBlock(required=True, default="Inscrição", help_text="Título do primeiro módulo")
    module1_description = blocks.TextBlock(required=True, help_text="Descrição do primeiro módulo", default="Lorem ipsum dolor sit amet, lorem ipsum dolor sit amet")
    
    # Módulo 2
    module2_title = blocks.CharBlock(required=True, default="Seleção", help_text="Título do segundo módulo")
    module2_description = blocks.TextBlock(required=True, help_text="Descrição do segundo módulo", default="Lorem ipsum dolor sit amet, lorem ipsum dolor sit amet")
    
    # Módulo 3
    module3_title = blocks.CharBlock(required=True, default="Resultado", help_text="Título do terceiro módulo")
    module3_description = blocks.TextBlock(required=True, help_text="Descrição do terceiro módulo", default="Lorem ipsum dolor sit amet, lorem ipsum dolor sit amet")
    
    class Meta:
        template = "enap_designsystem/blocks/feature_processo_seletivo.html"
        icon = "list-ul"
        label = "Processo Seletivo - Background verde, Título e descrição - Três Etapas (titulo e descrição)"
        initialized = True




class TeamCarouselBlock(blocks.StructBlock):
    """Carrossel para exibir membros da equipe."""
    title = blocks.CharBlock(required=True, default="Nossa Equipe", help_text="Título da seção")
    description = blocks.RichTextBlock(
    required=False, 
    help_text="Descrição da seção da equipe (suporta formatação rica)", 
    default="<p>Nossa equipe é composta por desenvolvedores experientes e apaixonados por tecnologia...</p>"
    )
    view_all_text = blocks.CharBlock(required=False, default="Ver todos", help_text="Texto do botão 'ver todos'")
    
    members = blocks.ListBlock(
        blocks.StructBlock([
            ("name", blocks.CharBlock(required=True, help_text="Nome do membro da equipe")),
            ("role", blocks.RichTextBlock(required=True, help_text="Cargo/função do membro")),
            ("image", ImageChooserBlock(required=False, help_text="Foto do membro da equipe")),
        ]),
        help_text="Adicione os membros da equipe",
        default=[
            {'name': 'Membro 1', 'role': 'Cargo 1', 'image': None},
            {'name': 'Membro 2', 'role': 'Cargo 2', 'image': None},
            {'name': 'Membro 3', 'role': 'Cargo 3', 'image': None},
            {'name': 'Membro 4', 'role': 'Cargo 4', 'image': None},
        ],
        collapsed=False
    )

    class Meta:
        template = 'enap_designsystem/blocks/team_carousel.html'
        icon = 'group'
        label = 'Carrossel de Equipe'




class TestimonialsCarouselBlock(blocks.StructBlock):
    """Carrossel para exibir depoimentos ou testemunhos."""
    title = blocks.CharBlock(required=True, default="Depoimentos", help_text="Título da seção")
    description = blocks.TextBlock(required=False, help_text="Descrição opcional da seção")
    
    testimonials = blocks.ListBlock(
        blocks.StructBlock([
            ("name", blocks.CharBlock(required=True, help_text="Nome da pessoa", default="Nome do profissional")),
            ("position", blocks.CharBlock(required=True, help_text="Cargo ou posição da pessoa", default="Cargo do profissional")),
            ("testimonial", blocks.TextBlock(required=True, help_text="Depoimento da pessoa", default="Lorem ipsum dolor sit amet, lorem ipsum dolor sit amet")),
            ("image", ImageChooserBlock(required=False, help_text="Foto da pessoa")),
        ]),
        help_text="Adicione os depoimentos"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/testimonials_carousel.html'
        icon = 'openquote'
        label = 'Carrossel de Depoimentos'







# Definição dos blocos de conteúdo para o StreamField
class HeadingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True)
    level = blocks.ChoiceBlock(choices=[
        ('h2', 'Título Nível 2'),
        ('h3', 'Título Nível 3'),
        ('h4', 'Título Nível 4'),
    ], default='h2')

    class Meta:
        template = 'blocks/heading_block.html'
        icon = 'title'
        label = 'Título'


class RichTextBlock(blocks.RichTextBlock):
    class Meta:
        template = 'enap_designsystem/blocks/richtext_block.html'
        icon = 'doc-full'
        label = 'Texto'


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True) 
    caption = blocks.CharBlock(required=False)
    
    class Meta:
        template = 'enap_designsystem/blocks/image_block.html'
        icon = 'image'
        label = 'Imagem'

class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock(required=True)
    attribution = blocks.CharBlock(required=False)
    
    class Meta:
        template = 'enap_designsystem/blocks/quote_block.html'
        icon = 'openquote'
        label = 'Citação'


class VideoBlock(blocks.StructBlock):
    url = blocks.URLBlock(required=True, help_text="URL do YouTube ou Vimeo")
    caption = blocks.CharBlock(required=False)
    
    class Meta:
        template = 'enap_designsystem/blocks/video_block.html'
        icon = 'media'
        label = 'Embed Vídeo'



class ImageTextBlockChoices(blocks.StructBlock):
    """
    Componente flexível de imagem com texto
    Permite escolher diferentes proporções de layout
    """
    
    # Opções de proporção
    LAYOUT_CHOICES = [
        ('50-50', 'Imagem 50% - Texto 50%'),
        ('30-70', 'Imagem 30% - Texto 70%'),
        ('70-30', 'Imagem 70% - Texto 30%'),
        ('40-60', 'Imagem 40% - Texto 60%'),
        ('60-40', 'Imagem 60% - Texto 40%'),
    ]
    
    # Posicionamento da imagem
    POSITION_CHOICES = [
        ('left', 'Imagem à esquerda'),
        ('right', 'Imagem à direita'),
    ]
    
    # Configuração do layout
    layout_proportion = blocks.ChoiceBlock(
        choices=LAYOUT_CHOICES,
        default='50-50',
        label='Proporção do Layout',
        help_text='Escolha a proporção entre imagem e texto'
    )
    
    image_position = blocks.ChoiceBlock(
        choices=POSITION_CHOICES,
        default='left',
        label='Posição da Imagem',
        help_text='Escolha se a imagem fica à esquerda ou direita do texto'
    )
    
    # Conteúdo
    image = ImageChooserBlock(
        label='Imagem',
        help_text='Selecione a imagem a ser exibida'
    )
    
    image_alt = blocks.CharBlock(
        label='Texto alternativo da imagem',
        help_text='Descrição da imagem para acessibilidade',
        required=False
    )
    
    title = blocks.CharBlock(
        label='Título',
        required=False,
        help_text='Título opcional acima do texto'
    )
    
    text = blocks.RichTextBlock(
        label='Texto',
        help_text='Conteúdo de texto ao lado da imagem',
        features=['bold', 'italic', 'link', 'ol', 'ul', 'h2', 'h3', 'h4']
    )
    
    # Configurações visuais opcionais
    background_color = blocks.ChoiceBlock(
        choices=[
            ('', 'Padrão (sem cor)'),
            ('bg-light', 'Fundo claro'),
            ('bg-secondary', 'Fundo secundário'),
            ('bg-primary-light', 'Fundo primário claro'),
        ],
        default='',
        required=False,
        label='Cor de fundo',
        help_text='Cor de fundo opcional para o componente'
    )
    
    add_container = blocks.BooleanBlock(
        default=True,
        required=False,
        label='Adicionar container',
        help_text='Adiciona margens laterais responsivas'
    )
    
    vertical_spacing = blocks.ChoiceBlock(
        choices=[
            ('py-3', 'Pequeno'),
            ('py-4', 'Médio'),
            ('py-5', 'Grande'),
            ('py-6', 'Extra Grande'),
        ],
        default='py-4',
        label='Espaçamento vertical',
        help_text='Espaçamento superior e inferior do componente'
    )
    
    def get_image_width_class(self, value):
        """Retorna a classe CSS para a largura da imagem"""
        proportion = value.get('layout_proportion', '50-50')
        width_map = {
            '30-70': 'col-md-4 col-lg-3',
            '40-60': 'col-md-5 col-lg-4', 
            '50-50': 'col-md-6',
            '60-40': 'col-md-7 col-lg-8',
            '70-30': 'col-md-8 col-lg-9',
        }
        return width_map.get(proportion, 'col-md-6')
    
    def get_text_width_class(self, value):
        """Retorna a classe CSS para a largura do texto"""
        proportion = value.get('layout_proportion', '50-50')
        width_map = {
            '30-70': 'col-md-8 col-lg-9',
            '40-60': 'col-md-7 col-lg-8',
            '50-50': 'col-md-6',
            '60-40': 'col-md-5 col-lg-4',
            '70-30': 'col-md-4 col-lg-3',
        }
        return width_map.get(proportion, 'col-md-6')
    
    def get_column_order(self, value):
        """Retorna as classes de ordem para posicionamento responsivo"""
        position = value.get('image_position', 'left')
        if position == 'right':
            return {
                'image_order': 'order-md-2',
                'text_order': 'order-md-1'
            }
        return {
            'image_order': '',
            'text_order': ''
        }
    
    class Meta:
        template = 'enap_designsystem/blocks/image_text_block.html'
        icon = 'image'
        label = 'Imagem com Texto'
        help_text = 'Componente flexível de imagem com texto em diferentes proporções'









ARTICLE_STREAMBLOCKS = [
    ('richtext', RichTextBlock()),
    ("button", ButtonBlock()),
    ('image', ImageBlock()),
    ('quote', QuoteBlock()),
    ('carousel', CarouselBlock()),
    ("download", DownloadBlock()),
    ("embed_video", VideoBlock()),
    ("noticias_carousel", NewsCarouselBlock()),
    ("eventos_carousel", EventsCarouselBlock()),
    ("Texto_image_choices", ImageTextBlockChoices()),
]



class ArticleGridBlock(blocks.StructBlock):
    """
    Wrapper para criar layouts de notícia normal ou revista
    """
    
    LAYOUT_CHOICES = [
        ('noticia', 'Notícia Normal (uma coluna)'),
        ('revista', 'Notícia Revista (duas colunas)'),
    ]

    layout_type = blocks.ChoiceBlock(
        choices=LAYOUT_CHOICES,
        default='noticia',
        label='Tipo de Layout',
        help_text='Escolha entre notícia normal ou formato revista'
    )
    
    # Conteúdo para notícia normal (uma coluna)
    conteudo = blocks.StreamBlock(
        ARTICLE_STREAMBLOCKS,
        label='Conteúdo',
        help_text='Conteúdo da notícia (aparece apenas no formato notícia normal)',
        required=False
    )
    
    # Conteúdos para formato revista (duas colunas)
    coluna_esquerda = blocks.StreamBlock(
        ARTICLE_STREAMBLOCKS,
        label='Coluna Esquerda',
        help_text='Conteúdo da primeira coluna (aparece apenas no formato revista)',
        required=False
    )
    
    coluna_direita = blocks.StreamBlock(
        ARTICLE_STREAMBLOCKS,
        label='Coluna Direita', 
        help_text='Conteúdo da segunda coluna (aparece apenas no formato revista)',
        required=False
    )
    
    class Meta:
        js = ('enap_designsystem/blocks/article_grid_conditional.js',)
        template = 'enap_designsystem/blocks/article_grid_block.html'
        icon = 'doc-full'
        label = 'Layout de Artigo'
        help_text = 'Escolha entre notícia normal ou formato revista'



class ArticlePage(Page):
    """
    Página de artigo, adequada para notícias ou conteúdo de blog.
    ATENÇÃO: NÃO UTILIZAR MAIS
    ASSIM QUE MIGRAR O NECESSÁRIO PARA "class ENAPNoticia(Page):" DELETAR!
    """

    class Meta:
        verbose_name = _("[OLD]ENAP Artigo")
        verbose_name_plural = _("[OLD]ENAP Artigos")

    template = "enap_designsystem/blocks/article_page.html"

    # Campo para o conteúdo principal
    body = StreamField(
        ARTICLE_STREAMBLOCKS,
        null=True,
        blank=True,
        verbose_name=_("Conteúdo"),
        use_json_field=True,
    )

    # Campos de metadados do artigo
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Legenda"),
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Autor"),
        related_name='articlepage_author_set',
    )
    
    author_display = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Exibir autor como"),
        help_text=_("Substitui como o nome do autor é exibido neste artigo."),
    )
    
    date_display = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Data de publicação para exibição"),
    )

    # Campos para SEO e compartilhamento
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_("Imagem destacada"),
        help_text=_("Imagem usada para compartilhamento em redes sociais e listagens"),
    )

    # Propriedades para SEO e exibição de metadados
    @property
    def seo_author(self) -> str:
        """
        Obtém o nome do autor usando uma estratégia de fallback.
        """
        if self.author_display:
            return self.author_display
        if self.author:
            return self.author.get_full_name()
        if self.owner:
            return self.owner.get_full_name()
        return ""

    @property
    def seo_published_at(self) -> datetime:
        """
        Obtém a data de publicação para exibição.
        """
        if self.date_display:
            return self.date_display
        return self.first_published_at

    @property
    def seo_description(self) -> str:
        """
        Obtém a descrição usando uma estratégia de fallback.
        """
        if self.search_description:
            return self.search_description
        if self.caption:
            return self.caption
        return self.get_body_preview(100)

    @property
    def get_body_preview(self, length=100) -> str:
        """
        Obtém uma prévia do conteúdo do artigo.
        """
        text = ""
        for block in self.body:
            if block.block_type == 'richtext':
                text += block.value.source
            elif block.block_type == 'heading':
                text += block.value['heading'] + " "
        
        # Remover tags HTML e limitar caracteres
        import re
        text = re.sub(r'<[^>]+>', '', text)
        return text[:length] + "..." if len(text) > length else text

    @property
    def url_filter(self):
        if hasattr(self, 'full_url') and self.full_url:
            return self.full_url
        return self.get_url_parts()[2] if self.get_url_parts() else ""
    
        
    # Configuração de busca
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('caption', boost=2),
        index.FilterField('author'),
        index.FilterField('author_display'),
        index.FilterField('date_display'),
        index.FilterField("url", name="url_filter"),
    ]

    # Painéis de conteúdo para o admin
    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('caption'),
        FieldPanel('featured_image'),
        MultiFieldPanel(
            [
                FieldPanel('author'),
                FieldPanel('author_display'),
                FieldPanel('date_display'),
            ],
            heading=_("Informações de Publicação"),
        ),
    ]
    
    def get_searchable_content(self):
        content = super().get_searchable_content()
        content.append(self.caption or "")
        content.append(self.seo_description or "")
        content.append(self.get_body_preview())
        return content
    
    # Métodos auxiliares para templates
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Você pode adicionar variáveis de contexto específicas para artigos aqui
        return context


class ArticleIndexPage(Page):
    """
    Página de índice que mostra uma lista de artigos.
    ATENÇÃO: NÃO UTILIZAR MAIS
    ASSIM QUE MIGRAR O NECESSÁRIO PARA "class ENAPNoticiasIndexPage(Page):" DELETAR!
    """

    class Meta:
        verbose_name = _("[OLD]ENAP Página de Índice de Artigos")
        verbose_name_plural = _("[OLD]ENAP Páginas de Índice de Artigos")

    template = "enap_designsystem/pages/article_index_page.html"

    # Introdução para a página de listagem
    intro = models.TextField(
        blank=True,
        verbose_name=_("Introdução"),
    )
    
    # Opções de exibição dos artigos
    show_images = models.BooleanField(
        default=True,
        verbose_name=_("Exibir imagens"),
    )
    
    show_captions = models.BooleanField(
        default=True,
        verbose_name=_("Exibir legendas"),
    )
    
    show_meta = models.BooleanField(
        default=True,
        verbose_name=_("Exibir autor e informações de data"),
    )
    
    show_preview_text = models.BooleanField(
        default=True,
        verbose_name=_("Exibir texto de prévia"),
    )
    
    articles_per_page = models.PositiveIntegerField(
        default=10,
        verbose_name=_("Artigos por página"),
    )

    # Configuração de busca
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    # Painéis de conteúdo para o admin
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        MultiFieldPanel(
            [
                FieldPanel('show_images'),
                FieldPanel('show_captions'),
                FieldPanel('show_meta'),
                FieldPanel('show_preview_text'),
                FieldPanel('articles_per_page'),
            ],
            heading=_("Exibição de artigos"),
        ),
    ]

    def get_searchable_content(self):
        content = super().get_searchable_content()
        content.append(self.intro or "")
        content.append(self.search_description or "")
        return content
    
    def get_context(self, request, *args, **kwargs):
        """
        Adiciona artigos ao contexto.
        """
        context = super().get_context(request, *args, **kwargs)
        
        # Obtém todos os artigos
        articles = ArticlePage.objects.live().descendant_of(self)
        
        # Ordena por data (mais recente primeiro)
        articles = articles.order_by('-date_display', '-first_published_at')
        
        # Paginação
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        paginator = Paginator(articles, self.articles_per_page)
        page = request.GET.get('page')
        
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)
        
        context['articles'] = articles
        return context


class ENAPNoticiasIndexPage(Page):
	subpage_types = ['enap_designsystem.ENAPNoticiaImportada', 'enap_designsystem.ENAPNoticia', 'enap_designsystem.ENAPRevista']

	class Meta:
		verbose_name = _("ENAP Índice de Notícias")
		verbose_name_plural = _("ENAP Índice de Notícias")

	template = "enap_designsystem/pages/article/enap_noticias_index.html"

	search_fields = []

	def get_context(self, request):
		context = super().get_context(request)

		start = int(request.GET.get("start", 0))
		page_size = 30
		page_number = (start // page_size) + 1

		children = []

		# Evita erro no preview antes da página existir na árvore
		if self.pk and self.live:
			children = self.get_children().live().specific().type(
				ENAPNoticiaImportada, ENAPNoticia, ENAPRevista
			).order_by("-first_published_at")

			paginator = Paginator(children, page_size)
			page = paginator.get_page(page_number)
			page_range = [
				(num, (num - 1) * page_size)
				for num in paginator.page_range
			]

			context["articles"] = page
			context["start"] = start
			context["page"] = page
			context["page_size"] = page_size
			context["start_prev"] = (page.previous_page_number() - 1) * page_size if page.has_previous() else None
			context["start_next"] = (page.next_page_number() - 1) * page_size if page.has_next() else None
			context["total_articles"] = len(children)
			context["page_range"] = page_range
		else:
			# Em preview de página nova, sem filhos
			context["articles"] = []
			context["start"] = 0
			context["page"] = None
			context["page_size"] = page_size
			context["start_prev"] = None
			context["start_next"] = None
			context["total_articles"] = 0
			context["page_range"] = None

		return context



class ENAPNoticia(Page):
	"""Modelo base para novas notícias (customizável depois)."""

	body = StreamField(
		ARTICLE_STREAMBLOCKS,
		null=True,
		blank=True,
		verbose_name=_("Conteúdo"),
		use_json_field=True,
	)
	
	subtitulo = models.CharField(
		max_length=255,
		blank=True,
		verbose_name=_("Subtítulo"),
		help_text=_("Texto complementar ao título da notícia."),
	)

	legenda_home = models.TextField(
		max_length=500,
		blank=True,
		verbose_name=_("Legenda para Home"),
		help_text=_("Texto que aparece nas listagens da home (máx. 500 caracteres). Se vazio, usará o subtítulo."),
	)

	imagem_externa = models.ForeignKey(
		get_image_model_string(),
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+',
		verbose_name=_("Imagem Externa"),
		help_text=_("Imagem principal da notícia para exibição externa (listagens, cards, etc)."),
	)

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		editable=True,
		on_delete=models.SET_NULL,
		verbose_name=_("Autor"),
		related_name='enap_noticiapage_set',
	)

	author_display = models.CharField(
		max_length=255,
		blank=True,
		verbose_name=_("Exibir autor como"),
		help_text=_("Substitui como o nome do autor é exibido neste artigo."),
	)

	date_display = models.DateField(
		null=True,
		blank=False,
		verbose_name=_("Data de publicação para exibição"),
	)

	featured_image = StreamField(
		[
			("image", ImageBlock()),
		],
		null=True,
		blank=True,
		verbose_name=_("Imagem Destacada"),
		help_text=_("Imagem interna do artigo, exibida no conteúdo."),
		use_json_field=True,
	)
	
	navbar = models.ForeignKey(
		"EnapNavbarSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	footer = models.ForeignKey(
		"EnapFooterSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	content_panels = Page.content_panels + [
		FieldPanel("navbar"),
		FieldPanel("footer"),
		MultiFieldPanel(
			[
				FieldPanel('subtitulo'),
				FieldPanel('legenda_home'),
				FieldPanel('imagem_externa'),
			],
			heading=_("Informações Básicas"),
		),
		FieldPanel('featured_image'),
		MultiFieldPanel(
			[
				FieldPanel('body'),
			],
			heading=_("Conteúdo da Notícia"),
		),
		MultiFieldPanel(
			[
				FieldPanel('author'),
				FieldPanel('author_display'),
				FieldPanel('date_display'),
			],
			heading=_("Informações de Publicação"),
		),
	]

	@property
	def titulo_filter(self):
		return strip_tags(self.title or "").strip()

	@property
	def descricao_filter(self):
		return strip_tags(self.subtitulo or "").strip()

	@property
	def legenda_home_filter(self):
		"""Retorna legenda_home ou fallback para subtítulo"""
		if self.legenda_home:
			return strip_tags(self.legenda_home).strip()
		return strip_tags(self.subtitulo or "").strip()

	@property
	def categoria(self):
		return "Notícias"

	@property
	def data_atualizacao_filter(self):
		return self.date_display or self.last_published_at or self.latest_revision_created_at or self.first_published_at

	@property
	def url_filter(self):
		if hasattr(self, 'full_url') and self.full_url:
			return self.full_url
		return self.get_url_parts()[2] if self.get_url_parts() else ""

	@property
	def imagem_filter(self):
		"""Retorna URL da imagem externa ou da featured_image como fallback."""
		# Prioridade: imagem_externa
		try:
			if self.imagem_externa:
				return self.imagem_externa.file.url
		except Exception:
			pass

		# Fallback: featured_image
		if self.featured_image and len(self.featured_image.stream_data) > 0:
			primeiro_bloco = self.featured_image.stream_data[0]
			if primeiro_bloco["type"] == "image":
				valor = primeiro_bloco["value"]
				if isinstance(valor, dict) and valor.get("id"):
					try:
						from wagtail.images import get_image_model
						Image = get_image_model()
						imagem = Image.objects.get(id=valor["id"])
						return imagem.file.url
					except Image.DoesNotExist:
						pass
		return ""

	@property
	def texto_unificado(self):
		def extract_text_from_block(block_value):
			result = []

			if isinstance(block_value, list):
				for subblock in block_value:
					result.extend(extract_text_from_block(subblock))
			elif hasattr(block_value, "get"):
				for key, val in block_value.items():
					result.extend(extract_text_from_block(val))
			elif isinstance(block_value, str):
				cleaned = strip_tags(block_value).strip()
				if cleaned and cleaned.lower() not in {
					"default", "tipo terciário", "tipo secundário", "tipo bg image",
					"bg-gray", "bg-blue", "bg-white", "fundo cinza", "fundo branco"
				}:
					result.append(cleaned)
			elif hasattr(block_value, "source"):
				cleaned = strip_tags(block_value.source).strip()
				if cleaned:
					result.append(cleaned)

			return result

		textos = []
		if self.body:
			for block in self.body:
				textos.extend(extract_text_from_block(block.value))

		if self.subtitulo:
			textos.append(strip_tags(self.subtitulo).strip())

		if self.legenda_home:
			textos.append(strip_tags(self.legenda_home).strip())

		return re.sub(r"\s+", " ", " ".join([t for t in textos if t])).strip()

	search_fields = Page.search_fields + [
		index.SearchField("title", boost=3),
		index.SearchField("titulo_filter", name="titulo"),
		index.SearchField("descricao_filter", name="descricao"),
		index.SearchField("legenda_home_filter", name="legenda_home"),
		index.FilterField("categoria", name="categoria_filter"),
		index.SearchField("url_filter", name="url"),
		index.SearchField("data_atualizacao_filter", name="data_atualizacao"),
		index.SearchField("imagem_filter", name="imagem"),
		index.SearchField("texto_unificado", name="body"),
	]
	
	class Meta:
		verbose_name = _("ENAP Notícia")
		verbose_name_plural = _("ENAP Notícias")

	template = "enap_designsystem/pages/article/enap_noticia.html"


class ENAPNoticiaImportada(Page):
	"""Página exclusiva para exibir artigos importados do Joomla, sem edição."""

	descricao_html = models.TextField(
		verbose_name="Descrição (Introtext)",
		blank=True,
		help_text="Conteúdo HTML do campo 'introtext' do Joomla."
	)

	conteudo_html = models.TextField(
		verbose_name="Conteúdo (Fulltext)",
		blank=True,
		help_text="Conteúdo HTML do campo 'fulltext' do Joomla."
	)

	xref_categoria = models.CharField(
		max_length=255,
		blank=True,
		verbose_name="Categoria Joomla (Texto Livre)"
	)

	autor = models.CharField(
		max_length=255,
		blank=True,
		verbose_name="Autor",
		help_text="Nome do autor do artigo."
	)

	fotografo = models.CharField(
		max_length=255,
		blank=True,
		verbose_name="Fotógrafo",
		help_text="Nome do fotógrafo responsável pelas imagens."
	)

	imagem_externa = models.ForeignKey(
		get_image_model_string(),
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+',
		verbose_name="Imagem Externa (image_intro)"
	)

	imagem_interna = models.ForeignKey(
		get_image_model_string(),
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+',
		verbose_name="Imagem Interna (image_fulltext)"
	)

	navbar = models.ForeignKey(
		"EnapNavbarSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)
	
	footer = models.ForeignKey(
		"EnapFooterSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	content_panels = Page.content_panels + [
		FieldPanel("navbar"),
		FieldPanel("footer"),
		FieldPanel("xref_categoria"),
		FieldPanel("autor"),
		FieldPanel("fotografo"),
		FieldPanel("imagem_externa"),
		FieldPanel("imagem_interna"),
		FieldPanel("descricao_html"),
		FieldPanel("conteudo_html"),
	]

	template = "enap_designsystem/pages/article/joomla/enap_noticia_importada.html"

	@property
	def titulo_filter(self):
		return strip_tags(self.title or "").strip()

	@property
	def descricao_filter(self):
		return strip_tags(self.descricao_html or "").strip()

	@property
	def categoria(self):
		return "Notícias"

	@property
	def data_atualizacao_filter(self):
		return self.last_published_at or self.latest_revision_created_at or self.first_published_at

	@property
	def url_filter(self):
		if hasattr(self, 'full_url') and self.full_url:
			return self.full_url
		return self.get_url_parts()[2] if self.get_url_parts() else ""

	@property
	def imagem_filter(self):
		try:
			if self.imagem_externa:
				return self.imagem_externa.file.url
		except Exception:
			pass

		try:
			if self.imagem_interna:
				return self.imagem_interna.file.url
		except Exception:
			pass

		return ""

	@property
	def texto_unificado(self):
		textos = [
			self.title,
			self.xref_categoria,
			self.descricao_html,
			self.conteudo_html,
		]

		limpos = [strip_tags(str(t)).strip() for t in textos if t]
		return re.sub(r"\s+", " ", " ".join(limpos)).strip()

	search_fields = Page.search_fields + [
		index.SearchField("title", boost=3),
		index.SearchField("titulo_filter", name="titulo"),
		index.SearchField("descricao_filter", name="descricao"),
		index.FilterField("categoria", name="categoria_filter"),
		index.SearchField("url_filter", name="url"),
		index.SearchField("data_atualizacao_filter", name="data_atualizacao"),
		index.SearchField("imagem_filter", name="imagem"),
		index.SearchField("texto_unificado", name="body"),
	]
		

	class Meta:
		verbose_name = _("ENAP Noticias Joomla")
		verbose_name_plural = _("ENAP Noticias Joomla")








class ENAPRevista(Page):
    """Modelo para artigos em formato revista com layout em duas colunas."""

    body = StreamField(
        [
            ("article_grid", ArticleGridBlock()),
        ],
        null=True,
        blank=True,
        verbose_name=_("Conteúdo"),
        help_text=_("Configure o layout: escolha 'Notícia Normal' ou 'Notícia Revista' e adicione o conteúdo."),
        use_json_field=True,
    )
    
    subtitulo = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Subtítulo"),
        help_text=_("Texto complementar ao título da revista."),
    )

    legenda_home = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_("Legenda para Home"),
        help_text=_("Texto que aparece nas listagens da home (máx. 500 caracteres). Se vazio, usará o subtítulo."),
    )

    imagem_externa = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_("Imagem Externa"),
        help_text=_("Imagem principal da revista para exibição externa (listagens, cards, etc)."),
    )

    # Campos de background da página
    background_type = models.CharField(
        max_length=20,
        choices=[
            ('color', _('Cor de Fundo')),
            ('image', _('Imagem de Fundo')),
        ],
        default='color',
        verbose_name=_("Tipo de Fundo"),
        help_text=_("Escolha entre cor sólida ou imagem de fundo."),
    )
    
    background_color = models.CharField(
        max_length=50,
        choices=[('', _('Padrão (sem cor)'))] + BACKGROUND_COLOR_CHOICES,
        default='',
        blank=True,
        verbose_name=_("Cor de Fundo"),
        help_text=_("Cor de fundo da página (usado quando 'Tipo de Fundo' é 'Cor')."),
    )
    
    background_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_("Imagem de Fundo"),
        help_text=_("Imagem de fundo da página (usado quando 'Tipo de Fundo' é 'Imagem')."),
    )
    
    background_image_position = models.CharField(
        max_length=30,
        choices=[
            ('center', _('Centro')),
            ('top', _('Topo')),
            ('bottom', _('Baixo')),
            ('left', _('Esquerda')),
            ('right', _('Direita')),
            ('top-left', _('Topo Esquerda')),
            ('top-right', _('Topo Direita')),
            ('bottom-left', _('Baixo Esquerda')),
            ('bottom-right', _('Baixo Direita')),
        ],
        default='center',
        verbose_name=_("Posição da Imagem"),
        help_text=_("Posição da imagem de fundo."),
    )
    
    background_image_size = models.CharField(
        max_length=20,
        choices=[
            ('cover', _('Cobrir (Cover)')),
            ('contain', _('Conter (Contain)')),
            ('auto', _('Automático')),
        ],
        default='cover',
        verbose_name=_("Tamanho da Imagem"),
        help_text=_("Como a imagem de fundo deve ser redimensionada."),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Autor"),
        related_name='enap_revista_set',
    )

    author_display = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Exibir autor como"),
        help_text=_("Substitui como o nome do autor é exibido neste artigo."),
    )

    date_display = models.DateField(
        null=True,
        blank=False,
        verbose_name=_("Data de publicação para exibição"),
    )

    featured_image = StreamField(
        [
            ("image", ImageBlock()),
        ],
        null=True,
        blank=True,
        verbose_name=_("Imagem Destacada"),
        help_text=_("Imagem de destaque que aparece no topo do artigo."),
        use_json_field=True,
    )
    
    # Campos específicos para revista
    edicao_numero = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Número da Edição"),
        help_text=_("Ex: Edição 15, Vol. 3, etc."),
    )
    
    categoria_revista = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ('entrevista', _('Entrevista')),
            ('artigo', _('Artigo')),
            ('especial', _('Especial')),
            ('inovacao', _('Inovação')),
            ('capacitacao', _('Capacitação')),
            ('pesquisa', _('Pesquisa')),
            ('internacional', _('Internacional')),
        ],
        verbose_name=_("Categoria da Revista"),
        help_text=_("Categoria específica para organização da revista."),
    )
    
    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    footer = models.ForeignKey(
        "EnapFooterSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Propriedade para obter o estilo CSS do background
    @property
    def background_style(self):
        """Gera o CSS para o background da página"""
        if self.background_type == 'image' and self.background_image:
            return (
                f"background-image: url('{self.background_image.file.url}'); "
                f"background-position: {self.background_image_position}; "
                f"background-size: {self.background_image_size}; "
                f"background-repeat: no-repeat;"
            )
        elif self.background_type == 'color' and self.background_color:
            return f"background-color: {self.background_color};"
        return ""

    content_panels = Page.content_panels + [
        FieldPanel("navbar"),
        FieldPanel("footer"),
        MultiFieldPanel(
            [
                FieldPanel('subtitulo'),
                FieldPanel('legenda_home'),
                FieldPanel('imagem_externa'),
                FieldPanel('edicao_numero'),
                FieldPanel('categoria_revista'),
            ],
            heading=_("Informações da Revista"),
        ),
        MultiFieldPanel(
            [
                FieldPanel('background_type'),
                FieldPanel('background_color'),
                FieldPanel('background_image'),
                FieldPanel('background_image_position'),
                FieldPanel('background_image_size'),
            ],
            heading=_("Configurações de Fundo"),
            help_text=_("Configure o fundo da página - escolha entre cor sólida ou imagem."),
        ),
        FieldPanel('featured_image'),
        MultiFieldPanel(
            [
                FieldPanel('body'),
            ],
            heading=_("Conteúdo da Revista"),
            help_text=_("DICA: Use o bloco 'Layout de Artigo' → 'Notícia Revista' para criar o layout em duas colunas como na imagem exemplo."),
        ),
        MultiFieldPanel(
            [
                FieldPanel('author'),
                FieldPanel('author_display'),
                FieldPanel('date_display'),
            ],
            heading=_("Informações de Publicação"),
        ),
    ]

    # Mesmas propriedades da ENAPNoticia para compatibilidade
    @property
    def titulo_filter(self):
        return strip_tags(self.title or "").strip()

    @property
    def descricao_filter(self):
        return strip_tags(self.subtitulo or "").strip()

    @property
    def legenda_home_filter(self):
        """Retorna legenda_home ou fallback para subtítulo"""
        if self.legenda_home:
            return strip_tags(self.legenda_home).strip()
        return strip_tags(self.subtitulo or "").strip()

    @property
    def categoria(self):
        return "Notícias"

    @property
    def data_atualizacao_filter(self):
        return self.date_display or self.last_published_at or self.latest_revision_created_at or self.first_published_at

    @property
    def url_filter(self):
        if hasattr(self, 'full_url') and self.full_url:
            return self.full_url
        return self.get_url_parts()[2] if self.get_url_parts() else ""

    @property
    def imagem_filter(self):
        """Retorna URL da imagem externa ou da featured_image como fallback."""
        # Prioridade: imagem_externa
        try:
            if self.imagem_externa:
                return self.imagem_externa.file.url
        except Exception:
            pass

        # Fallback: featured_image
        if self.featured_image and len(self.featured_image.stream_data) > 0:
            primeiro_bloco = self.featured_image.stream_data[0]
            if primeiro_bloco["type"] == "image":
                valor = primeiro_bloco["value"]
                if isinstance(valor, dict) and valor.get("id"):
                    try:
                        from wagtail.images import get_image_model
                        Image = get_image_model()
                        imagem = Image.objects.get(id=valor["id"])
                        return imagem.file.url
                    except Image.DoesNotExist:
                        pass
        return ""

    @property
    def texto_unificado(self):
        def extract_text_from_block(block_value):
            result = []

            if isinstance(block_value, list):
                for subblock in block_value:
                    result.extend(extract_text_from_block(subblock))
            elif hasattr(block_value, "get"):
                for key, val in block_value.items():
                    result.extend(extract_text_from_block(val))
            elif isinstance(block_value, str):
                cleaned = strip_tags(block_value).strip()
                if cleaned and cleaned.lower() not in {
                    "default", "tipo terciário", "tipo secundário", "tipo bg image",
                    "bg-gray", "bg-blue", "bg-white", "fundo cinza", "fundo branco"
                }:
                    result.append(cleaned)
            elif hasattr(block_value, "source"):
                cleaned = strip_tags(block_value.source).strip()
                if cleaned:
                    result.append(cleaned)

            return result

        textos = []
        if self.body:
            for block in self.body:
                textos.extend(extract_text_from_block(block.value))

        if self.subtitulo:
            textos.append(strip_tags(self.subtitulo).strip())

        if self.legenda_home:
            textos.append(strip_tags(self.legenda_home).strip())
            
        if self.edicao_numero:
            textos.append(strip_tags(self.edicao_numero).strip())

        return re.sub(r"\s+", " ", " ".join([t for t in textos if t])).strip()

    search_fields = Page.search_fields + [
        index.SearchField("title", boost=3),
        index.SearchField("titulo_filter", name="titulo"),
        index.SearchField("descricao_filter", name="descricao"),
        index.SearchField("legenda_home_filter", name="legenda_home"),
        index.FilterField("categoria", name="categoria_filter"),
        index.SearchField("url_filter", name="url"),
        index.SearchField("data_atualizacao_filter", name="data_atualizacao"),
        index.SearchField("imagem_filter", name="imagem"),
        index.SearchField("texto_unificado", name="body"),
        index.FilterField("categoria_revista"),
        index.SearchField("edicao_numero"),
    ]
    
    class Meta:
        verbose_name = _("ENAP Revista")
        verbose_name_plural = _("ENAP Revistas")

    template = "enap_designsystem/pages/article/enap_revista.html"



class ENAPDummyPage(Page):
	"""Página usada apenas como container na árvore, sem conteúdo visível."""

	class Meta:
		verbose_name = "Container (não exibido)"
		verbose_name_plural = "Containers"

	search_fields = []
	# Redireciona para o primeiro filho disponível, caso não tenha, 404
	def serve(self, request):
		# redireciona para o primeiro filho
		first_child = self.get_children().live().first()
		if first_child:
			return redirect(first_child.url)
		from django.http import Http404
		raise Http404("Sem conteúdo filho para redirecionar.")

# Definindo as cores da marca para reutilização
BRAND_COLOR_CHOICES = [
    ('#024248', 'Verde ENAP (#024248)'),
    ('#007D7A', 'Verde Link ENAP (#007D7A)'),
    ('#AD6BFC', 'Roxo Gnova (#AD6BFC)'),
    ('#B396FC', 'Roxo Claro Gnova (#B396FC)'),
    ('#FFFFFF', 'Branco (#FFFFFF)')
]

class SectionCardTitleCenterBlock(StructBlock):
    """Componente de seção com cards e título centralizado."""
    
    # Campos da seção
    title = CharBlock(
        required=False, 
        label="Título da Seção", 
        default="Título da Seção"
    )
    
    highlight_text = CharBlock(
        required=False, 
        label="Texto Destacado", 
        help_text="Parte do título que terá gradiente (opcional)",
        default=""
    )
    
    # Cor global para toda a seção
    highlight_color = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor que será aplicada no texto destacado e nos cards",
        default="#024248"
    )
    
    subtitle = RichTextBlock(
        required=False, 
        label="Subtítulo da Seção",
        default="<p>Subtítulo da seção com informações relevantes.</p>"
    )

    show_button = blocks.BooleanBlock(
        required=False,
        label="Mostrar Botão",
        default=False,
        help_text="Marque para exibir o botão."
    )
    
    # Cards como itens internos (sem campo de cor individual)
    cards = ListBlock(
        StructBlock([
            ('title', CharBlock(
                required=False, 
                label="Título do Card", 
                default="Título do Card"
            )),
            ('description', RichTextBlock(
                required=False, 
                label="Descrição do Card", 
                default="<p>Descrição detalhada do card com informações importantes para o usuário.</p>"
            )),
            ('icon_class', CharBlock(
                required=True, 
                label="Classe do Ícone", 
                help_text="Cole o código do Font Awesome aqui (ex: 'fa-solid fa-book')",
                default="fa-solid fa-star"
            )),
            ('link_text', CharBlock(
                required=False, 
                label="Texto do Link", 
                default="Acessar"
            )),
            ('link_url', URLBlock(
                required=False, 
                label="URL do Link", 
                default="https://gov.br/"
            )),
        ]),
        label="Cards",
        help_text="Adicione os cards da seção (a cor será aplicada automaticamente)"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/section_card_title_center.html'
        icon = 'placeholder'
        label = 'Seção: Título Subtítulo Centralizados e Cards com icones'




class SectionTabsCardsBlock(StructBlock):
    """Componente de seção com abas e cards dinâmicos."""
    # Campos da seção
    title = CharBlock(required=True, label="Título da Seção", default="Título da Seção")
    highlight_text = CharBlock(
        required=False, 
        label="Texto Destacado", 
        help_text="Parte do título que terá gradiente (opcional)",
        default=""
    )
    subtitle = RichTextBlock(
        required=True, 
        label="Subtítulo da Seção",
        default="<p>Subtítulo da seção com informações relevantes.</p>"
    )
    
    # Configuração das abas
    tabs = ListBlock(
        StructBlock([
            ('tab_title', CharBlock(required=True, label="Título da Aba", default="Título da Aba")),
            ('is_default_active', BooleanBlock(required=False, label="Ativar por padrão", default=False)),
            ('cards', ListBlock(
                StructBlock([
                    ('title', CharBlock(required=False, label="Título do Card", default="Título do Card")),
                    ('description', RichTextBlock(
                        required=False, 
                        label="Descrição do Card", 
                        default="<p>Descrição detalhada do card com informações importantes para o usuário.</p>"
                    )),
                    ('icon_class', CharBlock(
                        required=False, 
                        label="Classe do Ícone", 
                        help_text="Cole o código do Font Awesome aqui (ex: 'fa-solid fa-book')",
                        default="fa-solid fa-star"
                    )),
                    ('link_text', CharBlock(required=False, label="Texto do Link", default="Acessar")),
                    ('link_url', URLBlock(required=False, label="URL do Link", default="https://gov.br/")),
                    ('highlight_color', CharBlock(
                        required=True, 
                        label="Cor de Destaque", 
                        help_text="Insira um código de cor HEX (ex: #5E17EB)",
                        default="#FF7E38"
                    )),
                ]),
                label="Cards",
                default=[]
            )),
            ('layout_type', ChoiceBlock(
                choices=[
                    ('grid', 'Grid - Cards em forma de grade'),
                    ('list', 'Lista - Cards em formato de lista')
                ],
                default='grid',
                label="Tipo de Layout"
            )),
            ('columns', ChoiceBlock(
                choices=[
                    ('2', '2 Colunas'),
                    ('3', '3 Colunas'),
                    ('4', '4 Colunas'),
                    ('5', '5 Colunas')
                ],
                default='3',
                label="Número de Colunas"
            )),
        ]),
        label="Abas",
        default=[]
    )
    
    # Estilo personalizado
    primary_color = ChoiceBlock(
        choices=[
            ('#024248', 'Verde ENAP (#024248)'),
            ('#007D7A', 'Verde Link ENAP (#007D7A)'),
            ('#AD6BFC', 'Roxo Gnova (#AD6BFC)'),
            ('#B396FC', 'Roxo Claro Gnova (#B396FC)'),
            ('#FFFFFF', 'Branco (#FFFFFF)'),
        ],
        required=True, 
        label="Cor Primária", 
        help_text="Selecione a cor principal do componente",
        default="#024248"
    )
    
    secondary_color = ChoiceBlock(
        choices=[
            ('#024248', 'Verde ENAP (#024248)'),
            ('#007D7A', 'Verde Link ENAP (#007D7A)'),
            ('#AD6BFC', 'Roxo Gnova (#AD6BFC)'),
            ('#B396FC', 'Roxo Claro Gnova (#B396FC)'),
            ('#FFFFFF', 'Branco (#FFFFFF)'),
        ],
        required=True, 
        label="Cor Secundária", 
        help_text="Selecione a cor secundária do componente",
        default="#007D7A"
    )
    
    background_color = CharBlock(
        required=True, 
        label="Cor de Fundo", 
        help_text="Cor de fundo da seção (ex: #FFFFFF)",
        default="#FFFFFF"
    )

    class Meta:
        template = 'enap_designsystem/blocks/section_tabs_cards.html'
        icon = 'table'
        label = 'Seção de tabs com cards'




class CTAImagemBlock(blocks.StructBlock):
    # Content fields
    badge_text = blocks.CharBlock(
        default="Novidade", 
        max_length=50,
        label="Texto do Badge",
        help_text="Texto que aparece no badge superior"
    )
    
    title = blocks.CharBlock(
        default="Conheça a", 
        max_length=100,
        label="Título Principal",
        help_text="Primeira parte do título"
    )
    
    highlighted_title = blocks.CharBlock(
        default="Biblioteca do Futuro", 
        required=False, 
        max_length=100, 
        label="Título Destacado",
        help_text="Parte do título que terá gradiente (opcional)"
    )
    
    description = blocks.RichTextBlock(
        default="Uma iniciativa da Diretoria de Inovação que nasce da necessidade e do desejo de transformar a biblioteca em um espaço de construção de conhecimento, colaboração e inovação.",
        label="Descrição",
        help_text="Texto descritivo do CTA"
    )
    
    button_text = blocks.CharBlock(
        default="Saiba mais", 
        max_length=50,
        label="Texto do Botão"
    )
    
    button_link = blocks.URLBlock(
        default="google.com",
        label="Link do Botão"
    )
    
    # Color settings
    gradient_start_color = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor Inicial do Gradiente", 
        help_text="Cor inicial do gradiente do título destacado",
        default="#024248"
    )
    
    gradient_end_color = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor Final do Gradiente", 
        help_text="Cor final do gradiente do título destacado",
        default="#007D7A"
    )
    
    button_color = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor do Botão", 
        help_text="Cor de fundo do botão",
        default="#024248"
    )
    
    button_text_color = blocks.ChoiceBlock(
        choices=[
            ('#FFFFFF', 'Branco (#FFFFFF)'),
            ('#000000', 'Preto (#000000)'),
        ] + BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor do Texto do Botão", 
        help_text="Cor do texto do botão",
        default="#FFFFFF"
    )
    
    # Images
    top_image = ImageChooserBlock(
        required=True, 
        label="Imagem Superior",
        help_text="Imagem que aparece na parte superior"
    )
    
    bottom_image = ImageChooserBlock(
        required=True, 
        label="Imagem Inferior", 
        help_text="Imagem que aparece na parte inferior"
    )

    class Meta:
        template = 'enap_designsystem/blocks/cta_imagem_block.html'
        icon = 'image'
        label = 'CTA: Background Degradê - Tag, Título, Descrição - Imagens Sobrepostas'
        group = 'Custom Blocks'


# Definindo as cores da marca para reutilização
BRAND_COLOR_CHOICES = [
    ('#024248', 'Verde ENAP (#024248)'),
    ('#007D7A', 'Verde Link ENAP (#007D7A)'),
    ('#AD6BFC', 'Roxo Gnova (#AD6BFC)'),
    ('#B396FC', 'Roxo Claro Gnova (#B396FC)'),
    ('#FFFFFF', 'Branco (#FFFFFF)'),
]

class ContainerInfo(blocks.StructBlock):
    # Header content
    title_prefix = blocks.CharBlock(
        default="Nossas", 
        max_length=100,
        label="Prefixo do Título",
        help_text="Primeira parte do título"
    )
    
    title_highlight = blocks.CharBlock(
        default="Titulo Destacado", 
        max_length=100,
        label="Título Destacado",
        help_text="Parte do título que terá destaque visual"
    )
    
    description = blocks.TextBlock(
        default="Acesse bases de dados com livros e periódicos eletrônicos, nacionais e internacionais, sobre administração pública e áreas correlatas",
        label="Descrição",
        help_text="Texto descritivo da seção"
    )
    
    # Color settings
    highlight_color = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor principal do componente aplicada aos elementos destacados",
        default="#024248"
    )
    
    # Main content as StreamField
    content_sections = blocks.StreamBlock([
        ('section', blocks.StructBlock([
            ('database_title', blocks.CharBlock(
                default="Portal de Periódicos da Capes", 
                max_length=100,
                label="Título da Base de Dados"
            )),
            ('database_description', blocks.TextBlock(
                default="A Biblioteca da Enap disponibiliza acesso a bases de dados com livros e periódicos eletrônicos, nacionais e internacionais. O acesso ao Portal é vinculado à rede da Enap, mas alunos, pesquisadores, professores e servidores têm acesso remoto.",
                label="Descrição da Base de Dados"
            )),
            ('cards', blocks.ListBlock(
                blocks.StructBlock([
                    ('name', blocks.CharBlock(
                        default="JSTOR", 
                        max_length=100,
                        label="Nome da Base"
                    )),
                    ('info', blocks.TextBlock(
                        default="Base multidisciplinar com mais de 2.600 periódicos acadêmicos, livros e fontes primárias.",
                        label="Informações da Base"
                    )),
                    ('link', blocks.URLBlock(
                        default="https://www.jstor.org/", 
                        required=False, 
                        label="Link da Base",
                        help_text="Link para acessar a base de dados"
                    )),
                ]),
                label="Cards das Bases"
            )),
        ], label="Seção de Base de Dados")),
    ], label="Seções de Conteúdo")

    class Meta:
        template = 'enap_designsystem/blocks/container_info_block.html'
        icon = 'database'
        label = 'Informativo: Título, Descrição e Cards'
        group = 'Custom Blocks'





class ContatoBlock(blocks.StructBlock):
    # Header content
    title_prefix = blocks.CharBlock(default="Fale", max_length=100)
    title_highlight = blocks.CharBlock(default="Conosco", max_length=100)
    description = blocks.TextBlock(default="Entre em contato com a Biblioteca Graciliano Ramos")
    
    # Contact details
    phone_title = blocks.CharBlock(default="Telefone", max_length=100)
    phone = blocks.CharBlock(default="(61) 2020-3139", required=False)
    
    email_title = blocks.CharBlock(default="E-mail", max_length=100)
    email = blocks.CharBlock(default="biblioteca@enap.gov.br", required=False)
    
    address_title = blocks.CharBlock(default="Endereço", max_length=100)
    address = blocks.TextBlock(default="SPO Área Especial 2A - Térreo\nBrasília-DF - CEP: 70610-900", required=False)
    
    hours_title = blocks.CharBlock(default="Horário de Funcionamento", max_length=100)
    hours = blocks.TextBlock(default="Segunda a sexta-feira das 9h às 19h00", required=False)
    
    # Map
    map_embed_url = blocks.URLBlock(default="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3839.7410214087293!2d-47.91252422392779!3d-15.783966284838556!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x935a3aec4bdd315d%3A0xe4b35324fd775722!2sEscola%20Nacional%20de%20Administra%C3%A7%C3%A3o%20P%C3%BAblica%20(Enap)!5e0!3m2!1spt-BR!2sbr!4v1650293487600!5m2!1spt-BR!2sbr", required=True)
    
    # Color settings
    highlight_color = blocks.ChoiceBlock(choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor do Botão", 
        help_text="Cor de fundo do botão",
        default="#024248")

    class Meta:
        template = 'enap_designsystem/blocks/contato_block.html'
        icon = 'mail'
        label = 'Bloco de Contato'
        group = 'Custom Blocks'




class FormContato(blocks.StructBlock):
    """
    Componente de formulário de contato com personalização de cor.
    """
    cor_primaria = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    titulo = blocks.CharBlock(
        default="Fale Conosco",
        help_text="Título principal do formulário",
        required=False
    )
    
    subtitulo = blocks.TextBlock(
        default="Entre em contato conosco para esclarecer dúvidas, enviar sugestões ou solicitar informações.",
        help_text="Texto de introdução",
        required=False
    )
    
    # Campos do lado esquerdo (formulário)
    titulo_formulario = blocks.CharBlock(
        default="Envie sua mensagem",
        help_text="Título da seção do formulário"
    )
    
    mostrar_texto_obrigatorio = blocks.BooleanBlock(
        default=True,
        required=False,
        help_text="Exibir texto informando sobre campos obrigatórios"
    )
    
    texto_obrigatorio = blocks.CharBlock(
        default="* Campo obrigatório",
        help_text="Texto exibido para informar sobre campos obrigatórios",
        required=False
    )
    
    texto_botao = blocks.CharBlock(
        default="Enviar mensagem",
        help_text="Texto do botão de envio"
    )
    
    mostrar_checkbox_copia = blocks.BooleanBlock(
        default=True,
        required=False,
        help_text="Exibir opção para enviar cópia para o remetente"
    )
    
    texto_checkbox_copia = blocks.CharBlock(
        default="Enviar cópia para mim (opcional)",
        help_text="Texto da opção para enviar cópia",
        required=False
    )
    
    # Campos do lado direito (informações de contato)
    titulo_informacoes = blocks.CharBlock(
        default="Informações de Contato",
        help_text="Título da seção de informações de contato"
    )
    
    endereco_titulo = blocks.CharBlock(
        default="Campus Asa Sul",
        help_text="Título do endereço",
        required=False
    )
    
    endereco = blocks.CharBlock(
        default="SAIS AE 2A Térreo - Enap Campus Asa Sul – Brasília-DF",
        help_text="Endereço completo",
        required=False
    )
    
    horario_titulo = blocks.CharBlock(
        default="Horário de Funcionamento",
        help_text="Título do horário de funcionamento",
        required=False
    )
    
    horario = blocks.CharBlock(
        default="Segunda a sexta-feira das 9h às 18h00",
        help_text="Horário de funcionamento",
        required=False
    )
    
    telefone_titulo = blocks.CharBlock(
        default="Telefone",
        help_text="Título do telefone",
        required=False
    )
    
    telefone = blocks.CharBlock(
        default="(61) 2020-3139",
        help_text="Número de telefone",
        required=False
    )
    
    email_titulo = blocks.CharBlock(
        default="E-mail",
        help_text="Título do e-mail",
        required=False
    )
    
    email = blocks.CharBlock(
        default="biblioteca@enap.gov.br",
        help_text="Endereço de e-mail",
        required=False
    )
    
    # Mapa e localização
    mostrar_mapa = blocks.BooleanBlock(
        default=True,
        required=False,
        help_text="Exibir mapa de localização"
    )
    
    imagem_mapa = ImageChooserBlock(
        required=False,
        help_text="Imagem do mapa (opcional, se preferir usar uma imagem estática)"
    )
    
    link_mapa = blocks.URLBlock(
        default="https://maps.google.com",
        help_text="Link para o mapa (ex: Google Maps)",
        required=False
    )
    
    texto_link_mapa = blocks.CharBlock(
        default="Visualizar Localização - Google Maps",
        help_text="Texto do link para o mapa",
        required=False
    )

    class Meta:
        template = "enap_designsystem/blocks/form_contato.html"
        icon = "mail"
        label = "Formulário de Contato"
        help_text = "Adiciona um formulário de contato com informações e newsletter"

    def clean(self, value):
        cleaned_data = super().clean(value)
        errors = {}
        
        # Validação de cor hexadecimal
        cor_primaria = cleaned_data.get('cor_primaria', '')
        if not cor_primaria.startswith('#') or len(cor_primaria) != 7:
            errors['cor_primaria'] = ErrorList(['Formato de cor inválido. Use o formato hexadecimal (ex: #5e17eb)'])
        
        if errors:
            raise blocks.StructBlockValidationError(errors)
        
        return cleaned_data
    




class SobreLinhas(blocks.StructBlock):
    """
    Componente para exibir seções com títulos, ícones FontAwesome e conteúdo em formato de linhas.
    """
    cor_primaria = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    cor_secundaria = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    titulo = blocks.CharBlock(
        default="Sobre a Biblioteca",
        help_text="Título principal da página"
    )
    
    palavra_destaque = blocks.CharBlock(
        default="Biblioteca",
        help_text="Palavra do título que será destacada com gradiente"
    )
    
    subtitulo = blocks.TextBlock(
        default="Referência em Administração Pública e Gestão Governamental",
        help_text="Subtítulo ou descrição breve"
    )
    
    secoes = blocks.ListBlock(
        blocks.StructBlock([
            ('icone_fa', blocks.CharBlock(
                default="book",
                help_text="Código do ícone do FontAwesome (ex: book, home). Use apenas o nome sem 'fa-'."
            )),
            ('titulo_secao', blocks.CharBlock(
                default="Título da Seção",
                help_text="Título desta seção"
            )),
            ('conteudo', blocks.RichTextBlock(
                default="<p>Conteúdo da seção...</p>",
                help_text="Conteúdo detalhado desta seção"
            )),
        ]),
        min_num=1,
        help_text="Adicione seções com ícones, títulos e conteúdo"
    )
    
    mostrar_botao_acao = blocks.BooleanBlock(
        default=True,
        required=False,
        help_text="Exibir botão de ação ao final"
    )
    
    texto_botao = blocks.CharBlock(
        default="Acesse o Regulamento",
        help_text="Texto do botão de ação",
        required=False
    )
    
    link_botao = blocks.URLBlock(
        default="#",
        help_text="Link para onde o botão direciona",
        required=False
    )
    
    class Meta:
        icon = "doc-full"
        label = "Sobre em Tópicos"
        help_text = "Cards com ícones e cor variavel"
        template = "enap_designsystem/blocks/sobre_linhas.html"
        
    def clean(self, value):
        cleaned_data = super().clean(value)
        errors = {}
        
        # Validação de cor hexadecimal para cor primária
        cor_primaria = cleaned_data.get('cor_primaria', '')
        if not cor_primaria.startswith('#') or len(cor_primaria) != 7:
            errors['cor_primaria'] = ErrorList(['Formato de cor inválido. Use o formato hexadecimal (ex: #5e17eb)'])
            
        # Validação de cor hexadecimal para cor secundária (se fornecida)
        cor_secundaria = cleaned_data.get('cor_secundaria', '')
        if cor_secundaria and (not cor_secundaria.startswith('#') or len(cor_secundaria) != 7):
            errors['cor_secundaria'] = ErrorList(['Formato de cor inválido. Use o formato hexadecimal (ex: #ff5a5f)'])
        
        # Validação da palavra de destaque
        palavra_destaque = cleaned_data.get('palavra_destaque', '')
        titulo = cleaned_data.get('titulo', '')
        if palavra_destaque and palavra_destaque not in titulo:
            errors['palavra_destaque'] = ErrorList(['A palavra de destaque deve estar presente no título.'])
        
        if errors:
            raise blocks.StructBlockValidationError(errors)
        
        return cleaned_data
    




class EventoBlock(blocks.StructBlock):
    """Bloco para exibir eventos com filtros de categoria"""
    
    titulo_secao = blocks.CharBlock(
        default="Próximos Eventos",
        label="Título da Seção",
        help_text="Título que aparecerá no topo da seção de eventos"
    )
    
    descricao_secao = blocks.TextBlock(
        default="Participe de nossa programação diversificada de eventos presenciais e online",
        label="Descrição da Seção",
        help_text="Texto que aparecerá abaixo do título da seção"
    )
    
    cor_principal = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    # Sem o campo de cor individual para cada categoria
    categorias = blocks.ListBlock(
        blocks.StructBlock([
            ('nome', blocks.CharBlock(label="Nome da Categoria", default="Todos")),
        ]),
        label="Categorias de Eventos",
        help_text="Defina as categorias que serão usadas para filtrar os eventos"
    )
    
    eventos = blocks.ListBlock(
        blocks.StructBlock([
            ('titulo', blocks.CharBlock(label="Título do Evento", default="Novo Evento")),
            ('categoria', blocks.CharBlock(
                label="Categoria",
                help_text="Deve corresponder exatamente ao nome de uma categoria definida acima", default="Geral"
            )),
            ('imagem', ImageChooserBlock(label="Imagem do Evento", required=False)),
            ('data', blocks.DateBlock(label="Data do Evento", default=date.today())),
            ('hora_inicio', blocks.TimeBlock(label="Hora de Início", default=time(9, 0))),
            ('hora_fim', blocks.TimeBlock(label="Hora de Término", default=time(17, 0))),
            ('local', blocks.CharBlock(label="Local", default="A definir")),
            ('descricao', blocks.TextBlock(label="Descrição do Evento", default="Descrição do evento será adicionada em breve.")),
            ('vagas_disponiveis', blocks.IntegerBlock(label="Vagas Disponíveis", min_value=0, default=50)),
        ]),
        label="Lista de Eventos",
        help_text="Adicione os eventos que serão exibidos"
    )
    
    class Meta:
        template = "enap_designsystem/blocks/evento_block.html"
        icon = "date"
        label = "Bloco de Eventos com Filtro"
        
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        
        # Gerar slugs automaticamente para as categorias que não possuem
        categorias = []
        for categoria in value['categorias']:
            cat = dict(categoria)
            if not cat.get('slug'):
                cat['slug'] = slugify(cat.get('nome', ''))
            categorias.append(cat)
        
        # Vamos ordenar os eventos por data
        eventos_ordenados = sorted(
            value['eventos'], 
            key=lambda e: datetime.combine(e['data'], e['hora_inicio'])
        )
        
        # Organizando eventos por categoria
        eventos_por_categoria = {}
        for evento in eventos_ordenados:
            categoria = evento['categoria']
            if categoria not in eventos_por_categoria:
                eventos_por_categoria[categoria] = []
            eventos_por_categoria[categoria].append(evento)
            
        context['categorias'] = categorias
        context['eventos_ordenados'] = eventos_ordenados
        context['eventos_por_categoria'] = eventos_por_categoria
        context['cor_principal'] = value.get('cor_principal', '#3f51b5')
        
        return context
    




class HeroAnimadaBlock(blocks.StructBlock):
    """Bloco para exibir um banner animado com imagem e conteúdo"""
    
    titulo = blocks.CharBlock(
        default="Biblioteca do Futuro",
        label="Título",
        help_text="Título principal do banner"
    )
    
    texto_destaque = blocks.CharBlock(
        default="Futuro",
        label="Texto com Destaque",
        help_text="Parte do título que receberá o efeito gradiente"
    )
    
    descricao = blocks.TextBlock(
        default="Reimaginando a experiência da biblioteca tradicional com tecnologia",
        label="Descrição",
        help_text="Texto descritivo que aparecerá abaixo do título"
    )
    
    badge_texto = blocks.CharBlock(
        default="Novo Projeto",
        label="Texto do Badge",
        help_text="Texto que aparece no badge acima do título",
        required=False
    )
    
    imagem = ImageChooserBlock(
        label="Imagem do Banner",
        help_text="Selecione uma imagem para o lado direito do banner"
    )
    
    botao_principal_texto = blocks.CharBlock(
        default="Ver Próximos Eventos",
        label="Texto do Botão Principal",
        help_text="Texto do botão principal"
    )
    
    botao_principal_link = blocks.CharBlock(
        default="#eventos",
        label="Link do Botão Principal",
        help_text="Link para onde o botão principal levará (URL ou #anchor)"
    )
    
    botao_secundario_texto = blocks.CharBlock(
        default="Saiba Mais",
        label="Texto do Botão Secundário",
        help_text="Texto do botão secundário",
        required=False
    )
    
    botao_secundario_link = blocks.CharBlock(
        default="#sobre",
        label="Link do Botão Secundário",
        help_text="Link para onde o botão secundário levará (URL ou #anchor)",
        required=False
    )
    
    cor_principal = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    cor_secundaria = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    class Meta:
        template = "enap_designsystem/blocks/hero_animada_block.html"
        icon = "view"
        label = "Seção Background Duas Colunas Tag Título e Imagem"
        
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context['cor_principal'] = value.get('cor_principal', '#4F46E5')
        context['cor_secundaria'] = value.get('cor_secundaria', '#9333EA')
        return context
    



class BannerSearchBlock(blocks.StructBlock):
    """Banner com destaque e campo de busca para bibliotecas"""
    
    # Cores personalizáveis
    cor_primaria = blocks.CharBlock(
        default="#FF7E38",
        label="Cor Primária",
        help_text="Cor principal para textos e elementos (ex: #4a4a4a)"
    )
    
    cor_secundaria = blocks.CharBlock(
        default="#FF8502",
        label="Cor Secundária",
        help_text="Cor de destaque para títulos e botões (ex: #FF8502)"
    )
    
    cor_accent = blocks.CharBlock(
        default="#FFA135",
        label="Cor de Hover",
        help_text="Cor para efeitos de hover (ex: #FFA135)"
    )
    
    # Conteúdo textual
    titulo_principal = blocks.CharBlock(
        default="Descubra a",
        label="Título Principal",
        help_text="Primeira parte do título do banner"
    )
    
    titulo_destaque = blocks.CharBlock(
        default="Biblioteca Graciliano Ramos",
        label="Título em Destaque",
        help_text="Segunda parte do título que aparecerá com destaque"
    )
    
    subtitulo = blocks.TextBlock(
        default="Referência em Administração Pública e Gestão Governamental com mais de 29 mil obras em seu acervo",
        label="Subtítulo",
        help_text="Texto descritivo abaixo do título"
    )

    imagem_background = ImageChooserBlock(
    label="Imagem de Fundo",
    help_text="Imagem que será utilizada como fundo do banner",
    required=False
    )
    
    # Campo de busca
    texto_placeholder = blocks.CharBlock(
        default="O que você procura? Digite palavras-chave...",
        label="Texto do Placeholder",
        help_text="Texto que aparecerá como sugestão no campo de busca"
    )
    
    texto_botao = blocks.CharBlock(
        default="Buscar",
        label="Texto do Botão",
        help_text="Texto que aparecerá no botão de busca"
    )
    
    url_busca = blocks.CharBlock(
        default="/busca/",
        label="URL da Busca",
        help_text="URL para onde o formulário de busca será enviado"
    )
    
    # Badge de informação
    texto_badge = blocks.CharBlock(
        default="Segunda a sexta das 9h às 19h",
        label="Texto do Badge Informativo",
        help_text="Texto que aparecerá como informação adicional",
        required=False
    )
    
    # Imagem principal
    imagem_principal = ImageChooserBlock(
        label="Imagem Principal",
        help_text="Imagem que aparecerá no lado direito do banner"
    )
    
    # Badges flutuantes
    mostrar_badges = blocks.BooleanBlock(
        default=True,
        label="Mostrar Badges Flutuantes",
        help_text="Mostrar os badges de informação flutuantes ao redor da imagem",
        required=False
    )
    
    badge1_icone = blocks.CharBlock(
        default="📚",
        label="Ícone do Badge 1",
        help_text="Emoji ou ícone para o primeiro badge",
        required=False
    )
    
    badge1_texto = blocks.CharBlock(
        default="29 mil obras impressas",
        label="Texto do Badge 1",
        help_text="Texto que aparecerá no primeiro badge",
        required=False
    )
    
    badge2_icone = blocks.CharBlock(
        default="🌐",
        label="Ícone do Badge 2",
        help_text="Emoji ou ícone para o segundo badge",
        required=False
    )
    
    badge2_texto = blocks.CharBlock(
        default="Acervo digital completo",
        label="Texto do Badge 2",
        help_text="Texto que aparecerá no segundo badge",
        required=False
    )
    
    class Meta:
        template = "enap_designsystem/blocks/banner_search_block.html"
        icon = "search"
        label = "Banner com Busca"
        
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context['cor_primaria'] = value.get('cor_primaria')
        context['cor_secundaria'] = value.get('cor_secundaria')
        context['cor_accent'] = value.get('cor_accent')
        return context
    




class NavbarComponent(blocks.StructBlock):

    # Logo settings
    logo = ImageChooserBlock(required=False, help_text="Upload your logo image")
    
    # Border
    border_color = blocks.CharBlock(
        required=False, 
        default="#FF7E38",
        help_text="Color code for the 7px bottom border and hover effects (e.g. #3182ce)"
    )
    
    # Button
    portal_text = blocks.CharBlock(
        required=False, 
        default="Portal",
        help_text="Text for the portal button"
    )
    portal_url = blocks.CharBlock(
        required=False, 
        default="#",
        help_text="URL for the portal button"
    )
    
    # Menu items
    menu_items = blocks.ListBlock(
        blocks.StructBlock([
            ('text', blocks.CharBlock(required=False, help_text="Menu item text")),
            ('url', blocks.CharBlock(required=False, help_text="Menu item URL")),
            ('featured', blocks.BooleanBlock(required=False, help_text="Highlight this menu item"))
        ]),
        default=[
            {'text': 'Início', 'url': '#', 'featured': False},
            {'text': 'Acervo', 'url': '#acervo', 'featured': False},
            {'text': 'Áreas Temáticas', 'url': '#areas-tematicas', 'featured': False},
            {'text': 'Bases de Dados', 'url': '#bases-dados', 'featured': False},
            {'text': 'Sobre', 'url': '#sobre', 'featured': False},
            {'text': 'Contato', 'url': '#contato', 'featured': False}
        ]
    )
    
    class Meta:
        template = "enap_designsystem/blocks/navbar_component.html"
        icon = "site"
        label = "Navbar Component"






class SecaoAdesaoBlock(blocks.StructBlock):
    """
    Seção de grade com duas colunas (1fr 1fr) para apresentar informações sobre adesão 
    ao programa com um cartão de destaque verde.
    """
    # Coluna 1 - Conteúdo informativo
    titulo_informativo = blocks.CharBlock(
        required=True,
        max_length=100,
        default="Como aderir ao Enap Aqui?",
        help_text="Título da seção informativa (coluna esquerda)",
        verbose_name="Título"
    )
    
    texto_informativo = blocks.RichTextBlock(
        required=True,
        default=(
            "<p>A adesão ao Programa Enap Aqui é feita por meio da assinatura de "
            "um Acordo de Adesão, formalizado pela instituição interessada.</p>"
            "<p>O Acordo de Adesão ao Enap Aqui expressa o compromisso da instituição "
            "com a promoção de ações formativas voltadas a servidores públicos locais, "
            "por meio de uma abordagem híbrida que integra cursos a distância e oficinas "
            "presenciais, com foco em temas estratégicos para a gestão pública.</p>"
        ),
        help_text="Texto explicativo sobre o processo de adesão",
        verbose_name="Texto informativo"
    )
    
    # Coluna 2 - Cartão verde com call-to-action
    titulo_destaque = blocks.CharBlock(
        required=True,
        max_length=100,
        default="Torne-se um parceiro Enap Aqui",
        help_text="Título do cartão verde de destaque",
        verbose_name="Título do destaque"
    )
    
    texto_destaque = blocks.RichTextBlock(
        required=True,
        default="<p>Faça parte do Enap Aqui e acompanhe o processo:</p>",
        help_text="Texto curto para o cartão verde de destaque",
        verbose_name="Texto do destaque"
    )
    
    # NOVO: StreamBlock para múltiplos botões
    botoes = blocks.StreamBlock([
        ('botao', blocks.StructBlock([
            ('texto', blocks.CharBlock(
                max_length=50,
                help_text="Texto que será exibido no botão",
                verbose_name="Texto do botão"
            )),
            ('url', blocks.URLBlock(
                help_text="URL para onde o botão vai redirecionar",
                verbose_name="URL do botão"
            )),
            ('estilo', blocks.ChoiceBlock(
                choices=[
                    ('primario', 'Primário (destaque)'),
                    ('secundario', 'Secundário (outline)'),
                    ('terciario', 'Terciário (texto apenas)'),
                ],
                default='primario',
                help_text="Estilo visual do botão",
                verbose_name="Estilo do botão"
            )),
            ('abrir_nova_aba', blocks.BooleanBlock(
                required=False,
                default=False,
                help_text="Marque para abrir o link em uma nova aba",
                verbose_name="Abrir em nova aba"
            )),
            ('icone', blocks.CharBlock(
                required=False,
                max_length=50,
                help_text="Nome do ícone FontAwesome (ex: 'download', 'external-link-alt')",
                verbose_name="Ícone (opcional)"
            )),
        ], label="Botão"))
    ],
    min_num=1,
    max_num=4,
    help_text="Adicione até 4 botões para o cartão de destaque",
    verbose_name="Botões de ação"
    )
    
    # Layout dos botões
    layout_botoes = blocks.ChoiceBlock(
        choices=[
            ('vertical', 'Vertical (um abaixo do outro)'),
            ('horizontal', 'Horizontal (lado a lado)'),
            ('grid', 'Grade 2x2'),
        ],
        default='vertical',
        help_text="Como organizar os botões no cartão",
        verbose_name="Layout dos botões"
    )
    
    # Personalização (opcional)
    cor_fundo_destaque = blocks.CharBlock(
        required=False,
        max_length=7,
        default="#1F4D4D",
        help_text="Código hexadecimal da cor de fundo do cartão verde (ex: #1F4D4D)",
        verbose_name="Cor de fundo do destaque"
    )
    
    espaco_vertical = blocks.ChoiceBlock(
        choices=[
            ('pequeno', 'Pequeno'),
            ('medio', 'Médio'),
            ('grande', 'Grande'),
        ],
        default='medio',
        help_text="Espaçamento vertical da seção",
        verbose_name="Espaçamento"
    )
    

    class Meta:
        template = "enap_designsystem/blocks/cartao_destacado.html"
        icon = "placeholder"
        label = "Seção Duas Colunas Texto e Card Colorido"
        verbose_name = "Seção Duas Colunas Texto e Card Colorido com Múltiplos Botões"



class TextoImagemBlock(blocks.StructBlock):
    """
    Componente simples de duas colunas com texto e imagem
    """
    # Coluna de texto
    titulo = blocks.CharBlock(
        required=True,
        max_length=400,
        help_text="Título da seção",
        verbose_name="Título"
    )
    
    texto = blocks.RichTextBlock(
        required=True,
        help_text="Conteúdo em texto",
        verbose_name="Texto"
    )
    
    # Configuração de botão (opcional)
    incluir_botao = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Marque para incluir um botão de ação",
        verbose_name="Incluir botão"
    )
    
    texto_botao = blocks.CharBlock(
        required=False,
        max_length=50,
        help_text="Texto que aparecerá no botão (ex: 'Saiba mais', 'Ver detalhes')",
        verbose_name="Texto do botão"
    )
    
    link_botao = blocks.URLBlock(
        required=False,
        help_text="URL para onde o botão deve direcionar",
        verbose_name="Link do botão"
    )
    
    estilo_botao = blocks.ChoiceBlock(
        choices=[
            ('primario', 'Primário (destaque)'),
            ('secundario', 'Secundário'),
            ('outline', 'Contorno'),
            ('link', 'Estilo link'),
        ],
        default='primario',
        required=False,
        help_text="Estilo visual do botão",
        verbose_name="Estilo do botão"
    )
    
    # Coluna de imagem
    imagem = ImageChooserBlock(
        required=True,
        help_text="Imagem de destaque",
        verbose_name="Imagem"
    )
    
    # Opções de layout
    posicao_imagem = blocks.ChoiceBlock(
        choices=[
            ('direita', 'Imagem à direita'),
            ('esquerda', 'Imagem à esquerda'),
        ],
        default='direita',
        help_text="Posição da imagem em relação ao texto",
        verbose_name="Posição da imagem"
    )
    
    estilo_imagem = blocks.ChoiceBlock(
        choices=[
            ('normal', 'Normal'),
            ('arredondada', 'Cantos arredondados'),
            ('circular', 'Circular'),
            ('cobertura', 'Cobertura completa'),
        ],
        default='normal',
        help_text="Estilo de exibição da imagem",
        verbose_name="Estilo da imagem"
    )
    
    # Definições da classe
    class Meta:
        template = "enap_designsystem/blocks/texto_imagem.html"
        icon = "image"
        label = "Texto e Imagem"
        verbose_name = "Bloco de Texto com Imagem"
        help_text = "Bloco de duas colunas com título, texto, imagem e botão opcional"
    
    def clean(self, value):
        """
        Validação customizada: se incluir_botao for True,
        texto_botao deve ser obrigatório
        """
        cleaned_data = super().clean(value)
        
        if cleaned_data.get('incluir_botao') and not cleaned_data.get('texto_botao'):
            raise blocks.ValidationError('Texto do botão é obrigatório quando "Incluir botão" está marcado')
            
        return cleaned_data



class CardCursoBlock(BaseBlock):
    """
    A component for displaying course information.
    """
    type = blocks.ChoiceBlock(
        choices=[
            ('card-curso-em-breve', 'Curso em breve'),
            ('card-curso-aberto', 'Curso aberto'),
            ('card-curso-andamento', 'Curso em andamento'),
            ('card-curso-encerrado', 'Curso encerrado'),
        ],
        default='card-curso-em-breve',
        help_text="Escolha o status do curso",
        label="Status do curso"
    )

    title = blocks.CharBlock(
        required=True,
        max_length=255,
        label="Título do curso",
        default="Curso de Exemplo", 
    )
    
    description = blocks.RichTextBlock(
        features=["bold", "italic", "ol", "ul", "hr", "link", "document-link"],
        label="Descrição",
        default="Descrição do curso de exemplo.",
    )
    
    carga_horaria = blocks.CharBlock(
        required=True,
        max_length=50,
        label="Carga horária",
        default="40 horas", 
    )
    
    modalidade = blocks.ChoiceBlock(
        choices=[
            ('presencial', 'Presencial'),
            ('online', 'Online'),
            ('hibrido', 'Híbrido'),
        ],
        default='presencial',
        label="Modalidade",
    )
    
    highlight_color = ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor que será aplicada no texto destacado e nos cards",
        default="#024248"
    )
    
    link = blocks.StreamBlock(
        [
            ("button", ButtonBlock()),
        ],
        max_num=1,
        blank=True,
        required=False,
        label="Botão (link)",
    )

    class Meta:
        template = "enap_designsystem/blocks/card_curso_block.html"
        icon = "cr-list-alt"
        label = "Card Curso (Opção online ou presencial)"





class ImagemIndividualBlock(blocks.StructBlock):
    """
    Bloco para uma imagem individual na galeria
    """
    imagem = ImageChooserBlock(
        required=True,
        label="Imagem",
        help_text="Selecione a imagem para exibir"
    )
    
    titulo = blocks.CharBlock(
        required=False,
        max_length=100,
        label="Título da imagem",
        help_text="Título opcional que aparece sobre/abaixo da imagem"
    )
    
    descricao = blocks.TextBlock(
        required=False,
        max_length=300,
        label="Descrição",
        help_text="Descrição opcional da imagem"
    )
    
    link = blocks.URLBlock(
        required=False,
        label="Link (opcional)",
        help_text="URL para onde a imagem deve levar quando clicada"
    )
    
    abrir_nova_aba = blocks.BooleanBlock(
        required=False,
        default=False,
        label="Abrir link em nova aba",
        help_text="Marque para abrir o link em uma nova aba"
    )

    class Meta:
        icon = "image"
        label = "Imagem"


class GaleriaImagensBlock(BaseBlock):
    """
    Galeria de imagens com grid configurável (1, 2, 3 ou 4 colunas)
    """
    
    titulo_secao = blocks.CharBlock(
        required=False,
        max_length=200,
        label="Título da Seção",
        help_text="Título opcional para a galeria de imagens"
    )
    
    descricao_secao = blocks.TextBlock(
        required=False,
        max_length=500,
        label="Descrição da Seção",
        help_text="Descrição opcional para a galeria"
    )
    
    grid_colunas = blocks.ChoiceBlock(
        choices=[
            ('1', '1 coluna (imagem por linha)'),
            ('2', '2 colunas'),
            ('3', '3 colunas'),
            ('4', '4 colunas'),
        ],
        default='3',
        label="Layout do Grid",
        help_text="Quantas colunas de imagens por linha"
    )
    
    imagens = blocks.StreamBlock([
        ('imagem', ImagemIndividualBlock()),
    ],
    min_num=1,
    label="Imagens da Galeria",
    help_text="Adicione quantas imagens quiser usando o botão +"
    )
    
    # Configurações visuais
    espacamento = blocks.ChoiceBlock(
        choices=[
            ('pequeno', 'Pequeno (0.5rem)'),
            ('medio', 'Médio (1rem)'),
            ('grande', 'Grande (2rem)'),
        ],
        default='medio',
        label="Espaçamento entre imagens",
        help_text="Distância entre as imagens no grid"
    )
    
    altura_imagens = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Altura automática (preserva proporção)'),
            ('quadrada', 'Quadrada (1:1)'),
            ('retangular', 'Retangular (16:9)'),
            ('paisagem', 'Paisagem (4:3)'),
            ('retrato', 'Retrato (3:4)'),
        ],
        default='auto',
        label="Formato das imagens",
        help_text="Como as imagens devem ser cortadas/exibidas"
    )
    
    mostrar_titulos = blocks.BooleanBlock(
        required=False,
        default=True,
        label="Mostrar títulos das imagens",
        help_text="Exibir os títulos abaixo das imagens"
    )
    
    mostrar_descricoes = blocks.BooleanBlock(
        required=False,
        default=False,
        label="Mostrar descrições das imagens",
        help_text="Exibir as descrições abaixo das imagens"
    )
    
    efeito_hover = blocks.ChoiceBlock(
        choices=[
            ('nenhum', 'Nenhum efeito'),
            ('zoom', 'Zoom suave'),
            ('escala', 'Escala com sombra'),
            ('overlay', 'Overlay com informações'),
        ],
        default='zoom',
        label="Efeito ao passar o mouse",
        help_text="Efeito visual quando o usuário passa o mouse sobre a imagem"
    )
    
    bordas_arredondadas = blocks.BooleanBlock(
        required=False,
        default=True,
        label="Bordas arredondadas",
        help_text="Aplicar bordas arredondadas nas imagens"
    )

    class Meta:
        template = "enap_designsystem/blocks/galeria_imagens_block.html"
        icon = "image"
        label = "Galeria de Imagens"





class CarrosselCursosBlock(StructBlock):
    """
    Um wrapper de carrossel que permite adicionar múltiplos cards de curso.
    """
    cards = StreamBlock(
        [
            ("card", CardCursoBlock()),
        ],
        min_num=1,
        label=_("Cards de Curso"),
        help_text=_("Adicione os cards de curso que deseja exibir no carrossel")
    )
    
    slidesPerView_mobile = IntegerBlock(
        default=1,
        min_value=1,
        max_value=2,
        label=_("Cards por visualização (Mobile)"),
        help_text=_("Número de cards visíveis em dispositivos móveis")
    )
    
    slidesPerView_tablet = IntegerBlock(
        default=2,
        min_value=1,
        max_value=3,
        label=_("Cards por visualização (Tablet)"),
        help_text=_("Número de cards visíveis em tablets")
    )
    
    slidesPerView_desktop = IntegerBlock(
        default=3,
        min_value=1,
        max_value=4,
        label=_("Cards por visualização (Desktop)"),
        help_text=_("Número de cards visíveis em desktops")
    )
    
    auto_play = BooleanBlock(
        default=False,
        required=False,
        label=_("Auto-play"),
        help_text=_("Ativar rolagem automática do carrossel")
    )
    
    auto_play_delay = IntegerBlock(
        default=5000,
        min_value=1000,
        help_text=_("Tempo de espera entre slides em milissegundos (1000 = 1 segundo)"),
        label=_("Tempo de auto-play"),
        required=False
    )
    
    class Meta:
        template = "enap_designsystem/blocks/carrossel_cursos_block.html"
        icon = "view"
        label = _("Carrossel de Cursos")


class AccordionItemBlock(StructBlock):
    section_title = CharBlock(
        label="Título da Seção", 
        required=False, 
        help_text="Título principal da seção de accordions (opcional)",
        default="Perguntas Frequentes"
    )
    highlight_color = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    # Lista de itens de acordeão
    accordion_items = ListBlock(
        StructBlock([
            ('accordion_title', CharBlock(
                label="Título do Accordion", 
                required=True, 
                help_text="Título que será mostrado no accordion (pergunta)",
                default="Pergunta"
            )),
            ('accordion_response', RichTextBlock(
                label="Resposta do Accordion", 
                required=True, 
                help_text="Conteúdo que será exibido quando o accordion for expandido",
                default="Resposta detalhada para a pergunta do accordion."
            ))
        ]),
        label="Itens do Accordion",
        min_num=1,
        help_text="Adicione quantas perguntas e respostas desejar"
    )
    
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context['highlight_color'] = value.get('highlight_color') or "#5e17eb"
        return context
    
    class Meta:
        template = "enap_designsystem/blocks/accordionsv2.html"
        icon = "list-ul"
        label = "Accordion v2"






class NavbarBlockv3(blocks.StructBlock):
    """Navigation bar component with customizable colors and links."""
    logo_image = ImageChooserBlock(required=True, help_text="Logo image for the navigation bar")
    primary_color = blocks.ChoiceBlock(choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor do Botão", 
        help_text="Cor de fundo do botão",
        default="#024248")
    accent_color = blocks.ChoiceBlock(choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor do Botão", 
        help_text="Cor de fundo do botão",
        default="#024248")
    button_color = blocks.ChoiceBlock(choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor do Botão", 
        help_text="Cor de fundo do botão",
        default="#024248")
    button_text_color = blocks.ChoiceBlock(choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor do Botão", 
        help_text="Cor de fundo do botão",
        default="#024248")
    
    # Auth buttons configuration
    login_button_text = blocks.CharBlock(required=True, default="Entrar", help_text="Text for the login button")
    login_button_url = blocks.URLBlock(required=True, default="google.com", help_text="URL for the login button")
    
    cta_button_text = blocks.CharBlock(required=True, default="Acervo", help_text="Text for the call-to-action button")
    cta_button_url = blocks.URLBlock(required=True, default="google.com", help_text="URL for the call-to-action button")
    
    nav_items = blocks.ListBlock(
        blocks.StructBlock([
            ('link_text', blocks.CharBlock(required=True)),
            ('link_url', blocks.URLBlock(required=True)),
            ('is_active', blocks.BooleanBlock(required=False)),
        ])
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/navbarv3.html'
        icon = 'site'
        label = 'Navbar Flutuante'





class HeroBlockv3(blocks.StructBlock):
    """Hero section with customizable colors, content, and background image."""
    
    # Content
    title = blocks.CharBlock(
        required=True, 
        label="Título Principal",
        help_text="Texto principal do hero",
        default="Texto do Título Principal",
    )
    
    subtitle = blocks.TextBlock(
        required=True, 
        label="Subtítulo",
        help_text="Texto de apoio abaixo do título",
        default="Texto do Subtítulo",
    )
    
    # Colors
    primary_color = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor Primária", 
        help_text="Cor principal dos elementos destacados",
        default="#024248"
    )
    
    accent_color = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    background_color = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=True, 
        label="Cor de Fundo", 
        help_text="Cor de fundo da seção (se não usar imagem)",
        default="#FFFFFF"
    )
    
    # Primary Button
    primary_button_text = blocks.CharBlock(
        required=False,
        max_length=50,
        label="Texto do Botão Primário",
        help_text="Texto do botão principal",
        default="Saiba mais"
    )
    
    primary_button_url = blocks.URLBlock(
        required=False,
        label="Link do Botão Primário",
        help_text="URL do botão principal",
        default="google.com"
    )
    
    # Secondary Button
    secondary_button_text = blocks.CharBlock(
        required=False,
        max_length=50,
        label="Texto do Botão Secundário",
        help_text="Texto do botão secundário",
        default="Assistir vídeo"
    )
    
    secondary_button_url = blocks.URLBlock(
        required=False, 
        label="Link do Botão Secundário",
        help_text="URL do botão secundário",
        default="google.com"
    )
    
    # Display options
    show_play_icon = blocks.BooleanBlock(
        required=False, 
        default=True,
        label="Mostrar Ícone de Play",
        help_text="Exibir ícone de play no botão secundário",
    )
    
    show_play_button = blocks.BooleanBlock(
        required=False, 
        default=True, 
        label="Mostrar Botão de Play na Imagem",
        help_text="Exibir botão de play sobreposto na imagem de fundo"
    )
    
    # Background
    background_image = ImageChooserBlock(
        required=False, 
        label="Imagem de Fundo",
        help_text="Imagem de fundo da seção hero"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/herov3.html'
        icon = 'image'
        label = 'Seção Título com Subtítulo, Botões e Play no Vídeo'



class AvisoBlock(blocks.StructBlock):
    """
    Bloco de aviso simples sem dependências adicionais
    """
    titulo = blocks.CharBlock(
        required=True,
        label="Título do Aviso",
        help_text="O título principal do aviso",
        max_length=100,
        default="Aviso Importante"
    )
    
    data = blocks.DateBlock(
    required=True,
    label="Data do Aviso", 
    help_text="Data associada ao aviso",  # ← Adicione esta vírgula
    default=date.today(),
    )
    
    texto = blocks.RichTextBlock(
        required=True,
        label="Conteúdo do Aviso",
        help_text="O texto principal do aviso",
        features=['bold', 'italic', 'link'],
        default= "Por favor, leia atentamente as informações abaixo para garantir que você esteja ciente de todas as atualizações importantes.",
    )
    
    imagem = ImageChooserBlock(
        required=False,
        label="Imagem",
        help_text="Imagem exibida ao lado do aviso"
    )
    
    cor_borda = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    tag_texto = blocks.CharBlock(
        required=True,
        label="Texto da Tag",
        help_text="O texto exibido na tag destacada (ex: Importante, Urgente)",
        default="Importante",
        max_length=20
    )
    
    cor_tag = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    botao_texto = blocks.CharBlock(
        required=True,
        label="Texto do Botão",
        help_text="O texto a ser exibido no botão",
        default="Saiba mais",
        max_length=30
    )
    
    botao_link = blocks.URLBlock(
        required=True,
        label="Link do Botão",
        help_text="URL para onde o botão direciona",
        default="google.com",
    )
    
    cor_botao = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    class Meta:
        template = "enap_designsystem/blocks/aviso_block.html"
        icon = "warning"
        label = "Aviso"
        form_classname = "aviso-block struct-block"




class GalleryModernBlock(blocks.StructBlock):
    """Bloco para exibir uma galeria moderna com carrossel e filtros por categoria"""
    
    titulo_secao = blocks.CharBlock(
        default="Galeria de Eventos",
        label="Título da Seção",
        help_text="Título que aparecerá no topo da seção de galeria"
    )
    
    subtitulo_secao = blocks.CharBlock(
        default="Biblioteca do Futuro",
        label="Subtítulo da Seção",
        help_text="Texto que aparecerá abaixo do título da seção"
    )
    
    cor_principal = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    cor_secundaria = blocks.ChoiceBlock(
        choices=BRAND_COLOR_CHOICES,
        required=True, 
        label="Cor de Destaque", 
        help_text="Cor de destaque secundária",
        default="#007D7A"
    )
    
    categorias = blocks.ListBlock(
        blocks.StructBlock([
            ('nome', blocks.CharBlock(label="Nome da Categoria" , default="Todos")),
        ]),
        label="Categorias da Galeria",
        help_text="Defina as categorias que serão usadas para filtrar os itens da galeria"
    )
    
    itens_galeria = blocks.ListBlock(
        blocks.StructBlock([
            ('titulo', blocks.CharBlock(label="Título do Item", default="Título do Item")),
            ('categoria', blocks.CharBlock(
                label="Categoria",
                help_text="Deve corresponder exatamente ao nome de uma categoria definida acima", default="Categoria 1"
            )),
            ('imagem', ImageChooserBlock(label="Imagem", required=False, help_text="Imagem do item da galeria")),
        ]),
        label="Itens da Galeria",
        help_text="Adicione os itens que serão exibidos na galeria"
    )
    
    class Meta:
        template = "enap_designsystem/blocks/gallery_modern.html"
        icon = "image"
        label = "Galeria Moderna com Filtro"
        
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        
        # Gerar slugs automaticamente para as categorias que não possuem
        categorias = []
        for categoria in value['categorias']:
            cat = dict(categoria)
            if not cat.get('slug'):
                cat['slug'] = slugify(cat.get('nome', ''))
            categorias.append(cat)
        
        # Como não temos mais o campo data, vamos usar os itens na ordem em que foram adicionados
        itens_ordenados = value['itens_galeria']
        
        # Organizando itens por categoria
        itens_por_categoria = {}
        for item in itens_ordenados:
            categoria = item['categoria']
            if categoria not in itens_por_categoria:
                itens_por_categoria[categoria] = []
                
            # Adicionar o item à categoria correspondente
            itens_por_categoria[categoria].append(dict(item))
            
        context['categorias'] = categorias
        context['itens_ordenados'] = itens_ordenados
        context['itens_por_categoria'] = itens_por_categoria
        context['cor_principal'] = value.get('cor_principal', '#0f172a')
        context['cor_secundaria'] = value.get('cor_secundaria', '#0284c7')
        
        return context



class TeamModern(blocks.StructBlock):
    """Bloco para exibir um time de pessoas com carrossel."""
    title = blocks.CharBlock(
        label="Título", 
        max_length=200, 
        default="Temos uma rica experiência de diversos backgrounds",
        required=False,
    )
    subtitle = blocks.TextBlock(
        label="Subtítulo", 
        default="Nossa filosofia é simples: reunir pessoas talentosas e oferecer a elas os recursos e suporte para fazer seu melhor trabalho.",
        required=False,
    )
    
    team_members = blocks.ListBlock(
        blocks.StructBlock([
            ('photo', ImageChooserBlock(
                label="Foto",
                help_text="Recomendado: 270x320px ou proporção similar",
                required=False,
            )),
            ('name', blocks.CharBlock(label="Nome", max_length=100, default="Nome do Membro")),
            ('role', blocks.RichTextBlock(
            label="Cargo",
            default="<p>Cargo do Membro</p>",
            features=['h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul'], 
            help_text="Suporta formatação rica, listas e links"
            )),
            ('links_perfil', blocks.URLBlock(
                label="Link do Perfil", 
                required=False, 
                help_text="Link para LinkedIn, Lattes ou perfil profissional"
            )),
        ], icon="user", label="Membro da Equipe"),
        label="Membros da Equipe",
        min_num=1,
        help_text="Adicione os membros da equipe que aparecerão no carrossel"
    )

    class Meta:
        template = "enap_designsystem/blocks/team_modern.html"
        icon = "group"
        label = "Equipe com Carrossel"
        help_text = "Exibe membros da equipe em formato de carrossel navegável"





class CTA2Block(StructBlock):
    """Bloco StreamField para a seção Hero."""
    
    hero_badge = CharBlock(
        required=True,
        default="Gnova: Leitura ao ar livre",
        help_text="Texto do badge no topo da seção hero"
    )
    
    hero_title = CharBlock(
        required=True,
        default="Espaço para promover a rotatividade de livros e leitura ao ar livre.",
        help_text="Título principal da seção hero"
    )
    
    hero_description = RichTextBlock(
        required=True,
        features=['bold', 'italic', 'link'],
        default="<p>Um jardim interativo onde os livros podem ser trocados, lidos e apreciados em um ambiente natural.</p><p>Área para workshops, contação de histórias e eventos culturais.</p>",
        help_text="Descrição da seção hero (aceita formatação básica)"
    )
    
    hero_image = ImageChooserBlock(
        required=False,
        help_text="Imagem da seção hero (ideal: 1200x800px)"
    )
    
    class Meta:
        template = "enap_designsystem/blocks/cta2.html"
        icon = "view"
        label = "CTA: Duas Colunas - Coluna01: Tag, Texto, descrição // Coluna02: Imagem"





class JobVacancyPage(Page):
	"""Página individual para vaga de emprego."""
	STATUS_CHOICES = [
		('aberta', _('Aberta')),
		('em_andamento', _('Em Andamento')),
		('encerrada', _('Encerrada')),
	]
	
	AREA_CHOICES = [
		('professores_facilitadores', _('Professores e Facilitadores')),
		('servicos_tecnicos', _('Contratação de Serviços Técnicos')),
		('licitacoes', _('Licitações')),
		('outros', _('Outros')),
	]
	
	status = models.CharField(
		max_length=20,
		choices=STATUS_CHOICES,
		default='aberta',
		verbose_name=_('Status (Aberto, em andamento ou encerrada)'),
	)
	
	area = models.CharField(
		max_length=30,
		choices=AREA_CHOICES,
		default='outros',
		verbose_name=_('Área ou categoria'),
		help_text=_('Categoria para melhor organização')
	)
	
	image = StreamField([
		('image', ImageChooserBlock(required=False, label=_('Imagem'))),
	], 
	null=True,
	blank=True,
	verbose_name=_('Imagem'),
	use_json_field=True
	)
	
	description = RichTextField(
		verbose_name=_('Descrição curta'),
		help_text=_('Texto breve que aparecerá no card')
	)

	link_text = models.CharField(
		max_length=100,
		verbose_name=_('Texto do botão de destaque'),
		default='Ver detalhes',
		blank=True
	)
	
	process_code = models.CharField(
		max_length=100,
		verbose_name=_('Código do Processo'),
		blank=True
	)
	
	registration_start = models.DateField(
		verbose_name=_('Data de Inicio')
	)
	
	registration_end = models.DateField(
		verbose_name=_('Data Final')
	)
	
	inscription_link = models.URLField(
		verbose_name=_('Link de destaque'),
		blank=True
	)
	
	full_description = RichTextField(
		verbose_name=_('Descrição completa')
	)
	
	download_files = RichTextField(
		verbose_name=_('Arquivos para Download'),
		blank=True
	)

	navbar = models.ForeignKey(
		"EnapNavbarSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	footer = models.ForeignKey(
		"EnapFooterSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	card_type = models.CharField(
		choices=[
			('card-primary', _('Card Primário')),
			('card-secondary', _('Card Secundário')),
			('card-terciary', _('Card Terciário')),
			('card-horizontal', _('Card Horizontal')),
			('card-bgimage', _('Card com Imagem de Fundo')),
		],
		default='card-primary',
		max_length=50,
		verbose_name=_('Tipo de Card')
	)
	
	content_panels = Page.content_panels + [
		FieldPanel('card_type'),
		FieldPanel("navbar"),
		MultiFieldPanel([
			FieldPanel('status'),
			FieldPanel('area'),
		], heading=_('Classificação da Vaga')),
		FieldPanel('image'),
		FieldPanel('description'),
		FieldPanel('link_text'),
		MultiFieldPanel([
			FieldPanel('process_code'),
			FieldPanel('registration_start'),
			FieldPanel('registration_end'),
			FieldPanel('inscription_link'),
		], heading=_('Informações de Inscrição')),
		FieldPanel('full_description'),
		FieldPanel('download_files'),
		FieldPanel("footer"),
	]

	parent_page_types = ['JobVacancyIndexPage', 'ENAPComponentes']

	def get_context(self, request, *args, **kwargs):
		context = super().get_context(request, *args, **kwargs)
		context['registration_period'] = f"{self.registration_start.strftime('%d/%m/%Y')} - {self.registration_end.strftime('%d/%m/%Y')}"
		context['share_url'] = request.build_absolute_uri(self.url)
		return context

	def get_template(self, request, *args, **kwargs):
		return "enap_designsystem/blocks/job_vacancy_page.html"

	@property
	def get_status_label(self):
		status_map = {
			'aberta': _('Vaga Aberta'),
			'em_andamento': _('Em Andamento'),
			'encerrada': _('Vaga Encerrada'),
		}
		return status_map.get(self.status)

	@property
	def get_status_color(self):
		status_colors = {
			'aberta': 'status-open',
			'em_andamento': 'status-in-progress',
			'encerrada': 'status-closed',
		}
		return status_colors.get(self.status, '')

	@property
	def titulo_filter(self):
		return strip_tags(self.title or "").strip()

	@property
	def descricao_filter(self):
		return strip_tags(self.description or "").strip()

	@property
	def categoria(self):
		return "Especialização"

	@property
	def data_atualizacao_filter(self):
		return self.latest_revision_created_at or self.first_published_at

	@property
	def url_filter(self):
		if hasattr(self, 'full_url') and self.full_url:
			return self.full_url
		return self.get_url_parts()[2] if self.get_url_parts() else ""

	@property
	def imagem_filter(self):
		if self.image and len(self.image.stream_data) > 0:
			bloco = self.image.stream_data[0]
			if bloco["type"] == "image":
				valor = bloco["value"]
				if isinstance(valor, dict) and valor.get("id"):
					try:
						from wagtail.images import get_image_model
						Image = get_image_model()
						imagem = Image.objects.get(id=valor["id"])
						return imagem.file.url
					except Image.DoesNotExist:
						pass
		return ""

	@property
	def texto_unificado(self):
		def extract_text_from_block(block_value):
			result = []
			if isinstance(block_value, list):
				for subblock in block_value:
					result.extend(extract_text_from_block(subblock))
			elif hasattr(block_value, "get"):
				for key, val in block_value.items():
					result.extend(extract_text_from_block(val))
			elif isinstance(block_value, str):
				result.append(strip_tags(block_value).strip())
			elif hasattr(block_value, "source"):
				result.append(strip_tags(block_value.source).strip())
			return result

		tudo = []

		if self.full_description:
			tudo.append(strip_tags(self.full_description).strip())

		if self.download_files:
			tudo.append(strip_tags(self.download_files).strip())

		if self.image:
			for block in self.image:
				tudo.extend(extract_text_from_block(block.value))

		if self.description:
			tudo.append(strip_tags(self.description).strip())

		return re.sub(r"\s+", " ", " ".join([t for t in tudo if t])).strip()

	search_fields = Page.search_fields + [
		index.SearchField("title", boost=3),
		index.SearchField("titulo_filter", name="titulo"),
		index.SearchField("descricao_filter", name="descricao"),
		index.FilterField("categoria", name="categoria_filter"),
		index.SearchField("url_filter", name="url"),
		index.SearchField("data_atualizacao_filter", name="data_atualizacao"),
		index.SearchField("imagem_filter", name="imagem"),
		index.SearchField("texto_unificado", name="body"),
	]

	class Meta:
		verbose_name = _('Template (Vagas & Licitações)')
		verbose_name_plural = _('Vagas e Licitações')





class JobVacancyIndexPage(Page):
    """Página índice que lista todas as vagas."""
    
    intro = RichTextField(
        blank=True,
        verbose_name=_('Introdução')
    )

    card_type = models.CharField(
        choices=[
            ('card-primary', _('Card Primário')),
            ('card-secondary', _('Card Secundário')),
            ('card-terciary', _('Card Terciário')),
            ('card-horizontal', _('Card Horizontal')),
            ('card-bgimage', _('Card com Imagem de Fundo')),
        ],
        default='card-primary',
        max_length=50,
        verbose_name=_('Tipo de Card')
    )

    navbar = models.ForeignKey(
		"EnapNavbarSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

    footer = models.ForeignKey(
		"EnapFooterSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)
    
    content_panels = Page.content_panels + [
        FieldPanel("navbar"),
        FieldPanel('intro'),
        FieldPanel('card_type'),
        FieldPanel("footer"),
    ]
    
    subpage_types = ['JobVacancyPage']
    
    search_fields = []
    
    def get_index_children(self):
        """Retorna as páginas filhas ordenadas por data de início das inscrições."""
        return self.get_children().specific().live().order_by('-jobvacancypage__registration_start')
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Obter todas as vagas filhas desta página índice
        job_vacancies = JobVacancyPage.objects.live().descendant_of(self)
        
        # Separar por status
        context['open_jobs'] = job_vacancies.filter(status='aberta').order_by('-registration_start')
        context['in_progress_jobs'] = job_vacancies.filter(status='em_andamento').order_by('-registration_start')
        context['closed_jobs'] = job_vacancies.filter(status='encerrada').order_by('-registration_start')
        
        return context
    
    def get_template(self, request, *args, **kwargs):
        return "enap_designsystem/blocks/job_vacancy_index_page.html"
    
    class Meta:
        verbose_name = ('Página Índice de Vagas')





class JobVacanciesBlock(blocks.StructBlock):
    """
    Exibe cards de vagas de emprego separados por status.
    """
    
    indexed_by = blocks.PageChooserBlock(
        required=True,
        page_type='vagas.JobVacancyIndexPage',  # Ajuste conforme seu app
        label=_("Página índice"),
        help_text=_("Selecione a página índice que contém as vagas a serem exibidas.")
    )
    
    num_posts = blocks.IntegerBlock(
        default=6,
        label=_("Número de vagas a exibir por categoria"),
    )
    
    show_open = blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Mostrar vagas abertas"),
    )
    
    show_in_progress = blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Mostrar vagas em andamento"),
    )
    
    show_closed = blocks.BooleanBlock(
        default=False,
        required=False,
        label=_("Mostrar vagas encerradas"),
    )
    
    class Meta:
        template = "enap_designsystem/blocks/job_vacancies_block.html"
        icon = "clipboard-list"
        label = _("Vagas de Emprego")
    
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        
        indexer = value["indexed_by"].specific
        all_vacancies = indexer.get_children().live().specific()
        
        # Filtrar por status e limitar pelo número especificado
        open_jobs = []
        in_progress_jobs = []
        closed_jobs = []
        
        
        if value["show_open"]:
            open_jobs = [page for page in all_vacancies if hasattr(page, 'status') and page.status == 'aberta'][:value["num_posts"]]
            
        if value["show_in_progress"]:
            in_progress_jobs = [page for page in all_vacancies if hasattr(page, 'status') and page.status == 'em_andamento'][:value["num_posts"]]
            
        if value["show_closed"]:
            closed_jobs = [page for page in all_vacancies if hasattr(page, 'status') and page.status == 'encerrada'][:value["num_posts"]]
        
        context["open_jobs"] = open_jobs
        context["in_progress_jobs"] = in_progress_jobs
        context["closed_jobs"] = closed_jobs
        context["block"] = block_type
        
        return context
    



class CitizenServerBlock(blocks.StructBlock):
    
    title = blocks.CharBlock(required=True, help_text="Titulo (e.g. 'Olhar cidadão, servidor atuante, Estado capaz')")
    description = blocks.RichTextBlock(required=True, help_text="Descrição (e.g. 'A Enap é uma escola pública federal vinculada ao Ministério da Gestão e da Inovação em Serviços Públicos (MGI)')")
    small_text = blocks.CharBlock(required=False, help_text="Tag (e.g. 'Servir')")
    
    banner_size = blocks.ChoiceBlock(
        choices=[
            ('medium', 'Banner Médio'),
            ('large', 'Banner Grande'),
        ],
        default='medium',
        help_text="Escolha o tamanho do banner"
    )
    
    style_choice = blocks.ChoiceBlock(
        choices=[
            ('center', 'Texto Centralizado'),
            ('bottom', 'Texto Inferior'),
            ('overlay', 'Texto com Linha'),
        ],
        default='center',
        help_text="Choose the text display style"
    )

    section_id = blocks.CharBlock(
        required=False, 
        help_text="ID da seção para âncoras/navegação (e.g. 'clima', 'transformacao', 'cuidar')",
        max_length=50
    )
    
    background_media = blocks.StreamBlock([
        ('image', ImageChooserBlock(help_text="Imagem de fundo")),
        ('video', DocumentChooserBlock(help_text="Vídeo de fundo")),
    ], max_num=1, required=False, help_text="Escolha uma imagem ou vídeo de fundo")
    
    class Meta:
        template = "enap_designsystem/blocks/citizen_server_block.html"
        icon = "doc-full"
        label = "Banner: Tag, Título, Imagem ou Vídeo, Largura Contida"






class ServiceCardsBlock(blocks.StructBlock):
    """
    A grid of service cards that can be added to a StreamField
    """
    cards = blocks.ListBlock(
        blocks.StructBlock([
            ('image', ImageChooserBlock(required=True, help_text="Card image")),
            ('title', blocks.CharBlock(required=True, help_text="Card title")),
            ('description', blocks.RichTextBlock(required=True, help_text="Card description")),
            ('link', blocks.URLBlock(required=False, help_text="Optional link for the card")),
        ]),
        min_num=1,
        help_text="Add as many cards as you want"
    )

    class Meta:
        template = "enap_designsystem/blocks/service_cards.html"
        icon = "grip"
        label = "Cards Horizontais"






class FeatureListBlock(blocks.StructBlock):
    """
    A block with a featured item on the left and a list of related items on the right
    """
    # Featured item (left side)
    featured_image = ImageChooserBlock(required=True, help_text="Main featured image")
    featured_title = blocks.CharBlock(required=True, help_text="Featured item title")
    featured_description = blocks.RichTextBlock(required=True, help_text="Featured item description")
    featured_link_url = blocks.URLBlock(label="URL do link", required=True, help_text="Link for the featured item")
    
    
    # List items (right side)
    list_items = blocks.ListBlock(
        blocks.StructBlock([
            ('image', ImageChooserBlock(required=True, help_text="Item image")),
            ('title', blocks.CharBlock(required=True, help_text="Item title")),
            ('description', blocks.RichTextBlock(required=True, help_text="Item description")),
            ('link_url', blocks.URLBlock(label="URL do link")),
        ]),
        min_num=1,
        help_text="Add items to be displayed on the right side"
    )

    class Meta:
        template = "enap_designsystem/blocks/feature_list_block.html"
        icon = "table"
        label = "Seção Card Principal e Cards em Lista Lateral"






class CarouselGreen(blocks.StructBlock):
    """Bloco de carrossel com título, tag e itens."""
    
    # Cabeçalho do carrossel
    tag = blocks.CharBlock(label="Tag", max_length=50, default="Ethos Público", required=False)

    title = blocks.RichTextBlock(
        label="Título",  # ← Mudou de "Descrição" para "Título"
        default="Servir: a essência do serviço público",
        required=False,
        features=['bold', 'italic', 'link', 'ul', 'ol', 'h2', 'h3']
    )

    subtitle = blocks.RichTextBlock(
        label="Subtítulo",  # ← Mudou de "Descrição" para "Subtítulo"
        features=['bold', 'italic', 'link', 'ul', 'ol', 'h2', 'h3'],
        required=False
    )
    
    # Estrutura para os itens do carrossel
    items = blocks.ListBlock(
        blocks.StructBlock([
            ('image', ImageChooserBlock(label="Imagem")),
            ('title', blocks.CharBlock(label="Título", max_length=100)),
            ('description', blocks.RichTextBlock(
                label="Descrição",
                features=['bold', 'italic', 'link', 'ul', 'ol', 'h2', 'h3']
            )),
            ('link_text', blocks.CharBlock(label="Texto do link", max_length=50, default="Acesse o curso")),
            ('link_url', blocks.URLBlock(label="URL do link")),
        ]),
        label="Itens do Carrossel",
        min_num=1
    )
    
    class Meta:
        template = "enap_designsystem/blocks/carousel_bggreen.html"
        icon = "view"
        label = "Carrossel de Cards com fundo verde"
        
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['title'] = value.get('title', '')
        context['subtitle'] = value.get('subtitle', '')
        context['items'] = value.get('items', [])
        
        # Para debug
        print(f"CarouselGreen - Contexto: {context}")
        print(f"CarouselGreen - Items: {len(value.get('items', []))}")
        
        return context
    



class TopicLinksBlock(blocks.StructBlock):
    """
    Bloco para exibir tópicos com links "Veja mais"
    """
    
    topic1_title = blocks.CharBlock(
        required=True,
        max_length=100,
        label=_("Título do tópico 1"),
        default="Ethos Público: Compromisso de servir"
    )
    topic1_link = blocks.URLBlock(
        required=True,
        label=_("Link do tópico 1"),
        help_text=_("URL para 'Veja mais' do tópico 1")
    )
    
    topic2_title = blocks.CharBlock(
        required=True,
        max_length=100,
        label=_("Título do tópico 2"),
        default="Cidadania ativa"
    )
    topic2_link = blocks.URLBlock(
        required=True,
        label=_("Link do tópico 2"),
        help_text=_("URL para 'Veja mais' do tópico 2")
    )
    
    topic3_title = blocks.CharBlock(
        required=True,
        max_length=100,
        label=_("Título do tópico 3"),
        default="Estado e Desenvolvimento"
    )
    topic3_link = blocks.URLBlock(
        required=True,
        label=_("Link do tópico 3"),
        help_text=_("URL para 'Veja mais' do tópico 3")
    )
    
    class Meta:
        template = "enap_designsystem/blocks/topic_links_block.html"
        icon = "list-ul"
        label = _("Tópicos para Links")




class Banner_Image_cta(blocks.StructBlock):
    """
    Bloco de banner hero com imagem, texto e opção de botão ou vídeo
    """
    tag = blocks.CharBlock(
        required=False,
        max_length=50,
        label=_("Tag"),
        default="Ethos Público"
    )
    
    title = blocks.CharBlock(
        required=True,
        max_length=200,
        label=_("Título"),
        default="Servir: a essência do serviço público"
    )
    
    description = blocks.TextBlock(
        required=True,
        label=_("Descrição"),
        default="A ideia do \"Propósito do Servir\" destaca que trabalhar no serviço público vai além de cumprir uma função; é um compromisso verdadeiro com a sociedade."
    )
    
    background_image = ImageChooserBlock(
        required=False,
        label=_("Imagem de fundo (opcional)"),
        help_text=_("Se não fornecida, será usado fundo verde padrão")
    )
    
    # Opção para mostrar ou não a imagem principal
    show_hero_image = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Mostrar imagem principal?")
    )
    
    hero_image = ImageChooserBlock(
        required=False,
        label=_("Imagem principal"),
        help_text=_("Será exibida apenas se 'Mostrar imagem principal' estiver marcado")
    )
    
    # Tipo de ação (botão ou vídeo)
    action_type = blocks.ChoiceBlock(
        choices=[
            ('none', 'Nenhuma ação'),
            ('video', 'Botão de vídeo'),
            ('button', 'Botão de ação'),
        ],
        default='none',
        label=_("Tipo de ação"),
        help_text=_("Escolha se deseja exibir botão de vídeo, botão de ação ou nenhum")
    )
    
    # Campos para vídeo
    video_text = blocks.CharBlock(
        required=False,
        max_length=50,
        label=_("Texto do botão de vídeo"),
        default="VEJA O VÍDEO",
        help_text=_("Será exibido apenas se 'Botão de vídeo' estiver selecionado")
    )
    
    video_url = blocks.URLBlock(
        required=False,
        label=_("URL do vídeo"),
        help_text=_("Link para o vídeo (YouTube, Vimeo, etc). Será usado apenas se 'Botão de vídeo' estiver selecionado"),
        default="https://www.youtube.com/watch?v=dQw4w9WgXcQ"  
    )
    
    # Campos para botão de ação
    button_text = blocks.CharBlock(
        required=False,
        max_length=50,
        label=_("Texto do botão de ação"),
        default="SAIBA MAIS",
        help_text=_("Será exibido apenas se 'Botão de ação' estiver selecionado")
    )
    
    button_url = blocks.URLBlock(
        required=False,
        label=_("URL do botão"),
        help_text=_("Link para onde o botão deve direcionar. Será usado apenas se 'Botão de ação' estiver selecionado")
    )
    
    button_style = blocks.ChoiceBlock(
        choices=[
            ('primary', 'Primário'),
            ('secondary', 'Secundário'),
            ('outline', 'Contorno'),
        ],
        default='primary',
        label=_("Estilo do botão"),
        help_text=_("Será aplicado apenas se 'Botão de ação' estiver selecionado")
    )
    
    class Meta:
        template = "enap_designsystem/blocks/banner_image_cta.html"
        icon = "image"
        label = _("Banner Background-Imagem e Botão/Vídeo")
        



class FeatureWithLinksBlock(blocks.StructBlock):
    """
    A block with a featured image on the left and a grid of link cards on the right
    """
    # Featured item (left side)
    featured_image = ImageChooserBlock(required=True, help_text="Main featured image")
    featured_title = blocks.CharBlock(required=True, help_text="Featured title")
    featured_description = blocks.CharBlock(required=False, help_text="Featured description (optional)")
    
    # List items (right/bottom side) - Ajustado para garantir que funcione
    list_items = blocks.ListBlock(
        blocks.StructBlock([
            ('image', ImageChooserBlock(required=True, help_text="Item thumbnail")),
            ('title', blocks.CharBlock(required=True, help_text="Item title")),
            ('description', blocks.RichTextBlock(required=True, help_text="Item description")),
            ('link', blocks.URLBlock(required=False, help_text="Link URL (entire card will be clickable)")),
        ]),
        min_num=1,
        max_num=10,  # Limite opcional
        default=[{'title': 'Exemplo de item', 'description': '<p>Descrição do item</p>'}],  # Valor padrão
        help_text="Add as many items as you want in the grid"
    )

    class Meta:
        template = "enap_designsystem/blocks/feature_with_links_block.html"
        icon = "link"
        label = "Card Destaque - cards com links ao lado"





class QuoteBlockModern(blocks.StructBlock):
    """
    Um bloco personalizado para citações com foto no Wagtail.
    """
    person_image = ImageChooserBlock(
        label="Foto da Pessoa",
        help_text="Adicione uma foto da pessoa sendo citada. Recomendação: imagem no formato retrato com pelo menos 500x700px."
    )
    
    quote_text = blocks.TextBlock(
        label="Texto da Citação",
        help_text="O texto da citação. Não é necessário adicionar aspas, elas serão adicionadas automaticamente."
    )
    
    author_name = blocks.CharBlock(
        label="Nome do Autor",
        max_length=100,
        help_text="Nome da pessoa sendo citada."
    )
    
    author_title = blocks.CharBlock(
        label="Título/Cargo do Autor",
        max_length=150,
        required=False,
        help_text="Cargo, profissão ou título da pessoa (opcional)."
    )
    
    color_theme = blocks.ChoiceBlock(
        choices=[
            ('default', 'Padrão (Branco)'),
            ('blue', 'Azul'),
            ('green', 'Verde'),
        ],
        default='default',
        label="Tema de Cor",
        help_text="Escolha um tema de cor para a citação."
    )

    class Meta:
        template = "enap_designsystem/blocks/quote_modern.html"
        icon = "openquote"
        label = "Citação com Foto"
        help_text = "Citação elegante com foto do autor."




class BannerTopicsBlock(blocks.StructBlock):

    # Configurações principais
    titulo = blocks.CharBlock(
        label="Título",
        default="Titulo do Componente",
        max_length=100,
        help_text="Título principal do componente"
    )
    
    periodo_info = blocks.CharBlock(
        label="Sub Titulo",
        default="Sub Titulo do Componente",
        max_length=200,
        help_text="Informação e/ou descrição"
    )
    
    descricao = blocks.TextBlock(
        label="Descrição",
        default="Descrição do Componente",
        help_text="Descrição com mais detalhes",
    )
    
    # Imagem de fundo
    imagem_fundo = ImageChooserBlock(
        label="Imagem de Fundo",
        required=False,
        help_text="Imagem que será exibida como fundo do componente"
    )
    
    # StreamField para itens do menu
    itens_menu = blocks.StreamBlock([
        ('item_link', blocks.StructBlock([
            ('titulo', blocks.CharBlock(
                label="Título do Item",
                max_length=100
            )),
            ('url', blocks.URLBlock(
                label="URL do Link",
                help_text="URL completa (ex: https://exemplo.com)"
            )),
        ], label="Item do Menu", icon="link")),
    ], 
    label="Itens do Menu",
    help_text="Adicione quantos itens de menu desejar",
    required=False)
    
    class Meta:
        template = 'enap_designsystem/blocks/banner_topicos_block.html'
        icon = 'graduation'
        label = 'Banner com menu de navegação em tópicos'
        help_text = 'Banner com imagem de fundo, título, descrição e menu de navegação'




class LocalizacaoBlock(blocks.StructBlock):
    """
    Bloco para exibir informações de localização com mapa do Google Maps via iframe
    """
    
    # Informações do local
    titulo_secao = blocks.CharBlock(
        label="Título da Seção",
        default="Local",
        max_length=50,
        help_text="Título da seção (ex: Local, Onde Estamos)"
    )
    
    nome_instituicao = blocks.CharBlock(
        label="Nome da Instituição",
        default="Enap - Escola Nacional de Administração Pública",
        max_length=200,
        help_text="Nome completo da instituição"
    )
    
    endereco_completo = blocks.CharBlock(
        label="Endereço Completo",
        default="Asa Sul • SPO Área Especial 2-A • CEP 70.610-900 • Brasília/DF",
        max_length=300,
        help_text="Endereço completo com CEP e cidade"
    )
    
    # Link do Google Maps
    google_maps_url = blocks.URLBlock(
        label="Link do Google Maps",
        help_text="Cole aqui o link completo do Google Maps (ex: https://maps.google.com/...)"
    )
    
    mostrar_botao_rotas = blocks.BooleanBlock(
        label="Mostrar Botão de Rotas",
        default=True,
        required=False,
        help_text="Exibir botão para abrir rotas no Google Maps"
    )

    class Meta:
        template = 'enap_designsystem/blocks/localizacao_block.html'
        icon = 'site'
        label = 'Localização com Mapa'
        help_text = 'Componente para exibir localização com mapa do Google Maps'



class CtaDestaqueBlock(blocks.StructBlock):
    """
    Bloco para exibir informações sobre data de início da formação
    """
    
    # Configurações principais
    titulo = blocks.CharBlock(
        label="Título",
        default="Data de Início da Formação",
        max_length=100,
        help_text="Título principal do componente"
    )
    
    # Ícone personalizado (opcional)
    icone_personalizado = ImageChooserBlock(
        label="Ícone Personalizado",
        required=False,
        help_text="Imagem personalizada para o ícone (opcional, padrão será ícone de relógio)"
    )
    
    # Conteúdo
    descricao = blocks.RichTextBlock(
        label="Descrição",
        help_text="Texto com as informações sobre a formação",
        features=['bold', 'italic', 'link'],
        default="A formação começa no dia 15 de janeiro de 2024. Inscrições abertas até 10 de janeiro.",
    )

    class Meta:
        template = 'enap_designsystem/blocks/cta_destaque_formacao_block.html'
        icon = 'time'
        label = 'Imagem com título e descrição'
        help_text = 'CTA com ícone, título e descrição'








class HolofoteCarouselBlock(blocks.StructBlock):
    """
    Renders a carousel of pages with holofote styling.
    Automatically extracts media from CitizenServerBlock or uses cover_image.
    """

    indexed_by = blocks.PageChooserBlock(
        required=True,
        label=_("Parent page"),
        help_text=_(
            "Show a preview of pages that are children of the selected page. "
            "Uses ordering specified in the page's LAYOUT tab."
        ),
    )
    
    num_posts = blocks.IntegerBlock(
        default=3,
        label=_("Number of pages to show"),
    )

    class Meta:
        template = "enap_designsystem/blocks/holofote_carousel.html"
        icon = "media"
        label = _("Carrossel Holofote")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        indexer = value["indexed_by"].specific
        if hasattr(indexer, "get_index_children"):
            pages = indexer.get_index_children()
        else:
            pages = indexer.get_children().live()

        # SOLUÇÃO: Converter para objetos específicos
        context["pages"] = [p.specific for p in pages[: value["num_posts"]]]
        return context
    




class CustomLinkBlock(StructBlock):
    """Bloco para link customizado - página ou URL"""
    
    link_type = ChoiceBlock(
        choices=[
            ('page', 'Página interna'),
            ('url', 'Link externo'),
        ],
        default='page',
        verbose_name="Tipo de Link"
    )
    
    page = PageChooserBlock(
        required=False, 
        verbose_name="Página",
        help_text="Escolha uma página interna"
    )
    
    url = URLBlock(
        required=False, 
        verbose_name="URL Externa",
        help_text="Digite a URL completa (ex: https://exemplo.com)"
    )
    
    title = CharBlock(
        max_length=100, 
        verbose_name="Título do Link",
        help_text="Título que aparecerá no menu"
    )
    
    class Meta:
        icon = "link"

class HeroMenuItemBlock(StructBlock):
    """Bloco simples para itens do menu hero."""
    
    title = CharBlock(
        max_length=100,
        verbose_name="Título do Menu",
        help_text="Ex: Pós-Graduação, Inovação, Pesquisa"
    )
    
    parent_page = PageChooserBlock(verbose_name="Página Pai")
    
    # Links adicionais (páginas ou URLs)
    additional_links = ListBlock(
        CustomLinkBlock(),
        required=False,
        verbose_name="Links Adicionais",
        help_text="Links extras que aparecerão junto com as páginas filhas"
    )
    
    sort_order = ChoiceBlock(
        choices=[
            ('-first_published_at', 'Mais recente primeiro'),
            ('first_published_at', 'Mais antigo primeiro'),
            ('title', 'Alfabética A-Z'),
        ],
        default='-first_published_at',
        verbose_name="Ordenação"
    )
    
    class Meta:
        icon = "list-ul"
        label = "Item do Menu Hero"

    def get_all_menu_items(self, menu_item):
        """Combina páginas filhas e links adicionais em uma lista ordenada"""
        
        # Páginas filhas
        child_pages = list(menu_item['parent_page'].get_children().live().public())
        
        # Converte páginas filhas para formato padrão
        menu_items = []
        for page in child_pages:
            menu_items.append({
                'title': page.title,
                'url': page.url,
                'type': 'page',
                'page': page,
                'first_published_at': page.first_published_at
            })
        
        # Adiciona links customizados
        for link in menu_item['additional_links']:
            if link['link_type'] == 'page' and link['page'] and link['page'].live:
                menu_items.append({
                    'title': link['title'] or link['page'].title,
                    'url': link['page'].url,
                    'type': 'additional_page',
                    'page': link['page'],
                    'first_published_at': link['page'].first_published_at
                })
            elif link['link_type'] == 'url' and link['url']:
                menu_items.append({
                    'title': link['title'],
                    'url': link['url'],
                    'type': 'additional_url',
                    'page': None,
                    'first_published_at': None
                })
        
        # Remove duplicatas (páginas que aparecem como filhas e adicionais)
        seen_urls = set()
        unique_items = []
        for item in menu_items:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                unique_items.append(item)
        
        # Aplica ordenação
        sort_order = menu_item['sort_order']
        if sort_order == 'title':
            unique_items.sort(key=lambda x: x['title'])
        elif sort_order == 'first_published_at':
            # URLs vão para o final (sem data)
            unique_items.sort(key=lambda x: x['first_published_at'] or datetime.min, reverse=False)
        elif sort_order == '-first_published_at':
            # URLs vão para o final (sem data)
            unique_items.sort(key=lambda x: x['first_published_at'] or datetime.min, reverse=True)
        
        return unique_items



class ProgramaCardBlock(blocks.StructBlock):
    """Card individual do programa"""
    
    logo = ImageChooserBlock(
        label="Logo do Programa",
        help_text="Logo que aparece no card",
        required=False,
    )
    
    titulo = blocks.CharBlock(
        label="Título do Programa",
        max_length=200,
        help_text="Ex: Programa de Desenvolvimento Inicial para Cargos de Nível Intermediário"
    )
    
    duracao = blocks.CharBlock(
        label="Duração",
        max_length=50,
        help_text="Ex: 271h, 280h"
    )
    
    link = blocks.URLBlock(
        label="Link do Programa",
        required=False,
        help_text="URL para onde o card deve direcionar quando clicado"
    )
    
    class Meta:
        icon = 'doc-full'
        label = 'Card do Programa'
        template = 'enap_designsystem/blocks/programa_card.html'


class ProgramaCardsBlock(blocks.StructBlock):
    """Seção completa com título, imagem de fundo e cards dos programas"""
    
    titulo_principal = blocks.CharBlock(
        label="Título Principal",
        max_length=200,
        default="Programa",
        help_text="Título principal da seção",
        required=False,
    )
    
    subtitulo = blocks.CharBlock(
        label="Subtítulo",
        max_length=200,
        default="de Desenvolvimento Inicial",
        help_text="Subtítulo que aparece abaixo do título principal",
        required=False,
    )
    
    imagem_fundo = ImageChooserBlock(
        label="Imagem de Fundo",
        help_text="Imagem que será usada como background da seção"
    )
    
    posicao_cards = blocks.ChoiceBlock(
        label="Posição dos Cards",
        choices=[
            ('direita', 'Direita'),
            ('esquerda', 'Esquerda'),
        ],
        default='direita',
        help_text="Define se os cards ficam à direita ou esquerda do título"
    )
    
    cards = blocks.ListBlock(
        ProgramaCardBlock(),
        label="Cards dos Programas",
        min_num=1,
        max_num=4,
        help_text="Adicione até 4 cards de programas"
    )
    
    class Meta:
        icon = 'list-ul'
        label = 'Sessão com background-image, titulo e cards(titulo e horas)'
        template = 'enap_designsystem/blocks/programa_cards.html'




class CarouselSlideBlock(blocks.StructBlock):
    """Slide individual do carrossel com imagens desktop/mobile"""
    
    titulo = blocks.CharBlock(
        label="Título do Slide",
        max_length=200,
        required=False,
        help_text="Título que aparece sobre a imagem"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        label="Cor do Título",
        choices=BRAND_TEXTS_CHOICES,
        default='#FFFFFF',
        required=False,
        help_text="Cor do título conforme Design System ENAP"
    )
    
    subtitulo = blocks.RichTextBlock(
        label="Subtítulo",
        required=False,
        help_text="Texto com formatação: **bold**, *itálico*, listas, etc.",
        features=['bold', 'italic', 'ul', 'ol', 'link'] 
    )
    
    cor_subtitulo = blocks.ChoiceBlock(
        label="Cor do Subtítulo",
        choices=BRAND_TEXTS_CHOICES,
        default='#FFFFFF',
        required=False,
        help_text="Cor do subtítulo conforme Design System ENAP"
    )
    
    imagem_desktop = ImageChooserBlock(
        label="Imagem Desktop",
        help_text="Imagem para telas grandes (desktop/tablet)"
    )
    
    imagem_mobile = ImageChooserBlock(
        label="Imagem Mobile",
        help_text="Imagem para dispositivos móveis"
    )
    
    # Configurações do Botão
    mostrar_botao = blocks.BooleanBlock(
        label="Mostrar Botão",
        default=True,
        required=False,
        help_text="Se deve exibir o botão no slide"
    )
    
    texto_botao = blocks.CharBlock(
        label="Texto do Botão",
        max_length=100,
        default="Saiba mais",
        required=False,
        help_text="Texto que aparece no botão"
    )
    
    link_botao = blocks.URLBlock(
        label="Link do Botão",
        required=False,
        help_text="URL para onde o botão deve direcionar"
    )
    
    estilo_botao = blocks.ChoiceBlock(
        label="Estilo do Botão",
        choices=[
            ('primario', 'Primário (Azul)'),
            ('secundario', 'Secundário (Branco)'),
            ('outline', 'Outline (Borda)'),
            ('personalizado', 'Personalizado (usar cor customizada)'),
        ],
        default='primario',
        help_text="Estilo visual do botão"
    )
    
    cor_fundo_botao = blocks.ChoiceBlock(
        label="Cor de Fundo do Botão",
        choices=BRAND_TEXTS_CHOICES,
        default='#00777D',
        required=False,
        help_text="Cor de fundo do botão (usado quando estilo for 'Personalizado')"
    )
    
    cor_texto_botao = blocks.ChoiceBlock(
        label="Cor do Texto do Botão",
        choices=BRAND_TEXTS_CHOICES,
        default='#FFFFFF',
        required=False,
        help_text="Cor do texto do botão (usado quando estilo for 'Personalizado')"
    )
    
    cor_borda_botao = blocks.ChoiceBlock(
        label="Cor da Borda do Botão",
        choices=BRAND_TEXTS_CHOICES,
        default='#00777D',
        required=False,
        help_text="Cor da borda do botão (usado para estilos 'Outline' e 'Personalizado')"
    )
    
    # Posicionamento do Conteúdo
    posicao_conteudo = blocks.ChoiceBlock(
        label="Posição do Conteúdo",
        choices=[
            ('centro', 'Centro'),
            ('esquerda', 'Esquerda'),
            ('direita', 'Direita'),
            ('inferior-esquerda', 'Inferior Esquerda'),
            ('inferior-centro', 'Inferior Centro'),
            ('inferior-direita', 'Inferior Direita'),
        ],
        default='centro',
        help_text="Onde posicionar o texto e botão na imagem"
    )
    
    overlay_escuro = blocks.BooleanBlock(
        label="Overlay Escuro",
        default=True,
        required=False,
        help_text="Adicionar overlay escuro para melhor legibilidade"
    )
    
    class Meta:
        icon = 'image'
        label = 'Slide do Carrossel'


class EnapCarouselImagesBlock(blocks.StructBlock):
    """Carrossel de imagens responsivo da ENAP"""
    
    slides = blocks.ListBlock(
        CarouselSlideBlock(),
        label="Slides",
        min_num=1,
        max_num=50,
        help_text="Adicione os slides do carrossel"
    )
    
    # Configurações do Carrossel
    altura_desktop = blocks.ChoiceBlock(
        label="Altura Desktop",
        choices=[
            ('400px', 'Baixa (400px)'),
            ('500px', 'Média (500px)'),
            ('600px', 'Alta (600px)'),
            ('100vh', 'Tela Cheia'),
        ],
        default='500px',
        help_text="Altura do carrossel no desktop"
    )
    
    altura_mobile = blocks.ChoiceBlock(
        label="Altura Mobile",
        choices=[
            ('250px', 'Baixa (250px)'),
            ('300px', 'Média (300px)'),
            ('400px', 'Alta (400px)'),
            ('100vh', 'Tela Cheia'),
        ],
        default='300px',
        help_text="Altura do carrossel no mobile"
    )
    
    autoplay = blocks.BooleanBlock(
        label="Autoplay",
        default=True,
        required=False,
        help_text="Se o carrossel deve rodar automaticamente"
    )
    
    intervalo_autoplay = blocks.IntegerBlock(
        label="Intervalo Autoplay (segundos)",
        default=5,
        min_value=2,
        max_value=15,
        help_text="Tempo entre as transições automáticas"
    )
    
    mostrar_indicadores = blocks.BooleanBlock(
        label="Mostrar Indicadores",
        default=True,
        required=False,
        help_text="Pontos indicadores na parte inferior"
    )
    
    mostrar_setas = blocks.BooleanBlock(
        label="Mostrar Setas",
        default=True,
        required=False,
        help_text="Setas de navegação lateral"
    )
    
    efeito_transicao = blocks.ChoiceBlock(
        label="Efeito de Transição",
        choices=[
            ('slide', 'Deslizar'),
            ('fade', 'Fade'),
        ],
        default='slide',
        help_text="Tipo de transição entre slides"
    )
    
    class Meta:
        icon = 'view'
        label = 'Carrossel de Imagens'
        template = 'enap_designsystem/blocks/carousel_images.html'




class CarouselSectionBlock(blocks.StructBlock):
    """Wrapper para transformar qualquer seção em slide de carrossel"""
    
    # Aqui você pode adicionar outras seções conforme necessário
    @property 
    def secao(self):
        from .layout_blocks import EnapCardGridBlock
        return blocks.StreamBlock([
            ("enap_carousel", EnapCarouselImagesBlock()),
            ("programa_cards", ProgramaCardsBlock()),
            ("cta_destaque", CtaDestaqueBlock()),
            ("enap_cardgrid", EnapCardGridBlock([
                ('card_curso', CardCursoBlock()),
        ])),
    ], 
    label="Seção do Slide",
    help_text="Escolha qual tipo de seção será este slide"
    )
    
    # Configurações específicas do slide
    titulo_slide = blocks.CharBlock(
        label="Título do Slide (Opcional)",
        max_length=200,
        required=False,
        help_text="Título que identifica este slide no admin (não aparece no frontend)"
    )
    
    class Meta:
        icon = 'doc-full'
        label = 'Slide de Seção'


class EnapSectionCarouselBlock(blocks.StructBlock):
    """Carrossel que rola seções completas"""
    
    titulo_carrossel = blocks.CharBlock(
        label="Título do Carrossel",
        max_length=200,
        required=False,
        help_text="Título opcional acima do carrossel"
    )
    
    slides = blocks.ListBlock(
        CarouselSectionBlock(),
        label="Slides/Seções",
        min_num=2,
        max_num=6,
        help_text="Adicione as seções que farão parte do carrossel"
    )
    
    # Configurações do Carrossel
    autoplay = blocks.BooleanBlock(
        label="Autoplay",
        default=False,
        required=False,
        help_text="Se o carrossel deve rodar automaticamente"
    )
    
    intervalo_autoplay = blocks.IntegerBlock(
        label="Intervalo Autoplay (segundos)",
        default=8,
        min_value=3,
        max_value=20,
        help_text="Tempo entre as transições (recomendado: 8-15 segundos para seções)"
    )
    
    mostrar_indicadores = blocks.BooleanBlock(
        label="Mostrar Indicadores",
        default=True,
        required=False,
        help_text="Pontos/números indicadores na parte inferior"
    )
    
    mostrar_navegacao = blocks.BooleanBlock(
        label="Mostrar Navegação",
        default=True,
        required=False,
        help_text="Setas de navegação lateral"
    )
    
    estilo_indicadores = blocks.ChoiceBlock(
        label="Estilo dos Indicadores",
        choices=[
            ('pontos', 'Pontos'),
            ('numeros', 'Números'),
            ('barras', 'Barras de Progresso'),
        ],
        default='pontos',
        help_text="Como mostrar os indicadores"
    )
    
    posicao_controles = blocks.ChoiceBlock(
        label="Posição dos Controles",
        choices=[
            ('inferior', 'Inferior'),
            ('superior', 'Superior'),
            ('lateral', 'Lateral'),
        ],
        default='inferior',
        help_text="Onde posicionar os controles de navegação"
    )
    
    altura_minima = blocks.ChoiceBlock(
        label="Altura Mínima",
        choices=[
            ('auto', 'Automática'),
            ('400px', '400px'),
            ('500px', '500px'),
            ('600px', '600px'),
            ('100vh', 'Tela Cheia'),
        ],
        default='auto',
        help_text="Altura mínima do carrossel"
    )
    
    efeito_transicao = blocks.ChoiceBlock(
        label="Efeito de Transição",
        choices=[
            ('slide', 'Deslizar'),
            ('fade', 'Fade'),
            ('slide-vertical', 'Deslizar Vertical'),
        ],
        default='slide',
        help_text="Tipo de transição entre seções"
    )
    
    class Meta:
        icon = 'view'
        label = 'Carrossel de Seções'
        template = 'enap_designsystem/blocks/section_carousel.html'




class OuvidoriaBlock(StructBlock):
    """Block da seção de Ouvidoria e Acesso à Informação"""
    
    titulo = CharBlock(
        label="Título da Seção",
        default="Ouvidoria e Acesso à Informação",
        max_length=200,
        help_text="Título principal da seção de ouvidoria"
    )
    
    class Meta:
        template = "enap_designsystem/blocks/ouvidoria_block.html"
        icon = "help"
        label = "Ouvidoria"




class CardDestaqueBlock(StructBlock):
    """Bloco para cada card do dashboard"""
    
    # Imagem do card
    imagem = ImageChooserBlock(
        required=False,
        help_text="Imagem de destaque do card (opcional)"
    )
    
    # Conteúdo do card
    numero = CharBlock(
        required=False,
        max_length=50,
        help_text="Texto principal do card (ex: '1', 'INSCRIÇÕES ABERTAS', 'EM BREVE')"
    )
    
    icone_fontawesome = ChoiceBlock(
        choices=FONTAWESOME_ICON_CHOICES,
        required=False,
        help_text="Ícone FontAwesome para exibir no card (usado quando não há número nem imagem)"
    )
    
    titulo = CharBlock(
        max_length=100,
        help_text="Título principal do card"
    )
    
    subtitulo = CharBlock(
        required=False,
        max_length=200,
        help_text="Subtítulo ou descrição breve"
    )
    
    descricao = TextBlock(
        required=False,
        help_text="Descrição completa do card"
    )
    
    # Link/Ação
    link_url = URLBlock(
        required=False,
        help_text="URL para onde o card deve levar (opcional)"
    )
    
    texto_botao = CharBlock(
        default="Ver mais informações →",
        max_length=100,
        help_text="Texto do botão de ação"
    )
    
    # Cor do botão
    cor_botao = ChoiceBlock(
        choices=ACCENT_COLOR_CHOICES,
        default='enap-green',
        help_text="Cor do botão"
    )

    class Meta:
        icon = 'doc-full'
        label = 'Card Destaque'


class TabDestaqueBlock(StructBlock):
    """Bloco para cada tab do dashboard"""
    
    id_tab = CharBlock(
        max_length=50,
        help_text="ID único da tab (ex: cpnu1, cpnu2, pdi)"
    )
    
    label_tab = CharBlock(
        max_length=100,
        help_text="Texto da tab (ex: CPNU 1, CPNU 2, PDI)"
    )
    
    icone_tab_fontawesome = ChoiceBlock(
        choices=FONTAWESOME_ICON_CHOICES,
        required=False,
        help_text="Ícone FontAwesome da tab"
    )
    
    
    descricao_tab = TextBlock(
        required=False,
        help_text="Descrição que aparece abaixo do título principal"
    )
    
    cards = ListBlock(
        CardDestaqueBlock(),
        help_text="Cards desta tab"
    )

    class Meta:
        icon = 'folder-open-1'
        label = 'Tab Destaque'


class DestaqueMainTabBlock(StructBlock):
    """Bloco principal do Dashboard CPNU"""
    
    # Configurações gerais
    titulo_principal = CharBlock(
        default="CPNU",
        max_length=100,
        help_text="Título principal do dashboard"
    )
    
    subtitulo = CharBlock(
        default="Concurso Público Nacional Unificado",
        max_length=200,
        help_text="Subtítulo explicativo"
    )
    
    # Layout e alinhamento
    alinhamento_texto = ChoiceBlock(
        choices=[
            ('left', 'Esquerda'),
            ('center', 'Centro'),
            ('right', 'Direita'),
        ],
        default='left',
        help_text="Alinhamento do texto do cabeçalho"
    )
    
    cards_por_linha = ChoiceBlock(
        choices=[
            ('2', '2 cards por linha'),
            ('3', '3 cards por linha'), 
            ('4', '4 cards por linha'),
        ],
        default='2',
        help_text="Quantidade de cards por linha no desktop"
    )
    
    # Tabs do dashboard
    tabs = ListBlock(
        TabDestaqueBlock(),
        min_num=1,
        help_text="Tabs do dashboard"
    )

    class Meta:
        icon = 'view'
        label = 'Tab para destaque com cards dentro'
        template = 'enap_designsystem/blocks/cpnu_dashboard_block.html'



class ClienteIndividualBlock(StructBlock):
    """Bloco para um cliente individual - apenas logo"""
    
    logo = ImageChooserBlock(
        label="Logo do Cliente",
        help_text="Logo da empresa (formato PNG/SVG recomendado para melhor qualidade)"
    )

    class Meta:
        template = "enap_designsystem/blocks/logo_cliente.html"
        icon = "image"
        label = "Logo Cliente"


class ClientesBlock(StructBlock):
    """Componente principal de clientes"""
    
    titulo = CharBlock(
        label="Título da Seção",
        max_length=200,
        help_text="Ex: 'Nossos Clientes', 'Empresas que Confiam'"
    )
    
    alinhamento_titulo = ChoiceBlock(
        label="Alinhamento do Título",
        choices=[
            ('center', 'Centro'),
            ('left', 'Esquerda'),
        ],
        default='center'
    )
    
    subtitulo = TextBlock(
        label="Subtítulo",
        required=False,
        max_length=500,
        help_text="Texto adicional abaixo do título (opcional)"
    )
    
    clientes = StreamBlock([
        ('logo_cliente', ClienteIndividualBlock()),
    ], 
    label="Logos dos Clientes",
    help_text="Adicione quantos logos quiser usando o botão +",
    min_num=1
    )

    
    mostrar_botao = BooleanBlock(
        label="Mostrar Botão",
        default=False,
        required=False,
        help_text="Marque para exibir um botão adicional na seção"
    )

    button = ButtonBlock(
        label="Botão",
        required=False,
        help_text="Configure o botão (só será exibido se 'Mostrar Botão' estiver marcado)"
    )

    class Meta:
        template = "enap_designsystem/blocks/clientes_block.html"
        icon = "group"
        label = "Seção de Patrocinadores"







class ItemLegislacaoBlock(StructBlock):
    """
    Bloco para um item individual de legislação
    """
    tipo = CharBlock(
        label="Tipo",
        help_text="Tipo da legislação (ex: Edital, Decreto, Portaria, Normativa)",
        max_length=100,
        required=True
    )
    
    titulo = CharBlock(
        label="Título",
        help_text="Título completo da legislação",
        max_length=255,
        required=True
    )
    
    link = URLBlock(
        label="Link",
        help_text="Link para o documento da legislação",
        required=False
    )
    
    class Meta:
        icon = "doc-full"
        label = "Item de Legislação"


class LegislacaoBlock(StructBlock):
    """
    Wrapper para seção de legislação - só título e lista de itens
    """
    titulo = CharBlock(
        label="Título da Seção",
        help_text="Título da seção (ex: Legislação)",
        max_length=100,
        default="Legislação",
        required=True
    )
    
    itens = StreamBlock(
        [('item_legislacao', ItemLegislacaoBlock())],  
        label="Itens de Legislação",
        help_text="Lista de documentos legais relacionados",
        min_num=1
    )
    
    class Meta:
        icon = "list-ul"
        label = "Legislação"
        template = "enap_designsystem/blocks/legislacao_block.html"









class SimpleDashboardChartBlock(blocks.StructBlock):
    """Gráfico simples com dados manuais"""
    
    CHART_TYPES = [
        ('card', 'Card com Número'),
        ('donut', 'Gráfico Donut'),
        ('bar', 'Gráfico de Barras'),
        ('pie', 'Gráfico de Pizza'),
        ('line', 'Gráfico de Linha'),
    ]
    
    # Configurações básicas
    title = blocks.CharBlock(
        label="Título do Gráfico",
        max_length=100,
        help_text="Ex: Matriculados por Curso"
    )
    
    subtitle = blocks.CharBlock(
        label="Subtítulo",
        max_length=200,
        required=False,
        help_text="Descrição adicional (opcional)"
    )
    
    chart_type = blocks.ChoiceBlock(
        choices=CHART_TYPES,
        label="Tipo de Gráfico",
        default='card'
    )
    
    # Dados do gráfico
    chart_data = blocks.ListBlock(
        blocks.StructBlock([
            ('label', blocks.CharBlock(
                label="Rótulo",
                max_length=50,
                help_text="Ex: ATPS, AIE, ATI"
            )),
            ('value', blocks.IntegerBlock(
                label="Valor",
                help_text="Ex: 483, 291, 214"
            )),
            ('color', blocks.CharBlock(
                label="Cor",
                max_length=7,
                required=False,
                help_text="Código da cor (#FF0000) - opcional"
            )),
        ]),
        label="Dados do Gráfico",
        help_text="Adicione os dados que aparecerão no gráfico"
    )
    
    # Configurações visuais
    width = blocks.ChoiceBlock(
        choices=[
            ('col-12', 'Largura Total (100%)'),
            ('col-6', 'Meia Largura (50%)'),
            ('col-4', 'Um Terço (33%)'),
            ('col-3', 'Um Quarto (25%)'),
        ],
        label="Largura do Gráfico",
        default='col-6'
    )
    
    height = blocks.IntegerBlock(
        label="Altura (pixels)",
        default=300,
        min_value=200,
        max_value=600,
        help_text="Altura do gráfico em pixels"
    )
    
    show_legend = blocks.BooleanBlock(
        label="Mostrar Legenda",
        default=True,
        required=False
    )
    
    color_scheme = blocks.ChoiceBlock(
        choices=[
            ('enap', 'Cores ENAP (Azul/Verde)'),
            ('blue', 'Tons de Azul'),
            ('green', 'Tons de Verde'),
            ('warm', 'Cores Quentes'),
            ('cool', 'Cores Frias'),
        ],
        label="Esquema de Cores",
        default='enap'
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
        ('trending-down', 'Decrescimento'),
        ('activity', 'Atividade'),
        ('target', 'Meta'),
        ('award', 'Prêmio'),
        ('calendar', 'Calendário'),
        ('book', 'Livro/Curso'),
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
    
    subtitle = blocks.CharBlock(
        label="Subtítulo",
        max_length=100,
        required=False,
        help_text="Informação adicional (opcional)"
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
    
    # Indicador de tendência (opcional)
    show_trend = blocks.BooleanBlock(
        label="Mostrar Tendência",
        default=False,
        required=False
    )
    
    trend_direction = blocks.ChoiceBlock(
        choices=[
            ('up', 'Para Cima ↗'),
            ('down', 'Para Baixo ↘'),
        ],
        label="Direção da Tendência",
        default='up',
        required=False
    )
    
    trend_percentage = blocks.CharBlock(
        label="Porcentagem da Tendência",
        max_length=10,
        required=False,
        help_text="Ex: 5.2%, 12%"
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
    
    background_color = blocks.ChoiceBlock(
        choices=[
            ('', 'Transparente'),
            ('bg-light', 'Fundo Claro'),
            ('bg-primary-light', 'Fundo Azul Claro'),
            ('bg-success-light', 'Fundo Verde Claro'),
        ],
        label="Cor de Fundo",
        default='',
        required=False
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/simple_dashboard_row.html'
        icon = 'grip'
        label = "Linha de Gráficos"


class SimpleDashboardContainerBlock(blocks.StructBlock):
    """Container principal do dashboard"""
    
    dashboard_title = blocks.CharBlock(
        label="Título do Dashboard",
        max_length=200,
        help_text="Ex: Dashboard de Matrículas"
    )
    
    description = blocks.TextBlock(
        label="Descrição",
        required=False,
        help_text="Descrição do que o dashboard mostra"
    )
    
    # KPIs de destaque no topo
    highlight_kpis = blocks.ListBlock(
        SimpleKPICardBlock(),
        label="KPIs de Destaque",
        required=False,
        help_text="KPIs principais que aparecerão no topo"
    )
    
    # Linhas de gráficos
    dashboard_rows = blocks.ListBlock(
        SimpleDashboardRowBlock(),
        label="Linhas do Dashboard",
        help_text="Organize seus gráficos em seções"
    )
    
    # Configurações visuais
    show_last_update = blocks.BooleanBlock(
        label="Mostrar Última Atualização",
        default=True,
        required=False,
        help_text="Mostra data/hora da última atualização"
    )
    
    enable_print = blocks.BooleanBlock(
        label="Habilitar Impressão",
        default=True,
        required=False,
        help_text="Adiciona botão para imprimir dashboard"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/simple_dashboard_container.html'
        icon = 'view'
        label = "Dashboard Completo"






class CardBlock(blocks.StructBlock):
    """
    Bloco individual para um card com imagem, título, descrição e link
    """
    image = ImageChooserBlock(
        label="Imagem do Card",
        required=True,
        help_text="Imagem que será exibida no card"
    )
    
    title = blocks.CharBlock(
        label="Título",
        max_length=100,
        required=True,
        help_text="Título principal do card"
    )
    
    subtitle = blocks.CharBlock(
        label="Subtítulo/Cargo",
        max_length=150,
        required=False,
        help_text="Subtítulo ou cargo da pessoa (opcional)"
    )
    
    description = blocks.RichTextBlock(
        label="Descrição",
        required=False,
        help_text="Descrição adicional do card",
        features=['bold', 'italic', 'link']
    )
    
    link_url = blocks.URLBlock(
        label="URL do Link",
        required=False,
        help_text="Link para página externa ou interna"
    )
    
    link_text = blocks.CharBlock(
        label="Texto do Link",
        max_length=50,
        required=False,
        default="Saiba mais",
        help_text="Texto que aparecerá no botão/link"
    )
    
    link_target = blocks.ChoiceBlock(
        label="Abrir link em",
        choices=[
            ('_self', 'Mesma janela'),
            ('_blank', 'Nova janela'),
        ],
        default='_self',
        required=False
    )

    class Meta:
        icon = 'user'
        label = 'Card'
        template = 'enap_designsystem/blocks/card_item.html'


class CardsSectionBlock(blocks.StructBlock):
    """
    Seção com título e lista de cards
    """
    section_title = blocks.CharBlock(
        label="Título da Seção",
        max_length=200,
        required=True,
        help_text="Título principal da seção de cards"
    )
    
    section_subtitle = blocks.CharBlock(
        label="Subtítulo da Seção",
        max_length=300,
        required=False,
        help_text="Subtítulo ou descrição da seção (opcional)"
    )
    
    cards = blocks.ListBlock(
        CardBlock(),
        label="Cards",
        min_num=1,
        max_num=12,
        help_text="Adicione os cards que serão exibidos nesta seção"
    )
    
    cards_per_row = blocks.ChoiceBlock(
        label="Cards por linha",
        choices=[
            ('2', '2 cards por linha'),
            ('3', '3 cards por linha'),
            ('4', '4 cards por linha'),
        ],
        default='4',
        help_text="Quantos cards serão exibidos por linha (desktop)"
    )
    
    background_color = blocks.ChoiceBlock(
        label="Cor de fundo",
        choices=[
            ('bg-white', 'Branco'),
            ('bg-gray-50', 'Cinza claro'),
            ('bg-blue-50', 'Azul claro'),
            ('bg-primary-50', 'Primário claro'),
        ],
        default='bg-white',
        required=False
    )

    class Meta:
        icon = 'grip'
        label = 'Seção de Cards'
        template = 'enap_designsystem/blocks/cards_section.html'




class StatisticCardBlock(blocks.StructBlock):
    """
    Bloco individual para um card de estatística com número e descrição
    """
    number = blocks.CharBlock(
        label="Número",
        max_length=20,
        required=True,
        help_text="Número ou estatística principal (ex: 140, 45%, R$ 2.5M)"
    )
    
    description = blocks.CharBlock(
        label="Descrição",
        max_length=100,
        required=True,
        help_text="Descrição do que representa o número"
    )
    
    color = blocks.ChoiceBlock(
        label="Cor do Texto",
        choices=[
            ('text-green-400', 'Verde Claro'),
            ('text-green-500', 'Verde'),
            ('text-green-600', 'Verde Escuro'),
            ('text-blue-400', 'Azul Claro'),
            ('text-blue-500', 'Azul'),
            ('text-blue-600', 'Azul Escuro'),
            ('text-purple-400', 'Roxo Claro'),
            ('text-purple-500', 'Roxo'),
            ('text-orange-400', 'Laranja Claro'),
            ('text-orange-500', 'Laranja'),
            ('text-primary-400', 'Primário Claro'),
            ('text-primary-500', 'Primário'),
            ('text-white', 'Branco'),
        ],
        default='text-green-400',
        help_text="Cor que será aplicada ao número"
    )

    class Meta:
        icon = 'snippet'
        label = 'Card de Estatística'
        template = 'enap_designsystem/blocks/statistic_card.html'


class StatisticsSectionBlock(blocks.StructBlock):
    """
    Seção com título e cards de estatísticas configuráveis
    """
    section_title = blocks.CharBlock(
        label="Título da Seção",
        max_length=200,
        required=True,
        help_text="Título principal da seção de estatísticas"
    )
    
    section_subtitle = blocks.CharBlock(
        label="Subtítulo da Seção",
        max_length=300,
        required=False,
        help_text="Subtítulo ou descrição da seção (opcional)"
    )
    
    statistics = blocks.ListBlock(
        StatisticCardBlock(),
        label="Estatísticas",
        min_num=1,
        max_num=8,
        help_text="Adicione quantas estatísticas quiser (recomendado: 3-5 para melhor layout)"
    )
    
    background_style = blocks.ChoiceBlock(
        label="Estilo de Fundo",
        choices=[
            ('bg-primary-600', 'Fundo Verde ENAP'),
            ('bg-primary-700', 'Fundo Verde Escuro'),
            ('bg-gray-800', 'Fundo Cinza Escuro'),
            ('bg-blue-600', 'Fundo Azul'),
            ('bg-white', 'Fundo Branco'),
            ('bg-gray-50', 'Fundo Cinza Claro'),
        ],
        default='bg-primary-600',
        help_text="Cor de fundo da seção completa"
    )
    
    text_alignment = blocks.ChoiceBlock(
        label="Alinhamento do Texto",
        choices=[
            ('text-center', 'Centralizado'),
            ('text-left', 'Esquerda'),
        ],
        default='text-center',
        help_text="Como os textos serão alinhados nos cards"
    )
    
    cards_layout = blocks.ChoiceBlock(
        label="Layout dos Cards",
        choices=[
            ('auto', 'Automático (responsivo)'),
            ('2', '2 cards por linha'),
            ('3', '3 cards por linha'),
            ('4', '4 cards por linha'),
            ('5', '5 cards por linha'),
        ],
        default='auto',
        help_text="Como os cards serão organizados (automático se adapta à quantidade)"
    )

    class Meta:
        icon = 'list-ol'
        label = 'Seção de Estatísticas'
        template = 'enap_designsystem/blocks/statistics_section.html'




class HTMLCustomBlock(blocks.StructBlock):
    """Block simples para inserir HTML customizado"""
    
    html_content = blocks.RawHTMLBlock(
        label="Código HTML",
        help_text="Cole seu código HTML aqui"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/html_custom_block.html'
        icon = 'code'
        label = 'HTML Customizado'







class CarouselResponsivoSnippetBlock(SnippetChooserBlock):
    """
    Block para escolher um carrossel responsivo (snippet)
    """
    def __init__(self, **kwargs):
        # ✅ IMPORTANTE: usar o nome correto do app
        super().__init__('enap_designsystem.CarouselResponsivo', **kwargs)

    class Meta:
        template = 'enap_designsystem/blocks/carousel_responsivo_snippet.html'
        icon = 'image'
        label = 'Carrossel Responsivo'






class Error404Block(StructBlock):
    """Componente para página de erro 404"""
    
    titulo = CharBlock(
        max_length=100,
        default="Ops! Página não encontrada",
        help_text="Título principal da página 404"
    )
    
    subtitulo = CharBlock(
        max_length=200,
        default="A página que você está procurando não existe ou foi movida.",
        help_text="Descrição do erro"
    )
    
    mensagem_adicional = RichTextBlock(
        required=False,
        help_text="Texto adicional (opcional)"
    )
    
    mostrar_busca = BooleanBlock(
        default=True,
        required=False,
        help_text="Mostrar campo de busca"
    )
    
    mostrar_links_uteis = BooleanBlock(
        default=True,
        required=False,
        help_text="Mostrar links para páginas importantes"
    )
    
    class Meta:
        template = "enap_designsystem/blocks/error_404_block.html"
        icon = "warning"
        label = "Erro 404"
        help_text = "Componente para página de erro 404"







class TimelineEtapaBlock(blocks.StructBlock):
    """
    Card individual de etapa do timeline - Design System ENAP
    """
    numero = blocks.CharBlock(
        required=False,
        max_length=10,
        help_text="Número da etapa (ex: 01, 02, 03... ou deixe vazio para numeração automática)",
        label="Número"
    )
    
    titulo = blocks.CharBlock(
        required=True,
        max_length=200,
        help_text="Título da etapa",
        label="Título"
    )
    
    descricao = blocks.RichTextBlock(
        required=False,
        help_text="Descrição detalhada da etapa",
        label="Descrição",
        features=['bold', 'italic', 'link']
    )
    
    # Ícone FontAwesome
    icone_fontawesome = blocks.ChoiceBlock(
        choices=FONTAWESOME_ICON_CHOICES,
        required=False,
        help_text="Ícone FontAwesome para a etapa",
        label="Ícone FontAwesome"
    )
    
    # Ou imagem personalizada
    icone_imagem = ImageChooserBlock(
        required=False,
        help_text="Ou use uma imagem personalizada",
        label="Ícone Personalizado"
    )
    
    cor_destaque = blocks.ChoiceBlock(
        choices=ACCENT_COLOR_CHOICES,
        default='enap-green',
        required=False,
        help_text="Cor de destaque do card",
        label="Cor de Destaque"
    )
    
    link_botao = blocks.URLBlock(
        required=False,
        help_text="Link opcional para ação na etapa",
        label="Link do Botão"
    )
    
    texto_botao = blocks.CharBlock(
        required=False,
        max_length=50,
        help_text="Texto do botão de ação",
        label="Texto do Botão",
        default="Saiba mais"
    )
    class Meta:
        icon = 'list-ol'
        label = 'Etapa do Timeline'
        template = 'enap_designsystem/blocks/timeline_etapa.html'



class TimelineBlock(blocks.StructBlock):
    """
    Timeline de etapas - Design System ENAP
    """
    titulo = blocks.CharBlock(
        required=False,
        max_length=200,
        help_text="Título principal do timeline",
        label="Título"
    )
    
    descricao = blocks.RichTextBlock(
        required=False,
        help_text="Descrição do processo ou timeline",
        label="Descrição",
        features=['bold', 'italic', 'link']
    )
    
    alinhamento_titulo = blocks.ChoiceBlock(
        choices=[
            ('left', 'Esquerda'),
            ('center', 'Centro'),
        ],
        default='left',
        required=False,
        help_text="Alinhamento do título e descrição",
        label="Alinhamento do Título"
    )
    
    estilo_layout = blocks.ChoiceBlock(
        choices=[
            ('vertical', 'Vertical (Padrão)'),
            ('horizontal', 'Horizontal com Linha'),
            ('minimal', 'Minimalista'),
            ('cards', 'Cards Conectados'),
        ],
        default='vertical',
        required=False,
        help_text="Estilo do layout do timeline",
        label="Estilo do Layout"
    )
    
    mostrar_conectores = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Mostrar linhas conectando as etapas",
        label="Mostrar Conectores"
    )
    
    numeracao_automatica = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Numerar automaticamente as etapas (ignora números manuais)",
        label="Numeração Automática"
    )
    
    tamanho_cards = blocks.ChoiceBlock(
        choices=[
            ('compact', 'Compacto'),
            ('standard', 'Padrão'),
            ('expanded', 'Expandido'),
        ],
        default='standard',
        required=False,
        help_text="Tamanho dos cards das etapas",
        label="Tamanho dos Cards"
    )
    
    cor_tema = blocks.ChoiceBlock(
        choices=ACCENT_COLOR_CHOICES,
        default='enap-green',
        required=False,
        help_text="Cor principal do timeline",
        label="Cor do Tema"
    )
    
    etapas = blocks.StreamBlock([
        ('etapa', TimelineEtapaBlock()),
    ], min_num=1, label="Etapas do Timeline")

    class Meta:
        icon = 'timeline'
        label = 'Timeline de Etapas'
        template = 'enap_designsystem/blocks/timeline.html'







class DepoimentoVideoBlock(blocks.StructBlock):
    """
    Componente para exibir depoimento em vídeo individual
    """
    nome_pessoa = blocks.CharBlock(
        label="Nome da pessoa",
        max_length=100,
        help_text="Nome completo da pessoa que está dando o depoimento"
    )
    
    cargo_instituicao = blocks.CharBlock(
        label="Cargo e Instituição",
        max_length=200,
        required=False,
        help_text="Ex: Diretor de TI - Ministério da Educação"
    )
    
    foto_pessoa = ImageChooserBlock(
        label="Foto da pessoa",
        required=False,
        help_text="Foto de perfil da pessoa (opcional, caso o vídeo não mostre claramente)"
    )
    
    video_url = blocks.URLBlock(
        label="URL do vídeo",
        required=False,
        help_text="Link do YouTube, Vimeo ou outro serviço de vídeo"
    )
    
    video_embed = EmbedBlock(
        label="Vídeo incorporado",
        required=False,
        help_text="Cole a URL do vídeo para incorporação automática"
    )
    
    video_arquivo = DocumentChooserBlock(
        label="Arquivo de vídeo",
        required=False,
        help_text="Upload direto do arquivo de vídeo (MP4, WebM, etc.)"
    )
    
    transcricao = blocks.TextBlock(
        label="Transcrição do depoimento",
        required=False,
        help_text="Texto completo do depoimento para acessibilidade"
    )
    
    resumo_depoimento = blocks.TextBlock(
        label="Resumo do depoimento",
        max_length=300,
        required=False,
        help_text="Breve resumo ou frase de destaque do depoimento"
    )
    
    duracao = blocks.CharBlock(
        label="Duração",
        max_length=10,
        required=False,
        help_text="Ex: 2:30"
    )
    
    data_gravacao = blocks.DateBlock(
        label="Data da gravação",
        required=False
    )

    class Meta:
        template = 'enap_designsystem/blocks/depoimento_video.html'
        icon = 'media'
        label = 'Depoimento em Vídeo'
        help_text = 'Componente para exibir depoimento individual em vídeo'


class DepoimentosVideoListBlock(blocks.StructBlock):
    """
    Lista de depoimentos em vídeo com configurações de layout
    """
    titulo_secao = blocks.CharBlock(
        label="Título da seção",
        default="Depoimentos",
        help_text="Título principal da seção de depoimentos"
    )
    
    subtitulo = blocks.TextBlock(
        label="Subtítulo",
        required=False,
        help_text="Texto explicativo sobre os depoimentos"
    )
    
    layout_opcoes = blocks.ChoiceBlock(
        label="Layout de exibição",
        choices=[
            ('grid', 'Grade (cards lado a lado)'),
            ('carousel', 'Carrossel deslizante'),
            ('lista', 'Lista vertical'),
            ('destaque', 'Um em destaque + lista')
        ],
        default='grid'
    )
    
    videos_por_linha = blocks.IntegerBlock(
        label="Vídeos por linha",
        default=2,
        min_value=1,
        max_value=4,
        help_text="Quantidade de vídeos por linha no layout grade"
    )
    
    mostrar_transcricao = blocks.BooleanBlock(
        label="Mostrar transcrição",
        default=True,
        required=False,
        help_text="Exibir botão para mostrar/ocultar transcrição"
    )
    
    depoimentos = blocks.ListBlock(
        DepoimentoVideoBlock(),
        label="Lista de depoimentos",
        min_num=1,
        help_text="Adicione os depoimentos em vídeo"
    )

    class Meta:
        template = 'enap_designsystem/blocks/depoimentos_video_list.html'
        icon = 'list-ul'
        label = 'Lista de Depoimentos em Vídeo'
        help_text = 'Seção completa com múltiplos depoimentos em vídeo'






class FormularioDinamicoBlock(blocks.StructBlock):
    """
    Formulário dinâmico que usa os campos existentes do BASE_FORM_FIELD_BLOCKS
    """
    titulo = blocks.CharBlock(
        required=False,
        default="Formulário",
        help_text="Título do formulário"
    )
    
    descricao = blocks.TextBlock(
        required=False,
        help_text="Descrição ou instruções do formulário"
    )
    
    # Usar seus campos existentes
    campos = blocks.StreamBlock(
        BASE_FORM_FIELD_BLOCKS,
        label="Campos do Formulário",
        help_text="Adicione e configure os campos do formulário"
    )
    
    # Configurações
    email_notificacao = blocks.EmailBlock(
        required=False,
        help_text="E-mail para receber notificações (opcional)"
    )
    
    mensagem_sucesso = blocks.TextBlock(
        required=False,
        default="Obrigado! Seu formulário foi enviado com sucesso.",
        help_text="Mensagem exibida após envio bem-sucedido"
    )
    
    botao_texto = blocks.CharBlock(
        required=False,
        default="Enviar",
        help_text="Texto do botão de envio"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/formulario_dinamico.html'
        icon = 'form'
        label = 'Formulário Dinâmico'
        help_text = 'Formulário personalizável que salva no sistema de exportação'
    
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        
        # ID único para o formulário
        context['form_id'] = f"form_dinamico_{uuid.uuid4().hex[:8]}"
        
        # Página atual
        if parent_context:
            context['page'] = parent_context.get('page')
        
        return context










