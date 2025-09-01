from datasets import Dataset, concatenate_datasets,load_dataset
from torch.nn.utils.rnn import pad_sequence
import torch
import numpy as np
import random
from PIL import Image
import cv2
from tqdm import tqdm

def load_set(name_set:str):
    if(name_set.lower() == "set_a" ):
        dataset_set_a = load_dataset("aryadacademie/Ocr_Arabic_Merged_data_set",split='Ocr_Arabic_Merged_data_set_a')
        return dataset_set_a
    elif(name_set.lower() == "set_b" ):
        dataset_set_b = load_dataset("aryadacademie/Ocr_Arabic_Merged_data_set",split='Ocr_Arabic_Merged_data_set_b')
        return dataset_set_b   
    elif(name_set.lower() == "set_c" ):
        dataset_set_c = load_dataset("aryadacademie/Ocr_Arabic_Merged_data_set",split='Ocr_Arabic_Merged_data_set_c')
        return dataset_set_c
    elif(name_set.lower() == "set_d" ):
        dataset_d = load_dataset("aryadacademie/Ocr_Arabic_Merged_data_set",split='Ocr_Arabic_Merged_data_set_d')
        return dataset_d
    else:
        return None

def dataset_merged(list_set:list):
    gthru = ["set_a","set_b","set_c","set_d"]
    valid_sets = True
    for set_name in list_set:
        if set_name.lower() not in gthru:
            valid_sets = False
            break
    if valid_sets:
        all_datasets = [load_set(set_name.lower()) for set_name in list_set]
    else:
        assert False, "Invalid set name(s) provided. Valid names are: 'set_a', 'set_b', 'set_c', 'set_d'."
    return concatenate_datasets(all_datasets)

def filter_by_patterns(dataset:Dataset,patterns:list):
    def is_valid(example):
        phon = example["phonemes"]
        return not any(bad in phon for bad in patterns)
    return dataset.filter(is_valid)

class AryadCollator:
    def __init__(self, vocabOcrArabic, pad_token="<PAD>"):
        self.vocabOcrArabic = vocabOcrArabic
        self.pad_token_id = vocabOcrArabic[pad_token]

    def __call__(self, batch):
        images = [torch.tensor(ex["array"], dtype=torch.float32).unsqueeze(0) for ex in batch]
        labels = [torch.tensor([self.vocabOcrArabic.get(t) for t in ex["phonemes"].split("|")], dtype=torch.long) for ex in batch]

        images = torch.stack(images)
        labels_padded = pad_sequence(labels, batch_first=True, padding_value=self.pad_token_id)

        return {
            "pixel_values": images,  # (B, 1, H, W)
            "labels": labels_padded, # (B, L)
            "label_lengths": torch.tensor([len(l) for l in labels])
        }

def loader_batch_data(dataset:Dataset,batch_size:int,vocabOcrArabic:set,train:bool=True):
    from torch.utils.data import DataLoader
    collator = AryadCollator(vocabOcrArabic=vocabOcrArabic)
    if train:
        return DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collator)
    else:
        return DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=collator)

def elastic_deformation(image, alpha=19, sigma=3):
    original_size = image.size
    image_np = np.array(image)
    h, w = image_np.shape

    pad = 30
    padded = cv2.copyMakeBorder(image_np, pad, pad, pad, pad, cv2.BORDER_REFLECT_101)
    shape = padded.shape

    dx = cv2.GaussianBlur((np.random.rand(*shape) * 2 - 1), (17, 17), sigma) * alpha
    dy = cv2.GaussianBlur((np.random.rand(*shape) * 2 - 1), (17, 17), sigma) * alpha

    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    map_x = (x + dx).astype(np.float32)
    map_y = (y + dy).astype(np.float32)

    warped = cv2.remap(padded, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    center_crop = warped[pad:pad+h, pad:pad+w]
    return Image.fromarray(center_crop).resize(original_size)

def random_rotation(image, angle_range=10):
    angle = random.uniform(-angle_range, angle_range)
    return image.rotate(angle, resample=Image.NEAREST, fillcolor=0)

def perspective_skew(image, margin=5):
    original_size = image.size
    w, h = original_size
    orig_pts = np.float32([[margin, margin], [w-margin, margin], [w-margin, h-margin], [margin, h-margin]])
    shift = lambda: random.uniform(-margin, margin)
    dst_pts = np.float32([
        [margin + shift(), margin + shift()],
        [w - margin + shift(), margin + shift()],
        [w - margin + shift(), h - margin + shift()],
        [margin + shift(), h - margin + shift()]
    ])
    matrix = cv2.getPerspectiveTransform(orig_pts, dst_pts)
    image_np = np.array(image)
    warped = cv2.warpPerspective(image_np, matrix, (w, h), borderValue=0)
    return Image.fromarray(warped).resize(original_size)

# Appliquer une augmentation aléatoire n_times
def augment_images_by_label(image_np, label, n_times):
    augmented_images = []
    augmented_labels = []

    for _ in range(n_times):
        image = Image.fromarray(image_np).convert("L")
        transform = random.choice(['elastic', 'rotation', 'skew'])

        if transform == 'elastic':
            aug = elastic_deformation(image)
        elif transform == 'rotation':
            aug = random_rotation(image)
        elif transform == 'skew':
            aug = perspective_skew(image)
        else:
            aug = image 

        augmented_images.append(np.array(aug, dtype=np.uint8))
        augmented_labels.append(label)

    return np.stack(augmented_images), np.array(augmented_labels)

# Construire un dataset augmenté en conservant le schéma original
def build_augmented_dataset(dataset, n_times=1):
    features = dataset.features  
    aug_arrays = []
    aug_labels = []
    aug_ids = []

    for ex in tqdm(dataset):
        arrays, labels = augment_images_by_label(np.array(ex["array"], dtype=np.uint8), ex["phonemes"], n_times)
        aug_arrays.extend(arrays)
        aug_labels.extend(labels)
        aug_ids.extend([f"{ex['id']}_aug{i}" for i in range(n_times)])

    dataset_aug = Dataset.from_dict({
        "id": aug_ids,
        "array": aug_arrays,
        "phonemes": aug_labels
    }, features=features)

    return dataset_aug
