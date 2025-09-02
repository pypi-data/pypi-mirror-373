""" pagesizey.py
    A module that implements a simple function to take in a width and height
    as float numbers and return the closest approximate ansi or iso page size.
"""

size_definitions = {
    # ANSI page sizes (imperial)
    (5, 8): {"standard": "ansi", "size": "a", "common_name": "Junior Legal"},
    (5.5, 8.5): {"standard": "ansi", "size": "a", "common_name": "Half letter"},
    (8.5, 11): {"standard": "ansi", "size": "a", "common_name": "letter"},
    (8.5, 14): {"standard": "ansi", "size": "a", "common_name": "Legal"},
    (9, 12): {"standard": "ansi", "size": "arch a"},
    (11, 17): {"standard": "ansi", "size": "b", "common_name": "Ledger"},
    (12, 18): {"standard": "ansi", "size": "arch b"},
    (17, 22): {"standard": "ansi", "size": "c"},
    (18, 24): {"standard": "ansi", "size": "arch c"},
    (22, 34): {"standard": "ansi", "size": "d"},
    (24, 36): {"standard": "ansi", "size": "arch d"},
    (24, 44): {"standard": "ansi", "size": "e"},
    (36, 48): {"standard": "ansi", "size": "arch e"},
    # ISO page sizes (metric)
    (105, 148): {"standard": "iso", "size": "a6"},
    (148, 210): {"standard": "iso", "size": "a5"},
    (210, 297): {"standard": "iso", "size": "a4"},
    (297, 420): {"standard": "iso", "size": "a3"},
    (420, 594): {"standard": "iso", "size": "a2"},
    (594, 841): {"standard": "iso", "size": "a1"},
    (841, 1189): {"standard": "iso", "size": "a0"},
    (31, 44): {"standard": "iso", "size": "b10"},
    (44, 62): {"standard": "iso", "size": "b9"},
    (62, 88): {"standard": "iso", "size": "b8"},
    (88, 125): {"standard": "iso", "size": "b7"},
    (125, 176): {"standard": "iso", "size": "b6"},
    (176, 250): {"standard": "iso", "size": "b5"},
    (250, 353): {"standard": "iso", "size": "b4"},
    (353, 500): {"standard": "iso", "size": "b3"},
    (500, 707): {"standard": "iso", "size": "b2"},
    (707, 1000): {"standard": "iso", "size": "b1"},
    (1000, 1414): {"standard": "iso", "size": "b0"},
    # Cursed ISO page sizes (metperial)
    (4.1, 5.8): {"standard": "iso", "size": "a6"},
    (5.8, 8.3): {"standard": "iso", "size": "a5"},
    (8.3, 11.7): {"standard": "iso", "size": "a4"},
    (11.7, 16.5): {"standard": "iso", "size": "a3"},
    (16.5, 23.4): {"standard": "iso", "size": "a2"},
    (23.4, 33.1): {"standard": "iso", "size": "a1"},
    (33.1, 46.8): {"standard": "iso", "size": "a0"},
}

def _fuzzy_compare_int(num1:int, num2:int, tolerance:int) -> bool:
    """ _fuzzy_compare_int
        Does an equality toleranced compair between integer numbers.
    """
    return abs(num1 - num2) <= tolerance

def page_size(width:float, height:float) -> dict:
    """ page_size
        args:
            width   float value for width of page
            height  float value for height of page
        returns:
            Dict of the following:
                {
                    "standard": <standard for the page size (ex. ansi or iso)>,
                    "size": <size string, ex. a4 or d>,
                    "common_name": <Optional string of comon name or None> 
                }
    """

    # we create a list out of the dimensions
    dimensions = [width, height]

    # we sort the dimensions list smallest to greatest to match how the 
    # data is stored in the size_definitions key
    dimensions.sort()
    
    size = None

    # yes, this is just brute forced here. Its not elegant, but lets be honest
    # computers are really really fast and this is a really short list!
    for key, size_defined in size_definitions.items():
        if _fuzzy_compare_int(int(dimensions[0]), 
                                int(key[0]), 
                                int(key[0]*.05)):
            if _fuzzy_compare_int(int(dimensions[1]), 
                                int(key[1]), 
                                int(key[1]*.05)):
                size = size_defined
                break # we found a match so abort!
    
    if size == None:
        raise ValueError("ERROR: No size standard for the given dimensions.")
    
    return size