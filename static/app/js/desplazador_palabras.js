
document.addEventListener("DOMContentLoaded", function () {
  const selects = Array.from(document.querySelectorAll('.select-separado'));
  const selectsPorGrupo = 10;
  let grupoActual = 0;

  function mostrarGrupoSelects(indiceGrupo) {
      const inicio = indiceGrupo * selectsPorGrupo;
      const fin = inicio + selectsPorGrupo;

      selects.forEach((select, indice) => {
          if (indice >= inicio && indice < fin) {
              select.style.display = '';
          } else {
              select.style.display = 'none';
          }
      });
  }

  function manejarNavegacion(direccion) {
      const totalGrupos = Math.ceil(selects.length / selectsPorGrupo);

      if (direccion === 'siguiente') {
          grupoActual = Math.min(grupoActual + 1, totalGrupos - 1);
      } else {
          grupoActual = Math.max(grupoActual - 1, 0);
      }

      mostrarGrupoSelects(grupoActual);

      const anteriorBtn = document.getElementById('anterior-btn');
      const siguienteBtn = document.getElementById('siguiente-btn');

      if (grupoActual > 0) {
          anteriorBtn.style.display = '';
          siguienteBtn.style.display = 'none';
      } else {
          anteriorBtn.style.display = 'none';
          siguienteBtn.style.display = '';
      }
  }

  const siguienteBtn = document.getElementById('siguiente-btn');
  siguienteBtn.addEventListener('click', () => manejarNavegacion('siguiente'));

  const anteriorBtn = document.getElementById('anterior-btn');
  anteriorBtn.addEventListener('click', () => manejarNavegacion('anterior'));

  mostrarGrupoSelects(grupoActual);
  anteriorBtn.style.display = 'none'; 
});
