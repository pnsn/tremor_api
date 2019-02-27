import sys
sys.path.insert(0, '/var/www/tremor_api')
from app.app import create_app

activate_this = '/home/deploy/.virtualenvs/tremor_api/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
application = create_app('production')
