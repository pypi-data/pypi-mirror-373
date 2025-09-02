"""
Realistic speech generation tool using DIA (Dia) model.

DIA is a 1.6B parameter text-to-dialogue model that generates highly realistic
speech with emotions, nonverbal communications, and voice cloning capabilities.
"""

import os
import torch
from typing import Optional, List
from pathlib import Path
import uuid
from strands import tool


@tool
def realistic_speak(
    text: str,
    output_path: Optional[str] = None,
    speaker_format: bool = True,
    voice_clone_audio: Optional[str] = None,
    voice_clone_transcript: Optional[str] = None,
    max_new_tokens: int = 3072,
    guidance_scale: float = 3.0,
    temperature: float = 1.8,
    top_p: float = 0.90,
    top_k: int = 45,
    device: Optional[str] = None,
    play_audio: bool = True,
) -> str:
    """
    Generate realistic speech using DIA model with emotions and nonverbal communications.

    DIA can generate dialogue with multiple speakers, emotions, and nonverbal cues like
    laughter, coughs, etc. It also supports voice cloning for consistent speaker identity.

    Args:
        text: Text to convert to speech. Use [S1] and [S2] for different speakers.
              Example: "[S1] Hello there! (laughs) [S2] How are you doing today?"
        output_path: Path to save the generated audio file. If None, saves to ./speech_output_{uuid}.wav
        speaker_format: If True, automatically ensures text starts with [S1] if no speaker tags present
        voice_clone_audio: Path to audio file for voice cloning (5-10 seconds recommended)
        voice_clone_transcript: Transcript of the voice cloning audio with proper speaker tags
        max_new_tokens: Maximum number of new tokens to generate (default: 3072)
        guidance_scale: Guidance scale for generation (default: 3.0)
        temperature: Sampling temperature (default: 1.8)
        top_p: Top-p sampling parameter (default: 0.90)
        top_k: Top-k sampling parameter (default: 45)
        device: Device to use ('cuda', 'cpu', 'mps'). If None, auto-detects best available
        play_audio: Whether to play the audio after generation (macOS/Linux only)

    Returns:
        String with generation status and output file path

    Supported nonverbal tags:
        (laughs), (clears throat), (sighs), (gasps), (coughs), (singing), (sings),
        (mumbles), (beep), (groans), (sniffs), (claps), (screams), (inhales),
        (exhales), (applause), (burps), (humming), (sneezes), (chuckle), (whistles)

    Examples:
        # Simple dialogue
        realistic_speak("[S1] Hello! How are you? [S2] I'm doing great, thanks! (laughs)")

        # Single speaker with emotion
        realistic_speak("[S1] This is amazing! (excited) I can't believe it works so well!")

        # Voice cloning
        realistic_speak(
            text="[S1] This is my cloned voice speaking!",
            voice_clone_audio="./reference_voice.wav",
            voice_clone_transcript="[S1] Hello, this is my reference voice."
        )
    """

    try:
        # Import required dependencies
        try:
            from transformers import AutoProcessor, DiaForConditionalGeneration
        except ImportError:
            return "❌ Error: transformers library not found. Please install with: pip install git+https://github.com/huggingface/transformers.git"

        # Auto-detect device if not specified
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

        print(f"🎤 Using device: {device}")

        # Format text with speaker tags if needed
        formatted_text = text
        if speaker_format and not ("[S1]" in text or "[S2]" in text):
            formatted_text = f"[S1] {text}"

        # Handle voice cloning
        if voice_clone_audio and voice_clone_transcript:
            # Combine transcript and generation text for voice cloning
            formatted_text = f"{voice_clone_transcript} {formatted_text}"
            print(f"🎭 Voice cloning enabled with audio: {voice_clone_audio}")

        print(f"📝 Formatted text: {formatted_text}")

        # Load model and processor
        print("🔄 Loading DIA model...")
        model_checkpoint = "nari-labs/Dia-1.6B-0626"

        processor = AutoProcessor.from_pretrained(model_checkpoint)
        model = DiaForConditionalGeneration.from_pretrained(model_checkpoint).to(device)

        # Prepare input
        inputs = processor(text=[formatted_text], padding=True, return_tensors="pt").to(
            device
        )

        # Handle audio input for voice cloning
        if voice_clone_audio and os.path.exists(voice_clone_audio):
            try:
                # Load audio for voice cloning
                import torchaudio

                audio, sample_rate = torchaudio.load(voice_clone_audio)

                # Resample if needed (DIA typically expects 24kHz)
                if sample_rate != 24000:
                    resampler = torchaudio.transforms.Resample(sample_rate, 24000)
                    audio = resampler(audio)

                # Add audio to inputs
                inputs["audio"] = audio.to(device)
                print(f"🎵 Loaded voice cloning audio: {voice_clone_audio}")

            except Exception as e:
                print(f"⚠️  Warning: Could not load voice cloning audio: {e}")

        # Generate audio
        print("🎯 Generating speech...")

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                guidance_scale=guidance_scale,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=True,
            )

        # Decode outputs
        outputs = processor.batch_decode(outputs)

        # Generate output path if not provided
        if output_path is None:
            output_dir = Path("./.speak")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"speech_{uuid.uuid4().hex[:8]}.wav"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save audio
        print(f"💾 Saving audio to: {output_path}")
        processor.save_audio(outputs, str(output_path))

        # Play audio if requested (macOS/Linux)
        if play_audio:
            try:
                if os.name == "posix":  # Unix-like systems
                    if os.system("which afplay > /dev/null 2>&1") == 0:  # macOS
                        os.system(f"afplay '{output_path}' &")
                        print("🔊 Playing audio (macOS)")
                    elif os.system("which aplay > /dev/null 2>&1") == 0:  # Linux
                        os.system(f"aplay '{output_path}' &")
                        print("🔊 Playing audio (Linux)")
                    else:
                        print("ℹ️  Audio saved but no player found for auto-play")
                else:
                    print("ℹ️  Auto-play not supported on this platform")
            except Exception as e:
                print(f"⚠️  Could not play audio: {e}")

        # Calculate approximate duration (rough estimate: 1 second ≈ 86 tokens)
        estimated_duration = len(formatted_text.split()) * 0.1  # Very rough estimate

        result = f"""✅ **Realistic speech generated successfully!**

📄 **Text:** {formatted_text[:100]}{'...' if len(formatted_text) > 100 else ''}
💾 **Output:** {output_path}
📏 **Size:** {output_path.stat().st_size / 1024:.1f} KB
⏱️  **Est. Duration:** ~{estimated_duration:.1f}s
🎛️  **Settings:** temp={temperature}, guidance={guidance_scale}, device={device}

🎭 **Supported features:**
• Multi-speaker dialogue with [S1] and [S2] tags
• Nonverbal cues: (laughs), (coughs), (sighs), etc.
• Voice cloning with reference audio
• Emotional expression and tone control"""

        return result

    except Exception as e:
        error_msg = f"❌ **Error generating realistic speech:** {str(e)}"

        # Provide helpful troubleshooting info
        if "CUDA" in str(e):
            error_msg += "\n\n🔧 **GPU Issue:** Try setting device='cpu' or check CUDA installation"
        elif "transformers" in str(e):
            error_msg += "\n\n🔧 **Dependencies:** Install with: pip install git+https://github.com/huggingface/transformers.git"
        elif "model" in str(e).lower():
            error_msg += "\n\n🔧 **Model Issue:** Model download may have failed. Check internet connection."

        return error_msg


