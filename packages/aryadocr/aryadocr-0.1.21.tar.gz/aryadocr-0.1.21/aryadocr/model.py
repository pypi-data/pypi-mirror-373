from .aryadcnn import AryadCNN
import torch
import torch.nn as nn
from .context_encoder import ContextEncoder
from .utils import DecoderCTC
from .metrics import general_car,general_war
import numpy as np
import os
from tqdm import tqdm
import json


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['XLA_FLAGS'] = '--xla_gpu_cuda_data_dir=/usr/local/cuda'
import tensorflow.compat.v1 as tf

tf.disable_v2_behavior()
tf.logging.set_verbosity(tf.logging.ERROR)




class AryadOcr(nn.Module):
    def __init__(self, vocabOcr: dict, input_size=(100, 300), lr0=1e-4, wandb_run=None):
        super().__init__()

        # --- Vocabs ---
        self.vocabOcr = vocabOcr
        self.blank_idx = self.vocabOcr["<BLANK>"]

        # --- Runtime / Backends ---
        self. sess = tf.Session(config=tf.ConfigProto(device_count={'GPU': 0}))
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(self.device)

        # --- Backbone ---
        self.AryadCNN = AryadCNN()
        # Déterminer input_dim
        dim_in = torch.randn(1, 1, *input_size)
        with torch.no_grad():
            dim_out = self.AryadCNN(dim_in)
        input_dim = dim_out.shape[-1]

        self.context_encoder = ContextEncoder(input_dim=input_dim)
        self.decoder = DecoderCTC(d_model=256, num_classes=len(self.vocabOcr))

        # --- Optimizer / Loss ---
        self.optimizer = torch.optim.Adam(self.parameters(), lr=lr0)
        self.ctc_loss = nn.CTCLoss(blank=self.blank_idx, zero_infinity=True)

        # --- Logger ---
        self.wandb_run = wandb_run

    def forward(self, x):
        x = self.AryadCNN(x)                  # (B, T, C)
        x = self.context_encoder(x)           # (B, T, D)
        x = self.decoder(x)                   # (B, T, C)
        return x.permute(1, 0, 2)             # (T, B, C)
    
    def close(self):
        if self.sess is not None:
            self.sess.close()
            self.sess = None

    def fit(self, train_loader, val_loader=None, epochs=10, use_beam=True, beam_width=10, early_stopping_patience=5):
        best_val_loss = float('inf')
        epochs_no_improve = 0
        for epoch in range(1, epochs + 1):
            # ----------------- TRAIN -----------------
            self.train()
            train_loss = 0.0
            pbar = tqdm(train_loader, desc=f"[Epoch {epoch}/{epochs}] Training")
            for batch in pbar:
                images = batch['pixel_values'].to(self.device)
                labels = batch['labels'].to(self.device)
                label_lengths = batch['label_lengths'].to(self.device)

                logits = self(images)                 # (T, B, C)
                log_probs = nn.functional.log_softmax(logits, dim=2)
                input_lengths = torch.full(
                    (log_probs.size(1),),
                    log_probs.size(0),
                    dtype=torch.long
                ).to(self.device)
                targets = torch.cat([labels[i, :l] for i, l in enumerate(label_lengths)])

                loss = self.ctc_loss(log_probs, targets, input_lengths, label_lengths)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                train_loss += loss.item()
                pbar.set_postfix(loss=loss.item())

                # --- Nettoyage mémoire ---
                del logits, log_probs, targets, input_lengths
                torch.cuda.empty_cache()

            avg_train_loss = train_loss / len(train_loader)

            # ----------------- VALIDATION -----------------
            avg_val_loss, avg_car, avg_war = None, None, None
            if val_loader is not None:
                self.eval()
                val_loss = 0.0
                with torch.no_grad():
                    for batch in tqdm(val_loader, desc=f"[Epoch {epoch}/{epochs}] Val"):
                        images = batch['pixel_values'].to(self.device)
                        labels = batch['labels'].to(self.device)
                        label_lengths = batch['label_lengths'].to(self.device)

                        logits = self(images)
                        log_probs = nn.functional.log_softmax(logits, dim=2)
                        input_lengths = torch.full(
                            (log_probs.size(1),),
                            log_probs.size(0),
                            dtype=torch.long
                        ).to(self.device)
                        targets = torch.cat([labels[i, :l] for i, l in enumerate(label_lengths)])
                        loss = self.ctc_loss(log_probs, targets, input_lengths, label_lengths)
                        val_loss += loss.item()

                        # --- Décodage et métriques ---
                        batch_predictions = self.ctc_beam_decode_torch_to_tf(log_probs,beam=use_beam, beam_width=beam_width)
                        batch_ground_truths = [
                            [list(self.vocabOcr)[idx] for idx in labels[i][:label_lengths[i]] if list(self.vocabOcr)[idx] not in ['<PAD>', '<BLANK>']]
                            for i in range(labels.size(0))
                        ]

                        preds = ["".join(word.split('|')) for word in batch_predictions]
                        gt = ["".join(ph) for ph in batch_ground_truths]

                        avg_car = general_car(gt,preds) if preds else 0.0
                        avg_war = general_war(gt,preds) if preds else 0.0

                        # --- Nettoyage mémoire ---
                        del logits, log_probs, targets, input_lengths
                        torch.cuda.empty_cache()

                    avg_val_loss = val_loss / max(1, len(val_loader))
                # ----------------- LOG -----------------
                msg = f"Epoch {epoch} | Train Loss: {avg_train_loss:.4f}"
                if val_loader is not None:
                    msg += f" | Val Loss: {avg_val_loss:.4f} | CAR: {avg_car:.4f} | WAR: {avg_war:.4f}"
                print(msg)
                print("GT:",gt,"PREDI:",preds)
                
            # --- Logging W&B ---
            if self.wandb_run and val_loader is not None:
                self.wandb_run.log({
                    "train_loss": avg_train_loss,
                    "val_loss": avg_val_loss,
                    "car": avg_car,
                    "war": avg_war,
                    "epoch": epoch
                })

            # ----------------- EARLY STOP -----------------
            if val_loader is not None:
                if avg_val_loss < best_val_loss:
                    best_val_loss = avg_val_loss
                    epochs_no_improve = 0
                    torch.save({
                        'epoch': epoch,
                        'model_state_dict': self.state_dict(),
                        'optimizer_state_dict': self.optimizer.state_dict(),
                        'val_loss': avg_val_loss
                    }, "best_model.pt")
                    # Sauvegarde du vocabulaire en JSON
                    with open("vocabOcr.json", "w", encoding="utf-8") as f:
                        json.dump(self.vocabOcr, f, ensure_ascii=False, indent=4)
                else:
                    epochs_no_improve += 1
                    if epochs_no_improve >= early_stopping_patience:
                        print(f"Early stopping triggered after {epoch} epochs.")
                        break
        # --- Après toutes les epochs ---
        self.close()


    def predict(self,image, beam=True, beam_width=10):
        if not isinstance(image, np.ndarray):
            image = np.array(image)
        image = np.expand_dims(np.expand_dims(image, axis=0), axis=0)
        image = torch.tensor(image, dtype=torch.float32).to(self.device)

        self.eval()
        with torch.no_grad():
            logits = self(image)
            log_probs = nn.functional.log_softmax(logits, dim=2)
            preds = self.ctc_beam_decode_torch_to_tf(log_probs,beam=beam, beam_width=beam_width)

            # Nettoyage mémoire
            del logits, log_probs
            torch.cuda.empty_cache()

        return preds

    def ctc_beam_decode_torch_to_tf(self, log_probs,beam=True, beam_width=10):
        preds_ = log_probs.cpu().detach().numpy().astype(np.float32)  # (T, B, C)
        input_lengths = [preds_.shape[0]] * preds_.shape[1]

        # Décodage
        if beam and beam_width > 1:
            decodes, _ = tf.nn.ctc_beam_search_decoder(
                inputs=preds_,
                sequence_length=input_lengths,
                beam_width=beam_width,
                merge_repeated=True
            )
        else:
            decodes, _ = tf.nn.ctc_greedy_decoder(
                inputs=preds_,
                sequence_length=input_lengths,
                merge_repeated=True
            )
         # Session locale
        dense_decoded = self. sess.run(tf.sparse.to_dense(decodes[0], default_value=-1))  # (B, max_len)
        decoded_strings = []
        for seq in dense_decoded:
            decoded_str = "".join(
                [list(self.vocabOcr)[idx] + "|" for idx in seq if idx != -1 and list(self.vocabOcr)[idx] not in ["<PAD>", "<BLANK>"]]
            )
            decoded_strings.append(decoded_str[:-1] if decoded_str else "")

        # Nettoyage
        del preds_, dense_decoded
        return decoded_strings

    def evaluate(self,val_loader,use_beam=True,beam_width=10):
        # ----------------- VALIDATION -----------------
        avg_val_loss, avg_car, avg_war = None, [], []
        self.eval()
        val_loss = 0.0

        with torch.no_grad():
            for batch in tqdm(val_loader):
                images = batch['pixel_values'].to(self.device)
                labels = batch['labels'].to(self.device)
                label_lengths = batch['label_lengths'].to(self.device)

                logits = self(images)
                log_probs = nn.functional.log_softmax(logits, dim=2)
                input_lengths = torch.full(
                    (log_probs.size(1),),
                    log_probs.size(0),
                    dtype=torch.long
                ).to(self.device)
                targets = torch.cat([labels[i, :l] for i, l in enumerate(label_lengths)])
                loss = self.ctc_loss(log_probs, targets, input_lengths, label_lengths)
                val_loss += loss.item()

                # --- Décodage et métriques ---
                batch_predictions = self.ctc_beam_decode_torch_to_tf(log_probs,beam=use_beam, beam_width=beam_width)
                batch_ground_truths = [
                    [list(self.vocabOcr)[idx] for idx in labels[i][:label_lengths[i]] if list(self.vocabOcr)[idx] not in ['<PAD>', '<BLANK>']]
                    for i in range(labels.size(0))
                ]

                preds = ["".join(word.split('|')) for word in batch_predictions]
                gt = ["".join(ph) for ph in batch_ground_truths]

                avg_car.append(general_car(gt,preds) if preds else 0.0)
                avg_war.append(general_war(gt,preds) if preds else 0.0)

                # --- Nettoyage mémoire ---
                del logits, log_probs, targets, input_lengths
                torch.cuda.empty_cache()

            avg_val_loss = val_loss / max(1, len(val_loader))
        # ----------------- LOG -----------------
        msg = f"Val Loss: {avg_val_loss:.4f} | CAR: {np.mean(avg_car):.4f} | WAR: {np.mean(avg_war):.4f}"
        print(msg)
        self.close()