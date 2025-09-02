import numpy as np
from snp import SNP

def test_snp_runs():
    np.random.seed(0)
    x = np.linspace(0, 1, 200)
    y = np.sin(2*np.pi*x) + np.random.normal(0, 0.1, size=x.size)
    res = SNP(x, y)
    assert isinstance(res, dict)
    assert "y_k_opt" in res
    assert res["y_k_opt"].shape[0] == x.size
