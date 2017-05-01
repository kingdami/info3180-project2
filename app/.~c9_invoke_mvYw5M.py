"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from bs4 import BeautifulSoup
import requests
import urlparse
from models import Person
from models import Wish
import jwt
import time
import base64
from datetime import datetime,timedelta
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders


################################### api routes ##################################
@app.route('/')
def home():
    """Render website's home page."""
    return make_response(open('app/templates/index.html').read())
    
    
def create_token(user):
    payload = {
        'email': user.email_address,
        'password': user.password
        
    }
    token = jwt.encode(payload, app.config['TOKEN_SECRET'])
    return token.decode('unicode_escape')
    
def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, app.config['TOKEN_SECRET'])

@app.route('/api/users/register', methods=['POST'])
def apiregister():
    
    firstname= request.json['firstname']
    lastname= request.json['lastname']
    username= request.json['username']
    password= request.json['password']
    email_address=request.json['email']
    confirm_pass=request.json['confirm-password']
    pword_hint=request.json['hint']
    # if password confirmation matches we commit the new user to the db and cre
    if not firstname.isalpha() or not lastname.isalpha() or not username.isalnum() or not password.isalnum() or not confirm_pass.isalnum() or not pword_hint.isalnum():
        return jsonify({"error":"1","message":'Invalid Inputs'})
    
    # if password confirmation matches we commit the new user to the db and create a token for that new user
    if confirm_pass==password:
        user=  Person(first_name=firstname, last_name=lastname, username=username, password= password, email_address = email_address, pword_hint = pword_hint)
        db.session.add(user)
        db.session.commit()
        token=create_token(user)
        payload = jwt.decode(token,app.config['TOKEN_SECRET'], algorithm=['HS256']) 
        # return jsonify({"error":"null","data":{},"message":'Success'})
        response = jsonify(token=token,information={"error":"null","data":{'token':token,'expires': timeinfo(payload['exp']),'user':{'id':user.id,'email': user.email_address,'firstname':user.first_name,'lastname':user.last_name,'password':user.password,'username':user.username},"message":"Success"}})
    else:
        response= jsonify({"error":"1","message":'Registration failed. Please try again.'})
    
    return response
    
@app.route('/api/users/login', methods=["POST"])
def login():
    """Render the website's login user page."""
    secret= app.config['TOKEN_SECRET']
    
   
    email= request.json['email']
    password= request.json['password']
    
    payload={"email": email,"password": password}
    
    encoded_token=jwt.encode({'logon_info': payload}, secret, algorithm='HS256'
    
        
    
    user = Person.query.filter_by(email_address=email, password=password).first()
    if user is not None:
        login_user(user)
        # Sends back the information along with the token generated
        response = jsonify(information={"error":"null","data":{'user':{'id':user.id,'email': user.email_address,'fname':user.first_name, 'lname': user.last_name, 'Authorization_token':encoded_token},"message":"Success"}})
    else:
        response = jsonify({"error":"1","data":{},"message":'failed'})
        response.status_code = 401
    return response
            

@app.route('/api/users/<userid>/wishlist', methods=["GET","POST"])
@login_required
def apiadd(userid): 
    
    if request.method == "POST":
        new_wish= Wish(wish_url=request.json['url'], user_id=userid , wish_descript=request.json['description'], wish_title=request.json['title'], thumbnail=request.json['image'], added=str(datetime.now()));
        db.session.add(new_wish)
        db.session.commit()
        response = jsonify({"error":"null","data":{},"message":"Success"})
        return response
        
    else:
        user = Person.query.filter_by(id=userid).first()
        userwishes = Wish.query.filter_by(user_id=userid)
        wishlist = []
        for wish in userwishes:
            wishlist.append({'id':wish.wish_id,'title': wish.wish_title,'description':wish.wish_descript,'url':wish.wish_url,'thumbnail':wish.thumbnail, 'added': wish.added})
        if(len(wishlist)>0):
            response = jsonify({"error":"null","data":{"wishes":wishlist}})
        else:
            response = jsonify({"error":"1","data":{}})
        return response



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

@app.route('/api/users/<userid>/wishlist/<itemid>', methods=['POST'])
def deletewish(userid,itemid):
    item_id= request.json['itemid']
    #because based on the db the wish id and the person/userid are always the same 
    deleted_wish= Wish.query.filter_by(user_id=userid,wish_id= itemid).first()
    # use session.delete here instead of add
    db.session.delete(deleted_wish)
    db.session.commit()
    
    response = jsonify({"error":"null","data":{},"message":"Success"})
    return response
        
@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')
    
# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return Person.query.get(int(id))

# ###
# # The functions below should be applicable to all Flask apps.
# ###
@app.route('/share/', methods = ['POST'])
def send_email():
     
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    user= Person.query.filter_by(id=request.json['userid']).first()
    name = user.first_name
    userid= user.id
    
    from_addr = 'info3180wishlistproject@gmail.com' 
    to_addr  = request.json['email'] 
    
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = str(name) + " has shared their wishlist with you"
 
    body = "Member " + str(name) + " from Wishlstproject.com has shared their wishlist with you!!   https://www.google.com/search?q=cats+meme&client=firefox-b&noj=1&source=lnms&tbm=isch&sa=X&ved=0ahUKEwizk8GiyMXTAhWBKiYKHc0NAh0Q_AUICigB&biw=1366&bih=669"
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
    
    response = jsonify({"error":"null", "message":"Success"})
    return response
    
def timeinfo(entry):
    day = time.strftime("%a")
    date = time.strftime("%d")
    if (date <10):
        date = date.lstrip('0')
    month = time.strftime("%b")
    year = time.strftime("%Y")
    return day + ", " + date + " " + month + " " + year

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