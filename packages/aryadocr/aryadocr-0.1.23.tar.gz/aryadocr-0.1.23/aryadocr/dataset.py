from datasets import Dataset,load_dataset
from datasets import Dataset, concatenate_datasets
from torch.nn.utils.rnn import pad_sequence
import torch
from datasets import concatenate_datasets

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

