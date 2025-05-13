import streamlit as st
import os
import yt_dlp
import tempfile
import shutil


# Language translations
def get_translations(lang):
    return {
        "pl": {
            "title": "🎵 Pobierz swoją piosenkę z YouTube 🎵",
            "download_audio": "📥 Pobierz Audio",
            "youtube_link": "YouTube Link",
            "placeholder": "Wklej link do wideo na YouTube",
            "help": "Wklej link do wideo na YouTube",
            "download_audio_btn": "📥 Pobierz Audio",
            "language": "🌐 Język",
            "english": "🇬🇧 Angielski",
            "polish": "🇵🇱 Polski",
            "downloading": "🔄 Wczytywanie informacji o wideo:",
            "download_complete": "✅ Wczytywanie:",
            "video_info_error": "❌ Błąd pobierania tytułu:",
            "no_video_found": "🔍 Nie znaleziono pliku audio",
            "success": "🎉 Gotowe do pobrania!",
            "load_video_btn": "🔄 Wczytaj wideo do pobrania",
            "cleaning_up": "🗑️ Wyczyść poprzednio pobrane...",
            "how_to_use": "❓ Jak używać",
            "description": "🎵 Prosta aplikacja do pobierania audio z YouTube. Wystarczą 3 proste kroki! 🎵",
            "step1": "1️⃣ Wklej link do wideo YouTube w pole tekstowe",
            "step2": "2️⃣ Kliknij przycisk 'Wczytaj wideo i poczekaj kilka sekund'",
            "step3": "3️⃣ Kliknij przycisk pobrania, aby pobrać plik audio",
            "copy_link": "Kopiuj link - Ctrl+C",
            "paste_link": "Wklej link - Ctrl+V",
        },
        "en": {
            "title": "🎵 YouTube Audio Downloader 🎵",
            "download_audio": "📥 Download Audio",
            "youtube_link": "YouTube Link",
            "placeholder": "Paste YouTube video link here",
            "help": "Only video links are supported",
            "download_audio_btn": "📥 Download Audio",
            "language": "🌐 Language",
            "english": "🇬🇧 English",
            "polish": "🇵🇱 Polish",
            "downloading": "🔄 Fetching video info:",
            "download_complete": "✅ Download complete:",
            "video_info_error": "❌ Download title error:",
            "no_video_found": "🔍 Audio file not found",
            "success": "🎉 Download completed successfully!",
            "load_video_btn": "🔄 Load Video to download",
            "cleaning_up": "🗑️ Cleaning up previous download...",
            "how_to_use": "❓ How to use",
            "description": "🎵 Simple YouTube audio downloader. Just 3 easy steps! 🎵",
            "step1": "1️⃣ Paste YouTube video link in the text field",
            "step2": "2️⃣ Click the 'Load Video' button and wait few seconds",
            "step3": "3️⃣ Click download button to download the audio file",
            "copy_link": "Copy link - Ctrl+C",
            "paste_link": "Paste link - Ctrl+V",
        },
    }[lang]


def get_video_info(link):
    try:
        # po_token = st.secrets["po_token"]
        # Get video info first to get the title and check if link is valid
        ydl_opts_info = {
            "quiet": True,
            "extract_flat": "discard_key",
            # "extractor-args": {
            #     "youtube": {
            #         "po_token": f"web.gvs+{po_token}",
            #     }
            # },
            # "force_generic_extractor": True,
            "geo_bypass": True,
            "force_ipv4": True,
            "source_address": "0.0.0.0",
        }
        with st.spinner(get_translations(st.session_state.language)["downloading"]):
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(link, download=False)
                title = info.get("title", "downloaded_audio")
            # Display video preview
            st.video(link, format="video/youtube")

        return title
    except yt_dlp.utils.DownloadError as e:
        st.error(
            f"{get_translations(st.session_state.language)['video_info_error']} {e}"
        )
        return None


