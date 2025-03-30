import subprocess
import time
from pathlib import Path

def run_command(command, cwd=None):
    """
    Executes a shell command and streams the output in real-time.
    
    Args:
        command (list): The command to run as a list of strings.
        cwd (str or Path, optional): The working directory to execute the command in.

    Returns:
        int: The exit code of the command (0 for success, non-zero for failure).
    """
    print(f"Running: {' '.join(command)}")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,  
        cwd=cwd  
    )
    
    for line in process.stdout:
        print(line.strip())

    process.wait()
    return process.returncode  

def check_docker():
    """
    Checks if Docker is installed and accessible.

    Returns:
        bool: True if Docker is installed, False otherwise.
    """
    try:
        subprocess.run(
            ["docker", "--version"], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return True  
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: Docker is not installed or not in PATH.")
        return False  

def main():
    """
    Main function to build and run the Docker container for the application.

    Features:
    - Ensures Docker is running
    - Builds the Docker image
    - Stops and removes any existing container
    - Runs the container with an automatic **restart policy** to keep it running
    """

    # Step 1: Check if Docker is installed
    if not check_docker():
        return 1  

    # Step 2: Define the base directory where this script is located
    base_dir = Path(__file__).parent.absolute()
    
    # Step 3: Check if a .env file exists for environment variables
    env_file = base_dir / ".env"
    env_args = []  

    if env_file.exists():
        print(f"Using environment file: {env_file}")
        env_args = ["--env-file", str(env_file)]  
    else:
        print("No .env file found. Continuing without environment variables.")

    # Step 4: Build the Docker image
    print("\n=== Building the Docker image ===")
    if True:
        if run_command(["docker", "build", "-t", "move-app:latest", "."], cwd=base_dir) != 0:
            print("Error: Failed to build the Docker image.")
            return 1  
    else: 
        if run_command(["docker", "build", "--no-cache", "-t", "move-app:latest", "."], cwd=base_dir) != 0:
            print("Error: Failed to build the Docker image.")
            return 1


    # Step 5: Stop and remove any existing container before running a new one
    try:
        result = subprocess.run(
            ["docker", "ps", "-q", "--filter", "name=move-app-container"],
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print("\n=== Stopping existing container ===")
            run_command(["docker", "stop", "move-app-container"])
            run_command(["docker", "rm", "move-app-container"])
    
    except subprocess.SubprocessError:
        pass  

    # Step 6: Run the container with an automatic restart policy
    print("\\nn=== Starting the container with auto-restart ===\n\n")

    cmd = [
        "docker", "run", "-d",  
        "--name", "move-app-container",  
        "-p", "7862:7862",  
        "-v", "/root/move_data:/workspace/move_data",
        "--restart", "unless-stopped",  
        "--add-host", "host.docker.internal:host-gateway",
    ]
           
    # Add environment variable arguments if a .env file exists
    if env_args:
        print("\n===  Adding environment variable arguments ===\n")
        cmd.extend(env_args)

    print("\n===  Docker Basics ===\n")
    print("1. docker ps => List running containers (Example: docker ps)")
    print("2. docker ps -a => List all containers (Example: docker ps -a)")
    print("3. docker logs move-app-container => View container logs (Example: docker logs move-app-container)")
    print("4. docker exec -it move-app-container /bin/bash => Open a shell in the container (Example: docker exec -it move-app-container /bin/bash)")
    print("5. docker build -t move-app:latest . => Build an image (Example: docker build -t move-app:latest .)")
    print("6. docker run -p 7860:7860 move-app:latest => Run container with port mapping (Example: docker run -p 7860:7860 move-app:latest)")
    print("7. docker stop move-app-container => Stop the container (Example: docker stop move-app-container)")
    print("8. docker rm move-app-container => Remove the container (Example: docker rm move-app-container)")
    print("9. docker rmi move-app:latest => Remove the image (Example: docker rmi move-app:latest)\n\n")

    # Specify the Docker image to run
    cmd.append("move-app:latest")

    # Execute the Docker run command
    if run_command(cmd) != 0:
        print("Error: Failed to start the container.")
        return 1  

    # Step 7: Wait for a short time to ensure the container is running
    time.sleep(2)
    
    # Step 8: Print success message with instructions
    print("\n=== Application is now running and will auto-restart if it crashes! ===")
    print("-> Access it at: http://localhost:7862")
    print("\nTo manually stop the container, run:")
    print("   docker stop move-app-container && docker rm move-app-container")

    return 0  

if __name__ == "__main__":
    exit(main())