import streamlit as st
import replicate
import os
import concurrent.futures


def call_replicate_api(text_prompt, length):
    """Call MusicGen's Replicate API with text_prompt."""
    output = replicate.run(
        "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
        input={
            "model_version": "melody",
            "prompt": text_prompt,
            "duration": length,
        }
    )
    
    return output


st.header("MusicGen Single-Instrument Experiment 🎵")

# Load and set token
st.divider()

st.markdown("### Input your Replicate token:")

st.text_input(
    label="Token",
    value="",
    key="replicate_token",
    placeholder="Your Replicate Token",
    label_visibility="collapsed"
)

os.environ['REPLICATE_API_TOKEN'] = st.session_state.replicate_token 

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
        "Electric guitar solo, shoegaze, clean and clear recording quality, perfect for music production",
        "Drum percussion solo, four-on-the-floor beat, tribal sound, traditional instrument, BPM: 125, clean and clear recording quality",
        "Bell percussion solo, natural, organic, rhythmic, periodic, repetition, BPM: 125",
        "Synth arpeggio, 80's retro, BPM: 95, solo performance",
        "Piano solo, funky groove, chord progression, clean and clear recording quality, BPM: 128",
        "Ambient pad, dark atmosphere, heavy reverb",
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
    with st.spinner("Waiting for audio to be generated..."):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for _ in range(int(st.session_state.num_output)):
                future = executor.submit(call_replicate_api, prompt, st.session_state.generate_length)
                futures.append(future)
                
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                output = future.result()
                st.caption("Audio output #{}".format(i + 1))
                st.audio(output, format="audio/wav")
