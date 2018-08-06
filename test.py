import time
from MegapixelDomeCamera import MegapixelDomeCamera
import config

camera = MegapixelDomeCamera(config.host, config.port, config.user, config.password)
# print(camera.getRotationStatus())

# while True:
#     camera.moveToPositionPreset("1")
#     time.sleep(3)
#     camera.moveToPositionPreset("2")
#     time.sleep(3)
#     camera.moveToPositionPreset("3")
#     time.sleep(12) 

a = camera.xtest()
print(type(a), a)
