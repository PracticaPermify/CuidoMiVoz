$(document).ready(function() {
    var formularioVisible = false;

    function mostrarFormulario() {
        $("#formulario-pauta").slideDown();
        $("#mostrar-formulario-btn").hide();
        $("#ocultar-formulario-btn").show();
        formularioVisible = true;
        $("html, body").animate({ scrollTop: $("#formulario-pauta").offset().top }, "slow");
    }

    function ocultarFormulario() {
        limpiarCampos();

        $("#formulario-pauta").slideUp();
        $("#mostrar-formulario-btn").show();
        $("#ocultar-formulario-btn").hide();
        formularioVisible = false;
    }

    function limpiarCampos() {
        $("#id_cant_veces_dia").val("");
        $("#id_descripcion").val("");
        $("#fk_tp_terapia").val("");
        $("#fecha_inicio").val("");
        $("#id_descripcion").val("");
        $("#fecha_fin").val("");
        $("#id_comentario").val("");

        //Campos de intensidad

        $("#id_intensidad").val("");
        $("#id_min_db").val("");
        $("#id_max_db").val("");

        //campos de vocalizacion
        
        $("#id_duracion_seg").val("");
        $("#id_bpm").val("");
        $("#id_tempo").val("");
    }

    $("#mostrar-formulario-btn").click(function() {
        if (!formularioVisible) {
            mostrarFormulario();
        } else {
            ocultarFormulario();
        }
    });

    $("#ocultar-formulario-btn").click(function() {
        ocultarFormulario();
    });
});

document.addEventListener('DOMContentLoaded', function () {
    let tpTerapiaSelect = document.getElementById('fk_tp_terapia');
    let camposGrbas = document.querySelectorAll('.campos-vocalizacion'); // Nuevos campos para "GRBAS"
    let camposRasati = document.querySelectorAll('.campos-intensidad'); // Nuevos campos para "RASATI"

    function toggleCampos() {
        let selectedTipoInforme = tpTerapiaSelect.selectedOptions[0];

        // Lógica para mostrar u ocultar campos según el tipo de informe
        if (selectedTipoInforme.textContent === 'Vocalización') {
            camposGrbas.forEach(function (campo) {
                campo.style.display = 'block'; // Mostrar campos de "GRBAS"
            });

            camposRasati.forEach(function (campo) {
                campo.style.display = 'none'; // Ocultar campos de "RASATI"
            });
        } else if (selectedTipoInforme.textContent === 'Intensidad') {
            camposGrbas.forEach(function (campo) {
                campo.style.display = 'none'; // Ocultar campos de "GRBAS"
            });

            camposRasati.forEach(function (campo) {
                campo.style.display = 'block'; // Mostrar campos de "RASATI"
            });
        } else {
            camposGrbas.forEach(function (campo) {
                campo.style.display = 'none';
            });

            camposRasati.forEach(function (campo) {
                campo.style.display = 'none'; // Ocultar campos para otros valores de informe
            });
        }
    }
    tpTerapiaSelect.addEventListener('change', toggleCampos);

    // Llama a la función para configurar los campos según los valores iniciales
    toggleCampos();
});

// CAMBIO REQUIRED DE LOS ATRIBUTOS DE MANERA DINÁMICA
$(document).ready(function () {
    // TIPO DE TERAPIA
    var fkTpTerapiaField = $('#fk_tp_terapia');

    //CAMPOS VOCALIZACIÓN
    var duracionSegField = $('#id_duracion_seg');
    var id_bpm = $('#id_bpm');
    var id_tempo = $('#id_tempo');

    //CAMPOS INTENSIDAD
    var id_intensidad = $('#id_intensidad');
    var id_min_db = $('#id_min_db');
    var id_max_db = $('#id_max_db');


    function updateRequiredStatus() {
        var selectedTpTerapia = fkTpTerapiaField.val();
        console.log(selectedTpTerapia)

        //VOCALIZACIÓN
        if (selectedTpTerapia === "1") {
            // CAMPOS DE VOCALIZACIÓN
            duracionSegField.prop('required', true);
            id_bpm.prop('required', true);
            id_tempo.prop('required', true);
    
            // CAMPOS DE INTENSIDAD
            id_intensidad.prop('required', false);
            id_min_db.prop('required', false);
            id_max_db.prop('required', false);

        //INTENSIDAD
        } else if (selectedTpTerapia === "2") {

            //CAMPOS DE INTENSIDAD
            id_intensidad.prop('required', true);
            id_min_db.prop('required', false);
            id_max_db.prop('required', false);

            //CAMPOS DE VOCALIZACIÓN
            duracionSegField.prop('required', false);
            id_bpm.prop('required', false);
            id_tempo.prop('required', false);
        }
    }

    // Captura el evento cuando cambia el tipo de pauta terapéutica
    fkTpTerapiaField.change(function () {
        updateRequiredStatus();
    });

    // Ejecuta la función al cargar la página para reflejar el estado inicial
    updateRequiredStatus();
});
