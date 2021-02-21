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
                    a function : modify the function called after a parameter is set and
                        display a tk.Text popup
    columns -- give a tuples of strings if you want to have more columns
    width_parameter -- set the width of the first column (integer)
    width_value -- set the width of all other columns (integer)

    Public attribute:
    columns_list: store the columns of the treeview
    lines_list: store lines_parameters
    popup_window: store the popup (tk.Toplevel), (destroyed when validated)
    callback_at_validation: function called after a parameter is set or validated
    """

    def __init__(self, master=None, width_parameter=200, width_value=50, **kwargs):
        # initialize class attribute and give some examples
        if "columns" not in kwargs:
            kwargs["columns"] = ("Value",)
        if "lines_parameters" not in kwargs:
            kwargs["lines_parameters"] = [("", "param0", "1", ["a", "c", "g", "d"], True),
                                          ("param0", "param1", "2", bool(), True),
                                          ("param1", "param2", "3", "Text", True),
                                          ("", "param3", "4", bool(), True), ]
        # select argument for parent's class
        kwargstreeview = copy.deepcopy(kwargs)  # create a copy to build the dictionary for the treeview structure
        kwargstreeview.pop("lines_parameters")
        super(TreeviewMenu, self).__init__(master, **kwargstreeview)  # initialize a treeview widget
        self.columns_list = ("#0",)+kwargs["columns"]  # create a list to store columns
        self.lines_list = kwargs["lines_parameters"]  # store the list describing the treeview menu
        # create the menu
        for name_column in self.columns_list:  # initialize columns header
            if name_column == "#0":
                self.column(name_column, width=width_parameter, minwidth=50, stretch=False)
                self.heading(name_column, text="Parameter", anchor="w")
            else:
                self.column(name_column, width=width_value, minwidth=50, stretch=False)
                self.heading(name_column, text=name_column, anchor="w")
        self.popup_window = None
        self.popup_widget = None
        self.bind("<Double-Button-1>", self.do_popup)
        self.bind("<KeyPress-Return>", self.do_popup)
        self.callback_at_validation = lambda: None  # initialize the function called after a parameter is validated

    def create_parameter_list(self):
        """initialize the tree view menu for the self.lines_list attribute description"""
        for the_parent, the_child, the_value, dummy_value, *the_expansion in self.lines_list:
            self.insert(the_parent, 'end', the_child, text=the_child)
            if isinstance(the_value, type(list())):
                self.item(the_child, values=the_value)
            else:
                self.item(the_child, values=(the_value,))
            self.item(the_child, open=bool(the_expansion[0]))
        self.selection_set(self.lines_list[0][1])
        self.focus_set()
        self.focus(self.lines_list[0][1])

    def clear_parameter_list(self):
        """remove all item in the treeview widget"""
        self.delete(*self.get_children())

    def update_lines_list(self, parameter, values, position=1):
        """update the value stored in the self.lines_list descriptor if position=1,
        if position=2 change the type of the parameter
        tip: can be used to update the list to be displayed in the combox popup"""
        for i in range(len(self.lines_list)):
            if self.lines_list[i][1] == parameter and position == 1:
                self.lines_list[i] = self.lines_list[i][0:2] + (values,) + self.lines_list[i][3:]
            elif self.lines_list[i][1] == parameter and position == 2:
                self.lines_list[i] = self.lines_list[i][0:3]+(values,) + (self.lines_list[i][4],)

    def do_popup(self, event):
        """assess which input has been selected and call the right method depending on the input"""
        # if you want to select the item were the mouse is :item = self.identify_row(event.y)
        # get the selected item
        item = self.focus()
        # avoid toggling between expanded or unexpanded if the item have child
        self.item(item, open=not self.item(item)['open'])
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
                            if isinstance(result, (type(list()), type(tuple()))):
                                self.display_combobox_popup(item, list_combo=result)
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
                        elif isinstance(parameter_value_type, (type(list()), type(tuple()))):
                            self.display_combobox_popup(item, list_combo=parameter_value_type)
                        elif parameter_value_type is None:
                            pass
                        else:
                            print("Error", parameter_value_type, "from", item, ": unsupported data type")
            finally:
                self.grab_release()

    def display_text_popup(self, current_item, text_initialization=None):
        """open a text input popup w/ or w/o initialization"""
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
        """toggle the state of the item in focus"""
        if self.item(current_item)['values'][0] == 'False':
            self.item(current_item, values=['True'])
            self.update_lines_list(current_item, 'True')
        else:
            self.item(current_item, values=['False'])
            self.update_lines_list(current_item, 'False')
        self.callback_at_validation()

    def display_combobox_popup(self, current_item, list_combo=None):
        """display a combobox popup with values from a tuple or a list
         state='readonly' if a tuple is passed as an argument
         state='normal'  if a list is passed as an argument, """
        self.popup_window = tk.Toplevel()
        self.popup_window.title(str(self.focus()) + ': double press "Del" to validate')
        if isinstance(list_combo, type(tuple())):
            self.popup_widget = ttk.Combobox(self.popup_window, values=list_combo, state="readonly")
        elif isinstance(list_combo, type(list())):
            self.popup_widget = ttk.Combobox(self.popup_window, values=list_combo, state="normal")
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
        """handler to detect validation from <Double-KeyPress-Delete> event"""
        if event.keysym == "Delete":
            self.validate_popup(arg)

    def validate_popup(self, parameter):
        """assess the result from the popup window and execute the function self.callback_at_validation
        only text provide support for multi-columns values with one line per column"""
        result = ''
        if isinstance(self.popup_widget, tk.Text):
            result = self.popup_widget.get("1.0", "end-1c")
            result = result.split('\n')
            self.popup_widget.destroy()
            self.popup_widget = None
        if isinstance(self.popup_widget, ttk.Combobox):
            result = self.popup_widget.get() or self.item(parameter)['values'][0]
            self.popup_widget.destroy()
            self.popup_widget = None
        else:
            pass
        if isinstance(result, type(list())):
            self.item(parameter, values=result)
        else:
            self.item(parameter, values=(result,))
        self.popup_window.destroy()
        self.update_lines_list(parameter, result)
        self.callback_at_validation()


if __name__ == '__main__':
    # exemple

    main_window = tk.Tk()
    main_window.title("Fenêtre Menu")
    bt_quit = tk.Button(main_window, text="Quitter", command=main_window.destroy)
    bt_quit.bind("<KeyPress-Return>", lambda arg: main_window.destroy())
    tv_menu = TreeviewMenu(main_window, width_value=200)

    lines_parameters1 = [("", "param0", "1", ["a", "c", "g", "d"], True),
                         ("param0", "param1", "2", bool(), True),
                         ("param1", "param2", "3", "Text", True),
                         ("", "param3", "4", bool(), True),
                         ("param1", "param5", "3", "Text", True), ]

    def function_called_when_param4_clicked(treeviewmenu_in):
        def function_executed_after_validation(treeviewmenu=treeviewmenu_in):
            print('I''m changing the list')
            treeviewmenu.lines_list = lines_parameters1  # set the list to generate the treeview
            treeviewmenu.clear_parameter_list()  # clear the treeview
            treeviewmenu.create_parameter_list()  # generate the treeview
            treeviewmenu.callback_at_validation = lambda: None  # reset the function exectued
        return function_executed_after_validation

    def fonction_to_be_called_param4(arg1=tv_menu):
        return function_called_when_param4_clicked(arg1)

    lines_parameters0 = [("", "param0", "1", ["a", "c", "g", "d"], True),
                         ("param0", "param1", "2", bool(), True),
                         ("param1", "param2", "3", "Text", True),
                         ("", "param3", "4", bool(), True),
                         ("param1", "param5", ("one", "two"), "Text", True),
                         ("", "param4", "let it go", fonction_to_be_called_param4, True), ]
    tv_menu.lines_list = lines_parameters0
    tv_menu.create_parameter_list()
    tv_menu.pack()
    bt_quit.pack()
    main_window.mainloop()
