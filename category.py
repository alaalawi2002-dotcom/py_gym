from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Cat(FlaskForm):

  name = StringField(
    "اسم الفئة",
    validators=[DataRequired()]
)

  submit = SubmitField("إضافة الفئة")