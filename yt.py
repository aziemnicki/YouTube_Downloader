from pytube import YouTube
import os
import customtkinter
from tkinter import filedialog, Tk
import pygame.mixer as mix
from sys import argv


class Frame(customtkinter.CTkFrame):
    def __init__(self, master, width, corner_radius):
        super().__init__(master, width, corner_radius)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.selected = False
        self.selected_path = None
        self.title("Music Downloader")
        self.geometry("700x350")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.frame = Frame(self, width=500, corner_radius=10)
        self.frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
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


        self.player_frame = Frame(self, width=500, corner_radius=20)
        self.player_frame.configure(fg_color="#cce6d3", height=50)
        self.player_frame.grid(row=1, column=0,padx=10, pady=10, sticky='s')
        self.button3 = customtkinter.CTkButton(master=self.player_frame, text='<<', command=self.reverse)
        self.button3.grid(row=0, column=0, padx=(20, 10), pady=20, sticky='nswe')
        self.button4 = customtkinter.CTkButton(master=self.player_frame, text='| |', command=self.stop)
        self.button4.grid(row=0, column=1, padx=10, pady=20, sticky='nswe')
        self.button5 = customtkinter.CTkButton(master=self.player_frame, text='PLAY', command=self.play)
        self.button5.grid(row=0, column=2, padx=10, pady=20, sticky='nswe')
        self.button6 = customtkinter.CTkButton(master=self.player_frame, text='>>', command=self.next)
        self.button6.grid(row=0, column=3, padx=(10, 20), pady=20, sticky='nswe')
    def reverse(self):
        pass

    def stop(self):
        pass

    def play(self):
        pass

    def next(self):
        pass

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

        if link != "":
            # print("test")
            yt = YouTube(link)
            song = yt.streams.filter(only_audio=True).first()
            # print("Tytuł: ", yt.title)
            # print("Długość: ", yt.length)
            file = song.download(output_path=self.selected_path)
            base, ext = os.path.splitext(file)
            new_file = base + '.mp3'
            os.rename(file, new_file)
            print('Pobrano ', yt.title)
            # yd=yt.streams.get_highest_resolution()
            # yd.download('.Download')





if __name__ == "__main__":
    mix.init()
    folder = os.path.expanduser("~")
    main_path = os.path.join(folder, "Downloads")


    customtkinter.set_appearance_mode("system")
    customtkinter.set_default_color_theme("green")

    print('good')
    app = App()
    app.mainloop()

