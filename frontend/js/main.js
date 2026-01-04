// Main Application Logic

const App = {
    refreshInterval: 5000, // 5 seconds
    refreshTimer: null,
    settings: null,

    async initialize() {
        console.log('Initializing GPU Mining Suite Dashboard...');

        // Initialize charts
        Charts.initialize();

        // Setup event listeners
        this.setupEventListeners();

        // Load settings
        await this.loadSettings();

        // Load initial data
        await this.refreshAll();

        // Start auto-refresh
        this.startAutoRefresh();

        console.log('Dashboard initialized successfully');
    },

    setupEventListeners() {
        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Settings modal
        document.getElementById('settings-btn').addEventListener('click', () => {
            this.openSettings();
        });

        document.getElementById('close-settings').addEventListener('click', () => {
            this.closeSettings();
        });

        // Miner controls
        document.getElementById('start-mining-btn').addEventListener('click', () => {
            this.startMining();
        });

        document.getElementById('stop-mining-btn').addEventListener('click', () => {
            this.stopMining();
        });

        document.getElementById('restart-mining-btn').addEventListener('click', () => {
            this.restartMining();
        });

        // Settings actions
        document.getElementById('save-settings-btn').addEventListener('click', () => {
            this.saveSettings();
        });

        document.getElementById('test-notifications-btn').addEventListener('click', () => {
            this.testNotifications();
        });

        // Refresh profitability
        document.getElementById('refresh-profit-btn').addEventListener('click', () => {
            this.updateProfitability();
        });
    },

    async refreshAll() {
        try {
            await Promise.all([
                this.updateGPUStats(),
                this.updateMinerStatus(),
                this.updateProfitability(),
                this.updateEarnings()
            ]);
            
            this.updateConnectionStatus(true);
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.updateConnectionStatus(false);
        }
    },

    async updateGPUStats() {
        try {
            const data = await API.getGPUStats();
            this.displayGPUStats(data);

            // Update charts
            if (data.gpus && data.gpus.length > 0) {
                const gpu = data.gpus[0];
                Charts.updateTempChart(gpu.temperature, gpu.timestamp);
            }

            // Update timestamp
            const updateTime = new Date().toLocaleTimeString();
            document.getElementById('gpu-update-time').textContent = `Updated: ${updateTime}`;
        } catch (error) {
            console.error('Error updating GPU stats:', error);
        }
    },

    displayGPUStats(data) {
        const container = document.getElementById('gpu-stats-container');
        container.innerHTML = '';

        if (!data.gpus || data.gpus.length === 0) {
            container.innerHTML = '<p class="text-muted">No GPU data available</p>';
            return;
        }

        data.gpus.forEach(gpu => {
            const gpuCard = document.createElement('div');
            gpuCard.className = 'gpu-card';

            const tempClass = gpu.temperature > 75 ? 'temp-high' : 'temp-normal';

            gpuCard.innerHTML = `
                <div class="gpu-header">GPU ${gpu.gpu_id}</div>
                <div class="gpu-stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">Temperature</span>
                        <span class="stat-value ${tempClass}">${gpu.temperature}°C</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Fan Speed</span>
                        <span class="stat-value">${gpu.fan_speed}%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Power</span>
                        <span class="stat-value">${gpu.power_draw.toFixed(1)}W</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">GPU Usage</span>
                        <span class="stat-value">${gpu.gpu_utilization}%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Memory</span>
                        <span class="stat-value">${gpu.memory_used}/${gpu.memory_total} MB</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Core Clock</span>
                        <span class="stat-value">${gpu.core_clock} MHz</span>
                    </div>
                </div>
            `;

            container.appendChild(gpuCard);
        });
    },

    async updateMinerStatus() {
        try {
            const status = await API.getMinerStatus();
            this.displayMinerStatus(status);

            // Update hashrate chart
            if (status.mining && status.hashrate) {
                Charts.updateHashrateChart(status.hashrate, Date.now() / 1000);
            }
        } catch (error) {
            console.error('Error updating miner status:', error);
        }
    },

    displayMinerStatus(status) {
        // Update badge
        const badge = document.getElementById('miner-status-badge');
        if (status.mining) {
            badge.textContent = 'Running';
            badge.className = 'badge running';
        } else {
            badge.textContent = status.status === 'crashed' ? 'Crashed' : 'Stopped';
            badge.className = status.status === 'crashed' ? 'badge error' : 'badge stopped';
        }

        // Update info
        document.getElementById('current-coin').textContent = status.coin || '-';
        document.getElementById('current-hashrate').textContent = 
            status.hashrate ? `${status.hashrate.toFixed(2)} MH/s` : '0 MH/s';

        // Format uptime
        const hours = Math.floor(status.uptime / 3600);
        const minutes = Math.floor((status.uptime % 3600) / 60);
        document.getElementById('current-uptime').textContent = `${hours}h ${minutes}m`;

        document.getElementById('current-shares').textContent = 
            `${status.shares_accepted || 0}/${status.shares_rejected || 0}`;

        // Update button states
        const startBtn = document.getElementById('start-mining-btn');
        const stopBtn = document.getElementById('stop-mining-btn');
        const restartBtn = document.getElementById('restart-mining-btn');

        if (status.mining) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            restartBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            restartBtn.disabled = true;
        }
    },

    async updateProfitability() {
        try {
            const data = await API.getProfitability();
            this.displayProfitability(data);
        } catch (error) {
            console.error('Error updating profitability:', error);
        }
    },

    displayProfitability(data) {
        const container = document.getElementById('profit-container');
        container.innerHTML = '';

        if (!data || Object.keys(data).length === 0) {
            container.innerHTML = '<p class="text-muted">No profitability data available</p>';
            return;
        }

        // Sort by daily profit
        const sorted = Object.entries(data).sort((a, b) => 
            b[1].daily_profit - a[1].daily_profit
        );

        sorted.forEach(([coin, profit]) => {
            const profitItem = document.createElement('div');
            profitItem.className = 'profit-item';

            const profitClass = profit.daily_profit > 0 ? '' : 'negative';

            profitItem.innerHTML = `
                <div class="profit-coin">${coin}</div>
                <div class="profit-value ${profitClass}">$${profit.daily_profit.toFixed(2)}/day</div>
            `;

            container.appendChild(profitItem);
        });
    },

    async updateEarnings() {
        try {
            const [today, week, month] = await Promise.all([
                API.getEarnings('today'),
                API.getEarnings('week'),
                API.getEarnings('month')
            ]);

            document.getElementById('earnings-today').textContent = 
                `$${today.total_usd?.toFixed(2) || '0.00'}`;
            document.getElementById('earnings-week').textContent = 
                `$${week.total_usd?.toFixed(2) || '0.00'}`;
            document.getElementById('earnings-month').textContent = 
                `$${month.total_usd?.toFixed(2) || '0.00'}`;

            // Estimate monthly based on today's earnings
            const estimated = (today.total_usd || 0) * 30;
            document.getElementById('earnings-est').textContent = 
                `$${estimated.toFixed(2)}`;
        } catch (error) {
            console.error('Error updating earnings:', error);
        }
    },

    async startMining() {
        const coin = document.getElementById('coin-select').value;
        
        try {
            const result = await API.startMining(coin);
            console.log('Mining started:', result);
            await this.updateMinerStatus();
        } catch (error) {
            console.error('Error starting mining:', error);
            alert('Failed to start mining. Check console for details.');
        }
    },

    async stopMining() {
        try {
            const result = await API.stopMining();
            console.log('Mining stopped:', result);
            await this.updateMinerStatus();
        } catch (error) {
            console.error('Error stopping mining:', error);
            alert('Failed to stop mining. Check console for details.');
        }
    },

    async restartMining() {
        try {
            const result = await API.restartMining();
            console.log('Mining restarted:', result);
            await this.updateMinerStatus();
        } catch (error) {
            console.error('Error restarting mining:', error);
            alert('Failed to restart mining. Check console for details.');
        }
    },

    toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update theme toggle button
        const themeBtn = document.getElementById('theme-toggle');
        themeBtn.textContent = newTheme === 'light' ? '☀️' : '🌙';

        // Update charts
        Charts.updateTheme();
    },

    async loadSettings() {
        try {
            this.settings = await API.getSettings();
            
            // Apply saved theme
            const savedTheme = localStorage.getItem('theme') || 'dark';
            document.documentElement.setAttribute('data-theme', savedTheme);
            document.getElementById('theme-toggle').textContent = savedTheme === 'light' ? '☀️' : '🌙';
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    },

    openSettings() {
        if (!this.settings) return;

        // Populate form
        document.getElementById('wallet-address').value = 
            this.settings.mining?.wallet_address || '';
        document.getElementById('worker-name').value = 
            this.settings.mining?.worker_name || 'GTX1660S';
        document.getElementById('discord-webhook').value = 
            this.settings.notifications?.discord_webhook || '';
        document.getElementById('telegram-token').value = 
            this.settings.notifications?.telegram_token || '';
        document.getElementById('telegram-chat-id').value = 
            this.settings.notifications?.telegram_chat_id || '';
        document.getElementById('enable-alerts').checked = 
            this.settings.notifications?.enable_alerts ?? true;
        document.getElementById('enable-watchdog').checked = 
            this.settings.automation?.enable_watchdog ?? true;
        document.getElementById('enable-auto-switch').checked = 
            this.settings.mining?.auto_switch ?? false;

        // Show modal
        document.getElementById('settings-modal').classList.add('active');
    },

    closeSettings() {
        document.getElementById('settings-modal').classList.remove('active');
    },

    async saveSettings() {
        // Gather form data
        this.settings.mining.wallet_address = document.getElementById('wallet-address').value;
        this.settings.mining.worker_name = document.getElementById('worker-name').value;
        this.settings.notifications.discord_webhook = document.getElementById('discord-webhook').value;
        this.settings.notifications.telegram_token = document.getElementById('telegram-token').value;
        this.settings.notifications.telegram_chat_id = document.getElementById('telegram-chat-id').value;
        this.settings.notifications.enable_alerts = document.getElementById('enable-alerts').checked;
        this.settings.automation.enable_watchdog = document.getElementById('enable-watchdog').checked;
        this.settings.mining.auto_switch = document.getElementById('enable-auto-switch').checked;

        try {
            await API.updateSettings(this.settings);
            alert('Settings saved successfully!');
            this.closeSettings();
        } catch (error) {
            console.error('Error saving settings:', error);
            alert('Failed to save settings. Check console for details.');
        }
    },

    async testNotifications() {
        try {
            const results = await API.testNotifications();
            let message = 'Notification Test Results:\n\n';
            
            if (results.discord) {
                message += '✅ Discord: Success\n';
            } else {
                message += '❌ Discord: Failed or not configured\n';
            }
            
            if (results.telegram) {
                message += '✅ Telegram: Success\n';
            } else {
                message += '❌ Telegram: Failed or not configured\n';
            }
            
            alert(message);
        } catch (error) {
            console.error('Error testing notifications:', error);
            alert('Failed to test notifications. Check console for details.');
        }
    },

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('connection-status');
        const statusText = document.getElementById('api-status');
        
        if (connected) {
            indicator.style.color = 'var(--accent-success)';
            statusText.textContent = 'Connected';
        } else {
            indicator.style.color = 'var(--accent-danger)';
            statusText.textContent = 'Disconnected';
        }
    },

    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.refreshAll();
        }, this.refreshInterval);
    },

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.initialize();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    App.stopAutoRefresh();
    Charts.destroy();
});
