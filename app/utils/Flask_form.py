from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FileField
from wtforms.validators import DataRequired, NumberRange, Regexp, Optional

class UploadForm(FlaskForm):
    data = FileField('Data', validators=[DataRequired()])
    split_size = IntegerField('split size', validators=[DataRequired(), NumberRange(min=1)])
    class Meta:
        csrf = False

class S3UploadForm(FlaskForm):
    data = FileField('Data', validators=[DataRequired()])
    folder_name = StringField('Folder_name', validators=[Optional(), Regexp(r'^[\w-]*$', message="folder name must be alphanumeric with dashes or underscores or left blank")])    
    class Meta:
            csrf = False

