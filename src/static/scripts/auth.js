// Authentication Management
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.loginModal = null;
        this.registerModal = null;
        this.init();
    }

    init() {
        this.createAuthModals();
        this.setupEventListeners();
        this.checkAuthStatus();
    }

    createAuthModals() {
        // Create login modal
        this.loginModal = this.createModal('loginModal', 'Login to H2PETRONS', `
            <form id="loginForm">
                <div class="form-group">
                    <label for="loginUsername">Username or Email</label>
                    <input type="text" id="loginUsername" name="username" required>
                </div>
                <div class="form-group">
                    <label for="loginPassword">Password</label>
                    <input type="password" id="loginPassword" name="password" required>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Login</button>
                    <button type="button" class="btn btn-secondary" onclick="authManager.closeModal('loginModal')">Cancel</button>
                </div>
                <p class="auth-switch">
                    Don't have an account? <a href="#" onclick="authManager.showRegister()">Register here</a>
                </p>
            </form>
        `);

        // Create register modal
        this.registerModal = this.createModal('registerModal', 'Register for H2PETRONS', `
            <form id="registerForm">
                <div class="form-group">
                    <label for="registerUsername">Username</label>
                    <input type="text" id="registerUsername" name="username" required minlength="3">
                </div>
                <div class="form-group">
                    <label for="registerEmail">Email</label>
                    <input type="email" id="registerEmail" name="email" required>
                </div>
                <div class="form-group">
                    <label for="registerFirstName">First Name</label>
                    <input type="text" id="registerFirstName" name="first_name">
                </div>
                <div class="form-group">
                    <label for="registerLastName">Last Name</label>
                    <input type="text" id="registerLastName" name="last_name">
                </div>
                <div class="form-group">
                    <label for="registerPassword">Password</label>
                    <input type="password" id="registerPassword" name="password" required minlength="8">
                    <small>Password must be at least 8 characters with uppercase, lowercase, and number</small>
                </div>
                <div class="form-group">
                    <label for="confirmPassword">Confirm Password</label>
                    <input type="password" id="confirmPassword" name="confirmPassword" required>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Register</button>
                    <button type="button" class="btn btn-secondary" onclick="authManager.closeModal('registerModal')">Cancel</button>
                </div>
                <p class="auth-switch">
                    Already have an account? <a href="#" onclick="authManager.showLogin()">Login here</a>
                </p>
            </form>
        `);

        // Add modals to document
        document.body.appendChild(this.loginModal);
        document.body.appendChild(this.registerModal);
    }

    createModal(id, title, content) {
        const modal = document.createElement('div');
        modal.id = id;
        modal.className = 'auth-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="authManager.closeModal('${id}')"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close" onclick="authManager.closeModal('${id}')">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        return modal;
    }

    setupEventListeners() {
        // Login form
        document.addEventListener('submit', async (e) => {
            if (e.target.id === 'loginForm') {
                e.preventDefault();
                await this.handleLogin(e.target);
            } else if (e.target.id === 'registerForm') {
                e.preventDefault();
                await this.handleRegister(e.target);
            }
        });

        // Navigation auth buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('login-btn')) {
                this.showLogin();
            } else if (e.target.classList.contains('register-btn')) {
                this.showRegister();
            } else if (e.target.classList.contains('logout-btn')) {
                this.logout();
            }
        });
    }

    async checkAuthStatus() {
        if (window.api.isAuthenticated()) {
            try {
                const userData = await window.api.getCurrentUser();
                this.currentUser = userData.user;
                this.updateUI();
            } catch (error) {
                console.error('Failed to get current user:', error);
                window.api.clearTokens();
                this.updateUI();
            }
        } else {
            this.updateUI();
        }
    }

    async handleLogin(form) {
        const formData = new FormData(form);
        const username = formData.get('username');
        const password = formData.get('password');

        try {
            this.showLoading('loginForm');
            const response = await window.api.login(username, password);
            this.currentUser = response.user;
            this.closeModal('loginModal');
            this.updateUI();
            this.showMessage('Login successful!', 'success');
        } catch (error) {
            this.showMessage(error.message, 'error');
        } finally {
            this.hideLoading('loginForm');
        }
    }

    async handleRegister(form) {
        const formData = new FormData(form);
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');

        if (password !== confirmPassword) {
            this.showMessage('Passwords do not match', 'error');
            return;
        }

        const userData = {
            username: formData.get('username'),
            email: formData.get('email'),
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            password: password
        };

        try {
            this.showLoading('registerForm');
            const response = await window.api.register(userData);
            this.currentUser = response.user;
            this.closeModal('registerModal');
            this.updateUI();
            this.showMessage('Registration successful! Welcome to H2PETRONS!', 'success');
        } catch (error) {
            this.showMessage(error.message, 'error');
        } finally {
            this.hideLoading('registerForm');
        }
    }

    async logout() {
        try {
            await window.api.logout();
            this.currentUser = null;
            this.updateUI();
            this.showMessage('Logged out successfully', 'success');
        } catch (error) {
            console.error('Logout error:', error);
            // Clear tokens anyway
            window.api.clearTokens();
            this.currentUser = null;
            this.updateUI();
        }
    }

    updateUI() {
        const authButtons = document.querySelector('.auth-buttons');
        const userMenu = document.querySelector('.user-menu');

        if (this.currentUser) {
            // User is logged in
            if (authButtons) {
                authButtons.innerHTML = `
                    <div class="user-menu">
                        <span class="user-greeting">Welcome, ${this.currentUser.username}!</span>
                        <button class="btn btn-secondary logout-btn">Logout</button>
                    </div>
                `;
            }

            // Show/hide elements based on user role
            this.updateRoleBasedUI();
        } else {
            // User is not logged in
            if (authButtons) {
                authButtons.innerHTML = `
                    <button class="btn btn-primary login-btn">Login</button>
                    <button class="btn btn-secondary register-btn">Register</button>
                `;
            }

            // Hide role-based elements
            this.hideRoleBasedUI();
        }
    }

    updateRoleBasedUI() {
        const userRole = this.currentUser?.role || 'user';
        
        // Show/hide research submission based on role
        const submitResearchBtns = document.querySelectorAll('.submit-research-btn');
        submitResearchBtns.forEach(btn => {
            if (userRole === 'researcher' || userRole === 'moderator' || userRole === 'admin') {
                btn.style.display = 'inline-block';
            } else {
                btn.style.display = 'none';
            }
        });

        // Show/hide admin features
        const adminElements = document.querySelectorAll('.admin-only');
        adminElements.forEach(element => {
            if (userRole === 'admin' || userRole === 'moderator') {
                element.style.display = 'block';
            } else {
                element.style.display = 'none';
            }
        });
    }

    hideRoleBasedUI() {
        const roleBasedElements = document.querySelectorAll('.submit-research-btn, .admin-only');
        roleBasedElements.forEach(element => {
            element.style.display = 'none';
        });
    }

    showLogin() {
        this.closeModal('registerModal');
        this.loginModal.style.display = 'block';
        document.getElementById('loginUsername').focus();
    }

    showRegister() {
        this.closeModal('loginModal');
        this.registerModal.style.display = 'block';
        document.getElementById('registerUsername').focus();
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            // Clear form data
            const form = modal.querySelector('form');
            if (form) form.reset();
        }
    }

    showLoading(formId) {
        const form = document.getElementById(formId);
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Loading...';
        }
    }

    hideLoading(formId) {
        const form = document.getElementById(formId);
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = formId === 'loginForm' ? 'Login' : 'Register';
        }
    }

    showMessage(message, type = 'info') {
        // Create or update message element
        let messageEl = document.getElementById('auth-message');
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.id = 'auth-message';
            messageEl.className = 'auth-message';
            document.body.appendChild(messageEl);
        }

        messageEl.className = `auth-message ${type}`;
        messageEl.textContent = message;
        messageEl.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 5000);
    }

    // Utility methods
    isAuthenticated() {
        return !!this.currentUser;
    }

    getCurrentUser() {
        return this.currentUser;
    }

    hasRole(role) {
        if (!this.currentUser) return false;
        
        const roleHierarchy = {
            'user': 1,
            'researcher': 2,
            'moderator': 3,
            'admin': 4
        };

        const userLevel = roleHierarchy[this.currentUser.role] || 0;
        const requiredLevel = roleHierarchy[role] || 0;
        
        return userLevel >= requiredLevel;
    }
}

// Initialize auth manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
});