# Function to download YouTube audio
def download_audio(link, title):
    # po_token = st.secrets["po_token"]
    """Downloads audio from a YouTube link to a temporary file and returns the path and title."""
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

    # Initialize progress bar
    progress_bar = st.progress(
        0, text=f"{get_translations(st.session_state.language)['downloading']}..."
    )

    # Define progress hook
    def progress_hook(d):
        if d["status"] == "downloading":
            # Get progress percentage
            progress_str = d.get("_percent_str", "0%")
            # Remove ANSI escape codes
            progress_str = "".join(c for c in progress_str if c.isdigit() or c == ".")
            try:
                progress = float(progress_str)
                # Normalize progress to be between 0 and 1
                progress = min(max(progress / 100, 0), 1)
                progress_bar.progress(
                    progress,
                    text=f"{get_translations(st.session_state.language)['downloading']} {d.get('info_dict', {}).get('title', '...') if 'info_dict' in d else ''} - {progress * 100:.1f}%",
                )
            except (ValueError, TypeError):
                progress_bar.progress(
                    0,
                    text=f"{get_translations(st.session_state.language)['downloading']} {d.get('info_dict', {}).get('title', '...') if 'info_dict' in d else ''} - 0.0%",
                )
        elif d["status"] == "finished":
            progress_bar.progress(
                1.0,
                text=f"{get_translations(st.session_state.language)['download_complete']} {d.get('info_dict', {}).get('title', '...') if 'info_dict' in d else ''}",
            )

    ydl_opts_download = {
        "format": "bestaudio/best",  # Get the best audio stream in m4a format
        "outtmpl": output_template,  # Specify the output path template
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",  # Use FFmpeg to extract audio
                "preferredcodec": "mp3",  # Prefer mp3 codec
            }
        ],
        # 'extractor-args': {
        #     'youtube': {
        #         'po_token': f'web.gvs+{po_token}'
        #     }
        # },
        "progress_hooks": [progress_hook],
        "verbose": True,  # Suppress verbose output from yt-dlp itself
        # "no_warnings": True,  # Suppress warnings
        "geo_bypass": True,  # Attempt to bypass geographic restrictions
        # "force_generic_extractor": True,
        "force_ipv4": True,
        "source_address": "0.0.0.0",
    }

    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
        ydl.download([link])

    # Find the downloaded file in the temporary directory
    downloaded_file = None
    # List files in the temporary directory
    files_in_temp_dir = os.listdir(temp_dir)
    common_audio_extensions = (
        ".m4a",
        ".webm",
        ".mp3",
    )

    # Find the most recently modified file with a common audio extension
    if files_in_temp_dir:
        audio_files = [
            f for f in files_in_temp_dir if f.lower().endswith(common_audio_extensions)
        ]
        if audio_files:
            # Sort by modification time (most recent first)
            audio_files.sort(
                key=lambda x: os.path.getmtime(os.path.join(temp_dir, x)), reverse=True
            )
            downloaded_file = os.path.join(temp_dir, audio_files[0])

    if downloaded_file and os.path.exists(downloaded_file):
        st.success(get_translations(st.session_state.language)["success"])
        return downloaded_file, title
    else:
        # If the file wasn't found, it's a potential issue with yt-dlp output or filename
        st.error(
            f"{get_translations(st.session_state.language)['no_video_found']}. Expected file with extensions {common_audio_extensions}. Files found: {files_in_temp_dir}"
        )
        # Clean up the temporary directory if file not found
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return None, None


