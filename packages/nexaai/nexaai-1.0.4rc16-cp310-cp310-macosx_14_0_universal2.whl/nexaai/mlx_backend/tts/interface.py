from typing import Any, List, Optional, Sequence
import argparse
import sys
import os
import glob
import tempfile
import time
import soundfile as sf
import mlx.core as mx
import numpy as np

from ml import TTS, TTSConfig, TTSResult, TTSSamplerConfig, Path as MLPath
from mlx_audio.tts.utils import load_model

from profiling import ProfilingMixin, StopReason

class MlxTts(TTS, ProfilingMixin):
    """MLX Audio implementation of TTS interface."""
    
    def __init__(
        self,
        model_path: MLPath,
        vocoder_path: MLPath,
        device: Optional[str] = None,
    ) -> None:
        ProfilingMixin.__init__(self)
        
        if os.path.isfile(model_path):
            model_path = os.path.dirname(model_path)
        
        # vocoder_path is not used in MLX TTS since the vocoder is integrated
        super().__init__(model_path, vocoder_path, device)
        self._sampler_config = TTSSamplerConfig()
        self.model = None
        self._model_loaded = False
        
        # Load model during initialization (matching C API behavior)
        self._load_model()
        
    def _load_model(self) -> bool:
        """Load the TTS model."""
        try:
            self.model = load_model(self.model_path)
            self._model_loaded = True
            return True
        except Exception as e:
            print(f"Failed to load TTS model: {e}")
            return False
        
    def destroy(self) -> None:
        """Destroy the model and free resources."""
        if self.model is not None:
            del self.model
            self.model = None
            mx.clear_cache()
        self._model_loaded = False
        
    def synthesize(
        self,
        text: str,
        config: Optional[TTSConfig] = None,
        output_path: Optional[MLPath] = None,
        clear_cache: bool = True,
    ) -> TTSResult:
        """Synthesize speech from text and save to filesystem."""
        # Ensure model is loaded
        if not self._model_loaded or self.model is None:
            raise RuntimeError("TTS model not loaded")
        
        # Start profiling
        self._start_profiling()
        self._prompt_start()
        
        try:
            # Use default config if not provided
            if config is None:
                config = TTSConfig()
            
            # Generate output path if not provided
            if output_path is None:
                timestamp = int(time.time() * 1000)
                output_path = os.path.join(tempfile.gettempdir(), f"tts_output_{timestamp}.wav")
            
            # Resolve voice path for Kokoro models
            voice = config.voice
            if voice and not voice.endswith(".pt") and not os.path.isabs(voice):
                # For relative voice names like "af_heart", construct full path
                voice_path = os.path.join(self.model_path, "voices", f"{voice}.pt")
                if os.path.exists(voice_path):
                    voice = voice_path
            
            # End prompt processing, start decode
            self._prompt_end()
            self._decode_start()
            
            results = self.model.generate(
                text=text,
                voice=voice,
                speed=config.speed,
                temperature=self._sampler_config.temperature,
                seed=config.seed if config.seed != -1 else None,
                verbose=False,
                stream=False,
                join_audio=True,
            )
            
            # Get the results (should be a generator)
            audio_list = []
            sample_rate = None
            for result in results:
                audio_list.append(result.audio)
                sample_rate = result.sample_rate
                
            if not audio_list:
                raise RuntimeError("No audio generated")
            
            # Concatenate audio if multiple chunks
            if len(audio_list) > 1:
                audio = mx.concatenate(audio_list, axis=0)
            else:
                audio = audio_list[0]
                
            # Convert MLX array to numpy for saving
            if isinstance(audio, mx.array):
                audio_np = np.array(audio)
                
            else:
                audio_np = audio
                
            # Save audio to file
            sf.write(output_path, audio_np, sample_rate)

            if clear_cache:
                mx.clear_cache()
            
            # Calculate metadata
            channels = 1 if len(audio_np.shape) == 1 else audio_np.shape[1]
            num_samples = len(audio_np)
            duration_seconds = num_samples / sample_rate
            
            # End decode and profiling
            self._decode_end()
            self._set_stop_reason(StopReason.ML_STOP_REASON_COMPLETED)
            self._end_profiling()
            
            return TTSResult(
                audio_path=output_path,
                duration_seconds=duration_seconds,
                sample_rate=sample_rate,
                channels=channels,
                num_samples=num_samples
            )
        except Exception as e:
            # End profiling on error
            self._end_profiling()
            raise e
        

        
    def list_available_voices(self) -> List[str]:
        """List available voices."""
        # Common MLX TTS voice names - this could be enhanced to discover voices dynamically
        default_voices = [
            "af_heart", "af_bella", "af_nicole", "af_sarah", "af_sky", "af_sunshine",
            "am_adam", "am_michael", "am_mead", "an_nova", "an_michael",
            "bf_emma", "bf_isabella", "bm_george", "bm_lewis"
        ]
        
        # Try to discover voices from model directory if available
        if self.model_path and os.path.exists(self.model_path):
            discovered_voices = []
            voice_patterns = [
                "*.pt",  # Voice files in model root
                "voices/*.pt",  # Voice files in voices subdirectory
            ]
            
            for pattern in voice_patterns:
                voice_files = glob.glob(os.path.join(self.model_path, pattern))
                for voice_file in voice_files:
                    voice_name = os.path.splitext(os.path.basename(voice_file))[0]
                    discovered_voices.append(voice_name)
            
            if discovered_voices:
                return discovered_voices
        
        return default_voices





