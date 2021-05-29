def algorithm(folder,filename):
    # Your code here can use the file name to find the picture that needs processing
    # It should also save the image to /tmp/processedImage.jpg
    # The code can also return other parameters like the number of nuclei or certianty. You will just need to add it to the code.
    with open(folder+"/"+filename, "rb") as f:
        img = f.read()
    processedfilename = "processed_" + filename 

    with open(folder+"/"+processedfilename, "wb" ) as f:
        f.write(img)
    return processedfilename 