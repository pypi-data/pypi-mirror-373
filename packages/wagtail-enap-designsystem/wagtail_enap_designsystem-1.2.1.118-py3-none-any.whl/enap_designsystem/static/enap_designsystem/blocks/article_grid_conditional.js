/**
 * Script para mostrar/ocultar campos do ArticleGridBlock baseado no tipo de layout
 * Arquivo: static/enap_designsystem/js/article_grid_conditional.js
 */

document.addEventListener('DOMContentLoaded', function() {
    // Função para configurar a visibilidade condicional
    function setupConditionalFields() {
        // Procura por todos os ArticleGridBlocks na página
        document.querySelectorAll('[data-streamfield-stream-container]').forEach(function(container) {
            setupArticleGridConditionals(container);
        });
    }
    
    function setupArticleGridConditionals(container) {
        // Busca campos de layout_type dentro do container
        const layoutSelects = container.querySelectorAll('select[name*="layout_type"]');
        
        layoutSelects.forEach(function(select) {
            const blockContainer = select.closest('[data-streamfield-block]');
            if (!blockContainer) return;
            
            // Encontra os campos relacionados no mesmo bloco
            const conteudoField = blockContainer.querySelector('[data-streamfield-stream-container][data-name*="conteudo"]');
            const colunaEsquerdaField = blockContainer.querySelector('[data-streamfield-stream-container][data-name*="coluna_esquerda"]');
            const colunaDireitaField = blockContainer.querySelector('[data-streamfield-stream-container][data-name*="coluna_direita"]');
            
            if (!conteudoField || !colunaEsquerdaField || !colunaDireitaField) return;
            
            // Função para atualizar visibilidade
            function updateFieldVisibility() {
                const selectedValue = select.value;
                
                if (selectedValue === 'revista') {
                    // Modo revista: mostra colunas, esconde conteúdo normal
                    showField(colunaEsquerdaField);
                    showField(colunaDireitaField);
                    hideField(conteudoField);
                } else {
                    // Modo notícia normal: mostra conteúdo, esconde colunas
                    showField(conteudoField);
                    hideField(colunaEsquerdaField);
                    hideField(colunaDireitaField);
                }
            }
            
            // Aplica visibilidade inicial
            updateFieldVisibility();
            
            // Monitora mudanças no select
            select.addEventListener('change', updateFieldVisibility);
        });
    }
    
    function showField(field) {
        if (field) {
            const fieldWrapper = field.closest('.field, .sequence-member-inner, [class*="field"]');
            if (fieldWrapper) {
                fieldWrapper.style.display = '';
                fieldWrapper.style.opacity = '1';
                fieldWrapper.style.visibility = 'visible';
            }
            field.style.display = '';
        }
    }
    
    function hideField(field) {
        if (field) {
            const fieldWrapper = field.closest('.field, .sequence-member-inner, [class*="field"]');
            if (fieldWrapper) {
                fieldWrapper.style.display = 'none';
                fieldWrapper.style.opacity = '0';
                fieldWrapper.style.visibility = 'hidden';
            }
            field.style.display = 'none';
        }
    }
    
    // Configuração inicial
    setupConditionalFields();
    
    // Re-executa quando novos blocos são adicionados (Wagtail StreamField)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && node.querySelector) {
                        // Verifica se o novo nó contém ArticleGridBlocks
                        if (node.matches('[data-streamfield-stream-container]') || 
                            node.querySelector('[data-streamfield-stream-container]')) {
                            setTimeout(() => setupConditionalFields(), 100);
                        }
                    }
                });
            }
        });
    });
    
    // Observa mudanças no DOM para novos blocos
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Também monitora eventos customizados do Wagtail
    document.addEventListener('streamfield:ready', setupConditionalFields);
    document.addEventListener('streamfield:block-added', setupConditionalFields);
});