#!/bin/bash

# Co-DataScientist Docker Runner
# Makes it super easy to run the Docker version!

IMAGE_NAME="tropifloai/co-datascientist"

# Function to show usage
show_usage() {
    echo "🐳 Co-DataScientist Docker Runner"
    echo ""
    echo "Usage:"
    echo "  ./run-docker.sh <command> [arguments]"
    echo ""
    echo "Examples:"
    echo "  ./run-docker.sh set-token              # Set up your API key"
    echo "  ./run-docker.sh run my_script.py       # Optimize your ML script"
    echo "  ./run-docker.sh status                 # Check usage status"
    echo "  ./run-docker.sh costs                  # Check costs"
    echo "  ./run-docker.sh openai-key             # Set OpenAI key"
    echo ""
    echo "The script automatically mounts your current directory to the container!"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Show usage if no arguments
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Check if the image exists, if not suggest pulling it
if ! docker image inspect $IMAGE_NAME &> /dev/null; then
    echo "❌ Docker image '$IMAGE_NAME' not found."
    echo "💡 Please run: docker pull $IMAGE_NAME"
    echo "   Or build it locally: docker build -t $IMAGE_NAME ."
    exit 1
fi

# Run the command with current directory mounted
echo "🚀 Running co-datascientist $@ in Docker..."
docker run -v $(pwd):/workspace -it $IMAGE_NAME co-datascientist "$@" 