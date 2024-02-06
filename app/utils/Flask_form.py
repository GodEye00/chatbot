from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FileField
from wtforms.validators import DataRequired, NumberRange, Regexp

class UploadForm(FlaskForm):
    data = FileField('Data', validators=[DataRequired()])
    split_size = IntegerField('Split Size', validators=[DataRequired(), NumberRange(min=1)])
    index = StringField('Index', validators=[DataRequired(), Regexp(r'^[\w-]+$', message="Index must be alphanumeric with dashes or underscores")])
    class Meta:
        csrf = False

class S3UploadForm(FlaskForm):
    data = FileField('Data', validators=[DataRequired()])
    class Meta:
        csrf = False

