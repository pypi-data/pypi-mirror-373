# patching the _resume method in phonemizer because logger.setLevel(logging.ERROR) doesn't work - the logger instance is created and stored in the package.
try:
    from phonemizer.backend.espeak.words_mismatch import BaseWordsMismatch
    
    def silent_resume(self, nmismatch, nlines):
        """Silent version of _resume that suppresses warnings"""
        pass
    
    BaseWordsMismatch._resume = silent_resume
    
except ImportError:
    pass