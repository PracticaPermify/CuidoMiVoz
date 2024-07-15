document.addEventListener("DOMContentLoaded", function() {

  function traducirValor(valor) {
      var traducciones = {
          0: 'Normal',
          1: 'Alteración leve',
          2: 'Alteración moderada',
          3: 'Alteración severa',
      };
      return traducciones[valor] || valor;
  }

  var celdasTraducir = document.querySelectorAll('.valor-traducir');

  celdasTraducir.forEach(function(celda) {
      var valorOriginal = celda.textContent;
      var valorTraducido = traducirValor(parseInt(valorOriginal));
      celda.textContent = valorTraducido;
  });
});