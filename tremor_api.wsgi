import sys
sys.path.insert(0, '/var/www/tremor_api_v3')
from app.app import create_app

activate_this = '/home/deploy/.virtualenvs/tremor_api_v3/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
application = create_app('production')
