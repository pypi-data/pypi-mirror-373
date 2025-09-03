from abc import ABC, abstractmethod

class MigratorRowReaderInterface(ABC):

    @abstractmethod
    def get_source_query_with_incremental_column(self) -> str:
        pass

    @abstractmethod
    def get_source_query_without_incremental_column(self) -> str:
        pass
    
    @abstractmethod
    def get_source_data(self, function_get_source_query: object, type: str) -> list:
        pass
    
    @abstractmethod
    def get_columns_names(self, function_get_source_query: object) -> list:
        pass