# coding: utf-8
import threading
import time
import math
import os
import sys
import numpy as np
import pyaudio
import wave
import audioop
import termios
import matplotlib.pyplot as plt

fd        = sys.stdin.fileno()
old       = termios.tcgetattr(fd)
new       = termios.tcgetattr(fd)
new[3]   &= ~termios.ICANON
new[3]   &= ~termios.ECHO
path_here = os.getcwd()

class Monitor:
    data1 = np.array([])
    data2 = np.array([])
    d1x = np.arange(0, 10000)/10000

    def __init__(self):
        self.t1 = time.time()

    def graphplot(self,flag1,flag2):
        self.t2 = time.time()
        plt.clf()
        # wave
        plt.subplot2grid((2, 1), (0, 0))
        if flag1==1:
            plt.plot(self.d1x, self.data1)
        else:
            plt.plot(self.d1x, self.data1, label='forestgreen', color='forestgreen')
        plt.axis([0, 1, -0.8, 0.8])
        plt.xlabel("time [s]")
        plt.ylabel("amplitude")
        # wave
        plt.subplot2grid((2, 1), (1, 0))
        if flag2==1:
            plt.plot(self.d1x, self.data2)
        else:
            plt.plot(self.d1x, self.data2, label='forestgreen', color='forestgreen')
        plt.axis([0, 1, -0.8, 0.8])
        plt.xlabel("time [s]")
        plt.ylabel("amplitude")
        #Pause
        plt.pause(.01)

#-------------------------------------------------------------------------------
class Trigger():
    def __init__(self, input_device, output_device): #デフォルトでinitつく
        self.CHUNK = 128
        self.rate=10000
        self.flag=0
        self.vol=1.05 ##################### 0.58 for p3 (sato)
        self.audio_record = np.array([])
        self.p = pyaudio.PyAudio()
        self.stream_trigger = self.p.open(
                        format = pyaudio.paInt16,
                        channels=1,
                        rate=self.rate,
                        frames_per_buffer=self.CHUNK,
                        input_device_index = input_device,
                        output_device_index = output_device,
                        input=True,
                        output=True,
                        stream_callback=self.callback)


    # コールバック関数（再生が必要なときに呼び出される）
    def callback(self, in_data, frame_count, time_info, status):
        buffer = np.frombuffer(in_data, dtype='int16')
        self.audio_record = np.append(self.audio_record, buffer/32768.0)
        if self.flag ==1:
             vol=self.vol
        if self.flag ==0:
             vol=0
        
        # sub = np.frombuffer(in_data, dtype='int16')
        sub = np.array(buffer,dtype='float16') * vol
        out_data = np.array(sub,dtype='int16')
        return (out_data, pyaudio.paContinue)

    def close(self):
        f = open('output_1.txt', 'w')
        for x in self.audio_record:
            f.write(str(x) + "\n")
        f.close()
        self.p.terminate()

#-------------------------------------------------------------------------------


def thr():
    termios.tcsetattr(fd, termios.TCSANOW, new)
    while 1:
        try:
            res = sys.stdin.read(1)
            if res == "1":
                print("-------------熟練者")
                tr1.flag = 1
                tr2.flag = 0
            elif res == "2":
                print("-------------学習者")
                tr1.flag = 0
                tr2.flag = 1
            elif res == "3":
                tr1.vol = tr1.vol-0.01
                print("-------------")
                print(tr1.vol)
            elif res == "4":
                tr1.vol = tr1.vol+0.01
                if tr1.vol>1.5:
                    tr1.vol=1.5
                print("-------------")
                print(tr1.vol)
            elif res == "5":
                tr2.vol = tr2.vol-0.01
                print("-------------")
                print(tr2.vol)
            elif res == "6":
                tr2.vol = tr2.vol+0.01
                if tr2.vol>1.5:
                    tr2.vol=1.5
                print("-------------")
                print(tr2.vol)
            elif res == '9':
                # termios.tcsetattr(fd, termios.TCSANOW, old)
                tr1.stream_trigger.stop_stream()
                tr2.stream_trigger.stop_stream()
                tr1.stream_trigger.close()
                tr2.stream_trigger.close()
                tr1.close()
                tr2.close()
                sys.exit()
        except:
            break

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    moni = Monitor()
    # ディスプレイあり
    # expert_input=2
    # expert_output=7
    # user_input=4
    # user_output=5

    # ディスプレイなし
    expert_input=1
    expert_output=4
    user_input=3
    user_output=2

    # 無線
    # expert_input=7
    # expert_output=6
    # user_input=5
    # user_output=2

    tr1 = Trigger(expert_input,expert_output)
    tr2 = Trigger(user_input,user_output)
    tr1.flag=0
    tr2.flag=0
    

    th = threading.Thread(target=thr, daemon=True)
    th.start()

    # tr = Trigger() #tr=class trigger
    tr1.stream_trigger.start_stream()
    tr2.stream_trigger.start_stream()

    while tr1.stream_trigger.is_active():
        try:
            #moni.data1=tr1.audio_record[-tr1.rate:]
            #moni.data2=tr2.audio_record[-tr2.rate:]
            #moni.graphplot(tr1.flag,tr2.flag)
            time.sleep(1)
        except:
            pass
#        try:
#            print("...\n")
#            time.sleep(1)
#        except KeyboardInterrupt:
#            break

    # ストリーミングを止める場所
