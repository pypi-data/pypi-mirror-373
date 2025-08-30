
import shutil
import textwrap
import tempfile
import threading
import logging
import pyttsx4
import re
import sys
import os
import time
import speech_recognition as sr
from dotenv import load_dotenv
import warnings

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API",
    category=UserWarning,
    module=".*pkgdata"
)
import pygame

logger = logging.getLogger(__name__)
load_dotenv()


DEFAULT_WORD_REPL: dict[str, str] = {
    "dass": "dasi", "gass": "dasi",
    "deact": "deactivate", "de": "deactivate",
    "shut down": "shutdown", "a i": "ai",
    "fuc": "fuck", "fuckkk": "fuck", "fuckk": "fuck", "fuckkker": "fucker",
    "fuckker": "fucker", "fuckkking": "fucking", "fuckking": "fucking", "motherfuker": "motherfucker",
    "bich": "bitch"
}


DEFAULT_COMMANDS = {
    'voice': [
        "switch to voice", "voice mode", "enable voice", "listen to me", "activate voice"
    ],
    'keyboard': [
        "switch to keyboard", "keyboard mode", "type mode", "disable voice", "back to typing"
    ],
    'standby': [
        "standby", "go to sleep", "wait mode", "stop listening"
    ],
    'deactivate': [
        "deactivate", "shutdown"
    ],
    'pause': [
        "pause", "hold on", "wait", "wait a minute"
    ],
    'resume': [
        "resume", "continue", "carry on", "ok continue"
    ],
    'stop': [
        "stop", "halt", "end", "cancel"
    ]
}

ASSISTANT_GENDER = "Female" # Default gender for the assistant
DEFAULT_MODE = 'keyboard'  # Default input mode'

from HoloTTS import HoloTTS
from HoloSTT import HoloSTT
from HoloWave import HoloWave

