# Terminal Car Controller
# F1r3f0x - 2017

from gpiozero import Motor
import curses
from time import sleep

def define_colors():
    curses.init_pair(1,curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    curses.init_pair(2,curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3,curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(4,curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(5,curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(6,curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(7,curses.COLOR_YELLOW, curses.COLOR_WHITE)
    curses.init_pair(8,curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(9,curses.COLOR_YELLOW, curses.COLOR_MAGENTA)

    return 9

def update_strings(window, draw_buffer, refresh=True):
    """
    Draws the strings with addstr for in the array. Used for drawing on a loop.
        :param window: Window to draw the strings into.
        :param draw_buffer: Tupple with the strings to draw (use unpack)
    """
    for to_draw in draw_buffer:
        try:
            window.addstr(*to_draw)
        except:
            pass
    window.noutrefresh()

def get_input(window, prompt_y, prompt_x, prompt_text, length):
    """
    Draws a prompt, and gets a string from a bottom new line
        :param window: window to draw prompt and get the input
        :param prompt_y: 
        :param prompt_x: 
        :param prompt_text: 
        :param length: lenght of chars to get
    """
    curses.echo()
    getting = True
    while getting:
        try:
            window.addstr(prompt_y, prompt_x, prompt_text)
            window.refresh()
            s = window.getstr(prompt_y + 1, prompt_x, length)
            s = s.decode('ascii')
            getting = False
        except:
            window.addstr(prompt_y+2, prompt_x, "Bad Input! - ASCII only :(")
            window.refresh()
            window.getkey()
            window.erase()
    window.erase()
    curses.noecho()
    return s

def main(stdscr):
    """
    Main function
        :param stdscr: standard screen
    """
    # Clear screen
    stdscr.clear()
    # Get terminal size
    stdscr.refresh()
    # Hides the cursor
    curses.curs_set(False)

    # Define color pairs
    COLORS = define_colors()

    # Define borders "object"
    chkbd_border = (
            curses.ACS_CKBOARD, #l
            curses.ACS_CKBOARD, #lt
            curses.ACS_CKBOARD, #t
            curses.ACS_CKBOARD, #rt
            curses.ACS_CKBOARD, #r
            curses.ACS_CKBOARD, #rb
            curses.ACS_CKBOARD, #b
            curses.ACS_CKBOARD) #lb

    # Define Windows
    control_window = curses.newwin(6,45,14,2)
    control_window.bkgd(' ',curses.color_pair(8))

    WINDOWS = (control_window, stdscr)

    # Strings buffer to draw on main loop
    stdscr_buffer = []
    controls_buffer = []

    stdscr.bkgd(' ', curses.color_pair(8))
    getting_pins = True
    while getting_pins:
        try:
            fwd_left_pin = int(get_input(stdscr,2,1,"Motor Left - Forwards pin (GPIO):",2))
            bwd_left_pin = int(get_input(stdscr,2,1,"Motor Left - Backwards pin (GPIO):",2))
            fwd_right_pin = int(get_input(stdscr,2,1,"Motor Right - Forwards pin (GPIO):",2))
            bwd_right_pin = int(get_input(stdscr,2,1,"Motor Right - Backwards pin (GPIO):",2))
            getting_pins = False
        except ValueError:
            stdscr.addstr(3,1, "Bad Input!, pins are numbers only. ")
            stdscr.refresh()
            stdscr.getkey()
            stdscr.erase()
    stdscr.bkgd(' ', curses.color_pair(0))
    
    motor_left = Motor(fwd_left_pin, bwd_left_pin)
    motor_right = Motor(fwd_right_pin, bwd_right_pin)
    speed = 1

    pressed_key = 0
    str_key = ''

    # Deactivate wait-for-input
    stdscr.nodelay(True)

    while True:

        ## Getting Input
        try:
            key_char = stdscr.getch()
            if key_char != -1:
                pressed_key = key_char
                str_key = str(chr(key_char)).lower()
            else:
                str_key = 'n/a'
        except curses.error:
            key_char = None

        # Both Motors
        if str_key == 'w':
            motor_left.forward(speed)
            motor_right.forward(speed)
        elif str_key == 's':
            motor_left.backward(speed)
            motor_right.backward(speed)
        elif str_key == 'a':
            motor_left.backward(speed)
            motor_right.forward(speed)
        elif str_key == 'd':
            motor_left.forward(speed)
            motor_right.backward(speed)
        # Motor 1 
        elif str_key == 't':
            motor_left.forward(speed)
        elif str_key == 'g':
            motor_left.backward(speed)
        # Motor 2
        elif str_key == 'y':
            motor_right.forward(speed)
        elif str_key == 'h':
            motor_right.backward(speed)
        else:
            motor_left.stop()
            motor_right.stop()

        # Speed control
        if str_key == 'o': # o
            if speed < 1:
                speed += 0.1
        elif str_key == 'l': # l
            if speed > 0.1:
                speed -= 0.1

        if key_char == 3 : # ctrl+c
            curses.endwin()
            quit()

        ## Updating screen data
        # stdscreen
        stdscr.erase()
        stdscr_buffer.clear()
        stdscr_buffer.append([1,2, "Terminal Car Controller Program", curses.A_BOLD])
        stdscr_buffer.append([curses.LINES - 3, curses.COLS - 10 , "@F1r3f0x"])
        stdscr_buffer.append([3,2, 'Speed: ' + '{:.1f}'.format(speed)])
        stdscr_buffer.append([4,2, "Last key pressed: " + chr(pressed_key), curses.A_BOLD])
        stdscr_buffer.append([10,2, "Left Motor Pins: Fwd: {} || Bwd: {}".format(fwd_left_pin, bwd_left_pin)])
        stdscr_buffer.append([11,2, "Right Motor Pins: Fwd: {} || Bwd: {}".format(fwd_right_pin, bwd_right_pin)])
        stdscr_buffer.append([21,2, "CTRL+C to exit...", curses.A_REVERSE])
        stdscr.border(*chkbd_border)
        update_strings(stdscr, stdscr_buffer)

        # controls
        control_window.erase()
        controls_buffer.clear()
        controls_buffer.append([1,1, "Motors: WASD", curses.A_BOLD])
        controls_buffer.append([2,1, "Motor Left: T - forwards || G - Backwards"])
        controls_buffer.append([3,1, "Motor Right: Y - forwards || H - Backwards"])
        controls_buffer.append([4,1, "Speed: O - +0.1 || L - -0.1"])
        control_window.border(*chkbd_border)
        update_strings(control_window, controls_buffer)

        ## Drawing to screen
        curses.doupdate()

        sleep(1/30)

if __name__ == '__main__':
    curses.wrapper(main)
