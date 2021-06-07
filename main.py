# Use this code to launch the app in local development: 
# set FLASK_APP=main.py 
# set FLASK_ENV=development this turns on debug mode that updates the server instance each time the code is updated
# flask run or python -m flask run
# To launch the web app:
# gcloud app deploy app.yaml
# [START app]
import os
from flask import Flask, render_template,redirect, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
from process_image import process_image
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import google.cloud.logging
client = google.cloud.logging.Client()
import json
client.get_default_handler()
client.setup_logging()

VERIFY_URL = "https://hcaptcha.com/siteverify"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__, instance_relative_config=True)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"]
)
models = ["unet", "unetpp"]
WEB_APP = False
if WEB_APP:
    app.config.from_pyfile("configWebApp.py")
else:
    app.config.from_pyfile("config.py")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/tmp/<filename>')
@limiter.exempt
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/", methods=['GET', 'POST'])
def startingpoint():
    fileError = ""
    scroll = ""
    if request.method =="POST":
        if not app.config['RECAPTCHA_ENABLED'] or verify() :
            if 'file' not in request.files:
                fileError = "Please upload a file before hitting Submit"
                scroll = "Live-App"
            file = request.files['file']
            if file.filename == '':
                fileError = "Please upload a file before hitting Submit"
                scroll = "Live-App"
            if not allowed_file(file.filename):
                fileError = "Please upload a file with only one of the allowed types (.png, .jpg, .jpeg, .gif)"
                scroll = "Live-App"    
            if file and allowed_file(file.filename):
                model = request.form["model"]
                filename = secure_filename(file.filename)
                file.save(app.config['UPLOAD_FOLDER'] + "/" +filename)
                return redirect(url_for('processed',
                                      model=model, filename=filename))
        else:
            fileError = "There was a problem with the captcha, please try again"
            scroll = "Live-App"

    return render_template("basetemplate.html", error = fileError,  scroll=scroll)

@app.route('/processed/<model>/<filename>', methods=['GET', 'POST'])
def processed(model, filename):
    processedFilename = process_image(app.config['UPLOAD_FOLDER'], filename, model)
    return render_template("Results.html", processed = processedFilename, unprocessed = filename, scroll="Live-App")   

def verify():
    data = {
        "secret": app.config['RECAPTCHA_SECRET_KEY'],
        "response": request.form.get('h-captcha-response'),
        "remoteip": request.environ.get('REMOTE_ADDR')
    }
    r = requests.post(VERIFY_URL, data=data)
    logging.info("This is the responce from hcaptcha: "+str(r))
    logging.info("This is the json: "+ str(r.json()))
    return r.json()["success"] if r.status_code == 200 else False

@app.route('/API', methods=['POST'])
@limiter.limit("40/day;10/hour")
def API():
    print(json.loads(request.form["json"])["model"])
    if 'file' not in request.files:
        data= {"error": "No File Sent"}
        return data, 405
    file = request.files['file']
    if file.filename == '':
        data= {"error": "filename parameter blank"}
        return data, 406
    if not allowed_file(file.filename):
        data= {"error": "File Type Not Allowed"}
        return data, 406
    if 'json' not in request.form or json.loads(request.form["json"])["model"] not in models:
        data = {"error": "Model type not included. Please add model type of either unet or unetpp."}
        return data, 406
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = app.config['UPLOAD_FOLDER'] + "/" + filename
        file.save(path)
        model = json.loads(request.form["json"])["model"]
        processedFilename = process_image(app.config['UPLOAD_FOLDER'], filename, model)
        data = {"processedFile": app.config['UPLOAD_FOLDER'] + "/" + processedFilename}
        return data, 200

@app.errorhandler(404)
def handle_404(e):
    app.logger.exception(e)
    return redirect(url_for("startingpoint"))

@app.errorhandler(FileNotFoundError)
def missing_file(e):
    app.logger.exception(e)
    fileError = "There was a problem with the uploaded image file, please try uploading it again."
    scroll = "Live-App"
    return render_template("basetemplate.html", error = fileError,  scroll=scroll)