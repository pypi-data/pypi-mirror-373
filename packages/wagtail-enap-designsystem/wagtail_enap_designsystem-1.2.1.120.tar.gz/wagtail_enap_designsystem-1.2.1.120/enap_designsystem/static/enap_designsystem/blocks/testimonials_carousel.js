document.addEventListener('DOMContentLoaded', function() {
    // Forçar a exibição do botão próximo desde o início
    const nextButton = document.getElementById('next-button');
    if (nextButton) {
        nextButton.style.display = 'flex';
        nextButton.style.opacity = '1';
        nextButton.style.pointerEvents = 'auto';
    }
    
    // Código principal do carrossel
    function initCarousel() {
        const carousel = document.getElementById('testimonials-carousel');
        const prevButton = document.getElementById('prev-button');
        const nextButton = document.getElementById('next-button');
        const items = carousel.querySelectorAll('.testimonial-item-wrapper');
        
        if (items.length === 0) return;
        
        // Mostrar botão de próximo independente da quantidade de itens
        nextButton.style.opacity = '1';
        nextButton.style.pointerEvents = 'auto';
        
        let currentIndex = 0;
        let startX, moveX, initialPosition;
        let isDragging = false;
        
        // Número de itens visíveis depende da largura da tela
        function getVisibleItems() {
            return window.innerWidth < 992 ? 1 : 2;
        }
        
        // Obtém a largura de um item e o espaçamento
        function getItemWidth() {
            return items[0].offsetWidth;
        }
        
        function getItemGap() {
            return 25; // Gap fixo entre os itens
        }
        
        // Calcula o índice máximo com base nos itens visíveis
        function getMaxIndex() {
            return Math.max(0, items.length - getVisibleItems());
        }
        
        // Mostra os slides baseado no índice atual
        function showSlide(index) {
            currentIndex = Math.max(0, Math.min(index, getMaxIndex()));
            const itemWidth = getItemWidth();
            const itemGap = getItemGap();
            const offset = currentIndex * (itemWidth + itemGap);
            
            carousel.style.transform = `translateX(-${offset}px)`;
            updateNavigationButtons();
        }
        
        // Atualiza a visibilidade dos botões de navegação
        function updateNavigationButtons() {
            // No primeiro slide, ocultar o botão anterior
            if (currentIndex === 0) {
                prevButton.style.opacity = '0';
                prevButton.style.pointerEvents = 'none';
            } else {
                prevButton.style.opacity = '1';
                prevButton.style.pointerEvents = 'auto';
            }
            
            // No último slide, ocultar o botão próximo
            if (currentIndex >= getMaxIndex()) {
                nextButton.style.opacity = '0';
                nextButton.style.pointerEvents = 'none';
            } else {
                nextButton.style.opacity = '1';
                nextButton.style.pointerEvents = 'auto';
            }
            
            // Debug para verificar os valores
            console.log('Índice atual:', currentIndex);
            console.log('Índice máximo:', getMaxIndex());
            console.log('Botão próximo visível:', nextButton.style.opacity);
        }
        
        // Garantir sempre que o botão próximo esteja visível no início
        if (items.length > getVisibleItems()) {
            nextButton.style.opacity = '1';
            nextButton.style.pointerEvents = 'auto';
        }
        
        // Eventos dos botões
        prevButton.addEventListener('click', function() {
            showSlide(currentIndex - 1);
        });
        
        nextButton.addEventListener('click', function() {
            showSlide(currentIndex + 1);
        });
        
        // Eventos de arrastar
        carousel.addEventListener('mousedown', handleStart);
        carousel.addEventListener('touchstart', handleStart, { passive: true });
        
        carousel.addEventListener('mousemove', handleMove);
        carousel.addEventListener('touchmove', handleMove, { passive: true });
        
        carousel.addEventListener('mouseup', handleEnd);
        carousel.addEventListener('touchend', handleEnd);
        carousel.addEventListener('mouseleave', handleEnd);
        
        function handleStart(e) {
            isDragging = true;
            startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
            initialPosition = currentIndex * (getItemWidth() + getItemGap());
            carousel.style.transition = 'none';
        }
        
        function handleMove(e) {
            if (!isDragging) return;
            
            moveX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
            const diff = moveX - startX;
            
            carousel.style.transform = `translateX(${diff - initialPosition}px)`;
        }
        
        function handleEnd() {
            if (!isDragging) return;
            isDragging = false;
            
            carousel.style.transition = 'transform 0.3s ease-in-out';
            
            const diff = moveX - startX;
            const threshold = getItemWidth() / 3;
            
            if (diff > threshold) {
                showSlide(currentIndex - 1);
            } else if (diff < -threshold) {
                showSlide(currentIndex + 1);
            } else {
                showSlide(currentIndex);
            }
        }
        
        // Ajuste quando a tela é redimensionada
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                // Verifica se o índice atual ainda é válido com o novo tamanho
                if (currentIndex > getMaxIndex()) {
                    currentIndex = getMaxIndex();
                }
                showSlide(currentIndex);
            }, 200);
        });
        
        // Inicializar o carrossel
        showSlide(0);
    }
    
    // Iniciar carrossel com um pequeno atraso para garantir que todos os elementos estejam carregados
    setTimeout(initCarousel, 100);
});