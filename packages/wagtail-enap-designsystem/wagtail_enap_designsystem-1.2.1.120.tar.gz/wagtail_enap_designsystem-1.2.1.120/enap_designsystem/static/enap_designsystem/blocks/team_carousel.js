document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.getElementById('team-carousel');
    const prevButton = document.querySelector('.carousel-control-team-prev');
    const nextButton = document.querySelector('.carousel-control-team-next');
    const items = carousel.querySelectorAll('.carousel-item-wrapper');
    
    if (items.length === 0) return;
    
    const itemWidth = items[0].offsetWidth;
    const itemsGap = 25;
    
    let currentIndex = 0;
    let startX, moveX, initialPosition;
    let isDragging = false;
    
    // Variáveis para calcular visibilidade e total de slides
    const totalItems = items.length;
    const containerWidth = carousel.parentElement.offsetWidth;
    const visibleItems = Math.floor(containerWidth / (itemWidth + itemsGap));
    const maxIndex = Math.max(0, totalItems - visibleItems);
    
    // Função para exibir o slide
    function showSlide(index) {
        currentIndex = Math.max(0, Math.min(index, maxIndex));
        const offset = currentIndex * (itemWidth + itemsGap);
        carousel.style.transform = `translateX(-${offset}px)`;
        
        // Controlar a visibilidade dos botões de navegação
        updateNavigationButtons();
    }
    
    // Função para atualizar a visibilidade dos botões de navegação
    function updateNavigationButtons() {
        // No primeiro grupo (índice 0), mostrar apenas a seta da direita
        if (currentIndex === 0) {
            prevButton.style.display = 'none';
            nextButton.style.display = totalItems > visibleItems ? 'block' : 'none';
        } 
        // No último grupo, mostrar apenas a seta da esquerda
        else if (currentIndex >= maxIndex) {
            prevButton.style.display = 'block';
            nextButton.style.display = 'none';
        } 
        // Em grupos intermediários, mostrar ambas as setas
        else {
            prevButton.style.display = 'block';
            nextButton.style.display = 'block';
        }
    }
    
    // Inicializar a visibilidade dos botões
    updateNavigationButtons();
    
    // Determinar quantos itens mostrar por clique
    const itemsPerClick = Math.min(3, visibleItems);
    
    // Controles de seta
    prevButton.addEventListener('click', () => {
        showSlide(currentIndex - itemsPerClick);
    });
    
    nextButton.addEventListener('click', () => {
        showSlide(currentIndex + itemsPerClick);
    });
    
    // Touch e arraste para mobile
    carousel.addEventListener('touchstart', handleStart, { passive: true });
    carousel.addEventListener('touchmove', handleMove, { passive: true });
    carousel.addEventListener('touchend', handleEnd, { passive: true });
    
    // Mouse para desktop (como fallback)
    carousel.addEventListener('mousedown', handleStart);
    carousel.addEventListener('mousemove', handleMove);
    carousel.addEventListener('mouseup', handleEnd);
    carousel.addEventListener('mouseleave', handleEnd);
    
    function handleStart(e) {
        isDragging = true;
        startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
        initialPosition = currentIndex * (itemWidth + itemsGap);
        
        // Desativar transição durante o arrasto para melhor responsividade
        carousel.style.transition = 'none';
    }
    
    function handleMove(e) {
        if (!isDragging) return;
        
        moveX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
        const diff = moveX - startX;
        
        // Limitar o arrasto
        if (currentIndex === 0 && diff > 50) {
            carousel.style.transform = `translateX(${diff / 3 - initialPosition}px)`;
        } else if (currentIndex === maxIndex && diff < -50) {
            carousel.style.transform = `translateX(${diff / 3 - initialPosition}px)`;
        } else {
            carousel.style.transform = `translateX(${diff - initialPosition}px)`;
        }
    }
    
    function handleEnd() {
        if (!isDragging) return;
        isDragging = false;
        
        // Restaurar transição
        carousel.style.transition = 'transform 0.3s ease-in-out';
        
        const diff = moveX - startX;
        if (diff > 50) {
            showSlide(currentIndex - 1);
        } else if (diff < -50) {
            showSlide(currentIndex + 1);
        } else {
            showSlide(currentIndex);
        }
    }
    
    // Ajustar o carrossel quando a janela é redimensionada
    window.addEventListener('resize', function() {
        // Recalcular as variáveis importantes
        const containerWidth = carousel.parentElement.offsetWidth;
        const visibleItems = Math.floor(containerWidth / (itemWidth + itemsGap));
        const maxIndex = Math.max(0, totalItems - visibleItems);
        
        // Verificar se o índice atual ainda é válido
        if (currentIndex > maxIndex) {
            currentIndex = maxIndex;
        }
        
        showSlide(currentIndex);
    });
});