import streamlit as st
import speech_recognition as sr
import tempfile
import os

# Set page config
st.set_page_config(
    page_title="Speech Recognition App",
    page_icon="🎤",
    layout="wide"
)

# Initialize recognizer
@st.cache_resource
def get_recognizer():
    return sr.Recognizer()

r = get_recognizer()

# App title
st.title("🎤 Speech Recognition App")
st.markdown("Upload audio files to convert speech to text")

# Language selection
language = st.selectbox(
    "Select Language",
    ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE"],
    index=0
)

# File uploader
uploaded_file = st.file_uploader(
    "Upload audio file (WAV, MP3, FLAC)",
    type=['wav', 'mp3', 'flac']
)

if uploaded_file is not None:
    # Display audio
    st.audio(uploaded_file)
    
    # Transcribe button
    if st.button("🎵 Transcribe Audio", type="primary"):
        with st.spinner("Processing..."):
            try:
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                # Transcribe
                with sr.AudioFile(tmp_path) as source:
                    audio = r.record(source)
                    text = r.recognize_google(audio, language=language)
                
                # Display result
                st.success("✅ Transcription complete!")
                st.text_area("Transcribed Text:", text, height=200)
                
                # Download button
                st.download_button(
                    label="📥 Download Text",
                    data=text,
                    file_name="transcription.txt",
                    mime="text/plain"
                )
                
                # Cleanup
                os.unlink(tmp_path)
                
            except sr.UnknownValueError:
                st.error("Could not understand audio. Try a clearer recording.")
            except sr.RequestError as e:
                st.error(f"API Error: {e}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Instructions
with st.expander("📖 How to Use"):
    st.markdown("""
    1. Upload an audio file (WAV, MP3, or FLAC)
    2. Select language
    3. Click 'Transcribe Audio'
    4. View and download the text
    
    **Note:** Maximum file size is 50MB.
    """)
