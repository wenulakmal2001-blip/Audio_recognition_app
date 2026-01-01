import streamlit as st
import speech_recognition as sr
import soundfile as sf
import numpy as np
import io
import tempfile
import os
from datetime import datetime

# Set page configuration
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

# App title and description
st.title("🎤 Speech Recognition Web App")
st.markdown("""
This app converts speech to text using Google's Speech Recognition API.
You can either use your microphone or upload an audio file.
""")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Language selection
    language = st.selectbox(
        "Select Language",
        ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "hi-IN"],
        index=0
    )
    
    # Noise adjustment
    adjust_noise = st.checkbox("Adjust for ambient noise", value=True)
    
    # Timeout settings
    timeout = st.slider("Timeout (seconds)", 1, 10, 5)
    
    st.divider()
    st.markdown("### Instructions:")
    st.markdown("""
    1. For microphone: Click 'Start Recording'
    2. Speak clearly into your microphone
    3. Click 'Stop Recording' when done
    4. Or upload an audio file
    """)

# Create two columns for different input methods
col1, col2 = st.columns(2)

# Column 1: Microphone Input
with col1:
    st.header("🎤 Microphone Input")
    
    # Initialize session state for recording control
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None
    if 'recognized_text' not in st.session_state:
        st.session_state.recognized_text = ""
    
    # Recording controls
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if not st.session_state.recording:
            if st.button("🎤 Start Recording", use_container_width=True):
                st.session_state.recording = True
                st.rerun()
    
    with col_btn2:
        if st.session_state.recording:
            if st.button("⏹️ Stop Recording", use_container_width=True, type="primary"):
                st.session_state.recording = False
                st.rerun()
    
    # Recording status
    if st.session_state.recording:
        st.info("🔴 Recording... Speak now!")
        
        # Create a placeholder for dynamic updates
        status_placeholder = st.empty()
        
        try:
            # Audio recording
            with sr.Microphone() as source:
                if adjust_noise:
                    status_placeholder.info("🎵 Adjusting for ambient noise...")
                    r.adjust_for_ambient_noise(source, duration=0.5)
                
                status_placeholder.info("🎤 Listening... Speak now!")
                
                # Record audio
                audio = r.listen(source, timeout=timeout)
                st.session_state.audio_data = audio
                
                # Try to recognize speech
                try:
                    text = r.recognize_google(audio, language=language)
                    st.session_state.recognized_text = text
                    status_placeholder.success("✅ Recognition successful!")
                except sr.UnknownValueError:
                    st.session_state.recognized_text = "Could not understand audio"
                    status_placeholder.error("❌ Could not understand audio")
                except sr.RequestError as e:
                    st.session_state.recognized_text = f"API error: {e}"
                    status_placeholder.error(f"❌ API error: {e}")
                except Exception as e:
                    st.session_state.recognized_text = f"Error: {str(e)}"
                    status_placeholder.error(f"❌ Error: {str(e)}")
                    
        except Exception as e:
            st.error(f"Microphone error: {str(e)}")
            st.info("Please check your microphone connection and permissions.")
    
    # Display recognized text from microphone
    if st.session_state.recognized_text:
        st.subheader("📝 Recognized Text (Microphone):")
        st.text_area(
            "Result",
            st.session_state.recognized_text,
            height=150,
            key="mic_result"
        )
        
        # Add copy button
        st.download_button(
            label="📥 Download Text",
            data=st.session_state.recognized_text,
            file_name=f"speech_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# Column 2: Audio File Upload
with col2:
    st.header("📁 Audio File Upload")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'm4a', 'flac', 'ogg']
    )
    
    if uploaded_file is not None:
        # Display file info
        st.audio(uploaded_file, format='audio/wav')
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.json(file_details)
        
        # Process the uploaded file
        if st.button("🎵 Process Audio File", type="primary", use_container_width=True):
            with st.spinner("Processing audio file..."):
                try:
                    # Create a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Recognize speech from file
                    with sr.AudioFile(tmp_path) as source:
                        # Adjust for noise if selected
                        if adjust_noise:
                            r.adjust_for_ambient_noise(source, duration=0.5)
                        
                        audio = r.record(source)
                        
                        try:
                            text = r.recognize_google(audio, language=language)
                            
                            # Display result
                            st.subheader("📝 Recognized Text (File):")
                            st.text_area(
                                "Result",
                                text,
                                height=150,
                                key="file_result"
                            )
                            
                            # Add copy button
                            st.download_button(
                                label="📥 Download Text",
                                data=text,
                                file_name=f"file_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                key="file_download"
                            )
                            
                        except sr.UnknownValueError:
                            st.error("Could not understand audio in the file")
                        except sr.RequestError as e:
                            st.error(f"API error: {e}")
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
                    st.info("Supported formats: WAV, MP3, M4A, FLAC, OGG")

# Additional features in expanders
with st.expander("📚 How to Use"):
    st.markdown("""
    ### Microphone Input:
    1. Click **Start Recording**
    2. Speak clearly into your microphone
    3. Click **Stop Recording** when done
    4. View the recognized text
    
    ### File Upload:
    1. Click **Browse files** or drag and drop
    2. Select an audio file (WAV, MP3, etc.)
    3. Click **Process Audio File**
    4. View the recognized text
    
    ### Tips:
    - Ensure good microphone quality
    - Speak clearly and at a moderate pace
    - Reduce background noise
    - For files, use clear audio recordings
    """)

with st.expander("⚠️ Troubleshooting"):
    st.markdown("""
    ### Common Issues:
    
    **Microphone not working:**
    - Check if microphone is connected
    - Grant microphone permissions to browser
    - Try a different browser (Chrome works best)
    
    **Poor recognition accuracy:**
    - Enable "Adjust for ambient noise"
    - Speak closer to the microphone
    - Reduce background noise
    - Try different languages if applicable
    
    **API errors:**
    - Check your internet connection
    - Google Speech Recognition requires internet
    
    **File upload issues:**
    - Ensure file is in supported format
    - File should be less than 10MB
    - Clear audio recordings work best
    """)

# Footer
st.divider()
st.caption("Powered by Google Speech Recognition API | Built with Streamlit")