# Image Generation Providers

The D&D Image Generator supports multiple AI image generation providers through a modular architecture.

## Supported Providers

### 1. DALL-E 3 (OpenAI)
- **Status**: ✅ Fully implemented
- **API**: OpenAI Images API
- **Cost**: ~$0.04 per image (standard quality, 1024x1024)
- **Pros**: Easy to use, good quality, reliable
- **Cons**: Doesn't follow negative prompts well, adds unwanted UI elements

### 2. Stability.ai (Stable Diffusion XL)
- **Status**: ✅ Fully implemented
- **API**: Stability.ai REST API
- **Cost**: ~$0.01 per image
- **Pros**: Better at following negative prompts, cheaper, faster
- **Cons**: Requires more prompt engineering

---

## Switching Providers

### Step 1: Get API Key

**For DALL-E:**
```bash
# Get key from: https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-..."
```

**For Stability.ai:**
```bash
# Get key from: https://platform.stability.ai/
export STABILITY_API_KEY="sk-..."
```

### Step 2: Update .env File

```bash
# Copy example if you haven't already
cp .env.example .env

# Edit .env and add your key(s)
OPENAI_API_KEY=sk-your-key-here
STABILITY_API_KEY=sk-your-key-here
```

### Step 3: Update config.yaml

```yaml
image_generation:
  # Change this line to switch providers
  provider: "stability-ai"  # or "dall-e"
```

### Step 4: Test

```bash
# Dry run to verify configuration
python -m src.cli --entity-type races --limit 1 --dry-run

# Generate a test image
python -m src.cli --entity-type races --slug elf
```

---

## Provider Configuration

### DALL-E Configuration

```yaml
image_generation:
  provider: "dall-e"

  dall-e:
    api_key: "${OPENAI_API_KEY}"
    model: "dall-e-3"          # dall-e-2 or dall-e-3
    size: "1024x1024"          # 256x256, 512x512, 1024x1024
    quality: "standard"        # standard or hd (hd is 2x cost)
    style: "vivid"             # vivid or natural
    max_retries: 3
    retry_delay: 5
```

### Stability.ai Configuration

```yaml
image_generation:
  provider: "stability-ai"

  stability-ai:
    api_key: "${STABILITY_API_KEY}"
    model: "stable-diffusion-xl-1024-v1-0"
    width: 1024
    height: 1024
    cfg_scale: 7               # 1-35, how strictly to follow prompt
    steps: 30                  # 10-50, more = higher quality but slower
    samples: 1                 # Number of images per generation
    max_retries: 3
    retry_delay: 5
    # Global negative prompt (what to avoid)
    negative_prompt: "UI elements, grids, color palettes, text, diagrams, frames, borders"
```

---

## Adding New Providers

To add support for another provider (e.g., Midjourney, Leonardo.ai):

### 1. Create Provider Class

Create `src/generator/providers/yourprovider_provider.py`:

```python
from .base import ImageProvider

class YourProvider(ImageProvider):
    def __init__(self, config):
        super().__init__(config)
        # Initialize your provider

    def generate(self, prompt: str) -> str:
        # Call your provider's API
        # Return image URL or data URL
        pass

    def get_provider_name(self) -> str:
        return "your-provider"
```

### 2. Register in Factory

Edit `src/generator/providers/factory.py`:

```python
from .yourprovider_provider import YourProvider

def create_provider(provider_type: str, config: Dict[str, Any]) -> ImageProvider:
    providers = {
        "dall-e": DalleProvider,
        "stability-ai": StabilityProvider,
        "your-provider": YourProvider,  # Add here
    }
    # ...
```

### 3. Add to config.yaml

```yaml
image_generation:
  provider: "your-provider"

  your-provider:
    api_key: "${YOUR_PROVIDER_API_KEY}"
    # Your provider-specific settings
```

---

## Comparison

| Feature | DALL-E 3 | Stability.ai |
|---------|----------|--------------|
| Cost/image | $0.04 | $0.01 |
| Quality | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Speed | ~15s | ~10s |
| Negative prompts | ❌ Poor | ✅ Good |
| Consistency | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Setup complexity | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐ Easy |

---

## Troubleshooting

### "Unknown provider type" error
- Check `config.yaml` → `image_generation.provider` matches a supported provider
- Supported: `dall-e`, `stability-ai`

### "API key not found" error
- Verify `.env` file has the correct key
- Check environment variable name matches config (e.g., `STABILITY_API_KEY`)
- Restart terminal after updating `.env`

### Provider-specific errors

**DALL-E:**
- Rate limits: Wait 60s between large batches
- Content policy: DALL-E may refuse certain prompts

**Stability.ai:**
- Invalid model: Check model name in config
- 402 Payment Required: Add credits to your Stability account
- Timeout: Increase `steps` parameter for complex images

---

## Current Status

- ✅ DALL-E 3 - Fully tested
- ✅ Stability.ai - Implemented, ready to test
- 📋 Midjourney - Planned (waiting for official API)
- 📋 Replicate - Planned
