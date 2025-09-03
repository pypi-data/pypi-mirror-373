[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# RUDI Node tools: _rudi-node-read_ library

This library offers tools to take advantage of
the [external API](https://app.swaggerhub.com/apis/OlivierMartineau/RUDI-PRODUCER) of a RUDI Producer node (also
referred as RUDI node).

The Jupyter notebook [README.ipynb](https://github.com/OlivierMartineau/rudi-node-read/blob/release/README.ipynb) offers
an overview of the available functionalities.

## Installation

```sh
pip install rudi-node-read
```

You don't need installing any additional library to use this.

## Usage

See [Python notebook](https://github.com/OlivierMartineau/rudi-node-read/blob/release/README.ipynb) for use examples.

## Testing

Rudi-node-read supports unit test discovery using Pytest:

```sh
dest_dir="rudi-node-read"
git clone https://github.com/OlivierMartineau/rudi-node-read.git $dest_dir
cd $dest_dir

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements-dev.txt

pytest
```

You may have a look at the [tests](https://github.com/OlivierMartineau/rudi-node-read/tree/release/tests) if you wish to see how every class or function is used.
