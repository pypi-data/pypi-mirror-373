import editdistance
import numpy as np
def metric(gt,pred):
    correct_chars = len(gt) - editdistance.eval(pred, gt)
    return correct_chars / len(gt)

def general_car(all_ref,all_hyp):
    all_scores = []
    for ref,hyp in zip(all_ref,all_hyp):
        all_scores.append(metric(ref,hyp))
    return np.mean(all_scores)

def general_war(all_ref,all_hyp):
    return metric(all_ref,all_hyp)