@echo off

REM This will download all the needed models 
IF not exist %cd%\FCN\NUL GOTO prompta
IF not exist %cd%\unet\NUL GOTO prompta
IF not exist %cd%\unet++\NUL GOTO prompta
GOTO promptb

:prompta
setlocal
SET /P AREYOUSURE1="The models are not downloaded. Would you like to download them and include them in the directory?(y/n)"
IF /I "%AREYOUSURE1%" NEQ "y" GOTO RUNFLASK
endlocal

:DOWNLOADMODELS
bitsadmin /transfer downloadmodels "https://thisbucketholdsthemodelsforimsp21g1.s3-ap-northeast-1.amazonaws.com/models.zip" %cd%\models.zip
powershell Expand-Archive models.zip

:promptb
setlocal
SET /P AREYOUSURE2="Would you like to make sure that all the right python packages are installed and install the missing ones?(y/n)"
IF /I "%AREYOUSURE2%" NEQ "y" GOTO RUNFLASK
endlocal
pip install -r requirements.txt


:RUNFLASK
RunFlask
