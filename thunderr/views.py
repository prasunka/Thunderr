import sys

from .models import *
from .utils import *
from .forms import *

from flask import render_template, request
from flask import flash, redirect, url_for, abort, jsonify
from flask.helpers import make_response


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  ---------------------------------- Venues ----------------------------------


@app.route('/venues')
def venues():
    try:
        areas = []
        for city, state in db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all():
            area = {}
            venues = []
            for venue in Venue.query.filter(Venue.city == city, Venue.state == state).all():
                v = {}
                v['id'] = venue.id
                v['name'] = venue.name
                v['image_link'] = venue.image_link
                v['num_upcoming_shows'] = 0
                venues.append(v)
            area['city'] = city
            area['state'] = state
            area['venues'] = venues
            areas.append(area)
    except:
        print(sys.exc_info())
        abort(500)

    return render_template('pages/venues.html', areas=areas)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venues = []
    results = Venue.query.filter_by(id=venue_id).all()
    print(len(results))
    if len(results) == 0:
        abort(404)
        print('here')

    try:
        for row in results:
            venue = dict(row.__dict__)
            venue.pop('_sa_instance_state', None)

            past_shows = db.session.query(Show).filter(Show.venue_id == venue['id'],
                                                       Show.start_time < datetime.now()).all()
            venue['past_shows'] = []
            for s in past_shows:
                d_show = {}
                d_show['artist_id'] = s.artist_id
                d_show['start_time'] = s.start_time.strftime("%Y-%m-%dT%H:%M:%S")
                d_show['artist_name'] = db.session.query(Artist.name).filter(Artist.id == s.artist_id).one()[0]
                d_show['artist_image_link'] = \
                    db.session.query(Artist.image_link).filter(Artist.id == s.artist_id).one()[0]
                venue['past_shows'].append(d_show)

            upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue['id'],
                                                           Show.start_time >= datetime.now()).all()
            venue['upcoming_shows'] = []
            for s in upcoming_shows:
                d_show = {}
                d_show['artist_id'] = s.artist_id
                d_show['start_time'] = s.start_time.strftime("%Y-%m-%dT%H:%M:%S")
                d_show['artist_name'] = db.session.query(Artist.name).filter(Artist.id == s.artist_id).one()[0]
                d_show['artist_image_link'] = \
                    db.session.query(Artist.image_link).filter(Artist.id == s.artist_id).one()[0]
                venue['upcoming_shows'].append(d_show)

            venue['past_shows_count'] = len(venue['past_shows'])
            venue['upcoming_shows_count'] = len(venue['upcoming_shows'])

            # print(venue)
            # print()

            venues.append(venue)

        data = venues[0]

    except:
        abort(500)

    return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        form = VenueForm()
        v = Venue()
        v.name = form.name.data
        v.city = form.city.data
        v.state = form.state.data
        v.address = form.address.data
        v.phone = form.phone.data
        v.image_link = form.image_link.data
        v.facebook_link = form.facebook_link.data

        db.session.add(v)
        db.session.commit()

    except:
        db.session.rollback()
        abort(500)

    finally:
        db.session.close()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = Venue.query.get(venue_id)
    if venue is None:
        abort(404)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        form = VenueForm()
        v = Venue.query.get(venue_id)
        v.name = form.name.data
        v.city = form.city.data
        v.state = form.state.data
        v.address = form.address.data
        v.phone = form.phone.data
        v.image_link = form.image_link.data
        v.facebook_link = form.facebook_link.data

        db.session.add(v)
        db.session.commit()

    except:
        db.session.rollback()
        flash('Something went wrong! Try again')
        redirect(url_for('edit_venue', venue_id=venue_id))

    finally:
        db.session.close()
        flash('Information succesfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<int:venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    return render_template('pages/confirm-venue.html', id=venue_id)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue_submission(venue_id):
    try:
        v = Venue.query.get(venue_id)
        db.session.delete(v)
        db.session.commit()
    except:
        print(sys.exc_info())
        flash("Something went wrong! Try again")
        redirect_url = url_for('show_venue', venue_id=venue_id)
        return make_response(jsonify({'redirect_url': redirect_url}), 500)

    finally:
        db.session.close()

    flash('Venue deleted successfully!')
    return make_response('', 204)


#  -------------------------------- Artists --------------------------------

@app.route('/artists')
def artists():
    data = []
    for artist in db.session.query(Artist.id, Artist.name, Artist.image_link).all():
        a = {}
        a['id'] = artist[0]
        a['name'] = artist[1]
        a['image_link'] = artist[2]
        data.append(a)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artists = []
    results = Artist.query.filter_by(id=artist_id).all()
    if (len(results) == 0):
        abort(404)

    try:
        for row in results:
            artist = dict(row.__dict__)
            artist['genres'] = artist['genres'].split(',')
            artist.pop('_sa_instance_state', None)

            past_shows = db.session.query(Show).filter(Show.artist_id == artist['id'],
                                                       Show.start_time < datetime.now()).all()
            artist['past_shows'] = []
            for s in past_shows:
                d_show = {}
                d_show['venue_id'] = s.venue_id
                d_show['start_time'] = s.start_time.strftime("%Y-%m-%dT%H:%M:%S")
                print(s)
                d_show['venue_name'] = db.session.query(Venue.name).filter(Venue.id == s.venue_id).one()[0]
                d_show['venue_image_link'] = db.session.query(Venue.image_link).filter(Venue.id == s.venue_id).one()[0]
                artist['past_shows'].append(d_show)

            upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist['id'],
                                                           Show.start_time >= datetime.now()).all()
            artist['upcoming_shows'] = []
            for s in upcoming_shows:
                d_show = {}
                d_show['venue_id'] = s.venue_id
                d_show['start_time'] = s.start_time.strftime("%Y-%m-%dT%H:%M:%S")
                d_show['venue_name'] = db.session.query(Venue.name).filter(Venue.id == s.venue_id).one()[0]
                d_show['venue_image_link'] = db.session.query(Venue.image_link).filter(Venue.id == s.venue_id).one()[0]
                artist['upcoming_shows'].append(d_show)

            artist['past_shows_count'] = len(artist['past_shows'])
            artist['upcoming_shows_count'] = len(artist['upcoming_shows'])

            # print(artist)
            # print()

            artists.append(artist)

        data = artists[0]

    except:
        abort(500)

    return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        form = ArtistForm()
        a = Artist()
        a.name = form.name.data
        a.city = form.city.data
        a.state = form.state.data
        a.genres = ','.join(form.genres.data)
        a.phone = form.phone.data
        a.image_link = form.image_link.data
        a.facebook_link = form.facebook_link.data

        db.session.add(a)
        db.session.commit()

    except:
        db.session.rollback()
        abort(500)

    finally:
        db.session.close()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')



