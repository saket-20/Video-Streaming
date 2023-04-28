from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies

)
from passlib.hash import pbkdf2_sha256
from forms import RegisterForm
from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST
from flask import request,Response,jsonify,redirect,url_for

blp = Blueprint("Users", "users", description="Operations on users")



@blp.route("/register")
class UserRegister(MethodView):
    #@blp.arguments(UserSchema)
    def post(self):
        if request.form['password']!=request.form['passwordverify']:
            abort(400,message="Passwords dont match")
        if UserModel.query.filter(UserModel.username == request.form["username"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(
            username=request.form["username"],
            password=pbkdf2_sha256.hash(request.form["password"]),
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("loginform"))
        return {"message": "User created successfully."}, 201
    

@blp.route("/login")
class UserLogin(MethodView):
    #@blp.arguments(UserSchema)
    def post(self):
        user = UserModel.query.filter(
            UserModel.username == request.form["username"]
        ).first()

        if user and pbkdf2_sha256.verify(request.form["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            response1=redirect("/")
            set_access_cookies(response1,access_token)
            set_refresh_cookies(response1, refresh_token)
            return response1
        abort(401, message="Invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required(locations='cookies')
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


@blp.route("/user/<int:user_id>")
class User(MethodView):
    """
    This resource can be useful when testing our Flask app.
    We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful
    when we are manipulating data regarding the users.
    """

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True,locations='cookies')
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # Make it clear that when to add the refresh token to the blocklist will depend on the app design
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        response1=Response("SUCCESS, Token Refreshed",status=200)
        set_access_cookies(response1,new_token)
        return response1