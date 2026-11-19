# https://just.systems

test *args:
    uv run pytest -n auto . {{args}}

start:
    uv run --extra gurobipy13 mm_track

[working-directory: 'docs']
@docs-build:
  uv run make html
