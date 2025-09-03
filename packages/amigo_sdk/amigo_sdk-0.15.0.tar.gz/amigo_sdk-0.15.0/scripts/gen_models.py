import json
from pathlib import Path

import httpx
from datamodel_code_generator import (
    DataModelType,
    InputFileType,
    OpenAPIScope,
    generate,
)


def safe_class_name(name: str) -> str:
    # Strip your prefix if present; keep everything else intact
    prefix = "src__app__endpoints__"
    return name[len(prefix) :] if name.startswith(prefix) else name


def main() -> None:
    schema_url = "https://api.amigo.ai/v1/openapi.json"
    root = Path(__file__).parent.parent
    out_dir = root / "src" / "amigo_sdk" / "generated"
    output_file = out_dir / "model.py"
    aliases_path = root / "aliases.json"

    # Create the generated directory if it doesn't exist
    out_dir.mkdir(parents=True, exist_ok=True)

    # Remove existing model.py if it exists
    if output_file.exists():
        output_file.unlink()

    # Fetch the OpenAPI schema from the remote URL
    print(f"Fetching OpenAPI schema from {schema_url}...")
    response = httpx.get(schema_url)
    response.raise_for_status()
    openapi_content = response.text

    # Load aliases as a mapping (Python API expects a dict)
    aliases: dict[str, str] = {}
    if aliases_path.exists():
        aliases = json.loads(aliases_path.read_text())

    generate(
        openapi_content,
        input_file_type=InputFileType.OpenAPI,
        output=output_file,
        output_model_type=DataModelType.PydanticV2BaseModel,
        openapi_scopes=[
            OpenAPIScope.Schemas,
            OpenAPIScope.Parameters,
            OpenAPIScope.Paths,
            OpenAPIScope.Tags,
        ],
        snake_case_field=True,
        field_constraints=True,
        use_operation_id_as_name=True,  # Request/Response names from operationId
        reuse_model=True,
        custom_class_name_generator=lambda name: name.replace(
            "src__app__endpoints__", ""
        ),
        aliases=aliases,
        parent_scoped_naming=True,
        collapse_root_models=True,
    )

    print(f"✅ Models regenerated → {output_file}")


if __name__ == "__main__":
    main()
