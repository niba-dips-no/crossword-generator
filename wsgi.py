from app import app
import multiprocessing

# Calculate workers based on CPU count
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120  # 2 minutes
keepalive = 5

if __name__ == "__main__":
    app.run()
