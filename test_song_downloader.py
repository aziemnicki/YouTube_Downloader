import importlib
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class DownloaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        streamlit = types.ModuleType("streamlit")
        streamlit.set_page_config = lambda **kwargs: None
        yt_dlp = types.ModuleType("yt_dlp")
        with patch.dict(sys.modules, {"streamlit": streamlit, "yt_dlp": yt_dlp}):
            cls.app = importlib.import_module("song_downloader")

    def test_video_urls(self):
        canonical = "https://www.youtube.com/watch?v=ojlFMA7ASZU"
        for url in (
            canonical,
            canonical + "&list=RDojlFMA7ASZU&start_radio=1\xa0",
            "https://youtu.be/ojlFMA7ASZU?t=12",
            "https://m.youtube.com/shorts/ojlFMA7ASZU",
            "https://music.youtube.com/watch?list=PL123&v=ojlFMA7ASZU",
        ):
            with self.subTest(url=url):
                self.assertEqual(self.app.clean_youtube_url(url), canonical)
        for url in (
            "https://evil.example/watch?v=ojlFMA7ASZU",
            "https://youtube.com.evil.example/watch?v=ojlFMA7ASZU",
            "https://www.youtube.com/playlist?list=RDojlFMA7ASZU",
            "https://www.youtube.com/watch?v=bad",
            "javascript:youtube.com/watch?v=ojlFMA7ASZU",
            "",
        ):
            with self.subTest(url=url):
                self.assertEqual(self.app.clean_youtube_url(url), "")

    def test_download_one_mp3_and_cleanup_on_success_or_error(self):
        app = self.app
        seen = []

        class FakeYoutubeDL:
            fail = False

            def __init__(self, opts):
                self.opts = opts

            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def download(self, urls):
                seen.append((urls, self.opts))
                output_dir = Path(self.opts["outtmpl"]).parent
                if self.fail:
                    raise RuntimeError("download failed")
                (output_dir / "song.mp3").write_bytes(b"MP3")

        with patch.object(app.yt_dlp, "YoutubeDL", FakeYoutubeDL, create=True):
            url = "https://www.youtube.com/watch?v=ojlFMA7ASZU&list=RDojlFMA7ASZU"
            audio, filename, error = app.download_audio_file(url, "pl", None)
            self.assertEqual((audio, filename, error), (b"MP3", "song.mp3", None))
            self.assertEqual(seen[-1][0], ["https://www.youtube.com/watch?v=ojlFMA7ASZU"])
            self.assertTrue(seen[-1][1]["noplaylist"])
            self.assertFalse(os.path.exists(Path(seen[-1][1]["outtmpl"]).parent))

            FakeYoutubeDL.fail = True
            self.assertEqual(app.download_audio_file(url, "pl", None)[2], "download failed")
            self.assertFalse(os.path.exists(Path(seen[-1][1]["outtmpl"]).parent))


if __name__ == "__main__":
    unittest.main()
