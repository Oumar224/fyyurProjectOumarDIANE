from flask import Flask
from flask_sqlalchemy import SQLAlchemy 


app = Flask(__name__)
db = SQLAlchemy(app , session_options={"expire_on_commit":False})

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'
    # __searchable__=['name' , 'address' , 'genres'  , 'city' , 'state']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.PickleType)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean , default=False)
    seeking_description=db.Column(db.Text)
    image_link = db.Column(db.String(500))
    shows=db.relationship('Show', backref='venue', lazy=True)
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate(valider)

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.PickleType)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue=db.Column(db.Boolean , default=False)
    seeking_description=db.Column(db.Text)
    image_link = db.Column(db.String(500))
    shows=db.relationship('Show', backref='artist', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate(valider)

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True) 
    venue_id=db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id=db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    start_time=db.Column(db.DateTime , nullable=False)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.(valider)