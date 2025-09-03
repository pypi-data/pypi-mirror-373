try:
    from prompt_toolkit.completion import WordCompleter, PathCompleter, Completer
    from prompt_toolkit.document import Document
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

from cliify.CommandWrapper import CommandWrapper
import logging 

logger = logging.getLogger("CommandCompleter")

if PROMPT_TOOLKIT_AVAILABLE:
    class CommandCompleter(Completer):
        def __init__(self, cmd: CommandWrapper):
            self.path_completer = PathCompleter()
            self.args_completer = WordCompleter([], ignore_case=True)
            self.base_completer = WordCompleter([], ignore_case=True)
            self.completions_lists = {}
            self.cmd = cmd

        def get_completions(self, document: Document, complete_event):
            text = document.text
            commands = text.split(";")
            words = self.cmd.getCompletions(commands[-1])
            words = [str(word).strip() for word in words ]

            remove_words = []
            

            for word in words:
                if word.startswith("!"):
                    remove_words.append(word)
                    remove_words.append(word[1:])

            for word in words:

                if word == "$file":
                    path_text = document.get_word_before_cursor(WORD=True)
                    path_document = Document(path_text, len(path_text))
                    yield from self.path_completer.get_completions(path_document, complete_event)
                    remove_words.append(word)
                    

                if word =="$commands":
                    path_text = document.get_word_before_cursor(WORD=True)
                    path_document = Document(path_text, len(path_text))
                    cmds = self.cmd.getPathCompletions(path_document.text)
                    self.base_completer.words = [w for w in cmds if w not in remove_words]
                    yield from self.base_completer.get_completions(path_document, complete_event)
                    remove_words.append(word)
                    logging.warning(f"Removed $commands from completions for {path_text}")

            for word in remove_words:
                if word in words:
                    words.remove(word)


            self.base_completer.words = words

            if text.endswith("."):
                text = ""

            path_document = Document(text, len(text))

            
            yield from self.base_completer.get_completions(path_document, complete_event)
else:
    class CommandCompleter:
        """Fallback completer when prompt_toolkit is not available"""
        def __init__(self, cmd: CommandWrapper):
            self.cmd = cmd
            print("Warning: prompt_toolkit is not installed. Command completion is disabled.")