#!/usr/bin/env python
# rovio.py v0.0.1 alpha -- text-mode Rovio client for Linux
#
# a Rudforce Intragalactic endeavor
# http://www.rudforce.com/
#
# copyleft 2008 Del Rudolph
# see http://www.gnu.org/copyleft/gpl.html for latest license

# Set up the important stuff
# need to make this an interactive, first-run thing
# that gives option of saving to a config file
#
# theurl is in the form [IP_number:Port] (or just IP_Number if not using a port)
# this should be Rovio's LAN IP, running this over the internets would probably
# be too laggy to bother with
theurl = 'rovio.ip.number:port'

# an Admin user account on Rovio. Needs to be Admin for all functions to work!
username = 'adminUsername'

# said Admin user's password
password = 'adminPassword'

# nothing needs set below here, unless you wanna mess with it :)
################################################################

import curses, curses.wrapper
import urllib2
import time
import threading, Queue
import subprocess, os

# had to use DefaultRealm because Rovio uses different realm for Admin
passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, theurl, username, password)
authhandler = urllib2.HTTPBasicAuthHandler(passman)
opener = urllib2.build_opener(authhandler)
urllib2.install_opener(opener)

# fix these so they're figured from updateStats?
# nope, haven't figured out how to tell if headlight is already on
light = '0'

# set up some globals
battList = [126,126,126,126,126]
emailok = 0
vlcon = 0
head = 1

# set up all the curses UI stuff
import curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
curses.curs_set(0)

mainwin = curses.newwin(21, 66, 0, 0)
mainwin.border()
mainwin.overwrite(stdscr)

msgwin = curses.newwin(7, 13, 0, 66)
msgwin.border()
msgwin.addstr(1, 1, "   Rovio   ", curses.A_REVERSE);
msgwin.overwrite(stdscr)

lightwin = curses.newwin(7, 13, 7, 66)
lightwin.border()
lightwin.addstr(1, 2, "  _")
lightwin.addstr(2, 2, " / |")
lightwin.addstr(3, 2, "(> |")
lightwin.addstr(4, 2, " \_|")
lightwin.overwrite(stdscr)

headwin = curses.newwin(7, 13, 14, 66)
headwin.border()
headwin.addstr(4, 1, "<I______/")
headwin.addstr(5, 2, '(_)---`=[]')
headwin.overwrite(stdscr)

battwin = curses.newwin(3, 26, 21, 1)
battwin.border()
battwin.addstr(0, 1, "Battery")
battwin.overwrite(stdscr)

sswin = curses.newwin(3, 26, 21, 27)
sswin.border()
sswin.addstr(0, 1, "Signal")
sswin.overwrite(stdscr)

wifiwin = curses.newwin(3, 26, 21, 53)
wifiwin.border()
wifiwin.addstr(0, 1, "Wifi")
wifiwin.overwrite(stdscr)

# bunch o' functions from here

# found at http://code.activestate.com/recipes/65222/ and tweaked a bit
# using a thread, run a function every n seconds
class PeriodicExecutor(threading.Thread):
    def __init__(self,sleep,func):
        self.func = func
        self.sleep = sleep
        threading.Thread.__init__(self,name = "PeriodicExecutor")
        self.setDaemon(1)
    def run(self):
        while 1:
            time.sleep(self.sleep)
            apply(self.func)

def spawnVlc():
    global vlcon
    if os.access("/usr/bin/vlc", os.X_OK) and vlcon == 0:
        FNULL = open('/dev/null', 'w')
        vlcon = subprocess.Popen(["/usr/bin/vlc", "rtsp://"+username+":"+password+"@"+theurl+"/webcam"], stderr=FNULL, stdout=FNULL).pid

def makeProgBar(width,min,max,val):
    if val < min: val = min
    if val > max: val = max

    diff = float(val - min)
    span = float(max - min)

    # figure percent done
    pDone = (diff / span) * 100.0
    pDone = round(pDone)
    pDone = int(pDone)

    # Figure out how many # in percent done
    numEq = (pDone / 100.0) * width
    numEq = int(round(numEq))

    # build bar with = and -
    bar = '#'*numEq + '-'*(width-numEq)

    # place percentage in center
    pPlace = (len(bar) / 2) - len(str(pDone))
    pString = str(pDone) + "%"

    # slice the percentage into the bar
    bar = bar[0:pPlace] + pString + bar[pPlace+len(pString):]

    return str(bar)

