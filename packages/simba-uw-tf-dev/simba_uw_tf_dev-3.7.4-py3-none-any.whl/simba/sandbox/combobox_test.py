from typing import Union, Any, Iterable, Tuple, List, Optional, Callable
from tkinter.ttk import Combobox, Style
from tkinter import *
from simba.utils.enums import Formats


class SimBADropDown(Frame):
    def __init__(self,
                parent: Union[Frame, Canvas, LabelFrame, Toplevel, Tk],
                dropdown_options: Union[Iterable[Any], List[Any], Tuple[Any]],
                label: Optional[str] = None,
                label_width: Optional[int] = None,
                label_font: tuple = Formats.FONT_PLAYWRITE.value,
                dropdown_font_size: Optional[int] = None,
                justify: str = 'center',
                dropdown_width: Optional[int] = None,
                command: Callable = None,
                value: Optional[Any] = None):

        super().__init__(master=parent)
        self.dropdown_var = StringVar()
        self.dropdown_lbl = Label(self, text=label, width=label_width, anchor="w", font=label_font)
        self.dropdown_lbl.grid(row=0, column=0)
        self.dropdown_options = dropdown_options
        self.command = command
        if dropdown_font_size is None:
            drop_down_font = None
        else:
            drop_down_font = ("Poppins", dropdown_font_size)
        self.dropdown = Combobox(self, textvariable=self.dropdown_var, font=drop_down_font, values=self.dropdown_options, state="readonly", width=dropdown_width, justify=justify)
        self.dropdown.grid(row=0, column=1, sticky="nw")
        if value is not None: self.set_value(value=value)
        if command is not None:
            self.command = command
            self.dropdown.bind("<<ComboboxSelected>>", self.on_select)

    def set_value(self, value: Any):
        self.dropdown_var.set(value)

    def get_value(self):
        return self.dropdown_var.get()

    def enable(self):
        self.dropdown.configure(state="normal")

    def disable(self):
        self.dropdown.configure(state="disabled")

    def getChoices(self):
        return self.dropdown_var.get()

    def setChoices(self, choice):
        self.dropdown_var.set(choice)

    def on_select(self, event):
        selected_value = self.dropdown_var.get()
        self.command(selected_value)



def print_results(x):
    print(x)


root = Tk()
dd = SimBADropDown(parent=root, dropdown_options=['s', 'w', 'ss', 'pp'], label='ssss:', label_width=20, value='KUK', dropdown_width=40, command=print_results)
dd.grid(row=0, column=0)
#dd.disable()


root.mainloop()