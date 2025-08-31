
import logging
import os
import tempfile
import time
import threading
import re
from collections import deque
from tkinter import SE

import pyttsx4
from dotenv import load_dotenv
from pydub import AudioSegment

import numpy as np
import soundfile as sf
import warnings

warnings.filterwarnings('ignore', message='dropout option adds dropout after all but last recurrent layer.*')
warnings.filterwarnings('ignore', message='.*torch.nn.utils.weight_norm.*is deprecated.*')
warnings.filterwarnings(
    'ignore',
    message='`torch.distributed.reduce_op` is deprecated, please use `torch.distributed.ReduceOp` instead'
)
warnings.filterwarnings('ignore', category=UserWarning, message=r".*pkg_resources is deprecated as an API.*")

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame  # noqa: E402

import pyautogui  # noqa: E402

# Ensure environment variables are loaded
load_dotenv()
logger = logging.getLogger(__name__)

# Human-friendly, for docs
MALE_VOICE_LABEL = {
    1: "American English - Adam",
    2: "American English - Echo",
    3: "American English - Eric",
    4: "American English - Fenrir",
    5: "American English - Liam",
    6: "American English - Michael",
    7: "American English - Onyx",
    8: "American English - Puck",
    9: "British English - Daniel",
    10: "British English - Fable",
    11: "British English - Lewis",
    12: "Japanese - Kumo",
    13: "Chinese Mandarin - Yunxi",
    14: "Chinese Mandarin - Yunxia",
    15: "Chinese Mandarin - Yunyang",
    16: "Hindi - Omega",
    17: "Hindi - Psi",
    18: "Italian - Nicola",
    19: "Portuguese - Alex",
    20: "Spanish - Alex",
    21: "American English - Santa",
}

FEMALE_VOICE_LABEL = {
    1: "American English - Alloy",
    2: "American English - Aoede",
    3: "American English - Bella",
    4: "American English - Heart",
    5: "American English - Jessica",
    6: "American English - Kore",
    7: "American English - Nicole",
    8: "American English - Nova",
    9: "American English - River",
    10: "American English - Sarah",
    11: "American English - Sky",
    12: "British English - Alice",
    13: "British English - Emma",
    14: "British English - Lily",
    15: "French - Siwis",
    16: "Japanese - Alpha",
    17: "Japanese - Gongitsune",
    18: "Japanese - Nezumi",
    19: "Japanese - Tebukuro",
    20: "Chinese Mandarin - Xiaobei",
    21: "Chinese Mandarin - Xiaoni",
    22: "Chinese Mandarin - Xiaoxiao",
    23: "Chinese Mandarin - Xiaoyi",
    24: "Hindi - Alpha",
    25: "Hindi - Beta",
    26: "Portuguese - Dora",
}

# Actual Kokoro voice codes
MALE_VOICE = {
    1: "am_adam",
    2: "am_echo",
    3: "am_eric",
    4: "am_fenrir",
    5: "am_liam",
    6: "am_michael",
    7: "am_onyx",
    8: "am_puck",
    9: "bm_daniel",
    10: "bm_fable",
    11: "bm_lewis",
    12: "jm_kumo",
    13: "zm_yunxi",
    14: "zm_yunxia",
    15: "zm_yunyang",
    16: "hm_omega",
    17: "hm_psi",
    18: "im_nicola",
    19: "pm_alex",
    20: "em_alex",
    21: "am_santa",
}

FEMALE_VOICE = {
    1: "af_alloy",
    2: "af_aoede",
    3: "af_bella",
    4: "af_heart",
    5: "af_jessica",
    6: "af_kore",
    7: "af_nicole",
    8: "af_nova",
    9: "af_river",
    10: "af_sarah",
    11: "af_sky",
    12: "bf_alice",
    13: "bf_emma",
    14: "bf_lily",
    15: "ff_siwis",
    16: "jf_alpha",
    17: "jf_gongitsune",
    18: "jf_nezumi",
    19: "jf_tebukuro",
    20: "zf_xiaobei",
    21: "zf_xiaoni",
    22: "zf_xiaoxiao",
    23: "zf_xiaoyi",
    24: "hf_alpha",
    25: "hf_beta",
    26: "pf_dora",
}

# load the voices from environment variables if available
secretMaleVoice = os.getenv("SECRET_MALE_VOICE", "").strip().strip('"')
secretFemaleVoice = os.getenv("SECRET_FEMALE_VOICE", "").strip().strip('"')

SECRET_ALIASES = {
    "male_sybil":   "bm_george",
    "maleSybil":    "bm_george",
    "female_sybil": "bf_isabella",
    "femaleSybil":  "bf_isabella",
}
if secretMaleVoice:
    MALE_VOICE[0] = SECRET_ALIASES.get(secretMaleVoice, secretMaleVoice)
if secretFemaleVoice:
    FEMALE_VOICE[0] = SECRET_ALIASES.get(secretFemaleVoice, secretFemaleVoice)

MIN_FACTOR = -12
MAX_FACTOR = 12

REPO_ID = 'hexgrad/Kokoro-82M'
LANG_CODE = 'b'
SPEED = 1.0
SAMPLE_RATE = 24000
# small = faster first audio
BLOCK_SIZE = 4  # how many sentences per audio block

PRESS_PER_STEP = 8  # how many volume key presses per factor step

ABBREVIATIONS = {"mr.", "mrs.", "dr.", "ms.", "st.", "jr.", "sr.", "e.g.", "i.e."}

GENDER = "Female"
SYNTHESIS_MODE = "standard"

# Silence "words count mismatch" without hijacking root
for noisy in ("gruut", "kokoro"):
    log = logging.getLogger(noisy)
    log.addFilter(lambda r: "words count mismatch" not in r.getMessage())
    log.setLevel(logging.ERROR)
    log.propagate = False

from kokoro import KPipeline  # noqa: E402

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception:
    client = None