def updateVid():
    # get vid, print to screen
    # expects ascii converter to be /usr/bin/jp2a
    picUrl = "http://"+username+":"+password+"@"+theurl+"/Jpeg/CamImg1234.jpg"
    output = subprocess.Popen(["/usr/bin/jp2a", "--width=64 --height=20", picUrl], stdout=subprocess.PIPE).communicate()[0]
    imgtext = output.split("\n")
    for i in range(19):
        stdscr.addstr(i+1, 1, imgtext[i])

def returnConfirm(inText):
    shq = curses.newwin(3, 30, 10, 25)
    shq.border()
    shq.addstr(0, 1, "Confirm", curses.A_REVERSE);
    shq.addstr(1, 2, inText, curses.A_BOLD)
    shq.addstr(2, 16, "'y' or 'n'")
    c = shq.getch()
    if c in (ord('y'), ord('Y')):
        shq.clear()
        shq.refresh()
        return 1
    else:
        shq.clear()
        shq.refresh()
        return 0

def headPos(inpos):
    global head
    if inpos == head: return
    data = ""
    # call thing to lower head /rev.cgi?Cmd=nav&action=18&drive=[down=12,mid=13,up=11]
    if inpos == '1' and head != '1':
        data = "12"
        head = "1"
    if inpos == '2' and head != '2':
        data = "13"
        head = "2"
    if inpos == '3' and head != '3':
        data = "11"
        head = "3"
    SendRequest("Cmd=nav&action=18&drive="+data+"")

def setHome():
    if returnConfirm("Overwrite Home position?") == 1:
        SendRequest("Cmd=nav&action=14")

def Light():
    global light
    if light == "1":
        light = "0"
        for i in (2,3,4):
            lightwin.addstr(i, 6, "   ")
        lightwin.refresh()
    else:
        light = "1"
        for i in (2,3,4):
            lightwin.addstr(i, 6, "===")
        lightwin.refresh()
    SendRequest("Cmd=nav&action=19&LIGHT="+light+"")

def updateStats():
    # batt 100=dead in the water, <106 go home, 127 full
    # wifi 0-254
    # nav_ss 0-65535, <5000 no signal, >47000 strong signal
        #Cmd = nav
        #responses = 0|x=-1339|y=-5592|theta=-1.953|room=0|ss=8263
        #|beacon=0|beacon_x=0|next_room=9|next_room_ss=38
        #|state=0|resistance=0|sm=15|pp=0|flags=0005
        #|brightness=6|resolution=3|video_compression=1|frame_rate=20
        #|privilege=0|user_check=1|speaker_volume=15|mic_volume=17
        #|wifi_ss=233|show_time=0|ddns_state=0|email_state=0
        #|battery=126|charging=80|head_position=203|ac_freq=2
    # makeProgBar(width,min,max,val)
    stats = {}
    statstr = SendRequest("Cmd=nav&action=1", 1)
    statstr = statstr.replace("Cmd = nav\nresponses = 0|", '')
    statstr = statstr.replace("\n", "")
    for item in statstr.split('|'):
        a,b = item.split('=')
        stats[a] = b

    global emailok
    emailok = int(stats['email_state'])

    i = 0
    battavg = 0
    del battList[0]
    battList.append(int(stats['battery']))
    for item in battList: i += item
    battavg = i / 5
    battstr = makeProgBar(24, 100, 127, battavg)
    battwin.addstr(1, 1, battstr)
    battwin.refresh()

    if battavg < 108:
        curses.flash()
        msgwin.addstr(5, 1, "Low Battery", curses.A_STANDOUT)
        msgwin.refresh()

    ssstr = makeProgBar(24, 5000, 47000, int(stats['ss']))
    sswin.addstr(1, 1, ssstr)
    sswin.refresh()

    wifistr = makeProgBar(24, 0, 254, int(stats['wifi_ss']))
    wifiwin.addstr(1, 1, wifistr)
    wifiwin.refresh()

    # Going Home state doesn't seem to be used?
    state = ('  Roaming  ', 'Going Home', '  Docking  ', '           ', 'No Connection')
    msgwin.addstr(3, 1, state[int(stats['state'])])
    if int(stats['charging']) > 63: msgwin.addstr(3, 1, "  Docked   ")
    if int(stats['charging']) >= 80: msgwin.addstr(3, 1, " Charging  ")
    msgwin.refresh()

    hp = int(stats['head_position'])
    if hp > 195 and hp < 205:
        head = 1
        headwin.addstr(1, 4, '      ')
        headwin.addstr(2, 3, '      ')
        headwin.addstr(3, 3, "_______")
        headwin.refresh()
    if hp > 130 and hp < 150:
        head = 2
        headwin.addstr(1, 1, '   ___')
        headwin.addstr(2, 1, '  `--.\\')
        headwin.addstr(3, 1, '  ____\\\\_')
        headwin.refresh()
    if hp > 60 and hp < 70:
        head = 3
        headwin.addstr(1, 1, "    '\\")
        headwin.addstr(2, 1, '     \\\\')
        headwin.addstr(3, 3, '____\\\\_')
        headwin.refresh()

