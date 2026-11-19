from flask_wtf import FlaskForm
from wtforms import StringField,DateField,IntegerField,SelectField,SubmitField
from wtforms.validators import DataRequired
class Subscripe(FlaskForm):
 
  price      = IntegerField("enter the price "            , validators=[DataRequired()])
  plan_id    = SelectField("select Option",choices=[
    ("1","شهر"),
    ("2","ثلاثة شهور"),
    ("3","سنة")
  ],
  validators=[DataRequired()]
  
  )
  submit     = SubmitField("subscripe")
