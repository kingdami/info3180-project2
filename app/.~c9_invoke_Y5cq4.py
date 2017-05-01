"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from bs4 import BeautifulSoup
import requests
import urlparse
from models import Person
from models import Wish
import jwt
import base64
import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

################################### api routes ##################################
@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/api/users/register', methods=['POST'])
def apiregister():

    firstname= request.form['firstname']
    lastname= request.form['lastname']
    username= request.form['username']
    password= request.form['password']
    email_address=request.form['email']
    confirm_pass=request.form['confirm-password']
    pword_hint=request.form['hint']
    if confirm_pass==password:
        user=  Person(first_name=firstname, last_name=lastname, username=username, password= password, email_address = email_address, pword_hint = pword_hint)
        db.session.add(user)
        db.session.commit()
        flash("Now you may login new Wisher")
        return redirect(url_for('home'))
    else:
        flash("Your password didn't match the confirmmation password")
        return redirect(url_for('home'))
    
    return render_template('home.html')
    
@app.route('/api/users/login', methods=["POST"])
def login():
    """Render the website's login user page."""
    email= request.form['email']
    password= request.form['password']
    user = Person.query.filter_by(email_address=email, password=password).first()
    if user is not None:
        login_user(user)
        session['current_user'] = user.id
        return redirect(url_for('apiadd', userid=user.id))
        
        
    else:
        flash("Your password or email is incorrect")
        return redirect(url_for('home'))
            
            
            
    return render_template("home.html")

@app.route('/api/users/<userid>/wishlist', methods=["GET","POST"])
def apiadd(userid): 
    
    if request.method == "POST":
        new_wish= Wish(wish_name_url=request.json['url'], wish_id=session['current_user'] , wish_descript=request.json['description'], title=request.json['title'], thumbnail=request.json['image']);
        db.session.add(new_wish)
        db.session.commit()
        return redirect(url_for('wishers_page'))
        
    else:
        user = Person.query.filter_by(id=session['current_user']).first()
        userwishes = Wish.query.filter_by(wish_id=userid)
        return render_template('wishers_page.html',loggedUser=user, wishes=userwishes)
        #return userwishes


@app.route('/api/thumbnails', methods=['POST'])
def thumbnail():
    url = request.json['url']
    imagelist = get_images(url)
    for each in imagelist:
        if not each.lower().endswith(('.png', '.jpg', '.jpeg')):
            imagelist.remove(each) 
    imagelist= list(set(imagelist));
    output = jsonify(thumbnails= imagelist)
    return output
    
def get_images(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.text, "html.parser")
    imgs=[]
    image = "%s"
    
    for img in soup.findAll("img", src=True):
       link = image % urlparse.urljoin(url, img["src"])
       imgs+=[link]
    return imgs

@app.route('/api/users/{userid}/wishlist/{itemid}', methods=['DELETE'])
def deletewish(userid,itemid):
    item_id= request.json['itemid']
    #because based on the db the wish id and the person/userid are always the same 
    deleted_wish= Wish.query.filter_by(wish_id=session['current_user'],id= item_id)
    # use session.delete here instead of add
    db.session.delete(deleted_wish)
    db.session.commit()
    return redirect(url_for('wishers_page'))
        
@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')
    
@app.route('/wishers_page/')
@login_required
def wishers_page():
    """Render the  wishers page on our website that only logged in users can access."""
    
    return render_template('wishers_page.html')
    
# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return Person.query.get(int(id))

###
# The functions below should be applicable to all Flask apps.
###
@app.route('/share/', methods = ['POST'])
def send_email():
     
    
    user= Person.query.filter_by(id=session['current_user']).first()
    name = user.first_name
    userid= user.id
    
    from_addr = 'info3180wishlistproject@gmail.com' 
    to_addr  = request.json['email'] 
    
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = str(name) + " has shared his/her wishlist with you"
 
    body = "Member " + str(name) + " from Wishlstproject.com has shared his/her wishlist with you!!   https://www.google.com/search?q=cats+meme&client=firefox-b&noj=1&source=lnms&tbm=isch&sa=X&ved=0ahUKEwizk8GiyMXTAhWBKiYKHc0NAh0Q_AUICigB&biw=1366&bih=669"
    msg.attach(MIMEText(body, 'plain'))
    
    
    
    #from_name = 'wishlistproject'
    #to_name = request.json['name']
    #subject =  'Someone has shared their wishlist with you'
    ### message = 'Member '+ username + 'from Wishlstproject.com has shared his/her wishlist with you!! /n http://info3180-project2-shadain94.c9users.io/api/users/' + userid + '/wishlist'
    #message = "test"
    #message_to_send = message.format(from_name, from_addr, to_name, to_addr, subject, message) 
    # Credentials (if needed) 
    username = 'info3180wishlistproject@gmail.com' 
    password = 'qgxkbzahmbrikzja' 
    # The actual mail send 
    server = smtplib.SMTP('smtp.gmail.com:587') 
    server.ehlo()
    server.starttls() 
    server.login(username, password) 
    text = msg.as_string()
    server.sendmail(from_addr, to_addr, text) 
    server.quit() 
    return

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