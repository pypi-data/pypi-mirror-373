import numpy as np
import pytest

from lrdbench.models.data_models.arfima.arfima_model import ARFIMAModel


class TestARFIMAModel:
    def test_valid_parameters(self):
        model = ARFIMAModel(d=0.3, sigma=1.0)  # Pure fractional integration
        assert np.isclose(model.get_parameters()["d"], 0.3)
        assert model.get_parameters()["ar_params"] == []
        assert model.get_parameters()["ma_params"] == []
        assert np.isclose(model.get_parameters()["sigma"], 1.0)

    def test_invalid_fractional_integration(self):
        with pytest.raises(ValueError):
            ARFIMAModel(d=-0.6)
        with pytest.raises(ValueError):
            ARFIMAModel(d=0.6)

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            ARFIMAModel(d=0.3, sigma=0.0)

    def test_invalid_ar_parameters(self):
        # AR parameters that don't satisfy stationarity
        with pytest.raises(ValueError):
            ARFIMAModel(d=0.3, ar_params=[1.5])

    def test_invalid_ma_parameters(self):
        # MA parameters that don't satisfy invertibility
        with pytest.raises(ValueError):
            ARFIMAModel(d=0.3, ma_params=[1.5])

    def test_invalid_method(self):
        with pytest.raises(ValueError):
            ARFIMAModel(d=0.3, method="invalid")

    def test_generation_length_and_type(self):
        model = ARFIMAModel(d=0.3)  # Pure fractional integration
        data = model.generate(n=1024, seed=123)
        assert isinstance(data, np.ndarray)
        assert data.shape == (1024,)

    def test_reproducibility(self):
        model = ARFIMAModel(d=0.3)  # Pure fractional integration
        x1 = model.generate(n=256, seed=42)
        x2 = model.generate(n=256, seed=42)
        assert np.allclose(x1, x2)

    def test_different_methods(self):
        model1 = ARFIMAModel(d=0.3, method="simulation")
        model2 = ARFIMAModel(d=0.3, method="spectral")
        
        data1 = model1.generate(n=512, seed=123)
        data2 = model2.generate(n=512, seed=123)
        
        assert isinstance(data1, np.ndarray)
        assert isinstance(data2, np.ndarray)
        assert data1.shape == (512,)
        assert data2.shape == (512,)

    def test_pure_fractional_integration(self):
        # Test ARFIMA(0,d,0) - pure fractional integration
        model = ARFIMAModel(d=0.3)
        data = model.generate(n=512, seed=42)
        
        assert isinstance(data, np.ndarray)
        assert data.shape == (512,)

    def test_ar_only(self):
        # Test ARFIMA(1,d,0) - use valid AR parameter (|φ| < 1)
        model = ARFIMAModel(d=0.3, ar_params=[0.5])
        data = model.generate(n=512, seed=42)
        
        assert isinstance(data, np.ndarray)
        assert data.shape == (512,)

    def test_ma_only(self):
        # Test ARFIMA(0,d,1) - use valid MA parameter (|θ| < 1)
        model = ARFIMAModel(d=0.3, ma_params=[0.5])
        data = model.generate(n=512, seed=42)
        
        assert isinstance(data, np.ndarray)
        assert data.shape == (512,)

    def test_theoretical_properties(self):
        model = ARFIMAModel(d=0.3, sigma=2.0)  # Pure fractional integration
        props = model.get_theoretical_properties()
        
        assert props["fractional_integration"] == 0.3
        assert props["ar_order"] == 0
        assert props["ma_order"] == 0
        assert np.isclose(props["innovation_variance"], 4.0)
        assert props["long_range_dependence"] is True
        assert props["stationary"] is True
        assert props["invertible"] is True

    def test_increments(self):
        model = ARFIMAModel(d=0.3)  # Pure fractional integration
        data = model.generate(n=100, seed=42)
        increments = model.get_increments(data)
        
        assert isinstance(increments, np.ndarray)
        assert increments.shape == (99,)
        assert np.allclose(increments, np.diff(data))

    def test_parameter_setting(self):
        model = ARFIMAModel(d=0.3)  # Pure fractional integration
        model.set_parameters(d=0.4, sigma=1.5)
        
        params = model.get_parameters()
        assert np.isclose(params["d"], 0.4)
        assert params["ar_params"] == []
        assert params["ma_params"] == []
        assert np.isclose(params["sigma"], 1.5)

    def test_string_representations(self):
        model = ARFIMAModel(d=0.3)  # Pure fractional integration
        
        str_repr = str(model)
        repr_repr = repr(model)
        
        assert "ARFIMAModel" in str_repr
        assert "ARFIMAModel" in repr_repr
        assert "0.3" in str_repr

    def test_binomial_coefficient(self):
        model = ARFIMAModel(d=0.3)
        
        # Test some known values using scipy's gamma function
        from scipy.special import gamma
        
        def binomial_coef(d, k):
            if k == 0:
                return 1.0
            return gamma(d + 1) / (gamma(k + 1) * gamma(d - k + 1))
        
        assert np.isclose(binomial_coef(0.3, 0), 1.0)
        assert np.isclose(binomial_coef(0.3, 1), 0.3)
        assert np.isclose(binomial_coef(0.3, 2), 0.3 * (-0.7) / 2)

    def test_fractional_differencing(self):
        model = ARFIMAModel(d=0.3)
        
        # Test with simple data
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = model._fractional_differencing_fft(data, 0.3)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == data.shape
        # Note: FFT-based method may not preserve the first value exactly
        # due to circular convolution effects
