import glob
import os
import random
import json
# from shapely import geometry
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import math

# save mask in "8_bit_binary" or "1_bit_binary", 
# 8-bit mode has better compatibility in general
mode = "8_bit_binary"
in_dir = "C:/Users/Matthew/Desktop/Mobile Robotics - Personal Project/photos/original - pipeline/images"
out_dir = "C:/Users/Matthew/Desktop/Mobile Robotics - Personal Project/photos/original - pipeline/masks"
mask_list = {
"black_rect_sm",
"blue_rect_lg",
"blue_rect_md",
"green_cir_sm",
"green_rect_sm",
"red_rect_lg",
"red_rect_md",
"red_rect_sm"}  # set of label names

# create output directories
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

for name in mask_list:
    new_dir = os.path.join(out_dir, name)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

# set image mode
if mode == "1_bit_binary":
    pil_mode = "1"
    pil_fill = 1
elif mode == "8_bit_binary":
    pil_mode = "L"
    pil_fill = 255
else:
    raise Exception("Illegal image mode!")

# begin mask generation
for file in glob.glob(os.path.join(in_dir, "*.jpg")):
    im = Image.open(file)
    width, height = im.size
    
    # Find png and corresponding json file by name
    general_path = file.strip(".jpg")
    general_name = os.path.basename(general_path)
    json_path = general_path + ".json"
    json_data = open(json_path).read()
    data = json.loads(json_data)
    
    shapes = data["shapes"]
    masks = {}
    for shape in shapes:
        label = shape["label"]
        points = shape["points"]
        shape_type = shape["shape_type"]
        
        # create new mask if the class appear for the first time
        if label not in masks:
            masks[label] = Image.new(pil_mode, (width, height))
        draw = ImageDraw.Draw(masks[label])
        
        # TODO: Support more format. Only support polygon and circle yet
        if shape_type == "polygon":
            p = [(p[0], p[1]) for p in points]
            draw.polygon(p, fill=pil_fill)
        elif shape_type == "circle":
            center = points[0]
            another = points[1]
            radius = math.hypot(another[0] - center[0], another[1] - center[1])
            draw.ellipse((center[0] - radius, center[1] - radius,
                          center[0] + radius, center[1] + radius), fill=pil_fill)

    # create empty mask for absent label
    existed_mask = set(masks.keys())
    absent_mask = mask_list.difference(existed_mask)
    for absent in absent_mask:
        masks[absent] = Image.new(pil_mode, (width, height))

    # save all masks to file
    for label, mask in masks.items():
        mask_name = "_".join([general_name, label])
        mask_path = os.path.join(out_dir, label, mask_name)
        mask.save(mask_path + ".png", "PNG")
