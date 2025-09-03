# semana_models.py - Páginas e Models da Semana de Inovação
from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from enap_designsystem.blocks import SEMANA_INOVACAO_STREAMBLOCKS
from .semana_blocks import (
    BRAND_INOVACAO_CHOICES, 
    BRAND_TEXTS_CHOICES,
    BRAND_BG_CHOICES, 
    BRAND_BUTTON_CHOICES, 
    BRAND_HOVER_CHOICES
)

from .semana_blocks import (
    ImageBlock, ParticipanteBlock, StatBlock, GaleriaFotoBlock,
    FAQItemBlock, FAQTabBlock, AtividadeBlock, HospitalityCardBlock,
    VideoBlock, CertificadoBlock, NewsletterBlock, ContatoBlock, FooterBlock, BannerConcurso, MaterialApioBlock, SecaoPatrocinadoresBlock, SecaoApresentacaoBlock, SecaoCategoriasBlock, CronogramaBlock, SecaoPremiosBlock, SecaoFAQBlock, SecaoContatoBlock, MenuNavigationBlock, BannerResultadoBlock,
    PodcastSpotifyBlock,
    SecaoHeroBannerBlock,
    SecaoEstatisticasBlock,
    SecaoCardsBlock,
    SecaoTestemunhosBlock,
)


# =============================================================================
# SNIPPETS - COMPONENTES REUTILIZÁVEIS
# =============================================================================


@register_snippet
class EventInfo(models.Model):
    """Informações centralizadas do evento"""
    name = models.CharField("Nome do Evento", max_length=200, default="Semana de Inovação")
    year = models.CharField("Ano", max_length=4, default="2025")
    tagline = models.CharField("Slogan", max_length=300, default="O maior evento de inovação em governo da América Latina")
    
    # Datas
    start_date = models.DateField("Data de Início")
    end_date = models.DateField("Data de Fim")
    
    # Contatos
    contact_email = models.EmailField("Email de Contato", default="contato.si@enap.gov.br")
    
    # Redes sociais
    youtube_url = models.URLField("YouTube", blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    
    is_active = models.BooleanField("Configuração Ativa", default=True)

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('year'),
            FieldPanel('tagline'),
            FieldPanel('is_active'),
        ], heading="Informações Básicas"),
        
        MultiFieldPanel([
            FieldPanel('start_date'),
            FieldPanel('end_date'),
        ], heading="Datas do Evento"),
        
        MultiFieldPanel([
            FieldPanel('contact_email'),
        ], heading="Contatos"),
        
        MultiFieldPanel([
            FieldPanel('youtube_url'),
            FieldPanel('instagram_url'),
            FieldPanel('linkedin_url'),
        ], heading="Redes Sociais"),
    ]

    def save(self, *args, **kwargs):
        if self.is_active:
            EventInfo.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.year}"

    class Meta:
        verbose_name = "Informações do Evento"
        verbose_name_plural = "Informações do Evento"


