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
    window.location.href = '/analise_dados';
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

var table;

function uploadFile() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];
    if (file) {
        var formData = new FormData();
        formData.append('file', file);
        fetch('/uploadanalises', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            table = new Tabulator("#excel-table", {
                data: data.data,
                columns: data.columns.map(col => ({ title: col, field: col })),
            });

            // Preencher o select com as opções das colunas
            var select = document.getElementById('columns');
            data.columns.forEach(function(col) {
                var option = document.createElement('option');
                option.text = col;
                option.value = col;
                select.appendChild(option);
            });
        })
        .catch(error => console.error('Error:', error));
    }
}

function calculateSum() {
    var selectedColumn = document.getElementById('columns').value;
    var tableData = table.getData();
    var sum = tableData.reduce(function(total, row) {
        return total + parseFloat(row[selectedColumn] || 0);
    }, 0);
    document.getElementById('sumResult').value = sum;
}

function calculate() {
    var selectedColumn = document.getElementById('columns').value;
    var selectedOperation = document.getElementById('operation').value;
    var tableData = table.getData();

    var result;
    if (selectedOperation === 'sum') {
        result = tableData.reduce(function(total, row) {
            return total + parseFloat(row[selectedColumn] || 0);
        }, 0);
    } else if (selectedOperation === 'mean') {
        var sum = tableData.reduce(function(total, row) {
            return total + parseFloat(row[selectedColumn] || 0);
        }, 0);
        result = sum / tableData.length;
    } else if (selectedOperation === 'median') {
        var sortedValues = tableData.map(row => parseFloat(row[selectedColumn] || 0)).sort((a, b) => a - b);
        var middle = Math.floor(sortedValues.length / 2);
        if (sortedValues.length % 2 === 0) {
            result = (sortedValues[middle - 1] + sortedValues[middle]) / 2;
        } else {
            result = sortedValues[middle];
        }
    } else if (selectedOperation === 'mode') {
        var counts = {};
        tableData.forEach(row => {
            var value = parseFloat(row[selectedColumn] || 0);
            counts[value] = (counts[value] || 0) + 1;
        });
        var modeValue;
        var maxCount = 0;
        Object.keys(counts).forEach(key => {
            if (counts[key] > maxCount) {
                modeValue = parseFloat(key);
                maxCount = counts[key];
            }
        });
        result = modeValue;
    }

    document.getElementById('result').value = result;
}
