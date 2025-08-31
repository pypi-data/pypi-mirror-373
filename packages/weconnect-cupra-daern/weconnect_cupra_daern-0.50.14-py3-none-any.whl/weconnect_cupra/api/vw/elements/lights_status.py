from enum import Enum
import logging

from weconnect_cupra.addressable import AddressableAttribute, AddressableObject, AddressableDict
from weconnect_cupra.elements.generic_status import GenericStatus

LOG = logging.getLogger("weconnect_cupra")


class LightsStatus(GenericStatus):
    def __init__(
        self,
        vehicle,
        parent,
        statusId,
        fromDict=None,
        fixAPI=True,
    ):
        self.lights = AddressableDict(localAddress='lights', parent=self)
        super().__init__(vehicle=vehicle, parent=parent, statusId=statusId, fromDict=fromDict, fixAPI=fixAPI)

    def update(self, fromDict, ignoreAttributes=None):
        ignoreAttributes = ignoreAttributes or []
        LOG.debug('Update light status from dict')

        if 'value' in fromDict:
            if 'lights' in fromDict['value'] and fromDict['value']['lights'] is not None:
                for lightDict in fromDict['value']['lights']:
                    if 'name' in lightDict:
                        if lightDict['name'] in self.lights:
                            self.lights[lightDict['name']].update(fromDict=lightDict)
                        else:
                            self.lights[lightDict['name']] = LightsStatus.Light(fromDict=lightDict, parent=self.lights)
                for lightName in [lightName for lightName in self.lights.keys()
                                  if lightName not in [light['name'] for light in fromDict['value']['lights'] if 'name' in light]]:
                    del self.lights[lightName]
            else:
                self.lights.clear()
                self.lights.enabled = False
        else:
            self.lights.clear()
            self.lights.enabled = False

        super().update(fromDict=fromDict, ignoreAttributes=(ignoreAttributes + ['lights']))

    def __str__(self):
        string = super().__str__()
        if len(self.lights) > 0:
            string += f'\n\tLights: {len(self.lights)} items'
            for light in self.lights.values():
                string += f'\n\t\t{light}'
        return string

    class Light(AddressableObject):
        def __init__(
            self,
            parent,
            fromDict=None,
        ):
            super().__init__(localAddress=None, parent=parent)
            self.status = AddressableAttribute(localAddress='status', parent=self,
                                               value=None, valueType=LightsStatus.Light.LightState)
            if fromDict is not None:
                self.update(fromDict)

        def update(self, fromDict):
            LOG.debug('Update light from dict')

            if 'name' in fromDict:
                self.id = fromDict['name']
                self.localAddress = self.id
            else:
                LOG.error('Light is missing name attribute')

            self.status.fromDict(fromDict, 'status')

            for key, value in {key: value for key, value in fromDict.items() if key not in ['name', 'status']}.items():
                LOG.warning('%s: Unknown attribute %s with value %s', self.getGlobalAddress(), key, value)

        def __str__(self):
            return f'{self.id}: {self.status.value.value}'  # pylint: disable=no-member

        class LightState(Enum,):
            ON = 'on'
            OFF = 'off'
            UNKNOWN = 'unknown open state'
