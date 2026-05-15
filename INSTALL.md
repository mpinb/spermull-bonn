# Deployment Instructions

## Versions

This repository contains two independent implementations:

- **`main` branch** — Flask application (this guide)
- **`static-version` branch** — static HTML/JS for GitHub Pages (see that
  branch for its own build instructions)

---

## Flask application (`main` branch)

Here's how you can set up and run this project on a Linux server:

## Clone the repository:
```bash
git clone https://github.com/mpinb/spermull-bonn.git
cd spermull-bonn
```

## Option 1: Install with Pixi (Recommended)

### Install Pixi (if not already installed):
```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

### Initialize and activate the environment:
```bash
pixi run
```
This will create an environment with all required Python dependencies.

### Install Node.js (if not already installed):
**Using nvm (recommended for CentOS 7):**
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
# Source nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
# Install and use Node.js 16 (last compatible version for CentOS 7)
nvm install 16
nvm use 16
```

### Install Tailwind CSS dependencies:
```bash
npm install
```

### Build the CSS:
```bash
npm run build:css
```

### Run the Flask application:
```bash
pixi run python app.py
# Open http://localhost:3000
```

## Option 2: Install with Virtual Environment (Legacy method)

### Set up a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Install Node.js and npm (if not already installed):
```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# For CentOS/RHEL
sudo yum install nodejs npm
```

**NOTE:** To run `nodejs` in soma I used `nvm` then you don't need `sudo` level access to install packages. 
The last compatible version of node for CentOS 7 is 16:
```bash
nvm use 16
Now using node v16.20.2 (npm v8.19.4)
```

### Install Tailwind CSS dependencies:
```bash
npm install
```

### Run the Flask application:
```bash
python app.py
# Open http://localhost:3000
```

---

## Updating the pickup schedule data

When a new year's CSV is available, run these two scripts in order.
Both scripts use paths relative to the repository root — no hardcoded
absolute paths.

### Step 1 — Filter and normalize the raw CSV

```bash
pixi run python py/filter_spermull.py \
    --input  data/spermullterminebonn<YEAR>.csv \
    --output data/spermull_only_<YEAR>.csv
```

This keeps only `PLAN_BEZ == 'Sperrmüll'` rows, collects all non-empty
`TERMIN*` dates per row, converts them from `DD.MM.YYYY` to `YYYY-MM-DD`,
and writes a clean comma-separated CSV.

### Step 2 — Rebuild the map data (geo_dates.msg)

```bash
pixi run python py/merge_schedule_with_geocodes.py \
    --schedule data/spermull_only_<YEAR>.csv \
    --geocodes data/geocoded_addr.csv \
    --output   data/geo_dates.msg
```

The Flask app reads `data/geo_dates.msg` on every request — no restart needed.
See [py/date_to_geocode.ipynb](py/date_to_geocode.ipynb) for the original
exploratory notebook this script was ported from.

### Step 3 — Rebuild the address autocomplete database (if new streets were added)

```bash
pixi run python create_db.py
```

---

## Static version (`static-version` branch)

The `static-version` branch is a separate, self-contained implementation
that runs entirely in the browser. It pre-computes all pickup data into a
GeoJSON file at build time and is deployed to GitHub Pages.

To work on it:

```bash
git checkout static-version
```

See the scripts under `data/` on that branch for how to regenerate the
GeoJSON from a new schedule CSV.