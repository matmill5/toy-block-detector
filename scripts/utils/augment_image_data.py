'''
Generates synthetic variations of a base images-dataset
Creates more robust data & hedges against overfitting (memorizing data / failure to generalize)
'''

import imageio
import imgaug as ia
from imgaug import augmenters as iaa
import json
from imgaug.augmentables.polys import Polygon, PolygonsOnImage
import pprint
import os

def augment_image(image_name, frame_name):
    image = imageio.imread(f"C:/Users/Matthew/Desktop/Mobile Robotics - Personal Project/photos/original - labelme/{image_name}")
    
    with open(f"C:/Users/Matthew/Desktop/Mobile Robotics - Personal Project/photos/original - labelme/{frame_name}") as f:
        labelme_json = json.load(f)

    shapes_list = labelme_json['shapes']
    polygon_list = []
    for shape in shapes_list:
        polygon_list.append(Polygon(shape['points'], label=shape['label']))

    psoi = ia.PolygonsOnImage(polygon_list, shape=image.shape)
    # ia.imshow(psoi.draw_on_image(image, alpha_face=0.2, size_points=7))
    psoi.draw_on_image(image, alpha_face=0.2, size_points=7)
    
    ### Construct a sequential transformation pipeline ###
    # Randomly select some subset of the available transformations
    # Apply them in a random order
    # Seed a random value and rotate the image
    ia.seed(4)

    aug = iaa.Sequential([iaa.SomeOf((0, 7), [
        iaa.Affine(rotate=(-25, 25)),
        iaa.AdditiveGaussianNoise(scale=(30, 90)),
        iaa.Crop(percent=(0, 0.4)),
        iaa.CropAndPad(percent=(-0.2, 0.2), pad_mode="edge"),  # crop and pad images
        iaa.AddToHueAndSaturation((-60, 60)),  # change their color
        iaa.ElasticTransformation(alpha=90, sigma=9),  # water-like effect
        iaa.Cutout()  # replace one squared area within the image by a constant intensity value
    ], random_order=True)])

    # Conduct that sequential transofrmation in a random order, 32 times
    # augmented = [seq(image=image, polygons=psoi) for _ in range(32)]

    # Display the 32 synthetic variations of the original image
    # Print the frame name as a progress indicator
    print(f"Augmenting: {frame_name}")

    images_polys_aug = []
    for idx in range(32):
        image_aug, psoi_aug = aug(image=image, polygons=psoi)
        image_polys_aug = psoi_aug.draw_on_image(image_aug, alpha_face=0.2, size_points=11)
        images_polys_aug.append(image_polys_aug)

        shape_aug_list = []
        for poly_aug in psoi_aug:
            shape_aug_list.append(dict({
                'label' : poly_aug.label,
                'points' : list(poly_aug.coords.tolist()),
                "group_id": None,
                "shape_type": "polygon",
                "flags": {}
                }))

        labelme_json_augmented = {
        "version": "4.5.7",
        "flags": {},
        "shapes": shape_aug_list,
        "imagePath": f"{image_name.replace('.jpg','')}_v{idx}.jpg",
        "imageData" : None,
        "imageHeight": 480,
        "imageWidth": 640
        }

        # pprint.pprint(labelme_json_augmented)

        with open(f"C:/Users/Matthew/Desktop/Mobile Robotics - Personal Project/photos/original - labelme/{frame_name.replace('.json','')}_v{idx}.json", 'w') as f:
            json.dump(labelme_json_augmented, f)
        
        imageio.imwrite(f"C:/Users/Matthew/Desktop/Mobile Robotics - Personal Project/photos/original - labelme/{image_name.replace('.jpg','')}_v{idx}.jpg", image_aug)

    # ia.imshow(ia.draw_grid(images_polys_aug, cols=8))

# for file in os.listdir("C:/Users/Matthew/Desktop/Mobile Robotics - Personal Project/photos/original - labelme"):
#     if file.endswith(".jpg") and '_v' not in file:
#         augment_image(file, file.replace(".jpg", ".json"))

for file in os.listdir("C:/Users/Matthew/Desktop/Mobile Robotics - Personal Project/photos/original - pipeline/backgrounds"):
    if file.endswith(".jpg") and '_v' not in file:
        augment_image(file, file.replace(".jpg", ".json"))
        
# augment_image('frame0000.jpg', 'frame0000.json')