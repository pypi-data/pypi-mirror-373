# Run "sh ./tools/generate-dataclasses.sh" to generate dataclasses of the properties
# from the JSON schema.

# TODO: This currently can't seem to find the "tools" module/folder.
# This might not matter because if they change the schema, we'd have to
# modify this anyway.
uv run python tools/generate_dataclasses.py
