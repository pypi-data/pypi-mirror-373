# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 15:55:24 2024

@author: Alexandre Kenshilik Coche
"""
#%% IMPORT
import numpy as np
import numbers

#%% DISCRETE COLORMAPS FROM PERSONAL CATALOGS
def discrete(sequence_name='ibm', alpha=1, black=True, alternate=True, 
                  color_format='float'):
    """
    Generate a standardized colorscale, based on predefined color maps.

    Parameters
    ----------
    sequence_name : {"trio", "duo", "uno", "ibm", "wong"}, optional, default "ibm"
        A flag to choose the colorscale among the available ones.
        
        - ``"trio"``: a 3x9-color scale (+ grays) based on 9 distinct hues.
        
            - Two other colorscales can be derived from this one:
            - ``"duo"``: only the dark and light variations of each hue are returned.
            - ``"uno"``: only the middle variation of each hue is returned.
        
        - ``"wong"``: a 9-color scale (+ black) extended from Wong, adapted for \
colorblindness.
        - ``"ibm"``: a 6-color scale (+ black) extended from IBM colorscale, \
adapted for colorblindness.
        
    alpha : None or float, optional, default 1
        Transparency (from 0 to 1). If ``None``, colors are returned without
        the 4th value.
    black : bool, optional, default True
        If ``False``, the black color (and related gray variations) are not 
        included in the colorscale.
    alternate : bool, optional, default True
        If ``True``, the colorscale is not in rainbow order.
    color_format : {"float", "rbg_str", "rgba_tuple"}, optional, default "float"
        The way to define colors: 
            
            - ``"float"``: ``[0.22, 0.5, 0.99, 0.85]``
            - ``"rgba_str"``: ``"rgba(56.1, 127.5, 252.45, 0.82)"``
            - ``"rgba_tuple"``: ``(56.1, 127.5, 252.45, 0.82)``

    Returns
    -------
    Return a numpy.array where each row is a 1D-array [red, green, blue, alpha],
    with values between 0 and 1, or corresponding list with values converted to
    rgba tuples or strings.

    """
    
    # ---- Initialization
# =============================================================================
#     # OLD CATALOG
#     _cmap_catalog = [
#         [1.000, 0.500, 0.000, 0.9],  # 0. ~ orange
#         [0.980, 0.691, 0.168, 0.9],  # 1. orange-jaune (pour *.html)
#         [0.973, 0.392, 0.420, 0.9],  # 2. orange-rose
#         [0.847, 0.000, 0.035, 0.9],  # 3. ~ rouge royal
#         [0.471, 0.000, 0.118, 0.9],  # 4. ~ blackred
#         [1.000, 0.557, 0.827, 0.9],  # 5. ~ rose bonbon
#         [0.949, 0.000, 0.784, 0.9],  # 6. ~ fuschia
#         [0.655, 0.204, 0.886, 0.9],  # 7. ~ pourpre
#         [0.404, 0.059, 0.902, 0.9],  # 8. ~ violet fugace
#         [0.000, 0.000, 0.470, 0.9],  # 9. ~ bleu marine - noir
#         [0.000, 0.318, 0.910, 0.9],  # 10. ~ bleu
#         [0.000, 0.707, 0.973, 0.9],  # 11. ~ bleu ciel
#         [0.000, 0.757, 0.757, 0.9],  # 12. ~ bleu-vert émeraude
#         [0.625, 0.777, 0.027, 0.9],  # 13. ~ vert
#         [0.824, 0.867, 0.141, 0.9],  # 14. ~ vert-jaune (ou l'inverse)
#         [1.000, 0.784, 0.059, 0.9],  # 15. ~ jaune-orangé
#         [1.000, 0.941, 0.059, 0.9],  # 16. jaune
#         [0, 0, 0, 1],                # 17. ~ noir
#         [0.37, 0.37, 0.37, 1],       # 18. ~ gris sombrero
#         [0.70, 0.70, 0.70, 1],       # 19. ~ gris clairero
#         [0, 0, 0, 0.2],              # 20. ~ noir transparent
#         ]
# =============================================================================

    # NEW CATALOG (more complete)
    # CSS named colors are finally discarded (not distinct enough)
    cmap_catalog = {
        # oranges & yellows
        'darkorange':       [0.737, 0.416, 0.004, 1.0],
        'orange':           [0.996, 0.612, 0.016, 1.0],
        'lightorange':      [0.996, 0.820, 0.549, 1.0],
        # yellows
        'darkyellow':       [0.816, 0.737, 0.004, 1.0],
        'yellow':           [0.996, 0.890, 0.114, 1.0],
        'lightyellow':      [0.998, 0.945, 0.725, 1.0],
        # reds
        'darkred':          [0.659, 0.071, 0.106, 1.0],
        'red':              [0.953, 0.184, 0.286, 1.0],
        'lightred':         [0.961, 0.655, 0.682, 1.0],
        # pinks
        'darkpink':         [0.737, 0.102, 0.620, 1.0],
        'pink':             [0.922, 0.278, 0.843, 1.0],
        'lightpink':        [0.998, 0.522, 0.988, 1.0],
        # violets
        'darkviolet':       [0.435, 0.002, 0.820, 1.0],
        'violet':           [0.616, 0.396, 0.998, 1.0],
        'lightviolet':      [0.788, 0.718, 0.998, 1.0],
        # blues
        'darkblue':         [0.188, 0.188, 0.639, 1.0],
        'blue':             [0.239, 0.525, 0.953, 1.0],
        'lightblue':        [0.278, 0.796, 0.988, 1.0],
        # turquoise
        'darkturquoise':    [0.102, 0.565, 0.592, 1.0],
        'turquoise':        [0.102, 0.839, 0.820, 1.0],
        'lightturquoise':   [0.647, 0.976, 0.925, 1.0],
        # greens
        'darkgreen':        [0.169, 0.494, 0.239, 1.0],
        'green':            [0.290, 0.788, 0.302, 1.0],
        'lightgreen':       [0.659, 0.929, 0.635, 1.0],
        # olive
        'darkolive':        [0.416, 0.533, 0.212, 1.0],
        'olive':            [0.592, 0.769, 0.106, 1.0],
        'lightolive':       [0.835, 0.937, 0.165, 1.0],
        # grays
        'black':            [0.000, 0.000, 0.000, 1.0],
        'sombrero':         [0.370, 0.370, 0.370, 1.0], # ~ css_dimgray
        'darkgray':         [0.663, 0.663, 0.663, 1.0], # ~ clairero
        'lightgray':        [0.827, 0.827, 0.827, 1.0],
        # extended IBM colorscale (https://www.ibm.com/design/language/resources/color-library)
        'skyblue':          [0.188, 0.737, 0.945, 1.0],
        'bleuet':           [0.392, 0.561, 0.998, 1.0],
        'majorette':        [0.471, 0.369, 0.941, 1.0],
        'crimson':          [0.863, 0.149, 0.498, 1.0],
        'tangerine':        [0.996, 0.380, 0.002, 1.0],
        'gold':             [0.996, 0.690, 0.002, 1.0],
        # extended Wong colorscale (https://doi.org/10.1038/nmeth.1618)
        'purple_w':         [0.741, 0.522, 0.998, 1.0],
        'bordeau_w':        [0.533, 0.133, 0.333, 1.0],
        'red_w':            [0.835, 0.369, 0.002, 1.0],
        'orange_w':         [0.902, 0.623, 0.002, 1.0],
        'yellow_w':         [0.941, 0.894, 0.259, 1.0],
        'olive_w':          [0.722, 0.824, 0.624, 1.0],
        'green_w':          [0.002, 0.620, 0.451, 1.0],
        'blue_w':           [0.471, 0.765, 0.929, 1.0],
        'marine_w':         [0.002, 0.365, 0.698, 1.0],
        }
    
    # ---- Pre-generation of combinations
    # COMBINATIONS
    combinations = {
        'trio': np.array([
            'black', 'sombrero', 'darkgray',
            'darkyellow', 'yellow', 'lightyellow',
            'darkorange', 'orange', 'lightorange',
            'darkred', 'red', 'lightred',
            'darkpink', 'pink', 'lightpink',
            'darkviolet', 'violet', 'lightviolet',
            'darkblue', 'blue', 'lightblue',
            'darkturquoise', 'turquoise', 'lightturquoise',
            'darkgreen', 'green', 'lightgreen',
            'darkolive', 'olive', 'lightolive',
            ]),
        'ibm': np.array([
            'black', 'gold', 'tangerine', 'crimson',
            'majorette', 'bleuet', 'skyblue', 
            ]),
        'wong': np.array([
            'black', 'yellow_w', 'bordeau_w', 'purple_w', 
            'red_w', 'orange_w', 'green_w', 'olive_w',
            'marine_w', 'blue_w',
            ]),
    }
    
    # Reorder if alternate == True
    if alternate == True:
        combinations['trio'] \
            = np.reshape(
                np.reshape(
                    combinations['trio'], (int(len(combinations['trio'])/3), 3)
                    )[[0, 9, 3, 6, 2, 5, 8, 4, 7, 1]], 
                (int(len(combinations['trio'])),)
                )
        combinations['ibm'] = combinations['ibm'][[0, 3, 6, 2, 5, 1, 4]]
        combinations['wong'] = combinations['wong'][[0, 5, 9, 6, 1, 8, 4, 2, 3, 7]]
    
    # Remove black colors if specified
    if black == False:
        combinations['trio'] = combinations['trio'][3:]
        combinations['ibm'] = combinations['ibm'][1:]
        combinations['wong'] = combinations['wong'][1:]
    
    # Create derived combinations
    combinations['duo'] \
        = np.reshape(
            np.reshape(
                combinations['trio'], (int(len(combinations['trio'])/3), 3)
                )[:, [0, 2]],
            (int(len(combinations['trio'])/3*2),)
            )
    combinations['uno'] \
        = np.reshape(
            np.reshape(
                combinations['trio'], (int(len(combinations['trio'])/3), 3)
                )[:, 1],
            (int(len(combinations['trio'])/3),)
            )
    
    # ---- Generation the color map
    cmap = np.array([cmap_catalog[k] for k in combinations[sequence_name]])
    
    # Apply or remove alpha
    if alpha is None:
        cmap = cmap[:, 0:-1]
    else:
        cmap[:, -1] = alpha
        if alpha > 1:
            print("Warning: alpha is usually expected to be within 0 and 1")
        
    # Apply the color format
    if color_format.split('_')[0] == 'rgba':
        if alpha is None:
            cmap = cmap*255
        else:
            cmap[:, :-1] = cmap[:, :-1]*255
        cmap = cmap.tolist()
            
    if color_format == 'rgba_tuple':
        cmap = [tuple(cmap[i]) for i in range(0, len(cmap))]
    elif color_format == 'rgba_str':
        if alpha is not None:
            cmap = ['rgba' + str(tuple(cmap[i])) for i in range(0, len(cmap))]
        else:
            cmap = ['rgb' + str(tuple(cmap[i])) for i in range(0, len(cmap))]
        
    
    return cmap

#%% CONTINUOUS COLORSCALES FROM 2 OR 3 COLORS 
def custom(n_steps, *args):
    """
    args:
        color1, color2, color3... en format [Rouge Vert Bleu Alpha]
        (valeurs entre 0 et 1)
    """
    
    if len(args) == 4:
        n_steps_adjusted = int(n_steps/(len(args)-1))+1
        color_cmap = np.zeros(shape = (n_steps, 4))
        color_cmap[0:n_steps_adjusted, :] = custom_2_colors(n_steps_adjusted, args[0], args[1])
        color_cmap[n_steps_adjusted:2*n_steps_adjusted-1, :] = custom_2_colors(n_steps_adjusted, args[1], args[2])
        color_cmap[2*n_steps_adjusted-1:, :] = custom_2_colors(n_steps-(2*n_steps_adjusted-1)+1, args[2], args[3])
    
    elif len(args) == 3:
        n_steps_adjusted = int(n_steps/(len(args)-1))+1
        color_cmap = np.zeros(shape = (n_steps, 4)) #zeros(floor(n_steps/(nargin-2))*(nargin-2)+1, 3)
        color_cmap[0:n_steps_adjusted, :] = custom_2_colors(n_steps_adjusted, args[0], args[1])
        color_cmap[n_steps_adjusted-1:, :] = custom_2_colors(n_steps-n_steps_adjusted+1, args[1], args[2])
    
    elif len(args) == 2:
        color_cmap = custom_2_colors(n_steps, args[0], args[1])
    
    elif len(args) == 1:
        color_cmap = custom_2_colors(n_steps, args[0], [1, 1, 1])
        
    return color_cmap

    
def custom_2_colors(n_steps, first_color, last_color):
    # Color format correction (add alpha value):
    if len(first_color) == 3:
        first_color.append(1)
    if len(last_color) == 3:
        last_color.append(1)

    # Initialization
    col_array = np.zeros(shape = (n_steps, 4))
    col_array[0,:] = first_color
    col_array[-1,:] = last_color

    # Filling
    for i in range(0,4):
        incr = (last_color[i]-first_color[i])/(n_steps-1)
        col_array[1:(n_steps-1), i] = first_color[
            i] + np.dot(incr, list(range(1, (n_steps-1))))
    
    return col_array


#%% CONVERSION TOOLS
def to_rgba_str(color):
    """
    This function can convert a color variable of any format (``'float'``, ``'rgba_tuple'``,
    ``'rgba_str'``) and any shape (one color or several colors) into a color variable
    in the ``'rgba_str'`` format, for example::
        
        'rgb(239.95, 227.97, 66.045)'
    
    or::
        
        ['rgb(239.95, 227.97, 66.045)',
         'rgb(135.92, 33.915, 84.915)',
         'rgb(188.95, 133.11, 254.49)',
         'rgb(212.92, 94.095, 0.51)',
         'rgb(120.105, 195.08, 236.895)']

    Parameters
    ----------
    color : list, numpy.array, tuple or str
        Input color variable to convert.

    Returns
    -------
    A color variable similar to the input, but in the ``'rgba_str'`` format.

    """
    
    # ---- Handling lists
    if isinstance(color, list):
        color = color.copy() # to avoid rewriting on top of the same list
        
        # If color contains a list of numerical values, it is converted to a
        # np.array, which will be handled in the following part
        if isinstance(color[0], numbers.Number):
            color = np.array(color)
        # Else if color contains a list of iterables, this to_rgba_str function
        # is recursively called to convert each element of color
        else:
            color_str = []
            for i in range(0, len(color)):
                # color[i] = to_rgba_str(color[i])
                color_str.append(to_rgba_str(color[i]))
            return color_str
    
    # ---- Handling np.arrays
    if isinstance(color, np.ndarray):
        color = color.copy() # to avoid rewriting on top of the same list
        
        # If color contains a 1D-array, it is converted to a
        # string rgba or rgb depending on the presence/absence of alpha
        if isinstance(color[0], numbers.Number):
            if len(color) == 4:
                color[:-1] = color[:-1]*255
                return 'rgba' + str(tuple(color.tolist()))
            elif len(color == 3):
                color = color*255
                return 'rgb' + str(tuple(color.tolist()))
        # Else if color contains a 2D-array, this to_rgba_str function
        # is recursively called to convert each element of color
        else:
            color_str = []
            for i in range(0, color.shape[0]):
                # color[i] = to_rgba_str(color[i])
                color_str.append(to_rgba_str(color[i]))
            # return color.tolist()
            return color_str
    
    # ---- Handling other simplier cases
    elif isinstance(color, tuple):
        if len(color) == 4:
            return 'rgba' + str(color)
        elif len(color) == 3:
            return 'rgb' + str(color)
    
    elif isinstance(color, str):
        return color


    
    