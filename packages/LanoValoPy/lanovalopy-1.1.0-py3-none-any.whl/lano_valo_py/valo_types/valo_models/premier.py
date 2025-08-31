from pydantic import BaseModel


class GetPremierTeamFetchOptionsModel(BaseModel):
    team_name: str
    team_tag: str
