# Stock Market Prediction Gradio App

## Overview

This application provides a web interface built with Gradio for predicting stock market prices based on historical data. It allows users to select a stock ticker, granularity, prediction model, and other parameters to visualize historical data and future predictions.

The application is designed to be deployed using Docker for containerization and Caddy as a reverse proxy for automatic HTTPS.

**Technology Stack:**

*   **Backend:** Python
*   **Web Framework/UI:** Gradio
*   **Data Handling:** Pandas, Requests
*   **Machine Learning:** Scikit-learn
*   **Containerization:** Docker
*   **Web Server/Reverse Proxy:** Caddy (for HTTPS)
*   **Code Quality:** pre-commit (for commit message linting)

## Prerequisites

Before you begin, ensure you have the following:

*   **Git:** For cloning the repository.
*   **Linux Server:** A server (e.g., Ubuntu 20.04+) where you will deploy the application. You need `sudo` access.
*   **Docker:** Docker installed and running on the deployment server.
*   **Domain Name:** A domain name (e.g., `your_domain.com`) pointed to your server's public IP address via DNS A record.
*   **(For Development):** Python 3.11+ and `pip`.

## Architecture Overview

The production setup follows this flow:

1.  **User Request:** The user accesses `https://your_domain.com`.
2.  **DNS:** The domain resolves to the server's IP address.
3.  **Caddy:** Caddy receives the request on port 443 (HTTPS). It automatically handles TLS certificate acquisition and termination (using Let's Encrypt).
4.  **Reverse Proxy:** Caddy forwards the request internally to the application container running on port 7862.
5.  **Docker Container:** The container runs the Gradio application (`trader.py`).
6.  **Gradio App:** The Python application processes the request and serves the web interface.

```mermaid
graph LR
    A[User] -->|HTTPS request| B(your_domain.com);
    B -->|DNS Resolution| C(Server IP);
    C -->|Port 443| D[Caddy Server];
    D -->|Reverse Proxy| E[Docker Container: Port 7862];
    E -->|Runs| F[Gradio App (trader.py)];
    F -->|Serves UI| D;
    D -->|HTTPS response| A;
```

## Production Deployment (Step-by-Step)

These steps guide you through deploying the application on your Linux server.

**1. Clone the Repository**

```bash
git clone https://github.com/mdavarynejad/sm-gradio.git
cd sm-gradio
```

**2. Server Preparation**

*   **Update System Packages:**
    ```bash
    sudo apt-get update && sudo apt-get upgrade -y
    ```
*   **Install Docker (if not already installed):**
    ```bash
    sudo apt-get install docker.io -y
    sudo systemctl start docker
    sudo systemctl enable docker
    # Optional: Add user to docker group to avoid using sudo for docker commands
    # sudo usermod -aG docker $USER
    # newgrp docker # Requires logout/login or new shell
    ```
*   **Configure Firewall:** Allow incoming traffic on ports 80 (for HTTP ACME challenge) and 443 (for HTTPS). Port 7862 does *not* need to be publicly open as Caddy accesses it internally.
    ```bash
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw reload
    sudo ufw status
    ```

**3. Run Application Container**

Use the provided Python script to build the Docker image and run the container in detached mode with an auto-restart policy.

```bash
python run_docker.py
```

*   **What this script does:**
    *   Checks if Docker is running.
    *   Builds a Docker image named `move-app:latest` using the `Dockerfile`.
    *   Stops and removes any existing container named `move-app-container`.
    *   Starts a new container named `move-app-container` from the `move-app:latest` image.
    *   Runs the container in detached mode (`-d`).
    *   Sets the restart policy to `unless-stopped`, so it restarts automatically.
    *   Maps port `7862` inside the container to port `7862` on the host server.
    *   Mounts a host directory `/root/move_data` to `/workspace/move_data` inside the container. *(Note: The purpose of this volume is not immediately clear from the code and may need adjustment based on application needs).*
    *   *(Note: The script uses the names `move-app` and `move-app-container`. Consider updating the script and `Dockerfile` for names consistent with the repository, e.g., `sm-gradio`, if desired).*

**4. Install Caddy**

Install the Caddy web server on the host machine (not inside Docker).

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy -y
```

**5. Configure Caddy**

Create or edit the Caddy configuration file `/etc/caddy/Caddyfile`. Replace its contents with the following, substituting `your_domain.com` with your actual domain name:

```caddyfile
# /etc/caddy/Caddyfile

your_domain.com {
    # Enable compression
    encode gzip zstd

    # Reverse proxy requests to the Gradio app container running on port 7862
    reverse_proxy localhost:7862
}
```

*   **Explanation:**
    *   `your_domain.com`: Tells Caddy which domain this configuration applies to. Caddy will automatically provision and renew HTTPS certificates for this domain using Let's Encrypt.
    *   `encode gzip zstd`: Enables response compression.
    *   `reverse_proxy localhost:7862`: Forwards incoming requests for `your_domain.com` to the application running on `localhost:7862` (which is the Docker container mapped to the host).

**6. Start/Reload Caddy**

Apply the configuration and ensure Caddy is running.

*   **Reload configuration if Caddy is already running:**
    ```bash
    sudo systemctl reload caddy
    ```
*   **Start and enable Caddy if it's not running:**
    ```bash
    sudo systemctl start caddy
    sudo systemctl enable caddy # Ensures Caddy starts on system boot
    ```
*   **Check Caddy status:**
    ```bash
    sudo systemctl status caddy
    ```

**7. Verification**

Wait a minute or two for Caddy to obtain the SSL certificate. Then, open your web browser and navigate to `https://your_domain.com`. You should see the Gradio application interface served securely over HTTPS.

## Development Setup

Follow these steps to set up a local environment for development and contribution.

**1. Clone the Repository**

```bash
git clone https://github.com/mdavarynejad/sm-gradio.git
cd sm-gradio
```

**2. Create and Activate Virtual Environment**

It's highly recommended to use a virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate
# On Windows use: venv\Scripts\activate
```

**3. Install Dependencies**

Install all required Python packages, including development tools like `pre-commit`.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Set Up Commit Message Linting (pre-commit)**

This project uses `pre-commit` and the `conventional-pre-commit` hook to enforce the [Conventional Commits](https://www.conventionalcommits.org/) standard locally.

*   **Install the Git hook:** Run this command once within the repository:
    ```bash
    pre-commit install --hook-type commit-msg
    ```

Now, before finalizing any commit, the hook will automatically check your commit message format. If it's non-compliant, the commit will be aborted with an error message.

**5. Run Locally**

You can run the Gradio app directly for local testing (this will *not* use Docker or Caddy).

```bash
python trader.py
```

The app will typically be available at `http://127.0.0.1:7862`.

## Project Structure (Brief)

```
.
├── .git/                 # Git directory
├── .gitignore            # Specifies intentionally untracked files that Git should ignore
├── .pre-commit-config.yaml # Configuration for pre-commit hooks
├── data/                 # Data handling scripts/modules
│   └── data_handling.py
├── venv/                 # Python virtual environment (if created locally)
├── Dockerfile            # Instructions for building the Docker image
├── README.md             # This file
├── app.py                # Simple Gradio app (potentially unused)
├── main.py               # Simple main script (potentially unused)
├── prediction_plot.png   # Example output image
├── requirements.txt      # Python dependencies
├── run_docker.py         # Script to automate Docker build and run
└── trader.py             # Main Gradio application script for stock prediction
```


