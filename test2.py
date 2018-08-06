import time
from MegapixelDomeCamera import MegapixelDomeCamera

import config

camera = MegapixelDomeCamera(config.host, config.port, config.user, config.password)
print(camera.getRotationStatus())

# print("getPositionPresets:",camera.getPositionPresets())
#print("GetNode:",camera.getNode())
print("\n\n\ngetConfigurationOptions:",camera.getConfigurationOptions())
