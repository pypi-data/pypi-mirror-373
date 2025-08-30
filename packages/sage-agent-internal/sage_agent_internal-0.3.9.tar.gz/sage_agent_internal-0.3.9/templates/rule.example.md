# EXAMPLE TEMPLATE FILE

# Description: 
When called, look into the requested function or codeblock and see if you find any parallelizale code. You can use the following embarringly parallel code template to speed up those function computations

# Code:
```python
from joblib import Parallel, delayed

def run_in_batches(fn_name):
    tickers = get_sp500_tickers()
    
    # Process in smaller batches to control memory usage
    results = Parallel(
        n_jobs=-1, 
        batch_size=10,  # Process 10 items per batch
        backend='multiprocessing'
    )(delayed(test_ticket)(ticker) for ticker in tickers)
    
    return dict(zip(tickers, results))
```