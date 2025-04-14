# UNDP Web Enabled RAG Assistant

## Setting things up
This code base is written in Python3. Make sure to have Python3.13 or above installed on your machine.
It also requires that Ollama be installed on your machine, and that you have downloaded at least one open source Ollama compatible model.

- To download Ollama, visit: [https://ollama.com/download](https://ollama.com/download).
- To browse and download different Ollama compatible LLMs, visit: [https://ollama.com/library](https://ollama.com/library).

While it is configurable to use an online search engine, we strongly recommend you use an open-source local engine. [Searxng](https://github.com/searxng/searxng) is great for this! It is a privacy-respecting, hackable mastersearch engine—one that aggregates multiple different engines like Duck Duck Go, Google, etc.

- To run Searxng locally, we recommend you download and run the Docker image here: [https://github.com/searxng/searxng-docker](https://github.com/searxng/searxng-docker).
- Make sure to configure the `searxng/settings.yml` as follows:
```
search:
	...
	formats:
		- html
		- ...
		- json
```
The AI agents use the `json` format. If you do not use Searxng, or do not activate the `json` format, you will need to edit the `./process/_03_perform_search.py` file to return a json object with the appropriate formatting.

This of requires that you have Docker installed on your machine. Once Searxng is installed, run it via Docker. This should start a `localhost` server on port `8080`.

When these requirements are met, create a local python environment by running:
```
python -m venv /path/to/virtual/environment
```

Then install all the requirements:
```
pip install -r /path/to/requirements.txt
```

That is all! You should be good to go.
To start the assistant, run:
```
python main.py
```