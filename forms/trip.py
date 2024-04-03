from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired


class TripForm(FlaskForm):
    from_text = StringField('Откуда', validators=[DataRequired()])
    to_text = StringField('Куда', validators=[DataRequired()])
    date = DateField('Когда', validators=[DataRequired()])
    submit = SubmitField('В путь!')