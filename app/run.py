import os
from app.app import create_app
# from dotenv import load_dotenvs

# load the .env file
# APP_ROOT = os.path.join(os.path.dirname(__file__), '.')
# dotenv_path = os.path.join(APP_ROOT, '.env')
# load_dotenv(dotenv_path)
config_name = os.getenv('APP_SETTINGS')  # production, testing, staging ...
app = create_app(config_name)


if __name__ == '__main__':
    app.run()
