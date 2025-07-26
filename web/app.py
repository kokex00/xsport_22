from flask import Flask, render_template, request, jsonify
import threading
import os

class WebDashboard:
    def __init__(self, bot=None):
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.bot = bot
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/stats')
        def get_stats():
            if not self.bot:
                return jsonify({'error': 'Bot not available'})
            
            try:
                stats = {
                    'guilds': len(self.bot.guilds),
                    'users': sum(guild.member_count for guild in self.bot.guilds),
                    'uptime': 'Running',
                    'status': 'Online'
                }
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)})
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask app"""
        self.app.run(host=host, port=port, debug=debug, threaded=True)
    
    def start_in_thread(self, host='0.0.0.0', port=5000):
        """Start the Flask app in a separate thread"""
        thread = threading.Thread(
            target=self.run,
            kwargs={'host': host, 'port': port, 'debug': False},
            daemon=True
        )
        thread.start()
        return thread

# Create global dashboard instance
dashboard = WebDashboard()

if __name__ == '__main__':
    dashboard.run()
