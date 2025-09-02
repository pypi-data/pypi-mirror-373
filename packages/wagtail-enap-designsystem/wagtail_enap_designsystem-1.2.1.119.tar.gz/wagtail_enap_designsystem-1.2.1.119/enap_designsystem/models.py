from django.db import models
from wagtail.admin.panels import FieldPanel
from django.utils.translation import gettext_lazy as _
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import RichTextBlock
from wagtail import blocks
from wagtail.admin.panels import PageChooserPanel
from wagtail.models import Page
from .blocks.semana_inovacao import *
from .blocks.semana_blocks import *
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.images.blocks import ImageChooserBlock
from wagtail.fields import StreamField
from coderedcms.models import CoderedWebPage
from modelcluster.models import ClusterableModel
from wagtail.blocks import URLBlock
from wagtail.search import index
import requests
import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import shutil
import os
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from wagtail.snippets.models import register_snippet
from django.utils.html import strip_tags
import re
from wagtail.admin.panels import FieldPanel
from enap_designsystem.blocks import TextoImagemBlock
from django.shortcuts import redirect, render
from django.conf import settings
from datetime import datetime
from .utils.sso import get_valid_access_token
from wagtail.blocks import PageChooserBlock, StructBlock, CharBlock, BooleanBlock, ListBlock, IntegerBlock
from django.conf import settings

from .blocks.layout_blocks import EnapAccordionBlock

from wagtail.blocks import StreamBlock, StructBlock, CharBlock, ChoiceBlock, RichTextBlock, ChooserBlock, ListBlock


from django.db import models
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import MultiFieldPanel, FieldPanel, InlinePanel
from wagtail.documents.models import Document
from wagtail.fields import StreamField
from .blocks import ButtonBlock
from .blocks import ImageBlock
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable

from wagtail.images.models import Image
from django.dispatch import receiver
from wagtail.images import get_image_model_string
from enap_designsystem.blocks import EnapFooterGridBlock
from enap_designsystem.blocks import EnapFooterSocialGridBlock 
from enap_designsystem.blocks import EnapAccordionPanelBlock
from enap_designsystem.blocks import EnapNavbarLinkBlock
from enap_designsystem.blocks import EnapCardBlock
from enap_designsystem.blocks import EnapCardGridBlock
from enap_designsystem.blocks import EnapSectionBlock
from .blocks import ClientesBlock 

from django.http import Http404
from django.shortcuts import render
from wagtail.models import Page

from enap_designsystem.blocks import PageListBlock
from enap_designsystem.blocks import NewsCarouselBlock
from enap_designsystem.blocks import DropdownBlock
from enap_designsystem.blocks import CoursesCarouselBlock
from enap_designsystem.blocks import SuapCourseBlock
from enap_designsystem.blocks import HolofoteCarouselBlock
from enap_designsystem.blocks import SuapEventsBlock
from enap_designsystem.blocks import PreviewCoursesBlock
from enap_designsystem.blocks import EventsCarouselBlock
from enap_designsystem.blocks import EnapBannerBlock
from enap_designsystem.blocks import FeatureImageTextBlock
from enap_designsystem.blocks import EnapAccordionBlock
from enap_designsystem.blocks.base_blocks import ButtonGroupBlock
from enap_designsystem.blocks.base_blocks import CarouselBlock
from enap_designsystem.blocks import CourseIntroTopicsBlock
from .blocks import WhyChooseEnaptBlock
from .blocks import CourseFeatureBlock
from .blocks import CourseModulesBlock
from .blocks import ProcessoSeletivoBlock
from .blocks import TeamCarouselBlock  
from .blocks import TestimonialsCarouselBlock
from .blocks import CarouselGreen
from .blocks import TeamModern
from .blocks import HeroBlockv3
from .blocks import TopicLinksBlock
from .blocks import AvisoBlock
from .blocks import FeatureListBlock
from .blocks import ServiceCardsBlock
from .blocks import CitizenServerBlock
from .blocks import CarrosselCursosBlock
from .blocks import Banner_Image_cta
from .blocks import FeatureWithLinksBlock
from .blocks import QuoteBlockModern
from .blocks import CardCursoBlock
from .blocks import HeroAnimadaBlock
from .blocks import EventoBlock
from .blocks import ContainerInfo
from .blocks import CtaDestaqueBlock
from .blocks import SecaoAdesaoBlock
from .blocks import SectionTabsCardsBlock
from .blocks import GalleryModernBlock
from .blocks import ContatoBlock
from .blocks import FormContato
from .blocks import DownloadBlock
from .blocks import SectionCardTitleCenterBlock
from .blocks import CTA2Block
from .blocks import AccordionItemBlock
from .blocks.html_blocks import HeroMenuItemBlock 
from .blocks.form import FormularioPage


from wagtail.snippets.blocks import SnippetChooserBlock

from enap_designsystem.blocks import LAYOUT_STREAMBLOCKS
from enap_designsystem.blocks import DYNAMIC_CARD_STREAMBLOCKS
from enap_designsystem.blocks import CARD_CARDS_STREAMBLOCKS

# class ComponentLayout(models.Model):
#     name = models.CharField(max_length=255)
#     content = models.TextField()

#     panels = [
#         FieldPanel("name"),
#         FieldPanel("content"),
#     ]

#     class Meta:
#         abstract = True



class ENAPComponentes(Page):
	"""Página personalizada independente do CoderedWebPage."""

	parent_page_types = ['MbaEspecializacao']
	
	admin_notes = models.TextField(
		verbose_name="Anotações Internas",
		blank=True,
		help_text="Escreva observações importantes. Este campo é visível apenas para administradores."
	)

	template = "enap_designsystem/pages/enap_layout.html"

	body = StreamField(
		LAYOUT_STREAMBLOCKS,
		null=True,
		blank=True,
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
		FieldPanel("body"),
		FieldPanel("footer"),
		FieldPanel("admin_notes"),
	]

	@property
	def url_filter(self):
		if hasattr(self, 'full_url') and self.full_url:
			return self.full_url
		return self.get_url_parts()[2] if self.get_url_parts() else ""
	
	@property
	def titulo_filter(self):
		for block in self.body:
			if block.block_type == "enap_herobanner":
				return block.value.get("title", "")
		return ""

	@property
	def descricao_filter(self):
		for block in self.body:
			if block.block_type == "enap_herobanner":
				desc = block.value.get("description", "")
				if hasattr(desc, "source"):
					return strip_tags(desc.source).strip()
				return strip_tags(str(desc)).strip()
		return ""

	@property
	def data_atualizacao_filter(self):
		return self.last_published_at or self.latest_revision_created_at

	@property
	def categoria(self):
		return "Especialização"
	
	@property
	def imagem_filter(self):
		tipos_com_imagem = [
			("enap_herobanner", "background_image"),
			("bannertopics", "imagem_fundo"),
			("banner_image_cta", "hero_image"),
			("hero", "background_image"),
			("banner_search", "imagem_principal"),
		]

		try:
			for bloco in self.body:
				for tipo, campo_imagem in tipos_com_imagem:
					if bloco.block_type == tipo:
						imagem = bloco.value.get(campo_imagem)
						if imagem:
							return imagem.file.url
		except Exception:
			pass

		return ""
	
	@property
	def texto_unificado(self):
		def extract_text_from_block(block_value):
			result = []

			if isinstance(block_value, list):
				for subblock in block_value:
					result.extend(extract_text_from_block(subblock))
			elif hasattr(block_value, "get"):  # StructValue
				for key, val in block_value.items():
					result.extend(extract_text_from_block(val))
			elif isinstance(block_value, str):
				cleaned = strip_tags(block_value).strip()
				if cleaned and cleaned.lower() not in {
					"default", "tipo terciário", "tipo secundário", "tipo bg image",
					"bg-gray", "bg-blue", "bg-white", "fundo cinza", "fundo branco"
				}:
					result.append(cleaned)
			elif hasattr(block_value, "source"):  # RichText
				cleaned = strip_tags(block_value.source).strip()
				if cleaned:
					result.append(cleaned)

			return result

		textos = []
		if hasattr(self, "body") and self.body:
			for block in self.body:
				textos.extend(extract_text_from_block(block.value))

		# Junta tudo em uma string e remove quebras de linha duplicadas
		texto_final = " ".join([t for t in textos if t])
		texto_final = re.sub(r"\s+", " ", texto_final).strip()  # Remove espaços e quebras em excesso
		return texto_final

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
		verbose_name = "ENAP Componentes"
		verbose_name_plural = "ENAP Componentes"





class ENAPSemana(Page):
	"""Página personalizada independente do CoderedWebPage."""
	
	admin_notes = models.TextField(
		verbose_name="Anotações Internas",
		blank=True,
		help_text="Escreva observações importantes. Este campo é visível apenas para administradores."
	)

	template = "enap_designsystem/pages/enap_layout_semana.html"

	body = StreamField(
		SEMANA_INOVACAO_STREAMBLOCKS,
		null=True,
		blank=True,
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
		FieldPanel("body"),
		FieldPanel("footer"),
		FieldPanel("admin_notes"),
	]

	class Meta:
		verbose_name = "ENAP Semana"
		verbose_name_plural = "ENAP Semana"




