
"""Server for recyclers app."""

from flask import Flask, render_template, request, flash, session, redirect, url_for
from model import connect_to_db
from pprint import pformat
import os
import requests

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
    # search function makes a call to API
    # receives data as JSON
    # displays that data and the parts I want and the wait that you want
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
               'max_results': 10}
    response = requests.get(location_url, params=payload)
    print(response)
    final_data = response.json()
    recyclers = final_data['results']
    print(final_data)
    
    # print list of recyclers near that zip code
    # user = crud.get_user_by_email(new_email)
    return render_template('nearest_recyclers.html',
                            pformat=pformat,
                            data=final_data,
                            recyclers=recyclers)
    #return redirect(url_for('/nearest_recyclers', recyclers=recyclers))


# Nearest Recyclers: Show all of them
# Each title of recyclers make into a link
# @app.route('/nearest_recyclers')
# def nearest_recyclers(recyclers):
#     """View nearest recyclers"""    
#     print("entered nearest_recyclers route")
#     return render_template('nearest_recyclers.html', recyclers=recyclers)


@app.route('/recycler/<location_id>')
def show_recycler(location_id):
    """Show details of a particular recycler"""

    #recycler = crud.get_recycler_by_id(recycler_id)

    return render_template('recycler_details.html', recyclers = recyclers)


@app.route('/createaccount')
def create_account():
    """Create account for a new user."""

    #users = crud.get_users()
    return render_template('create_account.html')
#    return render_template('create_account.html', users=users)


@app.route('/createaccount', methods=['POST'])
def register_user():
    """Create a new uesr."""
    new_email = request.form.get('email')
    new_password = request.form.get('password')

     # if email exists, flash message to say you can't create an account 
     # if it doens't, create new user flash message telling it created successfully

    #user = crud.get_user_by_email(new_email)

    if user:
        flash("Can't create an account with that email. Try again.")
    else: 
        crud.create_user(new_email, new_password)
        flash('Account created. Please log in.')
    
    return redirect('/')

@app.route('/login')
def login():
    """Login page for a user."""

    #users = crud.get_users()
    return render_template('login.html')
#    return render_template('login.html', users=users)


@app.route('/login', methods=['POST'])
def login_user():
    user_email = request.form.get('email')
    user_password = request.form.get('password') 

    #user_id = crud.user_id_if_match(password)
    session['Current User'] = user_id

    flash('Logged in!')
    
    redirect('/<user_id')


@app.route('/<user_id>')
def show_user(user_id):
    """Show users info based on the specified user_id"""

    user = crud.get_user_by_id(user_id)

    return render_template('user_profile.html', user = user) 




if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)
