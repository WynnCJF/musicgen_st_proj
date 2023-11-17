import streamlit as st
import replicate
import os
import concurrent.futures

OUTPUT_NUM = 3

def call_replicate_api(text_prompt):
    """Call MusicGen's Replicate API with text_prompt."""
    output = replicate.run(
        "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
        input={
            "model_version": "melody",
            "prompt": text_prompt,
            "duration": 5,
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
        "Customize text input",
        "Choose from a pre-defined prompt",
    )
    
    input_mode_choice = st.radio(
        label="Input choice radio",
        label_visibility="collapsed",
        options=input_mode_options,
        key="input_mode_choice"
    )
    
# Prompt input
st.divider()

if st.session_state.input_mode_choice == "Customize text input":
    st.markdown("### Input your text prompt to MusicGen:")
    input_pmpt1 = st.text_input(
        label="Prompt",
        value="Electric guitar solo, shoegaze, clean and clear recording quality, perfect for music production",
        key="pmpt1",
        label_visibility="collapsed",
    )
else:
    st.markdown("### Choose a prompt:")
    pmpt_options = [
        "Electric guitar solo, shoegaze, clean and clear recording quality, perfect for music production",
        "Drum percussion solo, four-on-the-floor beat, tribal sound, traditional instrument, BPM: 125, clean and clear recording quality",
        "Solo drum percussion with hi-hat, snare and kick drum",
        "Synthesizer arpeggio with 80's retro feeling",
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
            for _ in range(OUTPUT_NUM):
                future = executor.submit(call_replicate_api, prompt)
                futures.append(future)
                
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                output = future.result()
                st.caption("Audio output #{}".format(i + 1))
                st.audio(output, format="audio/wav")
