document.getElementById('region').addEventListener('change', function() {
    const regionId = this.value;
    const provinciaSelect = document.getElementById('provincia');
    const comunaSelect = document.getElementById('comuna');
    const institucionSelect = document.getElementById('id_institucion');

    provinciaSelect.removeAttribute('disabled');
    comunaSelect.removeAttribute('disabled');
    institucionSelect.removeAttribute('disabled');

    
    provinciaSelect.innerHTML = '<option value="" selected>Selecciona una provincia</option>';
    comunaSelect.innerHTML = '<option value="" selected>Selecciona una comuna</option>';
    institucionSelect.innerHTML = '<option value="" selected>Selecciona una institución</option>'

    if (regionId) {
        
        //El metodo fetch permitira obtener la region a traves de la regiones que se declararon en la vista

        fetch(`/obtener_provincias/?region_id=${regionId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(provincia => {
                    const option = document.createElement('option');
                    option.value = provincia.id_provincia;
                    option.textContent = provincia.provincia;
                    provinciaSelect.appendChild(option);
                });

                if (data.length > 0) {
                    const primeraProvincia = data[0].id_provincia;
                    cargarComunasPorProvincia(primeraProvincia);
                }
            })
            .catch(error => console.error('Error:', error));
    }
});

document.getElementById('provincia').addEventListener('change', function() {
    const provinciaId = this.value;
    cargarComunasPorProvincia(provinciaId);
});

function cargarComunasPorProvincia(provinciaId) {
    const comunaSelect = document.getElementById('comuna');
    comunaSelect.innerHTML = '<option value="" selected>Selecciona una comuna</option>';

    if (provinciaId) {
        // esto permitira obtener las comunas para almacenarlas en la vista del usuario
        fetch(`/obtener_comunas/?provincia_id=${provinciaId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(comuna => {
                    const option = document.createElement('option');
                    option.value = comuna.id_comuna;
                    option.textContent = comuna.comuna;
                    comunaSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error:', error));
    }
}

document.getElementById('comuna').addEventListener('change', function() {
    const comunaId = this.value;
    const institucionSelect = document.getElementById('id_institucion');

    institucionSelect.innerHTML = '<option value="" selected>Selecciona una institución</option>';

    if (comunaId) {
        
        fetch(`/obtener_instituciones/?comuna_id=${comunaId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(institucion => {
                    const option = document.createElement('option');
                    option.value = institucion.id_institucion;
                    option.textContent = institucion.nombre_institucion;
                    institucionSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error:', error));
    }
});
