import time
from MegapixelDomeCamera import MegapixelDomeCamera

import config

camera = MegapixelDomeCamera(host, port, user, password)
print(camera.getRotationStatus())

print(camera.pztInfo())

