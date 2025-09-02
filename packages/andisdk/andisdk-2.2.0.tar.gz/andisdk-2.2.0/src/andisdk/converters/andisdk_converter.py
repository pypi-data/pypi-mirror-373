import sys
import typing   
from .utils import AnyPath, fspath

if not (typing.TYPE_CHECKING or ('sphinx' in sys.modules)):
    import clr
    clr.AddReference('PrimaTestCaseLibrary')
    from PrimaTestCaseLibrary import FileConverterSdk as _FC

def andisdk_convert(infile: AnyPath, outfile: AnyPath):
    infile = fspath(infile)
    outfile = fspath(outfile)
    _FC.Convert(infile, outfile)
