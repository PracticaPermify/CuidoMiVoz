//funciones de Microfono


var nombre;
var cancelled=false;
var grabando=false;
var pauta_id = window.id;
var terapia = window.terapia;


function captureMicrophone(callback) {
    navigator.mediaDevices.getUserMedia({audio: true}).then(callback).catch(function(error) {
        alert('Unable to access your microphone.');
        console.error(error);
    });
}

function stopRecordingCallback() {
    audio.srcObject = null;
    var blob = recorder.getBlob();
    if(!cancelled){
        if(blob !==null){
            console.log("guardando");
            var formData = new FormData();
            var filer = new File([blob], "audio.wav", { type: "audio/wav" });
            formData.append('file', filer,);
            formData.append('string',nombre);

            //Logica de la construcción de URL

            var url_terapia;
            if (terapia === "Vocalización")  {

                var csrftoken = document.querySelector('#post-form [name=csrfmiddlewaretoken]').value;

                if (pauta_id) {
                    url_terapia = vocalizacionConPautaURL;
                } else {
                    url_terapia = vocalizacionURL;
                }
    
                fetch(url_terapia, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    
                })
                .then(response => {
                    if (response.ok) {
                        console.log('Grabación de audio completada y enviada al servidor.');
                        Swal.fire({
                            "title": "Correcto",
                            "text": "Grabación de audio completada y enviada al servidor. ¡Buen trabajo!",
                            "icon": "success"
                        });
                    } else {
                        console.error('Error al enviar el audio al servidor.');
                    }
                });

            } else if (terapia === "Intensidad") {

                var crsftoken = window.csrftoken;

                if (pauta_id) {
                    url_terapia = intensidadeConPautaURL;
                } else {
                    url_terapia = '/intensidad/';
                }

                
                //console.log("Intensidad" + crsftoken);

                fetch(url_terapia, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': crsftoken
                    },
                    
                })
                .then(response => {
                    if (response.ok) {
                        console.log('Grabación de audio completada y enviada al servidor.');
                        Swal.fire({
                            "title": "Correcto",
                            "text": "Grabación de audio completada y enviada al servidor. ¡Buen trabajo!",
                            "icon": "success"
                        });
                    } else {
                        console.error('Error al enviar el audio al servidor.');
                    }
                });


            } else if (terapia === "Escala_vocal") {

                var crsftoken = window.csrftoken;

                if (pauta_id) {
                    url_terapia = escalavocalesConPautaURL;
                } else {
                    url_terapia = '/escalas_vocales/';
                }

                
                //console.log("Intensidad" + crsftoken);

                fetch(url_terapia, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': crsftoken
                    },
                    
                })
                .then(response => {
                    if (response.ok) {
                        console.log('Grabación de audio completada y enviada al servidor.');
                        Swal.fire({
                            "title": "Correcto",
                            "text": "Grabación de audio completada y enviada al servidor. ¡Buen trabajo!",
                            "icon": "success"
                        });
                    } else {
                        console.error('Error al enviar el audio al servidor.');
                    }
                });



            }
            
        }
        else{console.log("nada que guardar");}
    }
    audio.src = URL.createObjectURL(blob);
    recorder.microphone.stop();
    grabando=false;
}
var recorder; // globally accessible

const iniciarGrabacion= () => {
    //this.disabled = true;
    captureMicrophone(function(microphone) {
        audio.srcObject = microphone;

        recorder = RecordRTC(microphone, {
            type: 'audio',
            //recorderType: StereoAudioRecorder,
            mimeType: 'audio/wav',
            recorderType: RecordRTC.StereoAudioRecorder,
            numberOfAudioChannels: 1,
            desiredSampRate: 16000
        });

        recorder.startRecording();
        if(nombre==="vocalizacion"){
            iniciarMetronomo();
        }
        // release microphone on stopRecording
        recorder.microphone = microphone;
        grabando=true;
        //document.getElementById('btn-stop-recording').disabled = false;
    });
    return true;
};
const guardarGrabacion =() =>{
    if(blob !==null){
        console.log("guardando");
        var formData = new FormData();
        var filer = new File([blob], "audio.wav", { type: "audio/wav" });
        formData.append('file', filer,);
        formData.append('string',nombre);
        fetch('/vocalizacion/', {
            method: 'POST',
            body: formData});
    }
    else{console.log("nada que guardar");}
}

const detenerGrabacion = () => {
    //this.disabled = true;
    //document.getElementById('btn-save-recording').disabled=false;
    recorder.stopRecording(stopRecordingCallback);
};

//funciones de contadores,metronomo y conexion a documento
var audio = document.querySelector('audio');
const $duracion = document.querySelector("#duracion");
const $start_stop = document.querySelector("#start_stop");
// Variables "globales"
let tiempoInicio, idIntervalo;

const segundosATiempo = numeroDeSegundos => {
    let horas = Math.floor(numeroDeSegundos / 60 / 60);
    numeroDeSegundos -= horas * 60 * 60;
    let minutos = Math.floor(numeroDeSegundos / 60);
    numeroDeSegundos -= minutos * 60;
    numeroDeSegundos = parseInt(numeroDeSegundos);
    if (horas < 10) horas = "0" + horas;
    if (minutos < 10) minutos = "0" + minutos;
    if (numeroDeSegundos < 10) numeroDeSegundos = "0" + numeroDeSegundos;
    return `${horas}:${minutos}:${numeroDeSegundos}`;
};


const refrescar = () => {
    $duracion.textContent = segundosATiempo((Date.now() - tiempoInicio) / 1000);
}

const comenzarAContar = () => {
    tiempoInicio = Date.now();
    idIntervalo = setInterval(refrescar, 500);
    
};

const detenerConteo = () => {
    clearInterval(idIntervalo);
    tiempoInicio = null;
    $duracion.textContent = "La grabacion comenzara una vez precione el boton";
}

const iniciarMetronomo = () => {
    metronome.start();
    $start_stop.textContent = "PARAR";
    let segundos = document.querySelector("#segundos").textContent;
    timerId = setTimeout(() => {
        if(grabando){
            metronome.stop();
            detenerGrabacion();
            $start_stop.textContent = "COMENZAR";
        }
    },  segundos  * 1100);
}

clickAudio = (a) => {
    console.log($start_stop.textContent)
    let val = $start_stop.textContent
    //si lo invoca la vista intensidad
    if(a){
        if(val === "PARAR"){
            detenerGrabacion();
                
            //guardarGrabacion();
            $start_stop.textContent = "COMENZAR";

        }else if(val = "COMENZAR"){
            nombre="intensidad";
            iniciarGrabacion();
            $start_stop.textContent = "PARAR";
        }
    }
    //si lo invoca la vista vocalizacion
    else{
        if(val === "PARAR"){
            cancelled=true;
            detenerGrabacion();
            metronome.stop();
            $start_stop.textContent = "COMENZAR";
        }else if(val = "COMENZAR"){
            cancelled=false;
            nombre="vocalizacion";
            iniciarGrabacion();
        }
    }
}







