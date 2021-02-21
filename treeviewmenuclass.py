import tkinter as tk
import tkinter.ttk as ttk
import copy


class TreeviewMenu(ttk.Treeview):
    """Treeview based menu, calls popup to allows user to send input.
    The menu is created from a list of tuple. This class inherit from ttk.Treeview.
    It can execute a function after each change

    Keyword argument:
    lines_parameters -- define all parameters in the menu. It except a list of tuples.
        the tuples should be five object long : 1st, string, parent ("", for the root). 2nd, string, name of
         the parameter (should be unique). 3rd, string, default value. 4th, parameter type,
        5th initial view, True: expand children.
        details on the 4th parameter, if:
            bool() : will toggle value between True and False
            list of string : will pop up a window with a tk.Combobox
            text : will pop up a window with a tk.Text editor
            function : run the function and store the result
                if the result is:
                    a list : display a tk.Combobox with the list
                    a str : display a tk.Text with the string as default value
                    a function : modify the function called after execution and
                        display a tk.Text

    Public attribute:
    columns_list: store the columns of the treeview
    lines_list: store lines_parameters
    popup_window: store the popup (tk.Toplevel), (destroyed when validated)
    callback_at_validation: function called after a parameter is set or validated
    """

    def __init__(self, master=None, **kwargs):
        # initialize class attribute and give some examples
        if "columns" not in kwargs:
            kwargs["columns"] = ("Value",)
        if "lines_parameters" not in kwargs:
            kwargs["lines_parameters"] = [("", "param0", "1", ["a", "c", "g", "d"], True),
                                          ("param0", "param1", "2", bool(), True),
                                          ("param1", "param2", "3", "Text", True),
                                          ("", "param3", "4", bool(), True), ]
        # select argument for parent's class
        kwargstreeview = copy.deepcopy(kwargs)
        kwargstreeview.pop("lines_parameters")
        super(TreeviewMenu, self).__init__(master, **kwargstreeview)
        self.columns_list = ("#0",)+kwargs["columns"]
        self.lines_list = kwargs["lines_parameters"]
        # create the menu
        for name_column in self.columns_list:
            if name_column == "#0":
                self.column(name_column, width=200, minwidth=50, stretch=False)
                self.heading(name_column, text="Parameter", anchor="w")
            else:
                self.column(name_column, width=50, minwidth=50, stretch=False)
                self.heading(name_column, text=name_column, anchor="w")
        # create the parameter list
        self.popup_window = None
        self.popup_widget = None
        self.bind("<Double-Button-1>", self.do_popup)
        self.bind("<KeyPress-Return>", self.do_popup)
        self.callback_at_validation = lambda: None

    def create_parameter_list(self):
        for the_parent, the_child, the_value, dummy_value, *the_expansion in self.lines_list:
            self.insert(the_parent, 'end', the_child, text=the_child, values=the_value)
            self.item(the_child, open=bool(the_expansion[0]))
        self.selection_set(self.lines_list[0][1])
        self.focus_set()
        self.focus(self.lines_list[0][1])

    def update_lines_list(self, parameter, values, position=1):
        for i in range(len(self.lines_list)):
            if self.lines_list[i][1] == parameter and position == 1:
                self.lines_list[i] = self.lines_list[i][0:2] + (values,) + self.lines_list[i][3:]
            elif self.lines_list[i][1] == parameter and position == 2:
                self.lines_list[i] = self.lines_list[i][0:3]+(values,) + (self.lines_list[i][4],)

    def do_popup(self, event):
        # if you want to select the item were the mouse is :item = self.identify_row(event.y)
        item = self.focus()
        # Define supported widget type
        if not item or self.popup_widget is not None:
            # Something wrong is happening, The user is already trying to modify a parameter
            self.popup_widget.destroy()
            self.popup_widget = None
            self.popup_window.destroy()
            print('Wrong input, or validate input', type(self.popup_widget))
        else:
            try:  # Fetch the widget depending on the type of the last tuple's item
                for i in self.lines_list:
                    if i[1] == item:
                        parameter_value_type = i[3]
                        # if the parameter is a function:
                        #   call the function and depending of the type
                        #       call a combobox if the function output a list, the option will be from the list
                        #       call a text edit if the function output a string, the text input will be the string
                        #       call a text edit if the function output a string, change the function called at the end
                        #               of the input if the function out a function
                        # if parameter is a list, call a combobox
                        # if parameter is a string, call a textbox
                        # if parameter is a boolean, toggle the value
                        if callable(parameter_value_type):
                            result = parameter_value_type()
                            if isinstance(result, type(list())):
                                self.display_combobox_popup(item, result)
                            elif isinstance(result, type(str())):
                                self.display_text_popup(item, text_initialization=result)
                            elif callable(result):
                                self.callback_at_validation = result
                                self.display_text_popup(item)
                            else:
                                print("Error: the function needs to return a list object")
                        elif isinstance(parameter_value_type, type(str())):
                            self.display_text_popup(item)
                        elif isinstance(parameter_value_type, type(bool())):
                            self.change_state(item)
                        elif isinstance(parameter_value_type, type(list())):
                            self.display_combobox_popup(item, list_combo=parameter_value_type)
                        elif parameter_value_type is None:
                            pass
                        else:
                            print("Error", parameter_value_type, "from", item, ": unsupported data type")
            finally:
                self.grab_release()

    def display_text_popup(self, current_item, text_initialization=None):
        self.popup_window = tk.Toplevel()
        self.popup_window.title(str(self.focus())+': double press "Del" to validate')
        self.popup_widget = tk.Text(self.popup_window, height=2, width=50)
        if text_initialization is None:
            if len(self.item(current_item)['values']):
                self.popup_widget.insert(1.0, str(self.item(current_item)['values'][0]))
        else:
            self.popup_widget.insert(1.0, str(text_initialization))
        self.popup_widget.pack()
        self.popup_widget.focus_set()
        tk.Button(self.popup_window, text="Ok",
                  command=lambda parameter=self.focus(): self.validate_popup(parameter)).pack()
        self.popup_window.tkraise()
        self.popup_widget.bind("<Double-KeyPress-Delete>",
                               lambda event, arg=self.focus(): self.event_handler(arg, event))

    def change_state(self, current_item):
        if self.item(current_item)['values'][0] == 'False':
            self.item(current_item, values=['True'])
            self.update_lines_list(current_item, 'True')
        else:
            self.item(current_item, values=['False'])
            self.update_lines_list(current_item, 'False')
        self.callback_at_validation()

    def display_combobox_popup(self, current_item, list_combo=None):
        self.popup_window = tk.Toplevel()
        self.popup_window.title(str(self.focus()) + ': double press "Del" to validate')
        self.popup_widget = ttk.Combobox(self.popup_window, values=list_combo, state="readonly")
        self.popup_widget.pack()
        temporary_button = tk.Button(self.popup_window, text="Ok",
                                     command=lambda parameter=self.focus(): self.validate_popup(parameter))
        temporary_button.pack()
        temporary_button.bind("<KeyPress-Return>", lambda event, parameter=self.focus(): self.validate_popup(parameter))
        self.popup_widget.focus_set()
        self.popup_window.tkraise()
        self.popup_widget.bind("<Double-KeyPress-Delete>",
                               lambda event, arg=self.focus(): self.event_handler(arg, event))

    def event_handler(self, arg, event):
        if event.keysym == "Delete":
            self.validate_popup(arg)

    def validate_popup(self, parameter):
        result = ''
        if isinstance(self.popup_widget, tk.Text):
            result = self.popup_widget.get("1.0", "end-1c")
            self.popup_widget.destroy()
            self.popup_widget = None
        if isinstance(self.popup_widget, ttk.Combobox):
            result = self.popup_widget.get() or self.item(parameter)['values'][0]
            self.popup_widget.destroy()
            self.popup_widget = None
        else:
            pass
        self.item(parameter, values=[result])
        self.popup_window.destroy()
        self.update_lines_list(parameter, result)
        self.callback_at_validation()


if __name__ == '__main__':
    # exemple
    main_window = tk.Tk()
    main_window.title("Fenêtre Menu")
    bt_quit = tk.Button(main_window, text="Quitter", command=main_window.destroy)
    bt_quit.bind("<KeyPress-Return>", lambda arg: main_window.destroy())
    tv_menu = TreeviewMenu(main_window)
    tv_menu.create_parameter_list()
    tv_menu.pack()
    bt_quit.pack()
    main_window.mainloop()
