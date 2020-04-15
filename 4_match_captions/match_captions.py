import os, json, math
import cv2, pprint
import argparse
import numpy as np
from pdf2image import convert_from_path,convert_from_bytes
from math import fabs

# search for the minimum distance sum
def BFS(x, time, image_num, caption_num, match_list, vis_list, dist, weight):
    max_num = 30
    need = [np.inf] * max_num * 2
    pre = [0] * max_num * 2
    u = 0
    nex = 0
    match_list[u] = x

    while True:
        x = match_list[u]
        D = np.inf
        vis_list[u] = time

        for y in range(image_num + 1, image_num + caption_num + 1):
            if vis_list[y] == time:
                continue

            t = weight[x] + weight[y] - dist[x][y - image_num]
            # Update need pre
            if t < need[y]:
                need[y] = t
                pre[y] = u
            # Update D nex
            if need[y] < D:
                D = need[y]
                nex = y
        
        # Update status
        weight[match_list[0]] -= D
        weight[0] += D
        for i in range(image_num + 1, image_num + caption_num + 1):
            if vis_list[i] == time:
                weight[match_list[i]] -= D
                weight[i] += D
            else:
                need[i] -= D
        
        u = nex

        if match_list[u] == 0:
            break
    
    while u:
        match_list[u] = match_list[pre[u]]
        u = pre[u]
    
    return

# Using KM algorithm to match captions
def match_captions_in_page(image_dict, caption_dict):
    image = np.array(image_dict)
    caption = np.array(caption_dict)

    # compute distance beween images and captions
    image_num = len(image)
    caption_num = len(caption)
    dist = np.zeros((30, 30))
    image = np.repeat(np.expand_dims(image, axis=1), caption_num, axis=1)
    caption = np.repeat(np.expand_dims(caption, axis=0), image_num, axis=0)
    tmp_dist = np.sum(np.power(image - caption, 2), axis=2)
    max_dist = np.max(np.reshape(tmp_dist, (-1)))
    dist[1:image_num+1, 1:caption_num+1] = -tmp_dist + max_dist + 1

    weight = np.zeros((30 * 2,))
    weight[:image_num+1] = np.max(dist, axis=1)[:image_num+1]
    time = 0
    vis_list = [0] * 30 * 2
    match_list = [0] * 30 * 2
    caption_num = max(caption_num, image_num)

    for i in range(1, image_num + 1):
        time += 1
        BFS(i, time, image_num, caption_num,\
            match_list, vis_list, dist, weight)
    
    for i in range(image_num + 1, image_num + caption_num + 1):
        if fabs(dist[match_list[i]][i-image_num]) > 1e-3:
            match_list[match_list[i]] = i

    result_list = []
    for i in range(1, image_num + 1):
        # print(match_list[i] - image_num if match_list[i] else match_list[i])
        if match_list[i]:
            result_list.append(match_list[i] - image_num)
        else:
            result_list.append(match_list[i])
    
    return result_list



# cal center point according to visimages_data
def cal_center_point(paper_path, paper_id, page_num, bbox, dpi=1):
    height = 1
    width = 1
    # transfer for bbox coordinates in 'visimages_data.json'
    if dpi != 1:
        img = convert_from_path(os.path.join(paper_path, paper_id + ".pdf"), \
                                dpi=dpi, first_page=page_num, last_page=page_num)
        page_img = cv2.cvtColor(np.array(img[0]),cv2.COLOR_RGB2BGR)
        height, width = page_img.shape[:2]

    center_x = (bbox[0] + bbox[2]) * width / 2
    center_y = (bbox[1] + bbox[3]) * height / 2
    return (center_x, center_y)


# match caption text to images, with the lowest sum of distance
def match_captions(args):
    paper_path = args.paper
    src_path = args.src
    dst_path = args.dst
    annos = args.annos

    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    
    all_images = {}
    with open(annos, "r") as f:
        all_images = json.load(f)
    
    caption_list = os.listdir(src_path)
    for paper in caption_list:
        paper_id = paper.split(".")[0]
        if not paper_id.isdigit() or paper_id not in all_images.keys():
            continue

        # read caption info
        with open(os.path.join(src_path, paper), "r") as f:
            captions = json.load(f)
            cur_paper = []
            caption_text_dict = dict()
            caption_dict = dict()
            image_dict = dict()
            image_index_dict = dict()

            # extract images of each page
            index = 0
            for image in all_images[paper_id]:
                page_num = image["page"] + 1
                if page_num not in image_dict.keys():
                    image_dict[page_num] = []
                    image_index_dict[page_num] = []
                image_dict[page_num].append(cal_center_point(paper_path, paper_id, page_num, image["bbox"], dpi=100))
                image_index_dict[page_num].append(index)
                index += 1
            
            # extract captions of each page
            for image in captions:
                page_num = image["Page"]
                if page_num not in caption_dict.keys():
                    caption_dict[page_num] = []
                    caption_text_dict[page_num] = []
                caption_dict[page_num].append(cal_center_point(paper_path, paper_id, page_num, image["CaptionBB"]))
                caption_text_dict[page_num].append((image["Caption"], image["CaptionBB"]))
            
            # unwrap caption info
            for page_num in image_dict.keys():
                if page_num not in caption_dict.keys():
                    for image_index in image_index_dict[page_num]:
                        cur_image = all_images[paper_id][image_index]
                        cur_image["caption_text"] = None
                        cur_image["caption_bbox"] = None
                        cur_paper.append(cur_image)
                else: 
                    match_list = match_captions_in_page(image_dict[page_num], caption_dict[page_num])
                    for index in range(len(match_list)):
                        caption_text = None
                        caption_bbox = None
                        if match_list[index] != 0:
                            caption_text = caption_text_dict[page_num][match_list[index] - 1][0]
                            caption_bbox = caption_text_dict[page_num][match_list[index] - 1][1]
                        image_index = image_index_dict[page_num][index]
                        cur_image = all_images[paper_id][image_index]
                        cur_image["caption_text"] = caption_text
                        cur_image["caption_bbox"] = caption_bbox
                        cur_paper.append(cur_image)
            
            with open(os.path.join(dst_path, paper), "w") as output:
                print(paper)
                json.dump(cur_paper, output)
                        





def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--paper", "-p", default="vis_data/papers", help="destination path", type=str)
    parser.add_argument("--src", "-s", default="3_extract_captions/pdffigures/precomputed", help="captions source path", type=str)
    parser.add_argument("--dst", "-d", default="vis_data/captions", help="destination path", type=str)
    parser.add_argument("--annos", default="vis_data/visimages_data.json", help="images destination path", type=str)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    match_captions(args)

