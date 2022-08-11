#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from datetime import datetime
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from sqlalchemy import func , or_
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
from models import Venue , Artist , Show , app , db
import sys


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database(valider)
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI']=SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config.from_object('config')
migrate=Migrate(app , db)





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
  # TODO: replace with real venues data.(valider)
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  #search cities and state
  data1=Venue.query.with_entities(Venue.city , Venue.state).distinct()

  #search all venues inside the current city using python generator
  data=[{"city":area.city ,
  "state":area.state ,
  "venues":[{"id":venues.id , 
  "name":venues.name , 
  "num_upcoming_shows":len(Show.query.join(Artist , Artist.id==Show.venue_id ).filter(Show.start_time > datetime.now() , Show.venue_id ==venues.id).all())}
  for venues in Venue.query.filter_by(city=area.city , state=area.state).all()]
   }
  for area in data1 ]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST' , 'GET'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.(valider)
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  result=Venue.query.filter(or_(func.lower(Venue.name).like('%' +search_term.lower()+ '%') , func.lower(Venue.city).like('%' +search_term.lower()+ '%') , func.lower(Venue.state).like('%' +search_term.lower()+ '%'))).all()
  response={
    "count": len(result),
    "data": [{
      "id": area.id,
      "name": area.name,
      "num_upcoming_shows": len(Show.query.join(Artist , Artist.id==Show.venue_id ).filter(Show.start_time > datetime.now() , Show.venue_id ==area.id).all())
    }
     for area in result
    ]
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id(valider)
  data1=[{
    "id": area.id,
    "name": area.name,
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": area.address,
    "city": area.city,
    "state": area.city,
    "phone": area.phone,
    "website": area.website,
    "facebook_link": area.facebook_link,
    "seeking_talent": area.seeking_talent,
    "seeking_description": area.seeking_description,
    "image_link": area.image_link,
    "past_shows": [{
      "artist_id": past.artist.id,
      "artist_name": past.artist.name ,
      "artist_image_link": past.artist.image_link,
      "start_time": str(past.start_time)
    } 
    for past in Show.query.join(Artist , Artist.id==Show.venue_id ).filter(Show.start_time < datetime.now() , Show.venue_id ==area.id).all()
    ],
    "upcoming_shows": [
      {
      "artist_id": past.artist.id,
      "artist_name": past.artist.name ,
      "artist_image_link": past.artist.image_link,
      "start_time": str(past.start_time)
    } 
    for past in Show.query.join(Artist , Artist.id==Show.venue_id ).filter(Show.start_time > datetime.now() , Show.venue_id ==area.id).all()
    ],
    "past_shows_count": len(Show.query.join(Artist , Artist.id==Show.venue_id ).filter(Show.start_time < datetime.now() , Show.venue_id ==area.id).all()) ,
    "upcoming_shows_count": len(Show.query.join(Artist , Artist.id==Show.venue_id ).filter(Show.start_time > datetime.now() , Show.venue_id ==area.id).all()) 
  }
  for area in Venue.query.all()
  ]
  data = list(filter(lambda d: d['id'] == venue_id, data1))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
    

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead(valider)
  try:
    form = VenueForm(request.form)
  # TODO: modify data to be the data object returned from db insertion(valider)
    venue=Venue(
    name=form.name.data, 
    genres=form.genres.data, 
    address=form.address.data, 
    city=form.city.data,
    state=form.state.data ,
    phone=form.phone.data, 
    website= form.website_link.data, 
    facebook_link=form.facebook_link.data, 
    seeking_description=form.seeking_description.data, 
    seeking_talent=form.seeking_talent.data, 
    image_link=form.image_link.data
    ) 
    db.session.add(venue)
    db.session.commit()
    print('mon message perso')
  # on successful db insert, flash success
    flash('Venue ' + venue.name + ' was successfully listed!')
  except:
   # TODO: on unsuccessful db insert, flash an error instead.(valider)
   db.session.rollback()
   flash('An error occurred. Venue '+venue.name+' could not be listed.')
  finally:
   db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/delete/<int:venue_id>', methods=['DELETE' ,'POST' , 'GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using(valider)
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue=Venue.query.filter(Venue.id==venue_id).first()
    db.session.delete(venue)
    db.session.commit()
    print('mon message perso')
  # on successful db insert, flash success
    flash('Venue  was successfully deleted!')
  except:
   # TODO: on unsuccessful db insert, flash an error instead.(valider)
   db.session.rollback()
   flash('An error occurred. Venue could not be deleted.')
  finally:
   db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database(valider)
  data=[{
    "id": artist.id,
    "name": artist.name
  }
  for artist in Artist.query.all()
  ]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.(valider)
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  result=Artist.query.filter(or_(func.lower(Artist.name).like('%' +search_term.lower()+ '%') , func.lower(Artist.city).like('%' +search_term.lower()+ '%') , func.lower(Artist.state).like('%' +search_term.lower()+ '%'))).all()
  response={
    "count": len(result),
    "data": [{
      "id": area.id,
      "name": area.name,
      "num_upcoming_shows": len(Show.query.join(Artist , Artist.id==Show.artist_id ).filter(Show.start_time > datetime.now() , Show.artist_id ==area.id).all())
    }
     for area in result
    ]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id(valider)
  data1=[{
    "id": area.id,
    "name": area.name,
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "city": area.city,
    "state": area.city,
    "phone": area.phone,
    "website": area.website,
    "facebook_link": area.facebook_link,
    "seeking_talent": area.seeking_venue,
    "seeking_description": area.seeking_description,
    "image_link": area.image_link,
    "past_shows": [{
      "venue_id": past.venue.id,
      "venue_name": past.venue.name ,
      "venue_image_link": past.venue.image_link,
      "start_time": str(past.start_time)
    } 
    for past in Show.query.join(Artist , Artist.id==Show.venue_id ).filter(Show.start_time < datetime.now() , Show.artist_id ==area.id).all()
    ],
    "upcoming_shows": [
      {
      "venue_id": past.venue.id,
      "venue_name": past.venue.name ,
      "venue_image_link": past.venue.image_link,
      "start_time": str(past.start_time)
    } 
    for past in Show.query.join(Artist , Artist.id==Show.venue_id ).filter(Show.start_time > datetime.now() , Show.artist_id ==area.id).all()
    ],
    "past_shows_count": len(Show.query.join(Artist , Artist.id==Show.venue_id ).filter(Show.start_time < datetime.now() , Show.artist_id ==area.id).all()) ,
    "upcoming_shows_count": len(Show.query.join(Artist , Artist.id==Show.venue_id ).filter(Show.start_time > datetime.now() , Show.artist_id ==area.id).all()) 
  }
  for area in Artist.query.all()
  ]
  data = list(filter(lambda d: d['id'] == artist_id, data1))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artists=Artist.query.filter(Artist.id==artist_id).all()
  value=[result for result in artists]
  artist=value[0]
  form.name.data=value[0].name
  form.genres.data=value[0].genres
  form.city.data=value[0].city
  form.state.data=value[0].state
  form.phone.data=value[0].phone
  form.website_link.data=value[0].website
  form.facebook_link.data=value[0].facebook_link
  form.seeking_venue.data=value[0].seeking_venue
  form.seeking_description.data=value[0].seeking_description
  form.image_link.data=value[0].image_link
  # TODO: populate form with fields from artist with ID <artist_id>(valider)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing(valider)
  # artist record with ID <artist_id> using the new attributes

  try:
    form = ArtistForm(request.form)
  # TODO: modify data to be the data object returned from db insertion(valider)
    artist=Artist.query.filter(Artist.id==artist_id).first()
    artist.name=form.name.data
    artist.genres=form.genres.data
    artist.city=form.city.data
    artist.state=form.state.data 
    artist.phone=form.phone.data
    artist.website= form.website_link.data
    artist.facebook_link=form.facebook_link.data
    artist.seeking_description=form.seeking_description.data
    artist.seeking_venue=form.seeking_venue.data
    artist.image_link=form.image_link.data
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully updated!')
  except:
   # TODO: on unsuccessful db insert, flash an error instead.(valider)
   flash('An error occurred. Artist '+form.name.data+' could not be update.')
   db.session.rollback()
  finally:
   db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venues=Venue.query.filter(Venue.id==venue_id).all()
  value=[result for result in venues]
  venue=value[0]
  form.name.data=value[0].name
  form.genres.data=value[0].genres
  form.address.data=value[0].address
  form.city.data=value[0].city
  form.state.data=value[0].state
  form.phone.data=value[0].phone
  form.website_link.data=value[0].website
  form.facebook_link.data=value[0].facebook_link
  form.seeking_talent.data=value[0].seeking_talent
  form.seeking_description.data=value[0].seeking_description
  form.image_link.data=value[0].image_link
  # TODO: populate form with values from venue with ID <venue_id>(valider)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing(valider)
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm(request.form)
  # TODO: modify data to be the data object returned from db insertion(valider)
    venue=Venue.query.filter(Venue.id==venue_id).first()
    venue.name=form.name.data
    venue.genres=form.genres.data
    venue.address=form.address.data
    venue.city=form.city.data
    venue.state=form.state.data 
    venue.phone=form.phone.data
    venue.website= form.website_link.data
    venue.facebook_link=form.facebook_link.data
    venue.seeking_description=form.seeking_description.data
    venue.seeking_talent=form.seeking_talent.data
    venue.image_link=form.image_link.data
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully updated!')
  except:
   # TODO: on unsuccessful db insert, flash an error instead.(valider)
   flash('An error occurred. Venue '+form.name.data+' could not be update.')
   db.session.rollback()
  finally:
   db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
   # TODO: insert form data as a new artist record in the db, instead(valider)
  try:
    form = ArtistForm(request.form)
  # TODO: modify data to be the data object returned from db insertion(valider)
    artist=Artist(
    name=form.name.data, 
    genres=form.genres.data, 
    city=form.city.data,
    state=form.state.data ,
    phone=form.phone.data, 
    website= form.website_link.data, 
    facebook_link=form.facebook_link.data, 
    seeking_description=form.seeking_description.data, 
    seeking_venue=form.seeking_venue.data, 
    image_link=form.image_link.data
    ) 
    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
   # TODO: on unsuccessful db insert, flash an error instead.(valider)
   flash('An error occurred. Artist '+form.image_link.data+' could not be listed.')
   db.session.rollback()
  finally:
   db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.(valider)
  data=[{
    "venue_id": area.venue_id,
    "venue_name": area.venue.name ,
    "artist_id": area.artist_id,
    "artist_name": area.artist.name,
    "artist_image_link": area.artist.image_link,
    "start_time": str(area.start_time)
  }
  for area in Show.query.join(Artist , Artist.id==Show.venue_id ).all()
  ]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
   # TODO: insert form data as a new artist record in the db, instead(valider)
  try:
    form =  ShowForm(request.form)
  # TODO: modify data to be the data object returned from db insertion(valider)
    show=Show(
    venue_id=form.venue_id.data, 
    artist_id=form.artist_id.data, 
    start_time=form.start_time.data
    ) 
    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
   # TODO: on unsuccessful db insert, flash an error instead(valider)
   flash('An error occurred. Show could not be listed.')
   db.session.rollback()
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
