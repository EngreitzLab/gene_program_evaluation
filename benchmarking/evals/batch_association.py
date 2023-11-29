import os
import argparse

from scipy import stats, sparse
from joblib import Parallel, delayed
from tqdm.auto import tqdm

def perform_kruskall_wallis(adata, prog_nam=None, batch_key=None):
    
    samples = []
    for batch in adata.obs[batch_key].astype(str).unique().values:
        sample_ = adata[adata.obs[batch_key]==batch, prog_nam].X[:,0]
        if sparse.issparse(sample_):
            sample_ = sample_.toarray().flatten()
        samples.append(sample_)
    
    stat, pval = stats.kruskall(*samples, nan_policy='propagate')
    
    mudata[prog_key].var.loc[prog_nam, 'kruskall_wallis_stat'] = stat
    mudata[prog_key].var.loc[prog_nam, 'kruskall_wallis_pval'] = pval

def compute_batch_association(mudata, batch_key=None, n_jobs=1,
	                          prog_key='prog', inplace=True):
    
    #TODO: Don't copy entire mudata only relevant Dataframe
    mudata = mudata.copy() if not inplace else mudata
    
    mudata[prog_key].var['kruskall_wallis_stat'] = None
    mudata[prog_key].var['kruskall_wallis_pval'] = None
    
    Parallel(n_jobs=n_jobs)(delayed(perform_kruskall_wallis)(mudata[prog_key], 
                                                             prog_nam=prog_nam, 
                                                             batch_key=batch_key) \
                                                             for prog_nam in tqdm(mudata[prog_key].var_names,
                                                             desc='Testing batch association', unit='programs'))

    if not inplace: return mudata[prog_key].var.loc[:, ['kruskall_wallis_stat', 
                                                        'kruskall_wallis_pval']]
	
if __name__=='__main__':
    parser = argparse.ArgumentParser()

        parser.add_argument('mudataObj')
        parser.add_argument('batch_key') 
        parser.add_argument('-n', '--n_jobs', default=1, typ=int)
        parser.add_argument('-pk', '--prog_key', default='prog', typ=str) 
        parser.add_argument('--output', action='store_false') 

        args = parser.parse_args()
    
        compute_batch_association(args.mudataObj, batch_key=args.batch_key, n_jobs=args.n_jobs
	                              prog_key=args.prog_key, inplace=args.output)