class HoloEcho:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent=None, commands=None):
        super().__init__()
        if hasattr(self, "initialized"):
            return

        self.parent = parent

        self.ambInputLock    = threading.Lock()
        self.engine          = pyttsx4.init()
        self.recognizer      = sr.Recognizer()
        self.gender          = getattr(self.parent, "gender", ASSISTANT_GENDER) if self.parent else ASSISTANT_GENDER
        self.mode            = getattr(self.parent, "mode", DEFAULT_MODE) if self.parent else DEFAULT_MODE
        self.commands        = {**DEFAULT_COMMANDS, **(commands or {})}
        #self.wordRepl        = getattr(self.parent, "wordRepl", None) if self.parent else None
        #self._setWordRepl(getattr(self.parent, "wordRepl", None) if self.parent else None)
        self.wordRepl        = {**DEFAULT_WORD_REPL, **(getattr(self.parent, "wordRepl", {}) if self.parent else {})}
        self.decibelFactor   = getattr(self.parent, "decibelFactor", 0) if self.parent else 0
        self.semitoneFactor  = getattr(self.parent, "semitoneFactor", 0) if self.parent else 0
        self.stepFactor      = getattr(self.parent, "stepFactor", 0) if self.parent else 0
        self.soundChannel    = getattr(self.parent, "soundChannel", 2) if self.parent else 2
        self.soundChoice     = getattr(self.parent, "soundChoice", 1) if self.parent else 1
        self.timeOut         = getattr(self.parent, "timeOut", 10) if self.parent else 10
        self.standardMaleVoice   = getattr(self.parent, "standardMaleVoice", 0) if self.parent else 0
        self.standardFemaleVoice = getattr(self.parent, "standardFemaleVoice", 1) if self.parent else 1
        self.advancedMaleVoice   = getattr(self.parent, "advancedMaleVoice", 1) if self.parent else 1
        self.advancedFemaleVoice = getattr(self.parent, "advancedFemaleVoice", 1) if self.parent else 1
        self.sounds          = getattr(self.parent, "sounds", {}) if self.parent else {}
        self.synthesisMode   = getattr(self.parent, "synthesisMode", 'Standard') if self.parent else 'Standard'
        self.isActivated     = getattr(self.parent, "isActivated", False) if self.parent else False
        self.useFallback     = getattr(self.parent, "useFallback", True) if self.parent else True
        self.printing        = getattr(self.parent, "printing", False) if self.parent else False
        self.synthesizing    = getattr(self.parent, "synthesizing", False) if self.parent else False
        self.fileName        = getattr(self.parent, "fileName", None) if self.parent else None
        self.deactivating    = getattr(self.parent, "deactivating", False) if self.parent else False
        self.processing      = getattr(self.parent, "processing", False) if self.parent else False
        self.paused          = getattr(self.parent, "paused", False) if self.parent else False
        self.storedOutput    = getattr(self.parent, "storedOutput", []) if self.parent else []
        self.storedInput     = getattr(self.parent, "storedInput", '') if self.parent else ''
        self.ambInput        = getattr(self.parent, "ambInput", None) if self.parent else None
        self.startMsg        = False
        self._buildPhraseMap()

        self.holoTTS  = HoloTTS(self) # Initialize the HoloTTS generator
        self.holoSTT  = HoloSTT(self) # Initialize the HoloTTS recognizer
        self.holoWave = HoloWave(self)  # Initialize the HoloWave instance
        self.initialized = True

    def _buildPhraseMap(self):
        self.phraseMap = {}
        for cmd, phrases in self.commands.items():
            for phrase in phrases:
                self.phraseMap[phrase] = cmd

        # print("Phrase Map:")
        # for cmd, phrases in self.commands.items():
        #     phraseList = ', '.join(f'"{p}"' for p in phrases)
        #     print(f"  {cmd}: {phraseList}")


    def getProperty(self, propName):
        """
        Retrieves properties from the TTS engine, HoloEcho instance, or special settings.
        """
        propMap = {
            # pyttsx4/pyttsx3 engine properties
            "rate":   lambda: self.engine.getProperty('rate'),
            "volume": lambda: self.engine.getProperty('volume'),
            "voice":  lambda: self.engine.getProperty('voice'),
            "voices": lambda: self.engine.getProperty('voices'),
            "pitch":  lambda: self.engine.getProperty('pitch'),  # pyttsx4 only

            # pygame mixer properties
            "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
            "soundChoice":  lambda v: setattr(self, "soundChoice", int(v)),

            # HoloEcho specific configs
            "gender":        lambda v: setattr(self, "gender", v.lower()),
            "mode":          lambda v: setattr(self, "mode", v.lower()),
            "timeOut":       lambda v: setattr(self, "timeOut", int(v)),
            "useFallback":   lambda v: setattr(self, "useFallback", bool(v)),
            "printing":      lambda v: setattr(self, "printing", bool(v)),
            "synthesizing":  lambda v: setattr(self, "synthesizing", bool(v)),
            "synthesisMode": lambda v: setattr(self, "synthesisMode", v),
            "commands":      lambda v: setattr(self, "commands", v),
            "wordRepl":      lambda v: setattr(self, "wordRepl", v),
        }
        getter = propMap.get(propName)
        if getter:
            return getter()
        else:
            raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

    def setProperty(self, propName, value):
        """
        Sets properties on the TTS engine or HoloEcho instance.
        Supports both pyttsx4 engine properties and HoloEcho-specific settings.
        """
        propMap = {
            # pyttsx4/pyttsx3 engine properties
            "rate":   lambda v: self.engine.setProperty('rate', v),
            "volume": lambda v: self.engine.setProperty('volume', v),
            "voice":  lambda v: self.engine.setProperty('voice', v),
            "pitch":  lambda v: self.engine.setProperty('pitch', v),  # pyttsx4 only

            # pygame mixer properties
            "sounds":       lambda v: setattr(self, "sounds", v),
            "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
            "soundChoice":  lambda v: setattr(self, "soundChoice", int(v)),

            # HoloEcho specific configs
            "standardMaleVoice":   lambda v: setattr(self, "standardMaleVoice", int(v)),
            "standardFemaleVoice": lambda v: setattr(self, "standardFemaleVoice", int(v)),
            "advancedMaleVoice":   lambda v: setattr(self, "advancedMaleVoice", int(v)),
            "advancedFemaleVoice": lambda v: setattr(self, "advancedFemaleVoice", int(v)),
            "gender":          lambda v: setattr(self, "gender", v.lower()),
            "mode":            lambda v: setattr(self, "mode", v.lower()),
            "timeOut":         lambda v: setattr(self, "timeOut", int(v)),
            "useFallback":     lambda v: setattr(self, "useFallback", bool(v)),
            "printing":        lambda v: setattr(self, "printing", bool(v)),
            "synthesizing":    lambda v: setattr(self, "synthesizing", bool(v)),
            "synthesisMode":   lambda v: setattr(self, "synthesisMode", v),
            "commands":        self._setCommands,  # UPDATED: use merge
            #"wordRepl":        lambda v: setattr(self, "wordRepl", v),
            "wordRepl":        self._setWordRepl
        }
        setter = propMap.get(propName)
        if setter:
            setter(value)
        else:
            raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

    def _setCommands(self, userCommands):
        # Always start from the current self.commands (usually has the defaults)
        merged = {}
        # Extend or create each group
        for key in DEFAULT_COMMANDS:
            if userCommands and key in userCommands:
                userList = userCommands[key]
                defaultList = DEFAULT_COMMANDS[key]
                # Combine user + default, no dups, preserve user order
                merged[key] = userList + [x for x in defaultList if x not in userList]
            else:
                merged[key] = DEFAULT_COMMANDS[key][:]
        # If user added new keys (not in defaults), add them as well
        if userCommands:
            for key in userCommands:
                if key not in merged:
                    merged[key] = userCommands[key]
        self.commands = merged
        self._buildPhraseMap()

    def _setWordRepl(self, userRepl):
        norm = lambda s: re.sub(r"\s+", " ", s.strip().lower())

        merged: dict[str, str] = {norm(k): v for k, v in DEFAULT_WORD_REPL.items()}

        if userRepl:
            for k, v in userRepl.items():
                merged[norm(k)] = v  # add/override only, never remove

        self.wordRepl = merged

        # Build one compiled regex for efficient replacement
        tokens = sorted(merged.keys(), key=len, reverse=True)
        escaped = [re.escape(t).replace(r"\ ", r"\s+") for t in tokens]
        pattern = r"(?<!\w)(" + "|".join(escaped) + r")(?!\w)"
        self._wordReplRx = re.compile(pattern, flags=re.IGNORECASE)
        self._wordReplMap = {t.lower(): merged[t] for t in merged}

    def listVoices(self) -> list:
        """Prints and returns all available voices: [idx], Name, Lang, and full ID on its own line."""
        return self.holoTTS.listVoices()

    def manageCommands(self):
        if not self.isActivated:
            return
        while self.synthesizing:
            inBackground = self.ambientInput()
            if inBackground:
                if not (self.paused or self.deactivating):
                    self.handleBackgroundCommands(inBackground)
                    if self.holoSTT.allowInterruption(inBackground):
                        self.handleInterruptionCommands(inBackground)
                else:
                    self.handleBackgroundCommands(inBackground)

    def handleBackgroundCommands(self, command):
        if not self.isActivated:
            return
        if not command:
            return

        # Find the action for the command phrase (case-insensitive)
        action = self.phraseMap.get(command.lower())

        # Mapping action to method calls
        actionMap = {
            "pause":  self.pause,
            "resume": self.resume,
            "stop":   self.stop,
        }

        func = actionMap.get(action)
        if func:
            func()

    def handleInterruptionCommands(self, command):
        if not self.isActivated:
            return
        if command and not self.paused:
            with self.ambInputLock:
                self.ambInput = command
                self.stop()

    def parseCommands(self, command):
        if not command:
            return

        # Find the action for the command phrase (case-insensitive)
        action = self.phraseMap.get(command.lower())
        actionMap = {
            'standby':    self.handleStandby,
            'deactivate': self.handleDeactivation,
            'voice':      lambda: self.handleSwitch('voice'),
            'keyboard':   lambda: self.handleSwitch('keyboard')
        }
        func = actionMap.get(action)
        if func:
            func()

    def handleStandby(self):
        if self.isActivated:
            self.isActivated = False
        return 'standby'

    def handleDeactivation(self):
        self.engine.stop()
        del self.engine
        sys.exit(0)

    def handleSwitch(self, mode):
        if self.mode != mode:
            self.mode = mode
        return mode

    def handleAmbientInput(self) -> str:
        if not self.isActivated:
            return
        if self.deactivating:
            return None
        with self.ambInputLock:
            if self.ambInput:
                msg = self.ambInput
                self.ambInput = None
                return msg.lower().strip()

    def voiceInput(self) -> str:
        return self.holoSTT.voiceInput()

    def ambientInput(self) -> str:
        if self.mode == "keyboard":
            return self.keyboardInput()
        return self.holoSTT.ambientInput()

    def keyboardInput(self, keyboardMsg):
        return self.holoSTT.keyboardInput(keyboardMsg)

    def printMessage(self, type, text, name=None):
        self.printing = True
        name = name if name else self.name if self.name else "Assistant"
        type = type.lower()
        labelMap = {
            'user': "\nYou said",
            'assistant': f"{name.title()}"
        }
        label = labelMap.get(type, "Message")

        # --- Terminal width wrapping ---
        wrapped = self._getTerminal(text)
        # -------------------------------

        print(f"{label}:\n{wrapped}\n")
        self.printing = False

    def streamMessage(self, type, text, mode="char", delay=None, name=None):
        self.printing = True
        name = name if name else self.name if self.name else "Assistant"
        type = type.lower()
        labelMap = {
            'user': "\nYou said",
            'assistant': f"{name.title()}"
        }
        label = labelMap.get(type, "Message")

        print(f"{label}:\n")
        self.printStream(text, mode, delay)

        self.printing = False

    def message(self, type, text, name=None, stream=False, mode="char", delay=None):
        """
        Print or stream a message depending on `stream` flag.
    
        :param type: 'user' or 'assistant'
        :param text: message content
        :param name: assistant name (fallbacks handled)
        :param stream: whether to stream output (default False = instant print)
        :param mode: 'char' or 'word' (only applies if stream=True)
        :param delay: typing delay (applies if stream=True)
        """
        if stream:
            self.streamMessage(type, text, mode, delay, name)
        else:
            self.printMessage(type, text, name)
            
    def printStream(self, text: str, mode: str = "char", delay: float = None):
        if delay is None:
            delay = 0.05 if mode == "char" else 0.13

        # --- Terminal width wrapping ---
        wrapped = self._getTerminal(text)
        # -------------------------------

        if mode == "word":
            for word in wrapped.split():
                sys.stdout.write(word + " ")
                sys.stdout.flush()
                time.sleep(delay)
        else:  # default: char mode
            for char in wrapped:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(delay)

        print("\n")

    def _getTerminal(self, text: str) -> str:
        """Wrap text to fit terminal width with indentation for long lines."""
        try:
            term_width = shutil.get_terminal_size((100, 20)).columns
        except Exception:
            term_width = 100

        lines = text.split('\n')
        wrapped_lines = [
            textwrap.fill(line, width=term_width, subsequent_indent='    ')
            for line in lines
        ]
        return "\n".join(wrapped_lines)

    # def streamInput(self, assistant, user):
    #     if not self.startMsg:
    #         text = (f"\nHello {user}, I am {assistant} your Holo Assistant.\n I'm online and ready to assist you.\n")
    #         self.printStream(text, mode="word", delay=0.13)
    #         self.startMsg = True
    #     return input("Enter your input:\n")

    # def streamOutput(self, text: str, assistant):
    #     print(f"{assistant}:")
    #     self.printStream(text, mode="char", delay=0.05)

    def getSound(self, key: int) -> None:
        self.holoWave.getSound(key)

    def createFile(self, media: str, delete: bool=False) -> None:
        with tempfile.NamedTemporaryFile(delete=delete, suffix=media) as temp_file:
            self.fileName = temp_file.name

    def transcribeContext(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return ""
        return re.sub(r"([.!?]\s*)(\w)", lambda x: x.group(1) + x.group(2).upper(), text.capitalize())

    def setSynthesisMode(self, mode: str=None):
        self.synthesisMode = mode if mode else "Standard"
        return self.synthesisMode

    def getSynthesisMode(self):
        return self.synthesisMode if getattr(self, 'synthesisMode', None) else "Standard"

    # def synthesize(self, text: str) -> None:
    #     if self.mode == "keyboard":
    #         return
    #     self.holoTTS.synthesize(text)
    # def synthesize(self, text: str, useThread: bool=False) -> None:
    #     if self.mode == "keyboard":
    #         return
    #     if useThread:
    #         def run():
    #             self.holoTTS.synthesize(text)
    #         threading.Thread(target=run, daemon=True).start()
    #     else:
    #         self.holoTTS.synthesize(text)
    def synthesize(self, text: str, useThread: bool=False, **kwargs) -> None:
        if self.mode == "keyboard":
            return
        if useThread:
            def run():
                self.holoTTS.synthesize(text, **kwargs)
            threading.Thread(target=run, daemon=True).start()
        else:
            self.holoTTS.synthesize(text, **kwargs)


    def pause(self) -> None:
        self.holoTTS.pause()

    def resume(self) -> None:
        self.holoTTS.resume()

    def stop(self) -> None:
        self.holoTTS.stop()

    def _adjustAttributes(self) -> None:
        self.holoTTS.adjustAttributes()

    def resetAttributes(self) -> None:
        self.holoTTS.resetAttributes()

    def resetProperty(self, prop: str) -> None:
        self.holoTTS.resetProperty(prop)

    def increaseProperty(self, prop: str, value: int = 1) -> None:
        self.holoTTS.increaseProperty(prop, value)

    def decreaseProperty(self, prop: str, value: int = 1) -> None:
        self.holoTTS.decreaseProperty(prop, value)

    def isSynthesizing(self) -> bool:
        return self.holoTTS.isPlaying()

    def isSounding(self) -> bool:
        return self.holoWave.isPlaying()



    def setVoice(self, gender: str = None):
        self.holoTTS.setVoice(gender)

    def resetVoice(self):
        self.resetProperty('voice')

    def setVolume(self, direction: str, value: int = 1):
        action = self._resolveAction(direction)
        if action:
            action('volume', value)
        return self.holoTTS.decibelFactor

    def resetVolume(self):
        self.resetProperty('volume')

    def setPitch(self, direction: str, value: int = 1):
        action = self._resolveAction(direction)
        if action:
            action('pitch', value)
        return self.holoTTS.semitoneFactor

    def resetPitch(self):
        self.resetProperty('pitch')

    def setRate(self, direction: str, value: int = 1):
        action = self._resolveAction(direction)
        if action:
            action('rate', value)
        return self.holoTTS.stepFactor

    def resetRate(self):
        self.resetProperty('rate')

    def _resolveAction(self, direction: str):
        direction = direction.strip().lower()
        if direction in ["increase", "increased", "up"]:
            return self.increaseProperty
        elif direction in ["decrease", "decreased", "down"]:
            return self.decreaseProperty
