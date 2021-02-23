# Interactible treeview with tkinter
Class to create TreeviewMenu object.
This class inherit from the Treeview class from tkinter and allow the user to interact with it to change it state.

Treeview based menu, calls popup to allows user to send input.
    The menu is created from a list of tuple. This class inherit from ttk.Treeview.
    It can execute a function after each change

Keyword argument:
   lines_parameters -- define all parameters in the menu. It except a list of tuples.
        each tuples should be five object long : 1st, string, parent ("", for the root). 2nd, string, name of
         the parameter (should be unique). 3rd, list of string, default value. 4th, parameter type,
        5th initial view, True: expand children.
        details on the 4th parameter, if:
            bool() : will toggle value between True and False
            list of strings : will pop up a window with a tk.Combobox
            text : will pop up a window with a tk.Text editor
            function : run the function and store the result
                if the result is:
                    a list : display a tk.Combobox with the list
                    a str : display a tk.Text with the string as default value
                    a function : modify the function called after a parameter is set and
                        display a tk.Text popup

Public attribute:
    columns_list: store the columns of the treeview
    lines_list: store lines_parameters
    popup_window: store the popup (tk.Toplevel), (destroyed when validated)
    callback_at_validation: function called after a parameter is set or validated
    
 init(self, master=None, width_parameter=200, width_value=50, kwargs)
 create_parameter_list(self):
 clear_parameter_list(self):
 update_lines_list(self, parameter, values, position=1):
 do_popup(self, event):
 display_text_popup(self, current_item, text_initialization=None):
 change_state(self, current_item):
 display_combobox_popup(self, current_item, list_combo=None):
 event_handler(self, arg, event):
 validate_popup(self, parameter):


Some suggestion to add:
add suppprt to allows for multiple columns values
add support to filter integer, float or other type from text input
