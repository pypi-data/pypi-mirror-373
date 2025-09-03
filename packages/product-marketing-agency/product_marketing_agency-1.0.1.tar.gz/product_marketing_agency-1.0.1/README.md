# Product Marketing Agency

![Product Marketing Agency](assets/pms2.jpeg)

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/swarms-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)

A comprehensive multi-agent system for generating professional product marketing images and content using the Swarms framework.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Framework](https://img.shields.io/badge/Framework-Swarms-orange.svg)

## Quick Start

### Installation

```bash
git clone https://github.com/The-Swarm-Corporation/Product-Marketing-Agency.git
cd Product-Marketing-Agency
pip install -r requirements.txt
```

### Setup Environment

```bash
export OPENAI_API_KEY="your-openai-api-key"
# or
export GEMINI_API_KEY="your-gemini-api-key"
```

### Basic Usage

```python
from product_marketing_agency.main import ProductMarketingAgency

# Initialize the agency
agency = ProductMarketingAgency(model_name="gpt-4o")

# Create product profile
product_data = {
    "product_name": "Premium Wireless Headphones",
    "category": "Electronics",
    "key_features": ["Noise cancellation", "40-hour battery", "Premium sound"],
    "accessories": ["Charging cable", "Carrying case", "Audio cable"],
    "objectives": ["Showcase premium quality", "Highlight features"],
    "suggested_image_types": [1, 2, 3, 7, 9]
}

# Generate marketing campaign
agency.create_product_profile(product_data)
results = agency.run_campaign()

print(f"Generated {results['images_generated']} marketing images")
```

### Run Interactive Mode

```bash
python product_marketing_agency/main.py
```

## Features

### 10 Specialized Image Types
- **Master Product Shot**: Hero images showcasing the main product
- **What's in the Box Flat Lay**: Unboxing and contents display
- **Extreme Macro Detail**: Close-up shots highlighting craftsmanship
- **Color/Style Variations**: Product variants and options
- **On-Foot Size Comparisons**: Scale and sizing demonstrations
- **Add a Model Two-Image Composite**: Lifestyle modeling shots
- **Lifestyle Action Shot**: Products in real-world usage
- **UGC Style Photos**: User-generated content aesthetic
- **Negative Space Banner**: Clean promotional banners
- **Shop the Look Flat Lay**: Complete styling and accessory layouts

### Multi-Agent Architecture
- Specialized agents for each image type
- Coordinated multi-agent workflows
- Rich interactive terminal interface
- Campaign reporting and analytics
- Batch processing capabilities

## Documentation

For detailed documentation, examples, and advanced usage, see [docs/README.md](docs/README.md).

## Support

- Issues: [GitHub Issues](https://github.com/The-Swarm-Corporation/Product-Marketing-Agency/issues)
- Community: [Discord Server](https://discord.gg/swarms-999382051935506503)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

Made by The Swarm Corporation