import streamlit as st
import yt_dlp
import tempfile
import shutil
import os

# -----------------------------------------------------------------------------
# 1. KONFIGURACJA I TŁUMACZENIA
# -----------------------------------------------------------------------------

def get_translations(lang):
    """Zwraca słownik tłumaczeń w zależności od wybranego języka."""
    return {
        "pl": {
            "title": "🎵 Pobierz swoją piosenkę z YouTube 🎵",
            "download_audio": "📥 Pobierz Audio",
            "youtube_link": "Link do YouTube",
            "placeholder": "Wklej link do wideo tutaj...",
            "help": "Obsługiwane są tylko linki do wideo",
            "download_audio_btn": "📥 Pobierz plik",
            "language": "🌐 Język",
            "english": "🇬🇧 Angielski",
            "polish": "🇵🇱 Polski",
            "downloading": "🔄 Przetwarzanie...",
            "download_complete": "✅ Gotowe:",
            "video_info_error": "❌ Nie udało się pobrać informacji o wideo:",
            "no_video_found": "🔍 Nie znaleziono pliku wyjściowego",
            "success": "🎉 Plik gotowy do pobrania!",
            "load_video_btn": "🔄 Wczytaj wideo",
            "cleaning_up": "🗑️ Wyczyść pliki tymczasowe",
            "how_to_use": "❓ Jak używać",
            "description": "🎵 Prosta aplikacja do pobierania muzyki z YouTube w formacie MP3. 🎵",
            "step1": "1️⃣ Wklej link do wideo w pole tekstowe.",
            "step2": "2️⃣ Kliknij 'Wczytaj wideo' i sprawdź podgląd.",
            "step3": "3️⃣ Kliknij 'Pobierz plik', aby zapisać MP3 na dysku.",
            "copy_link": "💡 Skrót: Kopiuj link - Ctrl+C",
            "paste_link": "💡 Skrót: Wklej link - Ctrl+V",
            "ffmpeg_error": "⚠️ Błąd: Nie wykryto FFmpeg. Upewnij się, że jest zainstalowany w systemie."
        },
        "en": {
            "title": "🎵 YouTube Audio Downloader 🎵",
            "download_audio": "📥 Download Audio",
            "youtube_link": "YouTube Link",
            "placeholder": "Paste YouTube video link here...",
            "help": "Only video links are supported",
            "download_audio_btn": "📥 Download File",
            "language": "🌐 Language",
            "english": "🇬🇧 English",
            "polish": "🇵🇱 Polish",
            "downloading": "🔄 Processing...",
            "download_complete": "✅ Complete:",
            "video_info_error": "❌ Failed to fetch video info:",
            "no_video_found": "🔍 Output file not found",
            "success": "🎉 File ready for download!",
            "load_video_btn": "🔄 Load Video",
            "cleaning_up": "🗑️ Clean temp files",
            "how_to_use": "❓ How to use",
            "description": "🎵 Simple app to download YouTube audio as MP3. 🎵",
            "step1": "1️⃣ Paste the YouTube link in the text box.",
            "step2": "2️⃣ Click 'Load Video' and check the preview.",
            "step3": "3️⃣ Click 'Download File' to save the MP3.",
            "copy_link": "💡 Hint: Copy link - Ctrl+C",
            "paste_link": "💡 Hint: Paste link - Ctrl+V",
            "ffmpeg_error": "⚠️ Error: FFmpeg not found. Please ensure it is installed."
        },
    }[lang]

# -----------------------------------------------------------------------------
# 2. FUNKCJE POMOCNICZE (BACKEND)
# -----------------------------------------------------------------------------

def get_common_opts():
    """
    Zwraca wspólne ustawienia dla yt-dlp.
    Kluczowe naprawy błędów SSAP i 403 Forbidden znajdują się tutaj.
    """
    return {
        "quiet": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        # NAPRAWA BŁĘDU SSAP / SIGNATURE EXTRACTION:
        # Udajemy klienta Android, który ma lżejsze zabezpieczenia niż wersja Web
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios"],
                "player_skip": ["web", "tv"],
            }
        },
        # Udawanie zwykłej przeglądarki w nagłówkach HTTP
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
    }

def get_video_info(link):
    """Pobiera tytuł i wyświetla podgląd wideo."""
    ydl_opts = get_common_opts()
    # Dodatkowe opcje tylko dla pobierania info (bez pliku)
    ydl_opts.update({
        "extract_flat": "discard_key", # Szybsze pobieranie info
    })

    try:
        with st.spinner(get_translations(st.session_state.language)["downloading"]):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                title = info.get("title", "Audio")
                
                # Wyświetl podgląd wideo
                st.video(link, format="video/youtube")
                return title
    except Exception as e:
        st.error(f"{get_translations(st.session_state.language)['video_info_error']} {str(e)}")
        return None

