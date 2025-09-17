// URL base del servidor local
const SERVER_BASE_URL = 'http://127.0.0.1:5050';

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

// Función para verificar el estado de la conexión al servidor local
function checkServerConnection() {
    const indicator = document.getElementById('server-indicator');
    const statusText = document.getElementById('server-status-text');
    
    // Añadir timestamp para evitar caché
    const url = `${SERVER_BASE_URL}/status?t=${Date.now()}`;
    
    fetch(url, { method: 'GET' })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        indicator.classList.remove('offline');
        indicator.classList.add('online');
        statusText.textContent = 'Conectado';
        return response.json();
    })
    .catch(error => {
        console.error('Error al verificar conexión:', error);
        indicator.classList.remove('online');
        indicator.classList.add('offline');
        statusText.textContent = 'Desconectado';
    });
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

// Función para cargar y procesar un contrato PDF
function loadContract() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.pdf';
    
    fileInput.onchange = function(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const panelContainer = document.getElementById('panel-container');
        // Limpiar el panel
        panelContainer.innerHTML = "";
        
        // Mostrar indicador de carga mientras se sube el archivo
        panelContainer.innerHTML += `
            <div class="contract-info">
                <p>Subiendo archivo y analizando...</p>
                <div class="loading-indicator">
                    <div class="spinner"></div>
                </div>
            </div>
        `;
        
        console.log('Enviando archivo al servidor local...');
        
        const formData = new FormData();
        formData.append('file', file);
        
        // Enviar el archivo al servidor local
        fetch(`${SERVER_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log('Respuesta recibida del servidor:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status} ${response.statusText}`);
            }
            return response.json();
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
                }
            } else {
                console.error('Error en la respuesta del servidor:', data.error);
                throw new Error(data.error || 'Error desconocido');
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
            showFlashMessage(`❌ Error al procesar el archivo: ${error.message}. Por favor, verifica que el servidor local esté funcionando.`, 'error', panelContainer, 5000);
        });
    };
    
    fileInput.click();
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

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log("Inicializando la aplicación...");
    
    // Hacer las funciones accesibles globalmente
    window.toggleReportCard = toggleReportCard;
    window.removeElement = removeElement;
    window.clearSavedReports = clearSavedReports;
    
    // Verificar la conexión con el servidor
    checkServerConnection();
    
    // Cargar reportes guardados desde localStorage
    loadSavedReports();
});