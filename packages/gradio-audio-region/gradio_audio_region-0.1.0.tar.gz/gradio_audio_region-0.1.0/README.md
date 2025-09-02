# Gradio Audio Region

A custom Gradio component that extends `gr.Audio` to return region selection timing data along with audio data. This allows you to preserve original audio quality by applying the selected timing to your source files instead of using Gradio's processed audio.

## Features

- ✨ **Identical UI**: Same user experience as `gr.Audio` with editable regions
- 🎯 **Timing Data**: Returns `(audio_data, start_time, end_time)` tuple when regions are selected
- 🔊 **Preserve Quality**: Apply timing to your original audio files at native sample rates
- 📦 **Drop-in Replacement**: Minimal code changes from `gr.Audio`
- 🚀 **HF Spaces Ready**: Works seamlessly in HuggingFace Spaces

## Installation

```bash
pip install gradio-audio-region
```

## Quick Start

```python
import gradio as gr
from gradio_audio_region import AudioWithRegion

def process_audio_with_timing(audio_data):
    if isinstance(audio_data, tuple) and len(audio_data) == 3:
        audio_array, start_time, end_time = audio_data
        # Apply these timings to your original audio file
        return f"Selected region: {start_time:.2f}s to {end_time:.2f}s"
    
    return "Standard audio data received"

with gr.Blocks() as demo:
    audio = AudioWithRegion(
        label="Select audio region",
        type="numpy",
        interactive=True,
        editable=True  # Enables region selection
    )
    
    result = gr.Textbox(label="Timing Info")
    
    audio.change(
        process_audio_with_timing,
        inputs=audio,
        outputs=result
    )

demo.launch()
```

## Use Case: Preserve Original Audio Quality

This component is perfect when you need to trim audio while preserving the original sample rate and bit depth:

```python
import soundfile as sf
from gradio_audio_region import AudioWithRegion

# Store original file path
original_file_path = "path/to/original.wav"

def trim_original_audio(audio_data):
    if isinstance(audio_data, tuple) and len(audio_data) == 3:
        _, start_time, end_time = audio_data
        
        # Load original at native quality
        original_audio, original_sr = sf.read(original_file_path)
        
        # Apply timing to original
        start_sample = int(start_time * original_sr)
        end_sample = int(end_time * original_sr)
        trimmed_audio = original_audio[start_sample:end_sample]
        
        # Save trimmed version preserving original quality
        sf.write("trimmed_output.wav", trimmed_audio, original_sr)
        
        return f"Trimmed original audio: {start_time:.2f}s - {end_time:.2f}s"
    
    return "No region selected"
```

## API Reference

### AudioWithRegion

Extends `gradio.Audio` with identical parameters. The key difference is the return format:

**Standard mode** (no region selected):
- Returns: Same as `gr.Audio` (numpy array or file path)

**Region mode** (when user selects and trims a region):
- Returns: `(audio_data, start_time, end_time)` tuple
  - `audio_data`: Trimmed audio as numpy array or file path
  - `start_time`: Start time in seconds (float)
  - `end_time`: End time in seconds (float)

### Parameters

All parameters identical to `gradio.Audio`:

- `type`: `"numpy"` or `"filepath"`
- `interactive`: Set to `True` for editing
- `editable`: Set to `True` to enable region selection
- `waveform_options`: Configure waveform display
- And all other standard `gr.Audio` parameters

## HuggingFace Spaces Deployment

Add to your `requirements.txt`:

```
gradio
gradio-audio-region
```

Then use normally in your Space:

```python
from gradio_audio_region import AudioWithRegion
# ... rest of your code
```

## Development

```bash
# Clone and install in development mode
git clone https://github.com/jsaluja/gradio-audio-region
cd gradio-audio-region
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black gradio_audio_region tests
isort gradio_audio_region tests
```

## How It Works

This component leverages Gradio's existing audio editing UI (powered by WaveSurfer.js) but captures the timing data that normally gets lost. The frontend region selection is preserved while giving you access to precise start/end times for your own audio processing.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- 📧 Issues: [GitHub Issues](https://github.com/jsaluja/gradio-audio-region/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/jsaluja/gradio-audio-region/discussions)
