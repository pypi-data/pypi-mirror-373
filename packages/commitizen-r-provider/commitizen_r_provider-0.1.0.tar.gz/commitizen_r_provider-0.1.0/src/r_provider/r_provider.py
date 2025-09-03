from pathlib import Path
from commitizen.providers.base_provider import VersionProvider
import re

class RProvider(VersionProvider):
    '''
    Version provider for DESCRIPTION files standard for R packages, based on Debian control file format.

    Args:
        VersionProvider (_type_): Base class from commitizen
    '''
    
    # version should be series of letters, numbers, periods, dashes 
    # btw "Version: " and "\n"
    file = Path('DESCRIPTION')
    patt = re.compile(r'(?<=Version:\s)([0-9a-z\-\.]+)(?=\n)')
    
    
    # def __init__(self, file: str | Path):
    #     self.file = Path(file)
    #     self.patt = re.compile(r'(?<=Version:\s)([0-9a-z\-\.]+)(?=\n)')
    
    def get_version(self) -> str:
        txt = self.file.read_text()
        return self.extract_version(txt)

    def set_version(self, version: str):
        oldtxt = self.file.read_text()
        newtxt = self.replace_version(oldtxt, version)
        self.file.write_text(newtxt)
        
    def extract_version(self, text: str) -> str:
        return self.patt.findall(text)[0]
    
    def replace_version(self, text: str, version: str) -> str:
        return self.patt.sub(version, text)