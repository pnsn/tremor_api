import os

from app.app import create_app
config_name = os.getenv('APP_SETTINGS') #development, production, testing, staging
app = create_app(config_name)


if __name__ == '__main__':
    app.run()
