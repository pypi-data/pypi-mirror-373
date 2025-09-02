from abc import ABC, abstractmethod

class ReaderInterface(ABC):
    @abstractmethod
    def get_incremental_statement(self) -> str:
        pass

    @abstractmethod
    def get_columns_source(self) -> str:
        pass

    @abstractmethod
    def get_order_by_sql_statement(self) -> str:
        pass

    @abstractmethod
    def get_limit_sql_statement(self) -> str:
        pass

    @abstractmethod
    def get_sql_statement(self) -> str:
        pass