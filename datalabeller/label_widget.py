from __future__ import print_function # For py 2.7 compat
from IPython.html import widgets # Widget definitions
from IPython.display import display # Used to display widgets in the notebook
from IPython.utils.traitlets import Unicode, Dict # Used to declare attributes of our widge
from IPython.html.widgets import interact, interactive


class LabellerWidget(widgets.DOMWidget):
    _view_name = Unicode('LabellerView', sync=True)
    value = Dict( sync = True) #Unicode(sync=True)
    
    
    def __init__(self, **kwargs):
        super(LabellerWidget, self).__init__(**kwargs)
        self.on_msg(self._handle_button_msg)
        self.description = 'LabellerWidget' 
        
        
    def _handle_button_msg(self, _, content):
        if content.get('event', '') == 'click':
            self.on_click(content)
        elif content.get('event', '') == 'keypress':
            self.on_key_press(content)

    def on_click(self, content):
        pass
#         print("Button {b}".format(b=content['button']))

    def on_key_press(self, content):
#         print("Key {c}".format(c=content['code']))
        
        #Have to add this weirdness as the sync only activates from the backend when the value changes
        #So if we hit the same key twice it doesn't change and so we don't get an event
        self.value = {'key_num' : None, 'key_press':True}
        self.value = {'key_num' : unicode(content['code']), 'key_press':False}                                