def download_audio(link):
    """Pobiera audio, konwertuje na mp3 i zwraca ścieżkę."""
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")
    
    # Inicjalizacja paska postępu
    progress_bar = st.progress(0, text=f"{get_translations(st.session_state.language)['downloading']}...")

    def progress_hook(d):
        if d["status"] == "downloading":
            p_str = d.get("_percent_str", "0%").replace("%", "")
            try:
                val = float(p_str) / 100
                progress_bar.progress(min(val, 1.0), text=f"⏳ {d.get('_percent_str', '')}")
            except ValueError:
                pass
        elif d["status"] == "finished":
            progress_bar.progress(1.0, text=get_translations(st.session_state.language)['download_complete'])

    # Opcje pobierania
    ydl_opts = get_common_opts()
    ydl_opts.update({
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "progress_hooks": [progress_hook],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
    except Exception as e:
        st.error(f"Error: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None, None

    # Szukanie pobranego pliku
    try:
        files = os.listdir(temp_dir)
        # Szukamy mp3 (bo taki kodek wymusiliśmy) lub innych audio
        target_files = [f for f in files if f.endswith(('.mp3', '.m4a', '.webm'))]
        
        if target_files:
            # Sortujemy po dacie, bierzemy najnowszy
            target_files.sort(key=lambda x: os.path.getmtime(os.path.join(temp_dir, x)), reverse=True)
            final_path = os.path.join(temp_dir, target_files[0])
            return final_path, target_files[0]
        else:
            st.error(get_translations(st.session_state.language)["no_video_found"])
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None, None
    except Exception:
        return None, None

# -----------------------------------------------------------------------------
# 3. INTERFEJS UŻYTKOWNIKA (FRONTEND)
# -----------------------------------------------------------------------------

def main():
    # Inicjalizacja stanu sesji (język)
    if "language" not in st.session_state:
        st.session_state.language = "pl"

    # --- SIDEBAR (Pasek boczny) ---
    current_lang = st.session_state.language
    st.sidebar.selectbox(
        get_translations(current_lang)["language"],
        ["pl", "en"],
        index=0 if current_lang == "pl" else 1,
        format_func=lambda x: get_translations(current_lang)["polish"] if x == "pl" else get_translations(current_lang)["english"],
        key="language_select",
        on_change=lambda: st.session_state.update(language=st.session_state.language_select),
    )

    st.sidebar.markdown("---")
    st.sidebar.header(get_translations(current_lang)["how_to_use"])
    st.sidebar.markdown(get_translations(current_lang)["description"])
    st.sidebar.markdown(get_translations(current_lang)["step1"])
    st.sidebar.markdown(get_translations(current_lang)["step2"])
    st.sidebar.markdown(get_translations(current_lang)["step3"])
    st.sidebar.divider()
    st.sidebar.caption(get_translations(current_lang)["copy_link"])
    st.sidebar.caption(get_translations(current_lang)["paste_link"])

    # --- GŁÓWNE OKNO ---
    st.title(get_translations(current_lang)["title"])
    
    # Zarządzanie stanem plików
    if "downloaded_file_path" not in st.session_state:
        st.session_state.downloaded_file_path = None
    if "downloaded_file_name" not in st.session_state:
        st.session_state.downloaded_file_name = None
    if "video_info" not in st.session_state:
        st.session_state.video_info = None

    st.header(get_translations(current_lang)["download_audio"])
    
    youtube_link = st.text_input(
        get_translations(current_lang)["youtube_link"],
        placeholder=get_translations(current_lang)["placeholder"],
        help=get_translations(current_lang)["help"],
        key="youtube_link_input"
    )

    # Logika zmiany linku - resetowanie stanu
    if youtube_link:
        if st.session_state.video_info is None or st.session_state.video_info.get("link") != youtube_link:
             # Resetuj poprzednie pobranie jeśli link się zmienił
            st.session_state.downloaded_file_path = None
            st.session_state.video_info = None

        # Pobieranie informacji o wideo (Tytuł + Podgląd)
        if st.session_state.video_info is None:
            title = get_video_info(youtube_link)
            if title:
                st.session_state.video_info = {"title": title, "link": youtube_link}

        # Jeśli mamy info o wideo, pokaż przyciski akcji
        if st.session_state.video_info:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Przycisk "Załaduj / Odśwież"
                if st.button(get_translations(current_lang)["load_video_btn"]):
                    # To wymusza ponowne pobranie
                    st.session_state.downloaded_file_path = None 
                    file_path, file_name = download_audio(youtube_link)
                    
                    if file_path and file_name:
                        st.session_state.downloaded_file_path = file_path
                        st.session_state.downloaded_file_name = file_name
                        st.success(get_translations(current_lang)["success"])

            # Wyświetlanie przycisku pobierania, jeśli plik istnieje na serwerze
            if st.session_state.downloaded_file_path and os.path.exists(st.session_state.downloaded_file_path):
                with open(st.session_state.downloaded_file_path, "rb") as f:
                    file_content = f.read()
                
                st.download_button(
                    label=f"{get_translations(current_lang)['download_audio_btn']} 🎵",
                    data=file_content,
                    file_name=st.session_state.downloaded_file_name,
                    mime="audio/mpeg"
                )

    # Przycisk czyszczenia
    if st.sidebar.button(get_translations(current_lang)["cleaning_up"]):
        if st.session_state.downloaded_file_path:
            # Próba usunięcia folderu tymczasowego
            try:
                temp_dir = os.path.dirname(st.session_state.downloaded_file_path)
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                st.error(f"Error: {e}")
        st.session_state.downloaded_file_path = None
        st.session_state.downloaded_file_name = None
        st.session_state.video_info = None
        st.rerun()

if __name__ == "__main__":
    main()