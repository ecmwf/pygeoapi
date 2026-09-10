# Local pygeoapi + polytope-mars-plugin setup

Instructions for building a local dev install of the ECMWF pygeoapi fork together with the polytope plugin.

## 1. Prerequisites

- Python 3.10+
- `git`, `pip`, `venv`

## 2. Create a working directory and virtualenv

```bash
mkdir -p ~/pygeoapi-dev && cd ~/pygeoapi-dev

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
```

## 3. Clone the repositories

```bash
# pygeoapi fork
git clone https://github.com/ecmwf/pygeoapi.git
cd pygeoapi
git checkout master
cd ..

# polytope plugin
git clone https://github.com/ecmwf/pygeoapi-polytope-plugin.git polytope_plugin
```

> If your polytope plugin repo has a different name/URL, replace the clone URL above.

## 4. Install the polytope plugin (editable)

```bash
cd polytope_plugin
pip install -e .
cd ..
```

## 5. Install pygeoapi (editable, from the fork)

```bash
cd pygeoapi
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Editable install (`-e`) means edits to the fork are picked up without reinstalling.

## 6. Configure pygeoapi

```bash
cp pygeoapi-config.yml example-config.yml

export PYGEOAPI_CONFIG=$PWD/example-config.yml
export PYGEOAPI_OPENAPI=$PWD/example-openapi.yml
```

Edit `example-config.yml` to register the polytope plugin under the relevant resource / provider block. See the plugin's README at https://github.com/ecmwf/pygeoapi-polytope-plugin for the exact provider class path and required config keys.

## 7. Generate OpenAPI document and run

```bash
pygeoapi openapi generate $PYGEOAPI_CONFIG --output-file $PYGEOAPI_OPENAPI
pygeoapi serve
```

Server is now at http://localhost:5000.

## 8. Daily workflow

```bash
source ~/pygeoapi-dev/.venv/bin/activate
cd ~/pygeoapi-dev/pygeoapi
pygeoapi serve
```

## 9. Updating

```bash
# pygeoapi fork
cd ~/pygeoapi-dev/pygeoapi
git pull origin master
pip install -r requirements.txt   # in case deps changed

# polytope plugin
cd ~/pygeoapi-dev/polytope_plugin
git pull
```

## Optional: Docker build

```bash
cd ~/pygeoapi-dev/pygeoapi
docker build -t pygeoapi:local .
docker run -p 5000:80 pygeoapi:local
```
