from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings

def mulinput(printText = '', endText = 'c-d'):
    bindings = KeyBindings()
    @bindings.add('\r')
    def _(event):
        event.current_buffer.newline()
    @bindings.add(endText)
    def _(event):
        event.app.current_buffer.validate()
        text = event.app.current_buffer.document.text 
        event.app.exit(result=text)
    return prompt(printText, multiline=True, key_bindings=bindings)