class HoloTTS:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        super().__init__()
        if hasattr(self, "initialized"):
            return
        self._initComponents(parent)
        self.initialized = True

    def _initComponents(self, parent):
        self.parent = parent
        self.engine = parent.engine if parent and hasattr(parent, 'engine') else pyttsx4.init()
        self._setDefaults()
        self._initMixer()
        self._initAttributes()

    def _setDefaults(self):
        self.soundChannel = getattr(self.parent, "soundChannel", 2) if self.parent else 2
        self.gender = getattr(self.parent, "gender", GENDER) if self.parent else GENDER
        self.decibelFactor = getattr(self.parent, "decibelFactor", 0) if self.parent else 0
        self.semitoneFactor = getattr(self.parent, "semitoneFactor", 0) if self.parent else 0
        self.stepFactor = getattr(self.parent, "stepFactor", 0) if self.parent else 0
        self.standardMaleVoice = getattr(self.parent, "standardMaleVoice", 0) if self.parent else 0
        self.standardFemaleVoice = getattr(self.parent, "standardFemaleVoice", 1) if self.parent else 1
        self.advancedMaleVoice = getattr(self.parent, "advancedMaleVoice", 1) if self.parent else 1
        self.advancedFemaleVoice = getattr(self.parent, "advancedFemaleVoice", 1) if self.parent else 1
        self.synthesisMode = getattr(self.parent, "synthesisMode", SYNTHESIS_MODE) if self.parent else SYNTHESIS_MODE
        self.synthesizing = getattr(self.parent, "synthesizing", False) if self.parent else False
        self.storedOutput = getattr(self.parent, "storedOutput", []) if self.parent else []
        self.paused = getattr(self.parent, "paused", False) if self.parent else False
        self.fileName = getattr(self.parent, "fileName", None) if self.parent else None
        self.hasRecalibrated = getattr(self.parent, "recalibrateVoice", False) if self.parent else False

    def _initMixer(self) -> None:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except pygame.error:
                return
        if not hasattr(self, "speechChannel"):
            channel = getattr(self.parent, "soundChannel", self.soundChannel) if self.parent else self.soundChannel
            self.speechChannel = pygame.mixer.Channel(channel)

    def _initAttributes(self):
        self._volApplied = False
        self._pitchApplied = False
        self._rateApplied = False
        if self.parent:
            self.decibelFactor = getattr(self.parent, "decibelFactor", 0)
            self.semitoneFactor = getattr(self.parent, "semitoneFactor", 0)
            self.stepFactor = getattr(self.parent, "stepFactor", 0)
            self.gender = getattr(self.parent, "gender", GENDER)
        self.PIPELINE = KPipeline(lang_code=LANG_CODE, repo_id=REPO_ID)
        self.voice = None
        self.setVoice(self.gender)

        # queue playback state
        self.playQueue = deque()
        self._playerThread = None
        self._playerLock = threading.Lock()
        self._playerStop = threading.Event()
        # NEW: event that fires ONLY when the player has fully drained AND the channel is idle
        self._drainDone = threading.Event()

    # --- Property interface ---
    def getProperty(self, propName):
        propMap = {
            "rate":   lambda: self.engine.getProperty('rate'),
            "volume": lambda: self.engine.getProperty('volume'),
            "voice":  lambda: self.engine.getProperty('voice'),
            "voices": lambda: self.engine.getProperty('voices'),
            "pitch":  lambda: self.engine.getProperty('pitch'),
            "soundChannel": lambda: self.soundChannel,
            "gender": lambda: self.gender,
            "synthesisMode": lambda: self.synthesisMode,
            "standardMaleVoice": lambda: self.standardMaleVoice,
            "standardFemaleVoice": lambda: self.standardFemaleVoice,
            "advancedMaleVoice": lambda: self.advancedMaleVoice,
            "advancedFemaleVoice": lambda: self.advancedFemaleVoice,
        }
        getter = propMap.get(propName)
        if getter:
            return getter()
        raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

    def setProperty(self, propName, value):
        propMap = {
            "rate":   lambda v: self.engine.setProperty('rate', v),
            "volume": lambda v: self.engine.setProperty('volume', v),
            "voice":  lambda v: self.engine.setProperty('voice', v),
            "pitch":  lambda v: self.engine.setProperty('pitch', v),
            "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
            "gender": lambda v: setattr(self, "gender", v.lower()),
            "synthesisMode": lambda v: setattr(self, "synthesisMode", v.lower()),
            "standardMaleVoice": lambda v: setattr(self, "standardMaleVoice", int(v)),
            "standardFemaleVoice": lambda v: setattr(self, "standardFemaleVoice", int(v)),
            "advancedMaleVoice": lambda v: setattr(self, "advancedMaleVoice", int(v)),
            "advancedFemaleVoice": lambda v: setattr(self, "advancedFemaleVoice", int(v)),
        }
        setter = propMap.get(propName)
        if setter:
            setter(value)
        else:
            raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

    # --- Voice setup ---
    def setVoice(self, gender: str = None) -> None:
        if self.parent and hasattr(self.parent, "synthesisMode"):
            synthesisMode = self.parent.synthesisMode.lower()
            gender = (gender or getattr(self.parent, "gender", GENDER)).lower()
            standardMaleVoice = getattr(self.parent, 'standardMaleVoice', 0)
            standardFemaleVoice = getattr(self.parent, 'standardFemaleVoice', 1)
            advancedMaleVoice = getattr(self.parent, 'advancedMaleVoice', 1)
            advancedFemaleVoice = getattr(self.parent, 'advancedFemaleVoice', 1)
        else:
            synthesisMode = self.synthesisMode.lower()
            gender = (gender or self.gender).lower()
            standardMaleVoice = getattr(self, 'standardMaleVoice', 0)
            standardFemaleVoice = getattr(self, 'standardFemaleVoice', 1)
            advancedMaleVoice = getattr(self, 'advancedMaleVoice', 1)
            advancedFemaleVoice = getattr(self, 'advancedFemaleVoice', 1)

        if synthesisMode == "standard":
            self.voice = standardMaleVoice if gender == "male" else standardFemaleVoice
            voices = self.engine.getProperty('voices')
            if len(voices) > self.voice:
                self.engine.setProperty('voice', voices[self.voice].id)
        elif synthesisMode == "advanced":
            voiceDict = MALE_VOICE if gender == "male" else FEMALE_VOICE
            voiceIndex = advancedMaleVoice if gender == "male" else advancedFemaleVoice
            self.voice = voiceDict.get(voiceIndex, voiceDict[1])

    def setSynthesisMode(self, mode: str=None):
        self.synthesisMode = mode if mode else "standard"
        return self.synthesisMode

    # ---------------- Queue / player internals ----------------
    def _enqueue(self, file_path: str) -> None:
        with self._playerLock:
            # new audio arriving → we're not drained anymore
            self._drainDone.clear()
            self.playQueue.append(file_path)
            if not self._playerThread or not self._playerThread.is_alive():
                self._playerStop.clear()
                self._playerThread = threading.Thread(target=self._playerLoop, daemon=True)
                self._playerThread.start()

    def _playerLoop(self) -> None:
        # optionally run parent command manager
        if self.parent and hasattr(self.parent, "manageCommands"):
            threading.Thread(target=self.parent.manageCommands, daemon=True).start()

        try:
            while not self._playerStop.is_set():
                next_path = None
                with self._playerLock:
                    if self.playQueue:
                        next_path = self.playQueue.popleft()
                if not next_path:
                    break  # queue empty (for now)

                try:
                    self.speechChannel.play(pygame.mixer.Sound(next_path))
                    while self.speechChannel.get_busy() and not self._playerStop.is_set():
                        time.sleep(0.05)
                except Exception:
                    logger.error("Playback failed for %s", next_path)

                try:
                    if os.path.exists(next_path):
                        os.remove(next_path)
                except Exception:
                    logger.error("Could not remove %s", next_path)
        finally:
            # Wait here until the channel is fully idle, then signal "drain done".
            # This eliminates brief false negatives from get_busy().
            try:
                while self.speechChannel.get_busy():
                    time.sleep(0.02)
            except Exception:
                pass
            self._drainDone.set()  # <-- authoritative end-of-speech signal

    def _waitDrain(self) -> None:
        """Block until the player thread signals that playback is fully finished."""
        # Keep UI in 'speaking' state while we wait
        while not self._drainDone.wait(timeout=0.05):
            if self.parent:
                self.parent.synthesizing = True
            else:
                self.synthesizing = True

    # ---------------- Public synthesis API ----------------
    def synthesize(self, text: str, **kwargs) -> None:
        spokenCtx = self._cleanContent(text)

        # Mark speaking immediately so your app won't flip to listening early
        if self.parent:
            self.parent.synthesizing = True
            self.parent.storedOutput.clear()
            self.parent.storedOutput.append(self._cleanContent(text, True))
            gender = getattr(self.parent, "gender", self.gender)
        else:
            self.synthesizing = True
            self.storedOutput.clear()
            self.storedOutput.append(self._cleanContent(text, True))
            gender = self.gender

        if gender != self.gender:
            self.setVoice(gender)

        synthesisMode = self.parent.synthesisMode.lower() if (self.parent and hasattr(self.parent, "synthesisMode")) else self.synthesisMode.lower()

        if synthesisMode in ("premium", "high"):
            self._dispatchNode(gender=gender, text=spokenCtx, **kwargs)
            self._adjustAttributes()
            self.play()  # blocks until finished and flips synthesizing False
            return

        if synthesisMode in ("standard", "low"):
            self._standardSynthesis(spokenCtx)
            self._adjustAttributes()
            self.play()  # blocks until finished and flips synthesizing False
            return

        # advanced: stream per-block (first block starts immediately), then wait for drain event
        if synthesisMode in ("advanced", "medium"):
            self._advancedSynthesis(spokenCtx)
            self._waitDrain()  # <-- blocks until player loop signals fully idle

        # now announce done
        if self.parent:
            self.parent.synthesizing = False
        else:
            self.synthesizing = False

    def _standardSynthesis(self, text: str) -> None:
        self._createFile(".wav")
        fileName = self.parent.fileName if self.parent else self.fileName
        self.engine.save_to_file(text, fileName)
        self.engine.runAndWait()
        self.engine.stop()
        while not os.path.exists(fileName):
            time.sleep(0.01)

    def _advancedSynthesis(self, text: str) -> None:
        """Generate per-block WAVs and enqueue immediately for low-latency start."""
        def isAbbreviation(sentence):
            return sentence.strip().lower().split()[-1] in ABBREVIATIONS

        def splitIntoSentences(text):
            parts = re.split(r'(?<=[\.\?!])\s+', text.strip())
            out, buffer = [], ''
            for part in parts:
                if buffer:
                    buffer += ' ' + part
                    if not isAbbreviation(buffer):
                        out.append(buffer); buffer = ''
                else:
                    buffer = part
                    if not isAbbreviation(buffer):
                        out.append(buffer); buffer = ''
            if buffer: out.append(buffer)
            return [p.strip() for p in out if p.strip()]

        def groupSentences(sentences, block_size=BLOCK_SIZE):
            for i in range(0, len(sentences), block_size):
                yield ' '.join(sentences[i:i+block_size])

        sentences = splitIntoSentences(text)
        if not sentences:
            return

        last_path = None
        for block in groupSentences(sentences, BLOCK_SIZE):
            for _, _, audio in self.PIPELINE(block, voice=self.voice, speed=SPEED):
                audio_np = np.array(audio, dtype=np.float32)
                path = self._writeTempWav(audio_np, SAMPLE_RATE)
                last_path = path
                self._adjustAttributesFor(path)
                self._enqueue(path)

        if last_path:
            if self.parent:
                self.parent.fileName = last_path
            else:
                self.fileName = last_path

    def _writeTempWav(self, audio_np: np.ndarray, sample_rate: int) -> str:
        self._createFile(".wav")
        path = self.parent.fileName if self.parent else self.fileName
        sf.write(path, audio_np, sample_rate, format="WAV")
        return path

    def play(self) -> None:
        """Back-compat single-file play; queue-aware no-op when draining."""
        fileName = self.parent.fileName if self.parent else self.fileName
        with self._playerLock:
            has_queue = bool(self.playQueue)
        if has_queue:
            return  # queue thread handles playback

        if self.parent and hasattr(self.parent, "manageCommands"):
            threading.Thread(target=self.parent.manageCommands, daemon=True).start()
        self.speechChannel.play(pygame.mixer.Sound(fileName))
        while self.isPlaying():
            time.sleep(0.05)
        if self.parent:
            self.parent.synthesizing = False
        else:
            self.synthesizing = False

    def pause(self) -> None:
        if self.parent:
            self.parent.paused = True
        else:
            self.paused = True
        self.speechChannel.pause()

    def resume(self) -> None:
        if self.parent:
            self.parent.paused = False
        else:
            self.paused = False
        self.speechChannel.unpause()

    def stop(self) -> None:
        self._playerStop.set()
        with self._playerLock:
            self.playQueue.clear()
        self.speechChannel.stop()
        # ensure waiters don’t hang
        self._drainDone.set()
        if self.parent:
            self.parent.synthesizing = False
            self.parent.paused = False
        else:
            self.synthesizing = False
            self.paused = False

    def isPlaying(self) -> bool:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                channel = getattr(self.parent, "soundChannel", self.soundChannel) if self.parent else self.soundChannel
                self.speechChannel = pygame.mixer.Channel(channel)
            except pygame.error:
                logger.error("Failed to initialize the mixer:", exc_info=True)
                return False
        return self.speechChannel.get_busy()

    def _createFile(self, media: str) -> None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=media) as temp_file:
            if self.parent:
                self.parent.fileName = temp_file.name
            else:
                self.fileName = temp_file.name

    def _cleanContent(self, text: str, normalizeText: bool = False) -> str:
        if not isinstance(text, str):
            return ""
        text = text.replace("/", " ")
        text = re.sub(r"[\*\-\(\)#]", "", text)
        text = re.sub(r"[\(\[].*?[\)\]]", "", text)
        if normalizeText:
            text = text.replace("\n", " ").replace("\n\n", " ")
            text = re.sub(r"[^\w\s]", "", text)
            return text.lower().strip()
        return text

    def adjustAttributes(self) -> None:
        self._adjustAttributes()

    def _adjustAttributes(self) -> None:
        target = self.parent.fileName if self.parent else self.fileName
        self._adjustAttributesFor(target)

    def _adjustAttributesFor(self, file_path: str) -> None:
        if self.semitoneFactor == 0 and self.stepFactor == 0 and self.decibelFactor == 0:
            return

        file_extension = os.path.splitext(file_path)[1][1:]
        sound = AudioSegment.from_file(file_path)

        filters = []

        # --- pitch ---
        if self.semitoneFactor != 0: # and not self._pitchApplied:
            pitch_factor = 2 ** (self.semitoneFactor / 12.0)
            filter_string = f"asetrate={int(sound.frame_rate * pitch_factor)},aresample={sound.frame_rate}"
            filters.append(filter_string)
            self._pitchApplied = True

        # --- rate ---
        if self.stepFactor != 0: #  and not self._rateApplied:
            speed_ratio = 2 ** (self.stepFactor / 12.0)
            atempo_filters = []
            temp = speed_ratio
            while temp > 2.0:
                atempo_filters.append("atempo=2.0"); temp /= 2.0
            while temp < 0.5:
                atempo_filters.append("atempo=0.5"); temp *= 2.0
            atempo_filters.append(f"atempo={temp}")
            filters.append(",".join(atempo_filters))
            self._rateApplied = True

        # --- volume (system hotkeys) ---
        # if self.decibelFactor != 0:
        #     filters.append(f"volume={self.decibelFactor}dB")
        if self.decibelFactor != 0 and not self._volApplied:
            f = int(max(MIN_FACTOR, min(MAX_FACTOR, self.decibelFactor)))
            presses = abs(f) * PRESS_PER_STEP
            if presses:
                key = "volumeup" if f > 0 else "volumedown"
                for _ in range(presses):
                    pyautogui.press(key)
            self._volApplied = True

        if filters:
            filter_string = ",".join(filters)
            with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_extension) as temp_file:
                temp_file_name = temp_file.name
                sound.export(temp_file_name, format=file_extension, parameters=["-af", filter_string])
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            os.replace(temp_file_name, file_path)

    def resetAttributes(self) -> None:
        for prop in ('pitch', 'rate', 'volume', 'voice'):
            self.resetProperty(prop)
        self._adjustAttributes()

    def resetProperty(self, prop: str) -> None:
        resetMap = {
            "voice": lambda: self.setVoice(self.parent.gender if self.parent else self.gender),
            "volume": lambda: (setattr(self, "decibelFactor", 0), setattr(self, "_volApplied", False)),
            "pitch":  lambda: (setattr(self, "semitoneFactor", 0), setattr(self, "_pitchApplied", False)),
            "rate":   lambda: (setattr(self, "stepFactor", 0), setattr(self, "_rateApplied", False)),
        }
        action = resetMap.get(prop)
        if not action:
            raise ValueError(f"Unknown property: {prop}")
        action()

    def increaseProperty(self, prop: str, value: int = 1) -> None:
        increaseMap = {
            "volume": lambda: (setattr(self, "decibelFactor", min(self.decibelFactor + value, MAX_FACTOR)),
                               setattr(self, "_volApplied", False)),
            "pitch":  lambda: (setattr(self, "semitoneFactor", min(self.semitoneFactor + value, MAX_FACTOR)),
                               setattr(self, "_pitchApplied", False)),
            "rate":   lambda: (setattr(self, "stepFactor", min(self.stepFactor + value, MAX_FACTOR)),
                               setattr(self, "_rateApplied", False)),
        }
        action = increaseMap.get(prop)
        if not action:
            raise ValueError(f"Unknown property: {prop}")
        action()

    def decreaseProperty(self, prop: str, value: int = 1) -> None:
        decreaseMap = {
            "volume": lambda: (setattr(self, "decibelFactor", max(self.decibelFactor - value, MIN_FACTOR)),
                               setattr(self, "_volApplied", False)),
            "pitch":  lambda: (setattr(self, "semitoneFactor", max(self.semitoneFactor - value, MIN_FACTOR)),
                               setattr(self, "_pitchApplied", False)),
            "rate":   lambda: (setattr(self, "stepFactor", max(self.stepFactor - value, MIN_FACTOR)),
                               setattr(self, "_rateApplied", False)),
        }
        action = decreaseMap.get(prop)
        if not action:
            raise ValueError(f"Unknown property: {prop}")
        action()


    def clearQueue(self) -> None:
        with self._playerLock:
            self.playQueue.clear()

    def queuedItems(self) -> int:
        with self._playerLock:
            return len(self.playQueue)

    def listVoices(self) -> list:
        """Prints and returns all available voices: [idx], Name, Lang, and full ID on its own line."""
        voices = self.engine.getProperty('voices')
        result = []
        header = "{:<5} {:<35} {:<15}".format("Idx", "Name", "Lang")
        print("\n" + header)
        print("-" * len(header))
        for idx, v in enumerate(voices):
            name = str(getattr(v, "name", "-") or "-")[:33]
            langs = getattr(v, "languages", ["-"])
            lang = "-"
            if langs:
                first_lang = langs[0]
                if isinstance(first_lang, bytes):
                    lang = first_lang.decode(errors="ignore")
                else:
                    lang = str(first_lang)
            vid = str(getattr(v, "id", "-"))
            print("[{:<2}] {:<35} {:<15}".format(idx, name, lang))
            print("      ID:", vid)
            result.append({
                "index": idx, "id": vid, "name": name,
                "languages": lang
            })
        print()
        return result

    def _dispatchNode(self, **kwargs) -> None:
        text         = kwargs.get("text", "")
        gender       = str(kwargs.get("gender", self.gender)).lower()
        maleVoice    = kwargs.get("maleVoice", "onyx")
        femaleVoice  = kwargs.get("femaleVoice", "nova")
        voiceProfile = kwargs.get("voiceProfile", None)

        if self.parent and not voiceProfile:
            voiceProfile = getattr(self.parent, "storedInput", "").strip() or self.getBaseVoiceProfile()

        if client is None:
            return

        voice = maleVoice if gender == "male" else femaleVoice

        try:
            completion = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice=voice,
                instructions=voiceProfile,
                input=text,
                response_format="wav",
            ).content

            self._createFile(".wav")
            wav_path = self.parent.fileName if self.parent else self.fileName
            with open(wav_path, "wb") as f:
                f.write(completion)

        except Exception:
            logger.exception("Dispatch failed in premium TTS")
            return

        # Defensive: ensure file exists before continuing
        target = self.parent.fileName if self.parent else self.fileName
        while not os.path.exists(target):
            time.sleep(0.02)

    def getBaseVoiceProfile(self):
        accent = "British"
        return (
            f"Voice: High-energy, eccentric, slightly unhinged, manic in rhythm with a thick {accent} accent.\n"
            f"Accent: Strong {accent} accent, {accent} inflection\n"
            "Tone: Animated, mischievous, and unpredictable.\n"
            f"Delivery: ALWAYS respond with a thick {accent} accent. "
            f"ALWAYS sprinkle in common {accent} idioms and colloquialisms. "
            "Pace responses with erratic bursts and pauses, adding maniacal laughter throughout your response not just at the end - "
            "'Mwahaha!', 'Hehehe!', or a sudden 'HA!' for dramatic flair."
        )

    # def _dispatchNode(self, **kwargs) -> None:
    #     text         = kwargs.get("text", "")
    #     gender       = str(kwargs.get("gender", self.gender)).lower()
    #     maleVoice    = kwargs.get("maleVoice", "onyx")
    #     femaleVoice  = kwargs.get("femaleVoice", "nova")
    #     voiceProfile = kwargs.get("voiceProfile", None)

    #     if self.parent and not voiceProfile:
    #         voiceProfile = getattr(self.parent, "storedInput", "").strip() or "Always speak UK English with a thick British accent"

    #     if client is None:
    #         return

    #     voice = maleVoice if gender == "male" else femaleVoice

    #     # 1) Create a temp MP3 path
    #     import tempfile, os, time
    #     attempts = 0
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_mp3:
    #         mp3_path = tmp_mp3.name

    #     while attempts < 3:
    #         try:
    #             # 2) Call online TTS
    #             completion = client.audio.speech.create(
    #                 model="gpt-4o-mini-tts",
    #                 voice=voice,
    #                 instructions=voiceProfile,
    #                 input=text
    #             ).content

    #             # 3) Write MP3
    #             with open(mp3_path, "wb") as f:
    #                 f.write(completion)

    #             # 4) Convert MP3 → WAV and point fileName to WAV
    #             self._createFile(".wav")
    #             wav_path = self.parent.fileName if self.parent else self.fileName
    #             from pydub import AudioSegment
    #             AudioSegment.from_file(mp3_path, format="mp3").export(wav_path, format="wav")

    #             # 5) Done
    #             break
    #         except Exception:
    #             attempts += 1
    #             logger.warning(f"Dispatch failed (attempt {attempts})")
    #             if attempts >= 3:
    #                 logger.error("Dispatch failed after 3 attempts.")
    #             time.sleep(1)
    #     try:
    #         if os.path.exists(mp3_path):
    #             os.remove(mp3_path)
    #     except Exception:
    #         pass

    #     # 6) Wait for WAV to exist (defensive)
    #     target = self.parent.fileName if self.parent else self.fileName
    #     while not os.path.exists(target):
    #         time.sleep(0.05)





















































