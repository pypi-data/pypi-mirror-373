# CoDatascientist Dev Readme
the user-facing co-datascientist python library!

dependencies: calls `co-datascientist-backend`

## Running CLI

1. **run co-datascientist-backend**: follow co-datascientist-backend instructions on how to run, it will probably run on port 8001. make sure the CO_DATASCIENTIST_BACKEND_URL in settings (.env) is correct.
2. **run main.py with arguments**. to test the whole workflow, use the test file at `tests/test_scripts/xor_solver.py`. 
run this command (make sure you have torch installed otherwise it won't work (you can try running the script to see if you have the right libraries): 
```bash
uv run main.py run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo_2/ppi.py  --python-path /home/ubuntu/miniconda3/bin/python
```


databricks demo: 
```bash
uv run main.py run --cloud-config /home/ozkilim/Co-DataScientist_/demos/XOR_databricks/databricks_config.yaml
```
uv run main.py run --script-path /home/ozkilim/Co-DataScientist_/demos/XOR/xor_solver.py  --python-path /home/ubuntu/miniconda3/envs/XOR/bin/python
```


<!-- #TODO: setupa comandad for testing always in dev mode ... on a dummy file with just the worse tokens etc ... 

python main.py run --script-path /home/ozkilim/Co-DataScientist/XOR/xor_solver.py --python-path /home/ozkilim/POC/Pi-aColada/.venv/bin/python -->

## 🔑 Adding Your OpenAI API Key (Development)

For development, you can manage your OpenAI API key through the CLI commands:

### Add/Update OpenAI Key
```bash
# This will prompt you to enter your OpenAI API key
uv run main.py --reset-openai-key --dev run --script-path tests/test_scripts/xor_solver.py
```

Or use the dedicated key management command:
```bash
# Manage your OpenAI key
uv run main.py openai-key
```

### Remove OpenAI Key
```bash
# Switch back to free tier
uv run main.py openai-key --remove
```

### Check Current Status
```bash
# See if you're using your OpenAI key or the free tier
uv run main.py status
```

**Benefits of adding your OpenAI key:**
- 🚀 **Unlimited usage** with your OpenAI account
- 💰 **Direct billing** to your OpenAI account  
- 🔒 **No usage limits** from TropiFlow's free tier
- 🛠️ **Better for development** - no rate limiting during testing

**Note**: Get your OpenAI API key from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

## Using the MCP

1. **configure cursor**: Follow the `README.md` instructions
2. **optional (but recommended) - enable autorun mode**: this way it doesn't ask for permission to run the tool each time. settings → features → enable auto-run 
3. **run the local mcp server**: 
```bash
uv run main.py mcp-server
```
it will ask you to enter your api key. generate a key following the readme in `co-datascientist-backend` repository.
4. **test it!**: open the test file at `tests/test_scripts/xor_solver.py` in cursor, and ask the model help from co-datascientist in improving the code.

*note:* when restarting the mcp-server, reload it from the cursor settings UI, otherwise it won't work

## KPI-Based Folder Naming

**Feature**: Automatically extract KPI scores from code output and use them to name output folders as `{KPI}_{idea_name}`. Falls back to original naming if KPI extraction fails.

**Usage**: Add `print("KPI:", score)` to your code. Supports formats like `KPI: 0.85`, `kpi: 0.95`, etc.

**Examples**: 
- `print("KPI: 0.85")` → folder named `0_85_baseline`
- `print("KPI: 1.0")` → folder named `1_baseline`
- No KPI found → folder named `baseline` (original behavior)

**Control**: 
```bash
export ENABLE_KPI_FOLDER_NAMING=true   # enable (default)
export ENABLE_KPI_FOLDER_NAMING=false  # disable
```

**Implementation**: Modular design in `kpi_extractor.py` with robust fallback - easy to remove if needed.
 
## Uploading to PyPi
following [this guide](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/) with uv, this is how to upload co-datascientist to pypi:
1. make sure you have a [PyPi](https://pypi.org/) account
2. generate release files: `uv build`
3. upload using twine (via uv to ensure latest version):
```bash
uv run twine upload dist/*
``` 
4. you will be prompted for a token, you can view it on your pypi account

# Developer Options

## Hidden CLI Flags

### --dev
Enables development mode (connects to local backend, disables production safety checks, etc). For developer use only. Not shown in user CLI help.

### --debug
Shows detailed logs and verbose output for workflow runs. For developer use only. Not shown in user CLI help.

Example usage:

```bash
python main.py run --script-path /abs/path/to/script.py --python-path python --debug
```

```bash
python main.py --dev
```

Databricks integration: 

python main.py run --cloud-config /home/ozkilim/Co-DataScientist_/demos/XOR_databricks/databricks_config.yaml


These options are not documented in the main README and are intended for internal development and debugging only.




setting upt he MCP server (TODO add to main readme: )

To use from cursor or other AI clients, run the MCP server:
```bash
co-datascientist mcp-server
```

And add the MCP configuration to the AI client. For example in cursor go to:
`file -> preferences -> cursor settings -> MCP -> Add new global MCP server`,
and add the co-datascientist mcp server config in the json, should look like this:
```json
{
  "mcpServers": {
    "CoDatascientist": {
        "url": "http://localhost:8000/sse"
    }
  }
}