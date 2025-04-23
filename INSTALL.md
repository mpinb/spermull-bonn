Deployment Instructions
Here's how you can set up and run this project on a Linux server:

Clone the repository (assuming you've put this in a Git repository):
bashgit clone <your-repo-url>
cd map_app

Set up a Python virtual environment:
bashpython3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Install Node.js and npm (if not already installed):
bash# For Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# For CentOS/RHEL
sudo yum install nodejs npm

Install Tailwind CSS dependencies:
bashnpm install

Build the CSS:
bashnpm run build:css

Run the Flask application:
bashpython app.py

Access the application at http://localhost:5000