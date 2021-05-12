import glob, os
with open("val.txt", "w") as f:
    os.chdir("C:/Users/Matthew/Desktop/Mobile Robotics - Personal Project/photos/original - pipeline/augmentation/val/")
    for file in glob.glob("*.jpg"):
        f.write(os.path.abspath(file) + "\n")
