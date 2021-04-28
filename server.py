
"""Server for recyclers app."""

from flask import Flask, render_template, request, flash, session, redirect, url_for
from model import connect_to_db
from pprint import pformat
from urllib.parse import urlencode
import os
import requests
import json
import crud
import materials

#this throws errors when a variable is undefined, otherwise no error
from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"

API_KEY = os.environ['EARTH911_KEY']

app.jinja_env.undefined = StrictUndefined

 
@app.route('/')
def homepage():
    """View homepage"""

    materials_list = materials.get_materials()
    
    return render_template('homepage.html', materials=materials_list)


@app.route('/search', methods=['GET'])
def search_for_recyclers():
    """Search for recycler in area."""

    chosen_material_id = []  

    materials_list = materials.get_materials()  # list of dictionaries    
    postalcode = request.args.get('zipcode')
    maxdistance = request.args.get('radius')
    chosen_materials = request.args.getlist('material_item')
    num_results = request.args.get('num_results')
    print('MATERIAL(S) CHOSEN: ', chosen_materials)
    print('material TYPE: ', type(chosen_materials))


    # Links material description to material ID. var material is a Type<'str>
    for material in chosen_materials: 
        # loop through 
        for material_dict in materials_list:
            if material == material_dict['description']:
                chosen_material_id.append(material_dict['material_id'])
                break 
    
    print('CHOSEN MATERIAL-IDS: ', chosen_material_id)
            
    url = f'http://api.earth911.com/earth911.getPostalData'
    payload = {'api_key': API_KEY,
               'country': 'US',
               'postal_code': postalcode}

    response = requests.get(url, params=payload)
    data = response.json()

    if 'error' in data:
        flash(f'{postalcode} is not a valid postal code. Please try again.')
        return redirect('/')

    latitude = data['result']['latitude']
    longitude = data['result']['longitude']
    
    location_url = f'http://api.earth911.com/earth911.searchLocations'
    
    if chosen_materials:
        payload = {'api_key': API_KEY,
                'latitude': latitude,
                'longitude': longitude,
                'material_id': chosen_material_id,
                'max_distance': maxdistance,
                'max_results': num_results}
    elif not chosen_materials:
       payload = {'api_key': API_KEY,
                'latitude': latitude,
                'longitude': longitude,
                'max_distance': maxdistance,
                'max_results': num_results}

    response = requests.get(location_url, params=payload)
    final_data = response.json()
    # print(final_data)
    recyclers = final_data['result']    # entire list of locations
    
    # Get address from location
    loc_ids = []
    locdetails_url = f'http://api.earth911.com/earth911.getLocationDetails'
    for recycler in recyclers:
        loc_ids.append(recycler['location_id'])
    print('TYPE loc_ids: ', type(loc_ids))
    print("LOCATION IDs: ", loc_ids)

    if loc_ids == []:
        flash('0 recyclers matched your search.')
        redirect('/')

    payload = {'api_key': API_KEY,
                'location_id[]': loc_ids}

    response = requests.get(locdetails_url, params=payload)
    loc_details = response.json()
    loc_details = loc_details['result']
    # print('LOC_DETAILS:', loc_details)
    
    return render_template('nearest_recyclers.html',
                            pformat=pformat,
                            data=final_data,
                            recyclers=recyclers,
                            loc_details=loc_details)
    

@app.route('/recycler/<location_id>')
def show_recycler(location_id):
    """Show details of a particular recycler"""
    
    is_favorited = []
    
    locdetails_url = f'http://api.earth911.com/earth911.getLocationDetails'
    # print("LOCATION ID: ", location_id)
    payload = {'api_key': API_KEY,
                'location_id[]': location_id}
    response = requests.get(locdetails_url, params=payload)
    loc_detail = response.json()
    recycler = loc_detail['result'][location_id]
    materials = recycler['materials'] 
    # print('Recycler:', recycler)
    # print('Accepted Materials:', materials) 

    if 'Current User' in session:
        is_favorited = crud.is_recycler_favorited(location_id,
                                                  session['Current User'])

    comments = crud.get_recycler_comments(location_id)

    print("ALL COMMENTS: ", comments)

    return render_template('recycler_details.html',
                           recycler=recycler,
                           materials=materials,
                           location_id=location_id,
                           comments=comments,
                           is_favorited=is_favorited)


@app.route('/recycler/<location_id>', methods=['POST'])
def submit_comment(location_id):
    """Get comment from user."""

    user_id = session['Current User']
    print('USER ID: ', session['Current User'])
    print("USER ID TYPE: ", type(user_id))
    comment = request.form.get('comment')
    print("LOCATION ID: ", location_id)
    name = crud.get_user_by_id(user_id).name
    print(name)
    crud.create_comment(user_id, name, location_id, comment)

    flash('Comment submitted.')
    return redirect(f'/recycler/{location_id}')


@app.route("/add_to_favorites/<location_id>", methods=['POST'])
def add_to_favorites(location_id):
    """Add a recycler to favorites and redirect to Favorites page."""

    user_id = session['Current User']

    # Get name of recycler from API
    locdetails_url = f'http://api.earth911.com/earth911.getLocationDetails'
    payload = {'api_key': API_KEY,
              'location_id[]': location_id}
    response = requests.get(locdetails_url, params=payload)
    loc_details = response.json()
    # print("Location Details: ", loc_details)
    recycler_name = loc_details['result'][location_id]['description']

    # Add the recycler to Favorites database
    crud.fav_a_recycler(user_id, location_id)
    flash(f"{recycler_name} was successfully added to Favorites.")
    return redirect(f'/recycler/{location_id}')


@app.route("/favorites")
def show_favorite_recyclers():
    """Display list of favorited recyclers."""

    loc_details=''
    favorites = crud.get_favorited_recyclers(session['Current User'])

    if favorites:
        print("FAVORITES: ", favorites)
        loc_ids = []

        url = f'http://api.earth911.com/earth911.getLocationDetails'
        
        #loop through the favorited recyclers and add them
        for favorite in favorites:
            loc_ids.append(favorite.location_id)
        
        print("LOCATION IDs FROM FAVORITES: ", loc_ids)
        payload = {'api_key': API_KEY,
                'location_id[]': loc_ids}

        response = requests.get(url, params=payload)
        loc_details = response.json()
        loc_details = loc_details['result']
        # print("FAVORITES Location Details: ", loc_details)

    return render_template("favorites.html", 
                            favorites=favorites,
                            loc_details=loc_details)


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

    user = crud.get_user_by_email(new_email)

    if user:
        flash("Can't create an account with that email. Try again.")
    else: 
        crud.create_user(new_name, new_email, new_password)
        flash('Account created. Please log in.')
    
    return redirect('/login')

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
    
    if user_id is not None:
        flash('Logged in!')
        return redirect(f'/user/{user_id}')
    else:
        flash("Email or password incorrect. Try again.")
        return redirect('/login')


@app.route('/user/<user_id>')
def show_user(user_id):
    """Show users info based on the specified user_id"""

    print('user_id Type: ', type(user_id))
    print('user_id: ', user_id)
    user = crud.get_user_by_id(int(user_id))

    print("USER TYPE: ", user)
    return render_template('user_profile.html', user=user)
    

@app.route('/logout')
def logout_user():
    """Logs out user."""
    if 'Current User' in session:    
        session.pop('Current User', None)
        flash("Successfully logged out.")
    else:
       session.clear()
       flash("You are not logged in.") 

    return redirect('/')




if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)
