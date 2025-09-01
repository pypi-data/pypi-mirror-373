# AryadOCR

AryadOCR est un module Python performant pour l'entraînement d'un modèle OCR basé sur PyTorch. 
Il est conçu pour la reconnaissance de caractères à partir de datasets fusionnés, 
avec une prise en charge du CTC Loss pour les séquences de longueur variable.

---

## Installation

Assurez-vous d'avoir Python 3.8+ et PyTorch installé :

```bash
pip install torch torchvision
pip install aryadocr
```

Installez les dépendances supplémentaires si nécessaire :

```bash
pip install numpy tqdm
```

---

## Fonctionnalités principales

- Chargement flexible des datasets (`load_set`, `dataset_merged`)
- Filtrage avancé par motifs (`filter_by_patterns`)
- Création automatique de vocabulaire pour le CTC
- Gestion des séquences via `AryadCollator`
- Modèle `AryadOcr` entraînable avec PyTorch
- Support complet pour entraînement et validation

---

## Chargement et fusion des datasets

1. `load_set(name_set : str)`  
   Charge un dataset spécifique par nom :

```python
from aryadocr.dataset import load_set

dataset_a = load_set("set_a")
dataset_b = load_set("set_b")
```

2. `dataset_merged(list_set : list)`  
   Fusionne plusieurs datasets en un seul objet :

```python
from aryadocr.dataset import dataset_merged

merged_dataset = dataset_merged(["set_a", "set_b", "set_c"])
```

3. `filter_by_patterns(dataset, patterns)`  
   Filtre le dataset selon des motifs présents dans les phonèmes :

```python
from aryadocr.dataset import filter_by_patterns

patterns = ['1', '2', 'llL']
filtered_dataset = filter_by_patterns(merged_dataset, patterns)
```

---

## Création du vocabulaire OCR

Le vocabulaire est généré automatiquement à partir des phonèmes filtrés :

```python
vocabOcrArabic = {
    v: k for k, v in enumerate(
        ['<BLANK>'] +
        list(set([token for phoneme in filtered_dataset['phonemes'] for token in phoneme.split('|')])) +
        ['<PAD>']
    )
}
num_classes = len(vocabOcrArabic)
```

- `<BLANK>` : utilisé pour le CTC Loss  
- `<PAD>` : padding pour séquences de différentes longueurs  

---

## Préparation des DataLoaders

Le collator gère les séquences de longueurs différentes et les transforme en tenseurs compatibles avec le CTC :

```python
from aryadocr.dataset import AryadCollator
from torch.utils.data import DataLoader

collator = AryadCollator(vocabOcrArabic=vocabOcrArabic)

train_loader = DataLoader(filtered_dataset, batch_size=4, shuffle=True, collate_fn=collator)
val_loader = DataLoader(filtered_dataset, batch_size=4, shuffle=False, collate_fn=collator)
```

---

## Initialisation et entraînement du modèle

```python
from aryadocr.model import AryadOcr

ocr_model = AryadOcr(vocabOcrArabic=vocabOcrArabic)
ocr_model.fit(train_loader)
```

Le modèle utilise le **CTC Loss** pour reconnaître des séquences de phonèmes et caractères.

---

## Bonnes pratiques

- Vérifiez que vos datasets contiennent la colonne `phonemes`.  
- Utilisez `filter_by_patterns` pour exclure les séquences non désirées.  
- Assurez-vous que le vocabulaire contient `<BLANK>` et `<PAD>` avant l’entraînement.  
- Ajustez le **batch size** selon la capacité GPU pour un entraînement optimal.  

---

## Exemple complet

```python
from aryadocr.dataset import dataset_merged, load_set, filter_by_patterns, AryadCollator
from torch.utils.data import DataLoader
from aryadocr.model import AryadOcr

patterns = ['1', '2', 'llL']
set_abc = filter_by_patterns(dataset_merged(["set_a", "set_b", "set_c"]), patterns)
set_d = filter_by_patterns(load_set("set_d"), patterns)

vocabOcrArabic = {
    v:k for k,v in enumerate(
        ['<BLANK>'] + 
        list(set([token for phoneme in set_abc['phonemes'] for token in phoneme.split('|')])) + 
        ['<PAD>']
    )
}

ocr_model = AryadOcr(vocabOcrArabic)
collator = AryadCollator(vocabOcrArabic=vocabOcrArabic)
train_loader = DataLoader(set_abc, batch_size=4, shuffle=True, collate_fn=collator)
val_loader = DataLoader(set_d, batch_size=4, shuffle=False, collate_fn=collator)

ocr_model.fit(train_loader)

#Evaluation du modèle entrainé
ocr_model.evaluate(val_loader)
```

## Chargement d’un modèle et vocabulaire pour évaluation
```python
import torch, json
from aryadocr.model import AryadOcr

# 1. Charger le vocabulaire
with open("vocabOcr.json", "r", encoding="utf-8") as f:
    vocabOcr = json.load(f)

# 2. Recréer le modèle
model = AryadOcr(vocabOcr=vocabOcr)

# 3. Charger le checkpoint
model.load_model("best_model.pt")

# 4. Évaluer
model.evaluate(val_loader)

# 5. Prédiction
pred = model.predict(img)
print(pred)
model.close()
```
## Comment Augmenter cette donnée
```python
from aryadocr.dataset import dataset_merged, load_set, filter_by_patterns,build_augmented_dataset
from datasets import concatenate_datasets

patterns = ['1', '2', 'llL']
set_abc = filter_by_patterns(dataset_merged(["set_a", "set_b", "set_c"]), patterns)

# 3 augmentation aléatoire par sample
dataset_aug = build_augmented_dataset(set_abc, n_times=3)

# Concaténer original + augmenté
data_train = concatenate_datasets([set_abc,dataset_aug])

print(data_train)
print("Taille finale :", data_train.num_rows)
```
---

## License

AryadOCR est publié sous licence **MIT**.  

---

## Support

Pour tout problème ou suggestion, merci de nous contacter : aryadacademie@gmail.com
