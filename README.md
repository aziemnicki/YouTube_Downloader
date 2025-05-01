# YouTube Audio Downloader

A simple and user-friendly application that allows you to download audio from YouTube videos. The application features a bilingual interface (Polish and English) with a clean, modern design.

## 🌐 Online Version

You can use the application online at: [https://youtubesongdownloader.streamlit.app](https://youtubesongdownloader.streamlit.app)

## 🖥️ Local Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv (Python package installer)
- yt-dlp (YouTube downloader)
- streamlit (Python web framework)
- ffmpeg (required for video processing)

### Installation Steps

1. Clone this repository:
```bash
git clone https://github.com/aziemnicki/YouTube_Downloader.git
cd YouTube_Downloader
```

2. Install Python Dependencies

All dependencies are managed via `pyproject.toml` and `uv.lock`.

```bash
# use pyproject.toml directly:
uv pip install -r pyproject.toml
```

Or simply:
```bash
uv venv .venv
uv pip install -e .
```

---

3. Run the Streamlit UI App

```bash
streamlit run song_downloader.py
```

This will launch the app in your default web browser.

---

The application will start and be available at `http://localhost:8501` by default.

## 📱 How to Use

1. Open the application in your web browser
2. Select your preferred language (Polish or English)
3. Follow the 3 simple steps in the sidebar:
   - Paste YouTube video link in the text field
   - Click the 'Load Video' button and wait few seconds
   - Click download button to download the audio file

## 🛠️ Features

- 🎵 Download audio from YouTube videos
- 🌐 Bilingual interface (Polish and English)
- 🔄 Progress tracking during downloads
- 🗑️ Automatic cleanup of temporary files
- 🔍 Error handling and user feedback
- 🎶 Support for multiple audio formats

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## 📬 Support

For support, please open an issue in the GitHub repository.

## 📚 Documentation

For more detailed documentation, please refer to the source code comments and docstrings.