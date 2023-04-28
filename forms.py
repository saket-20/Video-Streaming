from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField, PasswordField)
from wtforms.validators import InputRequired, Length

class RegisterForm(FlaskForm):
    username=StringField('username',validators=[InputRequired(),Length(min=5,max=15)])
    password=PasswordField('password',validators=[InputRequired(),Length(min=10,max=30)])