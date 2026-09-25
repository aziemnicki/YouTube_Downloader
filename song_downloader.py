import streamlit as st
import yt_dlp
import tempfile
import shutil
import os
import re
from urllib.parse import parse_qs, urlsplit

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
            "help": "Wklej link do filmu, także z playlisty. Pobrany zostanie tylko ten film.",
            "language": "🌐 Język",
            "english": "🇬🇧 Angielski",
            "polish": "🇵🇱 Polski",
            "downloading": "🔄 Przetwarzanie...",
            "download_complete": "✅ Gotowe",
            "video_info_error": "❌ Nie udało się pobrać informacji o wideo:",
            "no_video_found": "🔍 Nie znaleziono pliku wyjściowego",
            "success": "🎉 Plik gotowy do pobrania!",
            "cleaning_up": "🗑️ Wyczyść",
            "how_to_use": "❓ Jak używać",
            "description": "Prosta aplikacja do pobierania muzyki z YouTube w formacie MP3.",
            "step1": "1️⃣ Wklej link do wideo w pole tekstowe.",
            "step2": "2️⃣ Sprawdź podgląd filmu.",
            "step3": "3️⃣ Rozpocznij pobieranie, a następnie zapisz MP3 na dysku.",
            "invalid_link": "⚠️ To nie wygląda jak prawidłowy link. Wklej poprawny link do filmu na YouTube.",
            "save_to_disk": "💾 Zapisz plik na dysku",
            "download_another": "🔄 Pobierz kolejny utwór",
            "listen_preview": "▶️ Odsłuchaj przed zapisaniem:"
        },
        "en": {
            "title": "🎵 YouTube Audio Downloader 🎵",
            "youtube_link": "YouTube Link",
            "placeholder": "Paste YouTube video link here...",
            "help": "Paste a video link, including one from a playlist. Only that video will be downloaded.",
            "language": "🌐 Language",
            "english": "🇬🇧 English",
            "polish": "🇵🇱 Polish",
            "downloading": "🔄 Processing...",
            "download_complete": "✅ Complete",
            "video_info_error": "❌ Failed to fetch video info:",
            "no_video_found": "🔍 Output file not found",
            "success": "🎉 File ready for download!",
            "cleaning_up": "🗑️ Clear",
            "how_to_use": "❓ How to use",
            "description": "Simple app to download YouTube audio as MP3.",
            "step1": "1️⃣ Paste the YouTube link in the text box.",
            "step2": "2️⃣ Check the video preview.",
            "step3": "3️⃣ Start downloading, then save the MP3.",
            "invalid_link": "⚠️ This doesn't look like a valid link.",
            "save_to_disk": "💾 Save file to disk",
            "download_another": "🔄 Download another track",
            "listen_preview": "▶️ Listen before saving:"
        }
    }
    return translations.get(lang, translations["pl"])

# -----------------------------------------------------------------------------
# 2. FUNKCJE POMOCNICZE (BACKEND)
# -----------------------------------------------------------------------------

def clean_youtube_url(url: str) -> str:
    """Return one canonical video URL, or an empty string for invalid input."""
    try:
        parsed = urlsplit(url.strip())
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in ("http", "https") or parsed.username or parsed.password or parsed.port:
            return ""
        if host == "youtu.be":
            video_id = parsed.path.removeprefix("/")
        elif host in ("youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"):
            if parsed.path == "/watch":
                video_id = parse_qs(parsed.query).get("v", [""])[0]
            elif parsed.path.startswith(("/shorts/", "/live/")):
                video_id = parsed.path.split("/")[2]
            else:
                return ""
        else:
            return ""
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            return f"https://www.youtube.com/watch?v={video_id}"
    except ValueError:
        pass
    return ""

def get_js_runtimes():
    """Wykrywa środowisko JavaScript potrzebne do obsługi YouTube przez yt-dlp."""
    runtimes = {}
    if shutil.which("node"):
        runtimes["node"] = {}
    elif shutil.which("deno"):
        runtimes["deno"] = {}
    return runtimes

