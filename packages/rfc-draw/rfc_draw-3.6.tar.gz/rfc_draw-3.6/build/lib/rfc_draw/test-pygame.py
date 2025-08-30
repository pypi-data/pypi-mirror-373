# From GeeksforGeeks web page "How to play sounds in python with tkinter"
# Works properly on nebbiolo :-) :-)
# 1545, Sat 26 Apr 2025 (NZST)

from tkinter import *
import pygame

root = Tk()
root.title("GeeksforGeeks sound player")
root.geometry("500x400")

pygame.mixer.init()

def play():
    pygame.mixer.music.load("BSB-counter-bell.wav")
    pygame.mixer.music.play(loops=0)

title = Label(root,text="GeeksforGeeks", bd=9, relief=GROOVE,
    font=("times new roman",50,"bold"), bg="white", fg="green")
title.pack(side=TOP, fill=X)

play_button=Button(root, text="Play", font=("Helvetica",32),
                   command=play)
play_button.pack(pady=20)

root.mainloop()
