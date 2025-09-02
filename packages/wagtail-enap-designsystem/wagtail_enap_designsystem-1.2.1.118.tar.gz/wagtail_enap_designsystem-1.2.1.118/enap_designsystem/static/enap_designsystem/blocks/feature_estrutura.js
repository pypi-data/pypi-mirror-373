document.addEventListener('DOMContentLoaded', function() {
    // Seleciona todos os headers de dropdown
    const headers = document.querySelectorAll('.dropdown-header');
    
    // Adiciona o evento de clique a cada header
    headers.forEach(header => {
        header.addEventListener('click', function() {
            // Pega o elemento pai (o dropdown item)
            const parentItem = this.parentElement;
            
            // Verifica se este item já está ativo
            const isActive = parentItem.classList.contains('active');
            
            // Remove a classe active de TODOS os dropdowns
            document.querySelectorAll('.dropdown-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Adiciona a classe active apenas ao item clicado, SE não estava ativo antes
            if (!isActive) {
                parentItem.classList.add('active');
            }
        });
    });
});