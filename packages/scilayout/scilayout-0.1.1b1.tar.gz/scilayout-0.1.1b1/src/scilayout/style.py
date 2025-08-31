"""Define the parameters for the layout of scientific plots.


```scilayout.params['panellabel.font'] = 'sans-serif'```


"""

import json

# --- Handle styling of scilayout elements
# This dictionary defines the default styles used across scilayout.
# These can be overridden by the user by using a configuration file using scilayout.style.use(path/to/json) or by modifying the dictionary directly.
# The user can also set the parameters directly in the plotting functions/classes, which will override the stylesheet.
defaultstyles = {
    # classes.py
    # i.e. special cases of text/label styling
    # 'figuretext.font': 'sans-serif',
    'figuretext.fontsize': 8,
    'figuretext.fontstyle': 'normal',
    'figuretext.fontweight': 'normal',
    'panellabel.case': None,
    'panellabel.font': 'sans-serif',
    'panellabel.fontsize': 12,
    'panellabel.fontstyle': 'normal',
    'panellabel.fontweight': 'bold',
    'panellabel.xoffset': -0.5,
    'panellabel.yoffset': -0.1,
    
    'scalebars.fontsize': 8,
    'scalebars.linewidth': 1,
    'stats.linecolor': 'black',
    'stats.linewidth': 1,
    'stats.drop_amount': 0.025,
}

class StyleDictionary(dict):
    """A dictionary that allows access to keys as attributes"""
    # This is like matplotlib.rcParams but not so complicated (and validated) that it does your head in
    
    def __init__(self):
        super().__init__(defaultstyles.copy())
    
    def __setitem__(self, name, value):
        # Validate the key
        if name not in self.keys():
            raise ValueError(f"Invalid key: {name}. Can only set existing keys.")
        super().__setitem__(name, value)
        
    def _setitem_bypass(self, name, value):
        """Bypass the validation for setting the dictionary directly"""
        super().__setitem__(name, value)
    
    def __getattr__(self, key):
        return self[key]

params = StyleDictionary()

# --- Config file handling ---

def _load_config(filepath):
    """Load a configuration file to set parameters
    :param filepath: Path to the json configuration file
    :type filepath: str
    :return: Dictionary of parameters
    :rtype: dict
    """
    # Why JSON and not the same format as matplotlib? Because their implementation is too complicated to replicate here.
    # Fight me.
    with open(filepath, 'r') as f:
        config = json.load(f)
    return config

def use(filepath, params=params, allow_only_valid_keys=True):
    """Use a configuration file to set parameters

    :param filepath: Path to the configuration file
    :type filepath: str
    :param params: The dictionary to set the parameters in
    :type params: dict, optional
    :param allow_only_valid_keys: Whether to allow only keys that are already in the dictionary
    :type allow_only_valid_keys: bool, optional
    """
    config = _load_config(filepath)
    
    if allow_only_valid_keys:
        config_keys = config.keys()
        valid_keys = params.keys()
        failing_keys = []
        for key in config_keys:
            if key not in valid_keys:
                failing_keys.append(key)
        if len(failing_keys) > 0:
            # This error will occur if your configuration file has other options
            # If you're patching in something fresh, you might want to consider setting up some default values using params._setitem() first.
            # For example, if you're adding a new parameter called 'newparam', you could do:
            # params._setitem('newparam', 'defaultvalue')
            raise ValueError(f"Invalid keys in configuration file: {failing_keys}")
    
    for key in config:
        if key in params:
            # If allow_only_valid_keys is False, this would allow you to have other non-scilayout parameters in the config file 
            params[key] = config[key]

def reset():
    """Reset the parameters to the default values"""
    for key in params.keys():
        params[key] = defaultstyles[key]