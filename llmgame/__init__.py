import os

from flask import Flask

# from . import db
from . import lifelines
from llmgame.database import db


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///game.db"

    db_path = os.path.join(app.instance_path, 'game.db')

    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
        # store the database in the instance folder
        DATABASE=db_path,
    )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # register the database commands
    db.init_app(app)

    # check if database exists, if not initialise it
    if not os.path.isfile(db_path): # pragma: no cover
        with app.app_context():
            import llmgame.models
            db.create_all()
            #db.init_db()
            print("Initialized the database.")

    # apply the blueprints to the app
    from llmgame.llmgame import bp
    app.register_blueprint(bp)
    app.register_blueprint(lifelines.bp)
    app.add_url_rule('/', endpoint='index')

    return app
