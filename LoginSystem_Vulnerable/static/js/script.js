// Đợi cho DOM tải xong
document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Duyệt qua từng form và thêm event listener
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!validateForm(form)) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Tự động ẩn thông báo flash sau vài giây
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                fadeOut(alert);
            });
        }, 5000); // 5 giây
    }

    // Toggle password visibility
    const passwordToggles = document.querySelectorAll('.toggle-password');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const passwordInput = document.getElementById(targetId);
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.textContent = 'Ẩn';
            } else {
                passwordInput.type = 'password';
                this.textContent = 'Hiện';
            }
        });
    });
});

// Hàm kiểm tra và validate form
function validateForm(form) {
    let isValid = true;
    
    // Kiểm tra các trường input required
    const requiredInputs = form.querySelectorAll('[required]');
    requiredInputs.forEach(input => {
        if (input.value.trim() === '') {
            showError(input, 'Trường này không được để trống');
            isValid = false;
        } else {
            clearError(input);
        }
    });
    
    // Kiểm tra email
    const emailInput = form.querySelector('input[type="email"]');
    if (emailInput && emailInput.value.trim() !== '') {
        if (!isValidEmail(emailInput.value)) {
            showError(emailInput, 'Email không hợp lệ');
            isValid = false;
        } else {
            clearError(emailInput);
        }
    }
    
    // Kiểm tra mật khẩu và xác nhận mật khẩu
    const passwordInput = form.querySelector('input[name="password"]');
    const confirmPasswordInput = form.querySelector('input[name="confirm_password"]');
    
    if (passwordInput && confirmPasswordInput) {
        if (passwordInput.value.length < 8) {
            showError(passwordInput, 'Mật khẩu phải có ít nhất 8 ký tự');
            isValid = false;
        } else {
            clearError(passwordInput);
        }
        
        if (passwordInput.value !== confirmPasswordInput.value) {
            showError(confirmPasswordInput, 'Mật khẩu không khớp');
            isValid = false;
        } else {
            clearError(confirmPasswordInput);
        }
    }
    
    return isValid;
}

// Hiển thị thông báo lỗi
function showError(input, message) {
    const formGroup = input.closest('.form-group');
    const errorMessage = formGroup.querySelector('.invalid-feedback');
    
    input.classList.add('is-invalid');
    
    if (errorMessage) {
        errorMessage.textContent = message;
    } else {
        const newErrorMessage = document.createElement('div');
        newErrorMessage.className = 'invalid-feedback';
        newErrorMessage.textContent = message;
        formGroup.appendChild(newErrorMessage);
    }
}

// Xóa thông báo lỗi
function clearError(input) {
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
}

// Kiểm tra email hợp lệ
function isValidEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

// Hiệu ứng fade out
function fadeOut(element) {
    let opacity = 1;
    const interval = setInterval(() => {
        if (opacity <= 0.1) {
            clearInterval(interval);
            element.style.display = 'none';
        }
        element.style.opacity = opacity;
        opacity -= opacity * 0.1;
    }, 50);
}

// Chế độ tối (Dark mode)
function toggleDarkMode() {
    const body = document.body;
    body.classList.toggle('dark-mode');
    
    // Lưu trạng thái vào localStorage
    const isDarkMode = body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

// Kiểm tra và áp dụng chế độ tối nếu đã được set từ trước
const savedDarkMode = localStorage.getItem('darkMode');
if (savedDarkMode === 'true') {
    document.body.classList.add('dark-mode');
}
