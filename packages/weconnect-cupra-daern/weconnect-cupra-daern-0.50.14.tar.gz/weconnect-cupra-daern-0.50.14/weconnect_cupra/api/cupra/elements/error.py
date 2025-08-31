from typing import TYPE_CHECKING, Optional, Dict, Any

import logging

from datetime import datetime

from weconnect_cupra.addressable import AddressableObject, AddressableAttribute

if TYPE_CHECKING:
    from weconnect_cupra.elements.generic_status import GenericStatus

LOG: logging.Logger = logging.getLogger("weconnect_cupra")


class Error(AddressableObject):
    def __init__(
        self,
        localAddress: str,
        parent: Optional['GenericStatus'],
        fromDict: Dict[str, Any] = None,
    ) -> None:
        super().__init__(localAddress=localAddress, parent=parent)
        self.code: AddressableAttribute[int] = AddressableAttribute(localAddress='code', parent=self, value=None, valueType=int)
        self.message: AddressableAttribute[str] = AddressableAttribute(localAddress='message', parent=self, value=None, valueType=str)
        self.group: AddressableAttribute[int] = AddressableAttribute(localAddress='group', parent=self, value=None, valueType=int)
        self.info: AddressableAttribute[str] = AddressableAttribute(localAddress='info', parent=self, value=None, valueType=str)
        self.timestamp: AddressableAttribute[str] = AddressableAttribute(localAddress='timestamp', parent=self, value=None, valueType=datetime)
        self.retry: AddressableAttribute[bool] = AddressableAttribute(localAddress='retry', parent=self, value=None, valueType=bool)

        if fromDict is not None:
            self.update(fromDict)

    def reset(self) -> None:
        if self.code.enabled:
            self.code.setValueWithCarTime(None, lastUpdateFromCar=None, fromServer=True)
            self.code.enabled = False
        if self.message.enabled:
            self.message.setValueWithCarTime(None, lastUpdateFromCar=None, fromServer=True)
            self.message.enabled = False
        if self.group.enabled:
            self.group.setValueWithCarTime(None, lastUpdateFromCar=None, fromServer=True)
            self.group.enabled = False
        if self.info.enabled:
            self.info.setValueWithCarTime(None, lastUpdateFromCar=None, fromServer=True)
            self.info.enabled = False
        if self.retry.enabled:
            self.retry.setValueWithCarTime(None, lastUpdateFromCar=None, fromServer=True)
            self.retry.enabled = False
        if self.enabled:
            self.enabled = False

    def update(self, fromDict: Dict[str, Any]) -> None:
        LOG.debug('Update Status Error from dict')

        self.code.fromDict(fromDict, 'code')
        self.message.fromDict(fromDict, 'message')
        self.group.fromDict(fromDict, 'group')
        self.info.fromDict(fromDict, 'info')
        self.timestamp.fromDict(fromDict, 'errorTimeStamp')
        self.retry.fromDict(fromDict, 'retry')

        if not self.code.enabled and not self.message.enabled and not self.code.enabled and not self.info.enabled \
                and not self.retry.enabled:
            self.enabled = False
        else:
            self.enabled = True

        for key, value in {key: value for key, value in fromDict.items()
                           if key not in ['code', 'message', 'group', 'info', 'errorTimeStamp', 'retry']}.items():
            LOG.debug('%s: Unknown attribute %s with value %s', self.getGlobalAddress(), key, value)

    def __str__(self) -> str:
        return f'Error {self.code.value}: {self.message.value} \n\tinfo: {self.info.value} \n\ttimestamp: {self.timestamp.value}'
