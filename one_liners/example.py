[exec('import importlib'), globals().update({'__import': importlib.import_module})]
"""\noh wow, a file that shows some basic functionalities of this project!\n"""
[globals().update({'typing': __import('typing'), 'sys': __import('sys')})]
[(lambda module: globals().update({n: getattr(module, v) for n, v in [('pathsep', 'pathsep'), ('scan', 'scandir')]}))(__import('os'))]
_ = ( "a tuple construction", "how original" )
_ = [ ( "nested tuple construction and list construction" ) ]
'# and an in-line comment!'
print("hi!")
print("new statement, same line!")
print(typing, sys.dont_write_bytecode, pathsep, scan)
