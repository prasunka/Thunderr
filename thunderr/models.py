from . import db


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(500))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(1024))
    facebook_link = db.Column(db.String(1024))

    # artists = db.relationship('Show', backref=db.backref('venues', lazy=True))
    artist = db.relationship('Show', back_populates='venue')

    def __repr__(self):
        return f'<{self.id, self.name, self.city, self.state, self.address, self.phone, self.image_link, self.facebook_link}>'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(1024))
    facebook_link = db.Column(db.String(1024))

    venue = db.relationship('Show', back_populates='artist')

    def __repr__(self):
        return f'<{self.id, self.name, self.city, self.state, self.phone, self.genres, self.image_link, self.facebook_link}>'


class Show(db.Model):
    __tablename__ = 'bookedshow'

    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime(), primary_key=True)

    artist = db.relationship('Artist', back_populates='venue')
    venue = db.relationship('Venue', back_populates='artist')
