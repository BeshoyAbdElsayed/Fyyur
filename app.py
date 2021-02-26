#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for,
  abort, 
  jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from datetime import datetime
from models import (
  app,
  db,
  migrate, 
  Venue, 
  Artist, 
  Show, 
  VenueGenre, 
  ArtistGenre
)
from helpers import (
  get_num_past_shows, 
  get_num_upcoming_shows, 
  get_past_shows, 
  get_upcoming_shows
)
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
# connect to a local postgresql database
app.config.from_object('config')
db.init_app(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')



@app.route('/test')
def test():
  form = MyForm()
  return render_template('forms/test.html', form=form)

@app.route('/test', methods=['POST'])
def test_post():
  form = MyForm()
  if form.validate_on_submit():
      return 'success'
  return 'failed'
  


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #  replace with real venues data.
  # getting cities and states 
  citiesAndStates = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  dbData = []

  for cityandState in citiesAndStates:
    # grouping venues based on their city and state
    venues = Venue.query.filter(Venue.city==cityandState[0], Venue.state==cityandState[1]).all()
    # addign the num_upcoming_shows feild
    # venueList because venue obj doesn't support item assignment
    venueList = []
    for index, venue in enumerate(venues):
      venueList.append({
        "id": venue.id,
        "name": venue.name,
      })
      shows = venue.shows     
      venueList[index]['num_upcoming_shows'] = get_num_upcoming_shows(shows)
    dbData.append({
      "city": cityandState[0],
      "state": cityandState[1],
      "venues": venueList
    })
  
  # leaving mock data just for reference 
  mockData=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  # using real database data in the vue
  return render_template('pages/venues.html', areas=dbData);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on venues with partial string search. Ensure it is case-insensitive.
  search_term = search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  dbResponse = {
    "count": len(venues)
  }
  dbData = []
  for venue in venues:
    dbData.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": get_num_upcoming_shows(venue.shows)
    })
  dbResponse['data'] = dbData
  
  # leaving mock response for reference
  mockResponse={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=dbResponse, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id
  # if venue doesn't exist retun page 404
  venue = Venue.query.get(venue_id)
  try:
    venue.name
  except:
    abort(404)
  
  # prepare genres
  genres = []
  for genre in venue.genres:
    genres.append(genre.name)
  
  dbData = {
    "id": venue.id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": get_past_shows(venue.shows),
    "upcoming_shows": get_upcoming_shows(venue.shows),
    "past_shows_count": get_num_past_shows(venue.shows),
    "upcoming_shows_count": get_num_upcoming_shows(venue.shows) 
  }

  # leaving mock data for reference 
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }

  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  
  #using real database data
  return render_template('pages/show_venue.html', venue=dbData)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  data = request.form
  form = VenueForm()
  
  # validate input data
  if not form.validate_on_submit():
    flash('invalid input fields')
    return redirect(url_for('index'))

  error = False
  try:
    venue = Venue(
      name = data['name'],
      city = data['city'],
      state = data['state'],
      address = data['address'],
      phone = data['phone'],
      facebook_link = data['facebook_link'],
      image_link = data['image_link'],
      website = data['website'],
      seeking_talent = True if 'seeking_talent' in data.keys() else False,
      seeking_description = data['seeking_description']
    )
    # insert multiple genres
    for genre_name in form.genres.data:
      genre = VenueGenre(name = genre_name)
      venue.genres.append(genre)
    db.session.add(venue)	
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    #  on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # if artist doesn't exist retun page 404
  venue = Venue.query.get(venue_id)
  venue_name = venue.name
  try:
    venue.name
  except:
    abort(404)

  error = False
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

  if error:
    # on unsuccessful deletion flash an error instead
    flash(f'Venue {venue_name} deletion failed')
  else:
    flash(f'Venue {venue_name} was deleted successfully!')

  return redirect(url_for('index'))
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #------- Done it :D

  # delete artist
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # if artist doesn't exist retun page 404
  artist = Artist.query.get(artist_id)
  artist_name = artist.name
  try:
    artist.name
  except:
    abort(404)

  error = False
  try:
    db.session.delete(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()  

  if error:
    # on unsuccessful deletion flash an error instead
    flash(f'Artist {artist_name} deletion failed')
  else:
    flash(f'Artist {artist_name} was deleted successfully!')

  return redirect(url_for('index'))
  


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # replace with real data returned from querying the database
  artists = Artist.query.with_entities(Artist.id, Artist.name).all();
  dbData = []
  for artist in artists:
    dbData.append({
      "id": artist[0],
      "name": artist[1]
    })
  
  # leaving mock data for reference 
  mockData=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  return render_template('pages/artists.html', artists=dbData)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  dbResponse = {
    "count": len(artists)
  }
  dbData = []
  for artist in artists:
    dbData.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": get_num_upcoming_shows(artist.shows)
    })
  dbResponse['data'] = dbData

  # leaving mock response for reference
  mockResponse={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=dbResponse, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  #  replace with real artist data from the artists table, using artist_id
  # if artist doesn't exist retun page 404
  artist = Artist.query.get(artist_id)
  try:
    artist.name
  except:
    abort(404)
  
  # prepare genres
  genres = []
  for genre in artist.genres:
    genres.append(genre.name)
  
  dbData = {
    "id": artist.id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": get_past_shows(artist.shows),
    "upcoming_shows": get_upcoming_shows(artist.shows),
    "past_shows_count": get_num_past_shows(artist.shows),
    "upcoming_shows_count": get_num_upcoming_shows(artist.shows) 
  }

  # leaving mock data for reference 
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]

  # using real database data
  return render_template('pages/show_artist.html', artist=dbData)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # if artist doesn't exist retun page 404
  artist = Artist.query.get(artist_id)
  try:
    artist.name
  except:
    abort(404)
  
  # prepare genres
  genres = []
  for genre in artist.genres:
    genres.append(genre.name)
  

  dbData = {
    "id": artist.id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link, 
  }
  # return dbData;

  # leaving mock data for reference 
  mockArtist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=dbData)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  # if artist doesn't exist retun page 404
  artist = Artist.query.get(artist_id)
  try:
    artist.name
  except:
    abort(404)

  data = request.form
  
  # validate input data
  form = ArtistForm()

  if not form.validate_on_submit():
    flash('invalid input fields')
    return redirect(url_for('index'))
  
    
  error = False
  try:
    # updating data 
    artist.name =  data['name'] 
    artist.city = data['city'] 
    artist.state = data['state'] 
    artist.phone = data['phone'] 
    artist.facebook_link = data['facebook_link'] 
    artist.image_link = data['image_link'] 
    artist.website = data['website']
    artist.seeking_venue = True if 'seeking_venue' in data.keys() else False 
    artist.seeking_description = data['seeking_description'] 
 
    # update genre
    # first empty the artist genres
    artist.genres = []
    for genre_name in form.genres.data:
      genre = ArtistGenre(name = genre_name)
      artist.genres.append(genre)

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

  if error:
    # on unsuccessful db update flask an error instead
    flash('update  failed')
  else:
    flash('update was successful!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # if venue doesn't exist retun page 404
  venue = Venue.query.get(venue_id)
  try:
    venue.name
  except:
    abort(404)
  
  # prepare genres
  genres = []
  for genre in venue.genres:
    genres.append(genre.name)
  
  dbData = {
    "id": venue.id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }

  # leaving mock data for reference
  mockVenue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  #  populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=dbData)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  # if artist doesn't exist retun page 404
  venue = Venue.query.get(venue_id)
  try:
    venue.name
  except:
    abort(404)

  data = request.form

   # validate input data
  form = VenueForm()

  if not form.validate_on_submit():
    flash('invalid input fields')
    return redirect(url_for('index'))

    
  error = False
  try:
    # updating data
    
    venue.name =  data['name']
    venue.city = data['city']
    venue.state = data['state']
    venue.address = data['address']
    venue.phone = data['phone']
    venue.facebook_link = data['facebook_link']
    venue.image_link = data['image_link']
    venue.website = data['website']
    venue.seeking_talent = True if 'seeking_talent' in data.keys() else False 
    venue.seeking_description = data['seeking_description']
 
    # update genre
    # first empty the venue genres
    venue.genres = []
    for genre_name in form.genres.data:
      genre = VenueGenre(name = genre_name)
      venue.genres.append(genre)
  
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

  if error:
    # on unsuccessful db update flask an error instead
    flash('update failed')
  else:
    flash('update was successful!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  data = request.form
  form = ArtistForm()

  # validate input data
  if not form.validate_on_submit():
    flash('invalid input fields')
    return redirect(url_for('index'))

  error = False
  try:
    artist = Artist(
      name = data['name'],
      city = data['city'],
      state = data['state'],
      phone = data['phone'],
      facebook_link = data['facebook_link'],
      image_link = data['image_link'],
      website = data['website'],
      seeking_venue = True if 'seeking_venue' in data.keys() else False,
      seeking_description = data['seeking_description']
    )
    # insert multiple genres
    for genre_name in form.genres.data:
      genre = ArtistGenre(name = genre_name)
      artist.genres.append(genre)
    db.session.add(artist)	
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  
  # getting all the shows 
  # I was thinking getting only the upcomming shows 
  # but in the mock data there were shows in the past (2019)
  shows = Show.query.join('venue').join('artist').all()
  dbData = []
  for show in shows:
    dbData.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })

# leaving muck data for reference
  mockData=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]

  # using real db data
  return render_template('pages/shows.html', shows=dbData)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead

  form = ShowForm()
  # validate input data
  if not form.validate_on_submit():
    flash('invalid input fields')
    return redirect(url_for('index'))

  error = False
  try:
    data = request.form
    # this line to ensure that the time field is in a correct form
    # or else throw an error
    datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')

    venue = Venue.query.get(data['venue_id'])
    artist = Artist.query.get(data['artist_id'])
    show = Show(
      venue_id = venue.id,
      artist_id = artist.id,
      start_time = data['start_time']
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
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  else:
    # on successful db insert, flash success
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
