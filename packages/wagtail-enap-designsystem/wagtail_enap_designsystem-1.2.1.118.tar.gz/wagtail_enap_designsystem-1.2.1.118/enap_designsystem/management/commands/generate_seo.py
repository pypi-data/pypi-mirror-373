# enap_designsystem/management/commands/generate_seo.py

import re
from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from django.db import transaction
from wagtail.models import Page

class Command(BaseCommand):
    help = 'Gera meta descriptions e títulos SEO automaticamente para páginas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem alterar nada',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Sobrescreve campos SEO existentes',
        )
        parser.add_argument(
            '--page-type',
            type=str,
            help='Processa apenas páginas de um tipo específico (ex: ENAPService)',
        )
        parser.add_argument(
            '--exclude-test',
            action='store_true',
            default=True,
            help='Exclui páginas de teste (padrão: True)',
        )
        parser.add_argument(
            '--live-only',
            action='store_true',
            default=True,
            help='Processa apenas páginas publicadas (padrão: True)',
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.force = options['force']
        self.page_type = options['page_type']
        self.exclude_test = options['exclude_test']
        self.live_only = options['live_only']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODO DRY-RUN - Nenhuma alteração será feita\n')
            )
        
        self.process_pages()
    
    def process_pages(self):
        """Processa páginas com filtros de produção"""
        
        # Busca páginas base
        if self.live_only:
            queryset = Page.objects.live()
        else:
            queryset = Page.objects.all()
        
        # Exclui página raiz básica
        queryset = queryset.exclude(content_type__model='page')
        
        # Exclui páginas de teste se solicitado
        if self.exclude_test:
            test_patterns = [
                'root', 'home v1', '001', 'py ', 'teste', 'container',
                'title', 'joooma', 'dfdfsvdsv', 'ultima', 'migrate'
            ]
            for pattern in test_patterns:
                queryset = queryset.exclude(title__icontains=pattern)
        
        # Filtro por tipo específico
        if self.page_type:
            queryset = queryset.filter(content_type__model=self.page_type.lower())
        
        pages = queryset.specific()
        total_pages = pages.count()
        
        if total_pages == 0:
            self.stdout.write(
                self.style.WARNING('⚠️  Nenhuma página encontrada com os filtros aplicados')
            )
            return
        
        self.stdout.write(f'📄 Processando {total_pages} páginas...\n')
        
        # Contadores
        updated = 0
        errors = 0
        skipped = 0
        
        for page in pages:
            try:
                result = self.process_single_page(page)
                if result == 'updated':
                    updated += 1
                elif result == 'skipped':
                    skipped += 1
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro em {page.title}: {e}')
                )
        
        self.print_summary(updated, skipped, errors, total_pages)
    
    def process_single_page(self, page):
        """Processa uma página individual"""
        
        changes = []
        needs_update = False
        
        # Processa search_description (campo padrão do Wagtail)
        if hasattr(page, 'search_description'):
            current = getattr(page, 'search_description', '') or ''
            if not current.strip() or self.force:
                new_value = self.generate_meta_description(page)
                if new_value != current:
                    changes.append(('search_description', current, new_value))
                    if not self.dry_run:
                        page.search_description = new_value
                    needs_update = True
        
        # Processa meta_description customizada (se existir)
        if hasattr(page, 'meta_description'):
            current = getattr(page, 'meta_description', '') or ''
            if not current.strip() or self.force:
                new_value = self.generate_meta_description(page)
                if new_value != current:
                    changes.append(('meta_description', current, new_value))
                    if not self.dry_run:
                        page.meta_description = new_value
                    needs_update = True
        
        # Processa seo_title customizado (se existir)
        if hasattr(page, 'seo_title'):
            current = getattr(page, 'seo_title', '') or ''
            if not current.strip() or self.force:
                new_value = self.generate_seo_title(page)
                if new_value != current:
                    changes.append(('seo_title', current, new_value))
                    if not self.dry_run:
                        page.seo_title = new_value
                    needs_update = True
        
        # Salva mudanças
        if needs_update and not self.dry_run:
            try:
                with transaction.atomic():
                    page.save()
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao salvar {page.title}: {e}')
                )
                return 'error'
        
        # Log das mudanças
        if changes:
            self.log_page_changes(page, changes)
            return 'updated'
        
        return 'skipped'
    
    def log_page_changes(self, page, changes):
        """Registra mudanças no log"""
        self.stdout.write(f'📝 {page.title} ({page.__class__.__name__})')
        self.stdout.write(f'   🔗 URL: {page.url or "N/A"}')
        
        for field, old_value, new_value in changes:
            # Trunca valores longos para exibição
            old_display = (old_value[:47] + '...') if len(old_value) > 50 else old_value
            new_display = (new_value[:47] + '...') if len(new_value) > 50 else new_value
            
            self.stdout.write(f'   📋 {field}:')
            self.stdout.write(f'      Antes: "{old_display}"')
            self.stdout.write(f'      Depois: "{new_display}"')
        
        self.stdout.write('')  # Linha em branco
    
    def generate_seo_title(self, page):
        """Gera título SEO otimizado (máx 60 chars)"""
        title = page.title
        
        # Remove caracteres especiais e normaliza espaços
        title = re.sub(r'[^\w\s\-áéíóúâêîôûàèìòùãõçÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Trunca preservando palavras
        if len(title) > 60:
            words = title[:57].split()
            if len(words) > 1:
                title = ' '.join(words[:-1]) + '...'
            else:
                title = title[:57] + '...'
        
        return title
    
    def generate_meta_description(self, page):
        """Gera meta description inteligente"""
        
        # Campos prioritários para extração de conteúdo
        content_fields = ['introduction', 'summary', 'excerpt', 'body', 'content']
        
        # Tenta extrair conteúdo dos campos
        for field_name in content_fields:
            if hasattr(page, field_name):
                field_value = getattr(page, field_name)
                if field_value:
                    text = self.extract_text_from_field(field_value)
                    if text and len(text.strip()) > 30:  # Mínimo 30 chars
                        formatted = self.format_meta_description(text)
                        if len(formatted) >= 50:  # Descrição decente
                            return formatted
        
        # Fallback: descrição contextual
        return self.generate_contextual_description(page)
    
    def extract_text_from_field(self, field_value):
        """Extrai texto limpo de diferentes tipos de campo"""
        
        try:
            # StreamField do Wagtail
            if hasattr(field_value, 'stream_data'):
                return self.extract_from_streamfield(field_value)
            
            # RichTextField do Wagtail
            elif hasattr(field_value, 'source'):
                return strip_tags(field_value.source)
            
            # Campo de texto simples
            else:
                return strip_tags(str(field_value))
                
        except Exception:
            return ""
    
    def extract_from_streamfield(self, streamfield):
        """Extrai texto relevante de StreamField"""
        
        text_parts = []
        
        try:
            for block_data in streamfield.stream_data:
                block_type = block_data.get('type', '')
                block_value = block_data.get('value', '')
                
                # Prioriza blocos com texto útil
                if block_type in ['paragraph', 'text', 'rich_text', 'heading', 'introduction']:
                    extracted = self.extract_text_from_block_value(block_value)
                    if extracted:
                        text_parts.append(extracted)
                
                # Para quando tem texto suficiente
                if len(' '.join(text_parts)) > 200:
                    break
                    
        except Exception:
            pass
        
        return ' '.join(text_parts)
    
    def extract_text_from_block_value(self, block_value):
        """Extrai texto de valor de bloco StreamField"""
        
        try:
            if isinstance(block_value, str):
                return strip_tags(block_value)
            
            elif isinstance(block_value, dict):
                # Procura chaves comuns de texto
                text_keys = ['text', 'content', 'description', 'value', 'title']
                for key in text_keys:
                    if key in block_value and block_value[key]:
                        return strip_tags(str(block_value[key]))
        except Exception:
            pass
        
        return ""
    
    def format_meta_description(self, text):
        """Formata texto para meta description (máx 160 chars)"""
        
        # Remove HTML e normaliza espaços
        clean_text = re.sub(r'\s+', ' ', strip_tags(text)).strip()
        
        # Remove caracteres problemáticos (mantém acentos)
        clean_text = re.sub(r'[^\w\s\-.,!?()áéíóúâêîôûàèìòùãõçÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]', '', clean_text)
        
        # Trunca inteligentemente
        if len(clean_text) > 160:
            # Tenta cortar em ponto final
            max_length = 157  # Reserva 3 chars para "..."
            sentences = clean_text[:max_length].split('.')
            
            if len(sentences) > 1 and len(sentences[0]) >= 40:
                return sentences[0] + '.'
            
            # Corta em palavra completa
            words = clean_text[:max_length].split()
            if len(words) > 1:
                return ' '.join(words[:-1]) + '...'
            else:
                return clean_text[:max_length] + '...'
        
        return clean_text
    
    def generate_contextual_description(self, page):
        """Gera descrição baseada no tipo de página"""
        
        page_type = page.__class__.__name__
        title = page.title
        
        # Templates específicos por tipo de página
        contextual_templates = {
            'ENAPService': f'{title} - Serviço especializado da ENAP. Soluções inovadoras em administração pública para desenvolvimento do setor.',
            'ENAPComponentes': f'Curso {title} da ENAP. Capacitação profissional em administração pública com metodologia de excelência e certificação reconhecida.',
            'ENAPNoticiaImportada': f'{title} - Notícia oficial da ENAP. Mantenha-se atualizado com as principais novidades da Escola Nacional de Administração Pública.',
            'MbaEspecializacao': f'MBA e Especialização {title} - ENAP. Programas de pós-graduação de excelência em gestão pública e administração.',
            'TemplateEspecializacao': f'Especialização {title} - ENAP. Programa de pós-graduação em administração pública com metodologia de excelência.',
            'ENAPSemana': f'Evento {title} da ENAP. Participe de nossa programação de desenvolvimento profissional e networking em administração pública.',
            'HolofotePage': f'Destaque ENAP: {title}. Conteúdo selecionado sobre administração pública, inovação e desenvolvimento de competências.',
            'LiaPage': f'{title} - Inteligência Artificial na ENAP. Explore as aplicações de IA na administração pública.',
        }
        
        return contextual_templates.get(
            page_type,
            f'Conheça mais sobre {title} na ENAP - Escola Nacional de Administração Pública. Educação de excelência para o setor público.'
        )
    
    def print_summary(self, updated, skipped, errors, total):
        """Imprime resumo final da execução"""
        
        self.stdout.write('\n' + '='*60)
        
        if self.dry_run:
            self.stdout.write(
                self.style.SUCCESS('🔍 PREVIEW CONCLUÍDO')
            )
            self.stdout.write(f'   📊 {updated} páginas SERIAM atualizadas de {total} analisadas')
            self.stdout.write(f'   ⏭️  {skipped} páginas já possuem SEO')
            self.stdout.write(f'   🚀 Execute sem --dry-run para aplicar as mudanças')
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ PROCESSAMENTO CONCLUÍDO')
            )
            self.stdout.write(f'   📊 {updated} páginas atualizadas com sucesso')
            self.stdout.write(f'   ⏭️  {skipped} páginas não precisaram de alteração')
        
        if errors > 0:
            self.stdout.write(
                self.style.ERROR(f'   ❌ {errors} páginas com erro (verifique logs)')
            )
        
        self.stdout.write('='*60)