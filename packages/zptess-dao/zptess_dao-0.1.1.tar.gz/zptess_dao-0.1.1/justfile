# To install just on a per-project basis
# 1. Activate your virtual environemnt
# 2. uv add --dev rust-just
# 3. Use just within the activated environment

drive_uuid := "77688511-78c5-4de3-9108-b631ff823ef4"
#drive_uuid := "8425-155D"

user :=  file_stem(home_dir())
def_drive := join("/media", user, drive_uuid)
project := file_stem(justfile_dir())
local_env := join(justfile_dir(), ".env")


# list all recipes
default:
    just --list

# Install tools globally
tools:
    uv tool install twine
    uv tool install ruff

# Add conveniente development dependencies
dev:
    uv add --dev pytest

# Build the package
build:
    rm -fr dist/*
    uv build

# Generate a requirements file
requirements:
    uv pip compile pyproject.toml -o requirements.txt

# Publish the package to PyPi
publish prj=project pkg="zptessdao": build
    twine upload -r pypi dist/*
    uv run --no-project --with {{prj}} --refresh-package {{prj}} \
        -- python -c "from {{pkg}} import __version__; print(__version__)"

# Publish to Test PyPi server
test-publish prj=project pkg="zptessdao": build
    twine upload --verbose -r testpypi dist/*
    uv run --no-project  --with {{prj}} --refresh-package {{prj}} \
        --index-url https://test.pypi.org/simple/ \
        --extra-index-url https://pypi.org/simple/ \
        -- python -c "from {{pkg}} import __version__; print(__version__)"


# Backup .env to storage unit
env-bak drive=def_drive: (check_mnt drive) (env-backup join(drive, "env", project))

# Restore .env from storage unit
env-rst drive=def_drive: (check_mnt drive) (env-restore join(drive, "env", project))

# Restore a fresh, unmigrated ZPTESS database
db-anew date drive=def_drive: (check_mnt drive) (db-restore date)

# Starts a new database export migration cycle   
anew date="20250121" folder="migra" verbose="": (db-anew date)
    #!/usr/bin/env bash
    set -exuo pipefail
    uv sync --reinstall
    # I don't remember how I called this step
    uv run zp-db-fix --console  rounds --zp-fict --dry-run
    uv run zp-db-fix --console  rounds --stddev --dry-run
    test -d {{ folder }} || mkdir {{ folder }}
    uv run zp-db-schema --console  {{ verbose }}
    uv run zp-db-extract --console  {{ verbose }} all --output-dir {{ folder }}

# Starts a new database import migration cycle   
aload stage="summary" folder="migra":
    #!/usr/bin/env bash
    set -exuo pipefail
    test -d {{ folder }} || mkdir {{folder}}
    uv run zp-db-loader --console  config --input-dir {{folder}}
    uv run zp-db-loader --console  batch --input-dir {{folder}}
    if [ "{{stage}}" == "photometer" ]; then
        uv run zp-db-loader --console  photometer --input-dir {{folder}}
    elif [ "{{stage}}" == "summary" ]; then
        uv run zp-db-loader --console  photometer --input-dir {{folder}}
        uv run zp-db-loader --console  summary --input-dir {{folder}}
    elif [ "{{stage}}" == "rounds" ]; then
        uv run zp-db-loader --console  photometer --input-dir {{folder}}
        uv run zp-db-loader --console  summary --input-dir {{folder}}
        uv run zp-db-loader --console  rounds --input-dir {{folder}}
    elif [ "{{stage}}" == "samples" ]; then
        uv run zp-db-loader --console  photometer --input-dir {{folder}}
        uv run zp-db-loader --console  summary --input-dir {{folder}}
        uv run zp-db-loader --console  rounds --input-dir {{folder}}
        uv run zp-db-loader --console  samples --input-dir {{folder}}
    else
        echo "No known stage"
        exit 1
    fi

qa stage="summary" folder="migra":
    #!/usr/bin/env bash
    set -exuo pipefail
    uv run zp-db-qa --console  all
   

# =======================================================================


[private]
db-restore date:
    #!/usr/bin/env bash
    set -exuo pipefail
    cp {{ def_drive }}/zptess/zptess-{{date}}.db zptess.prod.db
    

check_mnt mnt:
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ ! -d  {{ mnt }} ]]; then
        echo "Drive not mounted: {{ mnt }}"
        exit 1 
    fi

[private]
env-backup bak_dir:
    #!/usr/bin/env bash
    set -exuo pipefail
    if [[ ! -f  {{ local_env }} ]]; then
        echo "Can't backup: {{ local_env }} doesn't exists"
        exit 1 
    fi
    mkdir -p {{ bak_dir }}
    cp {{ local_env }} {{ bak_dir }}

  
[private]
env-restore bak_dir:
    #!/usr/bin/env bash
    set -euxo pipefail
    if [[ ! -f  {{ bak_dir }}/.env ]]; then
        echo "Can't restore: {{ bak_dir }}/.env doesn't exists"
        exit 1 
    fi
    cp {{ bak_dir }}/.env {{ local_env }}
    