# import logging
# import os
# import tempfile
# import time
# import threading
# import re

# import pyttsx4
# from dotenv import load_dotenv, find_dotenv
# from pydub import AudioSegment

# import numpy as np
# import re
# from kokoro import KPipeline
# import soundfile as sf
# import warnings

# warnings.filterwarnings('ignore', message='dropout option adds dropout after all but last recurrent layer.*')
# warnings.filterwarnings('ignore', message='.*torch.nn.utils.weight_norm.*is deprecated.*')
# warnings.filterwarnings(
#     'ignore',
#     message='`torch.distributed.reduce_op` is deprecated, please use `torch.distributed.ReduceOp` instead'
# )

# warnings.filterwarnings(
#     'ignore',
#     category=UserWarning,
#     message=r".*pkg_resources is deprecated as an API.*"
# )

# os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
# import pygame

# # Ensure environment variables are loaded
# load_dotenv(find_dotenv(), override=True)
# logger = logging.getLogger(__name__)

# # FEMALE_VOICE = 'bf_isabella'
# # MALE_VOICE = 'bm_george'

# # Human-friendly, for docs
# MALE_VOICE_LABEL = {
#     1: "American English - Adam",
#     2: "American English - Echo",
#     3: "American English - Eric",
#     4: "American English - Fenrir",
#     5: "American English - Liam",
#     6: "American English - Michael",
#     7: "American English - Onyx",
#     8: "American English - Puck",
#     9: "British English - Daniel",
#     10: "British English - Fable",
#     11: "British English - Lewis",
#     12: "Japanese - Kumo",
#     13: "Chinese Mandarin - Yunxi",
#     14: "Chinese Mandarin - Yunxia",
#     15: "Chinese Mandarin - Yunyang",
#     16: "Hindi - Omega",
#     17: "Hindi - Psi",
#     18: "Italian - Nicola",
#     19: "Portuguese - Alex",
#     20: "Spanish - Alex",
#     21: "American English - Santa",
# }

