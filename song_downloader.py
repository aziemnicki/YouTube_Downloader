import streamlit as st
import yt_dlp
import tempfile
import shutil
import os
import re

# -----------------------------------------------------------------------------
# 1. KONFIGURACJA I TŁUMACZENIA
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="YouTube Audio Downloader",
    page_icon="🎵",
    layout="wide"
)

def get_translations(lang):
    """Zwraca słownik tłumaczeń w zależności od wybranego języka."""
    translations = {
        "pl": {
            "title": "🎵 Pobierz swoją piosenkę z YouTube 🎵",
            "youtube_link": "Link do YouTube",
            "placeholder": "Wklej link do wideo tutaj (np. https://youtube.com/...)",
            "help": "Obsługiwane są tylko linki do wideo",
            "load_video_btn": "🔍 Wczytaj wideo",
            "download_audio_btn": "📥 Pobierz plik MP3",
            "language": "🌐 Język",
            "english": "🇬🇧 Angielski",
            "polish": "🇵🇱 Polski",
            "downloading": "🔄 Przetwarzanie...",
            "download_complete": "✅ Gotowe",
            "video_info_error": "❌ Nie udało się pobrać informacji o wideo:",
            "no_video_found": "🔍 Nie znaleziono pliku wyjściowego",
            "success": "🎉 Plik gotowy do pobrania!",
            "cleaning_up": "🗑️ Wyczyść pliki tymczasowe",
            "how_to_use": "❓ Jak używać",
            "description": "Prosta aplikacja do pobierania muzyki z YouTube w formacie MP3.",
            "step1": "1️⃣ Wklej link do wideo w pole tekstowe.",
            "step2": "2️⃣ Kliknij 'Wczytaj wideo' i sprawdź podgląd.",
            "step3": "3️⃣ Rozpocznij pobieranie, a następnie zapisz MP3 na dysku.",
            "invalid_link": "⚠️ To nie wygląda jak prawidłowy link. Wklej poprawny link do filmu na YouTube.",
            "ffmpeg_error": "⚠️ Błąd: Nie wykryto FFmpeg."
        },
        "en": {
            "title": "🎵 YouTube Audio Downloader 🎵",
            "youtube_link": "YouTube Link",
            "placeholder": "Paste YouTube video link here...",
            "help": "Only video links are supported",
            "load_video_btn": "🔍 Load Video",
            "download_audio_btn": "📥 Download MP3 File",
            "language": "🌐 Language",
            "english": "🇬🇧 English",
            "polish": "🇵🇱 Polish",
            "downloading": "🔄 Processing...",
            "download_complete": "✅ Complete",
            "video_info_error": "❌ Failed to fetch video info:",
            "no_video_found": "🔍 Output file not found",
            "success": "🎉 File ready for download!",
            "cleaning_up": "🗑️ Clean temp files",
            "how_to_use": "❓ How to use",
            "description": "Simple app to download YouTube audio as MP3.",
            "step1": "1️⃣ Paste the YouTube link in the text box.",
            "step2": "2️⃣ Click 'Load Video' and check the preview.",
            "step3": "3️⃣ Start downloading, then save the MP3.",
            "invalid_link": "⚠️ This doesn't look like a valid link.",
            "ffmpeg_error": "⚠️ Error: FFmpeg not found."
        }
    }
    return translations.get(lang, translations["pl"])

# -----------------------------------------------------------------------------
# 2. FUNKCJE POMOCNICZE (BACKEND)
# -----------------------------------------------------------------------------

def get_common_opts():
    """Wspólne ustawienia dla yt-dlp. Zabezpieczenia przed banem (403)."""
    return {
        "quiet": True,
        "no_warnings": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "sleep_requests": 2,
        "sleep_interval": 3,
        "max_sleep_interval": 7,
        "extractor_args": {
            "youtube": {
                # Obejście dla błędu HTTP 403 Forbidden
                "player_client": ["ios,android,web"]
            }
        }
    }

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_video_info(link):
    """Pobiera informacje o wideo z cachem, by nie odpytywać API za każdym razem."""
    ydl_opts = get_common_opts()
    ydl_opts.update({"extract_flat": "discard_key"})
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return {"title": info.get("title", "Audio"), "success": True, "error": None}
    except Exception as e:
        return {"title": None, "success": False, "error": str(e)}

def download_audio_file(link, lang, progress_container):
    """Pobiera audio, konwertuje na mp3 i zwraca ścieżkę."""
    t = get_translations(lang)
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")
    
    # Inicjalizacja paska postępu w podanym kontenerze
    progress_bar = progress_container.progress(0, text=f"{t['downloading']} (0%)")

    def progress_hook(d):
        if d["status"] == "downloading":
            p_str = d.get("_percent_str", "0%").replace("%", "").strip()
            # Ekstrakcja liczby dla paska postępu
            match = re.search(r"(\d+\.\d+)", p_str)
            if match:
                try:
                    val = float(match.group(1)) / 100.0
                    # t['downloading'] ma w sobie emotkę "🔄" - używamy tylko jej
                    progress_bar.progress(min(max(val, 0.0), 1.0), text=f"{t['downloading']} {p_str}%")
                except ValueError:
                    pass
        elif d["status"] == "finished":
            progress_bar.progress(1.0, text=t['download_complete'])

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
        return None, None, str(e)

    # Szukanie pobranego pliku mp3
    try:
        files = os.listdir(temp_dir)
        target_files = [f for f in files if f.endswith(('.mp3', '.m4a', '.webm'))]
        if target_files:
            target_files.sort(key=lambda x: os.path.getmtime(os.path.join(temp_dir, x)), reverse=True)
            return os.path.join(temp_dir, target_files[0]), target_files[0], None
        else:
            return None, None, t["no_video_found"]
    except Exception as e:
        return None, None, str(e)

