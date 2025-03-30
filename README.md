# Simple Gradio App
This is a basic Gradio app that greets the user.

## Dependencies
- Gradio
- Python 3.x

### ⚙️ **How It Works:**

- **Gradio-based Interface:**
  - Provides a centralized interface where Y1D students can intergact with their client.

- **Tabbed Layout:**
  - Easy-to-use navigation with clear labeling:


  ### **Launching the Application:**

- Hosted locally on a Gradio server accessible at `0.0.0.0:7862`.
- Simply execute the Python script, and navigate to the provided URL in your browser.

```bash
python main.py
```

## Setup

### Prerequisites
- Docker
- Python 3.11+

In case of using a VM for deployment and model dev you can use `gh` to authorize your VM session. Steps include: 

1. Generate a Personal Access Token (PAT) Once
2. Install the GitHub CLI on your new VM

```bash
type -p curl >/dev/null || sudo apt install curl -y
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg 
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] \
  https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y
```

3. Log in with `gh` (Using Your Token)

```bash
gh auth login
```

### Update system and Install Docker

```bash
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

### Start Qdrant Server 

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

### Open firewall for port 7862

```bash
sudo ufw allow 7862/tcp
sudo ufw reload
```

### Install venv

```bash 
apt install python3.10-venv
```

### Clone the package and install dependencies

```bash
git clone https://github.com/mdavarynejad/DeepD.git
cd DeepD
python3 -m venv venv
source venv/bin/activate 
pip install --upgrade pip 
pip install -r requirements.txt
```