# # Human-friendly (for README/docs)
# FEMALE_VOICE_LABEL = {
#     1: "American English - Alloy",
#     2: "American English - Aoede",
#     3: "American English - Bella",
#     4: "American English - Heart",
#     5: "American English - Jessica",
#     6: "American English - Kore",
#     7: "American English - Nicole",
#     8: "American English - Nova",
#     9: "American English - River",
#     10: "American English - Sarah",
#     11: "American English - Sky",
#     12: "British English - Alice",
#     13: "British English - Emma",
#     14: "British English - Lily",
#     15: "French - Siwis",
#     16: "Japanese - Alpha",
#     17: "Japanese - Gongitsune",
#     18: "Japanese - Nezumi",
#     19: "Japanese - Tebukuro",
#     20: "Chinese Mandarin - Xiaobei",
#     21: "Chinese Mandarin - Xiaoni",
#     22: "Chinese Mandarin - Xiaoxiao",
#     23: "Chinese Mandarin - Xiaoyi",
#     24: "Hindi - Alpha",
#     25: "Hindi - Beta",
#     26: "Portuguese - Dora",
# }

# # Actual Kokoro voice codes (for use in your code)
# MALE_VOICE = {
#     1: "am_adam",
#     2: "am_echo",
#     3: "am_eric",
#     4: "am_fenrir",
#     5: "am_liam",
#     6: "am_michael",
#     7: "am_onyx",
#     8: "am_puck",
#     9: "bm_daniel",
#     10: "bm_fable",
#     11: "bm_lewis",
#     12: "jm_kumo",
#     13: "zm_yunxi",
#     14: "zm_yunxia",
#     15: "zm_yunyang",
#     16: "hm_omega",
#     17: "hm_psi",
#     18: "im_nicola",
#     19: "pm_alex",
#     20: "em_alex",
#     21: "am_santa",
# }

