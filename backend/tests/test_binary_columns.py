from sqlalchemy import LargeBinary, inspect

from app.models import ClassName, Guild, Role, Title, Vehicle


def test_binary_fields_are_postgresql_column_ready() -> None:
    binary_columns = {
        ClassName: ["class_icon"],
        Role: ["icon"],
        Title: ["icon"],
        Vehicle: ["icon"],
        Guild: ["image"],
    }

    for model, column_names in binary_columns.items():
        columns = inspect(model).columns
        for column_name in column_names:
            assert isinstance(columns[column_name].type, LargeBinary)
            assert columns[column_name].nullable is True


def test_binary_backed_models_keep_optional_asset_metadata() -> None:
    title_columns = inspect(Title).columns
    vehicle_columns = inspect(Vehicle).columns

    assert title_columns.icon_filename.nullable is True
    assert title_columns.icon_url.nullable is True
    assert vehicle_columns.icon_filename.nullable is True
    assert vehicle_columns.icon_url.nullable is True
