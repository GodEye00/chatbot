from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FileField
from wtforms.validators import DataRequired, NumberRange, Optional, ValidationError, Regexp
import re

class UploadForm(FlaskForm):
    data = FileField('Data', validators=[DataRequired()])
    split_size = IntegerField('Split Size', validators=[DataRequired(), NumberRange(min=1)])
    # index = StringField('Index', validators=[DataRequired(), Regexp(r'^[\w-]+$', message="Index must be alphanumeric with dashes or underscores and cannot be left blank")])
    index = StringField('Index', validators=[DataRequired()])
    
    # def validate_data(form, field):
    #     file = field.data
    #     filename = file.filename
    #     if not re.match(r'^[\w-]+\.\w+$', filename):
    #         raise ValidationError("Data must be alphanumeric with dashes or underscores and cannot be left blank. Also, it must have a valid extension.")

    class Meta:
        csrf = False

class S3UploadForm(FlaskForm):
    data = FileField('Data', validators=[DataRequired()])
    folder_name = StringField('Folder_name', validators=[Optional()])
    # folder_name = StringField('Folder_name', validators=[Optional(), Regexp(r'^[\w-]*$', message="Folder name must be alphanumeric with dashes or underscores or left blank")])

    # def validate_data(form, field):
    #     file = field.data
    #     filename = file.filename
    #     if not re.match(r'^[\w-]+\.\w+$', filename):
    #         raise ValidationError("Data must be alphanumeric with dashes or underscores and cannot be left blank. Also, it must have a valid extension.")

    class Meta:
        csrf = False
