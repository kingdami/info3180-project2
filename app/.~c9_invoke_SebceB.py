"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from bs4 import BeautifulSoup
import requests
import urlparse
from models import WishersInfo

################################### api routes ##################################
@app.route('/api/users/register', methods=["POST"])
def apiregister():
    #save registration details to database
    firstname= request.js["firstName"]
    lastname= request.json["lastName"]
    username= request.json["userName"]
    password= request.json["password"]
    email_address=request.json["email"]
    pword_hint=request.json["hint"]
    message =""
    m = {message: "it worked"}
    
    user=  WishersInfo(first_name=firstname, last_name=lastname, username=username, password= password, email_address = email_address, pword_hint = pword_hint)
    db.session.add(user)
    db.session.commit()
    
    
    return jsonify(m);

@app.route('/api/users/login', methods=["POST"])
def apilogin():
    # log user in
    return # json status message success or failure

@app.route('/api/users/{userid}/wishlist', methods=["POST"])
def apiadd(userid):
    # add items to users wish list
    return # json status message success or failure

@app.route('/api/users/{userid}/wishlist', methods=["GET"])
def apiwishlist(userid):
    # get users wishlist from database
    return #json wishlist

@app.route('/api/thumbnails', methods=["GET"])
def apithumbnails():
    #scrape url for images
    return # json containg list of image urls

@app.route('/api/users/{userid}/wishlist/{itemid}', methods=["DELETE"])
def apiremove(userid,itemid):
    # delete item from users wishlish
    return # json status message success or failure

################################## app routes ##########################



###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')
    
@app.route('/api/users/register', methods=["POST"])
def add_user():
    
    """Render the website's add user page."""
    if request.method == 'POST':
        firstname= request.form['firstname']
        lastname= request.form['lastname']
        username= request.form['username']
        email=request.form['email']
        p_hint=request.form['hint']
        password= hash(request.form['password']+str("i am a not so secret salt"))
        user= WishersInfo(first_name=firstname, last_name=lastname, username=username, password= password, email_address=email, pword_hint=p_hint)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created successfully.','success')
        return redirect(url_for("wishers_page"))
    
    
    return render_template('home.html')
    
    
@app.route('/api/users/login', methods=["POST"])
def login():
    """Render the website's login user page."""
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        user = WishersInfo.query.filter_by(email_address=email, password=password).first()
        if user is not None:
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for("wishers_page"))
        else:
            flash('Email or Password is incorrect.', 'danger')
            
            
            
    return render_template("home.html")
            
        
    
    
    
@app.route('/wishers_page/')
@login_required
def wishers_page():
    """Render the  wishers page on our website that only logged in users can access."""
    return render_template('wishers_page.html')
    


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))

###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")