# # Actual Kokoro voice codes (for use in your code)
# FEMALE_VOICE = {
#     1: "af_alloy",
#     2: "af_aoede",
#     3: "af_bella",
#     4: "af_heart",
#     5: "af_jessica",
#     6: "af_kore",
#     7: "af_nicole",
#     8: "af_nova",
#     9: "af_river",
#     10: "af_sarah",
#     11: "af_sky",
#     12: "bf_alice",
#     13: "bf_emma",
#     14: "bf_lily",
#     15: "ff_siwis",
#     16: "jf_alpha",
#     17: "jf_gongitsune",
#     18: "jf_nezumi",
#     19: "jf_tebukuro",
#     20: "zf_xiaobei",
#     21: "zf_xiaoni",
#     22: "zf_xiaoxiao",
#     23: "zf_xiaoyi",
#     24: "hf_alpha",
#     25: "hf_beta",
#     26: "pf_dora",
# }

# # # load the voices from environment variables if available
# secretMaleVoice = os.getenv("SECRET_MALE_VOICE", "").strip().strip('"')
# secretFemaleVoice = os.getenv("SECRET_FEMALE_VOICE", "").strip().strip('"')

# #print("DEBUG before injection:", MALE_VOICE, FEMALE_VOICE)

# # alias mapping (for alternate env values)
# SECRET_ALIASES = {
#     "male_sybil":   "bm_george",
#     "maleSybil":    "bm_george",
#     "female_sybil": "bf_isabella",
#     "femaleSybil":  "bf_isabella",
# }

