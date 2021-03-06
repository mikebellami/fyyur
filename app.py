#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import name
from click import Choice
import dateutil.parser 
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form 
from forms import *
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sys
from models import db, Venue, Artist, Show
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Fetch, Search and Veiw Venues details
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  cities = Venue.query.distinct(Venue.city, Venue.state).all()
  for city in cities:
    city_data = {
      "city": city.city,
      "state": city.state,
      "venues": []
    }
    venues = Venue.query.filter_by(city=city.city, state=city.state).all()
    for venue in venues:
      num_upcoming_shows = 0
      for show in venue.shows:
        if show.start_time > datetime.now():
          num_upcoming_shows += 1
      venue_data = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      }
      city_data["venues"].append(venue_data)
    data.append(city_data)
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response = {}
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response['count'] = len(venues)
  response['data'] = venues
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get_or_404(venue_id)
  data = {
    "id": venue.id, 
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.talent,
    "seeking_description": venue.description,
    "image_link": venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0
  }
  
  for show in venue.shows:
    if show.start_time <= datetime.now():
      data['past_shows'].append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%d-%m-%Y, %H:%M')
      })
      data['past_shows_count'] += 1
    else:
      data['upcoming_shows'].append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%d-%m-%Y, %H:%M')
      })
      data['upcoming_shows_count'] += 1
   
  return render_template('pages/show_venue.html', venue=data)
  
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  formdata = VenueForm(request.form)
  try:
    venue = Venue(
      name=formdata.name.data,
      city=formdata.city.data,
      state=formdata.state.data,
      address=formdata.address.data,
      phone=formdata.phone.data,
      genres=formdata.genres.data,
      facebook_link=formdata.facebook_link.data,
      image_link = formdata.image_link.data,
      website = formdata.website_link.data,
      talent = True if formdata.seeking_talent.data == 'y' else False,
      description = formdata.seeking_description.data
    )
   
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred.'+ str(formdata.name.data)+ ' Venue  could not be listed.')
    else:
     flash('Venue'+str(formdata.name.data) + ' was successfully listed!')
   
  return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    error = True
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get_or_404(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website
  form.seeking_talent.data = venue.talent
  form.seeking_description.data = venue.description  
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  formdata = request.form
  try:
    venue = Venue.query.get_or_404(venue_id)
    venue.name = formdata['name']
    venue.city = formdata['city']
    venue.state = formdata['state']
    venue.address = formdata['address']
    venue.phone = formdata['phone']
    venue.genres = formdata.getlist('genres')
    venue.image_link = formdata['image_link']
    venue.facebook_link = formdata['facebook_link']
    venue.website = formdata['website_link']
    venue.talent = True if 'seeking_talent' in formdata else False 
    venue.description = formdata['seeking_description']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be changed.')
  else:
    flash('Venue was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  formdata = ArtistForm(request.form)
  try:
    artist = Artist(
      name=formdata.name.data,
      city=formdata.city.data,
      state=formdata.state.data,
      phone=formdata.phone.data,
      genres=formdata.genres.data,
      facebook_link=formdata.facebook_link.data,
      image_link = formdata.image_link.data,
      website = formdata.website_link.data,
      venue = True if formdata.seeking_venue.data == 'y' else False,
      description = formdata.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + str(formdata.name.data) + ' could not be listed.')
  else:
    flash('Artist ' + str(formdata.name.data) + ' was successfully listed!')
  
  return render_template('pages/home.html')

#  Fetch, Search and Veiw Artists details
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response['count'] = len(artists)
  response['data'] = artists
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.venue,
    "seeking_description": artist.description,
    "image_link": artist.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0
  }
  print(past_shows_query)
  for show in artist.shows:
    if show.start_time < datetime.now():
      data['past_shows'].append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
      data['past_shows_count'] += 1
    else:
      data['upcoming_shows'].append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
      data['upcoming_shows_count'] += 1
  return render_template('pages/show_artist.html', artist=data)

#  Update Artists
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  form = ArtistForm()

  artist = Artist.query.get_or_404(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website
  form.seeking_venue.data = artist.venue
  form.seeking_description.data = artist.description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  # artist record with ID <artist_id> using the new attributes
  error = False
  formdata = request.form
  try:
    artist = Artist.query.get_or_404(artist_id)
    artist.name = formdata['name']
    artist.city = formdata['city']
    artist.state = formdata['state']
    artist.phone = formdata['phone']
    artist.genres = formdata.getlist('genres')
    artist.facebook_link = formdata['facebook_link']
    artist.image_link = formdata['image_link']
    artist.website = formdata['website_link']
    artist.venue = True if 'seeking_venue' in formdata else False 
    artist.description = formdata['seeking_description']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be changed.')
  else:
    flash('Artist was successfully updated!')
    
  return redirect(url_for('show_artist', artist_id=artist_id))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  formdata = ShowForm(request.form)
  try:
    show = Show(
      venue_id = formdata.venue_id.data,
      artist_id = formdata.artist_id.data,
      start_time = formdata.start_time.data 
    )
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
