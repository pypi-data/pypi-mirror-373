"""
Bark Text-to-Speech Tool

Generate realistic speech using Suno's Bark model with support for:
- Multilingual speech generation
- Nonverbal communications (laughing, sighing, crying)
- Background noise and sound effects
- Natural conversational speech patterns

Bark is faster and more stable than DIA while still providing high-quality output.
"""

import os
import uuid
import subprocess
import sys
import importlib
from typing import Optional, Dict, Any
from strands import tool


def _ensure_dependencies() -> tuple[bool, str]:
    """
    Ensure all required dependencies are installed.
    Returns (success: bool, message: str)
    """
    required_packages = [
        ("transformers", "transformers>=4.31.0"),
        ("scipy", "scipy"),
        ("torch", "torch>=2.0.0"),
        ("torchaudio", "torchaudio>=2.0.0"),
        ("numpy", "numpy"),
        ("soundfile", "soundfile"),
    ]

    missing_packages = []

    # Check each package
    for package_name, install_name in required_packages:
        try:
            importlib.import_module(package_name)
        except ImportError:
            missing_packages.append(install_name)

    if missing_packages:
        print(f"🔄 Installing missing dependencies: {', '.join(missing_packages)}")

        try:
            # Install missing packages
            for i, package in enumerate(missing_packages, 1):
                print(f"📦 [{i}/{len(missing_packages)}] Installing {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )

                if result.returncode != 0:
                    error_msg = (
                        f"Failed to install {package}\nError: {result.stderr[:500]}..."
                    )
                    return False, error_msg

        except subprocess.TimeoutExpired:
            return (
                False,
                "Installation timeout - packages are large, try manual installation",
            )
        except Exception as e:
            return False, f"Installation error: {str(e)}"

        print("✅ All dependencies installed successfully!")

    return True, "Dependencies ready"


def _test_bark_import() -> tuple[bool, str]:
    """Test if Bark can be imported and used."""
    try:
        from transformers import pipeline

        # Try to load the pipeline (this will download model if needed)
        print("🔄 Loading Bark model (first run may download ~2GB)...")
        synthesizer = pipeline("text-to-speech", "suno/bark")
        return True, "Bark loaded successfully"
    except Exception as e:
        error_msg = f"Bark import/load failed: {str(e)[:200]}..."
        return False, error_msg


@tool
def speak_bark(
    text: str,
    output_path: Optional[str] = None,
    play_audio: bool = True,
    voice_preset: Optional[str] = None,
    do_sample: bool = True,
    temperature: float = 1.0,
    max_length: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate speech using Suno's Bark model.

    Args:
        text: Text to convert to speech. Supports special tokens like [laughs], [sighs], etc.
        output_path: Path to save audio file. If None, saves to .speak/bark_output_{uuid}.wav
        play_audio: Whether to play the audio after generation
        voice_preset: Voice preset to use (e.g., "v2/en_speaker_0", "v2/en_speaker_1", etc.)
        do_sample: Whether to use sampling during generation
        temperature: Sampling temperature (higher = more random)
        max_length: Maximum sequence length for generation

    Returns:
        Dict with status and details

    Special tokens supported by Bark:
        [laughter], [laughs], [sighs], [music], [gasps], [clears throat], etc.

    Examples:
        speak_bark("Hello! [laughs] This is amazing!")
        speak_bark("I'm feeling great today [sighs] but also tired.")
    """

    # 1. Ensure dependencies
    deps_success, deps_msg = _ensure_dependencies()
    if not deps_success:
        return {
            "status": "error",
            "content": [{"text": f"❌ Dependency installation failed: {deps_msg}"}],
        }

    # 2. Test Bark import
    bark_success, bark_msg = _test_bark_import()
    if not bark_success:
        return {
            "status": "error",
            "content": [{"text": f"❌ Bark model loading failed: {bark_msg}"}],
        }

    try:
        # Import after ensuring dependencies
        from transformers import pipeline
        import torch

        # 3. Setup output path
        if output_path is None:
            os.makedirs(".speak", exist_ok=True)
            output_path = f".speak/bark_output_{uuid.uuid4().hex[:8]}.wav"
        else:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 4. Load Bark model
        print("🎙️ Generating speech with Bark...")

        # Setup forward parameters
        forward_params = {
            "do_sample": do_sample,
            "temperature": temperature,
        }

        if max_length:
            forward_params["max_length"] = max_length

        if voice_preset:
            forward_params["voice_preset"] = voice_preset

        # Create the TTS pipeline
        synthesizer = pipeline(
            "text-to-speech",
            "suno/bark",
            device=0 if torch.cuda.is_available() else -1,  # Use GPU if available
        )

        # 5. Generate speech
        print(f"🔄 Processing: {text[:50]}{'...' if len(text) > 50 else ''}")

        speech_result = synthesizer(text, forward_params=forward_params)

        # 6. Save audio file (using soundfile for better format handling)
        import numpy as np
        import soundfile as sf

        # Get audio data and sampling rate
        audio_data = speech_result["audio"]
        sample_rate = speech_result["sampling_rate"]

        # Ensure audio is in the right format
        if isinstance(audio_data, torch.Tensor):
            audio_data = audio_data.cpu().numpy()

        # Flatten if needed (Bark sometimes returns multi-dimensional arrays)
        if audio_data.ndim > 1:
            audio_data = audio_data.flatten()

        # Convert to float32 and normalize if needed
        audio_data = audio_data.astype(np.float32)
        if np.abs(audio_data).max() > 1.0:
            audio_data = audio_data / np.abs(audio_data).max()

        # Save using soundfile (handles formats automatically)
        sf.write(output_path, audio_data, sample_rate)

        # 7. Get file info
        file_size = os.path.getsize(output_path)
        duration = len(speech_result["audio"]) / speech_result["sampling_rate"]

        print(
            f"✅ Audio saved: {output_path} ({file_size/1024:.1f}KB, ~{duration:.1f}s)"
        )

        # 8. Play audio if requested
        if play_audio:
            try:
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["afplay", output_path], check=True)
                elif sys.platform.startswith("linux"):
                    subprocess.run(["aplay", output_path], check=True)
                else:
                    print("⚠️ Audio playback not supported on this platform")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️ Could not play audio - file saved successfully though")

        return {
            "status": "success",
            "content": [
                {
                    "text": (
                        f"🎯 **Bark speech generation complete!** ✅\n\n"
                        f"**📄 Text:** {text[:100]}{'...' if len(text) > 100 else ''}\n"
                        f"**🎵 Output:** {output_path}\n"
                        f"**📊 Details:** {file_size/1024:.1f}KB, ~{duration:.1f}s\n"
                        f"**⚙️ Settings:** Temperature {temperature}, Sampling {do_sample}\n"
                        f"**🔊 Playback:** {'✅' if play_audio else '❌'}\n\n"
                        f"**🎭 Bark Features:**\n"
                        f"- Supports [laughs], [sighs], [music], [gasps], etc.\n"
                        f"- Multilingual speech generation\n"
                        f"- Natural conversational patterns\n"
                        f"- Background noise and sound effects"
                    )
                }
            ],
        }

    except Exception as e:
        error_details = str(e)

        # Check for common issues
        if "CUDA out of memory" in error_details:
            suggestion = "Try using CPU: set CUDA_VISIBLE_DEVICES='' or restart Python"
        elif "model" in error_details.lower() and "download" in error_details.lower():
            suggestion = "Model download interrupted - check internet connection"
        elif "scipy" in error_details.lower():
            suggestion = "Try: pip install --upgrade scipy"
        else:
            suggestion = "Check the error details above for clues"

        return {
            "status": "error",
            "content": [
                {
                    "text": (
                        f"❌ **Bark speech generation failed**\n\n"
                        f"**Error:** {error_details[:300]}{'...' if len(error_details) > 300 else ''}\n\n"
                        f"**Suggestion:** {suggestion}\n\n"
                        f"**Alternative:** Use the regular `speak` tool for basic TTS"
                    )
                }
            ],
        }


def speak_bark_batch(
    texts: list[str],
    output_dir: Optional[str] = None,
    voice_preset: Optional[str] = None,
    **generation_params,
) -> Dict[str, Any]:
    """
    Generate speech for multiple texts in batch.

    Args:
        texts: List of texts to convert to speech
        output_dir: Directory to save all audio files
        voice_preset: Voice preset to use for all generations
        **generation_params: Additional parameters to pass to speak_bark

    Returns:
        Dict with batch processing results
    """

    if output_dir is None:
        output_dir = ".speak/batch"

    os.makedirs(output_dir, exist_ok=True)

    results = []
    successful = 0
    failed = 0

    print(f"🎙️ **Bark Batch Processing:** {len(texts)} texts")

    for i, text in enumerate(texts, 1):
        print(
            f"\n📄 [{i}/{len(texts)}] Processing: {text[:50]}{'...' if len(text) > 50 else ''}"
        )

        output_path = os.path.join(
            output_dir, f"bark_batch_{i:03d}_{uuid.uuid4().hex[:6]}.wav"
        )

        result = speak_bark(
            text=text,
            output_path=output_path,
            play_audio=False,  # Don't play during batch
            voice_preset=voice_preset,
            **generation_params,
        )

        results.append({"text": text, "output_path": output_path, "result": result})

        if result["status"] == "success":
            successful += 1
        else:
            failed += 1

    summary = (
        f"🎯 **Bark Batch Complete!**\n\n"
        f"**📊 Results:** {successful} successful, {failed} failed\n"
        f"**📁 Output:** {output_dir}\n"
        f"**🎵 Total files:** {successful} audio files generated"
    )

    return {"status": "success", "content": [{"text": summary}], "results": results}


# Tool metadata for registration
__all__ = ["speak_bark", "speak_bark_batch"]