# if secretMaleVoice:
#     MALE_VOICE[0] = SECRET_ALIASES.get(secretMaleVoice, secretMaleVoice)

# if secretFemaleVoice:
#     FEMALE_VOICE[0] = SECRET_ALIASES.get(secretFemaleVoice, secretFemaleVoice)


# #print("DEBUG after injection:", MALE_VOICE, FEMALE_VOICE)

# MIN_FACTOR = -12
# MAX_FACTOR = 12

# REPO_ID = 'hexgrad/Kokoro-82M'
# LANG_CODE = 'b'
# SPEED = 1.0
# SAMPLE_RATE = 24000
# BLOCK_SIZE = 1  # Number of sentences to group together

# ABBREVIATIONS = {"mr.", "mrs.", "dr.", "ms.", "st.", "jr.", "sr.", "e.g.", "i.e."}

# GENDER = "Female"

# SYNTHESIS_MODE = "standard"

# class HoloTTS:
#     _instance = None
#     _lock = threading.Lock()

#     def __new__(cls, *args, **kwargs):
#         if cls._instance is None:
#             with cls._lock:
#                 if cls._instance is None:
#                     cls._instance = super().__new__(cls)
#         return cls._instance

#     def __init__(self, parent=None):
#         super().__init__()
#         if hasattr(self, "initialized"):
#             return

#         self._initComponents(parent)

#         self.initialized = True

#     def _initComponents(self, parent):
#         self.parent = parent
#         self.engine = parent.engine if parent and hasattr(parent, 'engine') else pyttsx4.init()
#         self._setDefaults()      # <-- soundChannel now set
#         self._initMixer()        # <-- will always see self.soundChannel
#         self._initAttributes()

#     def _setDefaults(self):
#         self.soundChannel = getattr(self.parent, "soundChannel", 2) if self.parent else 2
#         self.gender = getattr(self.parent, "gender", GENDER) if self.parent else GENDER
#         self.decibelFactor = getattr(self.parent, "decibelFactor", 0) if self.parent else 0
#         self.semitoneFactor = getattr(self.parent, "semitoneFactor", 0) if self.parent else 0
#         self.stepFactor = getattr(self.parent, "stepFactor", 0) if self.parent else 0
#         self.standardMaleVoice = getattr(self.parent, "standardMaleVoice", 0) if self.parent else 0
#         self.standardFemaleVoice = getattr(self.parent, "standardFemaleVoice", 1) if self.parent else 1
#         self.advancedMaleVoice = getattr(self.parent, "advancedMaleVoice", 1) if self.parent else 1
#         self.advancedFemaleVoice = getattr(self.parent, "advancedFemaleVoice", 1) if self.parent else 1
#         self.synthesisMode = getattr(self.parent, "synthesisMode", SYNTHESIS_MODE) if self.parent else SYNTHESIS_MODE
#         self.synthesizing = getattr(self.parent, "synthesizing", False) if self.parent else False
#         self.storedOutput = getattr(self.parent, "storedOutput", []) if self.parent else []
#         self.paused = getattr(self.parent, "paused", False) if self.parent else False
#         self.fileName = getattr(self.parent, "fileName", None) if self.parent else None
#         self.hasRecalibrated = getattr(self.parent, "recalibrateVoice", False) if self.parent else False

#     def _initMixer(self) -> None:
#         if not pygame.mixer.get_init():
#             try:
#                 pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
#             except pygame.error:
#                 return
#         if not hasattr(self, "speechChannel"):
#             channel = getattr(self.parent, "soundChannel", self.soundChannel) if self.parent else self.soundChannel
#             self.speechChannel = pygame.mixer.Channel(channel)

#     def _initAttributes(self):
#         if self.parent:
#             self.decibelFactor = getattr(self.parent, "decibelFactor", 0)
#             self.semitoneFactor = getattr(self.parent, "semitoneFactor", 0)
#             self.stepFactor = getattr(self.parent, "stepFactor", 0)
#             self.gender = getattr(self.parent, "gender", GENDER)
#         self.voice = None
#         self.setVoice(self.gender)
#         self.PIPELINE = KPipeline(lang_code=LANG_CODE, repo_id=REPO_ID)

