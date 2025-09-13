// Verificar la conexión al cargar la página y luego cada 10 segundos
document.addEventListener('DOMContentLoaded', () => {
    console.log("Inicializando la aplicación...");
    checkServerConnection();
    setInterval(checkServerConnection, 10000);
});

// Función para verificar el estado de la conexión al servidor
function checkServerConnection() {
    const indicator = document.getElementById('server-indicator');
    const statusText = document.getElementById('server-status-text');
    
    // Usar la IP directa para evitar problemas de CORS
    const serverUrl = `http://127.0.0.1:5000/?t=${Date.now()}`; // Añadir timestamp para evitar caché
    
    console.log(`Verificando conexión con el servidor en: ${serverUrl}`);
    
    // Hacer una petición más simple para evitar problemas de CORS
    fetch(serverUrl, {
        method: 'GET',
        mode: 'cors'
    })
    .then(response => {
        console.log('Respuesta del servidor:', response.status, response.statusText);
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        indicator.classList.remove('offline');
        indicator.classList.add('online');
        statusText.textContent = '';
        return response.json();
    })
    .then(data => {
        console.log('Servidor respondió:', data);
        // No hacemos nada más con los datos, solo verificamos que respondió
    })
    .catch(error => {
        console.error('Error al verificar conexión:', error);
        indicator.classList.remove('online');
        indicator.classList.add('offline');
        statusText.textContent = 'Servidor desconectado';
    });
}

// Verificar la conexión al cargar la página y luego cada 10 segundos
document.addEventListener('DOMContentLoaded', () => {
    checkServerConnection();
    setInterval(checkServerConnection, 10000);
});

function loadContract() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.pdf';
    
    fileInput.onchange = function(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const panelContainer = document.getElementById('panel-container');
        const info = `
            <div class="contract-info">
                <h3>Archivo cargado:</h3>
                <p><strong>Nombre:</strong> ${file.name}</p>
                <p><strong>Tamaño:</strong> ${(file.size / 1024).toFixed(2)} KB</p>
                <p><strong>Tipo:</strong> ${file.type}</p>
            </div>
        `;
        panelContainer.innerHTML = info;
        const formData = new FormData();
        formData.append('file', file);
        
        // Mostrar indicador de carga mientras se sube el archivo
        panelContainer.innerHTML += `
            <div class="contract-info">
                <p>Subiendo archivo y analizando...</p>
                <div class="loading-indicator">
                    <div class="spinner"></div>
                </div>
            </div>
        `;
        
        console.log('Enviando archivo al servidor...');
        
        // Usar la URL dinámica basada en el host actual pero con el puerto 5000
        // En este caso usamos directamente 127.0.0.1 para evitar problemas de CORS
        const serverUrl = `http://127.0.0.1:5000/upload`;
        console.log(`Conectando con el servidor en: ${serverUrl}`);
        
        fetch(serverUrl, {
            method: 'POST',
            body: formData,
            mode: 'cors',  // Asegurarse de que las solicitudes cross-origin funcionen
            credentials: 'omit' // No enviar cookies ni credenciales para evitar problemas CORS
        })
        .then(response => {
            console.log('Respuesta recibida del servidor:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status} ${response.statusText}`);
            }
            return response.json().catch(error => {
                console.error("Error al parsear JSON:", error);
                throw new Error("Error al procesar la respuesta del servidor");
            });
        })
        .then(data => {
            console.log('Datos recibidos del servidor:', data);
            
            if (data.success) {
                // Eliminar todos los elementos de información previos
                panelContainer.innerHTML = info;
                
                // Si el servidor ya incluye el HTML del reporte
                if (data.html) {
                    console.log('HTML recibido del servidor, mostrando reporte');
                    panelContainer.innerHTML += `
                        <div class="contract-info">
                            <p>✅ Archivo procesado correctamente</p>
                        </div>
                        <div class="report-section">
                            <h2>Análisis del Contrato</h2>
                            ${data.html}
                        </div>
                    `;
                    console.log('Reporte mostrado en el panel');
                } else {
                    console.log('No se recibió HTML, solicitando análisis');
                    panelContainer.innerHTML += `
                        <div class="contract-info">
                            <p>✅ Archivo guardado como input.pdf</p>
                            <div class="loading-indicator">
                                <p>Analizando contrato... Por favor espere.</p>
                                <div class="spinner"></div>
                            </div>
                        </div>
                    `;
                    
                    // Si el servidor no incluye el HTML, hacer otra petición para analizarlo
                    console.log('Iniciando temporizador para solicitar análisis en 1 segundo');
                    setTimeout(analyzeContract, 1000);
                }
            } else {
                console.error('Error en la respuesta del servidor:', data.error);
                throw new Error(data.error);
            }
        })
        .catch(error => {
            console.error('Error en la petición:', error);
            panelContainer.innerHTML = `
                <div class="contract-info">
                    <h3>Archivo cargado:</h3>
                    <p><strong>Nombre:</strong> ${file.name}</p>
                    <p><strong>Tamaño:</strong> ${(file.size / 1024).toFixed(2)} KB</p>
                    <p><strong>Tipo:</strong> ${file.type}</p>
                </div>
                <div class="contract-info" style="border-left-color: #f44336;">
                    <p>❌ Error al procesar el archivo: ${error.message}</p>
                    <p>Por favor, verifica la conexión al servidor o inténtalo de nuevo.</p>
                </div>
            `;
        });
    };
    
    fileInput.click();
}

