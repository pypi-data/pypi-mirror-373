__version__ = '20250506   '

from .path_tool import MyPath
from .project import Project
from .file_version_control import ScriptResultManager as ScriptFileSaver
from .file_version_control import ScriptResultManager
class EasyDict(dict):
    """Convenience class that behaves like a dict but allows access with the attribute syntax."""

    def __getattr__(self, name: str):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value):
        self[name] = value

    def __delattr__(self, name: str):
        del self[name]
        
    @ classmethod
    def load(cls, path):
        """Create an EasyDict from a dict."""
        import pickle
        with open(path, 'rb') as f:
            d = pickle.load(f)
        return cls(d)
    
    def save(self, path):
        """Save an EasyDict to a file."""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self, f)
            
if __name__ == '__main__':
    dict = EasyDict()
    dict['a'] = 1
    
    print('Done')