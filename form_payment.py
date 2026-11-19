from flask_wtf import FlaskForm
from wtforms   import StringField,IntegerField,SelectField,SubmitField
from wtforms.validators import DataRequired

class Payment(FlaskForm):
  
    payment_method = StringField("cash OR visa "    , validators=[DataRequired()]) 
    payment_method = SelectField(
    "طريقة الدفع",
    choices=[
        ("cash", "كاش"),
        ("visa", "فيزا")
    ])
    submit = SubmitField("create subscripe")
