
from wagtail import blocks
from coderedcms.settings import crx_settings

from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from wagtail.documents.blocks import DocumentChooserBlock
from django import forms
from django.utils.functional import cached_property
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.blocks import StructBlock, CharBlock, TextBlock, ListBlock, ChoiceBlock
from wagtail.images.blocks import ImageChooserBlock


from .semana_blocks import (
    BRAND_INOVACAO_CHOICES, 
    BRAND_TEXTS_CHOICES,
    BRAND_BG_CHOICES, 
    BRAND_BUTTON_CHOICES, 
    BRAND_HOVER_CHOICES
)

class CoderedAdvSettings(blocks.StructBlock):
    """
    Common fields each block should have,
    which are hidden under the block's "Advanced Settings" dropdown.
    """

    # placeholder, real value get set in __init__()
    custom_template = blocks.Block()

    custom_css_class = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Custom CSS Class"),
    )
    custom_id = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Custom ID"),
    )

    class Meta:
        form_template = (
            "wagtailadmin/block_forms/base_block_settings_struct.html"
        )
        label = _("Configurações avançadas")

    def __init__(self, local_blocks=None, template_choices=None, **kwargs):
        if not local_blocks:
            local_blocks = ()

        local_blocks += (
            (
                "custom_template",
                blocks.ChoiceBlock(
                    choices=template_choices,
                    default=None,
                    required=False,
                    label=_("Template"),
                ),
            ),
        )

        super().__init__(local_blocks, **kwargs)

class BaseBlock(blocks.StructBlock):
    """
    Common attributes for all blocks used in Wagtail CRX.
    """

    # subclasses can override this to determine the advanced settings class
    advsettings_class = CoderedAdvSettings

    # placeholder, real value get set in __init__() from advsettings_class
    settings = blocks.Block()

    def __init__(self, local_blocks=None, **kwargs):
        """
        Construct and inject settings block, then initialize normally.
        """
        klassname = self.__class__.__name__.lower()
        choices = crx_settings.CRX_FRONTEND_TEMPLATES_BLOCKS.get(
            "*", []
        ) + crx_settings.CRX_FRONTEND_TEMPLATES_BLOCKS.get(klassname, [])

        if not local_blocks:
            local_blocks = ()

        local_blocks += (
            ("settings", self.advsettings_class(template_choices=choices)),
        )

        super().__init__(local_blocks, **kwargs)

    def render(self, value, context=None):
        template = value["settings"]["custom_template"]

        if not template:
            template = self.get_template(context=context)
            if not template:
                return self.render_basic(value, context=context)

        if context is None:
            new_context = self.get_context(value)
        else:
            new_context = self.get_context(value, parent_context=dict(context))

        return mark_safe(render_to_string(template, new_context))

class BaseLayoutBlock(BaseBlock):
    """
    Common attributes for all blocks used in Wagtail CRX.
    """

    # Subclasses can override this to provide a default list of blocks for the content.
    content_streamblocks = []

    def __init__(self, local_blocks=None, **kwargs):
        if not local_blocks and self.content_streamblocks:
            local_blocks = self.content_streamblocks

        if local_blocks:
            local_blocks = (
                (
                    "content",
                    blocks.StreamBlock(local_blocks, label=_("Conteúdo")),
                ),
            )

        super().__init__(local_blocks, **kwargs)

class LinkStructValue(blocks.StructValue):
    """
    Generates a URL and Title for blocks with multiple link choices.
    Designed to be used with ``BaseLinkBlock``.
    """

    @property
    def get_title(self):
        title = self.get("title")
        button_title = self.get("button_title")
        page = self.get("page_link")
        doc = self.get("doc_link")
        ext = self.get("other_link")
        if title:
            return title
        if button_title:
            return button_title
        if page:
            return page.title
        elif doc:
            return doc.title
        else:
            return ext

    @property
    def url(self):
        page = self.get("page_link")
        doc = self.get("doc_link")
        ext = self.get("other_link")
        if page and ext:
            return "{0}{1}".format(page.url, ext)
        elif page:
            return page.url
        elif doc:
            return doc.url
        else:
            return ext
        

class ButtonMixin(blocks.StructBlock):
    """
    Standard style and size options for buttons.
    """

    button_style = blocks.ChoiceBlock(
        choices=crx_settings.CRX_FRONTEND_BTN_STYLE_CHOICES,
        default=crx_settings.CRX_FRONTEND_BTN_STYLE_DEFAULT,
        required=False,
        label=_("Button Style"),
    )
    button_size = blocks.ChoiceBlock(
        choices=crx_settings.CRX_FRONTEND_BTN_SIZE_CHOICES,
        default=crx_settings.CRX_FRONTEND_BTN_SIZE_DEFAULT,
        required=False,
        label=_("Button Size"),
    )
    button_title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Title"),
    )

