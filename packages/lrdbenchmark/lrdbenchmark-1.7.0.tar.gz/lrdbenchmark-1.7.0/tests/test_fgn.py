import numpy as np
import pytest

from lrdbench.models.data_models.fgn.fgn_model import FractionalGaussianNoise


class TestFractionalGaussianNoise:
    def test_valid_parameters(self):
        model = FractionalGaussianNoise(H=0.7, sigma=1.0)
        assert np.isclose(model.get_parameters()["H"], 0.7)
        assert np.isclose(model.get_parameters()["sigma"], 1.0)

    def test_invalid_hurst_parameter(self):
        with pytest.raises(ValueError):
            FractionalGaussianNoise(H=-0.1)
        with pytest.raises(ValueError):
            FractionalGaussianNoise(H=1.0)

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            FractionalGaussianNoise(H=0.7, sigma=0.0)

    def test_generation_length_and_type(self):
        model = FractionalGaussianNoise(H=0.7, sigma=1.0)
        data = model.generate(n=1024, seed=123)
        assert isinstance(data, np.ndarray)
        assert data.shape == (1024,)

    def test_reproducibility(self):
        model = FractionalGaussianNoise(H=0.7, sigma=1.0)
        x1 = model.generate(n=256, seed=42)
        x2 = model.generate(n=256, seed=42)
        assert np.allclose(x1, x2)

    def test_theoretical_properties(self):
        model = FractionalGaussianNoise(H=0.7, sigma=2.0)
        props = model.get_theoretical_properties()
        assert props["hurst_parameter"] == 0.7
        assert np.isclose(props["variance"], 4.0)
        assert props["stationary"] is True



