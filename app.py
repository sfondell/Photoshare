######################################
# Sophia Fondell
# CS 460 - PA 1 - Photosharing App
# 11/10/18
######################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
#import flask.ext.login as flask_login
import flask_login
#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cs460password' #CHANGE THIS TO YOUR MYSQL PASSWORD
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
		<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register/", methods=['GET'])
def register():
	return render_template('register.html', supress='True')  

@app.route("/register/", methods=['POST'])
def register_user():
	try:
		# We only want to get necessary tokens here so that try/except is passed
		# if non-required information isn't entered
		fname = request.form.get('fname')
		lname = request.form.get('lname')
		email = request.form.get('email')
		password = request.form.get('password')
		dob = request.form.get('dob')
	except:
		print "Couldn't find all required values for registration" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		# Get the rest of the tokens from the form
		gender = request.form.get('gender')
		# If no gender was entered we want to make sure it's stored as NULL
		if (gender == None):
			gender = 'NULL'
		hometown = request.form.get('hometown')
		# If no hometown entered, store as NULL
		if (hometown == ''):
			hometown = 'NULL'
		profpic = request.files['profpic']
		# If no profile picture entered
		if (request.files['profpic'].filename == ''):
			profpic = 'NULL'
		else:
			profpic = base64.standard_b64encode(profpic.read())
		print cursor.execute("INSERT INTO Users (gender, fname, lname, email, dob, password, profpic, hometown) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')".format(gender, fname, lname, email, dob, password, profpic, hometown))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return flask.redirect(flask.url_for('protected'))
	else:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(userid):
	cursor = conn.cursor()
	cursor.execute("SELECT photoid, data, caption FROM Photos WHERE userid = '{0}'".format(userid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT userid FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

# Backend Helper Functions

def getUsersAlbums(userid):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Albums WHERE userid = '{0}'".format(userid))
	return cursor.fetchall()

def getUsersNamefromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT fname, lname FROM Users WHERE email = '{0}'".format(email))
	nametup = cursor.fetchone()
	namestr = nametup[0] + ' ' + nametup[1]
	return namestr

def getPhotosFromAlbum(albumid):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Photos WHERE albumid = '{0}'".format(albumid))
	return cursor.fetchall()

def getNamefromAlbumid(albumid):
	cursor = conn.cursor()
	cursor.execute("SELECT name FROM Albums WHERE albumid = '{0}'".format(albumid))
	return cursor.fetchone()[0]

def getProfilePicture(email):
	cursor = conn.cursor()
	cursor.execute("SELECT profpic FROM Users WHERE email = '{0}'".format(email))
	result = cursor.fetchone()[0]
	if (result == None):
		with open("static/default.jpg", "rb") as img:
			return base64.standard_b64encode(img.read())
	else:
		return result

def getBio(email):
	cursor = conn.cursor()
	cursor.execute("SELECT bio FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def searchByEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT userid, fname, lname, email FROM Users WHERE email LIKE '{0}'".format(email))
	return cursor.fetchall()

def searchByName(fname):
	cursor = conn.cursor()
	cursor.execute("SELECT userid, fname, lname, email FROM Users WHERE fname LIKE '{0}'".format(fname))
	return cursor.fetchall()

def getUsers():
	cursor = conn.cursor()
	cursor.execute("SELECT userid, fname, lname, email FROM Users")
	return cursor.fetchall()

def getGender(email):
	cursor = conn.cursor()
	cursor.execute("SELECT gender FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getHometown(email):
	cursor = conn.cursor()
	cursor.execute("SELECT hometown FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getfname(email):
	cursor = conn.cursor()
	cursor.execute("SELECT fname FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getlname(email):
	cursor = conn.cursor()
	cursor.execute("SELECT lname FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getEmailFromUserid(userid):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE userid = '{0}'".format(userid))
	return cursor.fetchone()[0]

def getNumLikes(photoid):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(photoid) FROM Likes WHERE photoid = '{0}".format(photoid))
	return cursor.fetchone()[0]

# Returns a list of userids and corresponding emails of all users who have liked a specified photo
def getLikesUsers(photoid):
	cursor = conn.cursor()
	cursor.execute("SELECT Likes.userid, Users.email FROM Likes INNER JOIN Users ON Likes.userid = Users.userid WHERE Likes.photoid = '{0}'".format(photoid))
	return cursor.fetchall()

def getUseridFromAlbumid(albumid):
	cursor = conn.cursor()
	cursor.execute("SELECT userid FROM Albums WHERE albumid = '{0}'".format(albumid))
	return cursor.fetchone()[0]

def getUsersNameFromUserid(userid):
	cursor = conn.cursor()
	cursor.execute("SELECT fname, lname FROM Users WHERE userid = '{0}'".format(userid))
	nametup = cursor.fetchone()
	namestr = nametup[0] + ' ' + nametup[1]
	return namestr

# Does nothing if the user has already liked the photo
def addLike(userid, photoid):
	cursor = conn.cursor()
	cursor.execute("SELECT photoid FROM Likes WHERE userid = '{0}'".format(userid))
	likedphotos = cursor.fetchall()
	if (photoid not in likedphotos):
		cursor.execute("INSERT INTO Likes (userid, photoid) VALUES ('{0}', '{1}')".format(userid, photoid))
		conn.commit()

def deleteAlbum(albumid):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Albums WHERE albumid = '{0}'".format(albumid))
	conn.commit()

def deletePhoto(photoid):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Photos WHERE photoid = '{0}'".format(photoid))
	conn.commit()

def getComments(photoid):
	cursor = conn.cursor()
	cursor.execute("SELECT Comments.commentid, Comments.userid, Comments.commenttext, Comments.posttime, Users.email FROM Comments INNER JOIN Users ON Comments.userid = Users.userid WHERE Comments.photoid = '{0}'".format(photoid))
	return cursor.fetchall()

def addComment(userid, photoid, albumid, commenttext):
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Comments (photoid, albumid, userid, commenttext) VALUES ('{0}', '{1}', '{2}', '{3}')".format(photoid, albumid, userid, commenttext))
	conn.commit()

def getTags(photoid):
	cursor = conn.cursor()
	cursor.execute("SELECT tag FROM Tags WHERE photoid = '{0}'".format(photoid))
	tags = cursor.fetchall()
	return [list(i)[0] for i in tags]

def getPhotoData(photoid):
	cursor = conn.cursor()
	cursor.execute("SELECT data FROM Photos WHERE photoid = '{0}'".format(photoid))
	return cursor.fetchone()[0]

def addTag(tag, photoid):
	cursor = conn.cursor()
	cursor.execute("SELECT photoid FROM tags WHERE tag = '{0}'".format(tag))
	results = cursor.fetchall()
	if (photoid not in results):
		cursor.execute("INSERT INTO Tags (tag, photoid) VALUES ('{0}', '{1}')".format(tag, photoid))
		conn.commit()

def deleteTag(tag, photoid):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Tags WHERE (tag = '{0}') AND (photoid = '{1}')".format(tag, photoid))
	conn.commit()

def getAlbumidFromPhotoid(photoid):
	cursor = conn.cursor()
	cursor.execute("SELECT albumid FROM Photos WHERE photoid = '{0}'".format(photoid))
	return cursor.fetchone()[0]

# Returns a list of lists for each photo in the album
# Each list contains [photoid, albumid, userid, data, caption, number of likes, [List of users that have liked the photo], [List of lists of comments & comment info]]
def concatAlbumInfo(albumid):
	photos = getPhotosFromAlbum(albumid)
	# Cast tuple of tuples to list of lists
	photoslst = [list(i) for i in photos]
	# Iterate through list of lists and add number of likes and users that liked each photo
	# So that aggregated information can be passed into render_template()
	for pic in photoslst:
		likes = getLikesUsers(pic[0])
		likes = [list(x) for x in likes]
		comments = getComments(pic[0])
		comments = [list(y) for y in comments]
		cursor.execute("SELECT tag FROM Tags WHERE photoid = '{0}'".format(pic[0]))
		tags = cursor.fetchall()
		tags = [list(z)[0] for z in tags]
		pic.append(len(likes))
		pic.append(likes)
		pic.append(comments)
		pic.append(tags)
	return photoslst

###################################

# VIEWING OWN PROFILE
@app.route('/profile')
@flask_login.login_required
def protected():
	# Pass in profile picture if user has set one, if not pass in default
	profpic = getProfilePicture(flask_login.current_user.id)
	bio = getBio(flask_login.current_user.id)
	gender = getGender(flask_login.current_user.id)
	hometown = getHometown(flask_login.current_user.id)
	return render_template('hello.html', loggedin=True, profpic=profpic, bio=bio, gender=gender, hometown=hometown, name=getUsersNamefromEmail(flask_login.current_user.id), message="Your profile")

@app.route('/edit', methods=['GET', 'POST'])
@flask_login.login_required
def edit_profile():
	if request.method == 'POST':
		userid = getUserIdFromEmail(flask_login.current_user.id)
		bio = request.form.get('bio')
		# If an empty string we assume change or leaving bio empty
		if (bio == ''):
			bio = 'NULL'
		profpic = request.files['profpic']
		# No new profile pic specified so we don't want to change it
		if (request.files['profpic'].filename == ''):
			# Update in backend
			cursor = conn.cursor()
			cursor.execute("UPDATE Users SET bio = '{0}' WHERE email = '{1}'".format(bio, flask_login.current_user.id))
			conn.commit()
		# New profile picture specified
		else:
			profpic = base64.standard_b64encode(profpic.read())
			# Update in backend
			cursor = conn.cursor()
			cursor.execute("UPDATE Users SET bio = '{0}', profpic = '{1}' WHERE email = '{2}'".format(bio, profpic, flask_login.current_user.id))
			conn.commit()
		return flask.redirect(flask.url_for('protected'))
	# Method is GET so we display form to update profile
	else:
		bio = getBio(flask_login.current_user.id)
		return render_template('edit.html', bio=bio)

@app.route('/edittags', methods=['POST'])
@flask_login.login_required
def edit_tags():
	dtags = request.form.getlist('dtag')
	print(dtags)
	ntags = request.form.get('newtags')
	print(ntags)
	photoid = request.form.get('photoid')

	if (len(dtags) > 0):
		for i in dtags:
			deleteTag(i[0], photoid)

	if (len(ntags) > 0):
		ntagslst = ntags.split(',')
		for i in ntagslst:
			addTag(i, photoid)

	own = getUserIdFromEmail(flask_login.current_user.id)
	albumid = getAlbumidFromPhotoid(photoid)
	albumName = getNamefromAlbumid(albumid)
	photos = concatAlbumInfo(albumid)
	user = getUsersNameFromUserid(own)
	return render_template('pictures.html', own=own, albumName=albumName, user=user, photos=photos, loggedin=True, curruser=own)

# Display all of a user's own photos by album
@app.route('/albums')
@flask_login.login_required
def displayalbums():
	albums = getUsersAlbums(getUserIdFromEmail(flask_login.current_user.id))
	return render_template('albums.html', albums=albums)

@app.route("/<albumid>/pictures/", methods=['GET', 'POST'])
def show_pics(albumid):
	# A user has liked or commented on the picture so we want to react accordingly
	# For now just handles likes
	if request.method == 'POST':
		# If a user liked a post
		if (request.form.get('action') == 'like'):
			userid = request.form.get('curruser')
			photoid = request.form.get('photoid')
			addLike(userid, photoid)
			# Show updated page after action
			albumName = getNamefromAlbumid(albumid)
			user = getUsersNameFromUserid(getUseridFromAlbumid(albumid))
			own = getUseridFromAlbumid(albumid)
			photos = concatAlbumInfo(albumid)
			return render_template('pictures.html', own=own, albumName=albumName, user=user, photos=photos, loggedin=True, curruser=userid)
		# If a user deleted their own album
		elif (request.form.get('action') == 'deletealbum'):
			deleteAlbum(albumid)
			albums = getUsersAlbums(getUserIdFromEmail(flask_login.current_user.id))
			# Back to albums because we have deleted an entire album
			return render_template('albums.html', albums=albums)
		# If a user deleted their own photo
		elif (request.form.get('action') == 'deletephoto'):
			photoid = request.form.get('photoid')
			deletePhoto(photoid)
			# Show updated page after action
			userid = getUserIdFromEmail(flask_login.current_user.id)
			albumName = getNamefromAlbumid(albumid)
			user = getUsersNameFromUserid(getUseridFromAlbumid(albumid))
			own = getUseridFromAlbumid(albumid)
			photos = concatAlbumInfo(albumid)
			return render_template('pictures.html', own=own, albumName=albumName, user=user, photos=photos, loggedin=True, curruser=userid)
		elif (request.form.get('action') == 'comment'):
			userid = request.form.get('curruser')
			photoid = request.form.get('photoid')
			albumid = request.form.get('albumid')
			commenttext = request.form.get('commenttext')
			addComment(userid, photoid, albumid, commenttext)
			# Show updated page after action
			albumName = getNamefromAlbumid(albumid)
			user = getUsersNameFromUserid(getUseridFromAlbumid(albumid))
			own = getUseridFromAlbumid(albumid)
			photos = concatAlbumInfo(albumid)
			if not flask_login.current_user.is_authenticated:
				loggedin = False
				userid = 100
			else:
				loggedin = True
				userid = getUserIdFromEmail(flask_login.current_user.id)
			return render_template('pictures.html', own=own, albumName=albumName, user=user, photos=photos, loggedin=loggedin, curruser=userid)
		elif (request.form.get('action') == 'edittags'):
			photoid = request.form.get('photoid')
			tags = getTags(photoid)
			data = getPhotoData(photoid)
			return render_template('edittags.html', photoid=photoid, tags=tags, data=data)
	else:
		# We only wanna display certain things if the user is logged in
		if flask_login.current_user.is_authenticated:
			curruser = getUserIdFromEmail(flask_login.current_user.id)
			albumName = getNamefromAlbumid(albumid)
			user = getUsersNameFromUserid(getUseridFromAlbumid(albumid))
			own = getUseridFromAlbumid(albumid)
			photos = concatAlbumInfo(albumid)
			return render_template('pictures.html', own=own, albumName=albumName, user=user, photos=photos, loggedin=True, curruser=curruser)
		# If user is not logged in there's certain things we don't wanna display
		else:
			albumName = getNamefromAlbumid(albumid)
			user = getUsersNameFromUserid(getUseridFromAlbumid(albumid))
			photos = concatAlbumInfo(albumid)
			own = getUseridFromAlbumid(albumid)
			return render_template('pictures.html', own=own, albumName=albumName, user=user, photos=photos, loggedin=False, curruser=100)

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		userid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		albumid = request.form.get('album')
		photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Photos (albumid, userid, data, caption) VALUES ('{0}', '{1}', '{2}' , '{3}')".format(albumid, userid, photo_data, caption))
		conn.commit()
		return flask.redirect(flask.url_for('protected'))
	#The method is GET so we return a HTML form to upload the a photo.
	else:
		albums = getUsersAlbums(getUserIdFromEmail(flask_login.current_user.id))
		print(albums)
		return render_template('upload.html', albums=albums)
#end photo uploading code 

@app.route('/new_album', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
	if request.method == 'POST':
		userid = getUserIdFromEmail(flask_login.current_user.id)
		name = request.form.get('name')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Albums (userid, creation, name) VALUES ('{0}', CURDATE(), '{1}')".format(userid, name))
		conn.commit()
		return flask.redirect(flask.url_for('protected'))
	# The method is GET so we wanna display the form for creating a new album
	else:
		return render_template('new_album.html')

@app.route('/browseusers', methods=['GET', 'POST'])
def browse_users():
	# Handle search query
	if request.method == 'POST':
		querytype = request.form.get('querytype')
		query = request.form.get('query')
		if (querytype == 'Email'):
			results = searchByEmail(query)
		else:
			results = searchByName(query)
		return render_template('queryresults.html', query=query, results=results)
	# The method is GET so we wanna display all users and the query form
	else:
		users = getUsers()
		return render_template('browseusers.html', users=users)

# Display another user's profile
@app.route('/<userid>/usrprofile')
def display_profile(userid):
	if flask_login.current_user.is_authenticated:
		# User is trying to view their own profile so we wanna display the appropriate page
		if (userid == getUserIdFromEmail(flask_login.current_user.id)):
			return flask.redirect(flask.url_for('protected'))
		# User is trying to view someone else's profile
		else:
			email = getEmailFromUserid(userid)
			fname = getfname(email)
			lname = getlname(email)
			bio = getBio(email)
			gender = getGender(email)
			hometown = getHometown(email)
			profpic = getProfilePicture(email)
			return render_template('usrprofile.html', userid=userid, fname=fname, lname=lname, bio=bio, gender=gender, hometown=hometown, profpic=profpic)
	# User is trying to view someone else's profile
	else:
		email = getEmailFromUserid(userid)
		fname = getfname(email)
		lname = getlname(email)
		bio = getBio(email)
		gender = getGender(email)
		hometown = getHometown(email)
		profpic = getProfilePicture(email)
		return render_template('usrprofile.html', userid=userid, fname=fname, lname=lname, bio=bio, gender=gender, hometown=hometown, profpic=profpic)

# Display another user's albums
@app.route('/<userid>/<userid1>/usralbums')
def display_useralbums(userid, userid1):
	if flask_login.current_user.is_authenticated:
		# User is trying to view their own albums so we wanna redirect to logged in user's album
		# I don't think you should be able get to this link anyways but just in case
		if (userid == getUserIdFromEmail(flask_login.current_user.id)):
			return flask.redirect(flask.url_for('displayalbums'))
		# Get album information and pass to html rendering
		else:
			email = getEmailFromUserid(userid)
			name = getUsersNamefromEmail(email)
			albums = getUsersAlbums(userid)
			return render_template('usralbums.html', name=name, albums=albums)
	# Get album information and pass to html rendering
	else:
		email = getEmailFromUserid(userid)
		name = getUsersNamefromEmail(email)
		albums = getUsersAlbums(userid)
		return render_template('usralbums.html', name=name, albums=albums)



#default home page  
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
