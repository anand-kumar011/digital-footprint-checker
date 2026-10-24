// Global state
let manualNumbers = [];
let uploadedFileName = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('uploadArea').addEventListener('click', function() {
        document.getElementById('fileInput').click();
    });
    
    updateUI();
});

// Add mobile number
function addNumber() {
    const input = document.getElementById('mobileInput');
    const number = input.value.trim();
    
    // Validate number
    if (!number) {
        showStatus('Please enter a mobile number', 'error');
        return;
    }
    
    if (!/^\d{10,15}$/.test(number)) {
        showStatus('Please enter a valid 10-15 digit number', 'error');
        return;
    }
    
    if (manualNumbers.includes(number)) {
        showStatus('Number already exists', 'error');
        return;
    }
    
    // Add to backend
    fetch('/api/add-number', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ number: number })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            manualNumbers.push(number);
            input.value = '';
            updateUI();
            showStatus(`${manualNumbers.length} number(s) added`, 'success');
        } else {
            showStatus(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Failed to add number', 'error');
    });
}

// Handle file upload
function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        showStatus('Please upload an Excel file (.xlsx or .xls)', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showStatus('Uploading file...', 'info');
    
    fetch('/api/upload-file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            uploadedFileName = data.filename;
            document.getElementById('uploadText').textContent = `File uploaded: ${file.name} (${data.count} numbers)`;
            updateUI();
            showStatus(`File uploaded: ${data.count} numbers found`, 'success');
        } else {
            showStatus(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Failed to upload file', 'error');
    });
}

// Clear all numbers
function clearAllNumbers() {
    fetch('/api/clear-numbers', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            manualNumbers = [];
            uploadedFileName = null;
            document.getElementById('uploadText').textContent = 'Click to upload Excel file';
            document.getElementById('fileInput').value = '';
            updateUI();
            showStatus('All numbers cleared', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Failed to clear numbers', 'error');
    });
}

// Remove single number
function removeNumber(index) {
    manualNumbers.splice(index, 1);
    
    fetch('/api/clear-numbers', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(() => {
        // Re-add remaining numbers
        const promises = manualNumbers.map(num => 
            fetch('/api/add-number', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ number: num })
            })
        );
        
        return Promise.all(promises);
    })
    .then(() => {
        updateUI();
        showStatus('Number removed', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Failed to remove number', 'error');
    });
}

// Process numbers
function processNumbers() {
    const totalNumbers = manualNumbers.length + (uploadedFileName ? 1 : 0);
    
    if (totalNumbers === 0) {
        showStatus('Please add numbers or upload a file', 'error');
        return;
    }
    
    const processBtn = document.getElementById('processBtn');
    processBtn.disabled = true;
    processBtn.innerHTML = `
        <svg class="btn-icon loading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 6v6l4 2"></path>
        </svg>
        Processing...
    `;
    
    showStatus('Processing numbers...', 'info');
    
    fetch('/api/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            uploaded_file: uploadedFileName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('Downloaded successfully', 'success');
            downloadFile(data.output_file);
            
            // Reset button
            setTimeout(() => {
                processBtn.disabled = false;
                processBtn.innerHTML = `
                    <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    Process & Download
                `;
            }, 1000);
        } else {
            showStatus(data.message, 'error');
            processBtn.disabled = false;
            processBtn.innerHTML = `
                <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                Process & Download
            `;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Processing failed', 'error');
        processBtn.disabled = false;
        processBtn.innerHTML = `
            <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
            Process & Download
        `;
    });
}

// Download file
function downloadFile(filename) {
    const link = document.createElement('a');
    link.href = `/api/download/${filename}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Update UI
function updateUI() {
    const numbersList = document.getElementById('numbersList');
    const numbersContainer = document.getElementById('numbersContainer');
    const numbersCount = document.getElementById('numbersCount');
    const totalCount = document.getElementById('totalCount');
    
    // Update counts
    const total = manualNumbers.length + (uploadedFileName ? '+' : '');
    numbersCount.textContent = manualNumbers.length;
    totalCount.textContent = total;
    
    // Show/hide numbers list
    if (manualNumbers.length > 0) {
        numbersList.style.display = 'block';
        
        // Render numbers
        numbersContainer.innerHTML = manualNumbers.map((num, index) => `
            <div class="number-item">
                <span class="number-value">${num}</span>
                <button class="btn-remove" onclick="removeNumber(${index})">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="15" y1="9" x2="9" y2="15"></line>
                        <line x1="9" y1="9" x2="15" y2="15"></line>
                    </svg>
                </button>
            </div>
        `).join('');
    } else {
        numbersList.style.display = 'none';
    }
}

// Show status message
function showStatus(message, type) {
    const statusText = document.getElementById('statusText');
    statusText.textContent = message;
    
    // Add color based on type
    if (type === 'success') {
        statusText.style.color = '#10b981';
    } else if (type === 'error') {
        statusText.style.color = '#ef4444';
    } else if (type === 'info') {
        statusText.style.color = '#22d3ee';
    } else {
        statusText.style.color = 'white';
    }
    
    // Reset color after 3 seconds
    setTimeout(() => {
        statusText.style.color = 'white';
    }, 3000);
}