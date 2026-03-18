// Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let selectedFile = null;
let extractedEvents = [];

// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const eventsSection = document.getElementById('eventsSection');
const eventsTableBody = document.getElementById('eventsTableBody');
const eventCount = document.getElementById('eventCount');
const addToCalendarBtn = document.getElementById('addToCalendarBtn');
const selectAllCheckbox = document.getElementById('selectAll');
const messageBox = document.getElementById('messageBox');

// Event Listeners
uploadBox.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
uploadBtn.addEventListener('click', handleUpload);
addToCalendarBtn.addEventListener('click', handleAddToCalendar);
selectAllCheckbox.addEventListener('change', handleSelectAll);

// Drag and Drop
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('drag-over');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('drag-over');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// File Handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    const allowedTypes = ['application/pdf', 'text/plain', 'text/markdown'];
    const allowedExtensions = ['.pdf', '.txt', '.text', '.md'];
    
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        showMessage('Please upload a PDF or text file', 'error');
        return;
    }

    selectedFile = file;
    uploadBox.classList.add('has-file');
    uploadBox.querySelector('.upload-text').innerHTML = 
        `✓ ${file.name} <br><span class="browse-link">Choose different file</span>`;
    uploadBtn.disabled = false;
}

// Upload and Extract Events
async function handleUpload() {
    if (!selectedFile) return;

    // Show loading
    loadingSpinner.classList.remove('hidden');
    eventsSection.classList.add('hidden');
    uploadBtn.disabled = true;
    hideMessage();

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch(`${API_BASE_URL}/extract-events`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to extract events');
        }

        extractedEvents = data.events;
        displayEvents(extractedEvents);
        showMessage(`✓ Successfully extracted ${extractedEvents.length} events!`, 'success');

    } catch (error) {
        console.error('Error:', error);
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        loadingSpinner.classList.add('hidden');
        uploadBtn.disabled = false;
    }
}

// Display Events in Table
function displayEvents(events) {
    if (events.length === 0) {
        eventsSection.classList.add('hidden');
        showMessage('No events found in the syllabus', 'error');
        return;
    }

    eventsTableBody.innerHTML = '';
    eventCount.textContent = events.length;

    events.forEach((event, index) => {
        const row = document.createElement('tr');
        row.dataset.index = index;
        
        row.innerHTML = `
            <td>
                <input type="checkbox" class="event-checkbox" checked data-index="${index}">
            </td>
            <td>
                <strong>${escapeHtml(event.title)}</strong>
                ${event.description ? `<br><small style="color: #666;">${escapeHtml(event.description)}</small>` : ''}
            </td>
            <td>
                <span class="event-type-badge type-${event.event_type}">
                    ${event.event_type}
                </span>
            </td>
            <td>${formatDate(event.start_date)}</td>
            <td>${event.start_time || 'All Day'}</td>
            <td>
                <button class="btn btn-delete" onclick="deleteEvent(${index})">
                    Delete
                </button>
            </td>
        `;

        eventsTableBody.appendChild(row);
    });

    eventsSection.classList.remove('hidden');
}

// Add Events to Google Calendar
async function handleAddToCalendar() {
    const selectedEvents = getSelectedEvents();

    if (selectedEvents.length === 0) {
        showMessage('Please select at least one event to add', 'error');
        return;
    }

    addToCalendarBtn.disabled = true;
    addToCalendarBtn.textContent = 'Adding to Calendar...';
    hideMessage();

    try {
        const response = await fetch(`${API_BASE_URL}/add-to-calendar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                events: selectedEvents
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to add events to calendar');
        }

        // Show results
        const successCount = data.created.length;
        const failCount = data.failed.length;

        if (data.success) {
            showMessage(`✓ Successfully added ${successCount} events to your Google Calendar!`, 'success');
            
            // Show calendar links
            if (data.created.length > 0) {
                const linksHtml = data.created.map(event => 
                    `<a href="${event.link}" target="_blank" style="color: #667eea;">${event.title}</a>`
                ).join(', ');
                showMessage(
                    `✓ Successfully added ${successCount} events! View: ${linksHtml}`, 
                    'success'
                );
            }
        } else {
            showMessage(
                `⚠️ Partially successful: ${successCount} added, ${failCount} failed`, 
                'error'
            );
        }

    } catch (error) {
        console.error('Error:', error);
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        addToCalendarBtn.disabled = false;
        addToCalendarBtn.textContent = '📅 Add All to Google Calendar';
    }
}

// Helper Functions
function getSelectedEvents() {
    const checkboxes = document.querySelectorAll('.event-checkbox:checked');
    const selected = [];
    
    checkboxes.forEach(checkbox => {
        const index = parseInt(checkbox.dataset.index);
        selected.push(extractedEvents[index]);
    });
    
    return selected;
}

function deleteEvent(index) {
    const row = document.querySelector(`tr[data-index="${index}"]`);
    row.remove();
    extractedEvents.splice(index, 1);
    
    // Update event count
    eventCount.textContent = extractedEvents.length;
    
    if (extractedEvents.length === 0) {
        eventsSection.classList.add('hidden');
        showMessage('All events removed', 'error');
    }
    
    // Re-index remaining rows
    document.querySelectorAll('#eventsTableBody tr').forEach((row, newIndex) => {
        row.dataset.index = newIndex;
        row.querySelector('.event-checkbox').dataset.index = newIndex;
        row.querySelector('.btn-delete').setAttribute('onclick', `deleteEvent(${newIndex})`);
    });
}

function handleSelectAll(e) {
    const checkboxes = document.querySelectorAll('.event-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = e.target.checked;
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        weekday: 'short',
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function showMessage(message, type) {
    messageBox.textContent = '';
    messageBox.innerHTML = message;
    messageBox.className = `message-box ${type}`;
    messageBox.classList.remove('hidden');
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            messageBox.classList.add('hidden');
        }, 5000);
    }
}

function hideMessage() {
    messageBox.classList.add('hidden');
}
