#project2/PyJSH/console/log.py
class Log:
    def __init__(self,text,sep=" ",end="\n"):
        self.sep=sep
        self.end=end
        self.text=text
        print(self.text,sep=self.sep,end=self.end)
        