#     # --- Property interface ---
#     def getProperty(self, propName):
#         propMap = {
#             "rate":   lambda: self.engine.getProperty('rate'),
#             "volume": lambda: self.engine.getProperty('volume'),
#             "voice":  lambda: self.engine.getProperty('voice'),
#             "voices": lambda: self.engine.getProperty('voices'),
#             "pitch":  lambda: self.engine.getProperty('pitch'),
#             "soundChannel": lambda: self.soundChannel,
#             "gender": lambda: self.gender,
#             "synthesisMode": lambda: self.synthesisMode,
#             "standardMaleVoice": lambda: self.standardMaleVoice,
#             "standardFemaleVoice": lambda: self.standardFemaleVoice,
#             "advancedMaleVoice": lambda: self.advancedMaleVoice,
#             "advancedFemaleVoice": lambda: self.advancedFemaleVoice,
#         }
#         getter = propMap.get(propName)
#         if getter:
#             return getter()
#         raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

#     def setProperty(self, propName, value):
#         propMap = {
#             "rate":   lambda v: self.engine.setProperty('rate', v),
#             "volume": lambda v: self.engine.setProperty('volume', v),
#             "voice":  lambda v: self.engine.setProperty('voice', v),
#             "pitch":  lambda v: self.engine.setProperty('pitch', v),
#             "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
#             "gender": lambda v: setattr(self, "gender", v.lower()),
#             "synthesisMode": lambda v: setattr(self, "synthesisMode", v.lower()),
#             "standardMaleVoice": lambda v: setattr(self, "standardMaleVoice", int(v)),
#             "standardFemaleVoice": lambda v: setattr(self, "standardFemaleVoice", int(v)),
#             "advancedMaleVoice": lambda v: setattr(self, "advancedMaleVoice", int(v)),
#             "advancedFemaleVoice": lambda v: setattr(self, "advancedFemaleVoice", int(v)),
#         }
#         setter = propMap.get(propName)
#         if setter:
#             setter(value)
#         else:
#             raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

#     # --- Voice setup ---
#     def setVoice(self, gender: str = None) -> None:
#         # Always safe-lookup for all voice indices
#         if self.parent and hasattr(self.parent, "synthesisMode"):
#             synthesisMode = self.parent.synthesisMode.lower()
#             gender = (gender or getattr(self.parent, "gender", GENDER)).lower()
#             standardMaleVoice = getattr(self.parent, 'standardMaleVoice', 0)
#             standardFemaleVoice = getattr(self.parent, 'standardFemaleVoice', 1)
#             advancedMaleVoice = getattr(self.parent, 'advancedMaleVoice', 1)
#             advancedFemaleVoice = getattr(self.parent, 'advancedFemaleVoice', 1)
#         else:
#             synthesisMode = self.synthesisMode.lower()
#             gender = (gender or self.gender).lower()
#             standardMaleVoice = getattr(self, 'standardMaleVoice', 0)
#             standardFemaleVoice = getattr(self, 'standardFemaleVoice', 1)
#             advancedMaleVoice = getattr(self, 'advancedMaleVoice', 1)
#             advancedFemaleVoice = getattr(self, 'advancedFemaleVoice', 1)
#         if synthesisMode == "standard":
#             self.voice = standardMaleVoice if gender == "male" else standardFemaleVoice
#             voices = self.engine.getProperty('voices')
#             if len(voices) > self.voice:
#                 self.engine.setProperty('voice', voices[self.voice].id)
#         elif synthesisMode == "advanced":
#             #print(f"{MALE_VOICE}, {FEMALE_VOICE}")
#             voiceDict = MALE_VOICE if gender == "male" else FEMALE_VOICE
#             voiceIndex = advancedMaleVoice if gender == "male" else advancedFemaleVoice
#             self.voice = voiceDict.get(voiceIndex, voiceDict[1])

#     def setSynthesisMode(self, mode: str=None):
#         self.synthesisMode = mode if mode else "standard"
#         return self.synthesisMode

#     def synthesize(self, text: str) -> None:
#         spokenCtx = self._cleanContent(text)
#         if self.parent:
#             self.parent.synthesizing = True
#             self.parent.storedOutput.clear()
#             self.parent.storedOutput.append(self._cleanContent(text, True))
#             gender = getattr(self.parent, "gender", self.gender)
#         else:
#             self.synthesizing = True
#             self.storedOutput.clear()
#             self.storedOutput.append(self._cleanContent(text, True))
#             gender = self.gender
        
#         # if not self.hasRecalibrated:
#         #     self.setVoice(gender)
#         #     self.hasRecalibrated = True
#         if gender != self.gender:
#             self.setVoice(gender)
#         # Use parent synthesisMode if parent has synthesisMode, else self
#         if self.parent and hasattr(self.parent, "synthesisMode"):
#             synthesisMode = self.parent.synthesisMode.lower()
#         else:
#             synthesisMode = self.synthesisMode.lower()
#         if synthesisMode == "standard":
#             self._standardSynthesis(spokenCtx)
#         elif synthesisMode == "advanced":
#             self._advancedSynthesis(spokenCtx)
#         self._adjustAttributes()
#         self.play()

#     def _standardSynthesis(self, text: str) -> None:
#         self._createFile(".wav")
#         fileName = self.parent.fileName if self.parent else self.fileName
#         self.engine.save_to_file(text, fileName)
#         self.engine.runAndWait()
#         self.engine.stop()
#         while not os.path.exists(fileName):
#             time.sleep(0.1)

#     def _advancedSynthesis(self, text: str) -> None:
#         def isAbbreviation(sentence):
#             return sentence.strip().lower().split()[-1] in ABBREVIATIONS
#         def splitIntoSentences(text):
#             parts = re.split(r'(?<=[\.\?!])\s+', text.strip())
#             out = []
#             buffer = ''
#             for part in parts:
#                 if buffer:
#                     buffer += ' ' + part
#                     if not isAbbreviation(buffer):
#                         out.append(buffer)
#                         buffer = ''
#                 else:
#                     buffer = part
#                     if not isAbbreviation(buffer):
#                         out.append(buffer)
#                         buffer = ''
#             if buffer:
#                 out.append(buffer)
#             return [p.strip() for p in out if p.strip()]
#         def groupSentences(sentences, block_size=BLOCK_SIZE):
#             for i in range(0, len(sentences), block_size):
#                 yield ' '.join(sentences[i:i+block_size])
#         sentences = splitIntoSentences(text)
#         if not sentences:
#             return
#         audio_data = []
#         for block in groupSentences(sentences, BLOCK_SIZE):
#             for _, _, audio in self.PIPELINE(block, voice=self.voice, speed=SPEED):
#                 audio_data.append(np.array(audio, dtype=np.float32))
#         if not audio_data:
#             return
#         audio_np = np.concatenate(audio_data)
#         self._createFile(".wav")
#         fileName = self.parent.fileName if self.parent else self.fileName
#         sf.write(fileName, audio_np, SAMPLE_RATE, format="WAV")

