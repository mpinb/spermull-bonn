# Deployment Instructions

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
python app.py
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

### Build the CSS:
```bash
npm run build:css
```

### Run the Flask application:
```bash
python app.py
```