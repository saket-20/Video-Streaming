from flask import Flask, jsonify,render_template,redirect,url_for
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from db import db
from blocklist import BLOCKLIST
#from method_override import MethodOverride
from resources.user import blp as UserBlueprint
from resources.video import blp as VideoBlueprint
from models.user import UserModel
# from resources.item import blp as ItemBlueprint
# from resources.store import blp as StoreBlueprint
# from resources.tag import blp as TagBlueprint
from forms import RegisterForm
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)

def create_app(db_url=None):
    app = Flask(__name__)
    app.config["API_TITLE"] = "Video REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config['SECRET_KEY'] = 'secret key'
    db.init_app(app)
    #app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "jose"
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    jwt = JWTManager(app)
    # @jwt.additional_claims_loader
    # def add_claims_to_jwt(identity):
    #     # TODO: Read from a config file instead of hard-coding
    #     if identity == 1:
    #         return {"is_admin": True}
    #     return {"is_admin": False}

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for('loginform'))

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return redirect(url_for('loginform'))

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return redirect(url_for('loginform'))

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return redirect(url_for('loginform'))

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return redirect(url_for('loginform'))

    # JWT configuration ends

    with app.app_context():
        import models  # noqa: F401

        db.create_all()

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(VideoBlueprint)
    @app.route('/')
    @jwt_required(locations="cookies")
    def index():
        id=get_jwt_identity()
        current_user=UserModel.query.filter_by(id=id).first_or_404()
        all_users=UserModel.query.all()
        print(all_users)
        #current_user=current_user.username
        context={"current_user":current_user,"all_users":all_users}
        return render_template('index.html',**context)
    @app.route('/registerform')
    def registerform():
        #form=RegisterForm()
        return render_template('register.html')

    @app.route('/loginform')
    def loginform():
        #form=RegisterForm()
        return render_template('signin.html')
    return app
    
create_app()