@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)
    if artist is None:
        abort(404)
    artist.genres = artist.genres.split(',')

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        form = ArtistForm()
        a = Artist.query.get(artist_id)
        a.name = form.name.data
        a.city = form.city.data
        a.state = form.state.data
        a.genres = ','.join(form.genres.data)
        a.phone = form.phone.data
        a.image_link = form.image_link.data
        a.facebook_link = form.facebook_link.data

        db.session.add(a)
        db.session.commit()

    except:
        db.session.rollback()
        flash('Something went wrong! Try again')
        redirect(url_for('edit_artist', artist_id=artist_id))

    finally:
        db.session.close()

    flash('Information succesfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<int:artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
    return render_template('pages/confirm-artist.html', id=artist_id)


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist_submission(artist_id):
    try:
        a = Artist.query.get(artist_id)
        db.session.delete(a)
        db.session.commit()
    except:
        print(sys.exc_info())
        flash("Something went wrong! Try again")
        redirect_url = url_for('show_artist', artist_id=artist_id)
        return make_response(jsonify({'redirect_url': redirect_url}), 500)

    finally:
        db.session.close()

    flash('Artist deleted successfully!')
    return make_response('', 204)


#  ----------------------------------- Shows -----------------------------------

@app.route('/shows')
def shows():
    data = []
    for a_show in db.session.query(Show):
        print(a_show)
        s = {}
        s['venue_id'] = a_show.venue_id
        s['artist_id'] = a_show.artist_id
        s['start_time'] = a_show.start_time.strftime("%Y-%m-%dT%H:%M:%S")

        s['venue_name'] = db.session.query(Venue.name).filter(Venue.id == a_show.venue_id).one()[0]
        s['artist_name'] = db.session.query(Artist.name).filter(Artist.id == a_show.artist_id).one()[0]
        s['artist_image_link'] = db.session.query(Artist.image_link).filter(Artist.id == a_show.artist_id).one()[0]

        data.append(s)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()

    try:
        v = Venue.query.filter(Venue.id == form.venue_id.data).one()
    except:
        flash('Venue not found!')
        return render_template('forms/new_show.html', form=ShowForm())

    try:
        a = Artist.query.filter(Artist.id == form.artist_id.data).one()
    except:
        flash('Artist not found!')
        return render_template('forms/new_show.html', form=ShowForm())

    try:
        s = Show(venue_id=v.id, artist_id=a.id, start_time=form.start_time.data)
        db.session.add(s)
        db.session.commit()
        flash('Show was successfully listed!')

    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(500)

    finally:
        db.session.close()

    return render_template('pages/home.html')


# ------------------------- Error Handlers -------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
