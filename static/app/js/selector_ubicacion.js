document.getElementById('region').addEventListener('change', function() {
    const regionId = this.value;
    const provinciaSelect = document.getElementById('provincia');
    const comunaSelect = document.getElementById('comuna');
    const institucionSelect = document.getElementById('institucion');

    provinciaSelect.removeAttribute('disabled');
    comunaSelect.removeAttribute('disabled');


    
    provinciaSelect.innerHTML = '<option value="" selected>Selecciona una provincia</option>';
    comunaSelect.innerHTML = '<option value="" selected>Selecciona una comuna</option>';


    if (regionId) {
        // Al seleccionar una región, cargar todas las provincias y la primera provincia seleccionada por defecto
        fetch(`/obtener_provincias/?region_id=${regionId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(provincia => {
                    const option = document.createElement('option');
                    option.value = provincia.id_provincia;
                    option.textContent = provincia.provincia;
                    provinciaSelect.appendChild(option);
                });

                // Una vez que se cargan las provincias, seleccionar la primera provincia por defecto
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
        // Al seleccionar una provincia, cargar las comunas relacionadas con esa provincia
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

