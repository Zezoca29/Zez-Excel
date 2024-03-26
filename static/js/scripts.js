function converterArquivos() {
    // Redirecionar para a rota de conversão de arquivos
    window.location.href = '/converter';
}

function manipularTabelas() {
    // Lógica para a manipulação de tabelas
    window.location.href = '/manipular';
}

function manipularDados() {
    // Lógica para a manipulação de dados
    console.log('Manipulação de dados');
}

function montarGrafico() {
    // Lógica para montar gráfico
    console.log('Montar gráfico');
}

function showButtons() {
    var buttonsContainer = document.getElementById('buttons-container');
    buttonsContainer.style.display = 'block';
    var startButton = document.getElementById('startButton');
    startButton.style.display = 'none';
}
