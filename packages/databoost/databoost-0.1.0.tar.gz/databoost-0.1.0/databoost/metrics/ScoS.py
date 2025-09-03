import numpy as np

def ScoS(y_true, y_pred, alpha=1, method="linear"):
    """
    Scolz's Score (ScoS)
    Penalizes more distant errors.
    
    Parameters:
    ----------
    y_true : array-like
        Array o lista dei valori reali
    y_pred : array-like
        Array o lista dei valori predetti
    alpha : float, optional
        Esponente che aumenta il peso degli errori più grandi (default=1)

    Returns:
    -------
    float
        ScoS score: più basso = migliore
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    diff = np.abs(y_true - y_pred)

    if method = "linear":
        weighted = diff * alpha
    elif method = "quadratic":
        weighted = diff**2 * alpha
    elif method = "log":
        weighted = np.log2(diff) * alpah
    
    # Media pesata
    score = weighted.mean()
    
    return score
