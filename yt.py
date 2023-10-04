import pygame
from pytube import YouTube
import customtkinter
from tkinter import filedialog, Tk
import pygame.mixer as mix
import subprocess
import youtube_dl
from moviepy.editor import *
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume



def get_system_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current_volume = volume.GetMasterVolumeLevelScalar()
    return current_volume


class Frame(customtkinter.CTkFrame):
    def __init__(self, master, width, corner_radius):
        super().__init__(master, width, corner_radius)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.selected = False
        self.selected_path = None
        self.button_play = False
        self.song_title = None
        self.timestamp = 0
        self.queue=[]



        self.title("Music Downloader")
        self.geometry("900x450")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.frame = customtkinter.CTkFrame(self, width=500, height=300, corner_radius=10)
        self.frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        # self.frame.pack(pady=20, padx=10, fill="both", expand=True)

        self.label = customtkinter.CTkLabel(self.frame,  text="Wklej link do piosenki na YouTube", font=("Roboto", 24))
        self.label.grid(row=0, column=0, pady=6, padx=10, sticky='nsew')
        # self.label.pack(pady=12, padx=10)
        self.entry1 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Miejsce na link", width=400, height=50)
        self.entry1.grid(row=1, column=0, padx=30, pady=0)
        #self.entry1.pack(pady=2, padx=10)
        self.label2 = customtkinter.CTkLabel(master=self.frame, text='Wybierz folder do pobrania',
                                        font=("Roboto", 12))
        self.label2.grid(row=0, column=1, padx=10, pady=(10,0), sticky='w')
        self.label3 = customtkinter.CTkLabel(master=self.frame,
                                             text='(domyślnie "Pobrane")',
                                             font=("Roboto", 12))
        self.label3.grid(row=0, column=1, padx=10, pady=(50, 0), sticky='w')
        # label2.pack(pady=2, padx=10)
        self.button1 = customtkinter.CTkButton(master=self.frame, text="Otwórz folder", command=self.foldery)
        self.button1.grid(row=1, column=1, padx=10, pady=12, sticky='w')
        # self.button1.pack(pady=12, padx=10, side="top")

        self.button2 = customtkinter.CTkButton(master=self.frame, text="Pobierz", command=self.download, width=100)
        self.button2.grid(row=2, column=0, padx=150, pady=12, sticky='nsew')
        # self.button2.pack(pady=12, padx=10, side="bottom")

        self.scroll = customtkinter.CTkScrollableFrame(self, label_text='Playlista', height=150, width=200, fg_color='#d2f7f5')
        self.scroll.grid(row=0, column=0, padx=10, pady=(10,0), sticky='e')


        self.label_frame = customtkinter.CTkFrame(self, )
        self.label_frame.grid(row=1, column=0, padx=15, pady=(10, 0), sticky="ew")
        self.label4 = customtkinter.CTkLabel(self.label_frame,
                                             text="Odtwarzacz muzyki, wklej link aby odsłuchać i sprawdzić",
                                             font=("Roboto", 16))
        self.label4.grid(row=0, column=0, padx=(200,0), pady=5, sticky='e')


        self.player_frame = Frame(self, width=500, corner_radius=20)
        self.player_frame.configure(fg_color="#cce6d3", height=50)
        self.player_frame.grid(row=2, column=0,padx=10, pady=10, sticky='s')

        self.button3 = customtkinter.CTkButton(master=self.player_frame, text='<<', text_color="#000000", width=100,
                                               font=customtkinter.CTkFont(size=12, weight="bold"), command=self.reverse)
        self.button3.grid(row=0, column=0, padx=(20, 10), pady=50, sticky='nswe')
        self.button4 = customtkinter.CTkButton(master=self.player_frame, text='| |',text_color="#000000", width=100,
                                               font=customtkinter.CTkFont(size=12, weight="bold"), command=self.stop)
        self.button4.grid(row=0, column=1, padx=10, pady=50, sticky='nswe')
        self.button5 = customtkinter.CTkButton(master=self.player_frame, text='PLAY',text_color="#000000", width=100,
                                               font=customtkinter.CTkFont(size=12, weight="bold"), command=self.play)
        self.button5.grid(row=0, column=2, padx=10, pady=50, sticky='nswe')
        self.button6 = customtkinter.CTkButton(master=self.player_frame, text='>>',text_color="#000000", width=100,
                                               font=customtkinter.CTkFont(size=12, weight="bold"), command=self.next)
        self.button6.grid(row=0, column=3, padx=10, pady=50, sticky='nswe')
        self.button7 = customtkinter.CTkButton(master=self.player_frame, text='NEXT>>', text_color="#000000", width=100,
                                               font=customtkinter.CTkFont(size=12, weight="bold"), command=self.next_song)
        self.button7.grid(row=0, column=4, padx=(10, 20), pady=50, sticky='nswe')

        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent", width=50, height=150)
        self.slider_progressbar_frame.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="e")
        self.slider = customtkinter.CTkSlider(self.player_frame, orientation="vertical", number_of_steps=100,
                                            from_=0, to=100, height=100, command=self.volume)
        self.slider.grid(row=0, column=5, rowspan=5, padx=(10, 40), pady=(10, 10), sticky="ns")
        self.slider.set(volume*100)

    def volume(self, value):
        print(self.slider.get())
        self.new_val = value/100.0
        mix.music.set_volume(self.new_val)


    def reverse(self):
        if mix.music.get_busy():
            mix.music.rewind()
            self.timestamp = 0
            mix.music.set_pos(0)

    def stop(self):
        if mix.music.get_busy():
            mix.music.pause()
            self.button4.configure(fg_color="#ff4d4d", text_color="#000000")
        else:
            mix.music.unpause()
            self.button4.configure(fg_color="#2cc985")


    def play(self):
        os.chdir(os.path.join(os.getcwd(), 'temp_audio'))
        self.selected_path = os.getcwd()
        self.download()
        files = os.listdir(self.selected_path)
        print(files)
        # print(self.song_title)
        if self.button_play:
            mix.music.queue(files[0])
            print("Dodano do kolejki")
            # self.button_play = False
            self.queue.extend(files)
        else:
            self.button_play = True
            for f in range(len( files)):
                if files[f] == self.song_title:
                    print(self.song_title)
                    mix.music.load(os.path.join(self.selected_path, self.song_title))
                    mix.music.play()

        os.chdir(os.path.dirname(os.getcwd()))
        print(os.getcwd())

    def next(self):
        if mix.music.get_busy():
            self.timestamp += (mix.music.get_pos()/1000)+10
            print(self.timestamp)
            mix.music.rewind()
            mix.music.set_pos(self.timestamp)

    def next_song(self):
        if mix.music.get_busy():
            if self.queue:
                next_song = self.queue[0]  # Pobierz następną piosenkę z kolejki
                try:
                    mix.music.load(os.path.join(self.selected_path, next_song))
                    mix.music.play()
                except pygame.error as e:
                    print(e)
                self.queue.pop(0)


    def foldery(self):
        if self.selected == False:
            self.selected_path = filedialog.askdirectory(initialdir=main_path, title="Wybierz folder")
            print(self.selected_path)
        else:
            self.selected_path = main_path
        return self.selected_path


    def download(self):
        link = app.entry1.get()
        if self.selected_path is None:
            self.selected_path = main_path
        # elif self.button_play:
        #     print(os.getcwd())
        #     self.selected_path = os.getcwd()

        if link != "":
            # print("test")
            yt = YouTube(link)
            song = yt.streams.filter(file_extension='mp4', resolution=yt.streams.get_highest_resolution()).first()
            # print("Tytuł: ", yt.title)
            # print("Długość: ", yt.length)
            file = song.download(output_path=self.selected_path, skip_existing=True)
            # mp3_file = 'audio.mp3'
            base, ext = os.path.splitext(file)
            new_file = base + '.mp3'
            self.song_title = yt.title + '.mp3'
            try:
                if new_file not in os.listdir(os.getcwd()):
                    video = VideoFileClip(file)
                    audioclip = video.audio
                    audioclip.write_audiofile(new_file)
                    audioclip.close()
                    video.close()
                    os.remove(file)
            except IOError as e:
                print(e)
            # print(new_file)
            # self.convert(file, "audio.mp3")

            # copy2(new_file, os.path.join(os.getcwd(), 'temp_audio'))
            print('Pobrano ', yt.title)
            app.entry1.delete(0, "end")

            # yd=yt.streams.get_highest_resolution()
            # yd.download('.Download')
            # self.download_and_convert(link, self.selected_path)




if __name__ == "__main__":
    mix.init()
    folder = os.path.expanduser("~")
    main_path = os.path.join(folder, "Downloads")
    # temp_path = os.path('temp_audio')

    customtkinter.set_appearance_mode("system")
    customtkinter.set_default_color_theme("green")
    # os.chdir(main_path)
    # sound = mix.music.load('audio.mp3')
    # mix.music.play()
    volume = get_system_volume()
    print('good')
    app = App()
    app.mainloop()
    mix.music.unload()
    os.chdir(os.path.join(os.getcwd(), 'temp_audio'))
    path = os.getcwd()
    files = os.listdir(path)
    for f in files:
        os.remove(f)
    print("close")