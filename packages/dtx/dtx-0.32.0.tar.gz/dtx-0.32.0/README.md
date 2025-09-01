# How to Install `dtx`

Before you begin, choose **how you want to run `dtx`** depending on your environment and requirements.

---

## Option 1: Install `dtx` locally **with full dependencies (torch etc.)**

This is recommended if you plan to run **local models** (e.g., Hugging Face, Ollama) on your machine.

```bash
pip install dtx[torch]
```

Includes:
- Core CLI
- `torch`, `transformers` for local LLM and classifier execution
- Supports all datasets and local execution

---

## Option 2: Install `dtx` if **torch is already installed**

If your environment already has `torch` installed (for example, in a GPU-accelerated ML environment), you can skip extras:

```bash
pip install dtx
```

`dtx` will use your existing `torch` installation.

> Tip: Verify torch is installed:
> ```bash
> python -c "import torch; print(torch.__version__)"
> ```

---

## Option 3: Use `uv` for fast installation in a clean environment

If you're creating a new environment and want **fast dependency resolution** with `uv`:

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install `dtx` with full dependencies

```bash
uv pip install dtx[torch]
```

---

## Option 4: Use Docker wrapper (`ddtx`)

If you prefer **Dockerized execution** (no local `torch` install required), you can use `ddtx`.

1. Install `dtx` (for the `ddtx` wrapper CLI):

```bash
pip install dtx
```

2. Use `ddtx` to run inside Docker:

```bash
ddtx redteam scope "Describe your agent" output.yml
```

Features:
- No need to install `torch` locally
- Fully containerized execution
- Automatically mounts `.env` and working directories
- Use Docker-managed templates and tools

---

## Summary of Options

| Method | Use case | Install command |
|--------|----------|----------------|
| Local, full dependencies | Full feature set, local models | `pip install dtx[torch]` |
| Local, existing torch | You already have `torch` installed | `pip install dtx` |
| New env, fast install | Clean, fast setup | `uv pip install dtx[torch]` |
| Docker (ddtx) | No local Python dependencies, isolated | `pip install dtx` + use `ddtx` CLI |


## How to Get Started (Development)

Follow these steps to set up `dtx` for local development.

---

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-ORG/dtx.git
cd dtx
```

---

### 2. Install Dependencies

Run the following command:

```bash
make install
```

This will:

* Ensure the `poetry-plugin-export` is installed
* Install all dependencies including `dev` and `torch` groups
* Set up the `dtx` package in editable mode

---

### 3. Activate the Virtual Environment

Run this in your shell to activate the Poetry-managed virtual environment:

```bash
eval $(poetry env activate)
```

Alternatively, you can run:

```bash
make venv
```

This will print the exact `eval` command you need to run manually. For example:

Note: `make` cannot modify your current shell environment, so you must run the `eval` command directly.

---

### 4. Run the CLI

Once the environment is active, you can use the CLI:

```bash
dtx --help
```

---

### 5. Export Requirements (Optional)

To export the current environment to a `requirements.txt` file (useful for `pip`-based tools or deployment):

```bash
make export
```

This will generate a `requirements.txt` file including development and optional dependencies like `torch`.



