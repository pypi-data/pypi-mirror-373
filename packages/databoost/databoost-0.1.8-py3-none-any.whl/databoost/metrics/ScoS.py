import numpy as np

def ScoS(y_true, y_pred, method="linear"):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    diff = np.abs(y_true - y_pred)

    if method == "linear":
        weighted = diff
    elif method == "quadratic":
        weighted = diff**2
    elif method == "log":
        weighted = np.log2(diff)
    
    score = weighted.mean()
    
    return score
