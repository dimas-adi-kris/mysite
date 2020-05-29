import os
import json

from app import app
from flask import render_template, request, redirect, jsonify, make_response, send_file, send_from_directory, abort, safe_join, url_for, session
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
# from Deployment import predict_bounding_box

from markupsafe import escape



app.config["IMAGE_UPLOADS"] = "/home/isysrg/app/Deployment/Predicting/"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 50 * 1024 * 1024

app.config["SECRET_KEY"] = 'qfLQFMLpUvwRmtBg'


users = {
	"julian": {
		"username": "julian",
		"email": "julian@gmail.com",
		"password": "Xcuy5679-",
		"bio": "Some guy from the internet"
	},
	"clarissa": {
		"username": "clarissa",
		"email": "clarissa@icloud.com",
		"password": "sweetpotato22",
		"bio": "Sweet potato is life"
	}
}


@app.route("/")
@app.route('/index')
def index():
	return render_template("public/index.html")


@app.route("/about")
def about():
	return render_template("public/about/public_templates.html")

@app.route("/get-image/<image_name>") # No converter (defaults to string)
def get_image(image_name):
	print(image_name)
	try:
		return send_from_directory(app.config["IMAGE_UPLOADS"], filename=image_name, as_attachment=True)
	except FileNotFoundError:
		print(app.config["IMAGE_UPLOADS"]+"<-- error 404")
		abort(404)


@app.route("/jinja")
def jinja():
	# Strings
	my_name = "Julian"

	#Integers
	my_age = 20

	#Lists
	langs = ["Python", "Java", "vbnet", "R", "C", "Golang", "javascript"]

	#Dictionaries
	friends = {
		"Tony": 43,
		"Cody": 28,
		"Amy": 26,
		"Clarissa": 23,
		"Wendell": 39,
		"Chris": 31
	}

	#Tuples
	colors = ("Red", "Blue", "yellow")

	#Booleans
	cool = True

	#Classes
	class GitRemote:
		def __init__(self, name, description, domain):
			self.name = name
			self.description = description
			self.domain = domain

		def pull(self):
			return f"Pulling repo '{self.name}'"

		def clone(self, repo):
			return f"Cloning into {repo}"

	my_remote = GitRemote(
		name="Learning Flask",
		description="Learn the Flask web frameword for python",
		domain="https://github.com/Julian-Nash/learning-flask.git"
	)

	#Function
	def repeat(x, qty=1):
		return x * qty
	
	#datetime
	date = datetime.utcnow()

	#HEADING 1
	my_html = "<h1>This is some HTML</h1>"

	#Suspicious
	suspicious = "<script>alert('NEVER TRUST USER INPUT!')</script>"

	return render_template(
            "public/jinja.html", my_name=my_name, my_age=my_age, langs=langs, friends=friends, colors=colors, cool=cool, GitRemote=GitRemote, my_remote=my_remote, repeat=repeat, date=date, my_html=my_html, suspicious=suspicious
        )


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
	if request.method == "POST":
			req = request.form
			print(req)

			missing = list()
			print(missing,"<-- missing = list()")

			for k, v in req.items():
				if v == "":
					missing.append(k)

			if missing:
				feedback = f"Missing fields for {', '.join(missing)}"
				print(feedback)
				return render_template("public/sign_up.html", feedback=feedback)
			return redirect(request.url)
	return render_template("public/sign_up.html")


@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
	hists = os.listdir(app.config["IMAGE_UPLOADS"])
	hists = ['/' + file for file in hists]

	# colorImage_path = app.config["IMAGE_UPLOADS"]+"/002.jpeg"
	# colorImage = Image.open(colorImage_path)

	# print(type(colorImage))

	# transposed = colorImage.transpose(Image.ROTATE_90)
	# print(transposed)
	
	# transposed.save(os.path.join(app.config["IMAGE_UPLOADS"], 'fixed_' + "002.jpg"))

	# fixed_transposed = url_for('static', filename='fixed_'+"002.jpg")

	# colorImage.close()
	# print(hists)
	if request.method == "POST":

		if request.files:

			image = request.files["image"]

			if image.filename == "":

				feedback = "No filename"
				# print(feedback)

				return render_template("public/upload_image.html",hists=hists, feedback=feedback)

			if allowed_image(image.filename):

				if "filesize" in request.cookies:
					if not allowed_image_filesize(request.cookies["filesize"]):
						print("Filesize exceeded maximum limit")
						return redirect(request.url)

				filename = secure_filename(image.filename)
				session['image_name'] = filename
				# session['image_name_path']
				image.save(os.path.join(app.config["IMAGE_UPLOADS"], session.get('image_name')))

				print("image saved with name", session.get('image_name'))

				saved_img = app.config["IMAGE_UPLOADS"] + "/" + session.get('image_name')
				str_saved_img = str(saved_img)

				
				print(str_saved_img)

				return redirect(request.url)
			
			else:
				print("That file extension is not allowed")
				return redirect(request.url)


	# print(hists[0])
	# file_to_predict = hists[0]
	# predict_bounding_box(file_to_predict)

	return render_template("public/upload_image.html", hists=hists, saved_image=session.get('image_name'))


def allowed_image(filename):
	#kita hanya ingin berkas dengan titik(.) di namanya
	if not "." in filename:
		return False

	#pisahkan ekstensi dari nama berkas
	ext = filename.rsplit(".", 1)[1]
	print(ext)

	#periksa apakah ekstensi-nya ada di ALLOWED_IMAGE_EXTENSIONS
	if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
		return True
	else:
		return False

def allowed_image_filesize(filesize):
	if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
		print(int(filesize))
		return True
	else:
		print(int(filesize))
		return False

@app.route("/profile")
def profile():

	if not session.get("USERNAME") is None:
		username = session.get("USERNAME")
		user = users[username]
		return render_template("public/profile.html", user=user)
	else:
		print("No username found in session")
		return redirect(url_for("sign_in"))


@app.route('/sign-in', methods = ['GET', 'POST'])
def sign_in():

	if request.method == 'POST':
		req = request.form
		# session.pop('image_name', None)
		print(session.get("image_name"))
		print(app.config['IMAGE_UPLOADS']+"/"+session.get("image_name"))
		username = req.get("username")
		password = req.get("password")
		print(session)
		if not username in users:
			print(session)
			print("username not found")
			return redirect(request.url)
		else:
			user = users[username]

		if not password == user["password"]:
			print("incorrect password")
			return redirect(request.url)
		else:
			session["USERNAME"] = user["username"]
			print(session)
			print("session username set")
			return redirect(url_for("profile"))
	return render_template("public/sign_in.html")
	
@app.route("/sign-out")
def sign_out():
	session.pop("USERNAME", None)
	return redirect(url_for('sign_in'))