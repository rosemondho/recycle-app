
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
    


# Nearest Recyclers: Show all of them
# Each title of recyclers make into a link
# @app.route('/nearest_recyclers')
# def nearest_recyclers(recyclers):
#     """View nearest recyclers"""    
#     print("entered nearest_recyclers route")
#     return render_template('nearest_recyclers.html', recyclers=recyclers)

# make a dedicated route for handling to favorite a recycler
# set it up like setting up details page
# pulling user_id from session to populate info 
# have a text box in form where to submit
# app.route: def make_favorite(location_id): [action of favoriting]
# /makefavorite
# app.route: def favorites_page(): [actual favorited page]
# submit form, get details from form, call crud, redirect location details
@app.route("/add_to_favorites/<recycler_id>")
def add_to_favorites(recycler_id):
    """Add a melon to cart and redirect to shopping cart page.

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
    session.setdefault("cart",{})
    melon_id_count = session["cart"]    # {melon_id: count}
    melon = melons.get_by_id(melon_id).common_name
    flash(f"{melon} was successfully added to cart.")
    melon_id_count[melon_id] = melon_id_count.get(melon_id, 0) + 1
    print(melon_id_count)
    return redirect("/cart")

# @app.route('/makefavorite')
# def make_favorite():
#     """Show details of a particular recycler"""

#     recycler = crud.get_recycler_by_id(recycler_id)

#     return render_template('recycler_details.html', recyclers = recyclers)

@app.route("/favorites")
def show_favorite_recyclers():
    """Display content of shopping cart."""

    # TODO: Display the contents of the shopping cart.

    # The logic here will be something like:
    #
    # - get the cart dictionary from the session
    # - create a list to hold melon objects and a variable to hold the total
    #   cost of the order
    # - loop over the cart dictionary, and for each melon id:
    #    - get the corresponding Melon object
    #    - compute the total cost for that type of melon
    #    - add this to the order total
    #    - add quantity and total cost as attributes on the Melon object
    #    - add the Melon object to the list created above
    # - pass the total order cost and the list of Melon objects to the template
    #
    # Make sure your function can also handle the case wherein no cart has
    # been added to the session
    fav_recycler = session["favorites"]
    melon_list = []
    cart_sum = 0
    for melon_id in melon_id_count:
        print("number of melons: " + str(melon_id_count[melon_id]))
        melon_obj = melons.get_by_id(melon_id)
        melon_obj.quantity = melon_id_count[melon_id]
        print("quantity * price per melon: " + melon_obj.total())
        total = melon_obj.total_cost
        melon_list.append(melon_obj)
        cart_sum = cart_sum + total

    cart_sum = "${:.2f}".format(cart_sum)
    print(melon_list[0].common_name)
    print(cart_sum)
    print(melon_list)
    return render_template("cart.html", 
                            cart=melon_list, 
                            cart_sum=cart_sum, 
                            )

@app.route('/recycler/<location_id>')
def show_recycler(location_id):
    """Show details of a particular recycler"""
    # interact with API to call more details
    # recycler = crud.get_recycler_by_id(location_id)

    return render_template('recycler_details.html', recycler=recycler)


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
