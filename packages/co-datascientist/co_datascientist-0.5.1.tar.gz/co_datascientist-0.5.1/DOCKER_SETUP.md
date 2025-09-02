# 🔧 Docker Setup Guide (For Maintainers)

This guide explains how to set up automated Docker image builds that sync with your PyPI releases.

## 🎯 How It Works

1. **You release a new version** using `uv build` and publish to PyPI
2. **GitHub Actions detects the release** and automatically builds a new Docker image
3. **Docker image is pushed** to Docker Hub with both `latest` and version-specific tags
4. **Users get the update** automatically when they pull the latest image

## 🛠️ Setup Steps

### 1. Create Docker Hub Account & Repository

1. Go to [Docker Hub](https://hub.docker.com/)
2. Create account (if you don't have one)
3. Create a new repository: `your-username/co-datascientist`
4. Set it to public (so users can pull it easily)

### 2. Generate Docker Hub Access Token

1. Go to Docker Hub → Account Settings → Security
2. Click "New Access Token"
3. Name it "GitHub Actions"
4. Copy the token (you'll need it in step 3)

### 3. Add GitHub Secrets

In your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add these secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: The access token from step 2

### 4. Update the Workflow File

Edit `.github/workflows/docker-publish.yml` and replace:
```yaml
IMAGE_NAME: your-dockerhub-username/co-datascientist
```

With your actual Docker Hub username:
```yaml
IMAGE_NAME: tropifloai/co-datascientist
```

### 5. Test the Setup

1. **Create a test release:**
   ```bash
   git tag v0.3.8-test
   git push origin v0.3.8-test
   gh release create v0.3.8-test --title "Test Release v0.3.8" --notes "Testing Docker automation"
   ```

2. **Check GitHub Actions:** Go to Actions tab and watch the build

3. **Verify Docker Hub:** Check that the image was pushed

4. **Test locally:**
   ```bash
   docker pull your-username/co-datascientist:0.3.8-test
   docker run -it your-username/co-datascientist:0.3.8-test co-datascientist --help
   ```

## 🔄 Release Process

Your new release process becomes super simple:

1. **Update version** in `pyproject.toml`
2. **Build and publish** to PyPI:
   ```bash
   uv build
   uv publish
   ```
3. **Create GitHub release:**
   ```bash
   git tag v0.3.8
   git push origin v0.3.8
   gh release create v0.3.8 --title "Release v0.3.8" --notes "New features and improvements"
   ```
4. **Docker image builds automatically!** ✨

## 🏷️ Version Tagging Strategy

The automation creates these Docker tags:
- `latest` - Always points to the newest release
- `0.3.8` - Specific version tags for reproducibility

## 🚨 Troubleshooting

### Build Fails
- Check GitHub Actions logs
- Verify Docker Hub credentials
- Ensure PyPI package is available

### Image Not Updated
- Check if the release triggered the workflow
- Verify the tag format (should be `v0.3.8` or `0.3.8`)
- Check GitHub Actions permissions

### Users Can't Pull
- Ensure Docker Hub repository is public
- Check the image name is correct
- Verify the image was actually pushed

## 💡 Pro Tips

1. **Test releases** in a separate repository first
2. **Use semantic versioning** (v1.2.3 format)
3. **Write good release notes** - they become part of your Docker Hub description
4. **Monitor build times** - they usually take 2-5 minutes
5. **Consider multi-platform builds** - the workflow builds for both Intel and ARM (Apple Silicon)

That's it! Your Docker images will now stay perfectly in sync with your PyPI releases! 🎉 