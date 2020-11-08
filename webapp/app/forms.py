from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired

class ComputeFeeForm(FlaskForm):
    postal_code = IntegerField('Code Postal', validators=[DataRequired()])
    address = StringField('Adresse', validators=[DataRequired()])
    price = FloatField('Prix', validators=[DataRequired()])
    submit = SubmitField("Calcule le frais d'agence")