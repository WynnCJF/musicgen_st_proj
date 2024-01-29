import streamlit as st
import replicate
import concurrent.futures
import os
import urllib
import math
import librosa
import soundfile as sf


file_counter = 1

def call_replicate_api(text_prompt, length):
    """Call MusicGen's Replicate API with text_prompt."""
    global file_counter
    cur_file = file_counter
    file_counter += 1
    
    # Generate initial output
    output = replicate.run(
        "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
        input={
            "model_version": "melody",
            "prompt": text_prompt,
            "duration": length,
        }
    )
    
    # Seperate audio stems
    output_separate = replicate.run(
        "cjwbw/demucs:25a173108cff36ef9f80f854c162d01df9e6528be175794b81158fa03836d953",
        input={
            "audio": output
        }
    )
    
    # Load original output to local directory
    original_output_fn = f"output_{cur_file}.wav"
    urllib.request.urlretrieve(output, original_output_fn)
    
    # Load seperated stems to local directory
    for stem, source in output_separate.items():
        if source is None: continue
        
        stem_output_fn = f"output_{stem}_{cur_file}.wav"
        urllib.request.urlretrieve(source, stem_output_fn)
    
    # Beat tracking
    original_audio, sr = librosa.load(original_output_fn, sr=None)
    tempo, beat_frames = librosa.beat.beat_track(y=original_audio, sr=sr, trim=False)
    
    # Check if beat and tempo are corectly detected
    onbeat_sample = None
    if tempo != 0:
        beat_frames_time = librosa.frames_to_time(beat_frames, sr=sr)
        onbeat_sample = math.floor(beat_frames_time[0] * sr)
    else:
        onbeat_sample = 0
    
    # Save onbeat audio
    onbeat_audio = original_audio[onbeat_sample:]
    onbeat_output_fn = f"output_onbeat_{cur_file}.wav"
    sf.write(onbeat_output_fn, onbeat_audio, sr)
    
    # Save onbeat audio for stems
    onbeat_stem_filenames = {}
    for stem, source in output_separate.items():
        if source is None: continue
        
        stem_audio, sr = librosa.load(f"output_{stem}_{cur_file}.wav", sr=None)
        stem_output_fn = f"output_{stem}_onbeat_{cur_file}.wav"
        stem_onbeat_audio = stem_audio[onbeat_sample:]
        sf.write(stem_output_fn, stem_onbeat_audio, sr)
        
        onbeat_stem_filenames[stem] = stem_output_fn
    
    return original_output_fn, onbeat_output_fn, onbeat_stem_filenames


st.header("MusicGen Single-Instrument Experiment 🎵")

# Sidebar selection
with st.sidebar:
    st.markdown("## Select an input mode:")
    
    input_mode_options = (
        "Choose from a pre-defined prompt",
        "Customize text input",
    )
    
    input_mode_choice = st.radio(
        label="Input choice radio",
        label_visibility="collapsed",
        options=input_mode_options,
        key="input_mode_choice"
    )
    
    st.divider()
    
    num_output = st.slider(
        label="Number of generated outputs",
        min_value=1,
        max_value=5,
        value=3,
        step=1,
        key="num_output",
    )
    
    generate_length = st.slider(
        label="Duration of generated audio (seconds)",
        min_value=5,
        max_value=30,
        value=5,
        step=1,
        key="generate_length",
    )
    
# Prompt input
st.divider()

if st.session_state.input_mode_choice == "Customize text input":
    st.markdown("### Input your text prompt to MusicGen:")
    input_pmpt1 = st.text_input(
        label="Prompt",
        value="",
        key="pmpt1",
        label_visibility="collapsed",
        placeholder="Electric guitar solo, shoegaze, clean and clear recording quality, perfect for music production"
    )
else:
    st.markdown("### Choose a prompt:")
    pmpt_options = [
        # "Electric guitar solo, shoegaze, clean and clear recording quality, perfect for music production",
        # "Drum percussion solo, four-on-the-floor beat, tribal sound, traditional instrument, BPM: 125, clean and clear recording quality",
        # "Bell percussion solo, natural, organic, rhythmic, periodic, repetition, BPM: 125",
        # "Synth arpeggio, 80's retro, BPM: 95, solo performance",
        # "Piano solo, funky groove, chord progression, clean and clear recording quality, BPM: 128",
        # "Ambient pad, dark atmosphere, heavy reverb",
        "A reggae fusion track that blends traditional reggae rhythms with elements of modern electronic music",
        "A lively jazz fusion piece characterized by a complex, upbeat rhythm; saxophone for the main melody; electric guitar bassline",
        "A high-energy trance anthem with fast-paced rhythm; soaring synth leads; driving bassline; euphoric mood",
        "A tropical house track featuring steel drums, gentle flute melody, a deep bass and vocal chops",
    ]

    input_pmpt_choice = st.selectbox(
        label="Prompt selection",
        options=pmpt_options,
        key="input_pmpt_choice",
        index=None,
        label_visibility="collapsed",
    )

# Generate output
pmpt1_button = st.button("Generate Audio")
if pmpt1_button:
    if st.session_state.input_mode_choice == "Customize text input":
        prompt = st.session_state.pmpt1
    else:
        prompt = st.session_state.input_pmpt_choice
        
    st.markdown("### Output ⬇️")
    futures = []
    original_outputs = []
    output_success = 0
    with st.spinner("Waiting for audio to be generated..."):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for _ in range(int(st.session_state.num_output)):
                future = executor.submit(call_replicate_api, prompt, st.session_state.generate_length)
                futures.append(future)
                
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                original_audio_fn, onbeat_audio_fn, onbeat_stem_fns = future.result()
                
                st.caption("Audio output #{} generated".format(i + 1))
                st.write("**Original audio**")
                st.audio(original_audio_fn, format="audio/wav")
                
                st.write("**Onbeat audio**")
                st.audio(onbeat_audio_fn, format="audio/wav")
                
                for stem_name, stem_fn in onbeat_stem_fns.items():
                    st.write(f"*Onbeat {stem_name} audio*")
                    st.audio(stem_fn, format="audio/wav")
                                    
                output_success += 1
        