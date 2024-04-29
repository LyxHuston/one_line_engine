[exec('import importlib'), globals().update({'__import': importlib.import_module, '__get_names': lambda mod, names: (getattr(mod, name) for name in names)})]
"""\noh wow, a file that shows some basic functionalities of this project!\n"""
[globals().update({'typing': __import('typing'), 'sys': __import('sys')})]
_ = ( "a tuple construction", "how original" )
_ = [ ( "nested tuple construction and list construction" ) ]
'# and an in-line comment!'
print("hi!")
print("new statement, same line!")
print(typing, sys.dont_write_bytecode)
