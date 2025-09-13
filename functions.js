// Función para mostrar un mensaje flash que desaparece después de 2 segundos
function showFlashMessage(message, type = 'success', container = null, duration = 2000) {
    // Si no se proporciona un contenedor, usar el panel principal
    if (!container) {
        container = document.getElementById('panel-container');
        if (!container) return;
    }
    
    // Eliminar cualquier mensaje flash previo del mismo tipo
    const existingFlashes = container.querySelectorAll(`.flash-${type}`);
    existingFlashes.forEach(flash => {
        if (flash.parentNode) {
            flash.parentNode.removeChild(flash);
        }
    });
    
    // Crear el elemento del mensaje flash
    const flashDiv = document.createElement('div');
    flashDiv.className = `flash-message flash-${type}`;
    flashDiv.style.opacity = '1'; // Asegurarse de que sea visible inicialmente
    flashDiv.innerHTML = message;
    
    // Añadir al inicio del contenedor
    if (container.firstChild) {
        container.insertBefore(flashDiv, container.firstChild);
    } else {
        container.appendChild(flashDiv);
    }
    
    // Configurar para que se elimine después del tiempo especificado
    setTimeout(() => {
        // Aplicar animación de desvanecimiento
        flashDiv.style.opacity = '0';
        flashDiv.style.transform = 'translateY(-10px)';
        flashDiv.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        // Eliminar después de que termine la animación
        setTimeout(() => {
            if (flashDiv.parentNode) {
                flashDiv.parentNode.removeChild(flashDiv);
            }
        }, 500);
    }, duration);
    
    return flashDiv;
}

// Verificar la conexión al cargar la página y luego cada 10 segundos
// Función para expandir/colapsar una tarjeta de reporte
function toggleReportCard(id) {
    const card = document.getElementById(id);
    if (card) {
        card.classList.toggle('expanded');
    }
}

// Función para eliminar un elemento por su ID
function removeElement(id, event) {
    if (event) {
        event.stopPropagation(); // Evitar que el click se propague al header
    }
    const element = document.getElementById(id);
    if (element && element.parentNode) {
        // Mostrar mensaje flash de información
        showFlashMessage('Reporte cerrado', 'info');
        
        // Animación de desvanecimiento antes de eliminar
        element.style.opacity = '0';
        element.style.transform = 'translateY(-20px)';
        element.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 300);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("Inicializando la aplicación...");
    checkServerConnection();
    setInterval(checkServerConnection, 10000);
    
    // Hacer las funciones accesibles globalmente
    window.toggleReportCard = toggleReportCard;
    window.removeElement = removeElement;
    window.clearSavedReports = clearSavedReports;
    
    // Cargar reportes guardados desde localStorage
    loadSavedReports();
});

// Función para obtener la URL base del servidor
function getServerBaseUrl() {
    // Si estamos en localhost, usar también localhost para el servidor
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://127.0.0.1:5000';
    }
    
    // En otro caso, intentar usar la misma IP pero puerto 5000
    return `http://${window.location.hostname}:5000`;
}

