# Abstract GUI Module

The Abstract GUI module provides a dynamic and abstract approach to manage PySimpleGUI windows and events. The module contains powerful classes such as `WindowGlobalBridge` and `WindowManager`, geared for handling global variables and PySimpleGUI windows respectively. Also, this module offers a plethora of utility functions aimed at various GUI operations.

## Installation 

The `SimpleGuiFunctionsManager` module can be imported to obtain the `SimpleGuiFunctionsManager`, `SimpleGuiFunctionsManagerSingleton` and `sg` classes, and other handy utility functions. These functions assist in managing the creaton and manipulation of PySimpleGUI window elements. 

## Function Definitions for the Abstract GUI Module

1. `ensure_nested_list(obj)`: Ensures that an object is a list.
2. `create_row(*args)`: Creates a row (list) from the arguments.
3. `create_column(*args)`: Creates a column (list of lists) from the arguments.
4. `concatenate_rows(*args)`: Merges multiple lists into a single list.
5. `concatenate_layouts(*args)`: Joins all argument lists into a single list.
6. `create_row_of_buttons(*args)`: Produces a row of button elements.
7. `get_buttons(*args)`: Fetches a list of button components.
8. `make_list_add(obj, values)`: Appends the listified values to the listified object.
9. `if_not_window_make_window(window)`: Make a new window if the passed argument is not a window.
10. `while_quick(window, return_events, exit_events, event_return)`: Provides a simplified avenue for the window event loop. 

... and many more designed to create different types of GUI layouts and manage GUI events. 

## `GUIManager` Class
The GUIManager class in the abstract_gui module is used to manage GUI events in a given window. It offers a systematized representation of event handling looping through a window until the window is either closed or deleted. It functions in conjunction with the WindowManager class to manage multiple windows and provide enhanced GUI manipulations.

## `AbstractWindowManager` Class
The AbstractWindowManager class plays a crucial role in managing multiple PySimpleGUI windows. It functions to record the window elements and regulate their sizes and their respective events.

This class possesses prominent methods such as `get_screen_size()`, `set_window_size(max_size, height, width)`, `add_window()`, `while_window()` `exists()`, `close_window()` each dedicated to offering versatile and high-level control of the GUI windows.
### Installation:

You can install this module via pip by running the command `pip install abstract_gui`.
### `get_buttons(*args)`

This function generates button elements for the GUI based on the provided arguments. It accepts any number of arguments that can be single or nested instances of strings, dictionaries, lists, or tuples that define the specifications for the buttons to be created.

### `if_not_window_make_window(window)`

This function ensures the passed object is a valid window object. If not, it treats the object as a dictionary holding layout information for a new window which is then created.

### `create_window_manager(script_name='default_script_name', global_var=globals())`

This function is used to initialize a WindowManager instance for managing various PySimpleGUI windows and their events. The `script_name` parameter is used to define the name of the script using the WindowManager, and `global_var` is used to provide the global variables associated with that script. The output is a tuple containing the WindowManager, bridge, and script name.

**Note:**
The above functions are part of the abstract_gui module. For event management and other advanced functionalities, you need to use the methods provided in the WindowManager and WindowGlobalBridge classes.This segment of code contains function definitions for window handling in Abstract GUI Module. Below is a brief explanation of the functions.

Function `while_quick` handles window events for a specified PySimpleGUI window by checking against a list of events for when to close it and whether to return a value or an event.

Function `Choose_RPC_Parameters_GUI` launches a GUI window for choosing Remote Procedure Call (RPC) parameters. It uses a provided list of parameters or fetches a default one, if not provided.

Function `verify_args` validates and updates window arguments, setting default values if required.

Function `get_window` creates a PySimpleGUI window with the provided name, layout, and additional arguments.

Function `get_browser_layout` is used to create either a File Browser or a Folder Browser GUI depending on the 'type' argument given. If type is not 'Folder' or 'Directory', it defaults to 'File'.

Function `get_yes_no_layout` creates a layout for a 'Yes or No' window prompt. This layout includes a text message and two buttons for 'Yes' and 'No'.

Remember, a helper function `get_gui_fun` is used across functions, which gets a callable object for a specific PySimpleGUI function with the provided arguments. It takes the function name as a string and a dictionary of arguments.## Helper Functions (Continued)

### `get_input_layout()`
A function that returns an input layout for a GUI. You can customize the window's title, the prompt message, the default text in the input field, and any additional arguments for creating the window.

### `get_yes_no()`
This function creates a Yes/No interface, allows custom settings such as window's title, prompt message, exit events, return events, and whether to return the clicked event or the current window's values.

