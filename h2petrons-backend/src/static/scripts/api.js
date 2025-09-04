// API Client for H2PETRONS Backend
class H2PetronsAPI {
    constructor() {
        this.baseURL = '/api';
        this.token = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    // Helper method to make HTTP requests
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Add authorization header if token exists
        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            
            // Handle token refresh if needed
            if (response.status === 401 && this.refreshToken) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    config.headers['Authorization'] = `Bearer ${this.token}`;
                    return await fetch(url, config);
                }
            }

            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Authentication methods
    async login(username, password) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            this.setTokens(data.access_token, data.refresh_token);
            return data;
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Login failed');
        }
    }

    async register(userData) {
        const response = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });

        if (response.ok) {
            const data = await response.json();
            this.setTokens(data.access_token, data.refresh_token);
            return data;
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Registration failed');
        }
    }

    async logout() {
        try {
            await this.request('/auth/logout', { method: 'POST' });
        } catch (error) {
            console.error('Logout request failed:', error);
        } finally {
            this.clearTokens();
        }
    }

    async refreshAccessToken() {
        if (!this.refreshToken) return false;

        try {
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.refreshToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access_token;
                localStorage.setItem('access_token', this.token);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }

        this.clearTokens();
        return false;
    }

    async getCurrentUser() {
        const response = await this.request('/auth/me');
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to get current user');
    }

    // Token management
    setTokens(accessToken, refreshToken) {
        this.token = accessToken;
        this.refreshToken = refreshToken;
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }

    clearTokens() {
        this.token = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    isAuthenticated() {
        return !!this.token;
    }

    // Research methods
    async getResearchPapers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/research${queryString ? '?' + queryString : ''}`;
        const response = await this.request(endpoint);
        
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch research papers');
    }

    async getResearchPaper(id) {
        const response = await this.request(`/research/${id}`);
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch research paper');
    }

    async submitResearchPaper(formData) {
        const response = await this.request('/research', {
            method: 'POST',
            headers: {}, // Don't set Content-Type for FormData
            body: formData
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to submit research paper');
        }
    }

    async getMyResearchPapers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/research/my-papers${queryString ? '?' + queryString : ''}`;
        const response = await this.request(endpoint);
        
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch your research papers');
    }

    async likeResearchPaper(id) {
        const response = await this.request(`/research/${id}/like`, {
            method: 'POST'
        });

        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to like research paper');
    }

    async getResearchCategories() {
        const response = await this.request('/research/categories');
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch research categories');
    }

    // News methods
    async getNewsArticles(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/news${queryString ? '?' + queryString : ''}`;
        const response = await this.request(endpoint);
        
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch news articles');
    }

    async getNewsArticle(id) {
        const response = await this.request(`/news/${id}`);
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch news article');
    }

    async getFeaturedNews() {
        const response = await this.request('/news/featured');
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch featured news');
    }

    async getNewsCategories() {
        const response = await this.request('/news/categories');
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch news categories');
    }

    // Community methods
    async getForumCategories() {
        const response = await this.request('/forum/categories');
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch forum categories');
    }

    async getForumTopics(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/forum/topics${queryString ? '?' + queryString : ''}`;
        const response = await this.request(endpoint);
        
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch forum topics');
    }

    async getForumTopic(id, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/forum/topics/${id}${queryString ? '?' + queryString : ''}`;
        const response = await this.request(endpoint);
        
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch forum topic');
    }

    async createForumTopic(topicData) {
        const response = await this.request('/forum/topics', {
            method: 'POST',
            body: JSON.stringify(topicData)
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create forum topic');
        }
    }

    async createForumPost(topicId, content) {
        const response = await this.request(`/forum/topics/${topicId}/posts`, {
            method: 'POST',
            body: JSON.stringify({ content })
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create forum post');
        }
    }

    async getInterestGroups(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/groups${queryString ? '?' + queryString : ''}`;
        const response = await this.request(endpoint);
        
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch interest groups');
    }

    async createInterestGroup(groupData) {
        const response = await this.request('/groups', {
            method: 'POST',
            body: JSON.stringify(groupData)
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create interest group');
        }
    }

    async getCommunityEvents(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/events${queryString ? '?' + queryString : ''}`;
        const response = await this.request(endpoint);
        
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch community events');
    }

    async createCommunityEvent(eventData) {
        const response = await this.request('/events', {
            method: 'POST',
            body: JSON.stringify(eventData)
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create community event');
        }
    }

    async attendEvent(eventId) {
        const response = await this.request(`/events/${eventId}/attend`, {
            method: 'POST'
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to register for event');
        }
    }

    // User methods
    async getUsers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/users${queryString ? '?' + queryString : ''}`;
        const response = await this.request(endpoint);
        
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch users');
    }

    async getUser(id) {
        const response = await this.request(`/users/${id}`);
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch user');
    }

    async updateProfile(profileData) {
        const response = await this.request('/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update profile');
        }
    }

    // Statistics methods
    async getResearchStats() {
        const response = await this.request('/research/stats');
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch research statistics');
    }

    async getNewsStats() {
        const response = await this.request('/news/stats');
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch news statistics');
    }

    async getCommunityStats() {
        const response = await this.request('/community/stats');
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Failed to fetch community statistics');
    }
}

// Create global API instance
window.api = new H2PetronsAPI();

