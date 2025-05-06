/**
 * Main JavaScript file for Hotel Accounting System
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Add active class to current nav item
    var currentLocation = window.location.pathname;
    var navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
    
    // Format currency inputs
    var currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function(e) {
            var value = parseFloat(this.value.replace(/[^\d.-]/g, ''));
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });
    
    // Date picker initialization for date inputs
    var dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        if (!input.value) {
            var today = new Date();
            var dd = String(today.getDate()).padStart(2, '0');
            var mm = String(today.getMonth() + 1).padStart(2, '0');
            var yyyy = today.getFullYear();
            
            today = yyyy + '-' + mm + '-' + dd;
            input.value = today;
        }
    });
    
    // Confirm delete actions
    var deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Toggle password visibility
    var togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var input = document.querySelector(this.getAttribute('data-target'));
            if (input.type === 'password') {
                input.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                input.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });
    
    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Attendance marking - calculate status based on shifts
    var morningCheckboxes = document.querySelectorAll('.morning-present');
    var eveningCheckboxes = document.querySelectorAll('.evening-present');
    var statusElements = document.querySelectorAll('.attendance-status');
    
    function updateAttendanceStatus(index) {
        if (morningCheckboxes[index] && eveningCheckboxes[index] && statusElements[index]) {
            var morningPresent = morningCheckboxes[index].checked;
            var eveningPresent = eveningCheckboxes[index].checked;
            var statusElement = statusElements[index];
            
            if (morningPresent && eveningPresent) {
                statusElement.textContent = 'Present';
                statusElement.className = 'attendance-status attendance-status-present';
            } else if (morningPresent || eveningPresent) {
                statusElement.textContent = 'Half-day';
                statusElement.className = 'attendance-status attendance-status-half-day';
            } else {
                statusElement.textContent = 'Absent';
                statusElement.className = 'attendance-status attendance-status-absent';
            }
        }
    }
    
    morningCheckboxes.forEach(function(checkbox, index) {
        checkbox.addEventListener('change', function() {
            updateAttendanceStatus(index);
        });
    });
    
    eveningCheckboxes.forEach(function(checkbox, index) {
        checkbox.addEventListener('change', function() {
            updateAttendanceStatus(index);
        });
    });
    
    // Payroll calculation
    var calculatePayrollBtn = document.getElementById('calculate-payroll');
    if (calculatePayrollBtn) {
        calculatePayrollBtn.addEventListener('click', function() {
            var employeeId = document.getElementById('employee_id').value;
            var periodStart = document.getElementById('period_start').value;
            var periodEnd = document.getElementById('period_end').value;
            
            if (employeeId && periodStart && periodEnd) {
                fetch('/api/payroll/calculate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        employee_id: employeeId,
                        period_start: periodStart,
                        period_end: periodEnd
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('employee_name').textContent = data.employee_name;
                    document.getElementById('total_days').textContent = data.total_days;
                    document.getElementById('present_days').textContent = data.present_days;
                    document.getElementById('half_days').textContent = data.half_days;
                    document.getElementById('absent_days').textContent = data.absent_days;
                    document.getElementById('weekoff_days').textContent = data.weekoff_days;
                    document.getElementById('weekoff_worked').textContent = data.weekoff_worked;
                    document.getElementById('base_salary').textContent = '₹' + data.base_salary.toFixed(2);
                    document.getElementById('weekoff_pay').textContent = '₹' + data.weekoff_pay.toFixed(2);
                    document.getElementById('net_salary').textContent = '₹' + data.net_salary.toFixed(2);
                    
                    document.getElementById('payroll-details').classList.remove('d-none');
                })
                .catch((error) => {
                    console.error('Error:', error);
                    alert('Failed to calculate payroll. Please try again.');
                });
            } else {
                alert('Please select employee and date range.');
            }
        });
    }
});