def main():
    """Main function for command line text-to-speech synthesis."""
    parser = argparse.ArgumentParser(description="Synthesize speech using MLX TTS")
    parser.add_argument("model_path", help="Path to the TTS model")
    parser.add_argument("text", help="Text to synthesize")
    parser.add_argument("--voice", "-v", default="af_heart", help="Voice to use (default: af_heart)")
    parser.add_argument("--speed", "-s", type=float, default=1.0, help="Speech speed (default: 1.0)")
    parser.add_argument("--output", "-o", default="output.wav", help="Output audio file (default: output.wav)")
    parser.add_argument("--sample-rate", "-sr", type=int, default=24000, help="Sample rate (default: 24000)")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature for sampling (default: 0.7)")
    parser.add_argument("--seed", type=int, default=-1, help="Random seed (-1 for random)")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    
    args = parser.parse_args()
    
    # Check if model path exists
    if not os.path.exists(args.model_path):
        print(f"Error: Model path does not exist: {args.model_path}")
        sys.exit(1)
    
    # Initialize TTS adapter
    print(f"Initializing TTS with model: {args.model_path}")
    try:
        tts = MlxTts(
            model_path=args.model_path,
            vocoder_path="",  # Not used in MLX TTS
            device=None
        )
        
        print("TTS model loaded successfully")
        
        # List voices if requested
        if args.list_voices:
            voices = tts.list_available_voices()
            print(f"Available voices: {', '.join(voices)}")
            return
        
    except Exception as e:
        print(f"Error initializing TTS: {e}")
        sys.exit(1)
    
    # Set up synthesis config
    sampler_config = TTSSamplerConfig(
        temperature=args.temperature,
        noise_scale=0.667,
        length_scale=1.0
    )
    tts._sampler_config = sampler_config
    
    config = TTSConfig(
        voice=args.voice,
        speed=args.speed,
        seed=args.seed,
        sample_rate=args.sample_rate
    )
    
    # Synthesize speech
    print(f"Synthesizing text: '{args.text}'")
    print(f"Using voice: {args.voice}")
    print(f"Speed: {args.speed}x")
    print("-" * 50)
    
    try:
        result = tts.synthesize(args.text, config, args.output)
        
        # Print results
        print("Synthesis Results:")
        print("=" * 50)
        print(f"Audio generated:")
        print(f"  Duration: {result.duration_seconds:.2f} seconds")
        print(f"  Sample rate: {result.sample_rate} Hz")
        print(f"  Channels: {result.channels}")
        print(f"  Samples: {result.num_samples}")
        print(f"✅ Audio saved to: {result.audio_path}")
        
    except Exception as e:
        print(f"Error during synthesis: {e}")
        sys.exit(1)
    finally:
        # Clean up
        tts.destroy()


if __name__ == "__main__":
    main()
