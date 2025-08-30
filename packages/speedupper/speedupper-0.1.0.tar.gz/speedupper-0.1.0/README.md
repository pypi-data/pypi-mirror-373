# speedupper

Қарапайым FPS booster кітапхана.  

Мысалы:

```python
from speedupper import sucode, string

code = sucode(limit=61)
code.SUC = string("""
import time
for i in range(5):
    print("Frame", i)
    _speedupper_tick()
""")
code.SUC.run()