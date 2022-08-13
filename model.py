from sqlalchemy import String, ARRAY
#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db





# TODO: connect to a local postgresql database
 # local connection db 
class Show(db.Model):
    __tablename__ = 'show'
      # define relationships between artist and venue
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    
class Venue(db.Model):
    __tablename__ = 'venue'
     
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(ARRAY(String))
    # define relationship with venues
    shows = db.relationship('Show', backref='venue', lazy=True)
    
    def __repr__(self):
           return f'<Venue {self.id}{self.name} { self.city}{self.state} {self.phone}{self.address}{self.genres}{self.image_link}{self.facebook_link}{self.website_link}{self.seeking_talent}{self.seeking_description}>'
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)    
    seeking_description = db.Column(db.String(120))
    # define relationship with artists
    shows = db.relationship('Show', backref='artist', lazy=True)
    
    def __repr__(self):
        return f'<Artist {self.id} {self.name} { self.city}{self.state} {self.phone}{self.genres}{self.image_link}{self.facebook_link}{self.website_link}{self.seeking_venue}{self.seeking_description}>'
class Genres(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)  