class ENAPFormacao(CoderedWebPage):
	"""Página personalizada herdando todas as características de CoderedWebPage."""

	admin_notes = models.TextField(
		verbose_name="Anotações Internas",
		blank=True,
		help_text="Escreva observações importantes."
	)

	template = "enap_designsystem/pages/template_cursos.html"
	miniview_template = "coderedcms/pages/article_page.mini.html"
	search_template = "coderedcms/pages/article_page.search.html"

	content = StreamField(
		[("banner", EnapBannerBlock())],
		null=True,
		blank=True,
		use_json_field=True,
	)

	feature = StreamField(
		[("enap_herofeature", FeatureImageTextBlock())],
		null=True,
		blank=True,
		use_json_field=True,
	)

	accordion_cursos = StreamField(
		[
			("enap_accordion", EnapAccordionBlock()),
			("button_group", ButtonGroupBlock()),
			("carousel", CarouselBlock()),
			("dropdown", DropdownBlock()),
		],
		null=True,
		blank=True,
		use_json_field=True,
	)

	body = StreamField(
		CARD_CARDS_STREAMBLOCKS,
		null=True,
		blank=True,
		use_json_field=True,
	)

	modal = models.ForeignKey("enap_designsystem.Modal", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
	navbar = models.ForeignKey("EnapNavbarSnippet", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
	footer = models.ForeignKey("EnapFooterSnippet", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
	modalenap = models.ForeignKey("enap_designsystem.ModalBlock", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
	alert = models.ForeignKey("Alert", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
	wizard = models.ForeignKey("Wizard", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
	FormularioContato = models.ForeignKey("FormularioContato", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
	tab = models.ForeignKey("Tab", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

	@property
	def titulo_filter(self):
		return strip_tags(self.title or "").strip()

	@property
	def descricao_filter(self):
		return strip_tags(self.admin_notes or "").strip()

	@property
	def categoria(self):
		return "Cursos"

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
			for bloco in self.content:
				if bloco.block_type == "banner":
					background = bloco.value.get("background_image")
					if background:
						return background.file.url
		except Exception:
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
				for _, val in block_value.items():
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
		for sf in [self.content, self.feature, self.accordion_cursos, self.body]:
			if sf:
				for block in sf:
					textos.extend(extract_text_from_block(block.value))

		if self.admin_notes:
			textos.append(strip_tags(self.admin_notes).strip())

		return re.sub(r"\s+", " ", " ".join([t for t in textos if t])).strip()

	search_fields = CoderedWebPage.search_fields + [
		index.SearchField("title", boost=3),
		index.SearchField("titulo_filter", name="titulo"),
		index.SearchField("descricao_filter", name="descricao"),
		index.FilterField("categoria", name="categoria_filter"),
		index.SearchField("url_filter", name="url"),
		index.SearchField("data_atualizacao_filter", name="data_atualizacao"),
		index.SearchField("imagem_filter", name="imagem"),
		index.SearchField("texto_unificado", name="body"),
	]

	content_panels = CoderedWebPage.content_panels + [
		FieldPanel('navbar'),
		FieldPanel('modal'),
		FieldPanel('modalenap'),
		FieldPanel('wizard'),
		FieldPanel('alert'),
		FieldPanel('FormularioContato'),
		FieldPanel('tab'),
		FieldPanel('footer'),
		FieldPanel('content'),
		FieldPanel('feature'),
		FieldPanel('accordion_cursos'),
	]
	
	class Meta:
		verbose_name = "Template ENAP Curso"
		verbose_name_plural = "Template ENAP Cursos"


class ENAPTemplatev1(CoderedWebPage):
	"""Página personalizada herdando todas as características de CoderedWebPage."""
	
	admin_notes = models.TextField(
		verbose_name="Anotações Internas",
		blank=True,
		help_text="Escreva observações importantes."
	)

	template = "enap_designsystem/pages/template_homeI.html"
	miniview_template = "coderedcms/pages/article_page.mini.html"
	search_template = "coderedcms/pages/article_page.search.html"

	page_destaque = RichTextField(
		max_length=255, 
		default="Título Padrão", 
		verbose_name="Título da Página"
	)

	hero_menu_items = StreamField(
        [("menu_item", HeroMenuItemBlock())],
        null=True,
        blank=True,
        use_json_field=True,
        verbose_name="Itens do Menu Hero",
        help_text="Adicione quantos itens de menu quiser. Cada item terá um dropdown com as páginas filhas.",
		default=list
    )

	body_stream = StreamField(
		LAYOUT_STREAMBLOCKS,
		null=True,
		blank=True,
		use_json_field=True,
	)

	body = StreamField(
		DYNAMIC_CARD_STREAMBLOCKS,
		null=True,
		blank=True,
		use_json_field=True,
	)

	suap_courses = StreamField(
		[("suap_courses", SuapCourseBlock())],
		null=True,
		blank=True,
		use_json_field=True,
	)

	suap_events = StreamField(
		[("suap_events", SuapEventsBlock())],
		null=True,
		blank=True,
		use_json_field=True,
	)

	noticias = StreamField(
		[("eventos_carousel", EventsCarouselBlock())], 
		null=True,
		blank=True,
		use_json_field=True,
	)

	teste_noticia = StreamField(
		[("noticias_carousel", NewsCarouselBlock())], 
		null=True,
		blank=True,
		use_json_field=True,
	)

	teste_preview = StreamField(
		[("page_preview_teste", HolofoteCarouselBlock())],
		null=True,
		blank=True,
		use_json_field=True,
	)
	
	paragrafo = RichTextField(
		blank=True, 
		help_text="Adicione o texto do parágrafo aqui.", 
		verbose_name="Parágrafo sessao dinamica"
	)
	
	video_background = models.FileField(
		upload_to='media/videos', 
		null=True, 
		blank=True, 
		verbose_name="Vídeo de Fundo"
	)

	background_image = StreamField(
		[
			("image", ImageBlock()),
		],
		null=True,
		blank=True,
		use_json_field=True,
	)

	linkcta = RichTextField(blank=True)
	button_link = models.URLField(
		"Link do Botão",
		blank=True,
		help_text="URL do link do botão"
	)

	parceiros = StreamField([
        ("clientes", ClientesBlock()),
    ], blank=True, help_text="Adicione componentes à sua página", use_json_field=True)
    

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

	# Painéis no admin do Wagtail
	content_panels = CoderedWebPage.content_panels + [
		FieldPanel('navbar'),
		FieldPanel('video_background'),
		FieldPanel('hero_menu_items'),
		MultiFieldPanel(
			[
				FieldPanel('page_destaque'),
				FieldPanel('paragrafo'),
				FieldPanel('background_image'),
				FieldPanel('button_link'),
			],
			heading="Título e Parágrafo CTA Dinamico"
		),
		FieldPanel('suap_courses'),
		FieldPanel('suap_events'),
		FieldPanel('body_stream'),
		FieldPanel('noticias'),
		FieldPanel('teste_preview'),
		FieldPanel('teste_noticia'),
		FieldPanel('parceiros'),  
		FieldPanel('footer'),
	]

	@property
	def url_filter(self):
		if hasattr(self, 'full_url') and self.full_url:
			return self.full_url
		return self.get_url_parts()[2] if self.get_url_parts() else ""

	search_fields = []

	def get_searchable_content(self):
		content = super().get_searchable_content()

		if self.page_title:
			content.append(self.page_title)
		if self.paragrafo:
			content.append(self.paragrafo)
		if self.linkcta:
			content.append(self.linkcta)

		def extract_text_from_block(block_value):
			result = []

			if isinstance(block_value, list):  # lista de blocos (ex: StreamBlock)
				for subblock in block_value:
					result.extend(extract_text_from_block(subblock))
			elif hasattr(block_value, "get"):  # tipo StructValue
				for key, val in block_value.items():
					result.extend(extract_text_from_block(val))
			elif isinstance(block_value, str):
				result.append(block_value)
			elif hasattr(block_value, "source"):  # RichText
				result.append(block_value.source)

			return result

		# StreamFields a indexar
		streamfields = [
			self.body,
			self.teste_courses,
			self.suap_courses,
			self.noticias,
			self.teste_noticia,
			self.teste_preview,
			self.dropdown_content,
		]

		for sf in streamfields:
			if sf:
				for block in sf:
					content.extend(extract_text_from_block(block.value))

		return content

	
	
	class Meta:
		verbose_name = "Enap home v1"
		verbose_name_plural = "Enap Home v1"


class ENAPTeste(CoderedWebPage):
	"""Página personalizada herdando todas as características de CoderedWebPage."""
	
	admin_notes = models.TextField(
		verbose_name="Anotações Internas",
		blank=True,
		help_text="Escreva observações importantes."
	)

	template = "enap_designsystem/pages/template_homeII.html"
	miniview_template = "coderedcms/pages/article_page.mini.html"
	search_template = "coderedcms/pages/article_page.search.html"

	page_title = models.CharField(
		max_length=255, 
		default="Título Padrão", 
		verbose_name="Título da Página"
	)


	body = StreamField(
		DYNAMIC_CARD_STREAMBLOCKS,
		null=True,
		blank=True,
		use_json_field=True,
	)


	teste_courses = StreamField(
		[("courses_carousel", CoursesCarouselBlock())], 
		null=True,
		blank=True,
		use_json_field=True,
	)

	suap_courses = StreamField(
		[("suap_courses", SuapCourseBlock())],
		null=True,
		blank=True,
		use_json_field=True,
	)

	noticias = StreamField(
		[("eventos_carousel", EventsCarouselBlock())], 
		null=True,
		blank=True,
		use_json_field=True,
	)

	teste_noticia = StreamField(
		[("noticias_carousel", NewsCarouselBlock())], 
		null=True,
		blank=True,
		use_json_field=True,
	)

	teste_preview = StreamField(
		[("page_preview_teste", HolofoteCarouselBlock())],
		null=True,
		blank=True,
		use_json_field=True,
	)

	dropdown_content = StreamField(
		[("dropdown", DropdownBlock())],
		null=True,
		blank=True,
		use_json_field=True,
	)
	
	paragrafo = RichTextField(
		blank=True, 
		help_text="Adicione o texto do parágrafo aqui.", 
		verbose_name="Parágrafo sessao dinamica"
	)
	
	video_background = models.FileField(
		upload_to='media/videos', 
		null=True, 
		blank=True, 
		verbose_name="Vídeo de Fundo"
	)

	background_image = StreamField(
		[
			("image", ImageBlock()),
		],
		null=True,
		blank=True,
		use_json_field=True,
	)

	linkcta = RichTextField(blank=True)
	button_link = models.URLField(
		"Link do Botão",
		blank=True,
		help_text="URL do link do botão"
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

	# Painéis no admin do Wagtail
	content_panels = CoderedWebPage.content_panels + [
		FieldPanel('navbar'),
		FieldPanel('video_background'),
		MultiFieldPanel(
			[
				FieldPanel('page_title'),
				FieldPanel('paragrafo'),
				FieldPanel('background_image'),
				FieldPanel('button_link'),
			],
			heading="Título e Parágrafo CTA Dinamico"
		),
		FieldPanel('teste_courses'),
		FieldPanel('suap_courses'),
		FieldPanel('noticias'),
		FieldPanel('dropdown_content'),
		FieldPanel('teste_preview'),
		FieldPanel('teste_noticia'),  
		FieldPanel('footer'),
	]

	search_fields = []

	class Meta:
		verbose_name = "Enap Home v2"
		verbose_name_plural = "Home V2"





@register_snippet
class EnapFooterSnippet(ClusterableModel):
	"""
	Custom footer for bottom of pages on the site.
	"""

	class Meta:
		verbose_name = "ENAP Footer"
		verbose_name_plural = "ENAP Footers"

	image = StreamField([
		("logo", ImageChooserBlock()),
	], blank=True, use_json_field=True)

	name = models.CharField(
		max_length=255,
		blank=False,
		null=False,
		help_text="Título do snippet"
	)

	links = StreamField([
		("enap_footergrid", EnapFooterGridBlock()),
	], blank=True, use_json_field=True)

	social = StreamField([
		("enap_footersocialgrid", EnapFooterSocialGridBlock()),
	], blank=True, use_json_field=True)

	panels = [
		FieldPanel("name"),
		FieldPanel("image"),
		FieldPanel("social"),
		FieldPanel("links"),
	]

	def __str__(self) -> str:
		return self.name
	

@register_snippet
class EnapAccordionSnippet(ClusterableModel):
	"""
	Snippet de Accordion estilo FAQ.
	"""
	class Meta:
		verbose_name = "ENAP Accordion"
		verbose_name_plural = "ENAP Accordions"

	name = models.CharField(
		max_length=255,
		blank=False,
		null=False,
		help_text="Nome do snippet para facilitar a identificação no admin."
	)

	panels_content = StreamField([
		("accordion_item", EnapAccordionPanelBlock()),
	], blank=True, use_json_field=True)

	panels = [
		FieldPanel("name"),
		FieldPanel("panels_content"),
	]

	def __str__(self):
		return self.name
	





class EnapNavbarChooserPageBlock(blocks.StructBlock):
    """
    ChooserPage dropdown que mostra páginas mãe à esquerda e filhas à direita.
    """
    
    title = blocks.CharBlock(
        max_length=255,
        required=True,
        label="Título do Menu",
        default="Menu Principal",
        help_text="Título que aparece no botão do menu"
    )
    
    parent_pages = blocks.ListBlock(
        blocks.StructBlock([
            ('page', PageChooserBlock(
                required=True,
                help_text="Página mãe (as páginas filhas serão mostradas automaticamente)"
            )),
            ('custom_title', blocks.CharBlock(
                required=False,
                max_length=100,
                help_text="Título customizado (opcional, senão usa o título da página)"
            )),
            ('icon', blocks.CharBlock(
                required=False,
                max_length=50,
                help_text="Ícone Material Icons (opcional) - ex: school, event, book, business"
            )),
        ]),
        required=True,
        min_num=1,
        max_num=8,
        label="Páginas Mãe",
        help_text="Adicione as páginas mãe que aparecerão no menu lateral"
    )
    
    max_child_pages = blocks.IntegerBlock(
        required=False,
        default=10,
        min_value=1,
        max_value=20,
        help_text="Número máximo de páginas filhas a mostrar"
    )
    
    show_child_descriptions = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Mostrar descrições das páginas filhas (se disponível)"
    )
    
    class Meta:
        icon = "folder-open-inverse"
        label = "ChooserPage"

    
@register_snippet
class EnapNavbarSnippet(ClusterableModel):
	"""
	Snippet para a Navbar do ENAP, permitindo logo, busca, idioma e botão de contraste.
	"""

	name = models.CharField(
		max_length=255,
		blank=False,
		null=False,
		help_text="Nome do snippet para facilitar a identificação no admin."
	)

	logo = StreamField([
		("image", ImageChooserBlock())
	], blank=True, use_json_field=True, verbose_name="Logo da Navbar")

	links = StreamField([
		("navbar_link", EnapNavbarLinkBlock()),
		("chooserpage", EnapNavbarChooserPageBlock()),
	], blank=True, use_json_field=True)

	logo_link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Página para onde a logo deve direcionar (deixe em branco para usar a página inicial)",
        verbose_name="Link da Logo"
    )

	panels = [
		FieldPanel("name"),
		PageChooserPanel("logo_link_page"),
		FieldPanel("logo"),
		FieldPanel("links"),
	]

	class Meta:
		verbose_name = " ENAP Navbar"
		verbose_name_plural = "ENAP Navbars"

	def __str__(self):
		return self.name


ALERT_TYPES = [
	('success', 'Sucesso'),
	('error', 'Erro'),
	('warning', 'Aviso'),
	('info', 'Informação'),
]
@register_snippet
class Alert(models.Model):
	
	title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Título")
	message = RichTextField(verbose_name="Mensagem") 
	alert_type = models.CharField(
		max_length=20, 
		choices=ALERT_TYPES, 
		default='success', 
		verbose_name="Tipo de Alerta"
	)
	button_text = models.CharField(
		max_length=50, 
		blank=True, 
		default="Fechar", 
		verbose_name="Texto do Botão"
	)
	show_automatically = models.BooleanField(
		default=True, 
		verbose_name="Mostrar automaticamente"
	)
	
	panels = [
		FieldPanel('title'),
		FieldPanel('message'),
		FieldPanel('alert_type'),
		FieldPanel('button_text'),
		FieldPanel('show_automatically'),
	]
	
	def __str__(self):
		return self.title or f"Alerta ({self.get_alert_type_display()})"
	
	class Meta:
		verbose_name = "ENAP Alerta"
		verbose_name_plural = "ENAP Alertas"




# Os ícones, cores de fundo e cores dos ícones serão aplicados automaticamente
# com base no tipo de alerta selecionado

class AlertBlock(StructBlock):
	title = CharBlock(required=False, help_text="Título do alerta (opcional)")
	message = RichTextBlock(required=True, help_text="Mensagem do alerta")
	alert_type = ChoiceBlock(choices=ALERT_TYPES, default='success', help_text="Tipo do alerta")
	button_text = CharBlock(required=False, default="Fechar", help_text="Texto do botão (deixe em branco para não mostrar botão)")
	
	class Meta:
		template = "enap_designsystem/blocks/alerts.html"
		icon = 'warning'
		label = 'ENAP Alerta'




class WizardChooserBlock(ChooserBlock):
	@property
	def target_model(self):
		from enap_designsystem.models import Wizard  # Importação local para evitar referência circular
		return Wizard

	def get_form_state(self, value):
		return {
			'id': value.id if value else None,
			'title': str(value) if value else '',
		}

@register_snippet
class Wizard(ClusterableModel):
	"""
	Snippet para criar wizards reutilizáveis
	"""
	title = models.CharField(max_length=255, verbose_name="Título")
	
	panels = [
		FieldPanel('title'),
		InlinePanel('steps', label="Etapas do Wizard"),
	]
	
	def __str__(self):
		return self.title
	
	class Meta:
		verbose_name = "ENAP Wizard"
		verbose_name_plural = "ENAP Wizard"


class WizardStep(Orderable):
	"""
	Uma etapa dentro de um wizard
	"""
	wizard = ParentalKey(Wizard, on_delete=models.CASCADE, related_name='steps')
	title = models.CharField(max_length=255, verbose_name="Título da Etapa")
	content = models.TextField(blank=True, verbose_name="Conteúdo")
	
	panels = [
		FieldPanel('title'),
		FieldPanel('content'),
	]
	
	def __str__(self):
		return f"{self.title} - Etapa {self.sort_order + 1}"


class WizardBlock(StructBlock):
	"""
	Bloco para adicionar um wizard a uma página
	"""
	wizard = WizardChooserBlock(required=True)
	current_step = ChoiceBlock(
		choices=[(1, 'Etapa 1'), (2, 'Etapa 2'), (3, 'Etapa 3'), (4, 'Etapa 4'), (5, 'Etapa 5')],
		default=1,
		required=True,
		help_text="Qual etapa deve ser exibida como ativa",
	)
	
	def get_context(self, value, parent_context=None):
		context = super().get_context(value, parent_context)
		wizard = value['wizard']
		
		# Adiciona as etapas do wizard ao contexto
		steps = wizard.steps.all().order_by('sort_order')
		
		# Adapta o seletor de etapa atual para corresponder ao número real de etapas
		current_step = min(int(value['current_step']), steps.count())
		
		context.update({
			'wizard': wizard,
			'steps': steps,
			'current_step': current_step,
		})
		return context
	
	class Meta:
		template = 'enap_designsystem/blocks/wizard.html'
		icon = 'list-ol'
		label = 'ENAP Wizard'




@register_snippet
class Modal(models.Model):
	"""
	Snippet para criar modais reutilizáveis
	"""
	title = models.CharField(max_length=255, verbose_name="Título do Modal")
	content = RichTextField(verbose_name="Conteúdo do Modal")
	button_text = models.CharField(max_length=100, verbose_name="Texto do Botão", default="Abrir Modal")
	button_action_text = models.CharField(max_length=100, verbose_name="Texto do Botão de Ação", blank=True, help_text="Deixe em branco para não exibir um botão de ação")
	
	panels = [
		FieldPanel('title'),
		FieldPanel('content'),
		FieldPanel('button_text'),
		FieldPanel('button_action_text'),
	]
	
	def __str__(self):
		return self.title
	
	class Meta:
		verbose_name = "ENAP Modal"
		verbose_name_plural = "ENAP Modais"




@register_snippet
class ModalBlock(models.Model):
	"""
	Modal configurável que pode ser reutilizado em várias páginas.
	"""
	title = models.CharField(verbose_name="Título", max_length=255)
	content = RichTextField(verbose_name="Conteúdo", blank=True)
	button_text = models.CharField(verbose_name="Texto do botão", max_length=100, default="Abrir Modal")
	button_action_text = models.CharField(verbose_name="Texto do botão de ação", max_length=100, blank=True)
	
	# Novas opções
	SIZE_CHOICES = [
		('small', 'Pequeno'),
		('medium', 'Médio'),
		('large', 'Grande'),
	]
	size = models.CharField(verbose_name="Tamanho do Modal", max_length=10, choices=SIZE_CHOICES, default='medium')
	
	TYPE_CHOICES = [
		('message', 'Mensagem'),
		('form', 'Formulário'),
	]
	modal_type = models.CharField(verbose_name="Tipo de Modal", max_length=10, choices=TYPE_CHOICES, default='message')
	
	# Campos para formulário
	form_placeholder = models.CharField(verbose_name="Placeholder do formulário", max_length=255, blank=True)
	form_message = models.TextField(verbose_name="Mensagem do formulário", blank=True)
	
	panels = [
		FieldPanel('title'),
		FieldPanel('content'),
		FieldPanel('button_text'),
		FieldPanel('button_action_text'),
		FieldPanel('size'),
		FieldPanel('modal_type'),
		FieldPanel('form_placeholder'),
		FieldPanel('form_message'),
	]
	
	def __str__(self):
		return self.title
	
	class Meta:
		verbose_name = "Modal"
		verbose_name_plural = "Modais"


class ModalBlockStruct(blocks.StructBlock):
	modalenap = blocks.PageChooserBlock(
		required=True,
		label="Escolha um Modal",
	)

	class Meta:
		template = "enap_designsysten/blocks/modal_block.html"


@register_snippet
class Tab(ClusterableModel):
	"""
	Snippet para criar componentes de abas reutilizáveis com diferentes estilos
	"""
	title = models.CharField(max_length=255, verbose_name="Título do Componente")
	
	style = models.CharField(
		max_length=20,
		choices=[
			('style1', 'Estilo 1 (Com borda e linha inferior)'),
			('style2', 'Estilo 2 (Fundo verde quando ativo)'),
			('style3', 'Estilo 3 (Fundo verde quando ativo, sem bordas)'),
		],
		default='style1',
		verbose_name="Estilo Visual"
	)
	
	panels = [
		FieldPanel('title'),
		FieldPanel('style'),
		InlinePanel('tab_items', label="Abas"),
	]
	
	def __str__(self):
		return self.title
	
	class Meta:
		verbose_name = "Enap Tab"
		verbose_name_plural = "Enap Tabs"


class TabItem(Orderable):
	"""
	Um item de aba dentro do componente Tab
	"""
	tab = ParentalKey(Tab, on_delete=models.CASCADE, related_name='tab_items')
	title = models.CharField(max_length=255, verbose_name="Título da Aba")
	content = RichTextField(verbose_name="Conteúdo da Aba")
	
	panels = [
		FieldPanel('title'),
		FieldPanel('content'),
	]
	
	def __str__(self):
		return f"{self.tab.title} - {self.title}"
	

class TabBlock(StructBlock):
	tab = SnippetChooserBlock(
		'enap_designsystem.Tab', 
		required=True, 
		help_text="Selecione um componente de abas"
	)
	
	class Meta:
		template = "enap_designsystem/blocks/draft_tab.html"
		icon = 'table'
		label = 'ENAP Abas'

@register_snippet
class FormularioContato(models.Model):
	titulo = models.CharField(max_length=100, default="Formulário de Contato")
	estilo_campo = models.CharField(
		max_length=20,
		choices=[
			('rounded', 'Arredondado (40px)'),
			('square', 'Quadrado (8px)'),
		],
		default='rounded',
		help_text="Escolha o estilo de borda dos campos do formulário"
	)
	
	panels = [
		FieldPanel('titulo'),
		FieldPanel('estilo_campo'),
	]
	
	def __str__(self):
		return self.titulo
	
	class Meta:
		verbose_name = "ENAP Formulário de Contato"
		verbose_name_plural = "ENAP Formulários de Contato"




class DropdownLinkBlock(StructBlock):
	link_text = CharBlock(label="Texto do link", required=True)
	link_url = URLBlock(label="URL do link", required=True)
	
	class Meta:
		template = "enap_designsystem/blocks/dropdown.html"
		icon = "link"
		label = "Link do Dropdown"

# Bloco principal do dropdown
class DropdownBlock(StructBlock):
	label = CharBlock(label="Label", required=True, default="Label")
	button_text = CharBlock(label="Texto do botão", required=True, default="Select")
	dropdown_links = ListBlock(DropdownLinkBlock())
	
	class Meta:
		template = "enap_designsystem/blocks/dropdown.html"
		icon = "arrow-down"
		label = "Dropdown"




class MbaEspecializacao(Page):
	"""Página de MBA e Especialização com componente CourseIntroTopics."""

	template = 'enap_designsystem/pages/mba_especializacao.html'

	subpage_types = ['TemplateEspecializacao', 'ENAPComponentes']

	navbar = models.ForeignKey(
		"EnapNavbarSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	course_intro_topics = StreamField([
		('course_intro_topics', CourseIntroTopicsBlock()),
		# Outros blocos podem ser adicionados aqui se necessário
	], use_json_field=True, blank=True)

	why_choose = StreamField([
		# Outros blocos existentes
		('why_choose', WhyChooseEnaptBlock()),
	], blank=True, null=True)

	testimonials_carousel = StreamField([
		# Outros blocos existentes
		('testimonials_carousel', TestimonialsCarouselBlock()),
	], blank=True, null=True)

	preview_courses = StreamField(
		[("preview_courses", PreviewCoursesBlock())],
		null=True,
		blank=True,
		use_json_field=True,
	)

	content = StreamField(
		[
			("banner", EnapBannerBlock()), 
			("BannerConcurso", BannerConcurso()),
		],
		null=True,
		blank=True,
		use_json_field=True,
	)

	teste_noticia = StreamField(
		[("noticias_carousel", NewsCarouselBlock())], 
		null=True,
		blank=True,
		use_json_field=True,
	)

	cards = StreamField(
		CARD_CARDS_STREAMBLOCKS,
		null=True,
		blank=True,
		use_json_field=True,
	)


	footer = models.ForeignKey(
		"EnapFooterSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	@classmethod  
	def can_create_at(cls, parent):  
		import inspect  
		for frame_record in inspect.stack():  
			if 'request' in frame_record.frame.f_locals:  
				user = frame_record.frame.f_locals['request'].user  
				
				if user.is_superuser: 
					return super().can_create_at(parent)  
				
				from .models import GroupPagePermission  
				has_permission = GroupPagePermission.objects.filter(  
					group__in=user.groups.all(), 
					page_type='MBAPage'  
				).exists()  
				
				return has_permission and super().can_create_at(parent)  
		
		return super().can_create_at(parent)  

	def save(self, *args, **kwargs):
        # Só adiciona os blocos padrão se for uma nova página
		if not self.pk:
            # Adiciona course_intro_topics se estiver vazio
			if not self.course_intro_topics:
				self.course_intro_topics = [
					{'type': 'course_intro_topics', 'value': {}}
				]

			# Adiciona why_choose se estiver vazio  
			if not self.why_choose:
				self.why_choose = [
					{'type': 'why_choose', 'value': {}}
				]

			# Adiciona testimonials_carousel se estiver vazio
			if not self.testimonials_carousel:
				self.testimonials_carousel = [
					{'type': 'testimonials_carousel', 'value': {}}
				]

			# Adiciona preview_courses se estiver vazio
			if not self.preview_courses:
				self.preview_courses = [
					{'type': 'preview_courses', 'value': {}}
				]

			# Adiciona banner no content se estiver vazio
			if not self.content:
				self.content = [
					{'type': 'banner', 'value': {}}
				]

			# Adiciona noticias_carousel se estiver vazio
			if not self.teste_noticia:
				self.teste_noticia = [
					{'type': 'noticias_carousel', 'value': {}}
				]
        
		super().save(*args, **kwargs)

	
	content_panels = Page.content_panels + [
		FieldPanel('navbar'),
		FieldPanel('content'),
		FieldPanel('course_intro_topics'),
		FieldPanel('why_choose'),
		FieldPanel('testimonials_carousel'),
		FieldPanel('preview_courses'),
		FieldPanel('teste_noticia'),
		FieldPanel('cards'),
		FieldPanel("footer"),
	]
	
	@property
	def url_filter(self):
		if hasattr(self, 'full_url') and self.full_url:
			return self.full_url
		return self.get_url_parts()[2] if self.get_url_parts() else ""
	
	@property
	def titulo_filter(self):
		if self.content:
			for block in self.content:
				if block.block_type == "banner":
					return strip_tags(str(block.value.get("title", ""))).strip()
		return ""

	@property
	def descricao_filter(self):
		if self.content:
			for block in self.content:
				if block.block_type == "banner":
					desc = block.value.get("description", "")
					if hasattr(desc, "source"):
						return strip_tags(desc.source).strip()
					return strip_tags(str(desc)).strip()
		return ""

	@property
	def data_atualizacao_filter(self):
		return self.last_published_at or self.latest_revision_created_at

	@property
	def categoria(self):
		return "Serviços"
	
	@property
	def imagem_filter(self):
		try:
			for bloco in self.content:
				if bloco.block_type == "banner":
					background = bloco.value.get("background_image")
					if background:
						return background.file.url
		except Exception:
			pass
		return ""
	
	@property
	def texto_unificado(self):
		def extract_text_from_block(block_value):
			result = []

			if isinstance(block_value, list):
				for subblock in block_value:
					result.extend(extract_text_from_block(subblock))
			elif hasattr(block_value, "get"):  # StructValue
				for key, val in block_value.items():
					result.extend(extract_text_from_block(val))
			elif isinstance(block_value, str):
				cleaned = strip_tags(block_value).strip()
				if cleaned and cleaned.lower() not in {
					"default", "tipo terciário", "tipo secundário", "tipo bg image",
					"bg-gray", "bg-blue", "bg-white", "fundo cinza", "fundo branco"
				}:
					result.append(cleaned)
			elif hasattr(block_value, "source"):  # RichText
				cleaned = strip_tags(block_value.source).strip()
				if cleaned:
					result.append(cleaned)

			return result

		streamfields = [
			self.content,
			self.course_intro_topics,
			self.why_choose,
			self.testimonials_carousel,
			self.preview_courses,
			self.teste_noticia,
		]

		textos = []
		for sf in streamfields:
			if sf:
				for block in sf:
					textos.extend(extract_text_from_block(block.value))

		texto_final = " ".join([t for t in textos if t])
		return re.sub(r"\s+", " ", texto_final).strip()

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
		verbose_name = "MBA e Especialização"
		verbose_name_plural = "MBAs e Especializações"



class TemplateEspecializacao(Page):
	"""Página de MBA e Especialização com componente CourseIntroTopics."""

	template = 'enap_designsystem/pages/template_mba.html'
	parent_page_types = ['MbaEspecializacao']

	STATUS_INSCRICAO = [
		('abertas', 'Inscrições Abertas'),
		('encerradas', 'Inscrições Encerradas'),
		('em_andamento', 'Curso em Andamento'),
		('finalizado', 'Curso Finalizado'),
	]

	status_inscricao = models.CharField(
		max_length=20,
		choices=STATUS_INSCRICAO,
		default='abertas',
		verbose_name='Status das Inscrições',
		help_text='Define o status atual do curso/inscrições'
	)

	navbar = models.ForeignKey(
		"EnapNavbarSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	feature_course = StreamField([
		('feature_course', CourseFeatureBlock()),
	], use_json_field=True, blank=True, null=True, default=[
		('feature_course', {
			'title_1': 'Características do Curso',
			'description_1': 'Conheça os principais diferenciais e características que tornam nosso programa único no mercado.',
			'title_2': 'Metodologia Inovadora',
			'description_2': 'Utilizamos as mais modernas práticas pedagógicas para garantir o melhor aprendizado.',
			'image': None
		})
	])

	content = StreamField(
		[
			("banner", EnapBannerBlock()), 
		],
		null=True,
		blank=True,
		use_json_field=True,
		default=[
			('banner', {
				'background_image': None,
				'title': 'MBA e Especialização',
				'description': '<p>Desenvolva suas competências e alcance novos patamares na sua carreira profissional com nossos programas de excelência.</p>'
			})
		]
	)

	feature_estrutura = StreamField([
		('feature_estrutura', CourseModulesBlock()),
	], use_json_field=True, blank=True, null=True, default=[
		('feature_estrutura', {
			'title': 'Estrutura do Curso',
			'modules': [
				{
					'module_title': '1º Módulo - Fundamentos',
					'module_description': 'Módulo introdutório com os conceitos fundamentais da área',
					'module_items': [
						'Conceitos básicos e terminologias',
						'Fundamentos teóricos essenciais',
						'Práticas introdutórias',
						'Estudos de caso iniciais'
					]
				},
				{
					'module_title': '2º Módulo - Desenvolvimento',
					'module_description': 'Aprofundamento nos conhecimentos e técnicas avançadas',
					'module_items': [
						'Técnicas avançadas',
						'Metodologias práticas',
						'Projetos aplicados',
						'Análise de casos reais'
					]
				},
				{
					'module_title': '3º Módulo - Especialização',
					'module_description': 'Especialização e aplicação prática dos conhecimentos',
					'module_items': [
						'Tópicos especializados',
						'Projeto final',
						'Apresentação e defesa',
						'Networking e mercado'
					]
				}
			]
		})
	])

	feature_processo_seletivo = StreamField([
		('feature_processo_seletivo', ProcessoSeletivoBlock()),
	], use_json_field=True, blank=True, null=True, default=[
		('feature_processo_seletivo', {
			'title': 'Processo Seletivo',
			'description': 'Conheça as etapas do nosso processo seletivo e saiba como participar',
			'module1_title': 'Inscrição',
			'module1_description': 'Realize sua inscrição através do nosso portal online. Preencha todos os dados solicitados e anexe a documentação necessária.',
			'module2_title': 'Análise Curricular',
			'module2_description': 'Nossa equipe realizará uma análise criteriosa do seu perfil profissional e acadêmico para verificar a adequação ao programa.',
			'module3_title': 'Resultado Final',
			'module3_description': 'Os candidatos aprovados serão comunicados via e-mail e receberão todas as orientações para início do curso.'
		})
	])

	team_carousel = StreamField([
		('team_carousel', TeamCarouselBlock()),
	], use_json_field=True, blank=True, null=True, default=[
		('team_carousel', {
			'title': 'Nossa Equipe',
			'description': 'Conheça os profissionais especializados que compõem nosso corpo docente',
			'view_all_text': 'Ver todos os professores',
			'members': [
				{
					'name': 'Prof. Dr. Nome Sobrenome',
					'role': '<p>Coordenador Acadêmico</p>',
					'image': None
				},
				{
					'name': 'Prof. Mestre Nome Sobrenome',
					'role': '<p>Docente Especialista</p>',
					'image': None
				},
				{
					'name': 'Prof. Dr. Nome Sobrenome',
					'role': '<p>Professor Convidado</p>',
					'image': None
				},
				{
					'name': 'Prof. Mestre Nome Sobrenome',
					'role': '<p>Consultor Especializado</p>',
					'image': None
				}
			]
		})
	])

	cards = StreamField(
		CARD_CARDS_STREAMBLOCKS,
		null=True,
		blank=True,
		use_json_field=True,
	)

	footer = models.ForeignKey(
		"EnapFooterSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)
	
	content_panels = Page.content_panels + [
		FieldPanel('navbar'),
		FieldPanel('status_inscricao'),
		FieldPanel('content'),
		FieldPanel('feature_course'),
		FieldPanel('feature_estrutura'),
		FieldPanel('feature_processo_seletivo'),
		FieldPanel('team_carousel'),
		FieldPanel('cards'),
		FieldPanel("footer"),
	]
	
	@property
	def url_filter(self):
		if hasattr(self, 'full_url') and self.full_url:
			return self.full_url
		return self.get_url_parts()[2] if self.get_url_parts() else ""

	@property
	def titulo_filter(self):
		if self.content:
			for block in self.content:
				if block.block_type == "banner":
					return strip_tags(str(block.value.get("title", ""))).strip()
		return ""

	@property
	def descricao_filter(self):
		if self.content:
			for block in self.content:
				if block.block_type == "banner":
					desc = block.value.get("description", "")
					if hasattr(desc, "source"):
						return strip_tags(desc.source).strip()
					return strip_tags(str(desc)).strip()
		return ""

	@property
	def categoria(self):
		return "Serviços"

	@property
	def data_atualizacao_filter(self):
		return self.last_published_at or self.latest_revision_created_at or self.first_published_at

	@property
	def imagem_filter(self):
		try:
			for bloco in self.content:
				if bloco.block_type == "banner":
					background = bloco.value.get("background_image")
					if background:
						return background.file.url
		except Exception:
			pass
		return ""
	
	@property
	def texto_unificado(self):
		def extract_text_from_block(block_value):
			result = []

			if isinstance(block_value, list):
				for subblock in block_value:
					result.extend(extract_text_from_block(subblock))
			elif hasattr(block_value, "get"):  # StructValue
				for key, val in block_value.items():
					result.extend(extract_text_from_block(val))
			elif isinstance(block_value, str):
				cleaned = strip_tags(block_value).strip()
				if cleaned and cleaned.lower() not in {
					"default", "tipo terciário", "tipo secundário", "tipo bg image",
					"bg-gray", "bg-blue", "bg-white", "fundo cinza", "fundo branco"
				}:
					result.append(cleaned)
			elif hasattr(block_value, "source"):  # RichText
				cleaned = strip_tags(block_value.source).strip()
				if cleaned:
					result.append(cleaned)

			return result

		streamfields = [
			self.content,
			self.feature_course,
			self.feature_estrutura,
			self.feature_processo_seletivo,
			self.team_carousel,
		]

		textos = []
		for sf in streamfields:
			if sf:
				for block in sf:
					textos.extend(extract_text_from_block(block.value))

		texto_final = " ".join([t for t in textos if t])
		return re.sub(r"\s+", " ", texto_final).strip()

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
		verbose_name = "MBA e Especialização Especifico"
		verbose_name_plural = "MBAs e Especializações"





class OnlyCards(Page):
	template = 'enap_designsystem/pages/template_only-cards.html'

	featured_card = StreamField([
		("enap_section", EnapSectionBlock([
			("enap_cardgrid", EnapCardGridBlock([
				("enap_card", EnapCardBlock()),
			])),
		])),
	], blank=True, use_json_field=True)

	banner = StreamField(
		[
			("banner", EnapBannerBlock()), 
		],
		null=True,
		blank=True,
		use_json_field=True,
	)

	course_intro_topics = StreamField([
		('course_intro_topics', CourseIntroTopicsBlock()),
		# Outros blocos podem ser adicionados aqui se necessário
	], use_json_field=True, blank=True)

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
		FieldPanel('navbar'),
		FieldPanel('banner'),
		FieldPanel('course_intro_topics'),
		FieldPanel('featured_card'),
		FieldPanel("footer"),
	]

	@property
	def url_filter(self):
		if hasattr(self, 'full_url') and self.full_url:
			return self.full_url
		return self.get_url_parts()[2] if self.get_url_parts() else ""

	search_fields = Page.search_fields + [
		index.SearchField("title", boost=3),
		index.SearchField("banner"),
		index.SearchField("course_intro_topics"),
		index.SearchField("featured_card"),
		index.FilterField("url", name="url_filter"),
	]
	
	def get_searchable_content(self):
		content = super().get_searchable_content()

		def extract_text_from_block(block_value):
			result = []
			if isinstance(block_value, list):
				for subblock in block_value:
					result.extend(extract_text_from_block(subblock))
			elif hasattr(block_value, "get"):
				for key, val in block_value.items():
					result.extend(extract_text_from_block(val))
			elif isinstance(block_value, str):
				result.append(block_value)
			elif hasattr(block_value, "source"):
				result.append(block_value.source)
			return result

		streamfields = [
			self.banner,
			self.course_intro_topics,
			self.featured_card,
		]

		for sf in streamfields:
			if sf:
				for block in sf:
					content.extend(extract_text_from_block(block.value))

		return content


	class Meta:
		verbose_name = "ENAP apenas com cards(usar paar informativos)"
		verbose_name_plural = "ENAP Pagina so com cards"






class AreaAluno(Page):
	"""Página personalizada para exibir dados do aluno logado."""

	template = "enap_designsystem/pages/area_aluno.html"

	body = StreamField(
		LAYOUT_STREAMBLOCKS,
		null=True,
		blank=True,
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
		FieldPanel("body"),
	]

	# Serve apenas com usuário logado via sessão
	def serve(self, request):
		aluno = request.session.get("aluno_sso")
		if not aluno:
			return redirect("/")

		nome_completo = aluno.get("nome", "")
		primeiro_nome = nome_completo.split(" ")[0] if nome_completo else "Aluno"
		access_token = get_valid_access_token(request.session)
		verify_ssl = not settings.DEBUG

		headers = {
			"Authorization": f"Bearer {access_token}"
		}

		def fetch(endpoint, expect_dict=False):
			try:
				url = f"{settings.BFF_API_URL}{endpoint}"
				resp = requests.get(url, headers=headers, timeout=10, verify=verify_ssl)
				resp.raise_for_status()
				data = resp.json()

				if expect_dict:
					if isinstance(data, list):
						return data[0] if data else {}
					elif isinstance(data, dict):
						return data
					else:
						return {}
				return data

			except Exception as e:
				print(f"Erro ao acessar API {endpoint}: {e}")
				return {} if expect_dict else []

		def parse_date(date_str):
			if not date_str:
				return None
			for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
				try:
					return datetime.strptime(date_str, fmt)
				except ValueError:
					continue
			return None

		aluno_resumo = fetch("/aluno/resumo", expect_dict=True)
		print("aluno_resumo", aluno_resumo)
		cursos_andamento = fetch("/aluno/cursos/andamento")
		cursos_matriculado = fetch("/aluno/cursos/matriculado")
		cursos_analise = fetch("/aluno/cursos/analise")
		cursos_eventos = fetch("/aluno/cursos/eventos")
		

		for lista in [cursos_andamento, cursos_matriculado, cursos_analise, cursos_eventos]:
			lista = lista or []
			for curso in lista:
				curso["dataInicio"] = parse_date(curso.get("dataInicio"))
				curso["dataTermino"] = parse_date(curso.get("dataTermino"))

		TITULOS_CERTIFICADOS = {
			"distancia": "Cursos a distância",
			"outros": "Outros cursos",
			"certificacoes": "Certificações",
			"eventos": "Eventos, Oficinas e Premiações",
			"migrados": "Outros",
			"voluntariado": "Voluntariado",
		}

		certificados = {
			"distancia": fetch("/aluno/certificados/cursos-distancia"),
			"outros": fetch("/aluno/certificados/cursos-outros"),
			"certificacoes": fetch("/aluno/certificados/certificacoes"),
			"eventos": fetch("/aluno/certificados/eventos-oficinas-premiacoes"),
			"migrados": fetch("/aluno/certificados/migrados"),
			"voluntariado": fetch("/aluno/certificados/voluntariado"),
		}

		for lista in certificados.values():
			lista = lista or []
			for cert in lista:
				cert["dataInicioAula"] = parse_date(cert.get("dataInicioAula"))
				cert["dataFimAula"] = parse_date(cert.get("dataFimAula"))
				cert["dataEmissao"] = parse_date(cert.get("dataEmissao"))

		context = self.get_context(request)
		context["aluno"] = aluno
		context["primeiro_nome"] = primeiro_nome
		context["aluno_resumo"] = aluno_resumo
		# Atualmente a API não retorna foto/imagem do usuário
		# de qualquer forma esse método (serve()) e o html já esperam
		context["aluno_foto"] = aluno_resumo.get("foto") or "/static/enap_designsystem/blocks/suap/default_1.png"
		context["aluno_estatisticas"] = {
			"eventos": aluno_resumo.get("eventos") if aluno_resumo else 0,
			"oficinas": aluno_resumo.get("oficinas") if aluno_resumo else 0,
			"cursos": aluno_resumo.get("cursos") if aluno_resumo else 0,
		}
		context["aluno_cursos"] = {
			"eventos": cursos_eventos,
			"andamento": cursos_andamento,
			"matriculado": cursos_matriculado,
			"analise": cursos_analise,
		}
		context["certificados_nomeados"] = [
			{
				"tipo": tipo,
				"titulo": TITULOS_CERTIFICADOS[tipo],
				"lista": certificados.get(tipo, []),
			}
			for tipo in TITULOS_CERTIFICADOS
		]

		return render(request, self.template, context)

	indexed = False

	@classmethod
	def get_indexed_instances(cls):
		return []

	def indexing_is_enabled(self):
		return False

	search_fields = []

	class Meta:
		verbose_name = "Área do Aluno"
		verbose_name_plural = "Área do Aluno"
class EnapSearchElastic(Page):
	template = "enap_designsystem/pages/page_search.html"

	navbar = models.ForeignKey("EnapNavbarSnippet", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
	footer = models.ForeignKey("EnapFooterSnippet", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

	content_panels = Page.content_panels + [
		FieldPanel('navbar'),
		FieldPanel("footer"),
	]

	# Caso entre na pagina de Busca sem nada, redireciona para um default
	def serve(self, request, *args, **kwargs):
		if "tipo" not in request.GET:
			query = request.GET.get("q", "")
			ordenacao = request.GET.get("ordenacao", "recentes")
			return redirect(f"{request.path}?q={query}&tipo=todos&ordenacao={ordenacao}")

		return super().serve(request, *args, **kwargs)
	
	######### ATENÇÃO JOOMLA-WAGTAIL
	# Imagens atuais usam o enap.gov.br do Joomla para serem exibidas!
	# Após virar a chave pelo Wagtail, as imagens deixarão de funcionar
	# Será necessário tratar com imagens que existam no wagtail
	# ou utilizar algum link no lugar de enap.gov.br
	def parse_images(self, item, tipo):
		try:
			img = item.get("imagem")

			# Caso 1: imagem é dict com image_intro
			if isinstance(img, dict) and img.get("image_intro"):
				item["imagem"] = "https://enap.gov.br/" + img["image_intro"]

			# Caso 2: imagem é string (link parcial)
			elif isinstance(img, str):
				item["imagem"] = img

			# Caso 3: nenhum dos dois — define None ou imagem default
			else:
				if tipo == "noticias":
					item["imagem"] = "/static/enap_designsystem/icons/thumb-noticias.png"
				else:
					item["imagem"] = None  # ou: "/static/enap_designsystem/icons/280-140-default.png"

		except Exception as e:
			print("Erro ao processar imagem:", e)
			item["imagem"] = None

		return item

	def parse_datas(self, item, tipo):
		"""Converte campos de data string ISO para datetime"""
		campos_data = [
			"dataPublicacao",
			"dataAtualizacao",
			"inicioInscricoes",
			"fimInscricoes",
			"inicioRealizacao",
			"fimRealizacao",
			"data_publicacao"
		]

		for campo in campos_data:
			valor = item.get(campo)
			if isinstance(valor, str) and valor:
				try:
					# Substitui Z por +00:00 para compatibilidade com datetime.fromisoformat
					item[campo] = datetime.fromisoformat(valor.replace("Z", "+00:00"))
				except Exception:
					# Se falhar a conversão, deixa como estava
					pass
		
		return self.parse_images(item, tipo)

	def normalize_noticia(self, item):
		# Dicionário com os mapeamentos dos sufixos para os nomes amigáveis
		mapping = {
   			"title": "titulo",
   			"_descricao_filter": "descricao",
			"_url_filter": "url",
			"_data_atualizacao_filter": "data_atualizacao",
			"last_published_at_filter": "data_publicacao",
			"enap_designsystem_enapnoticiaimportada__imagem_filter":"imagem"
		}

		# Inicializa o dicionário resultante
		normalized = {}

		# Itera sobre as chaves do item
		for key, value in item.items():
			for suffix, normalized_key in mapping.items():
				if key.endswith(suffix):
					normalized[normalized_key] = value
					break  # Para caso o sufixo seja encontrado

		return normalized
  
	def normalize_wagtail(self, item):
		# Dicionário com os mapeamentos dos sufixos para os nomes amigáveis
		mapping = {
			"titulo": "titulo",
			"tag": "origem",
			"link": "link",
			"descricao": "descricao",
			"title": "title",
			"_titulo_filter": "titulo_2",
			"_descricao_filter": "descricao_2",
			"_url_filter": "url",
			"last_published_at_filter": "data_atualizacao",
			"first_published_at_filter": "data_publicacao",
			"dataPublicacao": "dataPublicacao"
		}

		# Inicializa o dicionário resultante
		normalized = {}

		# Itera sobre as chaves do item
		for key, value in item.items():
			for suffix, normalized_key in mapping.items():
				if key.endswith(suffix):
					normalized[normalized_key] = value
					break  # Para caso o sufixo seja encontrado

		return normalized

	def normalize_servico(self, item):
		# Dicionário com os mapeamentos dos sufixos para os nomes amigáveis
		mapping = {
   			"title": "titulo",
   			"_descricao_filter": "descricao",
			"_url_filter": "url",
			"_data_atualizacao_filter": "data_atualizacao",
			"first_published_at_filter": "data_publicacao",
		}

		# Inicializa o dicionário resultante
		normalized = {}

		# Itera sobre as chaves do item
		for key, value in item.items():
			for suffix, normalized_key in mapping.items():
				if key.endswith(suffix):
					normalized[normalized_key] = value
					break  # Para caso o sufixo seja encontrado

		return normalized

	# ✅ NOVA FUNÇÃO ADICIONADA
	def get_sort_field(self, tipo_conteudo, ordenacao_atual):
		"""Retorna o campo de ordenação correto baseado na documentação da API"""
		ordenacao_por_endpoint = {
			"eventos": {
				"recentes": "inicioRealizacao",
				"relevantes": "_score", 
				"vistos": "dataPublicacao"
			},
			"noticias": {
				"recentes": "dataAtualizacao",
				"relevantes": "_score",
				"vistos": "dataPublicacao"
			},
			"servicos": {
				"recentes": "dataAtualizacao",
				"relevantes": "_score", 
				"vistos": "dataPublicacao"
			},
			"pesquisa_conhecimento": {
				"recentes": "dataPublicacao",
				"relevantes": "_score",
				"vistos": "dataPublicacao"
			},
			"cursos": {
				"recentes": "dataPublicacao",
				"relevantes": "_score",
				"vistos": "dataPublicacao"
			},
			"todos": {
				"recentes": "dataPublicacao",
				"relevantes": "_score",
				"vistos": "dataPublicacao"
			}
		}
		
		tipo_config = ordenacao_por_endpoint.get(tipo_conteudo, ordenacao_por_endpoint["todos"])
		return tipo_config.get(ordenacao_atual, "dataPublicacao")

	def get_context(self, request, *args, **kwargs):
		context = super().get_context(request, *args, **kwargs)
		verify_ssl = not settings.DEBUG
		query = request.GET.get("q", "").strip()
		tipo = request.GET.get("tipo", "").strip()
		ordenacao = request.GET.get("ordenacao", "recentes")
		page = int(request.GET.get("page", 1))
		if tipo == "cursos":
			rows_per_page = 12
		else:
			rows_per_page = 10
		
		context["query_navbar"] = request.GET.get("q", "")

		base_url = os.getenv("BFF_API_URL", "https://bff-portal.sandbox.enap.gov.br/v1")

		endpoints = {
			"cursos": "/busca/cursos/pesquisa",
			"noticias": "/busca/wagtail/pesquisa",
			"eventos": "/busca/eventos-oficinas/pesquisa",
			"servicos": "/busca/wagtail/pesquisa",
			"pesquisa_conhecimento": "/busca/repositorio/pesquisa",
			"todos": "/busca/pesquisa-wagtail"
		}

		endpoints_filtros = {
			"modalidade": "/busca/cursos/modalidades",
			"inscricoes": "/busca/cursos/inscricoes",
			"temas": "/busca/cursos/temas",
			"categoria": "/busca/cursos/categorias",
			"competencias": "/busca/cursos/competencias",
		}

		context["filtros"] = {}

		for chave, endpoint in endpoints_filtros.items():
			try:
				resp = requests.get(f"{base_url.rstrip('/')}{endpoint}", timeout=10, verify=verify_ssl)
				resp.raise_for_status()
				context["filtros"][chave] = resp.json()
			except Exception:
				context["filtros"][chave] = []

		# ✅ NOVA LÓGICA DE ORDENAÇÃO
		sort_by = self.get_sort_field(tipo, ordenacao)

		# Filtros principais
		filter_data = {"termo": query}
		mapa_chaves = {
			"modalidade": "modalidades",
			"inscricoes": "inscricoes",
			"temas": "temas",
			"categoria": "categorias",
			"competencias": "competencias"
		}

		for campo, chave_api in mapa_chaves.items():
			valores = request.GET.getlist(campo)
			if valores:
				filter_data[chave_api] = valores

		# Criar payload baseado no tipo
		if tipo == "noticias":
			payload = {
				"sortBy": sort_by,
				"descending": True,
				"page": page,
				"rowsPerPage": rows_per_page,
				"filter": {**filter_data, "categoria": "Notícias"}
			}
		elif tipo == "servicos":
			payload = {
				"sortBy": sort_by,
				"descending": True,
				"page": page,
				"rowsPerPage": rows_per_page,
				"filter": {**filter_data, "categoria": "Serviços"}
			}
		else:
			payload = {
				"sortBy": sort_by,
				"descending": True,
				"page": page,
				"rowsPerPage": rows_per_page,
				"filter": filter_data
			}

		context.update({
			"query": query,
			"tipo": tipo,
			"ordenacao": ordenacao
		})

		# ✅ NOVA LÓGICA DOS TOTAIS - SIMPLIFICADA
		tabs_totais = {}
		for chave, endpoint in endpoints.items():
			# Usa a nova função para cada aba
			sort_tab = self.get_sort_field(chave, ordenacao)
			
			# Filtros específicos
			if chave == "noticias":
				filter_tab = {**filter_data, "categoria": "Notícias"}
			elif chave == "servicos":
				filter_tab = {**filter_data, "categoria": "Serviços"}
			else:
				filter_tab = filter_data

			payload_tab = {
				"sortBy": sort_tab,
				"descending": True,
				"page": 1,
				"rowsPerPage": 1,
				"filter": filter_tab
			}
			
			try:
				resp = requests.post(
					f"{base_url.rstrip('/')}{endpoint}",
					json=payload_tab,
					timeout=10,
					verify=verify_ssl
				)
				resp.raise_for_status()
				tabs_totais[chave] = resp.json().get("total", 0)
			except Exception as e:
				print(f"[ERRO total aba {chave}]", e)
				tabs_totais[chave] = 0

		context["tabs_totais"] = tabs_totais

		# Se tipo atual for válido, busca resultados dessa aba
		if tipo in endpoints:
			try:
				url = f"{base_url.rstrip('/')}{endpoints[tipo]}"
				resp = requests.post(url, json=payload, timeout=10, verify=verify_ssl)
				resp.raise_for_status()
				raw_results = resp.json().get("results", [])
				total_results = resp.json().get("total", 0)
				if tipo == "noticias":
					normalized = [self.normalize_noticia(item) for item in raw_results]
					results = [self.parse_datas(item, tipo) for item in normalized]
				elif tipo == "servicos":
					normalized = [self.normalize_servico(item) for item in raw_results]
					results = [self.parse_datas(item, tipo) for item in normalized]	
				elif tipo == "todos":
					normalized = [self.normalize_wagtail(item) for item in raw_results]
					results = [self.parse_datas(item, tipo) for item in normalized]	
				else:
					results = [self.parse_datas(item, tipo) for item in raw_results]
				
    
				context["results"] = results
				context["results_count"] = total_results
				
				# Paginação
				total_pages = (total_results + rows_per_page - 1) // rows_per_page
				window_size = 5
				half_window = window_size // 2

				if total_pages <= window_size:
					pages = list(range(1, total_pages + 1))
				elif page <= half_window + 1:
					pages = list(range(1, window_size + 1))
				elif page >= total_pages - half_window:
					pages = list(range(total_pages - window_size + 1, total_pages + 1))
				else:
					pages = list(range(page - half_window, page + half_window + 1))

				# Query string base
				from urllib.parse import urlencode
				query_params = request.GET.copy()
				query_params.pop("page", None)
				base_querystring = urlencode(query_params, doseq=True)
				if base_querystring:
					base_querystring += "&"

				# Exibição do intervalo "1 - 10 de 61"
				if total_results == 0 or len(results) == 0:
					start_display = 0
					end_display = 0
				else:
					start_display = ((page - 1) * rows_per_page) + 1
					end_display = start_display + len(results) - 1

				context["pagination"] = {
					"current_page": page,
					"total_pages": total_pages,
					"has_previous": page > 1,
					"has_next": page < total_pages,
					"pages": pages,
					"base_querystring": base_querystring,
					"start_display": start_display,
					"end_display": end_display
				}

			except Exception as e:
				print("Erro na busca:", e)
				context["results"] = []
				context["results_count"] = 0

		return context

	class Meta:
		verbose_name = "ENAP Busca (ElasticSearch)"


class Template001(Page):
	"""Página de MBA e Especialização com vários componentes."""

	template = 'enap_designsystem/pages/template_001.html'

	# Navbar (snippet)
	navbar = models.ForeignKey(
		"EnapNavbarSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	# Banner fields
	
	banner_background_image = models.ForeignKey(
		get_image_model_string(),
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+',
		verbose_name=_("Banner Background Image")
	)  

	banner_title = models.CharField(
		max_length=255,
		default="Título do Banner",
		verbose_name=_("Banner Title")
	)
	banner_description = RichTextField(
		features=["bold", "italic", "ol", "ul", "hr", "link", "document-link"],
		default="<p>Descrição do banner. Edite este texto para personalizar o conteúdo.</p>",
		verbose_name=_("Banner Description")
	)
	
	# Feature Course fields
	title_1 = models.CharField(
		max_length=255,
		default="Título da feature 1",
		verbose_name=_("Primeiro título")
	)
	description_1 = models.TextField(
		default="It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.",
		verbose_name=_("Primeira descrição")
	)
	title_2 = models.CharField(
		max_length=255,
		default="Título da feature 2",
		verbose_name=_("Segundo título")
	)
	description_2 = models.TextField(
		default="It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.",
		verbose_name=_("Segunda descrição")
	)
	image = models.ForeignKey(
		get_image_model_string(),
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+',
		verbose_name=_("Imagem da feature")
	)
	
	# Estrutura como StreamField
	# Estrutura como StreamField
	feature_estrutura = StreamField([
		('feature_estrutura', CourseModulesBlock()),
	], use_json_field=True, blank=True, null=True, default=[
		('feature_estrutura', {
			'title': 'Estrutura do curso',
			'modules': [
				{
					'module_title': '1º Módulo',
					'module_description': 'Descrição do primeiro módulo',
					'module_items': [
						'Conceitos básicos',
						'Fundamentos teóricos',
						'Práticas iniciais'
					]
				},
				{
					'module_title': '2º Módulo',
					'module_description': 'Descrição do segundo módulo',
					'module_items': [
						'Desenvolvimento avançado',
						'Estudos de caso',
						'Projetos práticos'
					]
				},
				{
					'module_title': '3º Módulo',
					'module_description': 'Descrição do terceiro módulo',
					'module_items': [
						'Especialização',
						'Projeto final',
						'Apresentação'
					]
				}
			]
		})
	]) 

	# Team Carousel como StreamField
	team_carousel = StreamField([
		('team_carousel', TeamCarouselBlock()),
	], use_json_field=True, blank=True, null=True, default=[
		('team_carousel', {
			'title': 'Nossa Equipe',
			'description': 'Equipe de desenvolvedores e etc',
			'view_all_text': 'Ver todos',
			'members': [
				{'name': 'Membro 1', 'role': 'Cargo 1', 'image': None},
				{'name': 'Membro 2', 'role': 'Cargo 2', 'image': None},
				{'name': 'Membro 3', 'role': 'Cargo 3', 'image': None},
				{'name': 'Membro 4', 'role': 'Cargo 4', 'image': None},
		]
	})])
	
	# Processo Seletivo fields
	processo_title = models.CharField(
		max_length=255, 
		default="Processo seletivo",
		verbose_name=_("Título do Processo Seletivo")
	)
	processo_description = models.TextField(
		default="Sobre o processo seletivo",
		verbose_name=_("Descrição do Processo Seletivo")
	)
	
	# Módulo 1
	processo_module1_title = models.CharField(
		max_length=255,
		default="Inscrição",
		verbose_name=_("Título do 1º Módulo")
	)
	processo_module1_description = models.TextField(
		default="Lorem ipsum dolor sit amet",
		verbose_name=_("Descrição do 1º Módulo")
	)
	
	# Módulo 2
	processo_module2_title = models.CharField(
		max_length=255,
		default="Seleção",
		verbose_name=_("Título do 2º Módulo")
	)
	processo_module2_description = models.TextField(
		default="Lorem ipsum dolor sit amet",
		verbose_name=_("Descrição do 2º Módulo")
	)
	
	# Módulo 3
	processo_module3_title = models.CharField(
		max_length=255,
		default="Resultado",
		verbose_name=_("Título do 3º Módulo")
	)
	processo_module3_description = models.TextField(
		default="Lorem ipsum dolor sit amet",
		verbose_name=_("Descrição do 3º Módulo")
	)

	# Footer (snippet)
	footer = models.ForeignKey(
		"EnapFooterSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)
	
	# Painéis de conteúdo organizados em seções
	content_panels = Page.content_panels + [
		FieldPanel('navbar'),
		
		MultiFieldPanel([
			FieldPanel('banner_background_image', classname="default-image-14"),
			FieldPanel('banner_title'),
			FieldPanel('banner_description'),
		], heading="Banner"),
		
		MultiFieldPanel([
			FieldPanel('title_1'),
			FieldPanel('description_1'),
			FieldPanel('title_2'),
			FieldPanel('description_2'),
			FieldPanel('image', classname="default-image-14"),
		], heading="Feature Course"),
		
		FieldPanel('feature_estrutura'),
		
		MultiFieldPanel([
			FieldPanel('processo_title'),
			FieldPanel('processo_description'),
			FieldPanel('processo_module1_title'),
			FieldPanel('processo_module1_description'),
			FieldPanel('processo_module2_title'),
			FieldPanel('processo_module2_description'),
			FieldPanel('processo_module3_title'),
			FieldPanel('processo_module3_description'),
		], heading="Processo Seletivo"),
		
		FieldPanel('team_carousel'),
		
		FieldPanel("footer"),
	]
	
	@property
	def url_filter(self):
		if hasattr(self, 'full_url') and self.full_url:
			return self.full_url
		return self.get_url_parts()[2] if self.get_url_parts() else ""

	@property
	def titulo_filter(self):
		return strip_tags(self.banner_title or "").strip()

	@property
	def descricao_filter(self):
		return strip_tags(self.banner_description or "").strip()

	@property
	def categoria(self):
		return "Serviços"

	@property
	def data_atualizacao_filter(self):
		return self.last_published_at or self.latest_revision_created_at or self.first_published_at

	@property
	def imagem_filter(self):
		try:
			if self.image:
				return self.image.file.url
		except Exception:
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

		# Campos simples (char/text/richtext)
		simples = [
			self.banner_title,
			self.banner_description,
			self.title_1,
			self.description_1,
			self.title_2,
			self.description_2,
			self.processo_title,
			self.processo_description,
			self.processo_module1_title,
			self.processo_module1_description,
			self.processo_module2_title,
			self.processo_module2_description,
			self.processo_module3_title,
			self.processo_module3_description,
		]

		for campo in simples:
			if campo:
				textos.append(strip_tags(str(campo)).strip())

		# Campos de blocos
		for sf in [self.feature_estrutura, self.team_carousel]:
			if sf:
				for block in sf:
					textos.extend(extract_text_from_block(block.value))

		return re.sub(r"\s+", " ", " ".join([t for t in textos if t])).strip()

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
	
	def get_searchable_content(self):
		content = super().get_searchable_content()

		fields = [
			self.banner_title,
			self.banner_description,
			self.title_1,
			self.description_1,
			self.title_2,
			self.description_2,
			self.processo_title,
			self.processo_description,
			self.processo_module1_title,
			self.processo_module1_description,
			self.processo_module2_title,
			self.processo_module2_description,
			self.processo_module3_title,
			self.processo_module3_description,
		]

		for f in fields:
			if f:
				content.append(str(f))

		def extract_text_from_block(block_value):
			result = []
			if isinstance(block_value, list):
				for subblock in block_value:
					result.extend(extract_text_from_block(subblock))
			elif hasattr(block_value, "get"):
				for key, val in block_value.items():
					result.extend(extract_text_from_block(val))
			elif isinstance(block_value, str):
				result.append(block_value)
			elif hasattr(block_value, "source"):
				result.append(block_value.source)
			return result

		if self.feature_estrutura:
			for block in self.feature_estrutura:
				content.extend(extract_text_from_block(block.value))
		if self.team_carousel:
			for block in self.team_carousel:
				content.extend(extract_text_from_block(block.value))

		return content


	class Meta:
		verbose_name = "Template 001"
		verbose_name_plural = "Templates 001"






class HolofotePage(Page):
	"""Template Holofote"""

	template = "enap_designsystem/pages/template_holofote.html"

	test_content = models.TextField(
        blank=True,
        null=True,
        help_text="Teste se campos normais funcionam"
    )

	footer = models.ForeignKey(
		"EnapFooterSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	navbar = models.ForeignKey(
		"EnapNavbarSnippet",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	# Página "O que é o Holofote?"
	holofote_info_link = models.URLField(
    max_length=200,
    blank=True,
    help_text="Link para informações sobre o Holofote",
    verbose_name="Link Info Holofote"
	)

	holofote_links = StreamField([
        ('holofote_link', StructBlock([
            ('title', CharBlock(
                max_length=50,
                help_text="Texto que aparecerá no link (ex: Servir, Clima, etc.)"
            )),
            ('page', PageChooserBlock(
                help_text="Página para onde o link deve direcionar"
            )),
            ('anchor', CharBlock(
                max_length=50,
                required=False,
                help_text="Âncora opcional (ex: #cuidar) - será adicionada após a URL da página"
            )),
        ], icon='link', label='Link do Holofote')),
    	], blank=True, use_json_field=True, verbose_name="Links de Navegação do Holofote")

    

	body = StreamField([
		('citizen_server', CitizenServerBlock()),
		('topic_links', TopicLinksBlock()),
		('feature_list_text', FeatureWithLinksBlock()), 
		('QuoteModern', QuoteBlockModern()),
		('service_cards', ServiceCardsBlock()),
		('carousel_green', CarouselGreen()),
		('section_block', EnapSectionBlock()),
		('feature_list', FeatureListBlock()),
		('service_cards', ServiceCardsBlock()),
		('banner_image_cta', Banner_Image_cta()),
		('citizen_server', CitizenServerBlock()),
		("carrossel_cursos", CarrosselCursosBlock()),
		("enap_section", EnapSectionBlock([
			("enap_cardgrid", EnapCardGridBlock([
				("enap_card", EnapCardBlock()),
				('card_curso', CardCursoBlock()),
				('texto_imagem', TextoImagemBlock()),
			])),
		])),
		# Outros blocos padrão do Wagtail
		('heading', blocks.CharBlock(form_classname="title", label=_("Título"))),
		('paragraph', blocks.RichTextBlock(label=_("Parágrafo"))),
		('image', ImageChooserBlock(label=_("Imagem"))),
		('html', blocks.RawHTMLBlock(label=_("HTML")))
	], null=True, blank=True, verbose_name=_("Conteúdo da Página"))

	

	content_panels = Page.content_panels + [
		FieldPanel('test_content'), 
		PageChooserPanel('holofote_info_link'),
        FieldPanel('holofote_links'),
		FieldPanel('body'),
		FieldPanel("footer"),
		FieldPanel("navbar"),
	]

	@property
	def titulo_filter(self):
		for block in self.body:
			if hasattr(block.value, "get") and "title" in block.value:
				titulo = block.value.get("title")
				if titulo:
					return strip_tags(str(titulo)).strip()
		return ""

	@property
	def descricao_filter(self):
		for block in self.body:
			if hasattr(block.value, "get") and "description" in block.value:
				desc = block.value.get("description")
				if hasattr(desc, "source"):
					return strip_tags(desc.source).strip()
				return strip_tags(str(desc)).strip()
		return ""

	@property
	def categoria(self):
		return "Outros"

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
			for bloco in self.body:
				if bloco.block_type == "banner_image_cta":
					hero_image = bloco.value.get("hero_image")
					if hero_image:
						return hero_image.file.url
		except Exception:
			pass

		return ""
	
	@property
	def texto_unificado(self):
		def extract_text_from_block(block_value):
			result = []

			if isinstance(block_value, list):
				for subblock in block_value:
					result.extend(extract_text_from_block(subblock))
			elif hasattr(block_value, "get"):  # StructValue
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

		texto_final = " ".join([t for t in textos if t])
		return re.sub(r"\s+", " ", texto_final).strip()
		
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
		verbose_name = _("Template Holofote")




# Funções para defaults dos StreamFields
def get_default_banner_evento():
    return [{'type': 'enap_herobanner', 'value': {}}]

def get_default_informacoes_evento():
    return [{'type': 'evento', 'value': {}}]

def get_default_por_que_participar():
    return [{'type': 'why_choose', 'value': {}}]

def get_default_palestrantes():
    return [{'type': 'team_carousel', 'value': {}}]

def get_default_inscricao_cta():
    return [{'type': 'cta_destaque', 'value': {}}]

def get_default_faq():
    return [{'type': 'accordion', 'value': {}}]


class PreEventoPage(Page):
    """Template para página de Pré-evento - divulgação e inscrições"""
    
    template = 'enap_designsystem/pages/pre_evento.html'
    
    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    # Banner principal do evento
    banner_evento = StreamField([
        ("enap_herobanner", EnapBannerBlock()),
        ("hero_animada", HeroAnimadaBlock()),
    ], use_json_field=True, blank=True, default=get_default_banner_evento)
    
    # Informações sobre o evento
    informacoes_evento = StreamField([
        ("evento", EventoBlock()),
        ("container_info", ContainerInfo()),
    ], use_json_field=True, blank=True, default=get_default_informacoes_evento)
    
    # Por que participar
    por_que_participar = StreamField([
        ("why_choose", WhyChooseEnaptBlock()),
        ("feature_list", FeatureListBlock()),
    ], use_json_field=True, blank=True, default=get_default_por_que_participar)
    
    # Palestrantes/Equipe
    palestrantes = StreamField([
        ("team_carousel", TeamCarouselBlock()),
        ("team_moderna", TeamModern()),
    ], use_json_field=True, blank=True, default=get_default_palestrantes)
    
    # CTA de inscrição
    inscricao_cta = StreamField([
        ("cta_destaque", CtaDestaqueBlock()),
        ("secao_adesao", SecaoAdesaoBlock()),
    ], use_json_field=True, blank=True, default=get_default_inscricao_cta)
    
    # FAQ sobre o evento
    faq = StreamField([
        ("accordion", EnapAccordionBlock()),
    ], use_json_field=True, blank=True, default=get_default_faq)
    
    footer = models.ForeignKey(
        "EnapFooterSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    def save(self, *args, **kwargs):
        # Método save simplificado - defaults já estão nos StreamFields
        super().save(*args, **kwargs)
    
    content_panels = Page.content_panels + [
        FieldPanel('navbar'),
        FieldPanel('banner_evento'),
        FieldPanel('informacoes_evento'),
        FieldPanel('por_que_participar'),
        FieldPanel('palestrantes'),
        FieldPanel('inscricao_cta'),
        FieldPanel('faq'),
        FieldPanel('footer'),
    ]

    class Meta:
        verbose_name = _("Enap Pré Evento")



# Funções para defaults - Durante Evento (APENAS UMA VEZ)
def get_default_banner_ao_vivo():
    return [{'type': 'enap_herobanner', 'value': {}}]

def get_default_transmissao():
    return [{'type': 'container_info', 'value': {}}]

def get_default_programacao():
    return [{'type': 'evento', 'value': {}}]

def get_default_palestrantes_atual():
    return [{'type': 'team_moderna', 'value': {}}]

def get_default_galeria_ao_vivo():
    return [{'type': 'galeria_moderna', 'value': {}}]

def get_default_interacao():
    return [{'type': 'contato', 'value': {}}]


class DuranteEventoPage(Page):
    """Template para página Durante o evento - transmissão ao vivo e interação"""
    
    template = 'enap_designsystem/pages/durante_evento.html'

    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    # Banner com status ao vivo
    banner_ao_vivo = StreamField([
        ("enap_herobanner", EnapBannerBlock()),
    ], use_json_field=True, blank=True, default=get_default_banner_ao_vivo)
    
    # Streaming/Transmissão
    transmissao = StreamField([
        ("container_info", ContainerInfo()),
        ("texto_imagem", TextoImagemBlock()),
    ], use_json_field=True, blank=True, default=get_default_transmissao)
    
    # Programação atual
    programacao = StreamField([
        ("evento", EventoBlock()),
    ], use_json_field=True, blank=True, default=get_default_programacao)
    
    # Palestrantes ativos
    palestrantes_atual = StreamField([
        ("team_moderna", TeamModern()),
    ], use_json_field=True, blank=True, default=get_default_palestrantes_atual)
    
    # Galeria de fotos ao vivo
    galeria_ao_vivo = StreamField([
        ("galeria_moderna", GalleryModernBlock()),
    ], use_json_field=True, blank=True, default=get_default_galeria_ao_vivo)
    
    # Área de contato/chat
    interacao = StreamField([
        ("contato", ContatoBlock()),
        ("form_contato", FormContato()),
    ], use_json_field=True, blank=True, default=get_default_interacao)

    footer = models.ForeignKey(
        "EnapFooterSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    def save(self, *args, **kwargs):
        # Defaults já estão nos StreamFields, método simplificado
        super().save(*args, **kwargs)
    
    content_panels = Page.content_panels + [
        FieldPanel('navbar'),
        FieldPanel('banner_ao_vivo'),
        FieldPanel('transmissao'),
        FieldPanel('programacao'),
        FieldPanel('palestrantes_atual'),
        FieldPanel('galeria_ao_vivo'),
        FieldPanel('interacao'),
        FieldPanel('footer'),
    ]

    class Meta:
        verbose_name = _("Enap Durante Evento")




# Funções para defaults - Pós Evento
def get_default_banner_agradecimento():
    return [{'type': 'enap_herobanner', 'value': {}}]

def get_default_materiais():
    return [{'type': 'download', 'value': {}}]

def get_default_galeria_evento():
    return [{'type': 'galeria_moderna', 'value': {}}]

def get_default_depoimentos():
    return [{'type': 'testimonials_carousel', 'value': {}}]

def get_default_proximos_eventos():
    return [{'type': 'eventos_carousel', 'value': {}}]

def get_default_proximas_acoes():
    return [{'type': 'cta_destaque', 'value': {}}]


class PosEventoPage(Page):
    """Template para página Pós-evento - materiais, feedback e próximos eventos"""
    
    template = 'enap_designsystem/pages/pos_evento.html'

    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    # Banner de agradecimento
    banner_agradecimento = StreamField([
        ("enap_herobanner", EnapBannerBlock()),
    ], use_json_field=True, blank=True, default=get_default_banner_agradecimento)
    
    # Materiais do evento
    materiais = StreamField([
        ("download", DownloadBlock()),
        ("section_card_title_center", SectionCardTitleCenterBlock()),
    ], use_json_field=True, blank=True, default=get_default_materiais)
    
    # Galeria de fotos do evento
    galeria_evento = StreamField([
        ("galeria_moderna", GalleryModernBlock()),
    ], use_json_field=True, blank=True, default=get_default_galeria_evento)
    
    # Depoimentos dos participantes
    depoimentos = StreamField([
        ("testimonials_carousel", TestimonialsCarouselBlock()),
        ("QuoteModern", QuoteBlockModern()),
    ], use_json_field=True, blank=True, default=get_default_depoimentos)
    
    # Próximos eventos
    proximos_eventos = StreamField([
        ("eventos_carousel", EventsCarouselBlock()),
        ("carrossel_cursos", CarrosselCursosBlock()),
    ], use_json_field=True, blank=True, default=get_default_proximos_eventos)
    
    # CTA para próximas ações
    proximas_acoes = StreamField([
        ("cta_destaque", CtaDestaqueBlock()),
        ("secao_adesao", SecaoAdesaoBlock()),
    ], use_json_field=True, blank=True, default=get_default_proximas_acoes)

    footer = models.ForeignKey(
        "EnapFooterSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    def save(self, *args, **kwargs):
        # Defaults já estão nos StreamFields, método simplificado
        super().save(*args, **kwargs)
    
    content_panels = Page.content_panels + [
        FieldPanel('navbar'),
        FieldPanel('banner_agradecimento'),
        FieldPanel('materiais'),
        FieldPanel('galeria_evento'),
        FieldPanel('depoimentos'),
        FieldPanel('proximos_eventos'),
        FieldPanel('proximas_acoes'),
        FieldPanel('footer'),
    ]

    class Meta:
        verbose_name = _("Enap Pós Evento")







# Função para pegar primeira página disponível
def get_first_available_page():
    from wagtail.models import Page
    try:
        # Tenta pegar a primeira página que não seja root ou home
        page = Page.objects.exclude(
            content_type__model__in=['page', 'rootpage']
        ).live().first()
        return page if page else None
    except:
        return None

# Funções de default para CursoEadPage
def get_default_banner_curso():
    return [{'type': 'hero', 'value': {}}]

def get_default_apresentacao_curso():
    return [{'type': 'course_intro_topics', 'value': {}}]

def get_default_estrutura_curso():
    return [{'type': 'feature_estrutura', 'value': {}}]

def get_default_vantagens():
    return [{'type': 'why_choose', 'value': {}}]

def get_default_depoimentos_alunos():
    return [{'type': 'testimonials_carousel', 'value': {}}]

def get_default_cursos_relacionados():
    default_page = get_first_available_page()
    if default_page:
        return [{
            'type': 'preview_courses', 
            'value': {
                'titulo': 'Cursos relacionados',
                'paginas_relacionadas': default_page.pk
            }
        }]
    else:
        # Se não encontrar página, retorna sem o campo obrigatório preenchido
        return [{
            'type': 'preview_courses', 
            'value': {
                'titulo': 'Cursos relacionados'
            }
        }]

def get_default_inscricao():
    return [{'type': 'cta_2', 'value': {}}]

def get_default_faq_curso():
    return [{
        'type': 'accordion', 
        'value': {
            'title': 'Pergunta Frequente 1',
            'content': 'Esta é uma resposta de exemplo para a primeira pergunta frequente. Você pode editar este conteúdo conforme necessário.'
        }
    }]

def get_default_curso():
    return [{'type': 'enap_section', 'value': {
        'content': [
            {
                'type': 'enap_cardgrid',
                'value': {
                    'cards_per_row': '2',  # Default para "Até 2 cards"
                    'cards': [
                        {'type': 'enap_card', 'value': {
                            'titulo': 'Card Exemplo 1',
                            'descricao': 'Descrição do primeiro card'
                        }},
                        {'type': 'card_curso', 'value': {
                            'titulo': 'Card Curso Exemplo',
                            'descricao': 'Descrição do card de curso'
                        }}
                    ]
                }
            },
            {
                'type': 'aviso',
                'value': {
                    'titulo': 'Aviso Importante',
                    'conteudo': 'Conteúdo do aviso'
                }
            }
        ]
    }}]


class CursoEadPage(Page):
    """Template para Cursos EAD - ensino à distância"""
    
    template = 'enap_designsystem/pages/curso_ead.html'

    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    # Banner do curso
    banner_curso = StreamField([
        ("hero", HeroBlockv3()),
        ("enap_herobanner", EnapBannerBlock()),
    ], use_json_field=True, blank=True, default=get_default_banner_curso)
    
    # Apresentação do curso
    apresentacao_curso = StreamField([
        ("course_intro_topics", CourseIntroTopicsBlock()),
        ("feature_course", CourseFeatureBlock()),
    ], use_json_field=True, blank=True, default=get_default_apresentacao_curso)
    
    # Estrutura do curso/módulos
    estrutura_curso = StreamField([
        ("feature_estrutura", CourseModulesBlock()),
        ("section_tabs_cards", SectionTabsCardsBlock()),
    ], use_json_field=True, blank=True, default=get_default_estrutura_curso)
    
    # Por que escolher este curso
    vantagens = StreamField([
        ("why_choose", WhyChooseEnaptBlock()),
        ("feature_list", FeatureListBlock()),
    ], use_json_field=True, blank=True, default=get_default_vantagens)
    
    # Depoimentos de alunos
    depoimentos_alunos = StreamField([
        ("testimonials_carousel", TestimonialsCarouselBlock()),
    ], use_json_field=True, blank=True, default=get_default_depoimentos_alunos)
    
    # Cursos relacionados
    cursos_relacionados = StreamField([
        ("preview_courses", PreviewCoursesBlock()),
        ("carrossel_cursos", CarrosselCursosBlock()),
    ], use_json_field=True, blank=True, default=get_default_cursos_relacionados)
    
    # CTA de inscrição
    inscricao = StreamField([
        ("cta_2", CTA2Block()),
        ("secao_adesao", SecaoAdesaoBlock()),
    ], use_json_field=True, blank=True, default=get_default_inscricao)
    
    # FAQ do curso
    faq_curso = StreamField([
        ("accordion", AccordionItemBlock()),
    ], use_json_field=True, blank=True, default=get_default_faq_curso)

    # Campo adicional com todos os blocos disponíveis
    curso = StreamField([
        ("enap_section", EnapSectionBlock([
            ("enap_cardgrid", EnapCardGridBlock([
                ("enap_card", EnapCardBlock()),
                ('card_curso', CardCursoBlock()),
            ])),
            ('aviso', AvisoBlock()),
        ])),
    ], use_json_field=True, blank=True, default=get_default_curso)

    footer = models.ForeignKey(
        "EnapFooterSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    def save(self, *args, **kwargs):
        # Defaults já definidos nos StreamFields, método simplificado
        super().save(*args, **kwargs)
    
    content_panels = Page.content_panels + [
        FieldPanel('navbar'),
        FieldPanel('banner_curso'),
        FieldPanel('apresentacao_curso'),
        FieldPanel('estrutura_curso'),
        FieldPanel('vantagens'),
        FieldPanel('depoimentos_alunos'),
        FieldPanel('cursos_relacionados'),
        FieldPanel('inscricao'),
        FieldPanel('faq_curso'),
        FieldPanel('curso'),  # Campo adicional para blocos extras
        FieldPanel('footer'),
    ]

    class Meta:
        verbose_name = _("Enap Curso EAD")






class Contato(models.Model):
    nome = models.CharField('Nome', max_length=200)
    email = models.EmailField('Email')
    mensagem = models.TextField('Mensagem')
    data = models.DateTimeField('Data de Envio', auto_now_add=True)
    
    def __str__(self):
        return f"{self.nome} - {self.data.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        ordering = ['-data']





@register_snippet
class FormularioSnippet(models.Model):
    """Formulário configurável como snippet"""
    nome = models.CharField('Nome do Formulário', max_length=100)
    titulo = models.CharField('Título', max_length=200, blank=True)
    descricao = models.TextField('Descrição', blank=True)
    email_destino = models.EmailField('Email de Destino')
    ativo = models.BooleanField('Ativo', default=True)
    
    panels = [
        FieldPanel('nome'),
        FieldPanel('titulo'),
        FieldPanel('descricao'),
        FieldPanel('email_destino'),
        FieldPanel('ativo'),
    ]
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Formulário"
        verbose_name_plural = "Formulários"


@register_snippet
class RespostaFormulario(models.Model):
    """Respostas dos formulários"""
    formulario = models.ForeignKey(
        FormularioSnippet,  # <- DEVE SER FormularioSnippet, NÃO FormularioContato
        on_delete=models.CASCADE, 
        related_name='respostas'
    )
    nome = models.CharField('Nome', max_length=200)
    email = models.EmailField('Email')
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    assunto = models.CharField('Assunto', max_length=200)
    mensagem = models.TextField('Mensagem')
    data = models.DateTimeField('Data de Envio', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    
    def __str__(self):
        return f"{self.nome} - {self.formulario.nome}"
    
    class Meta:
        verbose_name = "Resposta Formulário"
        verbose_name_plural = "Respostas Formulários"
        ordering = ['-data']






@register_snippet
class ChatbotConfig(models.Model):
    """Configurações do chatbot"""
    nome = models.CharField(max_length=100, default="Assistente ENAP")
    mensagem_boas_vindas = models.TextField(
        default="Olá! Sou o assistente virtual da ENAP. Como posso ajudar você hoje?"
    )
    prompt_sistema = models.TextField(
        default="""Você é um assistente virtual da ENAP (Escola Nacional de Administração Pública). 
        Responda perguntas sobre os conteúdos do portal de forma clara e objetiva. 
        Sempre indique links relevantes quando disponíveis."""
    )
    api_key_google = models.CharField(
        max_length=200, 
        blank=True, 
        help_text="API Key do Google AI Studio"
    )
    modelo_ia = models.CharField(
        max_length=50, 
        choices=[
            ('gemini-1.5-flash', 'Gemini 1.5 Flash'),
            ('gemini-1.5-pro', 'Gemini 1.5 Pro'),
            ('gemini-pro', 'Gemini Pro'),
        ],
        default='gemini-1.5-flash'
    )
    ativo = models.BooleanField(default=True)

    panels = [
        FieldPanel('nome'),
        FieldPanel('mensagem_boas_vindas'),
        FieldPanel('prompt_sistema'),
        FieldPanel('api_key_google'),
        FieldPanel('modelo_ia'),
        FieldPanel('ativo'),
    ]

    class Meta:
        verbose_name = "Configuração do Chatbot"
        verbose_name_plural = "Configurações do Chatbot"

    def __str__(self):
        return f"Chatbot: {self.nome}"


@register_snippet
class ChatbotWidget(models.Model):
    """Widget visual do chatbot"""
    nome = models.CharField(max_length=100)
    titulo_widget = models.CharField(max_length=200, default="Assistente Virtual ENAP")
    cor_primaria = models.CharField(
        max_length=7, 
        default="#0066cc", 
        help_text="Cor em hex (#000000)"
    )
    cor_secundaria = models.CharField(
        max_length=7, 
        default="#ffffff", 
        help_text="Cor em hex (#ffffff)"
    )
    posicao = models.CharField(
        max_length=20,
        choices=[
            ('bottom-right', 'Inferior Direito'),
            ('bottom-left', 'Inferior Esquerdo'),
            ('top-right', 'Superior Direito'),
            ('top-left', 'Superior Esquerdo'),
        ],
        default='bottom-right'
    )
    icone_chatbot = models.CharField(
        max_length=50,
        choices=[
            ('💬', 'Balão de conversa'),
            ('🤖', 'Robô'),
            ('💭', 'Balão de pensamento'),
            ('📞', 'Telefone'),
            ('❓', 'Interrogação'),
        ],
        default='🤖'
    )
    mostrar_em_mobile = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)

    panels = [
        FieldPanel('nome'),
        FieldPanel('titulo_widget'),
        FieldPanel('cor_primaria'),
        FieldPanel('cor_secundaria'),
        FieldPanel('posicao'),
        FieldPanel('icone_chatbot'),
        FieldPanel('mostrar_em_mobile'),
        FieldPanel('ativo'),
    ]

    class Meta:
        verbose_name = "Widget do Chatbot"
        verbose_name_plural = "Widgets do Chatbot"

    def __str__(self):
        return self.nome


class PaginaIndexada(models.Model):
    """Páginas indexadas para o chatbot"""
    pagina = models.ForeignKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name='indexacao_chatbot'
    )
    titulo = models.CharField(max_length=500)
    conteudo_texto = models.TextField()
    url = models.URLField()
    tags = models.TextField(blank=True)  # JSON com tags/palavras-chave
    data_indexacao = models.DateTimeField(auto_now=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Página Indexada"
        verbose_name_plural = "Páginas Indexadas"
        unique_together = ['pagina']

    def __str__(self):
        return f"Indexada: {self.titulo}"


class ConversaChatbot(models.Model):
    """Conversas do chatbot"""
    sessao_id = models.CharField(max_length=100)
    usuario_ip = models.GenericIPAddressField(blank=True, null=True)
    mensagem_usuario = models.TextField()
    resposta_bot = models.TextField()
    paginas_referenciadas = models.TextField(blank=True)  # JSON com links
    data_conversa = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Conversa do Chatbot"
        verbose_name_plural = "Conversas do Chatbot"

    def __str__(self):
        return f"Conversa {self.sessao_id[:8]} - {self.data_conversa.strftime('%d/%m/%Y %H:%M')}"
	






class CartaService(Page):
    
    template = 'enap_designsystem/pages/carta_servico.html'

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
        FieldPanel('navbar'),
        FieldPanel('footer'),
    ]

    class Meta:
        verbose_name = ("Carta de Serviço")






class ENAPService(Page):
	"""Página personalizada independente do CoderedWebPage."""
	
	admin_notes = models.TextField(
		verbose_name="Anotações Internas",
		blank=True,
		help_text="Escreva observações importantes. Este campo é visível apenas para administradores."
	)

	template = "enap_designsystem/pages/enap_layout.html"

	body = StreamField(
		LAYOUT_STREAMBLOCKS,
		null=True,
		blank=True,
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
		FieldPanel("body"),
		FieldPanel("footer"),
		FieldPanel("admin_notes"),
	]

	@property
	def url_filter(self):
		"""URL do serviço para busca"""
		if hasattr(self, 'full_url') and self.full_url:
			return self.full_url
		return self.get_url_parts()[2] if self.get_url_parts() else ""
	
	@property
	def titulo_filter(self):
		"""Título extraído do hero banner ou title da página"""
		for block in self.body:
			if block.block_type == "enap_herobanner":
				titulo_hero = block.value.get("title", "")
				if titulo_hero:
					return titulo_hero
		return self.title  # Fallback para o título da página
	
	@property
	def descricao_filter(self):
		"""Descrição extraída do hero banner ou search_description"""
		for block in self.body:
			if block.block_type == "enap_herobanner":
				desc = block.value.get("description", "")
				if desc:
					if hasattr(desc, "source"):
						return strip_tags(desc.source).strip()
					return strip_tags(str(desc)).strip()
		
		# Fallback para search_description
		if self.search_description:
			return self.search_description
		
		return ""

	@property
	def data_atualizacao_filter(self):
		"""Data de atualização para ordenação"""
		return self.last_published_at or self.latest_revision_created_at

	@property
	def data_publicacao_filter(self):
		"""Data de publicação para ordenação"""
		return self.first_published_at

	@property
	def categoria(self):
		"""Categoria do serviço"""
		return "Serviços"
	
	@property
	def imagem_filter(self):
		"""Imagem principal extraída dos blocos"""
		tipos_com_imagem = [
			("enap_herobanner", "background_image"),
			("bannertopics", "imagem_fundo"),
			("banner_image_cta", "hero_image"),
			("hero", "background_image"),
			("banner_search", "imagem_principal"),
		]

		try:
			for bloco in self.body:
				for tipo, campo_imagem in tipos_com_imagem:
					if bloco.block_type == tipo:
						imagem = bloco.value.get(campo_imagem)
						if imagem:
							return imagem.file.url
		except Exception:
			pass

		return ""
	
	@property
	def texto_unificado(self):
		"""Texto completo para busca textual"""
		def extract_text_from_block(block_value):
			result = []

			if isinstance(block_value, list):
				for subblock in block_value:
					result.extend(extract_text_from_block(subblock))
			elif hasattr(block_value, "get"):  # StructValue
				for key, val in block_value.items():
					result.extend(extract_text_from_block(val))
			elif isinstance(block_value, str):
				cleaned = strip_tags(block_value).strip()
				if cleaned and cleaned.lower() not in {
					"default", "tipo terciário", "tipo secundário", "tipo bg image",
					"bg-gray", "bg-blue", "bg-white", "fundo cinza", "fundo branco"
				}:
					result.append(cleaned)
			elif hasattr(block_value, "source"):  # RichText
				cleaned = strip_tags(block_value.source).strip()
				if cleaned:
					result.append(cleaned)

			return result

		textos = []
		if hasattr(self, "body") and self.body:
			for block in self.body:
				textos.extend(extract_text_from_block(block.value))

		# Junta tudo em uma string e remove quebras de linha duplicadas
		texto_final = " ".join([t for t in textos if t])
		texto_final = re.sub(r"\s+", " ", texto_final).strip()
		return texto_final

	# ✅ Search fields seguindo o padrão de notícias
	search_fields = Page.search_fields + [
		index.SearchField("title", boost=3),
		index.SearchField("titulo_filter", name="titulo"),
		index.SearchField("descricao_filter", name="descricao"),
		index.FilterField("categoria", name="categoria_filter"),
		index.SearchField("url_filter", name="url"),
		index.FilterField("data_atualizacao_filter", name="data_atualizacao"),
		index.FilterField("data_publicacao_filter", name="data_publicacao"),
		index.SearchField("imagem_filter", name="imagem"),
		index.SearchField("texto_unificado", name="body"),
	]

	class Meta:
		verbose_name = "serviços Enap"
		verbose_name_plural = "serviços Enap"






class LiaPage(Page):
	
    page_title = models.CharField(
        max_length=255, 
        default="Título Padrão", 
        verbose_name="Título da Página",
		blank=False, 
    )

    template = "enap_designsystem/blocks/page/lia.html"


    body = RichTextField(
        blank=True, 
        verbose_name="Título da sessão: O que é IA"
    )
    paragrafo = RichTextField(
        blank=True, 
        help_text="Adicione o texto do parágrafo aqui.", 
        verbose_name="Parágrafo card: O que é IA?"
    )
    
    video_background = models.FileField(
        upload_to='media/imagens', 
        null=True, 
        blank=True, 
        verbose_name="Vídeo de Fundo"
    )

    # Painéis no admin do Wagtail
    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        FieldPanel('body'),
        FieldPanel('paragrafo'),
        FieldPanel('video_background'),
    ]




original_serve = Page.serve

def custom_serve(self, request, *args, **kwargs):
    """Override que captura TODOS os 404s do Wagtail"""
    try:
        return original_serve(self, request, *args, **kwargs)
    except Http404:
        print(f"🚨 404 capturado no models.py: {request.path}")
        
        context = {
            'request': request,
            'page_title': 'Página não encontrada - ENAP',
            'requested_path': request.path,
            'site': getattr(request, 'site', None)
        }
        
        # 👇 AQUI VOCÊ ESCOLHE O TEMPLATE EXATO
        template_name = 'errors/404.html' 
        
        return render(request, template_name, context, status=404)

# Substitui o método serve de TODAS as páginas Wagtail
Page.serve = custom_serve

print("✅ Override de 404 ativado com template customizado!")






# seo_models.py - Implementação manual de SEO para Wagtail
from django.db import models
from django.utils.html import strip_tags
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
import re

class SEOMixin(models.Model):
    """
    Mixin para adicionar funcionalidades de SEO a qualquer página Wagtail
    Compatível com páginas existentes - não quebra nada!
    """
    
    # Campos SEO opcionais
    seo_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Título para SEO (máx. 60 caracteres). Se vazio, usa o título da página."
    )
    
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        help_text="Descrição para SEO (máx. 160 caracteres). Se vazio, gera automaticamente."
    )
    
    og_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Imagem para redes sociais (1200x630px recomendado)"
    )
    
    # Propriedades que funcionam automaticamente
    @property
    def get_meta_title(self):
        """Retorna título para SEO ou título da página"""
        return self.seo_title or self.title
    
    @property
    def get_meta_description(self):
        """Retorna descrição para SEO ou gera automaticamente"""
        if self.meta_description:
            return self.meta_description
        
        # Auto-gerar a partir do conteúdo da página
        return self._generate_auto_description()
    
    @property
    def get_og_image(self):
        """Retorna imagem para Open Graph"""
        if self.og_image:
            return self.og_image
        
        # Tenta encontrar primeira imagem no conteúdo
        return self._find_first_image()
    
    def _generate_auto_description(self):
        """Gera descrição automaticamente a partir do conteúdo"""
        description_sources = []
        
        # Tenta várias fontes de conteúdo
        content_fields = ['body', 'content', 'introduction', 'summary', 'description']
        
        for field_name in content_fields:
            if hasattr(self, field_name):
                field_value = getattr(self, field_name)
                if field_value:
                    if hasattr(field_value, 'source'):  # RichTextField
                        text = strip_tags(field_value.source)
                    else:
                        text = strip_tags(str(field_value))
                    
                    if text.strip():
                        description_sources.append(text.strip())
        
        if description_sources:
            # Pega o primeiro conteúdo encontrado
            full_text = description_sources[0]
            # Remove quebras de linha extras e espaços
            clean_text = re.sub(r'\s+', ' ', full_text).strip()
            # Corta em 160 caracteres
            if len(clean_text) > 160:
                return clean_text[:157] + '...'
            return clean_text
        
        # Fallback padrão
        return f"Conheça mais sobre {self.title} na ENAP - Escola Nacional de Administração Pública."
    
    def _find_first_image(self):
        """Encontra primeira imagem no conteúdo para Open Graph"""
        content_fields = ['body', 'content']
        
        for field_name in content_fields:
            if hasattr(self, field_name):
                field_value = getattr(self, field_name)
                if hasattr(field_value, 'stream_data'):  # StreamField
                    for block_data in field_value.stream_data:
                        if block_data.get('type') == 'image' and block_data.get('value'):
                            try:
                                from wagtail.images import get_image_model
                                Image = get_image_model()
                                return Image.objects.get(id=block_data['value'])
                            except:
                                continue
        return None
    
    # Painéis para o admin do Wagtail
    seo_panels = [
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('meta_description'),
            FieldPanel('og_image'),
        ], heading="SEO & Redes Sociais", classname="collapsible collapsed")
    ]
    
    class Meta:
        abstract = True


class OpenGraphMixin(models.Model):
    """
    Mixin adicional para Open Graph completo
    Use junto com SEOMixin se precisar de mais controle
    """
    
    og_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Título para redes sociais (se diferente do SEO)"
    )
    
    og_description = models.TextField(
        max_length=160,
        blank=True,
        help_text="Descrição para redes sociais (se diferente do SEO)"
    )
    
    twitter_card_type = models.CharField(
        max_length=20,
        choices=[
            ('summary', 'Summary'),
            ('summary_large_image', 'Summary Large Image'),
            ('app', 'App'),
            ('player', 'Player'),
        ],
        default='summary_large_image',
        help_text="Tipo de card do Twitter"
    )
    
    @property
    def get_og_title(self):
        return self.og_title or self.get_meta_title
    
    @property
    def get_og_description(self):
        return self.og_description or self.get_meta_description
    
    # Painéis adicionais
    og_panels = [
        MultiFieldPanel([
            FieldPanel('og_title'),
            FieldPanel('og_description'),
            FieldPanel('twitter_card_type'),
        ], heading="Open Graph Avançado", classname="collapsible collapsed")
    ]
    
    class Meta:
        abstract = True


# Classe combinada para uso mais fácil
class FullSEOMixin(SEOMixin, OpenGraphMixin):
    """
    Mixin completo com todas as funcionalidades de SEO
    """
    
    @property
    def all_seo_panels(self):
        return self.seo_panels + self.og_panels
    
    class Meta:
        abstract = True







@register_snippet
class FormularioDinamicoSubmission(models.Model):
    """
    Modelo para submissões do FormularioDinâmico
    Pode ser usado em qualquer página
    """
    # Referência genérica para qualquer página
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    page = GenericForeignKey('content_type', 'object_id')
    
    # Dados da submissão (mesmo formato do FormularioSubmission)
    form_data = models.JSONField(verbose_name="Dados do formulário", default=dict)
    files_data = models.JSONField(verbose_name="Metadados dos arquivos", default=dict)
    uploaded_files = models.JSONField(
        verbose_name="Caminhos dos arquivos salvos", 
        default=dict,
        help_text="Caminhos onde os arquivos foram salvos no sistema"
    )
    
    # Metadados (mesmo formato)
    submit_time = models.DateTimeField(auto_now_add=True)
    user_ip = models.GenericIPAddressField(verbose_name="IP do usuário", null=True, blank=True)
    user_agent = models.TextField(verbose_name="User Agent", blank=True)
    
    # Campos extraídos automaticamente para facilitar consultas e exportação
    user_name = models.CharField(max_length=200, blank=True, verbose_name="Nome")
    user_email = models.EmailField(blank=True, verbose_name="E-mail")
    user_phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    page_title = models.CharField(max_length=200, blank=True, verbose_name="Título da Página")
    
    class Meta:
        verbose_name = "Submissão de Formulário Dinâmico"
        verbose_name_plural = "Submissões de Formulários Dinâmicos"
        ordering = ['-submit_time']

    def __str__(self):
        nome = self.user_name or "Anônimo"
        return f"{nome} - {self.page_title} - {self.submit_time.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Extrair informações automaticamente dos dados do formulário
        if self.form_data:
            self.extract_user_info()
        
        # Extrair título da página
        if hasattr(self.page, 'title'):
            self.page_title = self.page.title
        
        super().save(*args, **kwargs)
    
    def extract_user_info(self):
        """Extrai informações do usuário dos dados do formulário"""
        for field_name, value in self.form_data.items():
            if not value:
                continue
                
            field_lower = field_name.lower()
            
            # Detectar nome
            if any(keyword in field_lower for keyword in ['nome', 'name']) and not self.user_name:
                self.user_name = str(value)[:200]
            
            # Detectar email
            elif 'email' in field_lower and not self.user_email:
                self.user_email = str(value)[:254]
            
            # Detectar telefone
            elif any(keyword in field_lower for keyword in ['telefone', 'phone', 'celular']) and not self.user_phone:
                self.user_phone = str(value)[:20]
    
    def get_readable_data(self):
        """Retorna dados em formato legível (mesmo método do FormularioSubmission)"""
        readable = {}
        for key, value in self.form_data.items():
            if isinstance(value, list):
                readable[key] = ', '.join(str(v) for v in value)
            else:
                readable[key] = str(value)
        return readable
	






@receiver(pre_delete, sender=FormularioDinamicoSubmission)
def delete_dynamic_submission_files(sender, instance, **kwargs):
    """Deleta arquivos quando submissão é deletada"""
    page_id = instance.object_id
    submission_folder = os.path.join(
        settings.MEDIA_ROOT, 
        'formularios', 
        f'page_{page_id}', 
        f'submission_{instance.id}'
    )
    
    if os.path.exists(submission_folder):
        shutil.rmtree(submission_folder)
        print(f"🗑️ Pasta deletada: {submission_folder}")

@receiver(pre_delete, sender=FormularioPage)
def delete_form_page_files(sender, instance, **kwargs):
    """Deleta TODOS os arquivos quando formulário é deletado"""
    form_folder = os.path.join(
        settings.MEDIA_ROOT, 
        'formularios', 
        f'page_{instance.id}'
    )
    
    if os.path.exists(form_folder):
        shutil.rmtree(form_folder)
        print(f"🗑️ FORMULÁRIO DELETADO: {form_folder}")













@register_snippet
class GroupPageTypePermission(models.Model):
    """
    Modelo para controlar quais tipos de página cada grupo pode acessar
    Registrado como snippet para fácil gerenciamento no admin
    """
    group = models.OneToOneField(
        Group, 
        on_delete=models.CASCADE,
        related_name='page_type_permissions',
        verbose_name='Grupo'
    )
    content_types = models.ManyToManyField(
        ContentType, 
        verbose_name='Tipos de Página Permitidos',
        help_text='Selecione todos os tipos de página que este grupo pode acessar',
        blank=True
    )
    
    panels = [
        FieldPanel('group'),
        FieldPanel('content_types'),
    ]
    
    class Meta:
        verbose_name = 'Permissão de Tipos de Página por Grupo'
        verbose_name_plural = 'Permissões de Tipos de Página por Grupo'
    
    def __str__(self):
        count = self.content_types.count()
        if count == 0:
            return f"{self.group.name} → Nenhum tipo permitido"
        elif count == 1:
            return f"{self.group.name} → {self.content_types.first().name}"
        else:
            return f"{self.group.name} → {count} tipos permitidos"

    @classmethod
    def get_allowed_page_types_for_user(cls, user):
        """
        Retorna os tipos de página que um usuário pode acessar
        """
        if user.is_superuser:
            return Page.get_page_types()
        
        user_groups = user.groups.all()
        allowed_types = set()
        
        for group in user_groups:
            try:
                permission = cls.objects.get(group=group)
                group_types = [ct.model_class() for ct in permission.content_types.all() if ct.model_class()]
                allowed_types.update(group_types)
            except cls.DoesNotExist:
                # Grupo não tem permissões configuradas
                continue
        
        return list(allowed_types) if allowed_types else []
    
    def get_allowed_content_types(self):
        """
        Retorna apenas ContentTypes que são páginas Wagtail válidas
        """
        page_content_types = []
        for ct in ContentType.objects.all():
            try:
                model_class = ct.model_class()
                if (model_class and 
                    issubclass(model_class, Page) and 
                    model_class != Page and
                    not model_class._meta.abstract):
                    page_content_types.append(ct)
            except:
                pass
        return page_content_types

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Após salvar, filtrar apenas ContentTypes válidos
        valid_content_types = self.get_allowed_content_types()
        self.content_types.set([ct for ct in self.content_types.all() if ct in valid_content_types])

