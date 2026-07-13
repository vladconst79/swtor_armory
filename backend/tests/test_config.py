from app.core.config import Settings


def test_settings_parse_cors_origins_from_comma_separated_string() -> None:
    settings = Settings(backend_cors_origins="http://localhost:5173, http://localhost:3000")

    assert settings.backend_cors_origins == [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
