import time

class string:
    def __init__(self, code_text: str):
        self.code_text = code_text
        self._compiled = compile(code_text, "<sucode>", "exec")
        self.parent = None  # sucode сілтемесі қойылады

    def run(self):
        gl = {
            "SPEEDUPPER_FPS_LIMIT": self.parent.limit if self.parent else 60,
            "_speedupper_tick": self.parent._tick if self.parent else (lambda: None),
        }
        exec(self._compiled, gl)

class sucode:
    def __init__(self, limit=60):
        self.limit = limit
        self._frame_time = 1.0 / limit
        self._last = time.perf_counter()
        self.SUC = None

    def __setattr__(self, name, value):
        if name == "SUC" and isinstance(value, string):
            object.__setattr__(self, name, value)
            value.parent = self
        else:
            object.__setattr__(self, name, value)

    def _tick(self):
        """Әр итерация соңында шақырылады.
        FPS ешқашан limit-тен төмендемейді (ұйықтап отырып теңестіріледі)."""
        now = time.perf_counter()
        elapsed = now - self._last
        if elapsed < self._frame_time:
            time.sleep(self._frame_time - elapsed)
        self._last = time.perf_counter()