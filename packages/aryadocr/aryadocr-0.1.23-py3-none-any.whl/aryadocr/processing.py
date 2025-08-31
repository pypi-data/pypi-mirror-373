import pandas as pd
from tqdm import tqdm
from glob import glob
import cv2
import re
from datasets import Dataset, Features, Array2D,Value,load_dataset


def processing_phoneme(dirs_files = {
    'set_a':"C:/Users/farya/Documents/OcrDataEtude/set_a/set_a/tru/*.tru",
    'set_b':"C:/Users/farya/Documents/OcrDataEtude/set_b/set_b/tru/*.tru",
    'set_c':"C:/Users/farya/Documents/OcrDataEtude/set_c/set_c/tru/*.tru",
    'set_d':"C:/Users/farya/Documents/OcrDataEtude/set_d/set_d/tru/*.tru",
},path_dataset="aryadacademie/Arabic_Ocr_set"):
    
    for name_file ,dir_file in tqdm(dirs_files.items()):
        try:
            tru = glob(dir_file)
            ids_files = []
            phonemes_files = []
            for path in tru:
                with open(f"{path}","r") as f:
                    verite = f.readlines()
                    id_file = re.search(r"COM:\s+(\S+\.tif)", verite[3]).group(1)[:-4]
                    phoneme_file = re.search(r"AW2:([^;]+)", verite[6]).group(1).rstrip('|')
                    ids_files.append(id_file)
                    phonemes_files.append(phoneme_file)
    
            df = pd.DataFrame({
                "id": ids_files,
                "phonemes": phonemes_files
            })
    
            features = Features({
                "id": Value("string"),
                "phonemes": Value("string")
            })
    
            dataset = Dataset.from_dict(df, features=features)
            dataset.push_to_hub(path_dataset, split=f"arabic_ocr_phonemes_{name_file}")
            print(f"Dataset {name_file} push avec succès\n")
    
        except Exception as e:
            print(f"Erreur avec {name_file} : {e}\n")


def processing_array(dir_image_resize = {
    "array_set_a":'C:/Users/farya/Documents/OcrDataEtude/set_a/set_a/tif/*.tif',
    "array_set_b":'C:/Users/farya/Documents/OcrDataEtude/set_b/set_b/tif/*.tif',
    "array_set_c":'C:/Users/farya/Documents/OcrDataEtude/set_c/set_c/tif/*.tif',
    "array_set_d":'C:/Users/farya/Documents/OcrDataEtude/set_d/set_d/tif/*.tif'
},path_dataset="aryadacademie/arabic_ocr_array_set_all"):
    for name_dir,path_dir in tqdm(dir_image_resize.items()):
        try:
            ids_paths = []
            imgs_paths = []
            images_paths = {re.search(r'([^\\/]+)\.tif$',path).group(1): cv2.resize(cv2.bitwise_not(cv2.imread(path.replace('\\','/'),0)),(300,100))//255  for path in glob(path_dir)}
            for id_path,img_path in images_paths.items():
                ids_paths.append(id_path)
                imgs_paths.append(img_path)
            
            ds = pd.DataFrame({
            "id":ids_paths,
            "array":imgs_paths}) 
            
            features = Features({
            "id": Value("string"),
            "array": Array2D(dtype="uint8", shape=(100,300))}) 
            
            dataset = Dataset.from_dict(ds, features=features)
            dataset.push_to_hub(path_dataset, split=f"arabic_ocr_{name_dir}")
            print(f"dataset {name_dir} push avec succès")
        
        except Exception as e:
            print(f"Erreur avec {name_dir} : {e}\n")


def merge_set(liste_set=['a','b','c','d'],
              ds_array = load_dataset("aryadacademie/arabic_ocr_array_set_all"),
              ds_ph = load_dataset("aryadacademie/Arabic_Ocr_set")
             ):
    for lettre in liste_set:
        ids_array = ds_array[f'arabic_ocr_array_set_{lettre}']['id']
        ids_ph = ds_ph[f'arabic_ocr_phonemes_set_{lettre}']['id']
        
        assert all(i == j for i, j in zip(ids_array, ids_ph))
        
        merged_dataset_set = ds_array[f'arabic_ocr_array_set_{lettre}'].add_column(
            'phonemes', 
            ds_ph[f'arabic_ocr_phonemes_set_{lettre}']['phonemes']
        )
        merged_dataset_set.push_to_hub("aryadacademie/Ocr_Arabic_Merged_data_set", split=f"Ocr_Arabic_Merged_data_set_{lettre}")
        print(f"dataset set_{lettre} push avec succès")


def vocab_processing(vocabs):
    for name_set,vocab in vocabs.items():
        vocab_set_token = set([token for phoneme in vocab for token in phoneme.split('|')])
        ds = {
            f'vocabulaire_{name_set}':list(vocab_set_token)
        }
        df = pd.DataFrame(ds)
        df.to_csv(f"vocabulaire_{name_set}.csv", index=False)

def read_csv_vocab(path):
    df = pd.read_csv(path)
    vocabOcrArabic = {token:id_ for token,id_ in zip(df['token'],df['id'])}
    return  vocabOcrArabic 