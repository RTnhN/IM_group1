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

# [START app]
import os
from flask import Flask, jsonify, render_template,redirect,flash, request, url_for, send_from_directory
from werkzeug.utils import secure_filename

WEB_APP = False
if WEB_APP: 
    UPLOAD_FOLDER = "/tmp"
else:
    UPLOAD_FOLDER = "tmp"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 7 * 1024 * 1024 # 7MB limit for image upload

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
        
    name1 = fileError + '''<form method=post enctype=multipart/form-data> 
              <input type=file name=file> 
              <input type=submit value=Upload>
              </form>'''
    return render_template("template.html", my_string = name1, scroll=scroll)

@app.route('/processed/<filename>', methods=['GET', 'POST'])
def processed(filename):
    path = app.config['UPLOAD_FOLDER'] + "/" + filename
    html_snippet = '''
    <p><a href="/#Live-App" class="w3-button w3-red">Upload another image</a></p>
    <div class="w3-row-padding">
        <div class="w3-half">
            <img src="/tmp/'''+ filename + '''" alt="Original Image" onclick="onClick(this)" style="width:100%;cursor:pointer"> 
                <p> This is the original image uploaded. </p>
        </div>
        <div class="w3-half">
            <img src="/tmp/'''+ filename + '''" alt="Image with marked nuclei" onclick="onClick(this)" style="width:100%;cursor:pointer">
            <div class="w3-display-container">
                <p> This is the image with the marked nuclei (if any)
            </div>
        </div>
    </div>

    '''
    return render_template("template.html", my_string = html_snippet, scroll="Live-App")   

