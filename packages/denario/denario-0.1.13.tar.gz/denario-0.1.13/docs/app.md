# DenarioApp

GUI for [Denario](https://github.com/AstroPilot-AI/Denario.git), powered by [streamlit](https://streamlit.io).

## Clone

Get the app with

`git clone https://github.com/AstroPilot-AI/DenarioApp.git`

## Run locally

Install the GUI from source following one of the following steps.

1. Install with pip

   ```bash
   pip install -e .
   ```

2. Install with [uv](https://docs.astral.sh/uv/)

   ```bash
   uv sync
   ```

Run the app with:

```bash
streamlit run src/denario_app/app.py
```

## Run in Docker

You may need `sudo` permission [or use this link](https://docs.docker.com/engine/install/linux-postinstall/). To build the docker run:

```bash
docker build -t denario-app .
```

To run the app:

```bash
docker run -p 8501:8501 --rm \
    -v $(pwd)/project_app:/app/project_app \
    -v $(pwd)/data:/app/data \
    -v $(pwd).env/app/.env \
    denario-app
```

That command exposes the default streamlit port `8501`, change it to use a different port. You can mount additional volumes to share data with the docker using the `-v` flag. The above command shares the `project_app` folder, where the project files are generated, a `data`folder, where the required data would be present, and a `.env` file with the API keys (so no need to parse them manually). To run the docker in interactive mode, add the flag `-it` and `bash` at the end of the command.

You can also use [docker compose](https://docs.docker.com/compose/), you can just run

```bash
docker compose up --watch
```

to build the image and run the container.
