from pydantic import BaseModel, ConfigDict


class EnvConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda k: k.upper(), populate_by_name=True
    )
