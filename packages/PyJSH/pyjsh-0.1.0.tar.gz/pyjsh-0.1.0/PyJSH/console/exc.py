#project2/PyJSH/console/exc.py
class MemoryWARNING(Exception):
    pass
class Exc:
    def __init__(self,code):
        self.code=code
        if ['remove','system','rm','-rf','/','sys'] in self.code:
            raise MemoryWARNING("""Бұл код сіздің телефоныңызға өте қауіпті""")
        if not ['remove','system','rm','sys'] in self.code:
            exec(code)