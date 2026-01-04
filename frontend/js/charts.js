// Charts Module - Temperature and Hashrate Charts

const Charts = {
    tempChart: null,
    hashrateChart: null,
    maxDataPoints: 60,

    initialize() {
        this.createTempChart();
        this.createHashrateChart();
    },

    createTempChart() {
        const ctx = document.getElementById('temp-chart');
        if (!ctx) return;

        const chartConfig = {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'GPU Temperature (°C)',
                    data: [],
                    borderColor: '#ff4444',
                    backgroundColor: 'rgba(255, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: getComputedStyle(document.documentElement)
                                .getPropertyValue('--text-primary').trim()
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: 'rgba(128, 128, 128, 0.2)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement)
                                .getPropertyValue('--text-secondary').trim(),
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        display: true,
                        min: 0,
                        max: 100,
                        grid: {
                            color: 'rgba(128, 128, 128, 0.2)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement)
                                .getPropertyValue('--text-secondary').trim()
                        }
                    }
                }
            }
        };

        this.tempChart = new Chart(ctx, chartConfig);
    },

    createHashrateChart() {
        const ctx = document.getElementById('hashrate-chart');
        if (!ctx) return;

        const chartConfig = {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Hashrate (MH/s)',
                    data: [],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: getComputedStyle(document.documentElement)
                                .getPropertyValue('--text-primary').trim()
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: 'rgba(128, 128, 128, 0.2)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement)
                                .getPropertyValue('--text-secondary').trim(),
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        display: true,
                        min: 0,
                        grid: {
                            color: 'rgba(128, 128, 128, 0.2)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement)
                                .getPropertyValue('--text-secondary').trim()
                        }
                    }
                }
            }
        };

        this.hashrateChart = new Chart(ctx, chartConfig);
    },

    updateTempChart(temperature, timestamp) {
        if (!this.tempChart) return;

        const timeLabel = new Date(timestamp * 1000).toLocaleTimeString();

        // Add new data point
        this.tempChart.data.labels.push(timeLabel);
        this.tempChart.data.datasets[0].data.push(temperature);

        // Keep only the last N data points
        if (this.tempChart.data.labels.length > this.maxDataPoints) {
            this.tempChart.data.labels.shift();
            this.tempChart.data.datasets[0].data.shift();
        }

        this.tempChart.update('none');
    },

    updateHashrateChart(hashrate, timestamp) {
        if (!this.hashrateChart) return;

        const timeLabel = new Date(timestamp * 1000).toLocaleTimeString();

        // Add new data point
        this.hashrateChart.data.labels.push(timeLabel);
        this.hashrateChart.data.datasets[0].data.push(hashrate);

        // Keep only the last N data points
        if (this.hashrateChart.data.labels.length > this.maxDataPoints) {
            this.hashrateChart.data.labels.shift();
            this.hashrateChart.data.datasets[0].data.shift();
        }

        this.hashrateChart.update('none');
    },

    updateTheme() {
        const textColor = getComputedStyle(document.documentElement)
            .getPropertyValue('--text-primary').trim();
        const textSecondary = getComputedStyle(document.documentElement)
            .getPropertyValue('--text-secondary').trim();

        // Update both charts
        [this.tempChart, this.hashrateChart].forEach(chart => {
            if (!chart) return;

            chart.options.plugins.legend.labels.color = textColor;
            chart.options.scales.x.ticks.color = textSecondary;
            chart.options.scales.y.ticks.color = textSecondary;
            chart.update('none');
        });
    },

    destroy() {
        if (this.tempChart) this.tempChart.destroy();
        if (this.hashrateChart) this.hashrateChart.destroy();
    }
};