// Función para verificar el estado de la conexión al servidor
function checkServerConnection() {
    const indicator = document.getElementById('server-indicator');
    const statusText = document.getElementById('server-status-text');
    
    // Usar URL dinámica basada en la ubicación actual
    const serverUrl = `${getServerBaseUrl()}/?t=${Date.now()}`; // Añadir timestamp para evitar caché
    
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
        // No mostramos la información del archivo, solo informamos que estamos procesando
        panelContainer.innerHTML = "";
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
        
        // Usar URL dinámica basada en la ubicación actual
        const serverUrl = `${getServerBaseUrl()}/upload`;
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
                panelContainer.innerHTML = "";
                
                // Si el servidor ya incluye el HTML del reporte
                if (data.html) {
                    console.log('HTML recibido del servidor, mostrando reporte');
                    
                    // Mostrar mensaje flash de éxito
                    showFlashMessage('✅ Archivo procesado correctamente', 'success');
                    
                    // Crear ID único para esta tarjeta
                    const reportId = 'report-' + Date.now();
                    
                    // Mostrar el reporte como tarjeta colapsable
                    panelContainer.innerHTML += `
                        <div id="${reportId}" class="report-card">
                            <div class="report-card-header" onclick="toggleReportCard('${reportId}')">
                                <h3>Análisis del Contrato: ${file.name}</h3>
                                <div style="display: flex; align-items: center;">
                                    <button type="button" class="report-card-toggle" title="Expandir/Colapsar">▼</button>
                                    <button type="button" class="report-card-close" title="Cerrar reporte" onclick="removeElement('${reportId}', event)">×</button>
                                </div>
                            </div>
                            <div class="report-card-content">
                                ${data.html}
                            </div>
                        </div>
                    `;
                    
                    // Guardar el reporte en localStorage
                    saveReportToLocalStorage(reportId, file.name, data.html);
                    
                    // Expandir automáticamente la tarjeta
                    setTimeout(() => toggleReportCard(reportId), 100);
                    
                    console.log('Reporte mostrado en el panel');
                } else {
                    console.log('No se recibió HTML, solicitando análisis');
                    
                    // Mostrar mensaje flash de éxito
                    showFlashMessage('✅ Archivo guardado como input.pdf', 'success');
                    
                    // Mostrar indicador de carga
                    panelContainer.innerHTML += `
                        <div class="loading-indicator">
                            <p>Analizando contrato... Por favor espere.</p>
                            <div class="spinner"></div>
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
            
            // Mostrar información del archivo
            panelContainer.innerHTML = `
                <div class="contract-info">
                    <h3>Archivo cargado:</h3>
                    <p><strong>Nombre:</strong> ${file.name}</p>
                    <p><strong>Tamaño:</strong> ${(file.size / 1024).toFixed(2)} KB</p>
                    <p><strong>Tipo:</strong> ${file.type}</p>
                </div>
            `;
            
            // Mostrar mensaje de error como flash
            showFlashMessage(`❌ Error al procesar el archivo: ${error.message}. Por favor, verifica la conexión al servidor o inténtalo de nuevo.`, 'error', panelContainer, 5000);
        });
    };
    
    fileInput.click();
}

// Función para expandir/colapsar una tarjeta de reporte
function toggleReportCard(id) {
    const reportCard = document.getElementById(id);
    if (reportCard) {
        reportCard.classList.toggle('expanded');
        
        // Cambiar el ícono del botón
        const toggleBtn = reportCard.querySelector('.report-card-toggle');
        if (toggleBtn) {
            toggleBtn.textContent = reportCard.classList.contains('expanded') ? '▲' : '▼';
        }
    }
}

// Función para eliminar una tarjeta de reporte
function removeElement(id, event) {
    if (event) {
        event.stopPropagation(); // Evitar que el clic se propague al elemento padre
    }
    const element = document.getElementById(id);
    if (element) {
        // Animar la salida
        element.style.opacity = '0';
        element.style.transform = 'scale(0.9)';
        
        // Eliminar después de la animación
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
                
                // Eliminar también del almacenamiento local
                removeReportFromLocalStorage(id);
            }
        }, 300);
    }
}

// Función para analizar el contrato
function analyzeContract() {
    const panelContainer = document.getElementById('panel-container');
    
    // Usar URL dinámica basada en la ubicación actual
    const serverUrl = `${getServerBaseUrl()}/analyze?format=html&t=${Date.now()}`; // Añadir timestamp para evitar caché
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
            
            // Crear ID único para esta tarjeta
            const reportId = 'report-' + Date.now();
            
            // Añadir el reporte HTML al panel como tarjeta colapsable
            panelContainer.innerHTML += `
                <div id="${reportId}" class="report-card">
                    <div class="report-card-header" onclick="toggleReportCard('${reportId}')">
                        <h3>Análisis del Contrato</h3>
                        <div style="display: flex; align-items: center;">
                            <button type="button" class="report-card-toggle" title="Expandir/Colapsar">▼</button>
                            <button type="button" class="report-card-close" title="Cerrar reporte" onclick="removeElement('${reportId}', event)">×</button>
                        </div>
                    </div>
                    <div class="report-card-content">
                        ${data.html}
                    </div>
                </div>
            `;
            
            // Guardar el reporte en localStorage
            saveReportToLocalStorage(reportId, "Análisis del Contrato", data.html);
            
            // Expandir automáticamente la tarjeta
            setTimeout(() => toggleReportCard(reportId), 100);
            
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
        
        // Mostrar mensaje de error como flash
        showFlashMessage(`❌ Error al analizar el contrato: ${error.message}. Comprueba la consola del navegador (F12) para más detalles.`, 'error', panelContainer, 5000);
    });
}

// Función para guardar un reporte en localStorage
function saveReportToLocalStorage(reportId, title, htmlContent) {
    try {
        // Obtener los reportes existentes o inicializar un arreglo vacío
        let savedReports = JSON.parse(localStorage.getItem('contractReports')) || [];
        
        // Añadir el nuevo reporte
        savedReports.push({
            id: reportId,
            title: title,
            html: htmlContent,
            date: new Date().toISOString()
        });
        
        // Limitar a los 5 reportes más recientes para no sobrecargar el localStorage
        if (savedReports.length > 5) {
            savedReports = savedReports.slice(-5);
        }
        
        // Guardar en localStorage
        localStorage.setItem('contractReports', JSON.stringify(savedReports));
        console.log('Reporte guardado en localStorage:', reportId);
    } catch (error) {
        console.error('Error al guardar el reporte en localStorage:', error);
    }
}

// Función para eliminar un reporte del localStorage
function removeReportFromLocalStorage(reportId) {
    try {
        // Obtener los reportes existentes
        const savedReports = JSON.parse(localStorage.getItem('contractReports')) || [];
        
        // Filtrar el reporte a eliminar
        const filteredReports = savedReports.filter(report => report.id !== reportId);
        
        // Guardar la lista actualizada
        localStorage.setItem('contractReports', JSON.stringify(filteredReports));
        console.log('Reporte eliminado de localStorage:', reportId);
    } catch (error) {
        console.error('Error al eliminar el reporte de localStorage:', error);
    }
}

// Función para cargar reportes guardados desde localStorage
function loadSavedReports() {
    try {
        // Obtener los reportes guardados
        const savedReports = JSON.parse(localStorage.getItem('contractReports')) || [];
        
        if (savedReports.length > 0) {
            const panelContainer = document.getElementById('panel-container');
            
            // Mostrar mensaje flash informando que se han cargado reportes
            if (savedReports.length > 0) {
                showFlashMessage(`ℹ️ Se han cargado ${savedReports.length} reportes guardados`, 'info');
            }
            
            // Mostrar cada reporte como una tarjeta
            savedReports.forEach(report => {
                panelContainer.innerHTML += `
                    <div id="${report.id}" class="report-card">
                        <div class="report-card-header" onclick="toggleReportCard('${report.id}')">
                            <h3>${report.title}</h3>
                            <div style="display: flex; align-items: center;">
                                <button type="button" class="report-card-toggle" title="Expandir/Colapsar">▼</button>
                                <button type="button" class="report-card-close" title="Cerrar reporte" onclick="removeElement('${report.id}', event)">×</button>
                            </div>
                        </div>
                        <div class="report-card-content">
                            ${report.html}
                        </div>
                    </div>
                `;
            });
            
            console.log(`Cargados ${savedReports.length} reportes desde localStorage`);
        }
    } catch (error) {
        console.error('Error al cargar reportes desde localStorage:', error);
    }
}

// Función para limpiar todos los reportes guardados
function clearSavedReports() {
    try {
        // Verificar si hay reportes guardados
        const savedReports = JSON.parse(localStorage.getItem('contractReports')) || [];
        
        if (savedReports.length === 0) {
            showFlashMessage('ℹ️ No hay reportes guardados para eliminar', 'info');
            return;
        }
        
        // Eliminar los reportes del localStorage
        localStorage.removeItem('contractReports');
        
        // Eliminar las tarjetas de reporte del DOM
        const panelContainer = document.getElementById('panel-container');
        const reportCards = panelContainer.querySelectorAll('.report-card');
        
        // Animar la eliminación de cada tarjeta
        reportCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9)';
                
                setTimeout(() => {
                    if (card.parentNode) {
                        card.parentNode.removeChild(card);
                    }
                }, 300);
            }, index * 100); // Eliminar con un pequeño retraso entre cada tarjeta para efecto visual
        });
        
        // Mostrar mensaje de éxito
        showFlashMessage('✅ Todos los reportes han sido eliminados', 'success');
        console.log('Todos los reportes eliminados de localStorage');
    } catch (error) {
        console.error('Error al limpiar reportes:', error);
        showFlashMessage('❌ Error al eliminar reportes: ' + error.message, 'error');
    }
}