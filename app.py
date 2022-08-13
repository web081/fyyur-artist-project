#from model import db_setup, Venue, Artist, Show
from multiprocessing import Event
from flask import Flask, render_template, request, flash, redirect, url_for, abort
import operator 
import dateutil.parser
import re
import babel
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from datetime import datetime
from flask_migrate import Migrate


#import urllib.parse

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app) 
Migrate = Migrate(app, db)

# import  models and table from model
from model import *
#defaults time format
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

 # TODO: replace with real venues data.
@app.route('/venues')
def venues():
    venues = Venue.query.all() # query all table using .all()
    result = [] 
    location = set()  # use set() to set city and state
    for venue in venues: # iterate or loop all venue details
      print(venue)
      location.add( (venue.city, venue.state) ) 
    location = list(location)  
    location.sort(key=operator.itemgetter(1,0)) 
    now = datetime.now() 
    for i in location:
     item_list = []
     for venue in venues:
       if (venue.city == i[0]) and (venue.state == i[1]): 
         venue_show = Show.query.filter_by(venue_id=venue.id).all()
         event_num = 0
         for show in venue_show:
          if show.start_time > now:
           event_num += 1
           item_list.append({
             "id": venue.id,
             "name": venue.name,
             "num_upcoming_shows": event_num
                })
           
         result.append({
            "city": i[0],
            "state": i[1],
            "venues": item_list
        })
     return render_template('pages/venues.html', areas=result)
 
# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
@app.route('/venues/search', methods=['POST'])
def search_venues():  
    #  venues query all() and filter name on the search
    venues = Venue.query.filter(Venue.name.ilike('%' 
     + request.form.get('search_term', '') 
     + '%')).all()
    venue_query = []   
    now = datetime.now()
    for venue in venues:
      venue_shows = Show.query.filter_by(venue_id=venue.id).all()
      num_upcoming = 0
      # loop through query to map results
      for show in venue_shows:   
        if show.start_time > now:
         num_upcoming += 1
         # append results to empty list
         venue_query.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming
            })
         # search for "Music" should return "The Musical Hop"
    response = {
           "count": len(venues),
            "data": venue_query
          }        
            
    return render_template('pages/search_venues.html', results=response, search_term= request.form.get('search_term', '') )           
      
 # TODO: replace with real venue data from the venues table, using venue_id    
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
      # show venue id from database
    venue = Venue.query.filter_by(venue_id) 
    past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()   
    past_shows = []
    past_shows_count = 0
    now = datetime.now()
    for show in past_shows_query:
      if show.start_time < now:
        past_shows_count += 1
        past_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))
                      })
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show. start_time>datetime.now()).all()   
    upcoming_shows = []
    now = datetime.now()
    upcoming_shows_count = 0
    for show in upcoming_shows_query:
     if show.start_time > now:
      upcoming_shows_count += 1 
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))}) 
    data = {
      "id": venue_id,
      "name": venue.name,
      "genres": venue.genres,
      "city": venue.city,
      "state": venue.state,
      "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
      "website_link": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_venue": venue.seeking_venue,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": upcoming_shows_count  }                      
    return render_template('pages/show_venue.html', venue=data)  
 
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form) # pass request.form to form constructor
    try:             # try to create submission
      name =form.name.data
      city=form.city.data
      state=form.state.data
      address=form.address.data
      phone =form.phone.data
      phone = re.sub('\D', '', str(phone)) # use string convert 819-392-1234 --> 8193921234
      genres = form.genres.data            
      seeking_talent = True if form.seeking_talent.data == 'Yes' else False # check for true or false
      seeking_description = form.seeking_description.data
      image_link = form.image_link.data
      website_link = form.website_link.data
      facebook_link = form.facebook_link.data
      # TODO: insert form data as a new Venue record in the db, instead
           # create a new venue to the database and flash response
      new_item = Venue(name=name, 
                  city=city, 
                  state=state, 
                  address=address,
                  phone=phone,
                  genres=genres, 
                  seeking_talent=seeking_talent, 
                  seeking_description=seeking_description, 
                  image_link=image_link,
                  website_link=website_link, 
                  facebook_link=facebook_link)
    
      db.session.add(new_item)
      db.session.commit()
      flash('venue successfully created')
    except: 
      db.session.rollback()
      flash('error, unable to create venue')
    finally: 
      db.session.close()
      return render_template('pages/home.html')
            
      
      
      
  
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    #error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
      db.session.rollback()
  finally:  
   return render_template('pages/venues.html', venue_id=venue_id)
      
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
 

#  Artists
#  ----------------------------------------------------------------
# TODO: replace with real data returned from querying the database
@app.route('/artists')
def artists():
  # Query artist database and sort alphabetically
  artists = Artist.query.order_by(Artist.name).all()
  result = []
  for artist in artists: # iterate or loop through all
        result.append({
          "id": artist.id,
          "name": artist.name
        })
  return render_template('pages/artists.html', artists=result)

