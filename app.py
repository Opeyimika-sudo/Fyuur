#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from models import db, Show, Artist, Venue
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
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


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data_set = []
    venues = Venue.query.all()
    places = set()
    for venue in venues:
        places.add((venue.city, venue.state))
    for place in places:
        data_set.append({
            "city": place[0],
            "state": place[1],
            "venues": []
        })
    for venue in venues:
        for i in data_set:
            if i['city'] == venue.city and i['state'] == venue.state:
                upcoming_shows = Show.query.filter(Show.venue_id == venue.id).filter(
                    Show.start_time > datetime.utcnow())
                venues_data = {
                  'id': venue.id,
                  'name': venue.name,
                  'upcoming_shows': upcoming_shows.count()
                }
                i['venues'].append(venues_data)
    return render_template('pages/venues.html', areas=data_set)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search = request.form.get("search_term")
  venues = Venue.query.filter(
    Venue.name.ilike('%' + search + '%')
  ).all()
  venues_list = []

  for venue in venues:
    upcoming_shows = Show.query.filter(Show.venue_id == venue.id).all()
    data = {
      "id": venue.id,
      "name": venue.name,
      "upcoming_shows": len(upcoming_shows)
    }
    venues_list.append(data)

  response = {
    "count": len(venues),
    "data": venues_list
  }

  return render_template('pages/search_venues.html', results=response, search_term=search)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data_set = []
  venue = Venue.query.get(venue_id)
  now = datetime.now()
  if not venue:
    abort(404)
    
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []

  for show in upcoming_shows_query:
    artist = Artist.query.filter(Artist.id == show.artist_id).first()

    upcoming_shows.append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image': artist.image_link,
      'start_time': format_datetime(value=str(show.start_time), format="full")
    })
  
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue.id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    artist = Artist.query.filter(Artist.id == show.artist_id).first()

    past_shows.append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image': artist.image_link,
      'start_time': format_datetime(value=str(show.start_time), format="full")
    })

  if venue.genres:
    genres = venue.genres.split(',')
  else:
    genres=''

  data = {
      "id": venue.id,
      "name": venue.name,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "genres": genres,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
  
  data_set.append(data)

  data = list(filter(lambda d: d['id'] == venue_id, data_set))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate():
    new_venue = Venue(
    name = form.name.data,
    city = form.city.data,
    state= form.state.data,
    phone= form.phone.data,
    genres= ",".join(form.genres.data),
    facebook_link= form.facebook_link.data,
    seeking_description= form.seeking_description.data,
    website= form.website_link.data,
    address=form.address.data,
    image_link= form.image_link.data,
    seeking_talent = form.seeking_talent.data
        )
    try:
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + new_venue.name + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue' + new_venue.name + 'could not be listed.')
    finally:
        db.session.close()
  else:
      for field, message in form.errors.items():
        flash(field + '-' + str(message), 'danger')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  try:
    Venue.query.filter_by(Venue.id==venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    flash('Venue' + venue['name'] + 'unable to be deleted')
    abort(500)
  finally:
    db.session.close()
    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    person = {
      "id": artist.id,
      "name": artist.name
    }
    data.append(person)
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search = request.form.get('search_term')
  artists = Artist.query.filter(
    Artist.name.ilike('%' + search + '%' )
  ).all()
  artists_list = []

  for artist in artists:
    upcoming_shows = Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).all()
    person = {
      "id": artist.id,
      "name": artist.name,
      "upcoming_shows": len(upcoming_shows)
    }
    artists_list.append(person)

  response = {
    "count": len(artists),
    "data": artists_list
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
 
  data_set=[]
  artists= Artist.query.all()
  for artist in artists:
    past_shows= []
    past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist.id).filter(Show.start_time<datetime.now()).all()
    for shows in past_shows_query:
      venue = Venue.query.filter(Venue.id==shows.venue_id).first()

      show_detail={
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": shows.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      }
      past_shows.append(show_detail)

    upcoming_shows= []
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all()
    for shows in upcoming_shows_query:
      venue= Venue.query.filter(Venue.id==shows.venue_id).first()

      show_detail={
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": shows.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      }
      upcoming_shows.append(show_detail)
        
   
    if artist.genres:
      genres= artist.genres.split(",")
    else:
      genres=""


    data={
      "id": artist.id,
      "name": artist.name,
      "city": artist.city,
      "address"
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "genres": genres,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "facebook_link": artist.facebook_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
   
    data_set.append(data)
  data = list(filter(lambda d: d['id'] == artist_id, data_set))[0]
  return render_template('pages/show_artist.html', artist=data)
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  edit_artist = Artist.query.filter(Artist.id==artist_id).first()

  artist={
    'id': edit_artist.id,
    'name':edit_artist.name,
    'genres': edit_artist.genres.split(','),
    'city': edit_artist.city,
    'state': edit_artist.state,
    'phone': edit_artist.phone,
    'website': edit_artist.website,
    'facebook_link': edit_artist.facebook_link,
    'seeking_venue': edit_artist.seeking_venue,
    'seeking_description': edit_artist.seeking_description,
    'image_link': edit_artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist=Artist.query.get(artist_id)
      form = ArtistForm(request.form)

      artist.name = form.name.data
      artist.city = form.city.data
      artist.state= form.state.data
      artist.genres=",".join(form.genres.data)
      artist.phone= form.phone.data
      artist.facebook_link= form.facebook_link.data
      artist.seeking_description= form.seeking_description.data
      artist.website= form.website_link.data
      artist.image_link= form.image_link.data
      artist.seeking_venue = form.seeking_venue.data
   
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + artist.name + ' was successfully updated!') 

    except:
      db.session.rollback()
      flash('Something is wrong with the update. Artist ' + artist.name + ' could not be updated.')
      print(sys.exc_info())

    finally:
      db.session.close()

  else:
    flash('Error with the update. Please try again.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  edit_venue = Venue.query.filter(Venue.id==venue_id).first()

  venue={
    'id': edit_venue.id,
    'name':edit_venue.name,
    'genres': edit_venue.genres.split(','),
    'city': edit_venue.city,
    'address':edit_venue.address,
    'state': edit_venue.state,
    'phone': edit_venue.phone,
    'website': edit_venue.website,
    'facebook_link': edit_venue.facebook_link,
    'seeking_talent': edit_venue.seeking_talent,
    'seeking_description': edit_venue.seeking_description,
    'image_link': edit_venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  if form.validate():
    try:
      venue=Venue.query.get(venue_id)
      form = VenueForm(request.form)

      venue.name = form.name.data
      venue.city = form.city.data
      venue.state= form.state.data
      venue.address= form.address.data
      venue.genres=",".join(form.genres.data)
      venue.phone= form.phone.data
      venue.facebook_link= form.facebook_link.data
      venue.seeking_description= form.seeking_description.data
      venue.website= form.website_link.data
      venue.image_link= form.image_link.data
      venue.seeking_talent = form.seeking_talent.data
   
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + venue.name + ' was successfully updated!') 

    except:
      db.session.rollback()
      flash('Something is wrong with the update. Venue ' + venue.name + ' could not be updated.')
      print(sys.exc_info())

    finally:
      db.session.close()

  else:
    flash('Error with the update. Please try again.')

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
  form = ArtistForm(request.form)
  if form.validate():
    new_artist = Artist(
    name = form.name.data,
    city = form.city.data,
    state= form.state.data,
    phone= form.phone.data,
    genres= ",".join(form.genres.data),
    facebook_link= form.facebook_link.data,
    seeking_description= form.seeking_description.data,
    website= form.website_link.data,
    image_link= form.image_link.data,
    seeking_venue = form.seeking_venue.data,
        )
    try:
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + new_artist.name + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist' + new_artist.name + ' could not be listed.')
    finally:
        db.session.close()

  else:
    for field, message in form.errors.items():
        flash(field + '-' + str(message), 'danger')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.all()
 

  for show in shows:
    venue = show.venue
    artist = show.artist
    show_detail = {
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
   
    data.append(show_detail)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  if form.validate():
    try:
      show = Show()

      show.artist_id = form.artist_id.data
      show.venue_id = form.venue_id.data
      show.start_time = form.start_time.data
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Show failed to be listed')
    finally:
      db.session.close()

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