# Additional helper function for batch processing
@tool
def realistic_speak_batch(
    texts: List[str],
    output_dir: Optional[str] = None,
    speaker_format: bool = True,
    **generation_params,
) -> str:
    """
    Generate realistic speech for multiple texts in batch.

    Args:
        texts: List of texts to convert to speech
        output_dir: Directory to save all generated audio files
        speaker_format: Whether to auto-format texts with speaker tags
        **generation_params: Additional parameters to pass to realistic_speak

    Returns:
        String with batch processing results
    """

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

    results = []
    successful = 0
    failed = 0

    for i, text in enumerate(texts):
        try:
            if output_dir:
                file_path = output_path / f"speech_batch_{i+1:03d}.wav"
            else:
                file_path = None

            result = realistic_speak(
                text=text,
                output_path=str(file_path) if file_path else None,
                speaker_format=speaker_format,
                play_audio=False,  # Don't play during batch processing
                **generation_params,
            )

            if result.startswith("✅"):
                successful += 1
                results.append(f"✅ Text {i+1}: Success")
            else:
                failed += 1
                results.append(f"❌ Text {i+1}: Failed")

        except Exception as e:
            failed += 1
            results.append(f"❌ Text {i+1}: {str(e)}")

    summary = f"""📊 **Batch Speech Generation Complete**

✅ **Successful:** {successful}/{len(texts)}
❌ **Failed:** {failed}/{len(texts)}
📁 **Output:** {output_dir if output_dir else './.speak'}

**Results:**
""" + "\n".join(
        results
    )

    return summary