class CoderedAdvTrackingSettings(CoderedAdvSettings):
    """
    CoderedAdvSettings plus additional tracking fields.
    """

    ga_tracking_event_category = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Tracking Event Category"),
    )
    ga_tracking_event_label = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Tracking Event Label"),
    )
    
class CoderedAdvColumnSettings(CoderedAdvSettings):
    """
    BaseBlockSettings plus additional column fields.
    """

    column_breakpoint = blocks.ChoiceBlock(
        choices=crx_settings.CRX_FRONTEND_COL_BREAK_CHOICES,
        default=crx_settings.CRX_FRONTEND_COL_BREAK_DEFAULT,
        required=False,
        verbose_name=_("Column Breakpoint"),
        help_text=_(
            "Screen size at which the column will expand horizontally or stack vertically."
        ),
    )

class BaseLinkBlock(BaseBlock):
    """
    Common attributes for creating a link within the CMS.
    """

    page_link = blocks.PageChooserBlock(
        required=False,
        label=_("Page link"),
    )
    doc_link = DocumentChooserBlock(
        required=False,
        label=_("Document link"),
    )
    other_link = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Other link"),
    )
    button_title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Title"),
    )

    advsettings_class = CoderedAdvTrackingSettings

    class Meta:
        value_class = LinkStructValue




class ButtonBlock(StructBlock):
    """
    Bloco individual para um botão dentro do ButtonGroup
    """
    label = CharBlock(required=True, help_text="Texto do botão")
    url = CharBlock(required=False, help_text="URL para onde o botão vai direcionar (opcional)")
    
    class Meta:
        icon = 'link'
        label = 'Botão'

class ButtonGroupBlock(StructBlock):
    """
    Bloco para um grupo de botões que pode alternar entre estilos solid e outline
    """
    style = ChoiceBlock(choices=[
        ('solid', 'Solid - Fundo colorido'),
        ('outline', 'Outline - Apenas contorno'),
    ], default='solid', help_text="Estilo visual dos botões")
    
    buttons = ListBlock(
        ButtonBlock(),
        min_num=1,
        max_num=10,
        help_text="Adicione botões ao grupo (entre 1 e 10)"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/buttongroup.html'
        icon = 'grip'
        label = 'Grupo de Botões'


class ButtonCenter(StructBlock):
    """
    Bloco para um grupo de botões que pode alternar entre estilos solid e outline
    """
    style = ChoiceBlock(choices=[
        ('solid', 'Solid - Fundo colorido'),
        ('outline', 'Outline - Apenas contorno'),
    ], default='solid', help_text="Estilo visual dos botões")
    
    buttons = ListBlock(
        ButtonBlock(),
        min_num=1,
        max_num=10,
        help_text="Adicione botões ao grupo (entre 1 e 10)"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/buttoncenter.html'
        icon = 'grip'
        label = 'Button center'

class CarouselSlideBlock(StructBlock):
    """
    Bloco para um slide individual dentro do carrossel
    """
    background_image = ImageChooserBlock(required=True, help_text="Imagem de fundo para o slide")
    slide_type = ChoiceBlock(choices=[
        ('title_center', 'Título centralizado'),
        ('title_desc_left', 'Título e descrição à esquerda com grafismo'),
        ('blank', 'Slide em branco'),
    ], default='title_center', help_text="Escolha o formato do slide")
    title = CharBlock(
        required=False, 
        help_text="Título do slide (não usado no formato em branco)"
    )
    
    title_color = ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#FFFFFF',
        required=False,
        help_text="Cor do título conforme Design System ENAP"
    )
    
    description = TextBlock(
        required=False, 
        help_text="Descrição do slide (usado apenas no formato 'Título e descrição à esquerda')"
    )
    
    description_color = ChoiceBlock(
        choices=BRAND_TEXTS_CHOICES,
        default='#FFFFFF',
        required=False,
        help_text="Cor da descrição conforme Design System ENAP"
    )
    
    class Meta:
        icon = 'image'
        label = 'Slide do Carrossel'

class CarouselBlock(StructBlock):
    """
    Bloco para um carrossel de slides
    """
    slides = ListBlock(
        CarouselSlideBlock(),
        min_num=1,
        max_num=10,
        help_text="Adicione slides ao carrossel (entre 1 e 10)"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/carousel.html'
        icon = 'image'
        label = 'Carrossel'






class FormularioSnippetBlock(blocks.StructBlock):
    """Bloco do formulário que usa snippet"""
    formulario = SnippetChooserBlock( 
        'enap_designsystem.FormularioSnippet',
        help_text="Escolha o formulário a ser exibido"
    )
    
    class Meta:
        template = 'enap_designsystem/blocks/formulario_snippet.html'
        icon = 'form'
        label = 'Formulário de Contato'