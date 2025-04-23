# Deployment Instructions

Here's how you can set up and run this project on a Linux server:

## Clone the repository (assuming you've put this in a Git repository):
```bash
git clone https://github.com/mpinb/spermull-bonn.git
cd spermull-bonn
```

## Set up a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Install Node.js and npm (if not already installed):
```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# For CentOS/RHEL
sudo yum install nodejs npm
```
**NOTE:** To run `nodejs` in soma I used `nvm` then you don't need `sudo` level access to install packages. 
The last compatible version of node for CentOS 7 is 16
```bash
somalogin01 ~/spermull-bonn (sperrmul-frontend) $ nvm use 16
Now using node v16.20.2 (npm v8.19.4)
somalogin01 ~/spermull-bonn (sperrmul-frontend) $ npm --version
8.19.4
somalogin01 ~/spermull-bonn (sperrmul-frontend) $ node --version
v16.20.2
```

## Install Tailwind CSS dependencies:
```bash
npm install
```

## Build the CSS:
```bash
npm run build:css
```

## Run the Flask application:
```bash
python app.py
```

## Access the application at http://localhost:5000