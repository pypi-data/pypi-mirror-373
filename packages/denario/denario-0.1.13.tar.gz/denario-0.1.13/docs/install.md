# Installation

## Requirements

For running Denario you will different API keys for the LLMs:

- OpenAI API key
- Gemini API key (optional)
- Anthropic API key (optional)
- gemini.json file (optional; needed if performing analysis with Gemini)
- Perplexity API key (optional; needed to put citations in the papers)

Click [here](apikeys.md) for more details on how to get the different API keys.

Also, you will need [LaTeX](https://www.latex-project.org/) installed for the write paper module. This is not required for the other modules.

## Virtual environment

Given that Denario could install packages and run code, we recommend to run it within a virtual environment. We recommend using Python 3.12. You can create a virtual environment with

```bash
python3 -m venv Denario_env
```

and activate it with

```bash
source Denario_env/bin/activate
```

Or use [conda](https://docs.conda.io/projects/conda/en/stable/index.html) instead:

```bash
conda create -n Denario_env python==3.12
conda activate Denario_env
```

## Install from PyPI

To install Denario, just run

```bash
pip install denario
```

## Build from source

### pip

You will need python 3.12 or higher installed. Clone Denario:

```bash
git clone https://github.com/AstroPilot-AI/Denario.git
cd Denario
```

Create and activate a virtual environment

```bash
python3 -m venv Denario_env
source Denario_env/bin/activate
```

And install the project

```bash
pip install -e .
```

### uv

You can also install the project using [uv](https://docs.astral.sh/uv/), just running:

```bash
uv sync
```

which will create the virtual environment and install the dependencies and project. Activate the virtual environment, if needed, with

```bash
source .venv/bin/activate
```
