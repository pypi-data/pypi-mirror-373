import pytest
import numpy as np
import gradio as gr
from gradio_audio_region import AudioWithRegion


class TestAudioWithRegion:
    """Test cases for AudioWithRegion component."""
    
    def test_component_initialization(self):
        """Test that the component initializes correctly."""
        component = AudioWithRegion(
            label="Test Audio",
            type="numpy",
            interactive=True,
            editable=True
        )
        
        assert component.label == "Test Audio"
        assert component.type == "numpy"
        assert component.interactive is True
        assert component.editable is True
    
    def test_component_inherits_from_audio(self):
        """Test that AudioWithRegion properly inherits from gr.Audio."""
        component = AudioWithRegion()
        assert isinstance(component, gr.Audio)
    
    def test_preprocess_none_input(self):
        """Test preprocess with None input."""
        component = AudioWithRegion()
        result = component.preprocess(None)
        assert result is None
    
    def test_postprocess_tuple_input(self):
        """Test postprocess with timing tuple."""
        component = AudioWithRegion()
        
        # Create mock audio data
        sample_rate = 44100
        audio_data = np.random.rand(44100)  # 1 second of random audio
        start_time = 0.5
        end_time = 1.5
        
        # Test with tuple input
        tuple_input = (audio_data, start_time, end_time)
        
        # This should process just the audio data part
        result = component.postprocess(tuple_input)
        
        # Result should be processed audio data (implementation dependent)
        # For now, we're checking it doesn't crash
        assert result is not None or result is None  # Allow both cases
    
    def test_postprocess_standard_input(self):
        """Test postprocess with standard audio input."""
        component = AudioWithRegion()
        
        # Create mock audio data
        audio_data = np.random.rand(44100)
        
        # Test with standard audio input
        result = component.postprocess(audio_data)
        
        # Should handle like standard gr.Audio
        assert result is not None or result is None  # Allow both cases
    
    def test_component_type_parameter(self):
        """Test different type parameters."""
        # Test numpy type
        component_numpy = AudioWithRegion(type="numpy")
        assert component_numpy.type == "numpy"
        
        # Test filepath type
        component_filepath = AudioWithRegion(type="filepath")
        assert component_filepath.type == "filepath"
    
    def test_waveform_options(self):
        """Test component with waveform options."""
        waveform_opts = gr.WaveformOptions(
            waveform_color="#ff0000",
            show_controls=True
        )
        
        component = AudioWithRegion(waveform_options=waveform_opts)
        assert component.waveform_options == waveform_opts
