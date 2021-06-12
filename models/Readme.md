The models are loaded from this folder. Each model should be a folder with the following structure:

* model
  * assets
  * variables
    * variables.data-00000-of-00001
    * variables.index 
  * saved_model.pb
  * keras_metadeata.pb (this is optional)

This folder format is the same one whenever saving a tensorflow model using the `model.save("model_name")` method