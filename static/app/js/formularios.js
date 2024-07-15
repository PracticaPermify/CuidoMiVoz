document.addEventListener('DOMContentLoaded', function () {
  let tipoUsuarioSelect = document.getElementById('tp_informe');
  
  if (tipoUsuarioSelect) {
      tipoUsuarioSelect.addEventListener('change', function () {
          let selectedOption = tipoUsuarioSelect.selectedOptions[0];
          let selectedText = selectedOption.textContent;
          console.log( selectedText);
          
          if (selectedText === 'GRBAS') {
              console.log('Seleccionaste GRBAS para formulario');
          } else if (selectedText === 'RASATI') {
              console.log('Seleccionaste RASATI para formulario');
          }
      });
  }
});

document.addEventListener('DOMContentLoaded', function () {
  let tpInformeSelect = document.getElementById('tp_informe');
  let camposGrbas = document.querySelectorAll('.campos-grbas'); 
  let camposRasati = document.querySelectorAll('.campos-rasati'); 

  function toggleCampos() {
      let selectedTipoInforme = tpInformeSelect.selectedOptions[0];

      // Condicional para mostrar valores de los campos ya sea grbas o rasati
      if (selectedTipoInforme.textContent === 'GRBAS') {
          camposGrbas.forEach(function (campo) {
              campo.style.display = 'block'; 
          });

          camposRasati.forEach(function (campo) {
              campo.style.display = 'none'; 
          });
      } else if (selectedTipoInforme.textContent === 'RASATI') {
          camposGrbas.forEach(function (campo) {
              campo.style.display = 'none'; 
          });

          camposRasati.forEach(function (campo) {
              campo.style.display = 'block'; 
          });
      } else {
          camposGrbas.forEach(function (campo) {
              campo.style.display = 'none';
          });

          camposRasati.forEach(function (campo) {
              campo.style.display = 'none'; 
          });
      }
  }
  tpInformeSelect.addEventListener('change', toggleCampos);

  toggleCampos();
});