@app.route('/artists/search', methods=['POST'])
def search_artists():
     # because of case sensitivity, use filter instead 
    artists= Artist.query.filter(Artist.name.ilike('%' + request.form.get('search_term', '')+ '%')).all()
    artist_search = []
    now = datetime.now()
    for artist in artists:
            artist_shows = Show.query.filter_by(venue_id=artist.id).all()
            num_upcoming = 0
            for show in artist_shows:
                  if show.start_time > now:
                        num_upcoming += 1
            artist_search.append({
              "id": artist.id,
              "name": artist.name,
              "num_upcoming_shows": num_upcoming
            })
    response = {
           "count": len(artists),
            "data": artist_search
          }           
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  # TODO: replace with real artist data from the artist table, using artist_id
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # show artist list and past event from database using dictionary 
  artist = Artist.query.get(artist_id)
  print(artist) 
  past_shows = []
  past_shows_count = 0
  upcoming_shows = []
  upcoming_shows_count = 0
  now = datetime.now()
  # shows the artist page with the given artist_id
  for show in artist.shows:
      if show.start_time > now:
         upcoming_shows_count += 1
         upcoming_shows.append({
               "venue_id": show.venue_id,
               "venue_name": show.venue.name,
               "venue_image_link": show.venue.image_link,
               "start_time": format_datetime(str(show.start_time))
                })
      if show.start_time < now:
            past_shows_count += 1
            past_shows.append({
               "venue_id": show.venue_id,
               "venue_name": show.venue.name,
               "venue_image_link": show.venue.image_link,
               "start_time": format_datetime(str(show.start_time))
                })
  result = {
            "id": artist_id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
            "website_link": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "past_shows_count": past_shows_count,
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": upcoming_shows_count
        }             
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=result)

#  Update
#  ----------------------------------------------------------------
# TODO: populate form with fields from artist with ID <artist_id>
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # pass request.form to artist
  form = ArtistForm(request.form)
  # query artist database for artist with ID <artist_id> using get artist
  artist = Artist.query.get(artist_id)
  artist={
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres ,
    "state": artist.state,
    "phone": (artist.phone[:3] + '_' + artist.phone[3:6] + '_' + artist.phone[6:]),
    "website_link": artist.website_link,
    "facebook": artist.facebook_link,
    "seeking_talent": artist.seeking_talent,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link   
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)
# TODO: take values from the form submitted, and update existing
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    # pass request.form to form
    try:  
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      phone = re.sub('\D', '', str(phone)) 
      genres = form.genres.data                  
      seeking_talent = True if form.seeking_talent.data == 'Yes' else False
      seeking_description = form.seeking_description.data
      image_link = form.image_link.data
      website_link = form.website_link.data
      facebook_link = form.facebook_link.data
        # query database for return values or object
      artist = Artist.query.filter_by(artist_id) 
      artist.name = name
      artist.city = city
      artist.state = state
      artist.phone = phone  
      artist.genres = genres       
      artist.seeking_talent = seeking_talent
      artist.seeking_description = seeking_description
      artist.image_link = image_link
      artist.website_link = website_link
      artist.facebook_link = facebook_link
          
      db.session.commit()
      flash('artist was successfully updated!')
    except:
          print (' something is wrong with edit_artist_submission()')
          db.session.rollback()
    finally:
          db.session.close()           
          return redirect(url_for('show_artist', artist_id=artist_id))  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres ,
    "address": venue.address,
    "state": venue.state,
    "phone": (venue.phone[:3] + '_' + venue.phone[3:6] + '_' + venue.phone[6:]),
    "website_link": venue.website_link,
    "facebook": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link   
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue)
# TODO: take values from the form submitted, and update existing
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    # pulling venue detail from database and inserting updated venue
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      address = form.address.data
      phone = form.phone.data
      phone = re.sub('\D', '', str(phone)) 
      genres = form.genres.data                  
      seeking_talent = True if form.seeking_talent.data == 'Yes' else False
      seeking_description = form.seeking_description.data
      website_link = form.website_link.data
      image_link = form.image_link.data
      facebook_link = form.facebook_link.data
       # creating update values into the database
      venue = Venue.query.get(venue_id) 
      venue.name = name
      venue.city = city
      venue.state = state
      venue.address = address
      venue.phone = phone         
      venue.seeking_talent = seeking_talent
      venue.seeking_description = seeking_description
      venue.image_link = image_link
      venue.website = website_link
      venue.facebook_link = facebook_link
      venue.genres = genres
      db.session.commit()
      flash(' list was successfully updated!')
    except:
          db.session.rollback()
          flash(' error occurred was not successfully updated!'  ) 
          print (' something is wrong with update')
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
    form = ArtistForm(request.form)
    try:  
      name =form.name.data
      city=form.city.data
      state=form.state.data
      phone = form.phone.data
      phone = re.sub('\D', '', str(phone)) 
      genres = form.genres.data            
      seeking_venue = True if form.seeking_venue.data == 'Yes' else False
      seeking_description = form.seeking_description.data
      image_link = form.image_link.data
      website_link = form.website_link.data
      facebook_link = form.facebook_link.data
           # creating new artist into the database 
      new_artist = Artist(name=name, 
                          city=city, 
                          state=state, 
                          phone=phone,
                          genres=genres, 
                          seeking_venue=seeking_venue, 
                          seeking_description=seeking_description, 
                          image_link=image_link,
                          website_link=website_link, 
                          facebook_link=facebook_link)
      
      db.session.add(new_artist)
      db.session.commit()
      flash( 'Artist was successfully listed!')
    except (e):       
      db.session.rollback()
      print('error occurred '+ (e) + 'in creating artist')
    finally:
      db.session.close()
      return render_template('pages/home.html')
         

#  Shows
#  ----------------------------------------------------------------

# TODO: replace with real venues data.
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  result = []
  shows = Show.query.all() # query all in the database
      
  for show in shows:
            result.append({
              "venue_id": show.venue.id,
              "venue_name": show.venue.name,
              "artist_id": show.artist.id,
              "artist_name": show.artist.name,
              "artist_image_link": show.venue.image_link,
              "start_time": format_datetime(str(show.start_time)),
         })    
      
  return render_template('pages/shows.html', shows=result) 

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    # create new show (relationship between artist and venue)
    try:
        artist_id = form.artist_id.data
        venue_id = form.venue_id.data
        start_time = form.start_time.data
        new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time )
        db.session.add(new_show)
        db.session.commit()
        flash('show was successfully listed!')
    except:
        db.session.rollback()
        flash(' an error occurred while creating show')
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
