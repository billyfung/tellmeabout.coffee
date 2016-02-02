"""
`appengine_config.py` is automatically loaded when Google App Engine
starts a new instance of your application. This runs before any
WSGI applications specified in app.yaml are loaded.
"""
import os
from google.appengine.ext import vendor

appstats_CALC_RPC_COSTS = True

# Workaround the dev-environment SSL
#   http://stackoverflow.com/q/16192916/893652
if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    import imp
    import os.path
    from google.appengine.tools.devappserver2.python import sandbox

    sandbox._WHITE_LIST_C_MODULES += ['_ssl', '_socket']
    # Use the system socket.
    psocket = os.path.join(os.path.dirname(os.__file__), 'socket.py')
    imp.load_source('socket', psocket)

# Third-party libraries are stored in "lib", vendoring will make
# sure that they are importable by the application.
vendor.add('lib')
