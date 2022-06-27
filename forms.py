from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField 
from wtforms.validators import DataRequired, AnyOf, URL, Regexp
from enums import Genre, State



class ShowForm(Form):
    artist_id = StringField(
        'artist_id', 
        validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id',
         validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', 
        validators=[DataRequired()],
        choices = State.choices()

    )
    address = StringField(
        'address',
        validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
         validators=[DataRequired(), Regexp('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')]
    )
    image_link = StringField(
        'image_link',
         validators=[URL()]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', 
        validators=[DataRequired()],
        choices = Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link',
        validators=[URL()]
    )

    seeking_talent = BooleanField( 
        'seeking_talent',
         default=False
        )

    seeking_description = StringField(
        'seeking_description' 
    )



class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', 
        validators=[DataRequired()],
        choices = State.choices()
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone',
        validators=[DataRequired(), Regexp('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', 
        validators=[DataRequired()],
        choices = Genre.choices()
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField( 
        'seeking_venue',
        default=False
     )

    seeking_description = StringField(
            'seeking_description'
     )

