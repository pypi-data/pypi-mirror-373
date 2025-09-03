from datetime import datetime
import time
from time import localtime
from time import strftime


from textual.app import  ComposeResult
from textual.widgets import Digits, Static

class Date(Static):
    def on_mount(self) -> None:
        self.set_date()

    
    def set_date(self) -> None:
        datevalues = strftime("%a, %d %b %Y ", localtime())
        self.update(datevalues)

class Clock(Digits):
        
    def on_mount(self) -> None:
        self.update_clock()
        self.set_interval(1, self.update_clock)
       

    def update_clock(self) -> None:
        clock = datetime.now().time()
        
        self.update(f"{clock:%T}")
        