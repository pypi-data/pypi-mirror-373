import logging

from weconnect_cupra.addressable import AddressableAttribute
from weconnect_cupra.elements.generic_status import GenericStatus

LOG = logging.getLogger("weconnect_cupra")


class BatteryStatus(GenericStatus):
    def __init__(
        self,
        vehicle,
        parent,
        statusId,
        fromDict=None,
        fixAPI=True,
    ):
        # TODO get from engines.primary.level (as float)
        self.currentSOC_pct = AddressableAttribute(
            localAddress='currentSOC_pct', parent=self, value=None, valueType=int)
        # TODO get from engines.primary.range.value (as float)
        self.cruisingRangeElectric_km = AddressableAttribute(
            localAddress='cruisingRangeElectric_km', value=None, parent=self, valueType=int)

        super().__init__(vehicle=vehicle, parent=parent, statusId=statusId, fromDict=fromDict, fixAPI=fixAPI)

    def update(self, fromDict, ignoreAttributes=None):
        ignoreAttributes = ignoreAttributes or []
        LOG.debug('Update battery status from dict')

        # Cupra
        if 'value' not in fromDict:
            fromDict['value'] = fromDict
            
        if 'value' in fromDict:
            self.currentSOC_pct.fromDict(fromDict['value'], 'currentSOC_pct')

            if 'cruisingRangeElectric_km' in fromDict['value']:
                cruisingRangeElectric_km = int(fromDict['value']['cruisingRangeElectric_km'])
                if self.fixAPI and cruisingRangeElectric_km == 0x3FFF:
                    cruisingRangeElectric_km = None
                    LOG.info('%s: Attribute cruisingRangeElectric_km was error value 0x3FFF. Setting error state instead'
                             ' of 16383 km.', self.getGlobalAddress())
                self.cruisingRangeElectric_km.setValueWithCarTime(
                    cruisingRangeElectric_km, lastUpdateFromCar=None, fromServer=True)
            else:
                self.cruisingRangeElectric_km.enabled = False
        else:
            self.currentSOC_pct.enabled = False
            self.cruisingRangeElectric_km.enabled = False

        super().update(fromDict=fromDict, ignoreAttributes=(
            ignoreAttributes + ['currentSOC_pct', 'cruisingRangeElectric_km']))

    def __str__(self):
        string = super().__str__()
        if self.currentSOC_pct.enabled:
            string += f'\n\tCurrent SoC: {self.currentSOC_pct.value}%'
        if self.cruisingRangeElectric_km.enabled:
            if self.cruisingRangeElectric_km.value is not None:
                string += f'\n\tRange: {self.cruisingRangeElectric_km.value}km'
            else:
                string += '\n\tRange: currently unknown'
        return string
