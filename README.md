# This Script can be used to generate and download Tower Data for [netzkarte.app](https://netzkarte.app)

> [!WARNING]
> Not affiliated with BNetzA, use at your own risk!

> [!INFO]
> Contains AI-generated code. Thrown together by me, a human :3
## The Data:
#### What you'll get:
- Official **locations** of all cellular towers in germany (~80K), including:
	- **Network providers**
	- Date of last equipment change
	- Sending units (~1.3M), including: 
		- **Mounting height**
		- **Sending direction**
		- Safety distances (general and vertical)
- Locations of small cells in germany (partly outdated)
#### What's not available:
- Sending frequencies
- Sending strengths
- Sending bands
- Sending technologies
- Network providers *per sending units*
- Infos about small cells apart from their position

## How to run this
### Step 1: Create a `venv` and install dependencies

> [!INFO]
> This requires Python 3.11 or higher.
> This is only needed if you want to host your own version of netzkarte.app

```bash
python -m venv .venv

.venv/bin/pip install -r requirements.txt
```

### Step 2: Run the script
```bash
.venv/bin/python main.py
```

### Result: 
- Inside `\serve` will be the **web-ready** final files to serve.
- Inside  `\assets\cell_towers` will be an **SQLite Database** containing all tower data.

### What to do with this:
##### You might
- estminate germany's cellular coverage. See [netzkarte-coverage](https://github.com/tinti-femboy/netzkarte-coverage)
- host your own cell tower API. See [netzkarte-backend](https://github.com/tinti-femboy/netzkarte-ai)
- estminate the individial providers on seperate sending units. See [netzkarte-ai](https://github.com/tinti-femboy/netzkarte-ai)
- compare different cellular providers. Up to [you](https://gist.github.com/mine).