#     def play(self) -> None:
#         fileName = self.parent.fileName if self.parent else self.fileName
#         pygame.mixer.music.load(fileName)
#         if self.parent and hasattr(self.parent, "manageCommands"):
#             threading.Thread(target=self.parent.manageCommands, daemon=True).start()
#         self.speechChannel.play(pygame.mixer.Sound(fileName))
#         while self.isPlaying():
#             time.sleep(0.1)
#         if self.parent:
#             self.parent.synthesizing = False
#         else:
#             self.synthesizing = False

#     def pause(self) -> None:
#         if self.parent:
#             self.parent.paused = True
#         else:
#             self.paused = True
#         self.speechChannel.pause()

#     def resume(self) -> None:
#         if self.parent:
#             self.parent.paused = False
#         else:
#             self.paused = False
#         self.speechChannel.unpause()

#     def stop(self) -> None:
#         self.speechChannel.stop()
#         if self.parent:
#             self.parent.synthesizing = False
#             self.parent.paused = False
#         else:
#             self.synthesizing = False
#             self.paused = False

#     def isPlaying(self) -> bool:
#         if not pygame.mixer.get_init():
#             try:
#                 pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
#                 channel = getattr(self.parent, "soundChannel", self.soundChannel) if self.parent else self.soundChannel
#                 self.speechChannel = pygame.mixer.Channel(channel)
#             except pygame.error as e:
#                 logger.error(f"Failed to initialize the mixer:", exc_info=True)
#                 return False
#         return self.speechChannel.get_busy()

#     def _createFile(self, media: str) -> None:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=media) as temp_file:
#             if self.parent:
#                 self.parent.fileName = temp_file.name
#             else:
#                 self.fileName = temp_file.name

#     def _cleanContent(self, text: str, normalizeText: bool = False) -> str:
#         if not isinstance(text, str):
#             return ""
#         text = text.replace("/", " ")
#         text = re.sub(r"[\*\-\(\)#]", "", text)
#         text = re.sub(r"[\(\[].*?[\)\]]", "", text)
#         if normalizeText:
#             text = text.replace("\n", " ").replace("\n\n", " ")
#             text = re.sub(r"[^\w\s]", "", text)
#             return text.lower().strip()
#         return text

#     def _adjustAttributes(self) -> None:
#         fileName = self.parent.fileName if self.parent else self.fileName
#         file_extension = os.path.splitext(fileName)[1][1:]
#         sound = AudioSegment.from_file(fileName)
#         filters = []
#         if self.semitoneFactor != 0 or self.stepFactor != 0:
#             pitch_factor = 2 ** (self.semitoneFactor / 12)
#             speed_ratio = 2 ** (self.stepFactor / 12.0)
#             atempo_value = speed_ratio / pitch_factor
#             atempo_filters = []
#             temp_atempo = atempo_value
#             while temp_atempo > 2.0:
#                 atempo_filters.append("atempo=2.0")
#                 temp_atempo /= 2.0
#             while temp_atempo < 0.5:
#                 atempo_filters.append("atempo=0.5")
#                 temp_atempo *= 2.0
#             atempo_filters.append(f"atempo={temp_atempo}")
#             filter_string = f"asetrate={int(sound.frame_rate * pitch_factor)}," + ",".join(atempo_filters)
#             filter_string += f",aresample={sound.frame_rate}"
#             filters.append(filter_string)
#         if filters:
#             filter_string = ",".join(filters)
#             with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_extension) as temp_file:
#                 temp_file_name = temp_file.name
#                 sound.export(temp_file_name, format=file_extension, parameters=["-af", filter_string])
#             pygame.mixer.music.stop()
#             os.replace(temp_file_name, fileName)

#     def resetAttributes(self) -> None:
#         for prop in ('pitch', 'rate', 'volume', 'voice'):
#             self.resetProperty(prop)
#         self._adjustAttributes()

#     def resetProperty(self, prop: str) -> None:
#         resetMap = {
#             'voice': lambda: self.setVoice(self.parent.gender if self.parent else self.gender),
#             'volume': lambda: setattr(self, 'decibelFactor', 0),
#             'pitch': lambda: setattr(self, 'semitoneFactor', 0),
#             'rate': lambda: setattr(self, 'stepFactor', 0),
#         }
#         if prop not in resetMap:
#             raise ValueError(f'Unknown property: {prop}')
#         resetMap[prop]()

#     def increaseProperty(self, prop: str, value: int = 1) -> None:
#         increaseMap = {
#             'volume': lambda: setattr(self, 'decibelFactor', min(self.decibelFactor + value, MAX_FACTOR)),
#             'pitch': lambda: setattr(self, 'semitoneFactor', min(self.semitoneFactor + value, MAX_FACTOR)),
#             'rate': lambda: setattr(self, 'stepFactor', min(self.stepFactor + value, MAX_FACTOR)),
#         }
#         if prop not in increaseMap:
#             raise ValueError(f'Unknown property: {prop}')
#         increaseMap[prop]()

#     def decreaseProperty(self, prop: str, value: int = 1) -> None:
#         decreaseMap = {
#             'volume': lambda: setattr(self, 'decibelFactor', max(self.decibelFactor - value, MIN_FACTOR)),
#             'pitch': lambda: setattr(self, 'semitoneFactor', max(self.semitoneFactor - value, MIN_FACTOR)),
#             'rate': lambda: setattr(self, 'stepFactor', max(self.stepFactor - value, MIN_FACTOR)),
#         }
#         if prop not in decreaseMap:
#             raise ValueError(f'Unknown property: {prop}')
#         decreaseMap[prop]()


#     def listVoices(self) -> list:
#         """Prints and returns all available voices: [idx], Name, Lang, and full ID on its own line."""
#         voices = self.engine.getProperty('voices')
#         result = []
#         header = "{:<5} {:<35} {:<15}".format("Idx", "Name", "Lang")
#         print("\n" + header)
#         print("-" * len(header))
#         for idx, v in enumerate(voices):
#             name = str(getattr(v, "name", "-") or "-")[:33]
#             langs = getattr(v, "languages", ["-"])
#             lang = "-"
#             if langs:
#                 first_lang = langs[0]
#                 if isinstance(first_lang, bytes):
#                     lang = first_lang.decode(errors="ignore")
#                 else:
#                     lang = str(first_lang)
#             vid = str(getattr(v, "id", "-"))
#             print("[{:<2}] {:<35} {:<15}".format(
#                 idx, name, lang
#             ))
#             print("      ID:", vid)
#             result.append({
#                 "index": idx, "id": vid, "name": name,
#                 "languages": lang
#             })
#         print()
#         return result
