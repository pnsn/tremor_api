import sys
activate_this = '/home/deploy/.virtualenvs/aqms_api/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
sys.path.insert(0, '/var/www/tremor_web_service')
from app.app import create_app
application=create_app('production')
