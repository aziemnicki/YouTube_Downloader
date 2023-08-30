from pytube import YouTube
import os
import customtkinter
from tkinter import filedialog, Tk
from sys import argv


folder = os.path.expanduser("~")
path = os.path.join(folder, "Downloads")

customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("green")

root = customtkinter.CTk()
root.title("Music Downloader")

root.geometry("700x350")

def download():
    link = entry1.get()
    if link != "":
        # print("test")
        yt = YouTube(link)
        song = yt.streams.filter(only_audio=True).first()
        # print("Tytuł: ", yt.title)
        # print("Długość: ", yt.length)
        file = song.download(output_path=path)
        base, ext = os.path.splitext(file)
        new_file = base + '.mp3'
        os.rename(file, new_file)
        print('Pobrano ', yt.title)
        # yd=yt.streams.get_highest_resolution()
        # yd.download('.Download')

def foldery():
    Tk.filename = filedialog.askopenfilename(initialdir=path, title="Wybierz folder")


frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=10, fill="both", expand=True)
# button_frame = customtkinter.CTkFrame(master=frame)
# button_frame.pack(pady=20, padx=10, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="Tu wklej link do piosenki na YouTube", font=("Roboto", 24))
label.pack(pady=12, padx=10)
entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="Link", width=400, height=50)
entry1.pack(pady=2, padx=10)

label2 = customtkinter.CTkLabel(master=frame, text='Folder w którym będzie plik (domyślnie "Pobrane")', font=("Roboto", 12))
label2.pack(pady=2, padx=10)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text="Lokalizacja", width=400)
entry2.pack(pady=2, padx=10, side="top")
button1 = customtkinter.CTkButton(master=frame, text="Otwórz folder", command=foldery)
button1.pack(pady=12, padx=10, side="top")
button2 = customtkinter.CTkButton(master=frame, text="Pobierz", command=download)
button2.pack(pady=12, padx=10, side="bottom")


root.mainloop()

