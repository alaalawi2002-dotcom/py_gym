from flask_wtf import FlaskForm
from wtforms   import StringField,SubmitField
from wtforms.validators import DataRequired


class loginFom(FlaskForm):

    name = StringField('please enter the name',validators=[DataRequired()])
    phone =StringField('enter the phone please' , validators=[DataRequired()])

    submit = SubmitField('eter')