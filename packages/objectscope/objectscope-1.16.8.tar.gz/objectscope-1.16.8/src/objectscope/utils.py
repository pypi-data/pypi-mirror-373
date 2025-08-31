from tensorboard import program
from objectscope import logger
import subprocess
from PIL import Image
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont
from cpauger.visualize import random_color
from detectron2.data import MetadataCatalog
import json
import os

def launch_tensorboard(logdir, port_num=None):
    if not port_num:
        port_num = "default"
    tb = program.TensorBoard()
    argv = [None, "--logdir", logdir, "--port", port_num]
    tb.configure(argv)
    url = tb.launch()
    logger.info(f"TensorBoard launched at {url}")
    
    
def run_optimize_model(model_name_or_path, output_dir, device="cpu",
                       provider="CPUExecutionProvider",
                       precision="int4",
                       ):
    logger.info("Optimizing model...")
    cmd = ["olive", "auto-opt",
            "--model_name_or_path", model_name_or_path,
            "--trust_remote_code",
            "--output_path", output_dir,
            "--device", device,
            "--provider", provider,
            "--use_ort_genai",
            "--precision", precision,
            "--log_level", 1
            ]
    subprocess.run(cmd, check=True)
    logger.info("Model optimization completed.")


def compute_statistics(img_paths: list):
    channel_sum    = np.zeros(3, dtype=np.float64)
    channel_sqsum  = np.zeros(3, dtype=np.float64)
    total_pixels   = 0

    for path in img_paths:
        with Image.open(path) as img:
            img = img.convert("RGB")
            arr = np.asarray(img, dtype=np.float64) / 255.0 

        h, w, _ = arr.shape
        pixels = h * w

        channel_sum   += arr.sum(axis=(0, 1))
        channel_sqsum += (arr ** 2).sum(axis=(0, 1))
        total_pixels  += pixels

    mean = channel_sum / total_pixels
    var  = channel_sqsum / total_pixels - mean ** 2
    std  = np.sqrt(var)

    return {
        "chan_mean": mean,  
        "chan_std":  std,   
        "chan_var":  var,   
    }


def predict_bbox(image, model_path):
    ort_session = ort.InferenceSession(model_path)
    input_name = ort_session.get_inputs()[0].name
    output = ort_session.run(None, {input_name: image})
    return {"bbox": output[0],
            "class": output[1],
            "score": output[2],
            "shape": output[3],
            }


def draw_bbox_and_polygons(image, bboxes, scores, 
                            class_names=None, 
                            score_thresh=0.3,
                            polygons=None
                        ) -> Image:
    """Visualize the bbox(es) and segmentation mask(s) of objects in image(s)

    Args:
        image (Image): PIL Image to draw bbox and segmentation on.
        bboxes (List): List of boundary boxes.
        scores (List): Confidence score to use for filtering and drawing on image.
        class_names (List): Name(s) of objects for each bbox and polygon.
        score_thresh (float, optional): Threshold to filter out low-confidence detections. Defaults to 0.3.
        polygons (List, optional): List of segmentation masks. Defaults to None.

    Returns: PIL Image with drawn bbox and segmentation mask.
    """
    try:
        font = ImageFont.truetype("arial.ttf", size=20)
    except IOError:
        font = ImageFont.load_default()

    if polygons:
        image = image.convert("RGBA")
        mask_img = Image.new("RGBA", image.size)
        draw = ImageDraw.Draw(mask_img)
    else:
        draw = ImageDraw.Draw(image)
        
    for bbox, class_name, score, polygon in zip(bboxes, class_names, scores, polygons if polygons else [None]*len(bboxes)):
        if score < score_thresh:
            continue
        color = random_color()
        bbox = [bbox[0], bbox[1], bbox[2], bbox[3]]
        draw.rectangle(bbox, outline=color, width=2)
        if polygon:
            draw.polygon(polygon, outline=color, fill=color + (100,))
        text_position = (bbox[0], bbox[1] - 10)
        draw.text(text_position, f"{class_name} @ {round(float(score), 4)}", 
                  fill=color, font=font,
                  )
    if polygons:
        blended_img = Image.alpha_composite(image, mask_img)
        image = blended_img.convert("RGB")
    return image    

def save_class_metadata(train_data_name,
                        save_metadata_as
                        ):
    metadata = MetadataCatalog.get(name=train_data_name)
    logger.info(f"metadata.thing_classes: {metadata.thing_classes}")
    logger.info(f"metadata.thing_dataset_id_to_contiguous_id: {metadata.thing_dataset_id_to_contiguous_id}")
    
    class_metadata_map = {"thing_names": metadata.thing_classes,
                            "thing_dataset_id_to_contiguous_id": metadata.thing_dataset_id_to_contiguous_id,
                            "class_id_class_names": {key: metadata.thing_classes[key] 
                                                    for key in metadata.thing_dataset_id_to_contiguous_id.values()
                                                    }
                            }
    dest_dir = os.path.dirname(save_metadata_as)
    os.makedirs(dest_dir, exist_ok=True)    
    with open(save_metadata_as, "w") as f:
        json.dump(class_metadata_map, f, indent=4)
        