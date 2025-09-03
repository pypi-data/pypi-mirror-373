// static/js/simple-dashboard.js
// Dashboard simples sem APIs - apenas Chart.js

// Esquemas de cores ENAP
const COLOR_SCHEMES = {
    'enap': ['#1e40af', '#059669', '#3b82f6', '#10b981', '#60a5fa', '#34d399'],
    'blue': ['#1e3a8a', '#1e40af', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd'],
    'green': ['#14532d', '#166534', '#16a34a', '#22c55e', '#4ade80', '#86efac'],
    'warm': ['#dc2626', '#ea580c', '#d97706', '#ca8a04', '#65a30d', '#16a34a'],
    'cool': ['#1e40af', '#7c3aed', '#be185d', '#059669', '#0891b2', '#4338ca']
};

// Função principal para criar gráficos
function createSimpleChart(canvasId, data, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas ${canvasId} não encontrado`);
        return;
    }

    // Prepara os dados
    const chartData = prepareChartData(data, config);
    
    // Configura o gráfico
    const chartConfig = getChartConfig(config.type, chartData, config);
    
    // Cria o gráfico Chart.js
    try {
        new Chart(canvas, chartConfig);
    } catch (error) {
        console.error('Erro ao criar gráfico:', error);
        showChartError(canvas);
    }
}

// Prepara dados para Chart.js
function prepareChartData(data, config) {
    const labels = data.map(item => item.label);
    const values = data.map(item => item.value);
    
    // Obtém cores
    const colors = getColors(data, config.colorScheme);
    
    return {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: colors.background,
            borderColor: colors.border,
            borderWidth: 2,
            tension: 0.4 // Para gráficos de linha
        }]
    };
}

// Obtém cores baseado no esquema
function getColors(data, scheme) {
    const schemeColors = COLOR_SCHEMES[scheme] || COLOR_SCHEMES['enap'];
    const background = [];
    const border = [];
    
    data.forEach((item, index) => {
        if (item.color && item.color.trim() !== '') {
            // Usa cor personalizada se fornecida
            background.push(item.color);
            border.push(item.color);
        } else {
            // Usa cor do esquema
            const color = schemeColors[index % schemeColors.length];
            background.push(color + '80'); // Adiciona transparência
            border.push(color);
        }
    });
    
    return { background, border };
}

// Configuração específica por tipo de gráfico
function getChartConfig(type, data, config) {
    const baseConfig = {
        type: getChartJsType(type),
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: config.showLegend,
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#ffffff',
                    borderWidth: 1
                }
            }
        }
    };

    // Configurações específicas por tipo
    switch (type) {
        case 'bar':
            baseConfig.options.scales = {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            };
            break;
            
        case 'line':
            baseConfig.data.datasets[0].fill = false;
            baseConfig.data.datasets[0].pointBackgroundColor = baseConfig.data.datasets[0].borderColor;
            baseConfig.data.datasets[0].pointBorderColor = '#fff';
            baseConfig.data.datasets[0].pointBorderWidth = 2;
            baseConfig.data.datasets[0].pointRadius = 5;
            
            baseConfig.options.scales = {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            };
            break;
            
        case 'donut':
            baseConfig.options.cutout = '60%';
            baseConfig.options.plugins.legend.position = 'right';
            break;
            
        case 'pie':
            baseConfig.options.plugins.legend.position = 'right';
            break;
    }

    return baseConfig;
}

// Converte tipos do nosso sistema para Chart.js
function getChartJsType(type) {
    const typeMap = {
        'donut': 'doughnut',
        'bar': 'bar',
        'line': 'line',
        'pie': 'pie'
    };
    return typeMap[type] || 'bar';
}

// Mostra erro quando gráfico falha
function showChartError(canvas) {
    const container = canvas.parentElement;
    container.innerHTML = `
        <div class="chart-error d-flex flex-column align-items-center justify-content-center text-danger">
            <i data-lucide="alert-circle" style="width: 48px; height: 48px;" class="mb-3"></i>
            <p class="mb-0">Erro ao carregar gráfico</p>
            <small class="text-muted">Verifique os dados fornecidos</small>
        </div>
    `;
    
    // Re-inicializa ícones Lucide
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Função para imprimir gráfico específico
function printChart(chartId) {
    const chartElement = document.querySelector(`[data-chart-id="${chartId}"]`);
    if (!chartElement) return;
    
    // Cria nova janela para impressão
    const printWindow = window.open('', '', 'width=800,height=600');
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gráfico - ${chartId}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { padding: 20px; }
                .card { box-shadow: none !important; border: 1px solid #dee2e6; }
                @media print {
                    .btn { display: none !important; }
                }
            </style>
        </head>
        <body>
            ${chartElement.outerHTML}
            <script>
                window.onload = function() {
                    setTimeout(function() {
                        window.print();
                        window.close();
                    }, 1000);
                };
            </script>
        </body>
        </html>
    `);
    
    printWindow.document.close();
}

// Utilitários
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function generateRandomColor() {
    const colors = COLOR_SCHEMES['enap'];
    return colors[Math.floor(Math.random() * colors.length)];
}

// Inicialização quando documento carrega
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa ícones Lucide se disponível
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Adiciona animação suave aos cards
    const cards = document.querySelectorAll('.card-hover');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Smooth scroll para seções
    const sectionTitles = document.querySelectorAll('.section-title');
    sectionTitles.forEach(title => {
        title.style.cursor = 'pointer';
        title.addEventListener('click', function() {
            this.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
    
    console.log('Dashboard simples inicializado com sucesso!');
});

// Exporta funções globais
window.createSimpleChart = createSimpleChart;
window.printChart = printChart;