import os
from flask import Flask
import sys

def init_webhooks(base_url):
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',   # TODO: should be overridden with a random value when deploying
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        BASE_URL="http://localhost:5000",
        USE_NGROK=os.environ.get("USE_NGROK", "False") == "True" and os.environ.get("WERKZEUG_RUN_MAIN") != "true",
    )

    if app.config.get("ENV") == "development" and app.config["USE_NGROK"]:
        # pyngrok will only be installed, and should only ever be initialized, in a dev environment
        from pyngrok import ngrok

        # Get the dev server port (defaults to 5000 for Flask, can be overridden with `--port`
        # when starting the server
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 5000

        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port).public_url
        print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

        # Update any base URLs or webhooks to use the public ngrok URL
        app.config["BASE_URL"] = public_url
        init_webhooks(public_url)
        
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # register the database command
    from . import db
    db.init_app(app)

    # register the auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # register the blog blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app