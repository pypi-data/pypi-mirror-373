# enap_designsystem/management/commands/check_seo.py

from django.core.management.base import BaseCommand
from wagtail.models import Page

class Command(BaseCommand):
    help = 'Verifica o status do SEO das páginas do site'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--missing-only',
            action='store_true',
            help='Mostra apenas páginas sem SEO completo',
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Mostra análise detalhada de cada página',
        )
        parser.add_argument(
            '--live-only',
            action='store_true',
            default=True,
            help='Verifica apenas páginas publicadas',
        )
    
    def handle(self, *args, **options):
        self.missing_only = options['missing_only']
        self.detailed = options['detailed']
        self.live_only = options['live_only']
        
        self.stdout.write('🔍 Verificando SEO das páginas...\n')
        
        # Busca páginas (exclui página raiz básica)
        if self.live_only:
            pages = Page.objects.live().exclude(content_type__model='page').specific()
        else:
            pages = Page.objects.exclude(content_type__model='page').specific()
        
        total = pages.count()
        
        if total == 0:
            self.stdout.write('⚠️  Nenhuma página encontrada')
            return
        
        # Análise das páginas
        complete_seo = 0
        partial_seo = 0
        no_seo = 0
        issues = []
        
        for page in pages:
            seo_status = self.analyze_page_seo(page)
            
            if seo_status['score'] >= 100:
                complete_seo += 1
                if not self.missing_only:
                    self.stdout.write(f'✅ {page.title} - SEO completo')
                    
            elif seo_status['score'] >= 50:
                partial_seo += 1
                if not self.missing_only or self.detailed:
                    self.stdout.write(f'⚠️  {page.title} - SEO parcial ({seo_status["score"]}%)')
                    for issue in seo_status['issues']:
                        self.stdout.write(f'     • {issue}')
                        
            else:
                no_seo += 1
                issues.append({
                    'page': page,
                    'status': seo_status
                })
        
        # Mostra páginas com problemas
        if issues:
            self.stdout.write(f'\n❌ PÁGINAS COM PROBLEMAS DE SEO ({len(issues)}):')
            for item in issues:
                page = item['page']
                status = item['status']
                
                self.stdout.write(f'\n📄 {page.title}')
                self.stdout.write(f'   🔗 URL: {page.url or "N/A"}')
                self.stdout.write(f'   📱 Tipo: {page.__class__.__name__}')
                self.stdout.write(f'   📊 Score: {status["score"]}%')
                
                for issue in status['issues']:
                    self.stdout.write(f'   ❌ {issue}')
        
        # Resumo final
        self.print_summary(complete_seo, partial_seo, no_seo, total)
    
    def analyze_page_seo(self, page):
        """Analisa o SEO de uma página específica"""
        
        score = 0
        issues = []
        
        # Verifica título SEO
        seo_title = None
        if hasattr(page, 'seo_title'):
            seo_title = getattr(page, 'seo_title', '')
        
        if seo_title and seo_title.strip():
            if len(seo_title) <= 60:
                score += 25
            else:
                score += 15
                issues.append(f'Título SEO muito longo ({len(seo_title)} chars)')
        else:
            # Verifica título padrão
            if len(page.title) <= 60:
                score += 15
            else:
                score += 5
                issues.append('Título padrão muito longo, precisa de seo_title')
        
        # Verifica meta description
        meta_desc = None
        
        # Procura em campos de meta description
        for field in ['meta_description', 'search_description']:
            if hasattr(page, field):
                desc = getattr(page, field, '')
                if desc and desc.strip():
                    meta_desc = desc
                    break
        
        if meta_desc:
            if 50 <= len(meta_desc) <= 160:
                score += 50
            elif len(meta_desc) > 160:
                score += 30
                issues.append(f'Meta description muito longa ({len(meta_desc)} chars)')
            else:
                score += 20
                issues.append('Meta description muito curta')
        else:
            issues.append('Meta description ausente')
        
        # Verifica imagem OG (se aplicável)
        if hasattr(page, 'og_image') or hasattr(page, 'seo_image'):
            og_image = getattr(page, 'og_image', None) or getattr(page, 'seo_image', None)
            if og_image:
                score += 15
            else:
                score += 5
                issues.append('Imagem para redes sociais ausente')
        else:
            score += 10  # Não penaliza se não tem campo
        
        # Verifica conteúdo para extração
        has_content = False
        content_fields = ['introduction', 'summary', 'body', 'content']
        
        for field in content_fields:
            if hasattr(page, field):
                field_value = getattr(page, field)
                if field_value:
                    has_content = True
                    break
        
        if has_content:
            score += 10
        else:
            issues.append('Sem conteúdo para extração automática')
        
        return {
            'score': min(score, 100),  # Máximo 100%
            'issues': issues,
            'has_seo_title': bool(seo_title),
            'has_meta_description': bool(meta_desc),
            'meta_length': len(meta_desc) if meta_desc else 0,
        }
    
    def print_summary(self, complete, partial, problems, total):
        """Imprime resumo da análise"""
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📊 RESUMO DA ANÁLISE DE SEO:')
        self.stdout.write(f'   ✅ SEO completo: {complete}/{total} ({complete/total*100:.1f}%)')
        self.stdout.write(f'   ⚠️  SEO parcial: {partial}/{total} ({partial/total*100:.1f}%)')
        self.stdout.write(f'   ❌ Problemas: {problems}/{total} ({problems/total*100:.1f}%)')
        
        if problems > 0:
            self.stdout.write(f'\n🚀 RECOMENDAÇÃO:')
            self.stdout.write(f'   Execute: python manage.py generate_seo --dry-run')
            self.stdout.write(f'   Depois: python manage.py generate_seo')
        
        self.stdout.write('='*60)