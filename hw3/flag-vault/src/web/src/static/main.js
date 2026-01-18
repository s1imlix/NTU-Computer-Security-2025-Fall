// Utility functions
function showElement(element) {
    element?.classList.remove('hidden');
}

function hideElement(element) {
    element?.classList.add('hidden');
}

// Flag page functionality
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('editFlagModal');
    const editFlagBtn = document.getElementById('editFlagBtn');
    const editFlagForm = document.getElementById('editFlagForm');
    const closeBtn = modal?.querySelector('.close');
    
    if (!modal) return;
    
    // Edit button handler
    editFlagBtn?.addEventListener('click', function() {
        const flagDisplay = document.querySelector('.flag-display code');
        const flagContentInput = document.getElementById('flagContentInput');
        if (flagContentInput) {
            flagContentInput.value = flagDisplay?.textContent || '';
        }
        showElement(modal);
    });
    
    // Close button handler
    closeBtn?.addEventListener('click', () => hideElement(modal));
    
    // Click outside modal to close
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            hideElement(modal);
        }
    });
    
    // Form submission handler
    editFlagForm?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const errorDiv = document.getElementById('editError');
        hideElement(errorDiv);
        
        try {
            const formData = new FormData(editFlagForm);
            const response = await fetch('/api/flag/', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                hideElement(modal);
                window.location.reload();
            } else {
                const error = await response.json();
                if (errorDiv) {
                    errorDiv.textContent = error.detail || 'Failed to save flag';
                    showElement(errorDiv);
                }
            }
        } catch (error) {
            if (errorDiv) {
                errorDiv.textContent = 'An error occurred, please try again later';
                showElement(errorDiv);
            }
        }
    });
});
