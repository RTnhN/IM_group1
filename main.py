# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Use this code to launch the app in the google cloud: 
# gcloud app deploy app.yaml
# 
# Use this code to launch the app in local development: 
# set FLASK_APP=main.py 
# set FLASK_ENV=development this turns on debug mode that updates the server instance each time the code is updated
# flask run or python -m flask run
# To launch the web app:
# gcloud app deploy app.yaml
# [START app]
import os
from flask import Flask, jsonify, render_template,redirect,flash, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
from algorithm import algorithm
import requests
import logging
import google.cloud.logging
client = google.cloud.logging.Client()
client.get_default_handler()
client.setup_logging()

VERIFY_URL = "https://hcaptcha.com/siteverify"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__, instance_relative_config=True)

WEBAPP = True

if WEBAPP:
    app.config.from_pyfile("configWebApp.py")
else:
    app.config.from_pyfile("config.py")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/tmp/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/", methods=['GET', 'POST'])
def startingpoint():
    fileError = ""
    scroll = ""
    if request.method =="POST":
        if not app.config['RECAPTCHA_ENABLED'] or verify() :
            if 'file' not in request.files:
                fileError = "<p>Please upload a file before hitting Submit</p>"
                scroll = "Live-App"
            file = request.files['file']
            if file.filename == '':
                fileError = "<p>Please upload a file before hitting Submit</p>"
                scroll = "Live-App"
            if not allowed_file(file.filename):
                fileError = "<p>Please upload a file with only one of the allowed types (.png, .jpg, .jpeg, .gif)</p>"
                scroll = "Live-App"    
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(app.config['UPLOAD_FOLDER'] + "/" +filename)
                return redirect(url_for('processed',
                                        filename=filename))
        else:
            fileError = "<p>There was a problem with the captcha, please try again</p>"
            scroll = "Live-App"
        
    name1 = fileError + '''<form method=post enctype=multipart/form-data>
              <div class="h-captcha" data-sitekey="2380b2b1-0209-4631-8c8f-1432f6528777"></div>
              <input type=file name=file> 
              <input type=submit value=Upload>
              </form>'''
    return render_template("template.html", my_string = name1, scroll=scroll)

@app.route('/processed/<filename>', methods=['GET', 'POST'])
def processed(filename):
    processedFilename = algorithm(filename)
    path = app.config['UPLOAD_FOLDER'] + "/" + filename
    html_snippet = '''
    <p><a href="/#Live-App" class="w3-button w3-red">Upload another image</a></p>
    <div class="w3-row-padding">
        <div class="w3-half">
            <img src="/tmp/'''+ filename + '''" alt="Original Image" onclick="onClick(this)" style="width:100%;cursor:pointer"> 
                <p> This is the original image uploaded. </p>
        </div>
        <div class="w3-half">
            <img src="/tmp/'''+ processedFilename + '''" alt="Image with marked nuclei" onclick="onClick(this)" style="width:100%;cursor:pointer">
            <div class="w3-display-container">
                <p> This is the image with the marked nuclei (if any)
            </div>
        </div>
    </div>

    '''
    return render_template("template.html", my_string = html_snippet, scroll="Live-App")   

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



