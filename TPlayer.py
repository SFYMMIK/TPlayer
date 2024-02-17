import os
import curses
import time
import pygame
import threading

# Function to play audio file
def play_audio(filename, start_pos=0.0):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(start=start_pos)

# Function to handle playback in a separate thread
def playback_thread(filename, playlist, current_index, start_pos=0.0):
    play_audio(filename, start_pos)
    time.sleep(pygame.mixer.Sound(filename).get_length() - start_pos)
    next_index = (current_index + 1) % len(playlist)
    play_next_song(playlist[next_index], playlist, next_index)

# Function to play next song
def play_next_song(filename, playlist, current_index, start_pos=0.0):
    global playback_thread_ref, current_song, duration
    current_song = os.path.basename(playlist[current_index])
    duration = format_duration(pygame.mixer.Sound(playlist[current_index]).get_length())
    playback_thread_ref = threading.Thread(target=playback_thread, args=(filename, playlist, current_index, start_pos))
    playback_thread_ref.start()

# Function to format duration into minutes and seconds
def format_duration(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}min {seconds}sec"

# Function to display UI
def display_ui(stdscr, status, duration, current_song):
    stdscr.clear()
    stdscr.addstr("TPlayer\n")
    stdscr.addstr("---------------------\n")
    stdscr.addstr("1. Enter music directory\n")
    stdscr.addstr("2. Play\n")
    stdscr.addstr("3. Pause (p)\n")
    stdscr.addstr("4. Unpause (u)\n")
    stdscr.addstr("5. Next Song (n)\n")
    stdscr.addstr("6. Previous Song (r)\n")
    stdscr.addstr("7. Exit (q)\n")
    stdscr.addstr("---------------------\n")
    stdscr.addstr("Status: " + status + "\n")
    stdscr.addstr("Duration: " + duration + "\n")
    stdscr.addstr("Current Song: " + current_song + "\n")
    stdscr.refresh()

# Main function
def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()

    music_dir = None
    playlist = []
    current_index = -1
    status = "No music loaded"
    playback_thread_ref = None
    duration = ""
    current_song = ""

    pygame.init()
    pygame.mixer.init()

    paused = False
    paused_position = 0.0

    while True:
        display_ui(stdscr, status, duration, current_song)
        key = stdscr.getch()

        if key == ord('1'):
            curses.echo()
            stdscr.clear()
            stdscr.addstr("Enter music directory: ")
            stdscr.refresh()
            music_dir = stdscr.getstr().decode('utf-8')
            curses.noecho()

            # Load music files from the directory
            playlist = [os.path.join(music_dir, file) for file in os.listdir(music_dir) if file.endswith((".mp3", ".wav", ".wma", ".flac"))]
            current_index = 0
            status = "Music loaded"

        elif key == ord('2'):
            if playlist:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    if playback_thread_ref is not None:
                        playback_thread_ref.join()
                duration = format_duration(pygame.mixer.Sound(playlist[current_index]).get_length())
                play_next_song(playlist[current_index], playlist, current_index)
                status = "Playing"
                paused = False
                current_song = os.path.basename(playlist[current_index])

        elif key == ord('p'):
            if pygame.mixer.music.get_busy() and not paused:
                pygame.mixer.music.pause()
                paused_position = pygame.mixer.music.get_pos() / 1000.0
                pygame.mixer.music.stop()
                status = "Paused"
                paused = True

        elif key == ord('u'):
            if paused:
                play_next_song(playlist[current_index], playlist, current_index, paused_position)
                status = "Playing"
                paused = False

        elif key == ord('n'):
            if playlist:
                current_index = (current_index + 1) % len(playlist)
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                duration = format_duration(pygame.mixer.Sound(playlist[current_index]).get_length())
                play_next_song(playlist[current_index], playlist, current_index)
                status = "Playing"
                paused = False
                current_song = os.path.basename(playlist[current_index])

        elif key == ord('r'):
            if playlist:
                current_index = (current_index - 1) % len(playlist)
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                duration = format_duration(pygame.mixer.Sound(playlist[current_index]).get_length())
                play_next_song(playlist[current_index], playlist, current_index)
                status = "Playing"
                paused = False
                current_song = os.path.basename(playlist[current_index])

        elif key == ord('q'):
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                if playback_thread_ref is not None:
                    playback_thread_ref.join()
            break

# Run the main function
if __name__ == "__main__":
    curses.wrapper(main)
