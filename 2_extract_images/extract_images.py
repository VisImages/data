import argparse
import cv2
import os, json
from pdf2image import convert_from_path
import numpy as np

# extract images from pdf files
def extract_images(args):
    src_path = args.src
    dst_path = args.dst
    annos = args.annos
    
    paper_list = os.listdir(src_path)
    all_images = {}
    with open(annos, "r") as f:
        all_images = json.load(f)
    
    for paper in paper_list:
        paper_id = paper.split(".")[0]
        if not paper_id.isdigit() or paper_id not in all_images.keys():
            continue
        
        if not os.path.exists(os.path.join(dst_path, paper_id)):
            os.makedirs(os.path.join(dst_path, paper_id))

        image_info = all_images[paper_id]
        for image in image_info:
            page_num = image["page"] + 1
            page_img = convert_from_path(os.path.join(src_path, paper), dpi=image["dpi"], first_page=page_num, last_page=page_num)
            page_img = cv2.cvtColor(np.array(page_img[0]), cv2.COLOR_RGB2BGR)
            
            height, width = page_img.shape[:2]
            bbox = image["bbox"].copy()
            img = page_img[int(height*bbox[1]):int(height*bbox[3]),int(width*bbox[0]):int(width*bbox[2])]

            cv2.imwrite(os.path.join(dst_path, paper_id, image["file_name"]), img)
        
        with open(os.path.join(dst_path, paper_id, "records.json"), "w") as output:
            json.dump(image_info, output)
            print(paper)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--src", "-s", default="vis_data/papers", help="pdf source path", type=str)
    parser.add_argument("--dst", "-d", default="vis_data/images", help="images destination path", type=str)
    parser.add_argument("--annos", default="vis_data/visimages_data.json", help="images destination path", type=str)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    extract_images(args)
    