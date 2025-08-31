import numpy as np
import pytest

from lrdbench.analysis.spectral.periodogram.periodogram_estimator import PeriodogramEstimator
from lrdbench.analysis.spectral.whittle.whittle_estimator import WhittleEstimator
from lrdbench.analysis.spectral.gph.gph_estimator import GPHEstimator
from lrdbench.models.data_models.fbm.fbm_model import FractionalBrownianMotion
from lrdbench.models.data_models.fgn.fgn_model import FractionalGaussianNoise


def generate_fgn_from_fbm(H: float, n: int, seed: int = 123) -> np.ndarray:
    # Use FractionalGaussianNoise directly instead of fBm differences
    fgn = FractionalGaussianNoise(H=H)
    return fgn.generate(n, seed=seed)


def test_periodogram_basic():
    data = generate_fgn_from_fbm(0.7, 2048)
    est = PeriodogramEstimator(max_freq_ratio=0.1)
    res = est.estimate(data)
    assert "hurst_parameter" in res
    assert np.isfinite(res["hurst_parameter"]) and 0.0 < res["hurst_parameter"] < 1.5


def test_whittle_basic():
    data = generate_fgn_from_fbm(0.6, 2048)
    est = WhittleEstimator()
    res = est.estimate(data)
    assert "hurst_parameter" in res and "d_parameter" in res
    assert np.isfinite(res["d_parameter"]) and -0.5 <= res["d_parameter"] <= 0.5


def test_gph_basic():
    data = generate_fgn_from_fbm(0.55, 2048)
    est = GPHEstimator(max_freq_ratio=0.1)
    res = est.estimate(data)
    assert "hurst_parameter" in res and "d_parameter" in res
    assert np.isfinite(res["hurst_parameter"]) and 0.0 < res["hurst_parameter"] < 1.5


def test_invalid_params():
    with pytest.raises(ValueError):
        PeriodogramEstimator(min_freq_ratio=0.0).estimate(np.random.randn(128))
    with pytest.raises(ValueError):
        GPHEstimator(max_freq_ratio=0.9).estimate(np.random.randn(128))




