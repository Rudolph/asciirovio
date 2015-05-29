 rovio.py v0.0.1 alpha -- text-mode Rovio client for Linux

 a Rudforce Intragalactic endeavor
 http://www.rudforce.com/

 copyleft 2008 Del Rudolph
 see http://www.gnu.org/copyleft/gpl.html for latest license


## Text-mode Rovio client for Linux ##
Rovio works just fine with Linux because it's controls are browser based. I did
think it would be quite amusing though to have a special Linux only interface
to the Rovio, naturally text based and running in a terminal. Since the idea of
it amused me so, I went ahead and made one. Because I like free software I'll
provide it to the world.


## Requirements ##
Python ( www.python.org ) -- I used 2.5, from the Ubuntu repos
jp2a ( jp2a.sf.net ) -- converts video to ascii, from Ubuntu repos
VLC ( www.videolan.org/vlc/ ) -- optional, for "real" video display, Ubuntu repos

## Configuration ##
Open up rovio.py in a text editor and edit the following;

# the url of your Rovio, including port if used
theurl = '192.168.0.22:1138'

# an Admin user account on Rovio. Needs to be an admin for all functions to work!
username = 'adminUsername'

# said Admin user's password
password = 'adminPassword'

And that's it!


## Installation ##
Copy rovio.py to somewhere in your path (like ~/bin/), make sure it's executable,
and run it (type rovio.py on your command line). Or, if it's not in your path,
make sure it's executable, and run it (type /path/to/rovio.py on your command
line).


## Usage ##
All commands are from the keyboard. Here's a list (so far) of what's available.
You can see a help screen by hitting the / or ? key, which shows exactly what I'm
about to say here.

        w - moves forward
        a - strafe left
        s - move backward
        d - strafe right
        q - rotate left
        e - rotate right
        [arrow keys] -  up, down, strafe left, strafe right

        l - turns headlight on/off

        1 - head down
        2 - head mid
        3 - head up

        h - (lowercase) go home and dock
        H - (uppercase) set home position

        spacebar - STOP!

        i - email image (if configured)
        v - spawn VLC in another process (if installed)

        x - quit the program

        / or ? - show Help

All the commands are case insensitive, except for 'h' and 'H'.


## TODO ##
Write the Todo's

## Changelog ##
v0.0.1 - Oct 16, 2008
    initial release
    posted to robocommunity.com
