from flask_wtf import FlaskForm
from wtforms   import StringField,IntegerField,SubmitField,SelectField
from wtforms.validators import DataRequired

class Users(FlaskForm):
 
  name        = StringField("enter your name please"    , validators=[DataRequired()])
  phone       = StringField("enter your phone please"   , validators=[DataRequired()])
  age         = IntegerField("enter your age"           , validators=[DataRequired()])
  submit      = SubmitField("login")