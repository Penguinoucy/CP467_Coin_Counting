"""Maximum-cardinality one-to-one matching, then minimum total original-pixel distance."""
import numpy as np
from scipy.optimize import linear_sum_assignment

def match_coins(predicted_coins,labelled_coins):
    n,m=len(predicted_coins),len(labelled_coins)
    if not n or not m:return []
    pred=np.asarray([[c['x'],c['y']] for c in predicted_coins],dtype=float)
    truth=np.asarray([[c['x'],c['y']] for c in labelled_coins],dtype=float)
    distance=np.linalg.norm(pred[:,None,:]-truth[None,:,:],axis=2)
    allowed=distance<=0.5*np.asarray([c['radius'] for c in labelled_coins])[None,:]
    largest=float(distance[allowed].max()) if allowed.any() else 0.0
    # One unmatched penalty outweighs any total improvement in valid distances.
    unmatched=(max(n,m)+1)*(largest+1);forbidden=(n+m+1)*unmatched
    cost=np.full((n,m+n),unmatched);cost[:,:m]=np.where(allowed,distance,forbidden)
    rr,cc=linear_sum_assignment(cost)
    return [(int(i),int(j)) for i,j in zip(rr,cc) if j<m and allowed[i,j]]
