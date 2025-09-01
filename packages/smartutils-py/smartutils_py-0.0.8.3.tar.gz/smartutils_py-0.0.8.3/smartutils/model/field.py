from pydantic import BaseModel, model_validator


def explicit_nonnull_fields(model: BaseModel) -> dict:
    try:
        # Pydantic 2
        data = model.model_dump(exclude_unset=True)
    except AttributeError:
        # Pydantic 1
        data = model.dict(exclude_unset=True)
    return {k: v for k, v in data.items() if v is not None}


class StrippedBaseModel(BaseModel):
    """自动对str进行strip"""

    @model_validator(mode="before")
    @classmethod
    def strip_str_fields(cls, values):
        if isinstance(values, dict):
            for field_name, field in cls.model_fields.items():
                if (
                    field.annotation is str
                    and field_name in values
                    and isinstance(values[field_name], str)
                ):
                    values[field_name] = values[field_name].strip()
        return values