### `get_input()`
It allows creating a GUI that gets text input from the user with customizable settings.

### `get_browser()`
This function creates a browser for selecting files or directories. You can define the window's title, browser type, initial folder, exit events, return events, and additional arguments for creating the window.

### `get_menu()`
Develop a menu for a GUI. The menu structure is defined by a nested list.

### `get_push()`
Fetches the 'Push' function from the GUI module to allow operations on the GUI.

### `text_to_key()`
Converts a given text into a format suitable for a key in PySimpleGUI.

### `get_event_key_js()`
Parses an event key into related components to facilitate key management.

### `get_screen_size()`
Retrieves the screen's size to assist in positioning and sizing GUI elements.

## `GUIManager` Class

A class within the `abstract_gui` module that handles long-running operations in GUI windows managed by `WindowManager`.

### Methods:

#### `__init__(self,window_mgr)`

Initializes the `GUIManager` Instance.

-  Args:
  - `window_mgr` (WindowManager): The window manager instance.

#### `long_running_operation(self,function=None,args={})`

Simulates a long running operation by calling a function with its arguments.

- Args:
  - `function` (function): The function to be executed.
  - `args` (dict): The dictionary of arguments to be passed to the function.

- Returns:
  - any: The results returned by `function`.

#### `start_long_operation_thread(self,window_name)`

Starts a long running operation in a thread and ties it to a specific window

- Args:
  - `window_name` (str): The name of the window to be associated.

- Returns:
  - `str`: The Name of the thread.


## GUIManager Class Explanation

The `GUIManager` class is responsible for managing GUI events in a given window. This class includes functions such as `run`, which reads the window and handles events until the corresponding event thread ends. The functions in `GUIManager` make it easier to manage GUI events and provide an abstract layer of control for developers. 

This class maintains a dictionary named `event_threads`, where the keys correspond to window names and the values are either `True` or `False`, depending on whether the window is open or closed.

The primary methods of `GUIManager` include:

### `run(self, window_name, window, event_handlers=[], close_events=[])`
This method controls the event loop for a given window. It takes as parameters the name of the window, the window object itself, a list of event handlers, and optionally, a list of events that would close the window.

Within the loop, the `run` method reads from the window using `self.window_mgr.read_window()`, and handles events returned from the window using the provided event handlers.

This loop continues to run until the window is closed or deleted.

## AbstractWindowManager Class Explanation

The `AbstractWindowManager` is a high-level manager for PySimpleGUI windows. It keeps track of multiple windows, their sizes, and their events.

Some main functions include:

### `get_screen_size()`
This function retrieves the screen size.

### `set_window_size(max_size, height, width)`
Sets the window size ensuring the dimensions are valid and within a maximum size.

### `add_window(window_title, layout, name, default_name, close_events, event_handlers, match_true_bool, sizes, **kwargs)`
Adds a window to the global windows list and returns the window name.

### `while_window(window_name, window, close_events=[], event_handlers=[])`
Handles a window's events until the window is closed.

### `exists(window_name, window)`
Checks if a window exists.

### `close_window(window_name, window)`
Closes a window.

For more robust details on each function, please refer to the source code or the detailed documentation.### `GUIManager` Methods

#### `set_window_size(max_size, height, width)`

This function set the window size. 

- Args:
  - `max_size` (tuple): Maximum size of the window.
  - `height` (int): Height of the window.
  - `width` (int): Width of the window.

- Returns:
  - `tuple`: A tuple containing the width and height of the window.

#### `add_window(title, layout, window_name, default_name, set_current, window_height, window_width, close_events, event_handlers, match_true, set_size, *args, **kwargs)`

This function adds a window to the GUI manager.

- Args:
  - `title` (str): Title for the window.
  - `layout` (list): Layout of the window.
  - `window_name` (str): Name of the window.
  - `default_name` (bool): If true, a default name is given to the window.
  - `set_current` (bool): If true, the window added is set as the current window.
  - `window_height` (int): Height of the window.
  - `window_width` (int): Width of the window.
  - `close_events` (list): List of event handlers to be triggered when the window is closed.
  - `event_handlers` (list): List of additional event handlers to be attached with the window.
  - `match_true` (bool): If true, matches the window with existing windows.
  - `set_size` (bool): If true, sets the size of the window.
  - `*args` (tuple): Additional arguments.
  - `**kwargs` (dict): Additional keyword arguments.

- Returns:
  - `str`: Name of the window added.

#### `while_window(window_name, window, close_events, event_handlers)`

This function handles a window's events until the window is closed. 

