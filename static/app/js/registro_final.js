document.addEventListener('DOMContentLoaded', function () {
  let tipoUsuarioSelect = document.getElementById('tipo_usuario');
  
  if (tipoUsuarioSelect) {
      tipoUsuarioSelect.addEventListener('change', function () {
          let selectedOption = tipoUsuarioSelect.selectedOptions[0];
          let selectedText = selectedOption.textContent;
          console.log('Seleccionaste:', selectedText);
          
          if (selectedText === 'Paciente') {
              console.log('Realiza lógica para Paciente');
        
          } else if (selectedText === 'Familiar') {
              console.log('Realiza lógica para Familiar');
        
          }
      });
  }
});

document.addEventListener('DOMContentLoaded', function () {
  let tipoUsuarioSelect = document.getElementById('tipo_usuario');
  let camposPaciente = document.querySelectorAll('.campos-paciente');
  let camposFamiliar = document.querySelectorAll('.campos-familiar'); 

  function toggleCampos() {
      let selectedOption = tipoUsuarioSelect.selectedOptions[0];
      let selectedText = selectedOption.textContent;

      if (selectedText === 'Paciente') {
          camposPaciente.forEach(function (campo) {
              campo.style.display = 'block';
          });

          camposFamiliar.forEach(function (campo) {
              campo.style.display = 'none'; 
          });
      } else if (selectedText === 'Familiar') {
          camposPaciente.forEach(function (campo) {
              campo.style.display = 'none'; 
          });

          camposFamiliar.forEach(function (campo) {
              campo.style.display = 'block'; 
          });
      } else {
          camposPaciente.forEach(function (campo) {
              campo.style.display = 'none';
          });

          camposFamiliar.forEach(function (campo) {
              campo.style.display = 'none'; 
          });
      }
  }

  tipoUsuarioSelect.addEventListener('change', toggleCampos);

  toggleCampos();
});


document.addEventListener('DOMContentLoaded', function () {
    let tipoUsuarioSelect = document.getElementById('tipo_usuario');
    
    if (tipoUsuarioSelect) {
        tipoUsuarioSelect.addEventListener('change', function () {
            let selectedOption = tipoUsuarioSelect.selectedOptions[0];
            let selectedText = selectedOption.textContent;
            console.log('Seleccionaste:', selectedText);
            
         
  
            let camposPaciente = document.querySelectorAll('.campos-paciente');
            camposPaciente.forEach(function (campo) {
                campo.querySelectorAll('input, select, textarea').forEach(function (input) {
                    input.required = (selectedText === 'Paciente');
                });
            });
  
            let camposFamiliar = document.querySelectorAll('.campos-familiar');
            camposFamiliar.forEach(function (campo) {
                campo.querySelectorAll('input, select, textarea').forEach(function (input) {
                    input.required = (selectedText === 'Familiar');
                });
            });
        });
    }
  });