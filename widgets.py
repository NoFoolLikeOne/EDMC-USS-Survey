import collections
import tkFont
import Tkinter as tk
import ttk


from ttkHyperlinkLabel import HyperlinkLabel

class SelfWrappingHyperlinkLabel(HyperlinkLabel):
    "Tries to adjust its width."

    def __init__(self, *a, **kw):
        "Init."

        HyperlinkLabel.__init__(self, *a, **kw)
        self.frame=a[0]
        self.frame.bind('<Configure>', self.__configure_event)		

    def __configure_event(self, event):
        "Handle resizing."
        self.configure(wraplength=event.width-2)