def emailImage():
    if emailok == 1:
        # send email
        SendRequest("SendMail")
        msgwin.addstr(3,1, " Photo Sent")
        msgwin.refresh()

# need to clean this up, make it more flexible
def SendRequest(indata, myreturn=0):
    if indata == 'SendMail':
        thefile = '/SendMail.cgi'
        thedata = ""
    else:
        thefile = "/rev.cgi"
        thedata = indata

    req = urllib2.Request("http://"+theurl+thefile, thedata)
    handle = urllib2.urlopen(req)
    if myreturn == 1:
        return handle.read()

def ShowHelp():
    shq = curses.newwin(16, 45, 3, 8)
    shq.border()
    shq.addstr(0, 1, "Help", curses.A_REVERSE);
    shq.addstr(1, 1, "[w] Forward        [s] Backward")
    shq.addstr(2, 1, "[a] Strafe Left    [d] Strafe Right")
    shq.addstr(3, 1, "[q] Rotate Left    [e] Rotate Right")
    shq.addstr(4, 1, "[l] Light          [1,2,3] Head Position")
    shq.addstr(5, 1, "[Arrow Keys] Directional")
    shq.addstr(7, 1, "[h] Go Home        [H] Set Home")
    shq.addstr(9, 1, "[Spacebar] Stop    ") # [p] Preferences goes here
    shq.addstr(10, 1, "[i] Email Image    [v] Start VLC")
    shq.addstr(12, 1, "[x] Quit           [/ or ?] Show Help")
    shq.addstr(14, 1, "     Press any key to continue")

    c = shq.getch()

# just adds a drive command to the queue
# command is in the form "drive_command:speed"
def Drive(command):
    if q.qsize() < 1:
        q.put(command)
    else:
        return

def doUpdate():
    updateVid()
    updateStats()

# this runs in seperate thread
# handles drive commands
def worker():
    tRevUrl = "http://"+theurl+"/rev.cgi"
    while True:
        item = q.get()
        fields = item.split(':')
        mydata = "Cmd=nav&action=18&drive="+fields[0]+"&speed="+fields[1]+""
        myreq = urllib2.Request(tRevUrl, mydata)
        urllib2.urlopen(myreq)
        time.sleep(0.15)

# this runs in seperate thread
# handles periodic refresh of stats and video
def timerThread():
    pe = PeriodicExecutor(1, doUpdate)
    pe.run()

q = Queue.Queue()

t = threading.Thread(target=worker)
t.setDaemon(1)
t.start()

t2 = threading.Thread(target=timerThread)
t2.setDaemon(1)
t2.start()

# now run the actual program loop
while 1:
    stdscr.timeout(500)
    c = stdscr.getch()
    if c in (ord('/'), ord('?')): ShowHelp()
    elif c in (ord('x'), ord('X')):
        if returnConfirm("Exit the program?") == 1: break

    #elif c == curses.KEY_UP: Drive("1:1")
    elif c in (ord('w'), curses.KEY_UP): Drive("1:1")
    #elif c == curses.KEY_DOWN: Drive("2:1")
    elif c in (ord('s'), curses.KEY_DOWN): Drive("2:1")
    #elif c == curses.KEY_LEFT: Drive("3:1")
    elif c in (ord('a'), curses.KEY_LEFT): Drive("3:1")
    #elif c == curses.KEY_RIGHT: Drive("4:1")
    elif c in (ord('d'), curses.KEY_RIGHT): Drive("4:1")
    elif c == ord('q'): Drive("5:5")
    elif c == ord('e'): Drive("6:5")

    elif c == ord('l'): Light()
    elif c == ord('h'): SendRequest("Cmd=nav&action=13")
    elif c == ord('H'): setHome()
    elif c == ord(' '): SendRequest("Cmd=nav&action=17")
    elif c == ord('1'): headPos('1')
    elif c == ord('2'): headPos('2')
    elif c == ord('3'): headPos('3')
    elif c in (ord('v'), ord('V')): spawnVlc()
    elif c in (ord('i'), ord('I')): emailImage()
    #elif c in (ord('p'), ord('P')):   # will eventually run preferences window

# if we get here the program is ending
curses.nocbreak(); stdscr.keypad(0); curses.echo()
curses.endwin()
