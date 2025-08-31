'''
Hooks for pyinstaller
'''

import os


def get_hook_dirs():
    '''Returns string of parent directory of this file, which is where hook modules are located.'''
    return [os.path.dirname(__file__)]