# 🐳 Docker Version of Co-DataScientist

This is a super simple way to use Co-DataScientist without installing anything on your computer except Docker!

## 🚀 Quick Start (3 steps!)

### Step 1: Pull the Docker image
```bash
docker pull your-dockerhub-username/co-datascientist
```

### Step 2: Set up your API token
```bash
docker run -it your-dockerhub-username/co-datascientist co-datascientist set-token
```
*This will ask you for your API key - just paste it in!*

### Step 3: Run on your ML script
```bash
docker run -v /path/to/your/ml/project:/workspace -it your-dockerhub-username/co-datascientist co-datascientist run your_script.py
```

## 📁 What's happening here?

Think of Docker like a **magic box** that contains:
- ✅ Python (the right version)
- ✅ Co-DataScientist tool (already installed)
- ✅ All the dependencies (no conflicts!)

The `-v /path/to/your/ml/project:/workspace` part is like **connecting a cable** between:
- Your computer's folder (where your ML scripts live)
- The magic box's workspace

So the tool can read your files and improve your models!

## 🛠️ All Available Commands

```bash
# Check your usage status
docker run -it your-dockerhub-username/co-datascientist co-datascientist status

# See your costs
docker run -it your-dockerhub-username/co-datascientist co-datascientist costs

# Set up OpenAI key for unlimited usage
docker run -it your-dockerhub-username/co-datascientist co-datascientist openai-key

# Run the optimization on your script
docker run -v $(pwd):/workspace -it your-dockerhub-username/co-datascientist co-datascientist run my_model.py
```

## 💡 Pro Tips

1. **Always use `-v $(pwd):/workspace`** when you want to work with files in your current directory
2. **Use `-it`** to make it interactive (so you can type responses)
3. **Your data never leaves your computer** - it just goes into the Docker container temporarily!

## 🔧 Building the Docker Image (for maintainers)

```bash
# Build the image
docker build -t your-dockerhub-username/co-datascientist .

# Push to Docker Hub
docker push your-dockerhub-username/co-datascientist
```

That's it! No complex setup, no Python environment issues, just pure magic! ✨ 