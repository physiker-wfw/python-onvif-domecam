#!/usr/bin/python
#-*-coding=utf-8

# pip install onvif_zeep

import zeep
from onvif import ONVIFCamera, ONVIFService, ONVIFError

def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue

zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue


class MegapixelDomeCamera:
    def __init__(self, host, port = 8999, user = "Admin", password = "admin"):
        self.__camera = ONVIFCamera(host, port, user, password, "wsdl/")
        self.__mediaService = self.__camera.create_media_service()
        self.__ptzService = self.__camera.create_ptz_service()
        self.__mediaProfileToken = self.__mediaService.GetProfiles()[0].token
        self.__ptzNodeToken = self.__ptzService.GetNodes()[0].token
        self.__ptzConfigToken = self.__ptzService.GetConfigurations()[0].token

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

    # def pztInfo(self):
    #     return self.__ptzService.GetServiceCapabilities() # Delivers only 'None'

    def getNode(self):
        '''Get a specific PTZ Node identified by a reference
        token or a name.'''
        return self.__ptzService.GetNode(self.__ptzNodeToken)   # 'PTZNODE_CH0'

    def getConfiguration(self):
        ''' The default Position/Translation/Velocity Spaces are introduced to allow NVCs sending move
            requests without the need to specify a certain coordinate system. The default Speeds are
            introduced to control the speed of move requests (absolute, relative, preset), where no
            explicit speed has been set.
            
            The allowed pan and tilt range for Pan/Tilt Limits is defined by a two-dimensional space range
            that is mapped to a specific Absolute Pan/Tilt Position Space. At least one Pan/Tilt Position
            Space is required by the PTZNode to support Pan/Tilt limits. The limits apply to all supported
            absolute, relative and continuous Pan/Tilt movements. The limits shall be checked within the
            coordinate system for which the limits have been specified. That means that even if
            movements are specified in a different coordinate system, the requested movements shall be
            transformed to the coordinate system of the limits where the limits can be checked. When a
            relative or continuous movements is specified, which would leave the specified limits, the PTZ
            unit has to move along the specified limits. The Zoom Limits have to be interpreted
            accordingly.'''
        return self.__ptzService.GetConfiguration(self.__ptzConfigToken)

    def xtest(self):
        '''Only for testing new functionality'''
        return self.__ptzService.GetConfiguration(self.__ptzConfigToken)


