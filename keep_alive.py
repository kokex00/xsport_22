from web.app import dashboard
import threading

def keep_alive():
    """Start the keep-alive web server"""
    try:
        dashboard.start_in_thread(host='0.0.0.0', port=5000)
        print("✅ Keep-alive web server started on port 5000")
        print("📊 Dashboard available at: http://0.0.0.0:5000")
    except Exception as e:
        print(f"❌ Error starting keep-alive server: {e}")

if __name__ == "__main__":
    keep_alive()
    # Keep the script running
    import time
    while True:
        time.sleep(60)
