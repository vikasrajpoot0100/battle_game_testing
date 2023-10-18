from tkinter import *
import tkinter as tk
import tkinter.messagebox as mbox
from tkinter import Entry
from tkinter import font
from tkinter import ttk
from tkinter.constants import END
from tkinter import StringVar
from tkinter import messagebox
import sys
from traceback import FrameSummary
from src.UI_Files.imagemap import ImageMap
from src.UI_Files.cell import Cell
from src.UI_Files.outputbar import OutputBar
#import game2dboard
import os
import math
import random
from collections import UserList
from PIL import ImageTk, Image
global datavalue
global datarow
global datacol
global troopname
global datarow_index
global datacol_index
datarow_index = None
datacol_index = None
troopname = None
datarow = None
datacol = None
datavalue = None


# TODO:
#   rezize(r, c), self[i] = [...], beep(), play_sound(), ...


class Board(UserList):
    """
    A graphical user interface for 2d arrays (matrix)
    """

    def __init__(
            self,
            nrows,
            ncols,titlename):
        """

        Creates an App

        :param int nrows:
            The number of rows.

        :param int ncols:
            The number of columns.
        """

        UserList.__init__(self)             # Initialize parent class
        # Create list [ncols][nrows]
        self.extend([self._BoardRow(ncols, self) for _ in range(nrows)])

        self._nrows = nrows
        self._ncols = ncols
        self._isrunning = False
        self._imgrow = 0
        self._imgcol = 0

        # Array used to store cells elements (rectangles)
        self._cells = [[None] * ncols for _ in range(nrows)]

        # The window
        self._root = Tk()
        # cell's container
        self._canvas = Canvas(self._root, highlightthickness=0)
        self._background_image = None           # background image file name
        # rectange for grid color
        self._bgrect = self._canvas.create_rectangle(1, 1, 2, 2, width=0)
        image_path = "./src/img/bg_img.png"
        self._bgimage_id = image_path
        self._msgbar = None                     # message bar component
        self._output_textfield = None

        # Fields for board properties
        self._title = titlename                 # default window title
        self._cursor = "arrow"                  # default mouse cursor
        self._margin = 25                        # default board margin (px)
        # default grid cell_spacing (px)
        self._cell_spacing = 1
        self._margin_color = "light grey"       # default border color
        self._cell_color = "#FFFFFF"              # default cell color
        self._grid_color = "black"              # default grid color
        self._cell_angle = 0

        self._on_start = None                   # game started callback
        self._on_key_press = None               # user key press callback
        self._on_mouse_click = None             # user mouse callback
        self._on_timer = None                   # user timer callback
        self._on_textval = None
        self._on_text_ipval = None                    # user texval
        self._output_text_fields = []
        # self._bg_color_with_opacity = None
        self.opacity = 1.0  # Default opacity
        self._overlay_color = None
        self._page_start = None
        button_frame = None
        text_frame = None
        text_frame_el = None
        dropdownval = None

        # event
        self._timer_interval = 0            # ms
        self._after_id = None               # current timer id
        self._is_in_timer_calback = False
        # register internal key callback
        self._root.bind("<Key>", self._key_press_clbk)
        # register internal mouse callback
        self._canvas.bind("<ButtonPress>", self._mouse_click_clbk)

    def __getitem__(self, row):             # subscript getter: self[row]
        # Store last accessed row (NOT thread safe... )
        self._BoardRow.current_i = row
        return super().__getitem__(row)     # return a _BoardRow


    # Properties
    # ---------------------------------------------------------------

    @property
    def size(self):
        """

        Number of elements in the array (readonly).

        :type: int
        """
        return self._nrows * self._ncols

    @property
    def nrows(self):
        """

        Number of rows in the array (readonly).

        :type: int
        """
        return self._nrows

    @property
    def ncols(self):
        """

        Number of columns in the array (readonly).

        :type: int
        """
        return self._ncols

    @property
    def width(self):
        """

        Board width, in px. Only available after .show() (readonly).

        :type: int
        """
        return self._root.winfo_reqwidth()

    @property
    def height(self):
        """

        Board height, in px. Only available after .show() (readonly).

        :type: int
        """
        return self._root.winfo_reqheight()

    @property
    def title(self):
        """

        Gets or sets the window title.

        :type: str
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self._root.title(value)

    @property
    def cursor(self):
        """

        Gets or sets the mouse cursor shape.<br>
        Setting to None hides the cursor.

        :type: str
        """
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = value
        if value is None:
            value = "none"
        self._canvas.configure(cursor=value)

    @property
    def margin(self):
        """

        Gets or sets the board margin (px).

        :type: int
        """
        return self._margin

    @margin.setter
    def margin(self, value):
        if self._isrunning:
            raise Exception("Can't update margin after show()")
        self._margin = value

    @property
    def cell_spacing(self):
        """
        Gets or sets the space between cells (px).

        :type: int
        """
        return self._cell_spacing

    @cell_spacing.setter
    def cell_spacing(self, value):
        if self._isrunning:
            raise Exception("Can't update cell_spacing after show()")
        self._cell_spacing = value

    @property
    def margin_color(self):
        """
        Gets or sets the margin_color.

        :type: str
        """
        return self._margin_color

    @margin_color.setter
    def margin_color(self, value):
        self._margin_color = value
        self._canvas.configure(bg=value)

    @property
    def cell_color(self):
        """
        Gets or sets cells color

        :type: str
        """
        return self._cell_color

    @cell_color.setter
    def cell_color(self, value):
        self._cell_color = value
        if self._isrunning:
            for row in self._cells:
                for cell in row:
                    cell.bgcolor = value


    @property
    def grid_color(self):
        """
        Gets or sets grid color

        :type: str
        """
        return self._grid_color

    @grid_color.setter
    def grid_color(self, value):
        self._grid_color = value
        self._canvas.itemconfig(
            self._bgrect, fill=value if not value is None else '')

    @property
    def cell_size(self):
        """
        Gets or sets the cells dimension (width, height)

        :type: int or (int, int)
        """
        return Cell.size

    @cell_size.setter
    def cell_size(self, value):
        if self._isrunning:
            raise Exception("Can't resize cells after run()")
        # size is a tuple (width, height)
        if not type(value) is tuple:
            v = int(value)
            value = (v, v)
        # All cells has same size (class field)
        Cell.size = value

    @property
    def background_image(self):
        """
        Gets or sets the board's background image


        :type: str
        """
        return self._background_image

    @background_image.setter
    def background_image(self, value):
        if self._background_image != value:
            self._background_image = value
            if self._bgimage_id:
                self._canvas.delete(self._bgimage_id)    # clear current image
            if not value is None:
                # self.margin_color = self.cell_color = None
                self.grid_color = self.margin_color = self.cell_color = None
                canvas_width = self._canvas.winfo_width()
                canvas_height = self._canvas.winfo_height()
                # self.tkimage = ImageMap.get_instance().load(value)
                self.tkimage = ImageTk.PhotoImage(Image.open(value).resize((1800, 2000), Image.ANTIALIAS))
                if not self.tkimage is None:
                    self._image_object = self.tkimage
                    self._bgimage_id = self._canvas.create_image(  # Draw a image
                        0,
                        0,
                        anchor=NW,
                        image=self.tkimage)
                    self._canvas.tag_lower(self._bgimage_id)

    # Private properties
    @property
    def _canvas_width(self):
        return self._ncols * (Cell.width + self.cell_spacing) - self.cell_spacing + (2 * self.margin)

    @property
    def _canvas_height(self):
        return self._nrows * (Cell.height + self.cell_spacing) - self.cell_spacing + (2 * self.margin)

    # Events
    # ---------------------------------------------------------------

    # Game state events
    @property
    def on_start(self):
        """
        Gets or sets the game started callback function.
        The GUI is ready and the program is going to enter the main loop.

        :type: function()
        """
        return self._on_start

    @on_start.setter
    def on_start(self, value):
        self._on_start = value

    # Keyboard events
    @property
    def on_key_press(self):
        """
        Gets or sets the keyboard callback function

        :type: function(key: str)
        """
        return self._on_key_press

    @on_key_press.setter
    def on_key_press(self, value):
        self._on_key_press = value

    # Internal callback
    def _key_press_clbk(self, ev):
        if callable(self._on_key_press):
            self._on_key_press(ev.keysym)

    # Mouse click events
    @property
    def on_mouse_click(self):
        """
        Gets or sets the mouse callback function

        :type: function(button: str, row: int, col: int)
        """
        return self._on_mouse_click

    @on_mouse_click.setter
    def on_mouse_click(self, value):
        self._on_mouse_click = value

    # Internal callback
    def _mouse_click_clbk(self, ev):
        if callable(self._on_mouse_click):
            rc = self._xy2rc(ev.x, ev.y)
            if rc:
                self._on_mouse_click(ev.num, rc[0], rc[1])

    # Timer events
    @property
    def on_timer(self):
        """
        Gets or sets the timer callback function

        :type: function
        """
        return self._on_timer 
    
    
    @property
    def on_textval(self):
        """
        Gets or sets the timer callback function

        :type: function
        """
        return self._on_textval
    
    
    @property
    def on_text_ipval(self):
        """
        Gets or sets the timer callback function

        :type: function
        """
        return self._on_text_ipval

    @on_timer.setter
    def on_timer(self, value):
        self._on_timer = value
        
        
    @on_textval.setter
    def on_textval(self, value):
        self._on_textval = value
    
    @on_text_ipval.setter
    def on_text_ipval(self, value):
        self._on_text_ipval = value

    # internal callback
    def _timer_clbk(self):
        if self._timer_interval > 0 and callable(self._on_timer):
            self._is_in_timer_calback = True
            self._on_timer()              # Call the user callback function
            self._is_in_timer_calback = False
        if self._timer_interval > 0:      # User callback function may change timer!
            self._after_id = self._root.after(
                self._timer_interval, self._timer_clbk)

    # Methods
    # ---------------------------------------------------------------

    def show(self):
        """

        Create the GUI, display and enter the run loop.

        """
        self._setupUI()
        self._isrunning = True
        if callable(self._on_start):
            self._on_start()
        self._root.mainloop()

    def clear(self):
        """

        Clear the board, setting all values to None.
        """
        self.fill(None)

    def close(self):
        """

        Close the board, exiting the program.
        """
        self._root.destroy()

    def create_output(self, **kwargs):
        """

        Create a output message bar.
        kwargs:
            color = str
            background_color` = str
            font_size = int
        """
        if self._isrunning:
            raise Exception("Can't create output after run()")
        elif self._msgbar is None:
            self._msgbar = OutputBar(
                self._root, **kwargs)

    def print(self, *objects, sep=' ', end=''):
        """

        Print message to output bar.
        Use like standard print() function.
        """
        if self._msgbar:
            s = sep.join(str(obj) for obj in objects) + end
            self._msgbar.show(s)

    def shuffle(self):
        """

        Random shuffle all values in the board
        """

        # Copy all values to an array, random.shuffle it, then copy back
        a = []
        for r in self:
            a.extend(r)
        random.shuffle(a)
        for row in self:
            for c in range(self._ncols):
                row[c] = a.pop()

    def fill(self, value, row=None, col=None):
        """

        Fill the board (or a row, or a column) with a value

        :param value: The value to store
        :param int row: Index of row to fill. Default=None (all rows)
        :param int col: Index of column to fill. Default=None (all columns)
        """
        if row is None and col is None:         # all rows and columns
            for r in range(self._nrows):
                for c in range(self._ncols):
                    self[r][c] = ((0,0,0),value)
        elif not row is None and col is None:  # single row
            for c in range(self._ncols):
                self[row][c] = ((0,0,0),value)
        elif row is None and not col is None:   # a single collumn
            for r in range(self._nrows):
                self[r][col] = ((0,0,0),value)
        else:
            raise Exception("Invalid argument supplied (row= AND col=)")

    def copy(self):
        """
        Returns a shallow copy of the array (only data, not the GUI) into a regular Python list (of lists).
        """
        return [[self[i][j] for j in range(self.ncols)] for i in range(self.nrows)]

    def load(self, data):
        """
        Copy data from regular Python 2D array (list of lists) into the Board.
        """
        if len(data) < self._nrows:
            raise IndexError()
        for r in range(self._nrows):
            if len(data[r]) < self._ncols:
                raise IndexError()
            for c in range(self._ncols):
                self[r][c] = data[r][c]

    def start_timer(self, msecs):
        """

        Start a periodic timer that executes the a function every msecs milliseconds

        The callback function must be registered using .on_timer property.

        :param int msecs: Time in milliseconds.
        """
        if msecs != self._timer_interval:                       # changed
            self.stop_timer()
            self._timer_interval = msecs
            if msecs > 0 and not self._is_in_timer_calback:
                self._after_id = self._root.after(msecs, self._timer_clbk)

    def stop_timer(self):
        """

        Stops the current timer.
        """
        self._timer_interval = 0
        if self._after_id:
            self._root.after_cancel(self._after_id)
            self._after_id = None

        # def clear(self):
        #     for buttont in self._output_text_fields:
        #         buttont.delete('1.0', END)
    
    def pause(self, msecs, change_cursor=True):
        """

        Delay the program execution for a given number of milliseconds.

        Warning: long pause freezes the GUI!

        :param int msecs: Time in milliseconds.
        :param bool change_cursor: Change the cursor to "watch" during pause?
        """
        if change_cursor:
            oldc = self.cursor
            self.cursor = "watch"
        self._root.update_idletasks()
        self._root.after(msecs)
        if change_cursor:
            self.cursor = oldc

    # Private methods
    # ---------------------------------------------------------------
    def set_bgframe(self,r,c,color):
        if(color == "yellow"):
            x, y = self._rc2xy(r, c)
            newcell = Cell(self._canvas, x, y)
            newcell.configure_cell_yellow(highlight=True)
        else:
            for a in range(self._nrows):
                for b in range(self._ncols):
                    x, y = self._rc2xy(a, b)
                    newcell = Cell(self._canvas, x, y)
                    newcell.configure_cell(highlight=True)

    def _setupUI(self):
        # Window is not resizable
        self._root.resizable(False, False)
        image_path = "./src/img/bg_img.png"
        self.background_image = image_path
        self.cell_color = self.margin_color = self.grid_color = None
        # self.cell_color = self._overlay_color
        # self.margin_color = None        # Paint background
        # self.grid_color = None              # Table internal lines
        # self.cell_color = self._cell_color 
        # self.background_image = ""  # Draw background image
        # if not self._background_image is None:
        #     self.margin_color = self.grid_color = self.cell_color = None
        # else:
        #     self.margin_color = self._margin_color          # Paint background
        #     self.grid_color = self._grid_color              # Table internal lines
        #     self.cell_color = self._cell_color              # Cells background

        self.margin = self._margin                      # Change root's margin
        self.cell_spacing = self._cell_spacing          # Change root's padx/y
        self.title = self._title                        # Update window's title
        self.cursor = self._cursor
        self._resize_canvas()
        # Create all cells
        for r in range(self._nrows):
            for c in range(self._ncols):
                x, y = self._rc2xy(r, c)
                newcell = Cell(self._canvas, x, y)
                #if r < 5 and c < 5:
                #    newcell.bgcolor = "yellow"
                #else:
                # newcell.border  = self._cell_color
                newcell.bgcolor = self._cell_color
                # self._cells[r][c] = newcell.configure_cell(highlight=True)
                self._cells[r][c] = newcell
                if self[r][c] != None:                       # Cell has a value
                    self._notify_change(r, c,(0,0,0), self[r][c])    # show it

        for r in range(self._nrows):
            x, y = self._rc2xy(r, self._ncols)
            self._canvas.create_text(  # or just draw the value as text
                x + self._nrows,
                y + 60 // 2,
                anchor=CENTER,
                text=str(self._nrows-r-1),
                fill="black",
                font=(None, max(min(50//4, 12), 6)),
                width=50-2)

        for c in range(self._ncols):
            x, y = self._rc2xy(self._nrows,c)
            self._canvas.create_text(  # or just draw the value as text
                x + 60 // 2,
                y + self._ncols/2,
                anchor=CENTER,
                text=str(c),
                fill="black",
                font=(None, max(min(50//4, 12), 6)),
                width=50-2)

        self._canvas.pack()
        self._root.update()

    def _notify_change(self, row, col, new_value):
        #print(new_value)
        if new_value[0][2] == 1:
            return
        if self._cells[row][col]:
            ori = (math.degrees(math.atan2(new_value[0][1],new_value[0][0])))
            diff = ori - self._cells[row][col].angle
            self._cells[row][col].angle = ori
            self._cells[row][col].value = new_value[1] 

    # Config the canvas size
    def _resize_canvas(self):
        self._canvas.config(width=self._canvas_width,
                            height=self._canvas_height)

        x1 = y1 = self.margin
        x2 = self._canvas_width - x1
        y2 = self._canvas_height - y1
        self._canvas.coords(self._bgrect, x1, y1, x2, y2)

    # Translate [row][col] to canvas coordinates
    def _rc2xy(self, row, col):
        x = col * (Cell.width + self.cell_spacing) + self.margin
        y = row * (Cell.height + self.cell_spacing) + self.margin
        return (x, y)

    # Translate canvas coordinates to (row, col)
    def _xy2rc(self, x, y):
        # how can i optimize it ???? May be _self.canvas.find_withtag(CURRENT)
        for r in range(self._nrows):
            for c in range(self._ncols):
                cell = self._cells[r][c]
                if cell.x < x < cell.x + Cell.width \
                        and cell.y < y < cell.y + Cell.height:
                    return (r, c)
        return None
    
    def button_frame(self):
        global button_frame
        button_frame = Frame(self._root)
        button_frame.pack(side=RIGHT, anchor='n')

    def create_eliminate(self):
        global text_frame_el
        text_frame_el = Frame(self._root)
        text_frame_el.pack(side=BOTTOM,anchor='n')
        buttone = Text(text_frame_el, bd=1, font=('Arial', 12), width=40)
        # buttont.insert(INSERT,self._on_textval)
        buttone.configure(height=4)
        buttone.grid(row=0, column=0)

        return buttone

    def create_output_textfield(self):
        global text_frame
        text_frame = Frame(self._root)
        text_frame.pack(side=TOP,anchor='n')
        buttont = Text(text_frame, bd=1, font=('Arial', 12), width=60)
        # buttont.insert(INSERT,self._on_textval)
        buttont.configure(height=2)
        buttont.grid(row=0, column=0)
        # button = tk.Button(button_frame, text="ENTER", command=self.on_box_find)
        # button.grid(row=3, column=1, padx=10, pady=5)

        # self._output_text_fields.append()

        return buttont
    
    def on_box_find(self,uniqId):
        global troopname

        if (uniqId == 10):
            img_file_name = "soldier-red.gif"
            troopname = "land"
        elif (uniqId == 15):
            img_file_name = "soldier-yellow.gif"
            troopname = "land"
        elif (uniqId == 11):
            img_file_name = "truck-red.gif"
            troopname = "land"
        elif (uniqId == 16):
            img_file_name = "truck-yellow.gif"
            troopname = "land"
        elif (uniqId == 12):
            img_file_name = "tank-red.gif"
            troopname = "land"
        elif (uniqId == 17):
            img_file_name = "tank-yellow.gif"
            troopname = "land"
        elif (uniqId == 13):
            img_file_name = "plane-red.gif"
            troopname = "plane"
        elif (uniqId == 18):
            img_file_name = "plane-yellow.gif"
            troopname = "plane"
        elif (uniqId == 14):
            img_file_name = "flag-red.gif"
            troopname = "land"
            # ResponseVal.dissabled_all()
        elif (uniqId == 19):
            img_file_name = "flag-yellow.gif"
            troopname = "land"
            # ResponseVal.dissabled_all()
        else:
            img_file_name = "flag-red.gif"
            troopname = "land"

        
        # if (uniqId == 10):
        #     img_file_name = "soldier-red.gif"
        #     troopname = "land"
        # elif (uniqId == 15):
        #     img_file_name = "soldier-yellow.gif"
        #     troopname = "land"
        # elif (uniqId == 11):
        #     img_file_name = "truck-red.gif"
        #     troopname = "land"
        # elif (uniqId == 16):
        #     img_file_name = "truck-yellow.gif"
        #     troopname = "land"
        # elif (uniqId == 12):
        #     img_file_name = "tank-red.gif"
        #     troopname = "land"
        # elif (uniqId == 17):
        #     img_file_name = "tank-yellow.gif"
        #     troopname = "land"
        # elif (uniqId == 13):
        #     img_file_name = "plane-red.gif"
        #     troopname = "plane"
        # elif (uniqId == 18):
        #     img_file_name = "plane-yellow.gif"
        #     troopname = "plane"
        # elif (uniqId == 14):
        #     img_file_name = "flag-red.gif"
        #     troopname = "land"
        #     # ResponseVal.dissabled_all()
        # elif (uniqId == 19):
        #     img_file_name = "flag-yellow.gif"
        #     troopname = "land"
        #     # ResponseVal.dissabled_all()
        # else:
        #     img_file_name = "flag-red.gif"
        #     troopname = "land"
            
        # img_file_name = "flag-red.gif"
            
        global datarow
        global datacol
        for row in range(11):
            for col in range(10):
                if self._cells[row][col].value == img_file_name:
                    if(img_file_name == "flag-red.gif" or img_file_name == "flag-yellow.gif"):
                        self._cells[self._imgrow][self._imgcol].configure(highlight=False)
                        # self._cells[row][col].configure(highlight=True) 
                        self._imgrow = row
                        self._imgcol = col
                        # datarow = row
                        # datacol = col
                    else:
                        self._cells[self._imgrow][self._imgcol].configure(highlight=False)
                        self._cells[row][col].configure(highlight=True) 
                        self._imgrow = row
                        self._imgcol = col
                        datarow = row
                        datacol = col

                    # print(f"The image 'a.gif' is located at row {row} and column {col}.")

    def on_aircraft(self,position):
        global datarow_index
        global datacol_index
        x, y, z = position
        datarow_index = x 
        datacol_index = abs(y - 10)

    # Inner classes
    # ---------------------------------------------------------------

    # A row is a list, so I can use the magic function __setitem__(board[i][j])

    class _BoardRow(UserList):
        # Last acessed row (class member).
        # Yes, its not thread safe!
        # Maybe in the future I will use a proxy class
        current_i = None

        def __init__(self, length, parent):
            UserList.__init__(self)
            self.extend([None] * length)         # Initialize the row
            self._parent = parent                # the board

        def __setitem__(self, j,value):
            self._parent._notify_change(self.__class__.current_i, j, value)
            return super().__setitem__(j, value)

class AlertWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.input_value = tk.StringVar()

        self.entry = tk.Entry(self, font=('Century 12'),width=40)
        self.entry.pack(padx=10, pady=10)

        self.ok_button = tk.Button(self, text="OK", command=self.get_input_value)
        self.ok_button.pack(pady=10)

        self.entry.focus_set()

    def handle_ok(self):
        self.destroy()

    def get_input_value(self):
        data_text = self.entry.get()
        # print(datavalue)
        global datavalue
        datavalue = data_text
        # print(datavalue)
        self.handle_ok()
        return data_text
    
class ExitWindow(AlertWindow):
    def show_alert():
        window = tk.Tk()
        window.withdraw()  # Hide the main window
        alert_window = AlertWindow(window)
        window.wait_window(alert_window)
        window.destroy()  # Destroy the main window
        return datavalue
    
class ResponseVal():
    def __init__(self):
        self.button_clicked = False
        self.radio_frame = None
        self.radio_buttons = []
        self.dropdown_values = None
        self.text_dataval = tk.StringVar()
        self.text_values = None
        self.textfield = None
        self.dropdown_var = tk.StringVar()
        self.button = None
        self.troop = None
        global datarow
        global datacol
        global troopname
        global dataval
        
    def create_output_text(self,text_data):
        # global button_frame
        # text_frame = Frame(self._root)
        # text_frame.pack(side=TOP,anchor='n')
        buttont = Text(text_frame, bd=1, font=('Arial', 12), width=60)
        buttont.insert(INSERT,text_data)
        buttont.configure(height=2)
        buttont.grid(row=0, column=0) 
        
    def create_eliminate(self,e_data):
        number_names = {
            10: "soldier-blue",
            11: "truck-blue",
            12: "tank-blue",
            13: "plane-blue",
            14: "flag-blue",
            15: "soldier-violet",
            16: "truck-violet",
            17: "tank-violet",
            18: "plane-violet",
            19: "flag-violet"
        }

        a = [10, 11, 12, 13, 14, 25, 26, 27, 15, 16, 17, 18, 19]
        b = e_data

        # Convert lists to sets for set operations
        set_a = set(a)
        set_b = set(b)

        # Find the missing elements in b but present in a
        missing_numbers = set_a - set_b

        # Find the names of the missing numbers
        print(missing_numbers)
        missing_names = ""
        s_names = ""
        if(missing_numbers ==  None):
            missing_names = ""
        else:
            for number in missing_numbers:
                if(number ==  25 or number ==  26 or number == 27):
                    missing_names = ""
                else:
                    name = number_names[number]
                    print(name)
                    s_names = s_names + name + " " 
                    # missing_names.append(name)
        print(s_names)
        # missing_names = [number_names[number] for number in missing_numbers]
        # Print the missing number names
        # print("Missing number names in b but present in a:", missing_names)
        # global text_frame
        # text_frame = Frame(self._root)
        # text_frame.pack(side=BOTTOM,anchor='n')
        buttone = Text(text_frame_el, bd=1, font=('Arial', 12), width=40)
        buttone.insert(INSERT,s_names)
        buttone.configure(height=4)
        buttone.grid(row=0, column=0)

    def create_dropdown(self, arr_msg):
        button_values = {
            "N.WEST": "7",
            "North.": "8",
            "N.East": "1",
            "West .": "6",
            "DoNot.": "0",
            "East .": "2",
            "S.West": "5",
            "South.": "4",
            "S.East": "3"
        }
        dark_blue = "#00008B"
        bg_white = "#FFFFFF"
        self.button = tk.Button(button_frame, text='Orientation', bg=bg_white, fg=dark_blue)
        self.button .grid(row=0, column=2, padx=10, pady=10) 
        self.button.config(state="disabled") 
        self.button = tk.Button(button_frame, text='Ground Troop Movement', bg=bg_white, fg=dark_blue)
        self.button .grid(row=4, column=2, padx=10, pady=10) 
        self.button.config(state="disabled") 
        self.button = tk.Button(button_frame, text='AirCraft Movement', bg=bg_white, fg=dark_blue)
        self.button .grid(row=6, column=2, padx=10, pady=10) 
        self.button.config(state="disabled") 
        self.button = tk.Button(button_frame, text='Aircraft Action', bg=bg_white, fg=dark_blue)
        self.button .grid(row=15, column=2, padx=10, pady=10) 
        self.button.config(state="disabled") 

        def button_callback(value):
            nonlocal selected_value
            self.button.quit()
            if troopname == "plane":
                selected_value = value
                print('Input_Call_Value',value)
                # self.button.config(state="normal")
                button_frame.quit()
            else:
                selected_value = value
                print('Input_Call_Value',value)
                button_frame.quit()

        keys = list(button_values.keys())
        values = list(button_values.values())

        if troopname == "plane":
            # print('datacol,datarow')
            # print(len(arr_msg))
            act_drp = str(arr_msg[-1]).split("- ")
            act_drp1 = str(arr_msg[-2]).split("- ")
            # print(act_drp,act_drp1)
            print(datarow,datacol)
            # button_f.destroy()
            datarow_y = datarow_index
            datacol_x = datacol_index

            if(len(arr_msg)  < 4):
                # print('length-3')
                # print(len(arr_msg))
                for i in range(3):
                    for j in range(3):
                        d = i * 3 + j
                        if d < len(keys):
                            button_text = keys[d]
                            value = values[d]
                            self.button = tk.Button(button_frame, text=button_text, command=lambda v=value: button_callback(v))
                            self.button.grid(row=i+1, column=j+1, padx=10, pady=10)
                            self.button.config(state="disabled")
                        else:
                            print("Invalid index")
                self.button = tk.Button(button_frame, text='Advance', command=lambda : button_callback(9))
                self.button.grid(row=5, column=1, padx=10, pady=10)
                self.button.config(state="disabled")

                self.button = tk.Button(button_frame, text='shoot', command=lambda : button_callback(10))
                self.button.grid(row=5, column=2, padx=10, pady=10)
                self.button.config(state="disabled")

                self.button = tk.Button(button_frame, text='Ram', command=lambda : button_callback(11))
                self.button.grid(row=5, column=3, padx=10, pady=10)
                self.button.config(state="disabled")

                self.button = tk.Button(button_frame, text='shoot', command=lambda : button_callback(localvar14))
                self.button .grid(row=17, column=1, padx=10, pady=10) 
                self.button.config(state="disabled") 

                # self.button  = tk.Button(button_frame, text='shoot', command=lambda : button_callback(2))
                # self.button .grid(row=16, column=3, padx=10, pady=10)
                # self.button.config(state="disabled")

                self.button = tk.Button(button_frame, text='bomb', command=lambda : button_callback(localvar15))
                self.button .grid(row=17, column=3, padx=10, pady=10)
                self.button.config(state="disabled") 

                self.button  = tk.Button(button_frame, text='Donot', command=lambda : button_callback(0))
                self.button .grid(row=16, column=1, padx=10, pady=10)

                self.button  = tk.Button(button_frame, text='Ascend', command=lambda : button_callback(1))
                self.button .grid(row=16, column=2, padx=10, pady=10)

                self.button  = tk.Button(button_frame, text='shoot', command=lambda : button_callback(2))
                self.button .grid(row=16, column=3, padx=10, pady=10)
            elif(len(arr_msg)  > 4):
                self.button  = tk.Button(button_frame, text='Donot', command=lambda : button_callback(0))
                self.button .grid(row=16, column=1, padx=10, pady=10)
                self.button.config(state="disabled")

                self.button  = tk.Button(button_frame, text='Ascend', command=lambda : button_callback(1))
                self.button .grid(row=16, column=2, padx=10, pady=10)
                self.button.config(state="disabled")

                self.button  = tk.Button(button_frame, text='shoot', command=lambda : button_callback(2))
                self.button .grid(row=16, column=3, padx=10, pady=10)
                self.button.config(state="disabled")

                self.button = tk.Button(button_frame, text='Advance', command=lambda : button_callback(9))
                self.button.grid(row=5, column=1, padx=10, pady=10)
                self.button.config(state="disabled")

                self.button = tk.Button(button_frame, text='shoot', command=lambda : button_callback(10))
                self.button.grid(row=5, column=2, padx=10, pady=10)
                self.button.config(state="disabled")

                self.button = tk.Button(button_frame, text='Ram', command=lambda : button_callback(11))
                self.button.grid(row=5, column=3, padx=10, pady=10)
                self.button.config(state="disabled")
                for i in range(3):
                    for j in range(3):
                        d = i * 3 + j
                        if d < len(keys):
                            button_text = keys[d]
                            value = values[d]
                            self.button = tk.Button(button_frame, text=button_text, command=lambda v=value: button_callback(v))
                            self.button.grid(row=i+1, column=j+1, padx=10, pady=10)
                        else:
                            print("Invalid index")
                global planeval
                planeval = 8
                if((datarow_y >= 0 and datarow_y <= 9) and (datacol_x+2 >= 0 and datacol_x+2 <=10)):
                    print('1',datarow_y , datacol_x+2)
                    localvar1 = planeval + 1
                    planeval = localvar1
                    print(planeval)
                    self.button = tk.Button(button_frame, text='↡', command=lambda : button_callback(localvar1))
                    self.button .grid(row=13, column=2, padx=10, pady=10)
                if((datarow_y-1 >= 0 and datarow_y-1 <= 9) and (datacol_x+1 >= 0 and datacol_x+1 <=10)):
                    print('2',datarow_y-1 , datacol_x+1)
                    localvar2 = planeval + 1
                    planeval = localvar2
                    print(planeval)
                    self.button = tk.Button(button_frame, text='↙', command=lambda : button_callback(localvar2))
                    self.button .grid(row=12, column=1, padx=10, pady=10)
                if((datarow_y >= 0 and datarow_y <= 9) and (datacol_x+1 >= 0 and datacol_x+1 <=10)):
                    print('3',datarow_y , datacol_x+1)
                    localvar3 = planeval + 1
                    planeval = localvar3
                    print(planeval)
                    self.button = tk.Button(button_frame, text='↓', command=lambda : button_callback(localvar3))
                    self.button .grid(row=12, column=2, padx=10, pady=10)
                if((datarow_y+1 >= 0 and datarow_y+1 <= 9) and (datacol_x+1 >= 0 and datacol_x+1 <=10)):
                    print('4',datarow_y+1 , datacol_x+1)
                    localvar4 = planeval + 1
                    planeval = localvar4
                    print(planeval)
                    self.button = tk.Button(button_frame, text='↘', command=lambda : button_callback(localvar4))
                    self.button .grid(row=12, column=3, padx=10, pady=10)
                if((datarow_y-2 >= 0 and datarow_y-2 <= 9) and (datacol_x >= 0 and datacol_x <=10)):
                    print('5',datarow_y-2 , datacol_x)
                    localvar5 = planeval + 1
                    planeval = localvar5
                    print(planeval)
                    self.button = tk.Button(button_frame, text='↞', command=lambda : button_callback(localvar5))
                    self.button .grid(row=11, column=0, padx=10, pady=10)
                if((datarow_y-1 >= 0 and datarow_y-1 <= 9) and (datacol_x >= 0 and datacol_x <=10)):
                    print('6',datarow_y-1 , datacol_x)
                    localvar6 = planeval + 1
                    planeval = localvar6
                    print(planeval)
                    self.button = tk.Button(button_frame, text='←', command=lambda : button_callback(localvar6))
                    self.button .grid(row=11, column=1, padx=10, pady=10)
                if((datarow_y >= 0 and datarow_y <= 9) and (datacol_x >= 0 and datacol_x <=10)):
                    print('7',datarow_y , datacol_x)
                    localvar7 = planeval + 1
                    planeval = localvar7
                    print(planeval)
                    self.button = tk.Button(button_frame, text='▣', command=lambda : button_callback(localvar7))
                    self.button .grid(row=11, column=2, padx=10, pady=10)
                if((datarow_y+1 >= 0 and datarow_y+1 <= 9) and (datacol_x >= 0 and datacol_x <=10)):
                    print('8',datarow_y+1 , datacol_x)
                    localvar8 = planeval + 1
                    planeval = localvar8
                    print(planeval)
                    self.button = tk.Button(button_frame, text='→', command=lambda : button_callback(localvar8))
                    self.button .grid(row=11, column=3, padx=10, pady=10)
                if((datarow_y+2 >= 0 and datarow_y+2 <= 9) and (datacol_x >= 0 and datacol_x <=10)):
                    print('9',datarow_y+2 , datacol_x)
                    localvar9 = planeval + 1
                    planeval = localvar9
                    print(planeval)
                    self.button = tk.Button(button_frame, text='↠', command=lambda : button_callback(localvar9))
                    self.button .grid(row=11, column=4, padx=10, pady=10)
                if((datarow_y-1 >= 0 and datarow_y-1 <= 9) and (datacol_x-1 >= 0 and datacol_x-1 <=10)):
                    print('10',datarow_y-1 , datacol_x-1)
                    localvar10 = planeval + 1
                    planeval = localvar10
                    print(planeval)
                    self.button = tk.Button(button_frame, text='↖', command=lambda : button_callback(localvar10))
                    self.button .grid(row=10, column=1, padx=10, pady=10)
                if((datarow_y >= 0 and datarow_y <= 9) and (datacol_x-1 >= 0 and datacol_x-1 <=10)):
                    print('11',datarow_y , datacol_x-1)
                    localvar11 = planeval + 1
                    planeval = localvar11
                    print(planeval)
                    self.button = tk.Button(button_frame, text='↑', command=lambda : button_callback(localvar11))
                    self.button .grid(row=10, column=2, padx=10, pady=10)
                if((datarow_y+1 >= 0 and datarow_y+1 <= 9) and (datacol_x-1 >= 0 and datacol_x-1 <=10)):
                    print('12',datarow_y+1 , datacol_x-1)
                    localvar12 = planeval + 1
                    planeval = localvar12
                    print(planeval)
                    self.button = tk.Button(button_frame, text='↗', command=lambda : button_callback(localvar12))
                    self.button .grid(row=10, column=3, padx=10, pady=10)
                if((datarow_y >= 0 and datarow_y <= 9) and (datacol_x-2 >= 0 and datacol_x-2 <=10)):
                    print('13',datarow_y , datacol_x-2)
                    localvar13 = planeval + 1
                    planeval = localvar13
                    print(planeval)
                    self.button = tk.Button(button_frame, text='↟', command=lambda : button_callback(localvar13))
                    self.button .grid(row=9, column=2, padx=10, pady=10) 
                if(act_drp[1] == "shoot" or act_drp1[1] == "shoot"):
                    localvar14 = planeval + 1
                    planeval = localvar14
                    print(localvar14)
                    self.button = tk.Button(button_frame, text='shoot', command=lambda : button_callback(localvar14))
                    self.button .grid(row=17, column=1, padx=10, pady=10) 
                if(act_drp[1] == "bomb" or act_drp1[1] == "bomb"): 
                    localvar15 = planeval + 1
                    planeval = localvar15
                    print(localvar15)
                    self.button = tk.Button(button_frame, text='bomb', command=lambda : button_callback(localvar15))
                    self.button .grid(row=17, column=3, padx=10, pady=10) 
                    # planeval = planeval+1  
            print("plane")
            # selected_value = 1
        elif troopname == "land":
            selected_value = None
            # Create a 3x3 grid of buttons
            for i in range(3):
                for j in range(3):
                    d = i * 3 + j
                    if d < len(keys):
                        button_text = keys[d]
                        value = values[d]
                        self.button = tk.Button(button_frame, text=button_text, command=lambda v=value: button_callback(v))
                        self.button.grid(row=i+1, column=j+1, padx=10, pady=10)
                    else:
                        print("Invalid index")
            self.button = tk.Button(button_frame, text='Advance', command=lambda : button_callback(9))
            self.button.grid(row=5, column=1, padx=10, pady=10)

            self.button = tk.Button(button_frame, text='shoot', command=lambda : button_callback(10))
            self.button.grid(row=5, column=2, padx=10, pady=10)

            self.button = tk.Button(button_frame, text='Ram', command=lambda : button_callback(11))
            self.button.grid(row=5, column=3, padx=10, pady=10)

            self.button = tk.Button(button_frame, text='↡', command=lambda : button_callback(localvar1))
            self.button .grid(row=13, column=2, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='↙', command=lambda : button_callback(localvar2))
            self.button .grid(row=12, column=1, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='↓', command=lambda : button_callback(localvar3))
            self.button .grid(row=12, column=2, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='↘', command=lambda : button_callback(localvar4))
            self.button .grid(row=12, column=3, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='↞', command=lambda : button_callback(localvar5))
            self.button .grid(row=11, column=0, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='←', command=lambda : button_callback(localvar6))
            self.button .grid(row=11, column=1, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='▣', command=lambda : button_callback(localvar7))
            self.button .grid(row=11, column=2, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='→', command=lambda : button_callback(localvar8))
            self.button .grid(row=11, column=3, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='↠', command=lambda : button_callback(localvar9))
            self.button .grid(row=11, column=4, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='↖', command=lambda : button_callback(localvar10))
            self.button .grid(row=10, column=1, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='↑', command=lambda : button_callback(localvar11))
            self.button .grid(row=10, column=2, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='↗', command=lambda : button_callback(localvar12))
            self.button .grid(row=10, column=3, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='↟', command=lambda : button_callback(localvar13))
            self.button .grid(row=9, column=2, padx=10, pady=10) 
            self.button.config(state="disabled")
            self.button  = tk.Button(button_frame, text='Donot', command=lambda : button_callback(0))
            self.button .grid(row=16, column=1, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button  = tk.Button(button_frame, text='Ascend', command=lambda : button_callback(1))
            self.button .grid(row=16, column=2, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button  = tk.Button(button_frame, text='shoot', command=lambda : button_callback(2))
            self.button .grid(row=16, column=3, padx=10, pady=10)
            self.button.config(state="disabled")
            self.button = tk.Button(button_frame, text='bomb', command=lambda : button_callback(localvar15))
            self.button .grid(row=17, column=3, padx=10, pady=10)
            self.button.config(state="disabled") 
            self.button = tk.Button(button_frame, text='shoot', command=lambda : button_callback(localvar14))
            self.button .grid(row=17, column=1, padx=10, pady=10) 
            self.button.config(state="disabled") 


        button_frame.mainloop()

        if selected_value is not None:
            # if troopname == "plane":
            #     button_frame.quit()
            print("Selected value:", selected_value)
            # self.button.config(state="disabled")
            
            return selected_value
        else:
            print("No value selected. Handle invalid input here.")


        # def passdata():
        #     selected_value_value = selected_value.get()
        #     print("Selected value:", selected_value_value)
        #     # print(val)
        #     print('IINN')
        #     button_frame.quit()
        # Remove the old radio buttons
        # if self.radio_frame:
        #     self.radio_frame.destroy()

        # Create a new frame for the radio buttons
        # self.radio_frame = tk.Frame(button_frame)
        # self.radio_frame.grid(row=3, column=0, padx=10, pady=5)

        # Create radio buttons for each option
        # for option in self.dropdown_values:
        #     radio_button = tk.Radiobutton(self.radio_frame, text=option, variable=self.dropdown_var, value=option,font=custom_font)
        #     radio_button.pack(anchor="w")
        #     self.radio_buttons.append(radio_button)


    def dissabled_all(self):
        button_values = {
            "N.WEST": "7",
            "North.": "8",
            "N.East": "1",
            "West .": "6",
            "DoNot.": "0",
            "East .": "2",
            "S.West": "5",
            "South.": "4",
            "S.East": "3"
        }
        keys = list(button_values.keys())
        values = list(button_values.values())
        dark_blue = "#00008B"
        bg_white = "#FFFFFF"
        self.button = tk.Button(button_frame, text='Orientation', bg=bg_white, fg=dark_blue)
        self.button .grid(row=0, column=2, padx=10, pady=10) 
        self.button.config(state="disabled") 
        self.button = tk.Button(button_frame, text='Ground Troop Movement', bg=bg_white, fg=dark_blue)
        self.button .grid(row=4, column=2, padx=10, pady=10) 
        self.button.config(state="disabled") 
        self.button = tk.Button(button_frame, text='Aircraft Movement', bg=bg_white, fg=dark_blue)
        self.button .grid(row=6, column=2, padx=10, pady=10) 
        self.button.config(state="disabled") 
        self.button = tk.Button(button_frame, text='Aircraft Action', bg=bg_white, fg=dark_blue)
        self.button .grid(row=15, column=2, padx=10, pady=10) 
        self.button.config(state="disabled") 

        self.button = tk.Button(button_frame, text='Advance')
        self.button.grid(row=5, column=1, padx=10, pady=10)
        self.button.config(state="disabled") 

        self.button = tk.Button(button_frame, text='shoot',)
        self.button.grid(row=5, column=2, padx=10, pady=10)
        self.button.config(state="disabled") 

        self.button = tk.Button(button_frame, text='Ram')
        self.button.grid(row=5, column=3, padx=10, pady=10)
        self.button.config(state="disabled") 

        self.button = tk.Button(button_frame, text='↡')
        self.button .grid(row=13, column=2, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='↙')
        self.button .grid(row=12, column=1, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='↓')
        self.button .grid(row=12, column=2, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='↘')
        self.button .grid(row=12, column=3, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='↞')
        self.button .grid(row=11, column=0, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='←')
        self.button .grid(row=11, column=1, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='▣')
        self.button .grid(row=11, column=2, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='→')
        self.button .grid(row=11, column=3, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='↠')
        self.button .grid(row=11, column=4, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='↖')
        self.button .grid(row=10, column=1, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='↑')
        self.button .grid(row=10, column=2, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='↗')
        self.button .grid(row=10, column=3, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='↟')
        self.button .grid(row=9, column=2, padx=10, pady=10) 
        self.button.config(state="disabled")
        self.button  = tk.Button(button_frame, text='Donot')
        self.button .grid(row=16, column=1, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button  = tk.Button(button_frame, text='Ascend')
        self.button .grid(row=16, column=2, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button  = tk.Button(button_frame, text='shoot')
        self.button .grid(row=16, column=3, padx=10, pady=10)
        self.button.config(state="disabled")
        self.button = tk.Button(button_frame, text='bomb')
        self.button .grid(row=17, column=3, padx=10, pady=10)
        self.button.config(state="disabled") 
        self.button = tk.Button(button_frame, text='shoot')
        self.button .grid(row=17, column=1, padx=10, pady=10) 
        self.button.config(state="disabled") 
        for i in range(3):
            for j in range(3):
                d = i * 3 + j
                if d < len(keys):
                    button_text = keys[d]
                    value = values[d]
                    self.button = tk.Button(button_frame, text=button_text)
                    self.button.grid(row=i+1, column=j+1, padx=10, pady=10)
                    self.button.config(state="disabled")
                else:
                    print("Invalid index")
    
    #     button = tk.Button(button_frame, text="ENTER", command=self.on_button_click)
    #     button.grid(row=3, column=1, padx=10, pady=5)
    #     button1 = tk.Button(button_frame, text="Click Me", command=self.button1_callback)
    #     button1.grid(row=4, column=1, padx=10, pady=5)

    #     if self.button_clicked:
    #         return 0
    #         # print(self.dropdown_var.get())
    #         # selected_value = self.dropdown_var.get()
    #         # selected_index = self.dropdown_values.index(selected_value)
    #         # return selected_index
    #     else:
    #         return "No Value Entered"
    # def button1_callback(self):
    #     print('red')
    #     # return "red"

    # def on_button_click(self):
    #     self.button_clicked = True
    #     button_frame.quit()
    #     # self.radio_frame.destroy()

    # def create_text(self, text_val):
    #     print(text_val)
    #     # self.textfield = tk.Text(button_frame, font=('Arial', 12), values=self.text_values, width=60)
    #     # self.textfield.configure(height=4)
    #     # self.textfield.insert("1.0", text_val)
    #     # self.textfield.grid(row=2, column=0, padx=10, pady=5)

    # # def on_button_click_text(self):
    # #     self.textfield.destroy()
