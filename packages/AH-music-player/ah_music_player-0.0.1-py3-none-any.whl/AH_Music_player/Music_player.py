from tkinter import Tk, mainloop, Button, filedialog, messagebox, Scale, Frame, LabelFrame, Label
from pygame import mixer
from PIL import Image, ImageTk
from threading import Thread
from time import sleep
BTN_SIZE = 128
BTN_CONFIG = {
    "font": ("", 24),
    "padx": 8,
    "pady": 8,
}
BG = "#333333"
FG = "green"


class MyMusicPlayer():
    def __init__(self, root,
                 sound_volume=50,
                 bg=BG,
                 fg=FG,
                 play_image_address="music_player images/play.png",
                 play_pause_address="music_player images/puase.png",
                 stop_image_address="music_player images/stop.png",
                 title="My music player"):
        mixer.init()
        if sound_volume > 100:
            sound_volume = 100
        elif sound_volume < 0:
            sound_volume = 0
        self.title = title
        self.bg = bg
        self.fg = fg
        self.sound_volume = sound_volume
        self.is_first_click = True
        self.is_playing = False
        self.playing_time = 0
        self.file_name = ""
        self.length_music = 0
        self.player = mixer.music
        self.player.set_volume(sound_volume/100)
        self.root = root
        self.frame_music_player = LabelFrame(
            self.root, text=self.title, bg=self.bg, fg=self.fg)

        self.play_image_address = play_image_address
        self.pause_image_address = play_pause_address
        self.stop_image_address = stop_image_address
        self.img_play = Image.open(self.play_image_address)
        self.img_pause = Image.open(self.pause_image_address)
        self.img_stop = Image.open(self.stop_image_address)

        self.img_play = self.img_play.resize((BTN_SIZE-10, BTN_SIZE-10))
        self.img_pause = self.img_pause.resize((BTN_SIZE-10, BTN_SIZE-10))
        self.img_stop = self.img_stop.resize((BTN_SIZE-10, BTN_SIZE-10))

        self.img_play = ImageTk.PhotoImage(self.img_play)
        self.img_pause = ImageTk.PhotoImage(self.img_pause)
        self.img_stop = ImageTk.PhotoImage(self.img_stop)

        self.btn_browse = Button(self.frame_music_player, bg=self.bg, activeforeground=self.bg, fg=self.fg, cnf=BTN_CONFIG,
                                 text="...", activebackground=self.fg, command=self.load_music)
        self.btn_play_pause = Button(self.frame_music_player, bg=self.bg, activeforeground=self.bg, fg=self.fg, cnf=BTN_CONFIG,
                                     image=self.img_play, activebackground=self.fg, command=self.play_pause)
        self.btn_stop = Button(self.frame_music_player, activeforeground=self.bg, bg=self.bg, fg=self.fg,
                               cnf=BTN_CONFIG, activebackground=self.fg, image=self.img_stop, command=self.stop)
        self.lbl_sound = Label(self.frame_music_player,
                               bg=self.bg, fg=self.fg, text="Sound")
        self.scale_sound = Scale(self.frame_music_player, activebackground=self.fg, highlightbackground=self.bg, troughcolor=self.bg, bg=self.bg, fg=self.fg, orient="horizontal", from_=0,
                                 to=100, command=self.change_volume)
        self.scale_sound.set(sound_volume)
        self.scale_time = Scale(self.frame_music_player, activebackground=self.fg, highlightbackground=self.bg, troughcolor=self.bg, bg=self.bg, fg=self.fg, orient="horizontal", from_=0,
                                command=self.play_here)
        self.lbl_time = Label(self.frame_music_player,
                              bg=self.bg, fg=self.fg, text="Time",)

        self.scale_time.bind("<ButtonRelease-1>", self.manage)
        self.btn_browse          .place(x=10*1+BTN_SIZE*0, y=10,
                                        width=BTN_SIZE, height=BTN_SIZE)
        self.btn_play_pause      .place(x=10*2+BTN_SIZE*1, y=10,
                                        width=BTN_SIZE, height=BTN_SIZE)
        self.btn_stop            .place(x=10*3+BTN_SIZE*2, y=10,
                                        width=BTN_SIZE, height=BTN_SIZE)
        self.scale_sound         .place(x=10*1+BTN_SIZE*0.5, y=10 +
                                        BTN_SIZE, width=BTN_SIZE*2.5+10*3, height=BTN_SIZE/2)
        self.lbl_sound          .place(x=10*1+BTN_SIZE*0, y=10 +
                                       BTN_SIZE, width=BTN_SIZE/2, height=BTN_SIZE/2)
        self.scale_time         .place(x=10*1+BTN_SIZE*0.5, y=10 +
                                       BTN_SIZE+BTN_SIZE/2, width=BTN_SIZE*2.5+10*3, height=BTN_SIZE/2)
        self.lbl_time           .place(x=10*1+BTN_SIZE*0, y=10 +
                                       BTN_SIZE+BTN_SIZE/2, width=BTN_SIZE/2, height=BTN_SIZE/2)

    def update_time(self):
        while True:
            while self.is_playing:
                self.scale_time.set(self.playing_time)
                self.playing_time += 1
                sleep(1)
            while not self.is_playing:
                self.playing_time = round(self.player.get_pos()/1000)
                sleep(1)

    def load_music(self):
        self.temp = filedialog.askopenfilename()
        if self.temp in ["", None, ()]:
            return
        self.file_name = self.temp
        self.is_playing = False
        self.playing_time = 0
        self.scale_time.set(0)
        self.btn_play_pause.config(image=self.img_play)
        self.player.load(self.file_name)
        self.temp = mixer.Sound(self.file_name)
        self.length_music = round(self.temp.get_length())
        self.scale_time.config(from_=0, to=self.length_music)
        self.player.play()
        self.player.pause()

    def play_pause(self):
        if self.file_name in ["", None, ()]:
            messagebox.showerror(
                "Error", "You must choose an audio file first")
            return
        if self.is_playing == True:
            self.is_playing = False
            self.player.pause()
            self.playing_time = round(self.player.get_pos()/1000)
            self.btn_play_pause.config(image=self.img_play)
            # btn_play_pause["image"] = img_play
        else:
            self.is_playing = True
            self.btn_play_pause.config(image=self.img_pause)
            self.playing_time = round(self.scale_time.get()/1000)
            self.player.play(start=self.playing_time)
            # btn_play_pause["image"] = img_pause
            if self.is_first_click:
                self.is_first_click = False
                self.th1 = Thread(target=self.update_time, daemon=True)
                self.th1.start()

    def stop(self):
        if self.length_music > 0:
            self.player.stop()
            self.player.play()
            self.player.pause()
        self.scale_time.set(0)
        self.sound_volume = 50
        self.scale_sound.set(self.sound_volume)
        self.is_playing = False
        self.playing_time = 0
        self.scale_time.set(0)
        self.btn_play_pause.config(image=self.img_play)

    def change_volume(self, event):
        self.sound_volume = int(event)
        self.player.set_volume(self.sound_volume/100)

    def manage(self, event):
        if self.is_playing:
            self.player.play(start=self.playing_time)

    def play_here(self, event):
        if self.length_music > 0:
            self.playing_time = int(event)
            self.scale_time.set(self.playing_time)
        # player.set_pos(float(event)*1000)

    def place(self, x=10*1, y=10, width=BTN_SIZE * 3+10*5, height=10*4+BTN_SIZE*2):
        self.frame_music_player      .place(
            x=x, y=y, width=width, height=height)


if __name__ == "__main__":
    root = Tk()
    root.geometry("1000x400+100+100")
    mplayer = MyMusicPlayer(root)
    mplayer.place()

    root.mainloop()
