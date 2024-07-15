//Ingresar informe ESV

var preguntas = document.querySelectorAll('.pregunta');
var index = 0;
var siguienteBtn = document.getElementById('siguiente-btn');
var anteriorBtn = document.getElementById('anterior-btn');

function mostrarPreguntas() {
    preguntas.forEach(function (pregunta, i) {
        pregunta.style.display = i >= index && i < index + 5 ? 'block' : 'none';
    });

    siguienteBtn.style.display = index + 5 < preguntas.length ? 'block' : 'none';
    anteriorBtn.style.display = index > 0 ? 'block' : 'none';
}

function cambiarPreguntas(cantidad) {
    index += cantidad;
    mostrarPreguntas();
}

mostrarPreguntas();
