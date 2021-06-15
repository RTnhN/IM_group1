# Use this code to launch the app in local development: 
# set FLASK_APP=main.py 
# set FLASK_ENV=development this turns on debug mode that updates the server instance each time the code is updated
# flask run or python -m flask run
# To launch the web app:
# gcloud app deploy app.yaml

from flask import Flask, render_template,redirect, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
from process_image import predict
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os

app = Flask(__name__, instance_relative_config=True)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["1000 per day", "200 per hour"])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MODELS = ["unet", "unetpp", "fcn", "gan"]

# There are some secret keys that I need to use for the web app. Those 
# are in configWebApp.py which is not pushed to the git repository. For 
# regular use, it is okay just to use config.py. By using config.py, no 
# captcha is needed when running the app. 

WEB_APP = False
if WEB_APP:
    app.config.from_pyfile("configWebApp.py")
else:
    app.config.from_pyfile("config.py")

if app.config["LOG"]:
    import logging
    import google.cloud.logging
    client = google.cloud.logging.Client()
    client.get_default_handler()
    client.setup_logging()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mode can either be "mem_save" or "time_save". "mem_save" loads the models into 
# memory only when needed while "time_save" loads all the models into memory at the 
# start so that prediction is faster
process_instance = predict(mode="time_save")

@app.route('/tmp/<filename>')
@limiter.exempt
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route("/", methods=['GET', 'POST'])
def home_route():
    error_text = ""
    scroll = ""
    if request.method =="POST":
        if not app.config['RECAPTCHA_ENABLED'] or verify() :
            if 'file' not in request.files:
                error_text = "Please upload a file before hitting Submit"
                scroll = "Live-App"
            file = request.files['file']
            if file.filename == '':
                error_text = "Please upload a file before hitting Submit"
                scroll = "Live-App"
            if not allowed_file(file.filename):
                error_text = "Please upload a file with only one of the allowed types (.png, .jpg, .jpeg, .gif)"
                scroll = "Live-App"    
            if file and allowed_file(file.filename):
                model = request.form["model"]
                filename = secure_filename(file.filename)
                file.save(app.config['UPLOAD_FOLDER'] + "/" +filename)
                return redirect(url_for('processed', model=model, filename=filename))
        else:
            error_text = "There was a problem with the captcha, please try again"
            scroll = "Live-App"
    return render_template("basetemplate.html", error = error_text,  scroll=scroll)

@app.route('/processed/<model>/<filename>', methods=['GET'])
def processed(model, filename):
    processed_filename = process_instance.process_image(app.config['UPLOAD_FOLDER'], filename, model)
    return render_template("Results.html", processed = processed_filename, unprocessed = filename, scroll="Live-App")   

def verify():
    data = {"secret": app.config['RECAPTCHA_SECRET_KEY'],
        "response": request.form.get('h-captcha-response'),
        "remoteip": request.environ.get('REMOTE_ADDR')}
    r = requests.post(app.config['VERIFY_URL'], data=data)
    if app.config["LOG"]:
        logging.info("This is the response from hcaptcha: "+str(r))
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
    if 'json' not in request.form or json.loads(request.form["json"])["model"] not in MODELS:
        data = {"error": "Model type not included. Please add model type of one of the following: " + " ".join(str(x) for x in MODELS)}
        return data, 406
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = app.config['UPLOAD_FOLDER'] + "/" + filename
        file.save(path)
        model = json.loads(request.form["json"])["model"]
        processed_filename = process_instance.process_image(app.config['UPLOAD_FOLDER'], filename, model)
        data = {"processed_file": app.config['UPLOAD_FOLDER'] + "/" + processed_filename}
        return data, 200

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.errorhandler(404)
def handle_404(e):
    app.logger.exception(e)
    return redirect(url_for("home_route"))

@app.errorhandler(FileNotFoundError)
def missing_file(e):
    app.logger.exception(e)
    error_text = "There was a problem with the uploaded image file, please try uploading it again."
    scroll = "Live-App"
    return render_template("basetemplate.html", error = error_text,  scroll=scroll)
