from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy()
# migration connection
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #  implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120)) 
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    # Venue Has Many VenueGenres
    genres = db.relationship('VenueGenre', backref='venues', cascade="all, delete", lazy=True) 
    # Venue Has Many Shows
    shows = db.relationship('Show', backref='venue', cascade="all, delete", lazy=True)

    def __repr__(self):
      return f'<{self.id}, {self.name}>'
    

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #  implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    # Artist Has Many ArtistGenres  
    genres = db.relationship('ArtistGenre', backref='artists', cascade="all, delete", lazy=True) 
    # Artist Has Many Shows
    shows = db.relationship('Show', backref='artist', cascade="all, delete", lazy=True)

    def __repr__(self):
      return f'<{self.id}, {self.name}>'


# creating genres tables to avoid multi values in a single field 
# and to achieve achieve 3NF 
# assuming a venue or an artist can has many genres 
class VenueGenre(db.Model):
    __tablename__ = 'venue_genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    def __repr__(self):
      return f'<{self.id}, {self.name}>'
 
class ArtistGenre(db.Model):
    __tablename__ = 'artist_genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    def __repr__(self):
      return f'<{self.id}, {self.name}>'

# creating shows table
class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.String(120), nullable=False)
    def __repr__(self):
      return f'<{self.id}, artist: {self.artist_id}, venue: {self.  venue_id}>'


