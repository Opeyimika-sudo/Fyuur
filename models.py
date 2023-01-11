from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String())

    genres = db.Column(db.String())
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    show = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue ID: {self.id}, Venue Name: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String())
    state = db.Column(db.String())
    phone = db.Column(db.String())
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String())

    genres = db.Column(db.String())
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    show = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist ID: {self.id}, Artist Name: {self.name}>'

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    start_time= db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))