// Función para analizar el contrato
function analyzeContract() {
    const panelContainer = document.getElementById('panel-container');
    
    // Usar la IP directa para evitar problemas de CORS
    const serverUrl = `http://127.0.0.1:5000/analyze?format=html&t=${Date.now()}`; // Añadir timestamp para evitar caché
    console.log(`Solicitando análisis desde: ${serverUrl}`);
    
    // Mostrar mensaje de que se está realizando el análisis
    const loadingMessage = document.querySelector('.loading-indicator');
    if (loadingMessage) {
        const messageText = loadingMessage.querySelector('p');
        if (messageText) {
            messageText.textContent = 'Conectando con el servidor para análisis...';
        }
    }
    
    fetch(serverUrl, {
        method: 'GET',
        mode: 'cors',  // Asegurarse de que las solicitudes cross-origin funcionen
        credentials: 'omit' // No enviar cookies ni credenciales para evitar problemas CORS
    })
    .then(response => {
        console.log('Respuesta de análisis recibida:', response.status, response.statusText);
        
        if (loadingMessage) {
            const messageText = loadingMessage.querySelector('p');
            if (messageText) {
                messageText.textContent = 'Procesando respuesta del servidor...';
            }
        }
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status} ${response.statusText}`);
        }
        
        // Intentar leer el texto primero para diagnosticar cualquier problema
        return response.text().then(text => {
            console.log(`Respuesta recibida del servidor (primeros 200 caracteres): ${text.substring(0, 200)}`);
            try {
                // Intentar parsear como JSON
                return JSON.parse(text);
            } catch (error) {
                console.error("Error al parsear JSON:", error);
                console.error("Texto recibido:", text);
                throw new Error("Error al parsear la respuesta del servidor como JSON");
            }
        });
    })
    .then(data => {
        console.log('Datos del análisis procesados:', data.success ? 'Éxito' : 'Error');
        
        if (data.success) {
            // Eliminar el indicador de carga
            const loadingIndicator = document.querySelector('.loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
            
            if (!data.html) {
                console.error('No se recibió contenido HTML en la respuesta');
                throw new Error('No se recibió contenido HTML del servidor');
            }
            
            console.log(`HTML recibido (longitud: ${data.html.length} caracteres)`);
            
            // Añadir el reporte HTML al panel
            panelContainer.innerHTML += `
                <div class="report-section">
                    <h2>Análisis del Contrato</h2>
                    ${data.html}
                </div>
            `;
            
            console.log('Reporte HTML mostrado en el panel');
        } else {
            console.error('Error en la respuesta:', data.error);
            throw new Error(data.error || 'Error desconocido en el servidor');
        }
    })
    .catch(error => {
        console.error('Error al analizar contrato:', error);
        
        // Eliminar el indicador de carga
        const loadingIndicator = document.querySelector('.loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
        
        panelContainer.innerHTML += `
            <div class="contract-info" style="border-left-color: #f44336;">
                <p>❌ Error al analizar el contrato: ${error.message}</p>
                <p>Comprueba la consola del navegador (F12) para más detalles.</p>
            </div>
        `;
    });
}