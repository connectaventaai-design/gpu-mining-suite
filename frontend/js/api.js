// API Wrapper Functions
const API = {
    baseURL: window.location.origin,

    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    },

    // GPU Monitoring
    async getGPUStats() {
        return await this.request('/api/gpu/stats');
    },

    async getGPUInfo() {
        return await this.request('/api/gpu/info');
    },

    async getGPUHistory(hours = 24) {
        return await this.request(`/api/gpu/history?hours=${hours}`);
    },

    // Miner Control
    async getMinerStatus() {
        return await this.request('/api/miner/status');
    },

    async startMining(coin, pool = null, wallet = null) {
        return await this.request('/api/miner/start', {
            method: 'POST',
            body: JSON.stringify({ coin, pool, wallet })
        });
    },

    async stopMining() {
        return await this.request('/api/miner/stop', {
            method: 'POST'
        });
    },

    async restartMining() {
        return await this.request('/api/miner/restart', {
            method: 'POST'
        });
    },

    async switchCoin(coin) {
        return await this.request('/api/miner/switch', {
            method: 'POST',
            body: JSON.stringify({ coin })
        });
    },

    // Profitability
    async getProfitability(electricityCost = 0.12) {
        return await this.request(`/api/profit?electricity_cost=${electricityCost}`);
    },

    async getBestCoin(electricityCost = 0.12) {
        return await this.request(`/api/profit/best?electricity_cost=${electricityCost}`);
    },

    async getCoinPrices() {
        return await this.request('/api/profit/prices');
    },

    // Earnings
    async getEarnings(period = 'today') {
        return await this.request(`/api/earnings?period=${period}`);
    },

    async getEarningsHistory(hours = 168) {
        return await this.request(`/api/earnings/history?hours=${hours}`);
    },

    // Overclock
    async getOverclockProfiles() {
        return await this.request('/api/overclock/profiles');
    },

    async getCurrentOverclock() {
        return await this.request('/api/overclock/current');
    },

    async applyOverclock(gpuId, profile) {
        return await this.request('/api/overclock/apply', {
            method: 'POST',
            body: JSON.stringify({ gpu_id: gpuId, profile })
        });
    },

    async resetOverclock(gpuId = 0) {
        return await this.request('/api/overclock/reset', {
            method: 'POST',
            body: JSON.stringify({ gpu_id: gpuId })
        });
    },

    // Settings
    async getSettings() {
        return await this.request('/api/settings');
    },

    async updateSettings(settings) {
        return await this.request('/api/settings', {
            method: 'POST',
            body: JSON.stringify(settings)
        });
    },

    async testNotifications() {
        return await this.request('/api/settings/test-notification', {
            method: 'POST'
        });
    },

    // System
    async getSystemInfo() {
        return await this.request('/api/system/info');
    },

    async getLogs() {
        return await this.request('/api/system/logs');
    }
};
