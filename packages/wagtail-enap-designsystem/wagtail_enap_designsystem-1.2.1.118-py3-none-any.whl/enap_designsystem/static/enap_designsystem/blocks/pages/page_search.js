// Função para abrir abas
function openTab(evt, cityName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tab-btn");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(cityName).style.display = "block";
    evt.currentTarget.className += " active";
}

// Função para abrir filtros
function openFilter(evt, filterType) {
    var i, filterContent, filterBtns;
    filterContent = document.getElementsByClassName("filter-content");
    for (i = 0; i < filterContent.length; i++) {
        filterContent[i].style.display = "none";
    }
    filterBtns = document.getElementsByClassName("filter-btn");
    for (i = 0; i < filterBtns.length; i++) {
        filterBtns[i].className = filterBtns[i].className.replace(" active", "");
    }
    document.getElementById(filterType).style.display = "block";
    evt.currentTarget.className += " active";
}

// Função para mostrar/ocultar filtro lateral
function toggleFiltro() {
    const filtroWrapper = document.querySelector('.filtro-wrapper');
    filtroWrapper.classList.toggle('filtro-aberto');
    
    // Alterar o texto do botão se necessário
    const btnFiltro = document.getElementById('toggleFiltro');
    if (filtroWrapper.classList.contains('filtro-aberto')) {
        btnFiltro.textContent = 'Ocultar Filtro';
    } else {
        btnFiltro.textContent = 'Filtro';
    }
}

function openFilter(evt, filterType) {
    var i, filterContent, filterBtns;
    filterContent = document.getElementsByClassName("filter-content");
    for (i = 0; i < filterContent.length; i++) {
        filterContent[i].style.display = "none";
    }
    filterBtns = document.getElementsByClassName("filter-btn");
    for (i = 0; i < filterBtns.length; i++) {
        filterBtns[i].className = filterBtns[i].className.replace(" active", "");
    }
    document.getElementById(filterType).style.display = "block";
    evt.currentTarget.className += " active";
}

function openSrvFilter(evt, filterType) {
    var i, filterContent, filterBtns;
    filterContent = document.getElementsByClassName("srv-filter-content");
    for (i = 0; i < filterContent.length; i++) {
        filterContent[i].style.display = "none";
    }
    filterBtns = document.getElementsByClassName("srv-filter-btn");
    for (i = 0; i < filterBtns.length; i++) {
        filterBtns[i].className = filterBtns[i].className.replace(" active", "");
    }
    document.getElementById(filterType).style.display = "block";
    evt.currentTarget.className += " active";
}

function openSrvFilter(evt, filterType) {
    var i, filterContent, filterBtns;
    filterContent = document.getElementsByClassName("srv-filter-content");
    for (i = 0; i < filterContent.length; i++) {
        filterContent[i].style.display = "none";
    }
    filterBtns = document.getElementsByClassName("srv-filter-btn");
    for (i = 0; i < filterBtns.length; i++) {
        filterBtns[i].className = filterBtns[i].className.replace(" active", "");
    }
    document.getElementById(filterType).style.display = "block";
    evt.currentTarget.className += " active";
}

function openPesquisaFilter(evt, filterType) {
var i, filterContent, filterBtns;

// Esconde todos os conteúdos
filterContent = document.querySelectorAll("#Tab04 .srv-filter-content");
for (i = 0; i < filterContent.length; i++) {
    filterContent[i].style.display = "none";
}

// Remove a classe active de todos os botões
filterBtns = document.querySelectorAll("#Tab04 .srv-filter-btn");
for (i = 0; i < filterBtns.length; i++) {
    filterBtns[i].className = filterBtns[i].className.replace(" active", "");
}

// Mostra o conteúdo atual e adiciona a classe active ao botão
document.getElementById(filterType).style.display = "block";
evt.currentTarget.className += " active";
}

function openTodosFilter(evt, filterType) {
var i, filterContent, filterBtns;

// Esconde todos os conteúdos
filterContent = document.querySelectorAll("#Tab05 .srv-filter-content");
for (i = 0; i < filterContent.length; i++) {
    filterContent[i].style.display = "none";
}

// Remove a classe active de todos os botões
filterBtns = document.querySelectorAll("#Tab05 .srv-filter-btn");
for (i = 0; i < filterBtns.length; i++) {
    filterBtns[i].className = filterBtns[i].className.replace(" active", "");
}

// Mostra o conteúdo atual e adiciona a classe active ao botão
document.getElementById(filterType).style.display = "block";
evt.currentTarget.className += " active";
}