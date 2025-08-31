
# Adapted FROM: https://github.com/PacktPublishing/Hands-On-Computer-Vision-with-Detectron2/blob/main/Chapter07/Detectron2_Chapter07_Anchors.ipynb
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans
import math
from tqdm import tqdm
from pandas import json_normalize
import json
from typing import List, Union
plt.rcParams["figure.dpi"] = 150

def boxes2wh(boxes):
    x1y1 = boxes[:, :2]
    x2y2 = boxes[:, 2:]
    return x2y2 - x1y1

def wh2ratio(wh):
    return wh[:, 1] / wh[:, 0]

def best_ratio(ac_wh, gt_wh):
    all_ratios = gt_wh[:, None] / ac_wh[None]
    inverse_ratios = 1 / all_ratios
    ratios = np.minimum(all_ratios, inverse_ratios)  
    worst = np.min(ratios, axis=-1)
    best = np.max(worst, axis=-1)
    return best

def fitness(ac_wh, gt_wh, EDGE_RATIO_THRESHOLD = 0.25):
    ratio = best_ratio(ac_wh, gt_wh)
    return (ratio * (ratio > EDGE_RATIO_THRESHOLD)).mean()

def best_recall(ac_wh, gt_wh, EDGE_RATIO_THRESHOLD=0.25):
    ratio = best_ratio(ac_wh, gt_wh)
    best = (ratio > EDGE_RATIO_THRESHOLD).float().mean()
    return best


def estimate_clusters(values, num_clusters, iter=100):
    std = values.std(0).item()
    k, _ = kmeans(values / std, num_clusters, iter=iter)
    k *= std
    return k

def visualize_clusters(values, centers):
    plt.hist(values, histtype="step")
    plt.scatter(centers, [0]*len(centers), c="red")
    plt.show()
    

def evolve(sizes, ratios, gt_wh,
           iterations=10_000,
           probability=0.9,
           muy=1, sigma=0.05,
           fit_fn=fitness,
           verbose=False
           ):
    anchors = generate_cell_anchors(tuple(sizes), tuple(ratios))
    ac_wh = boxes2wh(anchors)
    best_fit = fit_fn(ac_wh, gt_wh)
    anchor_shape = len(sizes) + len(ratios)
    
    pbar = tqdm(range(iterations), desc="Evolving ratios and sizes:")
    
    for i, _ in enumerate(pbar):
        mutation = np.ones(anchor_shape)
        mutate = np.random.random(anchor_shape) < probability
        mutation = np.random.normal(muy, sigma, anchor_shape)*mutate
        mutation = mutation.clip(0.3, 3.0)
        # mutated
        mutated_sizes = sizes.copy()*mutation[:len(sizes)]
        mutated_ratios = ratios.copy()*mutation[-len(ratios):]
        mutated_anchors = generate_cell_anchors(tuple(mutated_sizes), tuple(mutated_ratios))
        mutated_ac_wh = boxes2wh(mutated_anchors)
        mutated_fit = fit_fn(mutated_ac_wh, gt_wh)
        
        if mutated_fit > best_fit:
            sizes = mutated_sizes.copy()
            ratios = mutated_ratios.copy()
            best_fit = mutated_fit
            pbar.desc = (f"Evolving {ratios} and {sizes}, Fitness = {best_fit: .4f}")
            
    return sizes, ratios


# COPIED FROM: Detectron2 source code detectron2/modeling/anchor_generator.py
def generate_cell_anchors(sizes=(32, 64, 128, 256, 512), 
                          aspect_ratios=(0.5, 1, 2)
                          ):
    """
    Generate a tensor storing canonical anchor boxes, which are all anchor
    boxes of different sizes and aspect_ratios centered at (0, 0).
    We can later build the set of anchors for a full feature map by
    shifting and tiling these tensors (see `meth:_grid_anchors`).

    Args:
        sizes (tuple[float]):
        aspect_ratios (tuple[float]]):

    Returns:
        Array of shape (len(sizes) * len(aspect_ratios), 4) storing anchor boxes
            in XYXY format.
    """
    anchors = []
    for size in sizes:
        area = size**2.0
        for aspect_ratio in aspect_ratios:
            w = math.sqrt(area / aspect_ratio)
            h = aspect_ratio * w
            x0, y0, x1, y1 = -w / 2.0, -h / 2.0, w / 2.0, h / 2.0
            anchors.append([x0, y0, x1, y1])
    return np.array(anchors)