@register_snippet
class SemanaNavigation(ClusterableModel):
    """Configuração da navegação global da Semana"""
    
    # Logo
    logo_stream = StreamField([
        ('logo_imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    logo_alt_text = models.CharField("Texto Alternativo do Logo", max_length=200, blank=True)
    
    # Links de navegação
    sobre_link = models.URLField("Link Sobre", blank=True)
    nossa_historia_link = models.URLField("Link Nossa História", blank=True)
    o_local_link = models.URLField("Link O Local", blank=True)
    programacao_link = models.URLField("Link Programação", blank=True)
    quem_vai_estar_la_link = models.URLField("Link Quem vai estar lá", blank=True)
    noticias_link = models.URLField("Link Notícias", blank=True)
    apoie_inovacao_link = models.URLField("Link Apoie a Inovação", blank=True)
    perguntas_frequentes_link = models.URLField("Link Perguntas Frequentes", blank=True)
    entenda_gamificacao_link = models.URLField("Link Entenda Gamificação", blank=True)
    
    # Seletor de idiomas
    mostrar_seletor_idiomas = models.BooleanField("Mostrar Seletor de Idiomas", default=True)
    pt_br_link = models.URLField("Link PT-BR", blank=True)
    en_link = models.URLField("Link EN", blank=True)
    es_link = models.URLField("Link ES", blank=True)
    
    # Busca
    mostrar_busca = models.BooleanField("Mostrar Busca", default=True)
    
    # CTA
    cta_texto = models.CharField("Texto do CTA", max_length=100, default="Inscreva-se")
    cta_link = models.URLField("Link do CTA", blank=True)
    
    # JavaScript personalizado
    javascript_personalizado = models.TextField("JavaScript Personalizado", blank=True)
    
    is_active = models.BooleanField("Configuração Ativa", default=True)

    panels = [
        MultiFieldPanel([
            FieldPanel('logo_stream'),
            FieldPanel('logo_alt_text'),
            FieldPanel('is_active'),
        ], heading="Logo"),
        
        MultiFieldPanel([
            FieldPanel('sobre_link'),
            FieldPanel('nossa_historia_link'),
            FieldPanel('o_local_link'),
            FieldPanel('programacao_link'),
            FieldPanel('quem_vai_estar_la_link'),
            FieldPanel('noticias_link'),
            FieldPanel('apoie_inovacao_link'),
            FieldPanel('perguntas_frequentes_link'),
            FieldPanel('entenda_gamificacao_link'),
        ], heading="Links de Navegação"),
        
        MultiFieldPanel([
            FieldPanel('mostrar_seletor_idiomas'),
            FieldPanel('pt_br_link'),
            FieldPanel('en_link'),
            FieldPanel('es_link'),
        ], heading="Seletor de Idiomas"),
        
        MultiFieldPanel([
            FieldPanel('mostrar_busca'),
        ], heading="Busca"),
        
        MultiFieldPanel([
            FieldPanel('cta_texto'),
            FieldPanel('cta_link'),
        ], heading="Call to Action"),
        
        MultiFieldPanel([
            FieldPanel('javascript_personalizado'),
        ], heading="JavaScript Personalizado"),
    ]

    def save(self, *args, **kwargs):
        if self.is_active:
            SemanaNavigation.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Navegação {'(Ativa)' if self.is_active else ''}"

    class Meta:
        verbose_name = "Configuração de Navegação"
        verbose_name_plural = "Configurações de Navegação"

@register_snippet
class SemanaFooterSnippet(ClusterableModel):
    """Footer reutilizável para a Semana de Inovação - Com Cores Customizáveis"""
    
    # Identificação
    name = models.CharField("Nome do Footer", max_length=100, default="Footer Principal")
    is_active = models.BooleanField("Footer Ativo", default=True)
    
    # Logo
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Logo"
    )
    logo_alt_text = models.CharField("Texto Alternativo do Logo", max_length=200, blank=True)
    logo_link = models.URLField("Link do Logo", blank=True)
    
    # Informações do evento
    ano_evento = models.CharField("Ano do Evento", max_length=10, default="2025")
    data_inicio = models.CharField("Data de Início", max_length=50, default="30 de Setembro")
    data_fim = models.CharField("Data de Fim", max_length=50, default="02 de Outubro")
    modalidade = models.CharField("Modalidade", max_length=100, default="Online e Presencial")
    
    # Tagline
    tagline = RichTextField(
        "Tagline do Evento", 
        blank=True,
        default="O maior evento de inovação em governo da América Latina",
        features=['bold', 'italic']
    )
    
    # ========================================================================
    # CORES CUSTOMIZÁVEIS - NOVOS CAMPOS
    # ========================================================================
    cor_fundo = models.CharField(
        "Cor de Fundo", 
        max_length=70, 
        choices=BRAND_BG_CHOICES,
        default="#132929",
        help_text="Cor de fundo do footer"
    )
    cor_texto_principal = models.CharField(
        "Cor do Texto Principal", 
        max_length=70, 
        choices=BRAND_INOVACAO_CHOICES,
        default="#FFFFFF",
        help_text="Cor dos títulos e textos principais",
    )
    cor_texto_secundario = models.CharField(
        "Cor do Texto Secundário", 
        max_length=70, 
        choices=BRAND_INOVACAO_CHOICES,
        default="#B0C4DE",
        help_text="Cor dos textos secundários e descrições"
    )
    cor_links = models.CharField(
        "Cor dos Links", 
        max_length=70, 
        choices=BRAND_BUTTON_CHOICES,
        default="#FFEB31",
        help_text="Cor dos links e ícones das redes sociais"
    )
    cor_links_hover = models.CharField(
        "Cor dos Links (Hover)", 
        max_length=70, 
        choices=BRAND_HOVER_CHOICES,
        default="#E6D220",
        help_text="Cor dos links ao passar o mouse"
    )
    cor_icones_social = models.CharField(
        "Cor dos Ícones Sociais", 
        max_length=70, 
        choices=BRAND_BUTTON_CHOICES,
        default="#FFEB31",
        help_text="Cor específica dos ícones das redes sociais"
    )
    
    # Redes sociais
    youtube_url = models.URLField("YouTube", blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    twitter_url = models.URLField("Twitter/X", blank=True)
    facebook_url = models.URLField("Facebook", blank=True)
    tiktok_url = models.URLField("TikTok", blank=True)
    
    # Contato
    titulo_contato = models.CharField("Título da Seção de Contato", max_length=100, default="Entre em contato")
    texto_contato = models.TextField("Texto de Contato", blank=True, default="Fale com nosso time")
    email_contato = models.EmailField("Email de Contato", blank=True, default="semanainovacao@enap.gov.br")
    telefone_contato = models.CharField("Telefone", max_length=20, blank=True)
    
    # Copyright
    texto_copyright = models.CharField(
        "Texto do Copyright", 
        max_length=200, 
        blank=True,
        default="© 2025 ENAP - Escola Nacional de Administração Pública. Todos os direitos reservados."
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('is_active'),
        ], heading="🏷️ Identificação"),
        
        MultiFieldPanel([
            FieldPanel('logo'),
            FieldPanel('logo_alt_text'),
            FieldPanel('logo_link'),
        ], heading="🎨 Logo"),
        
        MultiFieldPanel([
            FieldPanel('ano_evento'),
            FieldPanel('data_inicio'),
            FieldPanel('data_fim'),
            FieldPanel('modalidade'),
            FieldPanel('tagline'),
        ], heading="📅 Informações do Evento"),
        
        # ========================================================================
        # NOVA SEÇÃO DE CORES
        # ========================================================================
        MultiFieldPanel([
            FieldPanel('cor_fundo'),
            FieldPanel('cor_texto_principal'),
            FieldPanel('cor_texto_secundario'),
            FieldPanel('cor_links'),
            FieldPanel('cor_links_hover'),
            FieldPanel('cor_icones_social'),
        ], heading="🎨 Cores Personalizadas"),
        
        MultiFieldPanel([
            FieldPanel('youtube_url'),
            FieldPanel('instagram_url'),
            FieldPanel('linkedin_url'),
            FieldPanel('twitter_url'),
            FieldPanel('facebook_url'),
            FieldPanel('tiktok_url'),
        ], heading="🌐 Redes Sociais"),
        
        MultiFieldPanel([
            FieldPanel('titulo_contato'),
            FieldPanel('texto_contato'),
            FieldPanel('email_contato'),
            FieldPanel('telefone_contato'),
        ], heading="📞 Contato"),
        
        InlinePanel('footer_columns', label="Colunas de Links"),
        
        FieldPanel('texto_copyright'),
    ]

    def save(self, *args, **kwargs):
        if self.is_active:
            SemanaFooterSnippet.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {'(Ativo)' if self.is_active else ''}"

    class Meta:
        verbose_name = "Footer da Semana"
        verbose_name_plural = "Footers da Semana"


# FooterColumn permanece igual
class FooterColumn(Orderable):
    """Colunas de links do footer"""
    
    footer = ParentalKey(
        SemanaFooterSnippet,
        on_delete=models.CASCADE,
        related_name='footer_columns'
    )
    
    titulo = models.CharField("Título da Coluna", max_length=100)
    
    # Links da coluna usando StreamField
    links = StreamField([
        ('link', blocks.StructBlock([
            ('texto', blocks.CharBlock(max_length=100, label="Texto do Link")),
            ('url', blocks.URLBlock(required=False, label="URL Externa")),
            ('pagina_interna', blocks.PageChooserBlock(required=False, label="Página Interna")),
            ('abrir_nova_aba', blocks.BooleanBlock(required=False, default=False, label="Abrir em Nova Aba")),
        ], icon='link', label='Link')),
    ], use_json_field=True, blank=True)

    panels = [
        FieldPanel('titulo'),
        FieldPanel('links'),
    ]

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Coluna do Footer"
        verbose_name_plural = "Colunas do Footer"


# =============================================================================
# PÁGINAS PRINCIPAIS
# =============================================================================


class SemanaHomePage(Page):
    """Página inicial da Semana de Inovação - PÁGINA PRINCIPAL"""
    
    # ========================================================================
    # SEÇÃO BANNER/HERO
    # ========================================================================

    body_semana = StreamField(
		SEMANA_INOVACAO_STREAMBLOCKS,
		null=True,
		blank=True,
		use_json_field=True,
	)

    banner_titulo = RichTextField("Título do Banner", blank=True)
    banner_subtitulo = models.CharField("Subtítulo do Banner", max_length=200, blank=True)
    banner_texto_botao = models.CharField("Texto do Botão", max_length=100, default="Saiba mais")
    logo_hero_stream = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    logo_hero_link = models.URLField("Link do Logo Hero", blank=True)
    banner_imagem = StreamField([
        ('banner_imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    
    # 🎨 CORES DO BANNER
    banner_cor_fundo = models.CharField("Cor de Fundo do Banner", max_length=7, default="#4A9AA8", help_text="Ex: #4A9AA8")
    banner_cor_texto = models.CharField("Cor do Texto do Banner", max_length=7, default="#FFFFFF", help_text="Ex: #FFFFFF")
    banner_cor_botao = models.CharField("Cor do Botão", max_length=7, default="#1ECD71", help_text="Ex: #FFEA05")
    
    # ========================================================================
    # SEÇÃO DE DESTAQUES
    # ========================================================================
    destaques_titulo = models.CharField("Título dos Destaques", max_length=200, default="Participantes em Destaque")
    participantes_destaques = StreamField([
        ('participante', ParticipanteBlock()),
    ], blank=True, use_json_field=True)
    
    # 🎨 CORES DOS DESTAQUES
    destaques_cor_fundo = models.CharField("Cor de Fundo dos Destaques", max_length=7, default="#1a2e38", help_text="Ex: #1a2e38")
    destaques_cor_texto = models.CharField("Cor do Texto dos Destaques", max_length=7, default="#FFFFFF", help_text="Ex: #FFFFFF")
    destaques_cor_destaque = models.CharField("Cor de Destaque", max_length=7, default="#8B951C", help_text="Ex: #8B951C")
    
    # ========================================================================
    # SEÇÃO DE VÍDEO
    # ========================================================================
    video_titulo = models.CharField("Título do Vídeo", max_length=200, default="Assista ao vídeo")
    video_url = models.URLField("URL do Vídeo", blank=True)
    
    # 🎨 CORES DO VÍDEO
    video_cor_fundo = models.CharField("Cor de Fundo do Vídeo", max_length=7, default="#4A9AA8", help_text="Ex: #4A9AA8")
    video_cor_texto = models.CharField("Cor do Texto do Vídeo", max_length=7, default="#FFFFFF", help_text="Ex: #FFFFFF")
    
    # ========================================================================
    # SEÇÃO DE NÚMEROS/ESTATÍSTICAS
    # ========================================================================
    numeros_stats = StreamField([
        ('stat', StatBlock()),
    ], blank=True, use_json_field=True)
    
    # 🎨 CORES DOS NÚMEROS
    numeros_cor_fundo = models.CharField("Cor de Fundo dos Números", max_length=7, default="#EEEEEE", help_text="Ex: #EEEEEE")
    numeros_cor_texto = models.CharField("Cor do Texto dos Números", max_length=7, default="#333333", help_text="Ex: #333333")
    numeros_cor_numero = models.CharField("Cor dos Números", max_length=7, default="#163841", help_text="Ex: #163841")
    
    # ========================================================================
    # SEÇÃO DE CERTIFICADO
    # ========================================================================
    certificado_titulo = models.CharField("Título do Certificado", max_length=200, blank=True)
    certificado_texto = RichTextField("Texto do Certificado", blank=True)
    certificado_texto_botao = models.CharField("Texto do Botão", max_length=100, default="Baixar certificado")
    certificado_imagem = StreamField([
        ('certificado_imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    
    # 🎨 CORES DO CERTIFICADO
    certificado_cor_fundo = models.CharField("Cor de Fundo do Certificado", max_length=7, default="#2B5E2B", help_text="Ex: #2B5E2B")
    certificado_cor_texto = models.CharField("Cor do Texto do Certificado", max_length=7, default="#FFFFFF", help_text="Ex: #FFFFFF")
    certificado_cor_botao = models.CharField("Cor do Botão do Certificado", max_length=7, default="#FFEA05", help_text="Ex: #FFEA05")
    
    # ========================================================================
    # SEÇÃO DE GALERIA
    # ========================================================================
    galeria_titulo = models.CharField("Título da Galeria", max_length=200, default="Galeria")
    galeria_subtitulo = models.CharField("Subtítulo da Galeria", max_length=300, blank=True)
    galeria_stream = StreamField([
        ('foto', GaleriaFotoBlock()),
    ], blank=True, use_json_field=True)
    
    # 🎨 CORES DA GALERIA
    galeria_cor_fundo = models.CharField("Cor de Fundo da Galeria", max_length=7, default="#1a2e38", help_text="Ex: #1a2e38")
    galeria_cor_texto = models.CharField("Cor do Texto da Galeria", max_length=7, default="#FFFFFF", help_text="Ex: #FFFFFF")
    
    # ========================================================================
    # NEWSLETTER
    # ========================================================================
    newsletter_stream = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    
    # 🎨 CORES DA NEWSLETTER
    newsletter_cor_fundo = models.CharField("Cor de Fundo da Newsletter", max_length=7, default="#EEEEEE", help_text="Ex: #EEEEEE")
    newsletter_cor_texto = models.CharField("Cor do Texto da Newsletter", max_length=7, default="#333333", help_text="Ex: #333333")
    newsletter_cor_botao = models.CharField("Cor do Botão da Newsletter", max_length=7, default="#163841", help_text="Ex: #163841")
    
    # ========================================================================
    # CONTATO
    # ========================================================================
    # 🎨 CORES DO CONTATO
    contato_cor_fundo = models.CharField("Cor de Fundo do Contato", max_length=7, default="#4A9AA8", help_text="Ex: #4A9AA8")
    contato_cor_texto = models.CharField("Cor do Texto do Contato", max_length=7, default="#FFFFFF", help_text="Ex: #FFFFFF")
    contato_cor_botao = models.CharField("Cor do Botão do Contato", max_length=7, default="#FFEA05", help_text="Ex: #FFEA05")
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    footer_stream = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    
    # 🎨 CORES DO FOOTER
    footer_cor_fundo = models.CharField("Cor de Fundo do Footer", max_length=7, default="#163841", help_text="Ex: #163841")
    footer_cor_texto = models.CharField("Cor do Texto do Footer", max_length=7, default="#FFFFFF", help_text="Ex: #FFFFFF")
    footer_cor_link = models.CharField("Cor dos Links do Footer", max_length=7, default="#FFEA05", help_text="Ex: #FFEA05")

    template = 'enap_designsystem/semana_inovacao/home.html'
    
    # 🎯 CONFIGURAÇÃO FUNDAMENTAL: Permite apenas páginas filhas específicas
    subpage_types = [
        'enap_designsystem.SemanaFAQPage',
        'enap_designsystem.SemanaProgramacaoPage', 
        'enap_designsystem.SemanaParticipantesPage',
        'enap_designsystem.SemanaLocalPage',
        'enap_designsystem.SemanaPatrocinadoresPage',
    ]

    content_panels = Page.content_panels + [
        # ========================================================================
        # SEÇÃO BANNER
        # ========================================================================
        MultiFieldPanel([
            FieldPanel('body_semana'),
            FieldPanel('banner_titulo'),
            FieldPanel('banner_subtitulo'),
            FieldPanel('banner_texto_botao'),
            FieldPanel('logo_hero_stream'),
            FieldPanel('logo_hero_link'),
            FieldPanel('banner_imagem'),
        ], heading="📸 Conteúdo do Banner"),
        
        MultiFieldPanel([
            FieldPanel('banner_cor_fundo'),
            FieldPanel('banner_cor_texto'),
            FieldPanel('banner_cor_botao'),
        ], heading="🎨 Cores do Banner"),
        
        # ========================================================================
        # SEÇÃO DESTAQUES
        # ========================================================================
        MultiFieldPanel([
            FieldPanel('destaques_titulo'),
            FieldPanel('participantes_destaques'),
        ], heading="👥 Conteúdo dos Destaques"),
        
        MultiFieldPanel([
            FieldPanel('destaques_cor_fundo'),
            FieldPanel('destaques_cor_texto'),
            FieldPanel('destaques_cor_destaque'),
        ], heading="🎨 Cores dos Destaques"),
        
        # ========================================================================
        # SEÇÃO VÍDEO
        # ========================================================================
        MultiFieldPanel([
            FieldPanel('video_titulo'),
            FieldPanel('video_url'),
        ], heading="🎬 Conteúdo do Vídeo"),
        
        MultiFieldPanel([
            FieldPanel('video_cor_fundo'),
            FieldPanel('video_cor_texto'),
        ], heading="🎨 Cores do Vídeo"),
        
        # ========================================================================
        # SEÇÃO NÚMEROS
        # ========================================================================
        MultiFieldPanel([
            FieldPanel('numeros_stats'),
        ], heading="📊 Conteúdo dos Números"),
        
        MultiFieldPanel([
            FieldPanel('numeros_cor_fundo'),
            FieldPanel('numeros_cor_texto'),
            FieldPanel('numeros_cor_numero'),
        ], heading="🎨 Cores dos Números"),
        
        # ========================================================================
        # SEÇÃO CERTIFICADO
        # ========================================================================
        MultiFieldPanel([
            FieldPanel('certificado_titulo'),
            FieldPanel('certificado_texto'),
            FieldPanel('certificado_texto_botao'),
            FieldPanel('certificado_imagem'),
        ], heading="🏆 Conteúdo do Certificado"),
        
        MultiFieldPanel([
            FieldPanel('certificado_cor_fundo'),
            FieldPanel('certificado_cor_texto'),
            FieldPanel('certificado_cor_botao'),
        ], heading="🎨 Cores do Certificado"),
        
        # ========================================================================
        # SEÇÃO GALERIA
        # ========================================================================
        MultiFieldPanel([
            FieldPanel('galeria_titulo'),
            FieldPanel('galeria_subtitulo'),
            FieldPanel('galeria_stream'),
        ], heading="🖼️ Conteúdo da Galeria"),
        
        MultiFieldPanel([
            FieldPanel('galeria_cor_fundo'),
            FieldPanel('galeria_cor_texto'),
        ], heading="🎨 Cores da Galeria"),
        
        # ========================================================================
        # NEWSLETTER
        # ========================================================================
        MultiFieldPanel([
            FieldPanel('newsletter_stream'),
        ], heading="📧 Conteúdo da Newsletter"),
        
        MultiFieldPanel([
            FieldPanel('newsletter_cor_fundo'),
            FieldPanel('newsletter_cor_texto'),
            FieldPanel('newsletter_cor_botao'),
        ], heading="🎨 Cores da Newsletter"),
        
        # ========================================================================
        # CONTATO
        # ========================================================================
        MultiFieldPanel([
            FieldPanel('contato_cor_fundo'),
            FieldPanel('contato_cor_texto'),
            FieldPanel('contato_cor_botao'),
        ], heading="🎨 Cores do Contato"),
        
        # ========================================================================
        # FOOTER
        # ========================================================================
        MultiFieldPanel([
            FieldPanel('footer_stream'),
        ], heading="🔗 Conteúdo do Footer"),
        
        MultiFieldPanel([
            FieldPanel('footer_cor_fundo'),
            FieldPanel('footer_cor_texto'),
            FieldPanel('footer_cor_link'),
        ], heading="🎨 Cores do Footer"),
    ]

    def save(self, *args, **kwargs):
        """Criar páginas filhas automaticamente quando a página for salva pela primeira vez"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.create_child_pages()

    def create_child_pages(self):
        """Criar todas as páginas filhas automaticamente"""
        from django.utils.text import slugify
        
        # Lista de páginas filhas para criar
        child_pages_data = [
            {
                'model': SemanaFAQPage,
                'title': 'Perguntas Frequentes',
                'slug': 'faq',
                'extra_data': {
                    'intro_title': 'Perguntas',
                    'intro_subtitle': 'Frequentes'
                }
            },
            {
                'model': SemanaProgramacaoPage,
                'title': 'Programação',
                'slug': 'programacao',
                'extra_data': {}
            },
            {
                'model': SemanaParticipantesPage,
                'title': 'Participantes',
                'slug': 'participantes',
                'extra_data': {
                    'subtitulo': 'SI 2024',
                    'titulo': 'Participantes'
                }
            },
            {
                'model': SemanaLocalPage,
                'title': 'O Local',
                'slug': 'local',
                'extra_data': {
                    'enap_title': 'ENAP',
                    'hospitality_title': 'Hospitalidade',
                    'directions_title': 'Como Chegar'
                }
            },
            {
                'model': SemanaPatrocinadoresPage,
                'title': 'Patrocinadores',
                'slug': 'patrocinadores',
                'extra_data': {
                    'titulo': 'Nossos Patrocinadores'
                }
            },
        ]
        
        for page_data in child_pages_data:
            # Verificar se a página já existe
            if not self.get_children().filter(slug=page_data['slug']).exists():
                # Criar nova página filha
                child_page = page_data['model'](
                    title=page_data['title'],
                    slug=page_data['slug'],
                    **page_data['extra_data']
                )
                
                # Adicionar como filha
                self.add_child(instance=child_page)
                
                # Publicar automaticamente
                child_page.save_revision().publish()

    def get_participantes_destaques(self):
        """Retorna os participantes em destaque"""
        return self.participantes_destaques

    class Meta:
        verbose_name = "Semana de Inovação - Site Principal"
        verbose_name_plural = "Semana de Inovação - Sites"




        
# =============================================================================
# PÁGINAS FILHAS (SÓ PODEM SER CRIADAS COMO FILHAS DA HOME)
# =============================================================================

class SemanaFAQPage(Page):
    """Página de Perguntas Frequentes"""
    
    intro_title = models.CharField("Título de Introdução", max_length=200, default="Perguntas")
    intro_subtitle = models.CharField("Subtítulo de Introdução", max_length=200, default="Frequentes")
    
    faq_tabs = StreamField([
        ('faq_tab', FAQTabBlock()),
    ], use_json_field=True)

    template = 'enap_designsystem/semana_inovacao/faq_semana.html'
    
    # 🎯 CONFIGURAÇÃO: Só pode ser filha da SemanaHomePage
    parent_page_types = ['enap_designsystem.SemanaHomePage']
    subpage_types = []  # Não permite filhas

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('intro_title'),
            FieldPanel('intro_subtitle'),
        ], heading="Introdução"),
        
        FieldPanel('faq_tabs'),
    ]

    class Meta:
        verbose_name = "FAQ da Semana"


class SemanaProgramacaoPage(Page):
    """Página de Programação"""
    
    # Atividades organizadas por data
    atividades = StreamField([
        ('atividade', AtividadeBlock()),
    ], use_json_field=True)

    template = 'enap_designsystem/semana_inovacao/programacao_semana.html'
    
    # 🎯 CONFIGURAÇÃO: Só pode ser filha da SemanaHomePage
    parent_page_types = ['enap_designsystem.SemanaHomePage']
    subpage_types = []  # Não permite filhas

    content_panels = Page.content_panels + [
        FieldPanel('atividades'),
    ]
    
    def get_atividades_por_data(self):
        """Retorna atividades organizadas por data"""
        atividades_dict = {}
        for block in self.atividades:
            if block.block_type == 'atividade':
                data = block.value['data']
                if data not in atividades_dict:
                    atividades_dict[data] = []
                atividades_dict[data].append(block.value)
        return atividades_dict
    
    def get_atividades_online(self):
        """Retorna apenas atividades online"""
        return [block.value for block in self.atividades if block.value.get('tipo') == 'online']
    
    def get_atividades_presenciais(self):
        """Retorna apenas atividades presenciais"""
        return [block.value for block in self.atividades if block.value.get('tipo') == 'presencial']

    class Meta:
        verbose_name = "Programação da Semana"


class SemanaParticipantesPage(Page):
    """Página de Participantes"""
    
    subtitulo = models.CharField("Subtítulo", max_length=200, default="SI 2024")
    titulo = models.CharField("Título", max_length=200, default="Participantes")
    introducao = RichTextField("Introdução", blank=True)
    
    participantes_stream = StreamField([
        ('participante', ParticipanteBlock()),
    ], use_json_field=True)
    
    # Newsletter (reutilizada)
    newsletter_stream = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    
    # Footer (reutilizado)
    footer_stream = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)

    template = 'enap_designsystem/semana_inovacao/participantes.html'
    
    # 🎯 CONFIGURAÇÃO: Só pode ser filha da SemanaHomePage
    parent_page_types = ['enap_designsystem.SemanaHomePage']
    subpage_types = []  # Não permite filhas

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('subtitulo'),
            FieldPanel('titulo'),
            FieldPanel('introducao'),
        ], heading="Cabeçalho"),
        
        FieldPanel('participantes_stream'),
        
        MultiFieldPanel([
            FieldPanel('newsletter_stream'),
            FieldPanel('footer_stream'),
        ], heading="Newsletter e Footer"),
    ]

    class Meta:
        verbose_name = "Participantes da Semana"


class SemanaLocalPage(Page):
    """Página O Local"""
    
    # Seção ENAP
    enap_image = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    enap_title = models.CharField("Título ENAP", max_length=200, default="ENAP")
    enap_description = RichTextField("Descrição ENAP", blank=True)
    
    # Seção Hospitalidade
    hospitality_title = models.CharField("Título Hospitalidade", max_length=200, default="Hospitalidade")
    hospitality_cards = StreamField([
        ('card', HospitalityCardBlock()),
    ], blank=True, use_json_field=True)
    
    # Seção Como Chegar
    directions_title = models.CharField("Título Como Chegar", max_length=200, default="Como Chegar")
    
    # Transporte - Metrô
    metro_title = models.CharField("Título Metrô", max_length=100, default="Metrô")
    metro_text = models.TextField("Texto Metrô", blank=True)
    
    # Transporte - Táxi
    taxi_title = models.CharField("Título Táxi", max_length=100, default="Táxi")
    taxi_text = models.TextField("Texto Táxi", blank=True)
    
    # Transporte - Ônibus
    bus_title = models.CharField("Título Ônibus", max_length=100, default="Ônibus")
    bus_text = models.TextField("Texto Ônibus", blank=True)
    
    # Transporte - Especial
    special_title = models.CharField("Título Especial", max_length=100, default="Transporte Especial")
    special_text = models.TextField("Texto Especial", blank=True)
    
    # Mapa
    map_image = StreamField([
    ('imagem', ImageBlock()),
    ], 
    use_json_field=True,
    blank=True,
    null=True,
    verbose_name="Imagem do Mapa"
    )
    template = 'enap_designsystem/semana_inovacao/local.html'
    
    # 🎯 CONFIGURAÇÃO: Só pode ser filha da SemanaHomePage
    parent_page_types = ['enap_designsystem.SemanaHomePage']
    subpage_types = []  # Não permite filhas

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('enap_image'),
            FieldPanel('enap_title'),
            FieldPanel('enap_description'),
        ], heading="Seção ENAP"),
        
        MultiFieldPanel([
            FieldPanel('hospitality_title'),
            FieldPanel('hospitality_cards'),
        ], heading="Seção Hospitalidade"),
        
        MultiFieldPanel([
            FieldPanel('directions_title'),
        ], heading="Como Chegar"),
        
        MultiFieldPanel([
            FieldPanel('metro_title'),
            FieldPanel('metro_text'),
        ], heading="Transporte - Metrô"),
        
        MultiFieldPanel([
            FieldPanel('taxi_title'),
            FieldPanel('taxi_text'),
        ], heading="Transporte - Táxi"),
        
        MultiFieldPanel([
            FieldPanel('bus_title'),
            FieldPanel('bus_text'),
        ], heading="Transporte - Ônibus"),
        
        MultiFieldPanel([
            FieldPanel('special_title'),
            FieldPanel('special_text'),
        ], heading="Transporte Especial"),
        
        FieldPanel('map_image'),
    ]

    class Meta:
        verbose_name = "O Local da Semana"


class SemanaPatrocinadoresPage(Page):
    """Página de Patrocinadores"""
    
    titulo = models.CharField("Título", max_length=200, default="Nossos Patrocinadores")
    
    patrocinadores = StreamField([
        ('patrocinador', ImageBlock()),
    ], use_json_field=True)

    template = 'enap_designsystem/semana_inovacao/patrocinadores.html'
    
    # 🎯 CONFIGURAÇÃO: Só pode ser filha da SemanaHomePage
    parent_page_types = ['enap_designsystem.SemanaHomePage']
    subpage_types = []  # Não permite filhas

    content_panels = Page.content_panels + [
        FieldPanel('titulo'),
        FieldPanel('patrocinadores'),
    ]

    class Meta:
        verbose_name = "Patrocinadores da Semana"



# =============================================================================
# CONCURSO DE INOVAÇÃO 
# =============================================================================

class EditalConcursoInovacao(Page):
    """PÁGINA PAI - Edital do Concurso de Inovação"""

    template = 'enap_designsystem/semana_inovacao/edital_concurso_inovacao.html'

    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

   
    menu_navegacao = StreamField([
        ('menu_navigation', MenuNavigationBlock()),
    ], use_json_field=True, max_num=1, blank=True, default=list, 
    help_text="Menu que aparecerá em todas as páginas do concurso")

    banner = StreamField([
        ('banner_concurso', BannerConcurso()),
    ], use_json_field=True, max_num=1)
    
    apresentacao = StreamField([
        ('secao_apresentacao', SecaoApresentacaoBlock()),
    ], use_json_field=True, blank=True)

    section_explica = StreamField([
        ('section_explica', SecaoCategoriasBlock()),
    ], use_json_field=True, blank=True)

    publico_alvo = StreamField([
        ('secao_apresentacao', SecaoApresentacaoBlock()),
    ], use_json_field=True, blank=True)

    cronograma = StreamField([
        ('cronograma', CronogramaBlock()),
    ], use_json_field=True, blank=True)

    premios = StreamField([
        ('premios', SecaoPremiosBlock()),
    ], use_json_field=True, blank=True)

    faq_block = StreamField([
        ('faq_block', SecaoFAQBlock()),
    ], use_json_field=True, blank=True)

    contato = StreamField([
        ('secao_contato', SecaoContatoBlock()),
    ], use_json_field=True, blank=True)

    patrocinadores = StreamField([
        ('patrocinadores', SecaoPatrocinadoresBlock()),
    ], use_json_field=True, blank=True, default=list) 

    footer = models.ForeignKey(
        "EnapFooterSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('navbar'),
        FieldPanel('menu_navegacao'),  
        FieldPanel('banner'),
        FieldPanel('apresentacao'),
        FieldPanel('section_explica'),
        FieldPanel('publico_alvo'),
        FieldPanel('cronograma'),
        FieldPanel('premios'),
        FieldPanel('faq_block'),
        FieldPanel('contato'),
        FieldPanel('patrocinadores'),
        FieldPanel('footer'),
    ]
    

    subpage_types = [
        'enap_designsystem.ConcursoInovacao',
        'enap_designsystem.SejaAvaliador',
        'enap_designsystem.ENAPComponentes',
        'enap_designsystem.ENAPSemana',
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Disponibilizar o menu para o template
        context['menu_concurso'] = self.menu_navegacao
        return context

    def save(self, *args, **kwargs):
        """Criar páginas filhas automaticamente quando a página é criada"""
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        if is_new:
            try:
                self.create_child_pages()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erro ao criar páginas filhas para {self.title}: {e}")

    def create_child_pages(self):
        """Criar as páginas filhas automaticamente"""
        try:
            # Verificar se as páginas filhas já existem
            concurso_exists = ConcursoInovacao.objects.child_of(self).exists()
            avaliador_exists = SejaAvaliador.objects.child_of(self).exists()
            
            # Criar página Concurso se não existir
            if not concurso_exists:
                concurso = ConcursoInovacao(
                    title=f"{self.title} - Concurso",
                    slug=f"{self.slug}-concurso",
                    # Herdar configurações da página pai
                    navbar=self.navbar,
                    footer=self.footer,
                )
                self.add_child(instance=concurso)
                concurso.save_revision().publish()
            
            # Criar página Seja Avaliador se não existir
            if not avaliador_exists:
                avaliador = SejaAvaliador(
                    title=f"{self.title} - Seja Avaliador", 
                    slug=f"{self.slug}-seja-avaliador",
                    # Herdar configurações da página pai
                    navbar=self.navbar,
                    footer=self.footer,
                )
                self.add_child(instance=avaliador)
                avaliador.save_revision().publish()
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro específico na criação de páginas filhas: {e}")
            raise

    class Meta:
        verbose_name = "Concurso de inovação - Home"
        verbose_name_plural = "Concursos de inovação - Home"


class ConcursoInovacao(Page):
    """PÁGINA FILHA - Página principal do concurso"""

    template = 'enap_designsystem/semana_inovacao/concurso_inovacao.html'

    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    banner = StreamField([
        ('banner_concurso', BannerConcurso()),
    ], use_json_field=True, max_num=1)
    
    material = StreamField([
        ('material_apoio', MaterialApioBlock()),
    ], use_json_field=True, blank=True)

    patrocinadores = StreamField([
        ('patrocinadores', SecaoPatrocinadoresBlock()),
    ], use_json_field=True, blank=True, default=list) 

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
        FieldPanel('material'),
        FieldPanel('patrocinadores'),
        FieldPanel('footer'),
    ]


    parent_page_types = ['enap_designsystem.EditalConcursoInovacao']

  
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Pegar menu da página pai (Edital)
        parent_page = self.get_parent().specific
        if hasattr(parent_page, 'menu_navegacao'):
            context['menu_concurso'] = parent_page.menu_navegacao
        return context

    class Meta:
        verbose_name = "Concursos de inovação - Edital"
        verbose_name_plural = "Concursos de inovação - Edital"


class SejaAvaliador(Page):
    """PÁGINA FILHA - Seja Avaliador"""

    template = 'enap_designsystem/semana_inovacao/seja_avaliador.html'

    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    banner = StreamField([
        ('banner_concurso', BannerConcurso()),
    ], use_json_field=True, max_num=1)
    
    material = StreamField([
        ('material_apoio', MaterialApioBlock()),
    ], use_json_field=True, blank=True)

    cronograma = StreamField([
        ('cronograma', CronogramaBlock()),
    ], use_json_field=True, blank=True)

    patrocinadores = StreamField([
        ('patrocinadores', SecaoPatrocinadoresBlock()),
    ], use_json_field=True, blank=True, default=list) 

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
        FieldPanel('material'),
        FieldPanel('cronograma'),
        FieldPanel('patrocinadores'),
        FieldPanel('footer'),
    ]


    parent_page_types = ['enap_designsystem.EditalConcursoInovacao']
    

    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Pegar menu da página pai (Edital)
        parent_page = self.get_parent().specific
        if hasattr(parent_page, 'menu_navegacao'):
            context['menu_concurso'] = parent_page.menu_navegacao
        return context

    class Meta:
        verbose_name = "Concurso de inovação - Seja Avaliador"
        verbose_name_plural = "Concurso de inovação - Seja Avaliador"