#project2/PyJSH/console/input.py
class Input:
    def __init__(self,text):
        self.text=text
        self.value=input(text)
    """қолдану:
        name=Input('атың:')
        console.log('Сәлем',name.value)
    """