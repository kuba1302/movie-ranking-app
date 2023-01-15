import json
from pathlib import Path

from pydantic import BaseModel

from src.sqlite import get_database_cursor_and_commit

sample_data_path = Path(__file__).parents[0] / "sample_data.json"


class Table(BaseModel):
    name: str
    values: list[dict]


class DataInserter:
    def __init__(self, sample_data_path: Path = sample_data_path) -> None:
        self.sample_data = self._load_data(sample_data_path)
        print([x for x in self.sample_data.items()])
        self.data = [
            Table(name=name, values=values) for name, values in self.sample_data.items()
        ]

    @staticmethod
    def _load_data(path: Path) -> dict[str, list[dict]]:
        with open(str(path)) as file:
            return json.load(file)

    def _prepare_query(self, table: Table) -> str:
        substring = ""
        for insert_data in table.values:
            substring += self._create_substring(insert_data)

        substring = substring[:-1]  # remove last comma

        return f"""
            --sql 
            INSERT INTO {table.name}
            VALUES {substring}; 
        """

    @staticmethod
    def _create_substring(insert_data: dict) -> str:
        value_list = []

        for value in insert_data.values():
            if isinstance(value, int):
                value_list.append(str(value))
            elif isinstance(value, str):
                value_list.append(f'"{value}"')
            else:
                raise ValueError(f"Wrong type! of value: {type(value)}")

        return f'({",".join(value_list)}),'

    def _insert_data_to_table(self, table: Table) -> None:
        with get_database_cursor_and_commit() as cursor:
            query = self._prepare_query(table)
            cursor.execute(query)

    def insert_data_to_tables(self) -> None:
        for table in self.data:
            self._insert_data_to_table(table)

    def insert_data_to_table(self, table_key: str) -> None:
        one_sample_value = self.sample_data[table_key]
        table = Table(name=table_key, values=one_sample_value)
        self._insert_data_to_table(table)


if __name__ == "__main__":
    inserter = DataInserter()
    inserter.insert_data_to_table("ratings")
