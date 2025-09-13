export function loadContract() {
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
        
        fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                panelContainer.innerHTML += `
                    <div class="contract-info">
                        <p>✅ Archivo guardado como input.pdf</p>
                    </div>
                `;
            } else {
                throw new Error(data.error);
            }
        })
        .catch(error => {
            panelContainer.innerHTML += `
                <div class="contract-info" style="border-left-color: #f44336;">
                    <p>❌ Error al guardar el archivo: ${error.message}</p>
                </div>
            `;
        });
    };
    
    fileInput.click();
}