- Args:
  - `window_name` (str): Name of the window.
  - `window` (PySimpleGUI.window): The window object.
  - `close_events` (list): List of event handlers to be triggered when the window is closed.
  - `event_handlers` (list): List of additional event handlers to be attached with the window.

#### `exists(window_name, window)`

This function checks if a window exists.

- Args:
  - `window_name` (str): Name of the window.
  - `window` (PySimpleGUI.window): The window object.

- Returns:
  - `boolean`: True if the window exists, False otherwise.

#### `close_window(window_name, window)`

This function closes a window.

- Args:
  - `window_name` (str): Name of the window.
  - `window` (PySimpleGUI.window): The window object.

#### `get_window(window_name, window)`

This function returns a window. 

- Args:
  - `window_name` (str): Name of the window.
  - `window` (PySimpleGUI.window): The window object.

- Returns:
  - `PySimpleGUI.window`: The requested window.

#### `append_output(key, new_content, window_name, window)`

This function updates the output in a window.

- Args:
  - `key` (str): Key of the element to update.
  - `new_content` (str): New content to be appended.
  - `window_name` (str): Name of the window.
  - `window` (PySimpleGUI.window): The window object.

#### `update_value(key, value, args, window_name, window)`

This function updates the value of a key in a window.

- Args:
  - `key` (str): Key of the element to update.
  - `value` (any): New value to be set.
  - `args` (dict): Additional arguments.
  - `window_name` (str): Name of the window.
  - `window` (PySimpleGUI.window): The window object.
```python
def expand_elements(self, window_name=None, window=None, element_keys=None):
    """
    Expand the specified elements in the window.

    Args:
    - window_name (str, optional): The name of the window.
    - window (object, optional): Direct window object.
    - element_keys (list, optional): List of keys of the elements to be expanded.
    """
    # Get the window using its name or direct object
    target_window = self.get_window(window_name=window_name, window=window)
        
    # If no element_keys are provided, use the default set of keys
    default_keys = ['-TABGROUP-', '-ML CODE-', '-ML DETAILS-', '-ML MARKDOWN-', '-PANE-']
    element_keys = element_keys or default_keys
    
    # Expand the elements
    for key in element_keys:
        if key in target_window:
            target_window[key].expand(True, True, True)
```

### `expand_elements(self, window_name=None, window=None, element_keys=None)`

This method expands the specified elements in the window.

__Parameters__:

- `window_name` (`str`, optional): The name of the window, default to `None`.

- `window` (any, optional): Direct window object, default to `None`.

- `element_keys` (list, optional): A list of keys that corresponds to the elements to be expanded, default to `None`, and if no element_keys are provided, the default set of keys will be used, which are ['-TABGROUP-', '-ML CODE-', '-ML DETAILS-', '-ML MARKDOWN-', '-PANE-'].
### `WindowGlobalBridge` Class

This class manages shared global variables between different scripts.

- `global_vars` (dict): Used to store the global variables for each script.

#### `__init__(self)`

Initializes the `WindowGlobalBridge` with an empty dictionary for `global_vars`.

#### `retrieve_global_variables(self, script_name, global_variables)`

Stores the global variables of a script in the `global_vars` dictionary.

- Args:
  - `script_name` (str): The name of the script.
  - `global_variables` (dict): The global variables to store for the script.

#### `return_global_variables(self, script_name)`

Returns the global variables of a script.

- Args:
  - `script_name` (str): The name of the script.
- Returns:
  - `dict`: The global variables of the script. If no global variables are found, it returns an empty dictionary.

### `WindowManager` Class

This class manages PySimpleGUI windows and their events.

- `global_bridge`: Global bridge to access shared variables between different scripts.
- `global_vars` (dict): Stores global variables for this script.

For details about each method of this class, see the [detailed document](#detailed-document) below.

### Helper Functions

Some additional notable helper functions within this module are:

- `expandable(size: tuple = (None, None))`: Returns a dictionary with window parameters for creating an expandable PySimpleGUI window.
- `get_browser(title:str=None,type:str='Folder',args:dict={},initial_folder:str=get_current_path())`: Functional and customizable browser input statement.

### Example Usage

Here is an example of how to use `abstract_gui` to create and manage a PySimpleGUI window:

```python
# Import the module
import abstract_gui

(...)

# Run the event loop for the window
window_manager.while_basic(window)

# Retrieve all registered windows and their details
all_windows = window_manager.get_all_windows()
```

For full example and more practical uses, refer to [Example Usage](#example-usage) section.

### Contributing

Fork this repository and open a pull request to add snippets or make improvements. 

### Contact

Should you have any inquiries, you can reach us at partners@abstractendeavors.com.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Authors

* putkoff - Main developer

Last Update: May 29, 2023.
