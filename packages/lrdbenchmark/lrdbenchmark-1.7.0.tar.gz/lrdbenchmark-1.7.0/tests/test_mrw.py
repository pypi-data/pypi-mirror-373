import numpy as np
import pytest

from lrdbench.models.data_models.mrw.mrw_model import MultifractalRandomWalk


class TestMultifractalRandomWalk:
    def test_valid_parameters(self):
        model = MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=1.0)
        assert np.isclose(model.get_parameters()["H"], 0.7)
        assert np.isclose(model.get_parameters()["lambda_param"], 0.3)
        assert np.isclose(model.get_parameters()["sigma"], 1.0)

    def test_invalid_hurst_parameter(self):
        with pytest.raises(ValueError):
            MultifractalRandomWalk(H=-0.1, lambda_param=0.3)
        with pytest.raises(ValueError):
            MultifractalRandomWalk(H=1.0, lambda_param=0.3)

    def test_invalid_lambda_parameter(self):
        with pytest.raises(ValueError):
            MultifractalRandomWalk(H=0.7, lambda_param=0.0)
        with pytest.raises(ValueError):
            MultifractalRandomWalk(H=0.7, lambda_param=-0.1)

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=0.0)

    def test_invalid_method(self):
        with pytest.raises(ValueError):
            MultifractalRandomWalk(H=0.7, lambda_param=0.3, method="invalid")

    def test_generation_length_and_type(self):
        model = MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=1.0)
        data = model.generate(n=1024, seed=123)
        assert isinstance(data, np.ndarray)
        assert data.shape == (1024,)

    def test_reproducibility(self):
        model = MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=1.0)
        x1 = model.generate(n=256, seed=42)
        x2 = model.generate(n=256, seed=42)
        assert np.allclose(x1, x2)

    def test_different_methods(self):
        model1 = MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=1.0, method="cascade")
        model2 = MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=1.0, method="direct")
        
        data1 = model1.generate(n=512, seed=123)
        data2 = model2.generate(n=512, seed=123)
        
        assert isinstance(data1, np.ndarray)
        assert isinstance(data2, np.ndarray)
        assert data1.shape == (512,)
        assert data2.shape == (512,)

    def test_theoretical_properties(self):
        model = MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=2.0)
        props = model.get_theoretical_properties()
        
        assert props["hurst_parameter"] == 0.7
        assert props["intermittency_parameter"] == 0.3
        assert np.isclose(props["base_volatility"], 2.0)
        assert props["multifractal"] is True
        assert props["scale_invariant"] is True
        assert props["volatility_clustering"] is True

    def test_increments(self):
        model = MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=1.0)
        data = model.generate(n=100, seed=42)
        increments = model.get_increments(data)
        
        assert isinstance(increments, np.ndarray)
        assert increments.shape == (99,)
        assert np.allclose(increments, np.diff(data))

    def test_parameter_setting(self):
        model = MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=1.0)
        model.set_parameters(H=0.8, lambda_param=0.4, sigma=1.5)
        
        params = model.get_parameters()
        assert np.isclose(params["H"], 0.8)
        assert np.isclose(params["lambda_param"], 0.4)
        assert np.isclose(params["sigma"], 1.5)

    def test_string_representations(self):
        model = MultifractalRandomWalk(H=0.7, lambda_param=0.3, sigma=1.0)
        
        str_repr = str(model)
        repr_repr = repr(model)
        
        assert "MultifractalRandomWalk" in str_repr
        assert "MultifractalRandomWalk" in repr_repr
        assert "0.7" in str_repr
        assert "0.3" in str_repr
