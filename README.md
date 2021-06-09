# IM_group1

This is the code repository for the industrial maintenance group 1

The models are too big for github, so I have saved them to an AWS bucket [here](https://thisbucketholdsthemodelsforimsp21g1.s3-ap-northeast-1.amazonaws.com/models.zip). When you download them, unzip the file and put all three models in the root directory (at the same level as main.py).

As a simple way to get started with the project, you can just run the SetupAndRunFlask.bat batch file. This will download the required model files, install the required python packages, and start flask. 

This flask app can be ran from your local computer. You just need to do a couple things. 

If you are on a windows computer, you need to type in the command prompt: 

```
set FLASK_APP = main.py
```

If you are using mac or linux, you will need to use `export` instead of `set`

You can then run flask which automatically loads the python script and starts the local server.

To run the flask app you need to type either:

```
python -m flask run
```
or 
```
flask run
```

When it runs, you should see an ip address that you can access the server from.

Make sure that in "main.py" that the code `WEB_APP` is set to `False`.

~~The webapp might be running.If it is, you can find it at http://imsp21g1.online/.  As of Fri 21-May-21 05:24 PM, the app just puts the uploaded picture in the webpage. More work will be done for the page.~~

~~I found out that the website does not cost any money since it has so few users, so it will just continuously be running. You can find it anytime at http://imsp21g1.online/. ~~

I found out that the website is a little expensive to contunuously run, so just let me know when you want to run it. 