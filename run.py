import os

# Load .env file if it exists (for local development)
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)