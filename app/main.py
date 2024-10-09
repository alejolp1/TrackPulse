import flet as ft
import os
import pygame as pg
import time
import threading
from mutagen.mp3 import MP3

def app(page: ft.Page):
    ## PROPERTIES
    page.title = "TrackPulse"
    page.bgcolor = "#0C101C"
    page.window.resizable = True
    page.window.height = 640
    page.window.width = 480
    
    pg.mixer.init()
    
    ## MUSIC FOLDER
    musicFolder = os.path.join(os.path.expanduser("~"), "Music")
    
    ## PLAYLIST
    playlist = [os.path.join(musicFolder, file) for file in os.listdir(musicFolder) if file.endswith(".mp3")]
    
    ## SONG IN THE PLAYLIST?
    if not playlist:
        raise Exception("No tracks.") 
    
    ## ACTUAL INDEX
    global crrntTrack_index
    crrntTrack_index = 0

    def crrntTrack():
        if len(playlist) > 0:
            pg.mixer.music.load(playlist[crrntTrack_index])
            pg.mixer.music.play()
            # Obtener la duración de la canción
            audio = MP3(playlist[crrntTrack_index])
            timeSlider.max = int(audio.info.length)  # Establecer el max del slider a la duración de la canción
            resetPlayPauseButton()
            updateTrackText()
            # Iniciar hilo para actualizar el slider
            threading.Thread(target=updateSlider, daemon=True).start()
        else:
            print("No MP3 files")
    
    ## UPDATE THE TRACK NAME IN THE TEXT
    current_track_text = ft.Text(
        value="",
        color="white", 
        size=12,
    )
    
    def updateTrackText():
        current_track_name = os.path.basename(playlist[crrntTrack_index])  ## FILE NAME
        current_track_text.value = f"Playing: {current_track_name}"
        page.title = f"TrackPulse - {current_track_name}"  ## SET TITLE TO CURRENT TRACK
        page.update()        
    
    ## NEXT TRACK FUNCTION
    def nextTrack(s=None):
        global crrntTrack_index 
        crrntTrack_index += 1
        timeSlider.value=0
        if crrntTrack_index >= len(playlist):
            crrntTrack_index = 0
        print(f"Playing next track: {playlist[crrntTrack_index]}")
        crrntTrack()
    
    ## RESET PLAY/PAUSE BUTTONS WHEN SONG CHANGES
    def resetPlayPauseButton():
        if pg.mixer.music.get_busy():
            btnB.icon = ft.icons.PAUSE
            btnB.icon_color = "#F0F6FC"
            btnB.disabled = False
        else:
            btnB.icon = ft.icons.PLAY_DISABLED
            btnB.disabled = True
        page.update()
    
    ## PREVIOUS TRACK FUNCTION
    def previousTrack(s=None):
        global crrntTrack_index 
        timeSlider.value=0
        crrntTrack_index -= 1
        if crrntTrack_index < 0:
            crrntTrack_index = len(playlist) - 1
        print(f"Playing previous track: {playlist[crrntTrack_index]}")
        crrntTrack()
    
    ## UPDATE PLAY/PAUSE BUTTON
    def tgglBtn(pp):
        if pp.control.data == "A":
            btnB.icon = ft.icons.PLAY_ARROW
            pp.control.data = "B"
            pg.mixer.music.pause()
        else:
            btnB.icon = ft.icons.PAUSE
            pp.control.data = "A"
            pg.mixer.music.unpause()  
        page.update()
    
    ## STARTER BUTTON TO PAGE.ADD
    btnB = ft.IconButton( 
        icon=ft.icons.PLAY_DISABLED,
        disabled=True,
        on_click=tgglBtn,
        data="A",
        icon_color="#ADADAD"
    )

    ## NEXT BUTTON
    nxtBtn = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_ROUNDED,
        on_click=nextTrack,
        icon_color="#F0F6FC",
    )

    ## BACK BUTTON
    prvBtn = ft.IconButton(
        icon=ft.icons.ARROW_BACK_ROUNDED,
        on_click=previousTrack,
        icon_color="#F0F6FC"
    )
    
    ## FILE SELECTOR
    def playSelectedTrack(filePath):
        global crrntTrack_index
        crrntTrack_index = playlist.index(filePath)
        crrntTrack()
    
    def listFiles():
        file_buttons = []
        if os.path.exists(musicFolder):
            for item in os.listdir(musicFolder):
                itemPath = os.path.join(musicFolder, item)
                if itemPath.endswith('.mp3'):
                    file_buttons.append(
                        ft.TextButton(
                            text=f"{item}",
                            on_click=lambda event, path=itemPath: playSelectedTrack(path),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(12),
                                bgcolor=ft.colors.TRANSPARENT,
                                color="white",
                                padding=12,
                            ),
                        )
                    )
        else:
            file_buttons.append(ft.Text("Folder doesn't exist."))

        return ft.ListView(
            controls=file_buttons,
            expand=True,
            auto_scroll=False
        )
    
    ## SPECIFIC TIME
    def seekAudio(position):
        pg.mixer.music.set_pos(position)
    
    ## SLIDER TIMER
    timeSlider = ft.Slider(
        min=0,
        max=100,
        value=0,
        on_change=lambda e: seekAudio(e.control.value),
        width=300,
    )
    
    ## UPDATE THE SLIDER
    def updateSlider():
        while pg.mixer.music.get_busy():
            currentPosition = pg.mixer.music.get_pos() / 1000 
            timeSlider.value = currentPosition  # SLIDER UPDATE
            page.update()
            time.sleep(1)
    
    ## RESET THE SLIDER
    def resetSlider():
        timeSlider.value = 0
        page.update()
    
    
    ## BOTTOM CONTAINER
    bottomContainer = ft.Container(
        bgcolor="TRANSPARENT",
        height=60,
        border_radius=12,
        expand=False,
        content=ft.Row(
            [
                prvBtn,
                btnB,
                nxtBtn,
                timeSlider
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

    ## REMAINING SPACE CONTAINER
    remainingContainer = ft.Container(
        bgcolor="TRANSPARENT",
        expand=True,
        content=ft.Column(
            [   
                listFiles(),
                current_track_text,
            ],
            spacing=10,
        ),
    )

    page.add(
        ft.Column(
            [
                remainingContainer,
                bottomContainer,
            ],
            expand=True,
            spacing=10,
        ),
    )


ft.app(target=app)

