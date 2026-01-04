"""
GPU Mining Suite - Main Flask Application
Provides REST API for mining management and monitoring
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
import time
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import our modules
from config import config
from database import db
from gpu_monitor import gpu_monitor
from miner_controller import miner_controller
from overclock import overclock_manager
from notifications import notification_manager
from profit_calculator import profit_calculator
from automation import automation_manager

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='')
CORS(app)

# Configure from settings
PORT = config.get_setting('dashboard', 'port') or 5000
HOST = config.get_setting('dashboard', 'host') or '0.0.0.0'

# Initialize components
def initialize_app():
    """Initialize application components"""
    print("=" * 50)
    print("GPU Mining Suite - Initializing...")
    print("=" * 50)
    
    # Configure notifications
    notif_config = config.settings.get('notifications', {})
    notification_manager.configure(
        discord_webhook=notif_config.get('discord_webhook', ''),
        telegram_token=notif_config.get('telegram_token', ''),
        telegram_chat_id=notif_config.get('telegram_chat_id', ''),
        enabled=notif_config.get('enable_alerts', True)
    )
    
    # Configure automation
    auto_config = config.settings.get('automation', {})
    automation_manager.configure(
        auto_switch=config.get_setting('mining', 'auto_switch') or False,
        watchdog=auto_config.get('enable_watchdog', True),
        scheduler=auto_config.get('enable_scheduler', False),
        hashrate_threshold=auto_config.get('hashrate_threshold', 20),
        mining_hours=auto_config.get('mining_hours', '00:00-23:59')
    )
    
    # Register automation callbacks
    automation_manager.register_callback('get_miner_status', lambda: miner_controller.get_status())
    automation_manager.register_callback('get_gpu_stats', lambda: gpu_monitor.get_latest_stats())
    automation_manager.register_callback('restart_miner', lambda: miner_controller.restart_mining())
    automation_manager.register_callback('on_miner_crash', lambda coin: notification_manager.alert_miner_crashed(coin))
    automation_manager.register_callback('on_low_hashrate', lambda coin, hr, exp: notification_manager.alert_low_hashrate(coin, hr, exp))
    automation_manager.register_callback('on_high_temp', lambda gpu_id, temp: notification_manager.alert_high_temperature(gpu_id, temp))
    
    # Start GPU monitoring
    def on_gpu_update(stats):
        # Save to database
        for gpu in stats.get('gpus', []):
            db.add_gpu_stats(gpu['gpu_id'], gpu)
    
    gpu_monitor.start_monitoring(interval=5, callback=on_gpu_update)
    
    # Start watchdog
    automation_manager.start_watchdog()
    
    print("✓ Initialization complete")
    print(f"Dashboard: http://localhost:{PORT}")
    print("=" * 50)

# ============================================================================
# Dashboard Routes
# ============================================================================

@app.route('/')
def index():
    """Serve main dashboard"""
    return send_from_directory(app.static_folder, 'index.html')

# ============================================================================
# GPU Monitoring API
# ============================================================================

@app.route('/api/gpu/stats')
def get_gpu_stats():
    """Get current GPU statistics for all GPUs"""
    stats = gpu_monitor.get_latest_stats()
    return jsonify(stats)

@app.route('/api/gpu/<int:gpu_id>/stats')
def get_specific_gpu_stats(gpu_id):
    """Get statistics for a specific GPU"""
    stats = gpu_monitor.get_gpu_stats(gpu_id)
    return jsonify(stats)

@app.route('/api/gpu/info')
def get_gpu_info():
    """Get GPU information"""
    gpus = []
    for i in range(max(1, gpu_monitor.gpu_count)):
        info = gpu_monitor.get_gpu_info(i)
        gpus.append(info)
    return jsonify({'gpus': gpus, 'count': len(gpus)})

@app.route('/api/gpu/history')
def get_gpu_history():
    """Get historical GPU data"""
    hours = request.args.get('hours', default=24, type=int)
    gpu_id = request.args.get('gpu_id', default=None, type=int)
    
    history = db.get_gpu_history(hours, gpu_id)
    return jsonify({'history': history, 'hours': hours})

# ============================================================================
# Miner Control API
# ============================================================================

@app.route('/api/miner/status')
def get_miner_status():
    """Get current miner status"""
    status = miner_controller.get_status()
    
    # Add miner API stats if available
    api_stats = miner_controller.get_miner_api_stats()
    if api_stats:
        miner_controller.update_stats(
            api_stats.get('hashrate', 0),
            api_stats.get('accepted', 0),
            api_stats.get('rejected', 0)
        )
        status.update(api_stats)
    
    return jsonify(status)

@app.route('/api/miner/start', methods=['POST'])
def start_miner():
    """Start mining"""
    data = request.get_json() or {}
    
    coin = data.get('coin') or config.get_setting('mining', 'default_coin')
    if not coin:
        return jsonify({'error': 'No coin specified'}), 400
    
    # Get coin configuration
    coin_config = config.get_coin_config(coin)
    if not coin_config:
        return jsonify({'error': f'Unknown coin: {coin}'}), 400
    
    # Get pool and wallet
    pool = data.get('pool') or config.get_setting('mining', 'mining_pool') or coin_config['pools'][0]
    wallet = data.get('wallet') or config.get_setting('mining', 'wallet_address')
    
    if not wallet:
        return jsonify({'error': 'No wallet address configured'}), 400
    
    worker_name = config.get_setting('mining', 'worker_name') or 'worker'
    
    # Start mining
    success = miner_controller.start_mining(
        coin=coin,
        algorithm=coin_config['algorithm'],
        pool=pool,
        wallet=wallet,
        worker_name=worker_name,
        miner=coin_config.get('miner', 't-rex')
    )
    
    if success:
        # Apply overclock profile
        gpu_model = 'GTX_1660_SUPER'  # Could detect this
        oc_profile = config.get_overclock_profile(gpu_model, coin)
        if oc_profile:
            overclock_manager.apply_coin_profile(0, gpu_model, coin, oc_profile)
        
        # Send notification
        notification_manager.alert_mining_started(coin, pool)
        
        return jsonify({'success': True, 'coin': coin, 'pool': pool})
    else:
        return jsonify({'error': 'Failed to start miner'}), 500

@app.route('/api/miner/stop', methods=['POST'])
def stop_miner():
    """Stop mining"""
    status = miner_controller.get_status()
    coin = status.get('coin')
    uptime = status.get('uptime', 0)
    
    success = miner_controller.stop_mining()
    
    if success:
        # Reset overclock
        overclock_manager.reset_to_default(0)
        
        # Send notification
        if coin:
            notification_manager.alert_mining_stopped(coin, uptime)
        
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to stop miner'}), 500

@app.route('/api/miner/restart', methods=['POST'])
def restart_miner():
    """Restart miner"""
    success = miner_controller.restart_mining()
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to restart miner'}), 500

@app.route('/api/miner/switch', methods=['POST'])
def switch_coin():
    """Switch to different coin"""
    data = request.get_json() or {}
    coin = data.get('coin')
    
    if not coin:
        return jsonify({'error': 'No coin specified'}), 400
    
    # Stop current mining
    miner_controller.stop_mining()
    time.sleep(2)
    
    # Start with new coin
    return start_miner()

# ============================================================================
# Profitability API
# ============================================================================

@app.route('/api/profit')
def get_profitability():
    """Get profitability for all coins"""
    electricity_cost = request.args.get('electricity_cost', default=0.12, type=float)
    
    profitability = profit_calculator.calculate_all_coins_profitability(
        config.coins,
        electricity_cost
    )
    
    return jsonify(profitability)

@app.route('/api/profit/best')
def get_best_coin():
    """Get most profitable coin"""
    electricity_cost = request.args.get('electricity_cost', default=0.12, type=float)
    
    best_coin = profit_calculator.get_most_profitable_coin(
        config.coins,
        electricity_cost
    )
    
    if best_coin:
        return jsonify({'coin': best_coin})
    else:
        return jsonify({'error': 'Could not determine best coin'}), 500

@app.route('/api/profit/prices')
def get_coin_prices():
    """Get current coin prices"""
    prices = profit_calculator.get_cached_prices()
    
    if not prices:
        # Update prices if cache is empty
        prices = profit_calculator.update_prices(config.coins)
    
    return jsonify(prices)

# ============================================================================
# Earnings API
# ============================================================================

@app.route('/api/earnings')
def get_earnings():
    """Get earnings summary"""
    period = request.args.get('period', default='today', type=str)
    
    summary = db.get_earnings_summary(period)
    
    return jsonify(summary)

@app.route('/api/earnings/history')
def get_earnings_history():
    """Get earnings history"""
    hours = request.args.get('hours', default=168, type=int)  # Default 7 days
    
    history = db.get_mining_history(hours)
    
    return jsonify({'history': history})

# ============================================================================
# Overclock API
# ============================================================================

@app.route('/api/overclock/profiles')
def get_overclock_profiles():
    """Get available overclock profiles"""
    return jsonify(config.overclock_profiles)

@app.route('/api/overclock/current')
def get_current_overclock():
    """Get current overclock settings"""
    profiles = overclock_manager.get_all_profiles()
    return jsonify(profiles)

@app.route('/api/overclock/apply', methods=['POST'])
def apply_overclock():
    """Apply overclock profile"""
    data = request.get_json() or {}
    
    gpu_id = data.get('gpu_id', 0)
    profile_name = data.get('profile')
    
    if not profile_name:
        return jsonify({'error': 'No profile specified'}), 400
    
    gpu_model = 'GTX_1660_SUPER'
    profile_data = config.get_overclock_profile(gpu_model, profile_name)
    
    if not profile_data:
        return jsonify({'error': 'Profile not found'}), 404
    
    success = overclock_manager.apply_coin_profile(gpu_id, gpu_model, profile_name, profile_data)
    
    if success:
        return jsonify({'success': True, 'profile': profile_name})
    else:
        return jsonify({'error': 'Failed to apply overclock'}), 500

@app.route('/api/overclock/reset', methods=['POST'])
def reset_overclock():
    """Reset overclock to defaults"""
    data = request.get_json() or {}
    gpu_id = data.get('gpu_id', 0)
    
    success = overclock_manager.reset_to_default(gpu_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to reset overclock'}), 500

# ============================================================================
# Settings API
# ============================================================================

@app.route('/api/settings')
def get_settings():
    """Get all settings"""
    return jsonify(config.settings)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    data = request.get_json() or {}
    
    # Update settings
    config.settings.update(data)
    success = config.save_json('settings.json', config.settings)
    
    if success:
        # Reconfigure components
        notif_config = config.settings.get('notifications', {})
        notification_manager.configure(
            discord_webhook=notif_config.get('discord_webhook', ''),
            telegram_token=notif_config.get('telegram_token', ''),
            telegram_chat_id=notif_config.get('telegram_chat_id', ''),
            enabled=notif_config.get('enable_alerts', True)
        )
        
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to save settings'}), 500

@app.route('/api/settings/test-notification', methods=['POST'])
def test_notification():
    """Test notification systems"""
    results = notification_manager.test_notifications()
    return jsonify(results)

# ============================================================================
# System API
# ============================================================================

@app.route('/api/system/info')
def get_system_info():
    """Get system information"""
    import platform
    import psutil
    
    return jsonify({
        'os': platform.system(),
        'os_version': platform.version(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total // (1024**3),  # GB
        'gpu_count': gpu_monitor.gpu_count,
        'uptime': time.time()
    })

@app.route('/api/system/logs')
def get_logs():
    """Get recent logs"""
    # Return recent events from database
    return jsonify({'logs': []})

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    try:
        initialize_app()
        app.run(host=HOST, port=PORT, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
        gpu_monitor.stop_monitoring()
        automation_manager.shutdown()
        gpu_monitor.shutdown()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
