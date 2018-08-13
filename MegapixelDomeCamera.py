#!/usr/bin/python
#-*-coding=utf-8

# pip install onvif_zeep

import os
import zeep
from onvif import ONVIFCamera, ONVIFService, ONVIFError
import time
from enum import Enum

# Correction of library 'zeep' for Phyton 3.6: ##################################
def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue
zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
# ##############################################################################

class Pan(Enum):
    RIGHT = 1
    LEFT = -1
    STOP = 0

class Tilt(Enum):
    UP = 1
    DOWN = -1
    STOP = 0

class Zoom(Enum):
    IN = 1
    OUT = -1
    STOP = 0

class MegapixelDomeCamera:
    def __init__(self, host, port = 8999, user = "admin", password = "admin"):
        currentModulPath = os.path.dirname(__file__)
        self.__camera = ONVIFCamera(host, port, user, password, currentModulPath+"/wsdl/")
        self.__mediaService = self.__camera.create_media_service()
        self.__ptzService = self.__camera.create_ptz_service()
        self.__mediaProfileToken = self.__mediaService.GetProfiles()[0].token
        self.__ptzNodeToken = self.__ptzService.GetNodes()[0].token
        self.__ptzConfigToken = self.__ptzService.GetConfigurations()[0].token
        self.__configureConfigurationOptions()

    def getSnapshot(self):
        response = self.__mediaService.GetSnapshotUri(self.__mediaProfileToken)
        return response.Uri

    def getRotationStatus(self):
        return self.__ptzService.GetStatus(self.__mediaProfileToken)

    # def move(self):
    #     vector = 10
    #     speed = 5
    #     return self.__ptzService.RelativeMove(self.__mediaProfileToken, vector)

    def getPositionPresets(self):
        return self.__ptzService.GetPresets(self.__mediaProfileToken)

    def moveToPositionPreset(self, presetToken):
        p = self.__ptzService.create_type("GotoPreset")
        p.ProfileToken = self.__mediaProfileToken
        p.PresetToken = presetToken

        self.__ptzService.GotoPreset(p)

    def pztInfo(self):
        return self.__ptzService.GetServiceCapabilities() # Delivers only 'None'

    def getNode(self):
        '''Get a specific PTZ Node identified by a reference
        token or a name.'''
        return self.__ptzService.GetNode(self.__ptzNodeToken)   # 'PTZNODE_CH0'

    def getConfiguration(self):
        ''' The default Position/Translation/Velocity Spaces are introduced to allow NVCs sending move
            params without the need to specify a certain coordinate system. The default Speeds are
            introduced to control the speed of move params (absolute, relative, preset), where no
            explicit speed has been set.

            The allowed pan and tilt range for Pan/Tilt Limits is defined by a two-dimensional space range
            that is mapped to a specific Absolute Pan/Tilt Position Space. At least one Pan/Tilt Position
            Space is required by the PTZNode to support Pan/Tilt limits. The limits apply to all supported
            absolute, relative and continuous Pan/Tilt movements. The limits shall be checked within the
            coordinate system for which the limits have been specified. That means that even if
            movements are specified in a different coordinate system, the paramed movements shall be
            transformed to the coordinate system of the limits where the limits can be checked. When a
            relative or continuous movements is specified, which would leave the specified limits, the PTZ
            unit has to move along the specified limits. The Zoom Limits have to be interpreted
            accordingly.'''
        return self.__ptzService.GetConfiguration(self.__ptzConfigToken)

    def __configureConfigurationOptions(self):
        ''' List supported coordinate systems including their range limitations. Therefore, the options
            MAY differ depending on whether the PTZ Configuration is assigned to a Profile containing a
            Video Source Configuration. In that case, the options may additionally contain coordinate
            systems referring to the image coordinate system described by the Video Source
            Configuration. If the PTZ Node supports continuous movements, it shall return a Timeout Range within
            which Timeouts are accepted by the PTZ Node.'''
        opt = self.__ptzService.GetConfigurationOptions(self.__ptzConfigToken)
        self.__panTiltVelocityRange = opt.Spaces.ContinuousPanTiltVelocitySpace[0]


    def relativeMove(self, pan=Pan.STOP, tilt=Tilt.STOP, zoom=Zoom.STOP, duration=2):
        ''' Operation for Relative Pan/Tilt and Zoom Move. The operation is supported if the PTZNode supports at least one relative Pan/Tilt or Zoom space.<br/> 
            The speed argument is optional. If an x/y speed value is given it is up to the device to either use 
            the x value as absolute resoluting speed vector or to map x and y to the component speed. 
            If the speed argument is omitted, the default speed set by the PTZConfiguration will be used.'''
        pan = Pan(pan).value
        tilt = Tilt(tilt).value
        zoom = Zoom(zoom).value
        param = self.__ptzService.create_type('ContinuousMove')
        param.ProfileToken =  self.__mediaProfileToken       
        param.Velocity = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': {'x': zoom}}
        message = self.__ptzService.ContinuousMove(param)
        if duration > 0:        # For negative durations, the movement continues for ever
            time.sleep(duration)
            self.__ptzService.Stop({'ProfileToken': self.__mediaProfileToken})
        return message
            

    def absoluteMove(self, pan, tilt, speed, zoom=1):
        ''' Operation to move pan,tilt or zoom to a absolute destination.

            The speed argument is optional. If an x/y speed value is given it is up to the device to either use 
            the x value as absolute resoluting speed vector or to map x and y to the component speed. 
            If the speed argument is omitted, the default speed set by the PTZConfiguration will be used.'''
        param = self.__ptzService.create_type('AbsoluteMove')
        param.ProfileToken =  self.__mediaProfileToken       
        param.Position = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': {'x': zoom}}
        param.Speed = {'PanTilt': {'x': speed, 'y': speed, 'space': 'http://www.onvif.org/ver10/tptz/PanTiltSpaces/VelocityGenericSpace'}, 'Zoom': {'x': 1.}}
        return self.__ptzService.AbsoluteMove(param)
            


    def xtest(self):
        '''Only for testing new functionality'''
        pass

    def showLiveVideo(self):
        ''' Show live video for testing. Press 'q' to stop. 
        If not working, check the last part of the rtsp address via ONVIF Device Manager.'''
        import cv2 as cv2
        cap = cv2.VideoCapture('rtsp://'+config.host+':554/1/h264major')
        while(True):
            # Capture frame-by-frame
            ret, frame = cap.read()
            # height, width = frame.shape[:2]
            # height, width = (480, 640)
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            cv2.imshow('Live Video',frame)
            if cv2.waitKey(20) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()        



if __name__ == '__main__':
    import config
    camera = MegapixelDomeCamera(config.host, config.port, config.user, config.password)
    # a = camera.getConfiguration()
    # print(a)
    # print(camera.relativeMove(pan=Pan.RIGHT, duration=4.2))
    camera.showLiveVideo()
    print(camera.relativeMove(tilt=Tilt.DOWN, duration=4.2))
    camera.showLiveVideo()

    time.sleep(5)
    # print(camera.absoluteMove(pan=0.6, tilt=0.7, speed=0.9))
    # print('Position presets:\n\n',camera.getPositionPresets()[:5])
    # camera.moveToPositionPreset(3)
    # time.sleep(5)
    # camera.moveToPositionPreset(1)