def _wh2size(gt_wh):
    return np.sqrt(gt_wh[:,0] * gt_wh[:,1])

def _boxes2wh(boxes):
    wh = boxes[:, 2:]
    return wh


def get_size_ratio_fitness_score(sizes, ratios, gt_wh):
    anchors = generate_cell_anchors(sizes=tuple(sizes), 
                                    aspect_ratios=tuple(ratios)
                                    )
    anchor_wh = boxes2wh(anchors)
    fit_score = fitness(anchor_wh, gt_wh)
    return fit_score

def coco_annotation_to_df(coco_annotation_file):
    with open(coco_annotation_file, "r") as annot_file:
        annotation = json.load(annot_file)
    annotations_df = json_normalize(annotation, "annotations")
    annot_imgs_df = json_normalize(annotation, "images")
    annot_cat_df = json_normalize(annotation, "categories")
    annotations_images_merge_df = annotations_df.merge(annot_imgs_df, left_on='image_id', 
                                                        right_on='id',
                                                        suffixes=("_annotation", "_image"),
                                                        how="outer"
                                                        )
    annotations_imgs_cat_merge = annotations_images_merge_df.merge(annot_cat_df, left_on="category_id", right_on="id",
                                                                    suffixes=(None, '_categories'),
                                                                    how="outer"
                                                                    )
    all_merged_df = annotations_imgs_cat_merge[['id_annotation', 'image_id','category_id', 'bbox', 'area', 'segmentation', 'iscrowd',
                                'file_name', 'height', 'width', 'name', 'supercategory'
                                ]]
    all_merged_df.rename(columns={"name": "category_name",
                                  "height": "image_height",
                                  "width": "image_width"}, 
                         inplace=True
                         )
    all_merged_df.dropna(subset=["file_name"], inplace=True)
    return all_merged_df

class AnchorMiner(object):
    def __init__(self,
                 coco_annotation_file: str
                 ) -> None:
        self.coco_annotation_file = coco_annotation_file
        self.annotations_df = coco_annotation_to_df(coco_annotation_file) 
        
    def get_sizes_ratios(self, num_sizes=5, num_ratios=3):
        self.gt_boxes = np.concatenate(self.annotations_df.bbox.dropna().values).reshape(-1,4)
        self.gt_wh = _boxes2wh(self.gt_boxes)
        gt_sizes = _wh2size(self.gt_wh)
        gt_ratios = wh2ratio(self.gt_wh)
        self.sizes = estimate_clusters(gt_sizes, num_sizes)
        self.ratios = estimate_clusters(gt_ratios, num_ratios)
        return self.sizes, self.ratios
    
    def tune_sizes_ratios(self, sizes: Union[None, List]=None, 
                          ratios: Union[None, List]=None, 
                          iterations=10_000,
                          include_fitness_score=True,
                          ):
        if not sizes and not ratios:
            if hasattr(self, "sizes"):
                sizes = self.sizes
                ratios = self.ratios
            else:
                sizes, ratios = self.get_sizes_ratios()
        elif not sizes:
            if hasattr(self, "sizes"):
                sizes = self.sizes
            else:
                sizes, _ = self.get_sizes_ratios()
        elif not ratios:
            if hasattr(self, "ratios"):
                ratios = self.ratios
            else:
                _, ratios = self.get_sizes_ratios() 
        if hasattr(self, "gt_boxes"):
            gt_boxes = self.gt_boxes
        else:        
            gt_boxes = np.concatenate(self.annotations_df.bbox.dropna().values).reshape(-1,4)
        if hasattr(self, "gt_wh"):
            gt_wh = self.gt_wh
        else:
            gt_wh = _boxes2wh(gt_boxes)
        e_sizes, e_ratios = evolve(sizes, ratios, gt_wh, 
                                   iterations=iterations
                                   )
        self.tuned_sizes = e_sizes
        self.tuned_ratios = e_ratios
        if include_fitness_score:
            self.fitness_score = get_size_ratio_fitness_score(e_sizes, e_ratios, gt_wh)
        return e_sizes, e_ratios, self.fitness_score if include_fitness_score else (e_sizes, e_ratios, None)