def cleanup_temp_files():
    """Czyści pliki tymczasowe."""
    if st.session_state.get("downloaded_file_path"):
        try:
            temp_dir = os.path.dirname(st.session_state.downloaded_file_path)
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
    
    st.session_state.downloaded_file_path = None
    st.session_state.downloaded_file_name = None
    st.session_state.current_video_link = None
    st.session_state.video_title = None
    st.session_state.file_saved = False

# -----------------------------------------------------------------------------
# 3. INTERFEJS UŻYTKOWNIKA (FRONTEND)
# -----------------------------------------------------------------------------

def render_sidebar(t, lang):
    """Generuje lewy panel nawigacyjny."""
    st.sidebar.selectbox(
        t["language"],
        ["pl", "en"],
        index=0 if lang == "pl" else 1,
        format_func=lambda x: t["polish"] if x == "pl" else t["english"],
        key="language_select",
        on_change=lambda: st.session_state.update(language=st.session_state.language_select)
    )

    st.sidebar.markdown("---")
    st.sidebar.header(t["how_to_use"])
    st.sidebar.markdown(t["description"])
    st.sidebar.markdown(t["step1"])
    st.sidebar.markdown(t["step2"])
    st.sidebar.markdown(t["step3"])
    st.sidebar.divider()

    if st.sidebar.button(t["cleaning_up"], use_container_width=True):
        cleanup_temp_files()
        st.toast("🗑️ Pliki usunięte!", icon="✅")
        st.rerun()

def render_main_area(t, lang):
    """Główna przestrzeń aplikacji."""
    st.title(t["title"])
    st.markdown("---")
    
    youtube_link = st.text_input(
        t["youtube_link"],
        placeholder=t["placeholder"],
        help=t["help"]
    )

    if youtube_link:
        is_valid = youtube_link.startswith("http") and ("youtube.com" in youtube_link or "youtu.be" in youtube_link)
        if not is_valid:
            st.error(t["invalid_link"])
        else:
            # Automatycznie po wklejeniu nowego linku (Enter/utrata fokusu) pobieramy info
            if st.session_state.current_video_link != youtube_link:
                cleanup_temp_files() # Czyszczenie starych plików
                st.session_state.current_video_link = youtube_link
                
                with st.spinner("Pobieranie informacji o wideo..."):
                    info = fetch_video_info(youtube_link)
                    
                    if info["success"]:
                        st.session_state.video_title = info["title"]
                        st.toast("✅ Informacje pobrane!", icon="ℹ️")
                    else:
                        st.error(f"{t['video_info_error']} {info['error']}")
                        st.session_state.current_video_link = None

    # Sekcja dla gotowego wideo (tylko gdy mamy info)
    if st.session_state.get("current_video_link") and st.session_state.get("video_title"):
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.subheader("📺 Podgląd")
            st.video(st.session_state.current_video_link)
            
        with col2:
            st.subheader(f"🎧 {st.session_state.video_title}")
            st.markdown("<br>", unsafe_allow_html=True)
            
            file_ready = st.session_state.get("downloaded_file_path") and os.path.exists(st.session_state.downloaded_file_path)
            
            # Krok 1: Wideo załadowane, czekamy na decyzję o pobraniu
            if not file_ready:
                progress_container = st.empty()
                if st.button("🚀 Rozpocznij pobieranie MP3", use_container_width=True, type="primary"):
                    with st.spinner(t["downloading"]):
                        file_path, file_name, err = download_audio_file(
                            st.session_state.current_video_link, 
                            lang, 
                            progress_container
                        )
                        
                        if file_path and not err:
                            st.session_state.downloaded_file_path = file_path
                            st.session_state.downloaded_file_name = file_name
                            st.toast(t["success"], icon="🎉")
                            st.rerun() # Odświeżenie aplikacji, by wyświetlić przycisk zapisu
                        else:
                            st.error(f"Error: {err}")
            
            # Krok 2: Plik MP3 gotowy do zapisania na dysku
            else:
                st.success(t["success"])
                with open(st.session_state.downloaded_file_path, "rb") as f:
                    file_content = f.read()
                
                st.download_button(
                    label=f"💾 Zapisz plik na dysku",
                    data=file_content,
                    file_name=st.session_state.downloaded_file_name,
                    mime="audio/mpeg",
                    use_container_width=True,
                    type="primary",
                    disabled=st.session_state.get("file_saved", False),
                    on_click=lambda: st.session_state.update(file_saved=True)
                )

# -----------------------------------------------------------------------------
# 4. START APLIKACJI
# -----------------------------------------------------------------------------

def main():
    # Inicjalizacja kluczowych zmiennych w session_state
    defaults = {
        "language": "pl",
        "downloaded_file_path": None,
        "downloaded_file_name": None,
        "current_video_link": None,
        "video_title": None,
        "file_saved": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    lang = st.session_state.language
    t = get_translations(lang)

    render_sidebar(t, lang)
    render_main_area(t, lang)

if __name__ == "__main__":
    main()