from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FileField
from wtforms.validators import DataRequired, NumberRange, Optional, ValidationError, Regexp
import re

class UploadForm(FlaskForm):
    data = FileField('Data', validators=[DataRequired()])
    split_size = IntegerField('Split Size', validators=[DataRequired(), NumberRange(min=1)])
    index = StringField('Index', validators=[DataRequired()])


    class Meta:
        csrf = False

class S3UploadForm(FlaskForm):
    data = FileField('Data', validators=[DataRequired()])
    folder_name = StringField('Folder_name', validators=[Optional()])

    class Meta:
        csrf = False
