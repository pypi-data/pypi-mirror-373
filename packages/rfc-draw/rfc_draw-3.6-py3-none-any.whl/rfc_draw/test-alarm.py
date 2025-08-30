import pygame, threading, time

class alarm():
    def big_bell(self):
        pygame.mixer.music.load("BSB-counter-bell.wav")
        pygame.mixer.music.play(loops=0)
        ##playsound.playsound("/home/nevil/n-backup/BSB-counter-bell.wav")
        
    def sound_bell(self):
        bell_thread = threading.Thread(target=self.big_bell, args=(()))
        bell_thread.start()

    def sound_alarm(self):
        pygame.mixer.init()
        for n in range(5):
            print("*")
            self.sound_bell()
            time.sleep(1.0)
    
#start_t = timer()
al = alarm()
al.sound_alarm()