def get_common_opts():
    """Wspólne ustawienia dla pobierania pojedynczego filmu."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "remote_components": ["ejs:github"],
    }

    js_runtimes = get_js_runtimes()
    if js_runtimes:
        opts["js_runtimes"] = js_runtimes

    return opts

def fetch_video_info(link):
    """Pobiera informacje o pojedynczym wideo."""
    clean_link = clean_youtube_url(link)
    if not clean_link:
        return {"title": None, "success": False, "error": "Nieprawidłowy link do filmu"}
    ydl_opts = get_common_opts()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_link, download=False)
            if not info or info.get("_type") == "playlist":
                raise ValueError("Nie znaleziono pojedynczego wideo")
            return {"title": info.get("title") or "Audio", "success": True, "error": None}
    except Exception as e:
        return {"title": None, "success": False, "error": str(e)}

def download_audio_file(link, lang, progress_container):
    """Pobiera jedno wideo i zwraca MP3 jako bajty, nazwę oraz błąd."""
    clean_link = clean_youtube_url(link)
    t = get_translations(lang)
    if not clean_link:
        return None, None, t["invalid_link"]
    progress_bar = None
    if progress_container is not None:
        try:
            progress_bar = progress_container.progress(0, text=f"{t['downloading']} (0%)")
        except Exception:
            progress_bar = None

    def progress_hook(d):
        if progress_bar is None:
            return
        try:
            if d["status"] == "downloading":
                downloaded = d.get("downloaded_bytes", 0)
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                if total and total > 0:
                    val = downloaded / total
                    percent_int = int(val * 100)
                    progress_bar.progress(min(max(val, 0.0), 1.0), text=f"{t['downloading']} {percent_int}%")
                else:
                    p_str = d.get("_percent_str", "0%").replace("%", "").strip()
                    match = re.search(r"(\d+(\.\d+)?)", p_str)
                    if match:
                        val = float(match.group(1)) / 100.0
                        progress_bar.progress(min(max(val, 0.0), 1.0), text=f"{t['downloading']} {p_str}%")
            elif d["status"] == "finished":
                progress_bar.progress(1.0, text=t["download_complete"])
        except Exception:
            pass

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = get_common_opts()
            ydl_opts.update({
                "format": "bestaudio/best",
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "progress_hooks": [progress_hook],
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([clean_link])
            mp3_files = [name for name in os.listdir(temp_dir) if name.lower().endswith(".mp3")]
            if len(mp3_files) != 1:
                return None, None, t["no_video_found"]
            filename = mp3_files[0]
            with open(os.path.join(temp_dir, filename), "rb") as audio_file:
                return audio_file.read(), filename, None
    except Exception as e:
        return None, None, str(e)

def clear_download():
    """Czyści dane poprzedniego utworu."""
    st.session_state.downloaded_file_name = None
    st.session_state.downloaded_audio_bytes = None
    st.session_state.current_video_link = None
    st.session_state.video_title = None

def reset_form():
    clear_download()
    st.session_state.youtube_link = ""

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

    if st.sidebar.button(t["cleaning_up"], use_container_width=True, on_click=reset_form):
        st.toast("🗑️ Pliki usunięte!", icon="✅")

def render_main_area(t, lang):
    """Główna przestrzeń aplikacji."""
    st.title(t["title"])
    st.markdown("---")
    
    youtube_link = st.text_input(
        t["youtube_link"],
        placeholder=t["placeholder"],
        help=t["help"],
        key="youtube_link",
    )

    clean_link = clean_youtube_url(youtube_link)
    if not clean_link and st.session_state.current_video_link:
        clear_download()
    if youtube_link and not clean_link:
        st.error(t["invalid_link"])
    elif clean_link:
        # Automatycznie po wklejeniu nowego linku pobieramy informacje.
        if st.session_state.current_video_link != clean_link:
            clear_download()
            st.session_state.current_video_link = clean_link
            with st.spinner("Pobieranie informacji o wideo..."):
                info = fetch_video_info(clean_link)
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
            
            file_ready = bool(st.session_state.get("downloaded_audio_bytes"))
            
            # Krok 1: Wideo załadowane, czekamy na decyzję o pobraniu
            if not file_ready:
                progress_container = st.empty()
                if st.button("🚀 Rozpocznij pobieranie MP3", use_container_width=True, type="primary"):
                    with st.spinner(t["downloading"]):
                        audio_bytes, file_name, err = download_audio_file(
                            st.session_state.current_video_link, 
                            lang, 
                            progress_container
                        )
                        
                        if audio_bytes is not None and not err:
                            st.session_state.downloaded_audio_bytes = audio_bytes
                            st.session_state.downloaded_file_name = file_name
                            st.toast(t["success"], icon="🎉")
                            st.rerun() # Odświeżenie aplikacji, by wyświetlić przycisk zapisu
                        else:
                            st.error(f"Error: {err}")
            
            # Krok 2: Plik MP3 gotowy do zapisania na dysku
            else:
                st.success(t["success"])

                if st.session_state.get("downloaded_audio_bytes"):
                    st.caption(t["listen_preview"])
                    st.audio(st.session_state.downloaded_audio_bytes, format="audio/mp3")

                    st.download_button(
                        label=t["save_to_disk"],
                        data=st.session_state.downloaded_audio_bytes,
                        file_name=st.session_state.downloaded_file_name or "audio.mp3",
                        mime="audio/mpeg",
                        use_container_width=True,
                        type="primary",
                        key="download_audio_ready_btn"
                    )

                st.markdown("<br>", unsafe_allow_html=True)
                st.button(t["download_another"], use_container_width=True, key="download_another_btn", on_click=reset_form)

# -----------------------------------------------------------------------------
# 4. START APLIKACJI
# -----------------------------------------------------------------------------

def main():
    # Inicjalizacja kluczowych zmiennych w session_state
    defaults = {
        "language": "pl",
        "downloaded_file_name": None,
        "downloaded_audio_bytes": None,
        "current_video_link": None,
        "video_title": None,
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
