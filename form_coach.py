from flask_wtf import FlaskForm
from wtforms import  StringField,IntegerField,SubmitField
from wtforms.validators import DataRequired

class coash(FlaskForm):

    name      = StringField("enter the name please" , validators=[DataRequired()])
    phone     = StringField("enter the name please" , validators=[DataRequired()])
    age       = IntegerField("enter the name please" , validators=[DataRequired()])
    specialty = StringField("enter the spechiality"  , validators=[DataRequired()])

    submit = SubmitField("login")
