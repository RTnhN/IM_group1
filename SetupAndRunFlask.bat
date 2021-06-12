@echo off

@REM REM This will download all the needed models 
@REM IF not exist %cd%\FCN\NUL GOTO prompta
@REM IF not exist %cd%\unet\NUL GOTO prompta
@REM IF not exist %cd%\unet++\NUL GOTO prompta
@REM GOTO promptb

@REM :prompta
@REM setlocal
@REM SET /P AREYOUSURE1="The models are not downloaded. Would you like to download them and include them in the directory?(y/n)"
@REM IF /I "%AREYOUSURE1%" NEQ "y" GOTO RUNFLASK
@REM endlocal

@REM :DOWNLOADMODELS
@REM bitsadmin /transfer downloadmodels "https://thisbucketholdsthemodelsforimsp21g1.s3-ap-northeast-1.amazonaws.com/models.zip" %cd%\models.zip
@REM powershell Expand-Archive models.zip

:promptb
setlocal
SET /P AREYOUSURE2="Would you like to make sure that all the right python packages are installed and install the missing ones?(y/n)"
IF /I "%AREYOUSURE2%" NEQ "y" GOTO RUNFLASK
endlocal
pip install -r requirements.txt


:RUNFLASK
RunFlask
