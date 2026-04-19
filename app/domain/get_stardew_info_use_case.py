from app.data.stardew_info_data_source import StardewDatasource


class GetStardewInfoUseCase:
    def __init__(self) -> None:
        self._datasource = StardewDatasource()

    def execute(self, query: str) -> str:
        data = self._datasource.get(query)
        return f"[{data['category'].upper()}] {data['name']}: {data['description']}"
