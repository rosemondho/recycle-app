
"""Server for recyclers app."""

from flask import Flask, render_template, request, flash, session, redirect, url_for
from model import connect_to_db
from pprint import pformat
from urllib.parse import urlencode
import os
import requests
import json
import crud

#this throws errors when a variable is undefined, otherwise no error
from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"

API_KEY = os.environ['EARTH911_KEY']

app.jinja_env.undefined = StrictUndefined

# have a search option
# menu on top to log in
# create an account 
# profile to get to show all favorite recyclers
# update to database based on what you're grabbing from API


 
@app.route('/')
def homepage():
    """View homepage"""

    return render_template('homepage.html')


@app.route('/searchbyzip', methods=['GET'])
def find_recycler_by_zip():
    """Create a new uesr."""
    postalcode = request.args.get('zipcode')
    maxdistance = request.args.get('radius')
    print(postalcode)
    print(maxdistance)
    url = f'http://api.earth911.com/earth911.getPostalData'
    payload = {'api_key': API_KEY,
               'country': 'US',
               'postal_code': postalcode}

    response = requests.get(url, params=payload)
    data = response.json()
    latitude = data['result']['latitude']
    longitude = data['result']['longitude']
    print(latitude, longitude)
    
    location_url = f'http://api.earth911.com/earth911.searchLocations'
    payload = {'api_key': API_KEY,
               'latitude': latitude,
               'longitude': longitude,
               'max_distance': maxdistance,
               'max_results': 5}
    response = requests.get(location_url, params=payload)
    final_data = response.json()
    print(final_data)
    recyclers = final_data['result']    # entire list of locations
    
    # Get address from location
    loc_ids = []
    locdetails_url = f'http://api.earth911.com/earth911.getLocationDetails'
    for recycler in recyclers:
        loc_ids.append(recycler['location_id'])
    print('TYPE loc_ids: ', type(loc_ids))
    print("LOCATION IDs: ", loc_ids)
    payload = {'api_key': API_KEY,
                'location_id[]': loc_ids}
    response = requests.get(locdetails_url, params=payload)
    loc_details = response.json()
    loc_details = loc_details['result']
    print('LOC_DETAILS:', loc_details)
    
    return render_template('nearest_recyclers.html',
                            pformat=pformat,
                            data=final_data,
                            recyclers=recyclers,
                            loc_details=loc_details)
    

@app.route('/recycler/<location_id>')
def show_recycler(location_id):
    """Show details of a particular recycler"""
    # interact with API to call more details  
    locdetails_url = f'http://api.earth911.com/earth911.getLocationDetails'
    print("LOCATION ID: ", location_id)
    payload = {'api_key': API_KEY,
                'location_id[]': location_id}
    response = requests.get(locdetails_url, params=payload)
    loc_detail = response.json()
    recycler = loc_detail['result'][location_id]
    materials = recycler['materials'] 
    print('Recycler:', recycler)
    print('Accepted Materials:', materials) 

    return render_template('recycler_details.html',
                           recycler=recycler,
                           materials=materials,
                           location_id=location_id)

# make a dedicated route for handling to favorite a recycler
# set it up like setting up details page
# pulling user_id from session to populate info 
# have a text box in form where to submit
# app.route: def make_favorite(location_id): [action of favoriting]
# /makefavorite
# app.route: def favorites_page(): [actual favorited page]
# submit form, get details from form, call crud, redirect location details
@app.route("/add_to_favorites/<location_id>")
def add_to_favorites(location_id):
    """Add a recycler to favorites and redirect to Favorites page.

    When a melon is added to the cart, redirect browser to the shopping cart
    page and display a confirmation message: 'Melon successfully added to
    cart'."""

    # The logic here should be something like:
    #
    # - check if a "cart" exists in the session, and create one (an empty
    #   dictionary keyed to the string "cart") if not
    # - check if the desired melon id is the cart, and if not, put it in
    # - increment the count for that melon id by 1
    # - flash a success message
    # - redirect the user to the cart page
    # add it to database to show user 


    session.setdefault(session['Current User'],{})  
    fav_recycler = session["favorites"]    # {location_id : comments} 
    
    # get name of recycler from API
    locdetails_url = f'http://api.earth911.com/earth911.getLocationDetails'
    payload = {'api_key': API_KEY,
              'location_id[]': location_id}
    response = requests.get(locdetails_url, params=payload)
    loc_details = response.json()
    print("Location Details: ", loc_details)
    recycler_name = loc_details['result'][location_id]['description']

    flash(f"{recycler_name} was successfully added to Favorites.")
    return redirect("/favorites")


@app.route("/favorites")
def show_favorite_recyclers(location_id):
    """Display list of favorited recyclers."""

    fav_recyclers = session["favorites"]
    fav_recycler_list = []
    for recycler in fav_recyclers:
        fav_recycler_list.append(location_id)

    print(fav_recycler_list[0]['result'][location_id]['description'])
    print(fav_recycler_list)
    return render_template("favorites.html", 
                            favorites=fav_recycler_list)


@app.route('/createaccount')
def create_account():
    """Create account for a new user."""
    return render_template('create_account.html')


@app.route('/createaccount', methods=['POST'])
def register_user():
    """Create a new uesr."""
    new_name = request.form.get('name')
    new_email = request.form.get('email')
    new_password = request.form.get('password')

     # if email exists, flash message to say you can't create an account 
     # if it doens't, create new user flash message telling it created successfully

    user = crud.get_user_by_email(new_email)

    if user:
        flash("Can't create an account with that email. Try again.")
    else: 
        crud.create_user(new_name, new_email, new_password)
        flash('Account created. Please log in.')
    
    return redirect('/')

@app.route('/login')
def login():
    """Login page for a user."""

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_user():
    user_email = request.form.get('email')
    user_password = request.form.get('password') 

    user_id = crud.user_id_if_match(user_email, user_password)
    session.setdefault('Current User', user_id) 
    print('SESSION: ', session)
    print('USER ID: ', user_id)
    

    if user_id:
        flash('Logged in!')
        return redirect(url_for('show_user', user_id=user_id))
    else:
        flash("Email or password incorrect. Try again.")
        return redirect('/login')


@app.route('/<user_id>')
def show_user(user_id):
    """Show users info based on the specified user_id"""
    print('ENTERED SHOW_USER FN')
    print('Type: ', type(user_id))
    user = crud.get_user_by_id(user_id)
    print('GOT USER')
    print(user)

    return render_template('user_profile.html', user=user)

@app.route('/logout')
def logout_user():
    """Logs out user."""
    if session['Current User']:    
        session.pop('Current User', None)
        flash("Successfully logged out.")

    return render_template('homepage.html')




if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)
