from abc import ABC, abstractmethod
from dataclasses import dataclass

from pathlib import Path

from typing import Type, List
from etiket_client.sync.database.models_pydantic import sync_item, new_sync_item_db

class SyncSourceBase(ABC):
    @property
    @abstractmethod
    def SyncAgentName(self) -> str:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def ConfigDataClass(self) -> Type[dataclass]:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def MapToASingleScope(self) -> bool:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def LiveSyncImplemented(self) -> bool:
        return False

    @staticmethod
    @abstractmethod
    def checkLiveDataset(configData: Type[dataclass], syncIdentifier: sync_item, maxPriority: bool) -> bool:
        pass
    
    @staticmethod
    @abstractmethod
    def syncDatasetNormal(configData: Type[dataclass], syncIdentifier: sync_item):
        pass
    
    @staticmethod
    @abstractmethod
    def syncDatasetLive(configData: Type[dataclass], syncIdentifier: sync_item):
        pass

class SyncSourceFileBase(SyncSourceBase):
    @property
    @abstractmethod
    def level(self) -> int:
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    def rootPath(configData: Type[dataclass]) -> Path:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def is_single_file(self) -> bool:
        raise NotImplementedError

class SyncSourceDatabaseBase(SyncSourceBase):
    @staticmethod
    @abstractmethod
    def getNewDatasets(configData: Type[dataclass], lastIdentifier: str) -> 'List[new_sync_item_db] | None':
        raise NotImplementedError