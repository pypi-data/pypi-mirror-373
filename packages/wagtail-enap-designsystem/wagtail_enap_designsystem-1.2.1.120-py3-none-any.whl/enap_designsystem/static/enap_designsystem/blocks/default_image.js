document.addEventListener('DOMContentLoaded', function() {
    // Procura por TODOS os campos de imagem com a classe que definimos
    const imageFields = document.querySelectorAll('.default-image-14 select, .default-image-14 input[type="hidden"]');
    
    // Itera sobre cada campo encontrado
    imageFields.forEach(function(imageField) {
        if (!imageField.value) {
            // Define o valor padrão se o campo estiver vazio
            imageField.value = '14';  // ID da imagem
            
            // Encontra o botão de escolha mais próximo dentro do mesmo container
            const container = imageField.closest('.default-image-14');
            const chooseBtn = container ? container.querySelector('.action-choose') : null;
            
            if (chooseBtn) {
                // Simula um clique para atualizar a visualização
                const event = new Event('change');
                imageField.dispatchEvent(event);
            }
        }
    });
});