def main():
    # Initialize session state for language
    if "language" not in st.session_state:
        st.session_state.language = "pl"

    # Create language toggle in sidebar
    current_lang = st.session_state.language
    st.sidebar.selectbox(
        get_translations(current_lang)["language"],
        ["pl", "en"],
        index=0
        if current_lang == "pl"
        else 1,  # Set the default selection based on current language
        format_func=lambda x: get_translations(current_lang)["polish"]
        if x == "pl"
        else get_translations(current_lang)["english"],
        key="language_select",
        on_change=lambda: st.session_state.update(
            language=st.session_state.language_select
        ),
    )

    # Add usage guide to sidebar
    st.sidebar.markdown("---")
    st.sidebar.header(get_translations(current_lang)["how_to_use"])
    st.sidebar.markdown(get_translations(current_lang)["description"])
    st.sidebar.markdown(get_translations(current_lang)["step1"])
    st.sidebar.markdown(get_translations(current_lang)["step2"])
    st.sidebar.markdown(get_translations(current_lang)["step3"])
    st.sidebar.divider()
    st.sidebar.markdown(get_translations(current_lang)["copy_link"])
    st.sidebar.markdown(get_translations(current_lang)["paste_link"])

    st.title(get_translations(st.session_state.language)["title"])

    # Initialize session state for downloaded file info and temporary directory
    if "downloaded_file_path" not in st.session_state:
        st.session_state.downloaded_file_path = None
    if "downloaded_file_name" not in st.session_state:
        st.session_state.downloaded_file_name = None
    if "temp_download_dir" not in st.session_state:
        st.session_state.temp_download_dir = None

    st.header(get_translations(st.session_state.language)["download_audio"])
    youtube_link = st.text_input(
        get_translations(st.session_state.language)["youtube_link"],
        placeholder=get_translations(st.session_state.language)["placeholder"],
        help=get_translations(st.session_state.language)["help"],
        key="youtube_link",
    )

    # Store video info in session state
    if "video_info" not in st.session_state:
        st.session_state.video_info = None

    # Get video info when link changes
    if youtube_link:
        if (
            st.session_state.video_info is None
            or st.session_state.video_info.get("link") != youtube_link
        ):
            # Clear previous download
            if "downloaded_file_path" in st.session_state:
                if st.session_state.downloaded_file_path and os.path.exists(
                    st.session_state.downloaded_file_path
                ):
                    shutil.rmtree(
                        os.path.dirname(st.session_state.downloaded_file_path)
                    )
                st.session_state.downloaded_file_path = None
                st.session_state.downloaded_file_name = None
                st.session_state.temp_download_dir = None

            title = get_video_info(youtube_link)
            if title:
                st.session_state.video_info = {"title": title, "link": youtube_link}
            else:
                st.session_state.video_info = None

        if st.session_state.video_info:
            if st.button(get_translations(st.session_state.language)["load_video_btn"]):
                # Clean up previous download if any
                if st.session_state.temp_download_dir and os.path.exists(
                    st.session_state.temp_download_dir
                ):
                    shutil.rmtree(st.session_state.temp_download_dir)
                    st.session_state.downloaded_file_path = None
                    st.session_state.downloaded_file_name = None
                    st.session_state.temp_download_dir = None

                # Call the download function with the stored title
                file_path, file_name = download_audio(
                    youtube_link, st.session_state.video_info["title"]
                )

                if file_path and file_name:
                    # Store the downloaded file path, name, and temp dir in session state
                    st.session_state.downloaded_file_path = file_path
                    # Determine the correct file extension from the downloaded file path
                    _, file_extension = os.path.splitext(file_path)
                    # Use the original title from yt-dlp info, but ensure a default if not available
                    display_file_name = file_name if file_name else "downloaded_audio"
                    st.session_state.downloaded_file_name = f"{display_file_name}{file_extension}"  # Use the actual extension and title
                    st.session_state.temp_download_dir = os.path.dirname(
                        file_path
                    )  # Store the temp directory path

                    # Read the content of the downloaded file
                    with open(st.session_state.downloaded_file_path, "rb") as f:
                        file_content = f.read()

                    # Provide the file content to st.download_button
                    st.download_button(
                        label=f"{get_translations(st.session_state.language)['download_audio_btn']} {st.session_state.downloaded_file_name}",
                        data=file_content,
                        file_name=st.session_state.downloaded_file_name,
                        # Determine mime type based on file extension
                        mime={
                            ".m4a": "audio/mp4",
                            ".opus": "audio/opus",
                            ".webm": "audio/webm",
                            ".mp3": "audio/mpeg",  # Added for completeness if conversion was done
                        }.get(
                            os.path.splitext(st.session_state.downloaded_file_name)[
                                1
                            ].lower(),
                            "application/octet-stream",
                        ),  # Default to generic binary if unknown
                    )
                else:
                    # Reset state if download failed
                    st.session_state.downloaded_file_path = None
                    st.session_state.downloaded_file_name = None
                    st.session_state.temp_download_dir = None

            if st.sidebar.button(
                get_translations(st.session_state.language)["cleaning_up"]
            ):
                if st.session_state.temp_download_dir and os.path.exists(
                    st.session_state.temp_download_dir
                ):
                    shutil.rmtree(
                        st.session_state.temp_download_dir
                    )  # Remove the entire temp directory
                st.session_state.downloaded_file_path = None
                st.session_state.downloaded_file_name = None
                st.session_state.temp_download_dir = None


if __name__ == "__main__":
    main()
