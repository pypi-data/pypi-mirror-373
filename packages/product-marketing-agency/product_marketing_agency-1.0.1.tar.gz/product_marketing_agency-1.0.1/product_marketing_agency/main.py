"""
Product Marketing Agency - Multi-Agent System
A comprehensive marketing system using the swarms framework for generating
various types of product marketing images and content.

Version: 1.0.0
"""

import json
import os
import time
import uuid
import logging
import shutil
import base64
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from swarms import Agent

# swarms framework handles base64 image processing automatically

# Rich library imports for enhanced UI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
)
from rich.text import Text
from rich.align import Align
from rich.syntax import Syntax
from rich.status import Status
from rich.prompt import Prompt, Confirm
from rich import box

# Initialize Rich console
console = Console()


class ImageType(Enum):
    """Available marketing image types - Exact 10 types as specified"""

    MASTER_PRODUCT_SHOT = 1
    WHATS_IN_THE_BOX_FLAT_LAY = 2
    EXTREME_MACRO_DETAIL = 3
    COLOR_STYLE_VARIATIONS = 4
    ON_FOOT_SIZE_COMPARISONS = 5
    ADD_A_MODEL_TWO_IMAGE_COMPOSITE = 6
    LIFESTYLE_ACTION_SHOT = 7
    UGC_STYLE_PHOTOS = 8
    NEGATIVE_SPACE_BANNER = 9
    SHOP_THE_LOOK_FLAT_LAY = 10


@dataclass
class ProductProfile:
    """Product information structure - matches exact JSON profile requirements"""

    product_name: str
    category: str
    key_features: List[str]
    accessories: List[str]
    objectives: List[str]
    suggested_image_types: List[
        int
    ]  # Array of numbers matching ImageType enum values
    product_id: str = None
    master_image_path: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.strftime("%Y%m%d_%H%M%S")
        if self.product_id is None:
            self.product_id = str(uuid.uuid4())


@dataclass
class MarketingJob:
    """Marketing job request structure"""

    job_id: str
    product_profile: ProductProfile
    image_type: ImageType
    custom_requirements: str = ""
    output_path: Optional[str] = None
    status: str = "pending"
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.strftime("%Y%m%d_%H%M%S")


class ProductMarketingAgency:
    """
    Multi-Agent Product Marketing System
    Orchestrates specialized agents to create comprehensive marketing materials
    """

    def __init__(
        self,
        save_directory: str = "./marketing_outputs",
        model_name: str = "gemini/gemini-2.5-flash-image-preview",
        enable_logging: bool = True,
    ):
        """
        Initialize the Product Marketing Agency with specialized agents

        Args:
            save_directory: Directory for storing outputs and state
            model_name: LLM model to use for agents
            enable_logging: Enable detailed logging
        """
        self.save_directory = Path(save_directory)
        self.model_name = model_name
        self.master_images = {}  # Store master image references
        self.product_profiles = {}  # Store product profiles
        self.active_jobs = {}  # Track active marketing jobs

        # Create directory structure
        self._setup_directories()

        # Setup logging
        if enable_logging:
            self._setup_logging()

        # Initialize specialized agents
        self._initialize_agents()

        # Load prompt templates
        self._initialize_prompt_templates()

    def _setup_directories(self):
        """Create organized directory structure"""
        directories = [
            self.save_directory,
            self.save_directory / "products",
            self.save_directory / "jobs",
            self.save_directory / "outputs",
            self.save_directory / "master_images",
            self.save_directory / "logs",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self):
        """Configure logging system"""
        log_file = (
            self.save_directory
            / "logs"
            / f"marketing_agency_{time.strftime('%Y%m%d')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
            ],
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info("Product Marketing Agency initialized")

    def _initialize_agents(self):
        """Initialize all specialized agents"""

        # Use text-only model for non-image-generation agents to prevent unwanted image generation
        text_model = "gemini/gemini-2.0-flash-exp"  # Text-only model

        # 1. Orchestrator Agent - Central coordinator
        self.orchestrator_agent = Agent(
            agent_name="Marketing-Orchestrator",
            agent_description="Central coordinator for marketing campaigns and workflow management",
            model_name=text_model,
            max_loops=1,
            dynamic_temperature_enabled=True,
            dynamic_context_window=True,
            retry_interval=2,
        )

        # 2. Product Interpreter Agent - Analyzes products and creates profiles
        self.product_interpreter_agent = Agent(
            agent_name="Product-Interpreter",
            agent_description="Analyzes product information and creates comprehensive marketing profiles",
            model_name=text_model,
            max_loops=1,
            dynamic_temperature_enabled=True,
            dynamic_context_window=True,
            retry_interval=2,
        )

        # 3. Image Type Selector Agent - Guides image type selection (TEXT ONLY!)
        self.image_selector_agent = Agent(
            agent_name="Image-Type-Selector",
            agent_description="Returns ONLY numbers for image type selection - no image generation",
            model_name=text_model,
            max_loops=1,
            dynamic_temperature_enabled=True,
            dynamic_context_window=True,
            retry_interval=2,
        )

        # 4. Prompt Generator Agent - Creates customized prompts
        self.prompt_generator_agent = Agent(
            agent_name="Prompt-Generator",
            agent_description="Generates highly customized prompts for marketing image creation",
            model_name=text_model,
            max_loops=1,
            dynamic_temperature_enabled=True,
            dynamic_context_window=True,
            retry_interval=2,
        )

        # 5. Image Generation Agent - Creates the actual images (ONLY THIS ONE GENERATES IMAGES)
        self.image_generation_agent = Agent(
            agent_name="Banana-Nano-Generator",
            agent_description="Specialized in creating high-quality marketing images using visual AI. Generates images directly without explanatory text.",
            model_name=self.model_name,  # Keep the multimodal model for actual image generation
            max_loops=1,
            dynamic_temperature_enabled=True,
            dynamic_context_window=True,
            retry_interval=2,
            system_prompt="You are an image generation AI. When given a prompt, generate the requested image immediately. Do not provide explanations, commentary, or descriptive text. Only generate the actual image output.",
        )

        # 6. Output Handler & Feedback Agent - Manages results and feedback
        self.output_handler_agent = Agent(
            agent_name="Output-Handler-Feedback",
            agent_description="Manages output delivery and processes user feedback for improvements",
            model_name=text_model,
            max_loops=1,
            dynamic_temperature_enabled=True,
            dynamic_context_window=True,
            retry_interval=2,
        )

    def _create_fresh_image_agent(self) -> Agent:
        """
        Create a fresh agent instance to prevent Google API caching issues
        Each agent gets a unique identity and session parameters
        """
        import random

        # Generate unique identifiers for this agent instance
        agent_uuid = str(uuid.uuid4())[:8]
        session_id = str(uuid.uuid4())

        # Force different temperature each time to ensure variety
        random_temp = 0.7 + (random.random() * 0.3)  # 0.7-1.0 range

        # Create system prompt with unique identity
        unique_system_prompt = (
            f"You are a fresh image generation AI instance #{agent_uuid}. "
            f"Session: {session_id}. Temperature: {random_temp:.3f}. "
            f"Generate unique, high-quality images immediately without any text explanations. "
            f"Each image must be completely different from any previous generations. "
            f"Do not provide conversational responses - only generate the requested image."
        )

        return Agent(
            agent_name=f"Fresh-Image-Generator-{agent_uuid}",
            agent_description=f"Unique image generation agent with session {session_id}",
            model_name=self.model_name,
            max_loops=1,
            dynamic_temperature_enabled=True,
            dynamic_context_window=True,
            retry_interval=2,
            temperature=random_temp,
            system_prompt=unique_system_prompt,
        )

    def _track_base64_globally(self, base64_data: str) -> bool:
        """
        Track base64 hashes across sessions to detect true duplicates
        Returns True if this base64 was seen before, False if it's unique
        """
        import hashlib

        # Create hash of the base64 content
        base64_content = base64_data.strip()
        if (
            "data:image" in base64_content
            and "base64," in base64_content
        ):
            # Extract just the base64 part for consistent hashing
            _, base64_content = base64_content.split("base64,", 1)

        base64_hash = hashlib.sha256(
            base64_content.encode()
        ).hexdigest()

        # Create tracking file path
        tracking_file = self.save_directory / "base64_tracking.json"

        # Load existing tracked hashes
        tracked_hashes = {}
        if tracking_file.exists():
            try:
                with open(tracking_file, "r") as f:
                    tracked_hashes = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(
                    f"Could not load base64 tracking file: {e}"
                )
                tracked_hashes = {}

        # Check if this hash was seen before
        current_time = time.time()
        if base64_hash in tracked_hashes:
            last_seen = tracked_hashes[base64_hash]
            self.logger.error(
                f"🚨 DUPLICATE BASE64 DETECTED! Hash: {base64_hash[:16]}..."
            )
            self.logger.error(
                f"   Previous generation: {time.ctime(last_seen)}"
            )
            self.logger.error(
                f"   Time difference: {current_time - last_seen:.2f} seconds"
            )
            return True

        # Store this hash with timestamp
        tracked_hashes[base64_hash] = current_time

        # Clean up old entries (keep only last 1000 to prevent file bloat)
        if len(tracked_hashes) > 1000:
            # Keep only the most recent 1000 entries
            sorted_hashes = sorted(
                tracked_hashes.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            tracked_hashes = dict(sorted_hashes[:1000])

        # Save updated tracking file
        try:
            with open(tracking_file, "w") as f:
                json.dump(tracked_hashes, f, indent=2)
        except IOError as e:
            self.logger.warning(
                f"Could not save base64 tracking file: {e}"
            )

        self.logger.info(
            f"✅ Unique base64 confirmed. Hash: {base64_hash[:16]}... (Total tracked: {len(tracked_hashes)})"
        )
        return False

    def _convert_base64_to_file(
        self, base64_data: str, output_dir: Path, filename_prefix: str
    ) -> Optional[str]:
        """
        Convert base64 image data to a saved image file

        Args:
            base64_data: Base64 encoded image data (with or without data URI prefix)
            output_dir: Directory to save the image
            filename_prefix: Prefix for the generated filename

        Returns:
            str: Path to the saved image file, or None if conversion failed
        """
        try:
            # Extract base64 data from data URI if present
            if base64_data.startswith("data:image"):
                # Format: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
                header, base64_content = base64_data.split(",", 1)
                # Extract image format from header
                format_match = re.search(r"data:image/(\w+)", header)
                image_format = (
                    format_match.group(1) if format_match else "png"
                )
            else:
                # Just raw base64 data
                base64_content = base64_data
                image_format = "png"  # Default format

            # Clean and fix base64 data for proper decoding
            base64_content = (
                base64_content.strip()
                .replace("\n", "")
                .replace(" ", "")
            )

            # Fix base64 padding if needed
            padding_needed = 4 - (len(base64_content) % 4)
            if padding_needed != 4:
                base64_content += "=" * padding_needed

            # Decode base64 data
            image_bytes = base64.b64decode(base64_content)

            # Generate filename - check if prefix already has timestamp and unique ID
            if (
                "_" in filename_prefix
                and len(filename_prefix.split("_")) >= 4
            ):
                # Filename prefix already contains timestamp and unique ID
                filename = f"{filename_prefix}.{image_format}"
            else:
                # Add timestamp and random suffix for legacy compatibility
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                random_suffix = str(uuid.uuid4())[:8]
                filename = f"{filename_prefix}_{timestamp}_{random_suffix}.{image_format}"

            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save image file
            output_path = output_dir / filename
            with open(output_path, "wb") as f:
                f.write(image_bytes)

            self.logger.info(
                f"Base64 image converted and saved to: {output_path}"
            )
            return str(output_path)

        except Exception as e:
            self.logger.error(
                f"Failed to convert base64 to image file: {str(e)}"
            )
            return None

    def _get_intelligent_image_suggestions(
        self, product_data: Dict[str, Any]
    ) -> List[int]:
        """
        Generate intelligent image type suggestions based on product category and features

        Args:
            product_data: Raw product information

        Returns:
            List[int]: Suggested image type numbers (1-10)
        """
        category = str(product_data.get("category", "")).lower()
        name = str(product_data.get("name", "")).lower()
        description = str(product_data.get("description", "")).lower()
        features = [
            str(f).lower() for f in product_data.get("features", [])
        ]

        # Combine all text for analysis
        all_text = (
            f"{category} {name} {description} {' '.join(features)}"
        )

        suggested_types = []

        # Electronics / Tech products
        if any(
            word in all_text
            for word in [
                "electronic",
                "tech",
                "smart",
                "digital",
                "wireless",
                "bluetooth",
                "app",
                "battery",
                "charging",
            ]
        ):
            suggested_types.extend(
                [1, 3, 7, 9]
            )  # MASTER_PRODUCT_SHOT, EXTREME_MACRO_DETAIL, LIFESTYLE_ACTION_SHOT, NEGATIVE_SPACE_BANNER

        # Fashion / Wearable products
        elif any(
            word in all_text
            for word in [
                "fashion",
                "clothing",
                "shoe",
                "sneaker",
                "watch",
                "jewelry",
                "accessory",
                "wearable",
            ]
        ):
            suggested_types.extend(
                [1, 4, 5, 7, 8]
            )  # Add COLOR_VARIATIONS and ON_FOOT_SIZE_COMPARISONS

        # Food / Beverage products
        elif any(
            word in all_text
            for word in [
                "food",
                "drink",
                "beverage",
                "nutrition",
                "organic",
                "healthy",
                "recipe",
            ]
        ):
            suggested_types.extend(
                [1, 2, 8, 10]
            )  # MASTER_PRODUCT_SHOT, WHATS_IN_THE_BOX, UGC_STYLE, SHOP_THE_LOOK

        # Home / Office products
        elif any(
            word in all_text
            for word in [
                "home",
                "office",
                "desk",
                "furniture",
                "kitchen",
                "decor",
                "organization",
            ]
        ):
            suggested_types.extend(
                [1, 6, 7, 9]
            )  # Include MODEL_COMPOSITE for lifestyle context

        # Fitness / Sports products
        elif any(
            word in all_text
            for word in [
                "fitness",
                "sport",
                "exercise",
                "workout",
                "athletic",
                "training",
                "gym",
            ]
        ):
            suggested_types.extend(
                [1, 5, 7, 8]
            )  # Focus on action and size comparisons

        # Beauty / Personal Care
        elif any(
            word in all_text
            for word in [
                "beauty",
                "cosmetic",
                "skincare",
                "personal",
                "care",
                "makeup",
                "fragrance",
            ]
        ):
            suggested_types.extend(
                [1, 3, 4, 8]
            )  # Detail shots and variations important

        # Automotive / Transportation
        elif any(
            word in all_text
            for word in [
                "car",
                "automotive",
                "vehicle",
                "bike",
                "transport",
                "motor",
            ]
        ):
            suggested_types.extend(
                [1, 3, 6, 7]
            )  # Product shots, details, composites, action

        # Default fallback for unknown categories
        if not suggested_types:
            suggested_types = [
                1,
                7,
                9,
            ]  # Conservative default: MASTER_PRODUCT_SHOT, LIFESTYLE_ACTION_SHOT, NEGATIVE_SPACE_BANNER

        # Remove duplicates and limit to 4-6 suggestions
        unique_suggestions = list(
            dict.fromkeys(suggested_types)
        )  # Preserves order, removes duplicates

        # Limit to 4-6 suggestions for better user experience
        final_suggestions = (
            unique_suggestions[:6]
            if len(unique_suggestions) > 6
            else unique_suggestions
        )

        self.logger.info(
            f"Generated intelligent suggestions for category '{category}': {final_suggestions}"
        )
        return final_suggestions

    def _get_image_type_specific_params(
        self, product_profile: ProductProfile, image_type: ImageType
    ) -> Dict[str, str]:
        """
        Generate image-type-specific parameters with enhanced variability and negative prompts

        Args:
            product_profile: Product information
            image_type: Specific image type being generated

        Returns:
            Dict[str, str]: Image-type-specific parameters with variability and negative prompts
        """
        import random

        base_params = {
            "product": product_profile.product_name,
            "product_description": (
                f"{product_profile.product_name} - {product_profile.category}"
            ),
            "type_specific_params": "",  # Will be populated per type
        }

        if image_type == ImageType.MASTER_PRODUCT_SHOT:
            # Add variability with random selections
            backgrounds = [
                "pristine white cyclorama",
                "gradient infinity cove",
                "brushed aluminum surface",
                "matte black studio",
            ]
            lighting_setups = [
                "three-point studio lighting with softboxes",
                "rim lighting with key light",
                "butterfly lighting setup",
                "split lighting with reflectors",
            ]
            angles = [
                "elevated 45-degree hero",
                "straight-on eye level",
                "low angle dramatic",
                "three-quarter view",
            ]
            atmospheres = [
                "luxury retail showroom",
                "high-end gallery space",
                "premium boutique setting",
                "flagship store display",
            ]

            return {
                **base_params,
                "background_surface": random.choice(backgrounds),
                "lighting_setup": random.choice(lighting_setups),
                "lighting_purpose": (
                    "sculpting dimension and highlighting premium materials"
                ),
                "angle_type": random.choice(angles),
                "specific_feature": (
                    ", ".join(product_profile.key_features[:2])
                    if product_profile.key_features
                    else "premium build quality"
                ),
                "key_detail": (
                    product_profile.key_features[0]
                    if product_profile.key_features
                    else "signature design elements"
                ),
                "atmosphere_description": random.choice(atmospheres),
                "style_reference": random.choice(
                    [
                        "Apple product photography",
                        "Leica camera aesthetics",
                        "Bang & Olufsen style",
                    ]
                ),
                "camera_equipment": random.choice(
                    [
                        "Hasselblad H6D-100c",
                        "Phase One XF IQ4",
                        "Canon 5DS R with 100mm macro",
                    ]
                ),
                "post_production": random.choice(
                    [
                        "subtle vignetting",
                        "micro-contrast enhancement",
                        "color grading for depth",
                    ]
                ),
                "negative_prompt": (
                    "Avoid: blurry edges, cartoonish rendering, flat lighting, cluttered background, amateur photography, stock photo look, oversaturated colors, visible dust or artifacts"
                ),
            }

        elif image_type == ImageType.LIFESTYLE_ACTION_SHOT:
            activities = [
                "urban street performance",
                "outdoor adventure expedition",
                "intense workout session",
                "creative collaboration",
                "competitive sports moment",
            ]
            environments = [
                "bustling city streets",
                "mountain trail at sunrise",
                "industrial urban landscape",
                "beachfront at sunset",
                "dynamic studio space",
            ]
            techniques = [
                "motion blur with sharp subject",
                "freeze-frame action",
                "panning shot technique",
                "high-speed capture",
                "dynamic composition",
            ]
            moods = [
                "energetic and vibrant",
                "aspirational and bold",
                "raw and authentic",
                "inspiring and uplifting",
            ]

            return {
                **base_params,
                "activity_context": random.choice(activities),
                "model_demographic": random.choice(
                    [
                        "professional athletes",
                        "creative professionals",
                        "adventure enthusiasts",
                        "urban explorers",
                    ]
                ),
                "action_verb": random.choice(
                    [
                        "performing",
                        "competing",
                        "creating",
                        "exploring",
                        "challenging limits with",
                    ]
                ),
                "camera_technique": random.choice(techniques),
                "environment_description": random.choice(
                    environments
                ),
                "lighting_condition": random.choice(
                    [
                        "golden hour",
                        "blue hour",
                        "dramatic storm light",
                        "high-contrast midday",
                    ]
                ),
                "mood_atmosphere": random.choice(moods),
                "focus_technique": random.choice(
                    [
                        "selective focus",
                        "zone focusing",
                        "continuous AF tracking",
                    ]
                ),
                "focal_point": "the product in active use",
                "color_palette": random.choice(
                    [
                        "vibrant and energetic",
                        "moody and dramatic",
                        "natural and earthy",
                    ]
                ),
                "photography_style": random.choice(
                    [
                        "documentary",
                        "editorial",
                        "cinematic",
                        "reportage",
                    ]
                ),
                "negative_prompt": (
                    "Avoid: static poses, studio lighting, plain backgrounds, stock photo appearance, unnatural movements, overprocessed look, fake motion blur"
                ),
            }

        elif image_type == ImageType.NEGATIVE_SPACE_BANNER:
            compositions = [
                "rule of thirds",
                "golden ratio",
                "diagonal balance",
                "asymmetric harmony",
            ]
            color_schemes = [
                "monochromatic minimal",
                "dual-tone contrast",
                "gradient subtle",
                "pure white space",
            ]
            placements = [
                "lower left third",
                "upper right corner",
                "centered bottom",
                "offset diagonal",
            ]

            return {
                **base_params,
                "composition_rule": random.choice(compositions),
                "color_scheme": random.choice(color_schemes),
                "space_percentage": random.choice(
                    ["20%", "25%", "30%"]
                ),
                "product_position": random.choice(placements),
                "text_space_location": (
                    "strategic text placement areas"
                ),
                "brand_aesthetic": random.choice(
                    [
                        "Swiss minimalism",
                        "Scandinavian design",
                        "Japanese zen aesthetics",
                    ]
                ),
                "shadow_treatment": random.choice(
                    [
                        "soft drop shadow",
                        "no shadow pure float",
                        "subtle ground shadow",
                    ]
                ),
                "design_principle": random.choice(
                    [
                        "less is more",
                        "form follows function",
                        "negative space as design element",
                    ]
                ),
                "negative_prompt": (
                    "Avoid: cluttered composition, busy background, multiple products, decorative elements, text overlays, logos, complex patterns"
                ),
            }

        elif image_type == ImageType.WHATS_IN_THE_BOX_FLAT_LAY:
            arrangements = [
                "geometric grid",
                "organic flow",
                "radial burst",
                "diagonal cascade",
                "symmetrical balance",
            ]
            surfaces = [
                "marble texture",
                "wood grain surface",
                "concrete industrial",
                "pristine white",
                "dark matte backdrop",
            ]
            lighting = [
                "soft overhead diffusion",
                "directional window light",
                "even studio lighting",
                "subtle gradient lighting",
            ]
            moods = [
                "premium unboxing experience",
                "minimalist presentation",
                "luxurious reveal",
                "organized perfection",
            ]

            return {
                **base_params,
                "item_1": (
                    product_profile.accessories[0]
                    if len(product_profile.accessories) > 0
                    else "instruction manual"
                ),
                "item_2": (
                    product_profile.accessories[1]
                    if len(product_profile.accessories) > 1
                    else "warranty card"
                ),
                "item_3": (
                    product_profile.accessories[2]
                    if len(product_profile.accessories) > 2
                    else "premium cable"
                ),
                "arrangement_style": random.choice(arrangements),
                "surface_description": random.choice(surfaces),
                "lighting_condition": random.choice(lighting),
                "mood_descriptor": random.choice(moods),
                "shadow_style": random.choice(
                    [
                        "soft natural shadows",
                        "minimal shadow presence",
                        "dramatic shadow play",
                    ]
                ),
                "negative_prompt": (
                    "Avoid: messy arrangement, overlapping items, perspective distortion, harsh shadows, cluttered composition, random placement"
                ),
            }

        elif image_type == ImageType.UGC_STYLE_PHOTOS:
            contexts = [
                "coffee shop moment",
                "home office setup",
                "weekend adventure",
                "daily commute",
                "friend gathering",
            ]
            filters = [
                "VSCO filter",
                "Instagram Valencia",
                "natural no filter",
                "slight fade effect",
                "warm vintage tone",
            ]
            platforms = [
                "Instagram feed",
                "TikTok video still",
                "Twitter post",
                "Pinterest save",
                "Snapchat story",
            ]

            return {
                **base_params,
                "phone_camera_style": random.choice(
                    [
                        "iPhone portrait mode",
                        "Android wide angle",
                        "front camera selfie style",
                        "quick snapshot",
                    ]
                ),
                "natural_lighting": random.choice(
                    [
                        "window light",
                        "outdoor shade",
                        "indoor ambient",
                        "mixed lighting",
                    ]
                ),
                "everyday_context": random.choice(contexts),
                "casual_styling": "spontaneous and unposed",
                "filter_effect": random.choice(filters),
                "social_elements": "authentic user-generated vibe",
                "social_media_platform": random.choice(platforms),
                "aspect_ratio": random.choice(
                    [
                        "1:1 square",
                        "4:5 portrait",
                        "9:16 stories",
                        "16:9 landscape",
                    ]
                ),
                "negative_prompt": (
                    "Avoid: professional photography, studio setup, perfect composition, commercial polish, stock photo look, staged scenarios"
                ),
            }

        elif image_type == ImageType.EXTREME_MACRO_DETAIL:
            technical_specs = [
                "100mm macro lens at 1:1",
                "focus stacking technique",
                "extension tubes setup",
                "microscope objective lens",
            ]
            styles = [
                "scientific documentation",
                "artistic abstract",
                "technical precision",
                "luxury detail showcase",
            ]

            return {
                **base_params,
                "detail_feature": (
                    product_profile.key_features[0]
                    if product_profile.key_features
                    else "signature texture"
                ),
                "texture_material": random.choice(
                    [
                        "woven carbon fiber",
                        "brushed metal grain",
                        "leather texture",
                        "technical fabric weave",
                    ]
                ),
                "quality_aspect": random.choice(
                    [
                        "handcrafted precision",
                        "engineering excellence",
                        "material innovation",
                        "artisan craftsmanship",
                    ]
                ),
                "focus_point": "microscopic detail revelation",
                "technical_description": random.choice(
                    technical_specs
                ),
                "lens_type": random.choice(
                    [
                        "100mm macro",
                        "180mm macro",
                        "MP-E 65mm",
                        "90mm macro",
                    ]
                ),
                "dof_description": (
                    "razor-thin depth of field with dreamy bokeh"
                ),
                "style_description": random.choice(styles),
                "negative_prompt": (
                    "Avoid: full product view, wide angle, deep depth of field, context shots, lifestyle elements, multiple focus points"
                ),
            }

        elif image_type == ImageType.COLOR_STYLE_VARIATIONS:
            layouts = [
                "clean grid matrix",
                "diagonal lineup",
                "circular arrangement",
                "stepped cascade",
                "horizontal parade",
            ]
            backgrounds = [
                "gradient backdrop",
                "color-matched backgrounds",
                "neutral gray studio",
                "white infinity",
                "complementary color blocks",
            ]

            return {
                **base_params,
                "variation_count": random.choice(
                    ["3", "4", "5", "6"]
                ),
                "variation_type": random.choice(
                    [
                        "colorways",
                        "material finishes",
                        "style options",
                        "seasonal variants",
                    ]
                ),
                "layout_style": random.choice(layouts),
                "arrangement_description": (
                    "systematic progression showing range"
                ),
                "background_type": random.choice(backgrounds),
                "lighting_consistency": (
                    "uniform lighting across all variants"
                ),
                "photography_style": random.choice(
                    [
                        "catalog precision",
                        "editorial layout",
                        "e-commerce standard",
                    ]
                ),
                "composition_rule": (
                    "balanced visual weight distribution"
                ),
                "negative_prompt": (
                    "Avoid: inconsistent angles, varying scales, misaligned products, color cast differences, shadowing variations"
                ),
            }

        elif image_type == ImageType.ON_FOOT_SIZE_COMPARISONS:
            comparison_types = [
                "side-by-side comparison",
                "overlay demonstration",
                "progression sequence",
                "reference grid",
            ]
            perspectives = [
                "eye level straight on",
                "45-degree angle",
                "top-down view",
                "profile silhouette",
            ]

            return {
                **base_params,
                "comparison_type": random.choice(comparison_types),
                "comparison_objects": random.choice(
                    [
                        "standard references",
                        "familiar objects",
                        "measurement tools",
                        "hand for scale",
                    ]
                ),
                "scale_demonstration": "clear size relationships",
                "measurement_indication": random.choice(
                    [
                        "ruler visible",
                        "grid background",
                        "size labels",
                        "dimensional callouts",
                    ]
                ),
                "camera_perspective": random.choice(perspectives),
                "lighting_setup": "even illumination for clarity",
                "detail_emphasis": "proportions and scale accuracy",
                "style_descriptor": random.choice(
                    [
                        "technical documentation",
                        "educational reference",
                        "comparison chart style",
                    ]
                ),
                "negative_prompt": (
                    "Avoid: perspective distortion, misleading scales, cluttered comparisons, inconsistent positioning"
                ),
            }

        elif image_type == ImageType.ADD_A_MODEL_TWO_IMAGE_COMPOSITE:
            composite_styles = [
                "split-screen diptych",
                "before/after panels",
                "layered double exposure",
                "side-by-side frames",
            ]
            settings = [
                "modern office",
                "urban street",
                "home interior",
                "outdoor adventure",
                "creative studio",
            ]
            moods = [
                "warm and inviting",
                "cool and professional",
                "energetic and dynamic",
                "calm and sophisticated",
            ]

            return {
                **base_params,
                "composite_style": random.choice(composite_styles),
                "first_composition": (
                    "product in pristine studio setting"
                ),
                "model_demographic": random.choice(
                    [
                        "young professionals",
                        "creative millennials",
                        "active lifestyle enthusiasts",
                        "sophisticated urbanites",
                    ]
                ),
                "environment_setting": random.choice(settings),
                "lighting_mood": random.choice(moods),
                "atmosphere_description": (
                    "cohesive narrative across both frames"
                ),
                "color_grading": random.choice(
                    [
                        "consistent warm tones",
                        "complementary color harmony",
                        "monochromatic elegance",
                    ]
                ),
                "negative_prompt": (
                    "Avoid: mismatched styles between frames, inconsistent lighting, different quality levels, jarring transitions"
                ),
            }

        elif image_type == ImageType.SHOP_THE_LOOK_FLAT_LAY:
            surfaces = [
                "marble surface",
                "rustic wood",
                "linen fabric",
                "concrete texture",
                "velvet backdrop",
            ]
            principles = [
                "color coordination",
                "theme cohesion",
                "style matching",
                "seasonal curation",
                "trend alignment",
            ]
            magazines = [
                "Vogue editorial",
                "Kinfolk minimal",
                "Cereal magazine",
                "Monocle style",
                "The Gentlewoman",
            ]

            return {
                **base_params,
                "accessory_1": (
                    product_profile.accessories[0]
                    if len(product_profile.accessories) > 0
                    else "style complement"
                ),
                "accessory_2": (
                    product_profile.accessories[1]
                    if len(product_profile.accessories) > 1
                    else "accent piece"
                ),
                "accessory_3": (
                    product_profile.accessories[2]
                    if len(product_profile.accessories) > 2
                    else "finishing touch"
                ),
                "surface_type": random.choice(surfaces),
                "styling_principle": random.choice(principles),
                "overhead_lighting": random.choice(
                    [
                        "soft diffused daylight",
                        "dramatic side light",
                        "even flat lighting",
                    ]
                ),
                "shadow_depth": random.choice(
                    [
                        "subtle depth",
                        "dramatic shadows",
                        "minimal shadow",
                    ]
                ),
                "color_coordination": (
                    "harmonious palette relationship"
                ),
                "spacing_rhythm": (
                    "balanced negative space distribution"
                ),
                "lifestyle_props": (
                    "curated selection of complementary items"
                ),
                "magazine_style": random.choice(magazines),
                "negative_prompt": (
                    "Avoid: random placement, clashing styles, overcrowded composition, mismatched aesthetics, poor color harmony"
                ),
            }

        # Fallback for any missing image types
        return {
            **base_params,
            "background_surface": "clean studio background",
            "lighting_setup": "professional lighting",
            "specific_feature": "key product elements",
        }

    def _initialize_prompt_templates(self):
        """Initialize marketing image prompt templates - SCENE-BASED PROFESSIONAL E-COMMERCE TEMPLATES"""

        # Professional scene-based templates focusing on narrative descriptions
        # Each template creates a vivid scene with specific details for maximum distinctiveness

        self.prompt_templates = {
            ImageType.MASTER_PRODUCT_SHOT: (
                """Create a high-resolution, photorealistic e-commerce hero shot depicting this vivid scene: {product_description} elegantly positioned on a {background_surface}, illuminated by {lighting_setup} that creates {lighting_purpose}. The camera captures from a {angle_type} perspective, revealing intricate details of {specific_feature} with tack-sharp focus on {key_detail}. The scene evokes a premium retail environment with {atmosphere_description}. Ultra-realistic rendering at 8K resolution, {style_reference} aesthetic, as if photographed with {camera_equipment}. Post-production includes {post_production} for magazine-quality finish. Professional product photography emphasizing trust and quality. {type_specific_params} NEGATIVE: {negative_prompt}"""
            ),
            ImageType.WHATS_IN_THE_BOX_FLAT_LAY: (
                """Illustrate a meticulously organized unboxing narrative from directly overhead: {product} takes center stage, surrounded by {item_1}, {item_2}, and {item_3} arranged in {arrangement_style} pattern that tells a story of premium packaging experience. Each item rests on {surface_description} with {lighting_condition} casting soft, welcoming shadows. The scene feels like an Instagram-worthy unboxing moment, with {mood_descriptor} atmosphere. Every component is captured in photorealistic detail with {shadow_style} depth. Professional flat lay photography at 8K resolution. {type_specific_params} NEGATIVE: {negative_prompt}"""
            ),
            ImageType.EXTREME_MACRO_DETAIL: (
                """Depict an intimate, scientific exploration scene focusing intensely on {detail_feature} of {product}. The extreme close-up reveals {texture_material} in dramatic detail, showcasing {quality_aspect} that speaks to craftsmanship. The scene employs {technical_description} with {lens_type} precision, creating {dof_description} that isolates the subject dramatically. Hyper-detailed {style_description} reminiscent of luxury watch advertisements. No full product visible - only mesmerizing textural details at microscopic scale. 8K resolution macro photography. {type_specific_params} NEGATIVE: {negative_prompt}"""
            ),
            ImageType.COLOR_STYLE_VARIATIONS: (
                """Compose a sophisticated retail display scene showing {variation_count} versions of {product} in different {variation_type}, arranged in {layout_style} formation. Each variant occupies its own visual space in {arrangement_description} on a {background_type} that enhances color differentiation. The scene uses {lighting_consistency} to maintain visual cohesion while highlighting unique characteristics. Professional {photography_style} following {composition_rule} for e-commerce galleries. The narrative emphasizes choice and personalization at 8K resolution. {type_specific_params} NEGATIVE: {negative_prompt}"""
            ),
            ImageType.ON_FOOT_SIZE_COMPARISONS: (
                """Construct a practical demonstration scene featuring {product} in a {comparison_type} context with {comparison_objects} for scale reference. The scene includes {scale_demonstration} with {measurement_indication} clearly visible. Shot from {camera_perspective} using {lighting_setup} that emphasizes proportions and dimensions. The narrative focuses on {detail_emphasis} with professional {style_descriptor} execution. Educational yet aesthetically pleasing composition at 8K resolution. {type_specific_params} NEGATIVE: {negative_prompt}"""
            ),
            ImageType.ADD_A_MODEL_TWO_IMAGE_COMPOSITE: (
                """Create a dynamic diptych scene in {composite_style}: The first frame captures {product} alone in {first_composition} while the second shows {model_demographic} using it in {environment_setting}. The scene uses {lighting_mood} to create {atmosphere_description} with cinematic {color_grading}. Both images tell a cohesive lifestyle story that resonates with target demographics. Professional fashion photography at 8K resolution. {type_specific_params} NEGATIVE: {negative_prompt}"""
            ),
            ImageType.LIFESTYLE_ACTION_SHOT: (
                """Capture an energetic moment where {product} becomes part of {activity_context} narrative. The scene freezes {model_demographic} mid-{action_verb} using {camera_technique} in {environment_description} during {lighting_condition}. Natural lighting creates {mood_atmosphere} that feels authentic and aspirational. The composition uses {focus_technique} on {focal_point} while maintaining context. {color_palette} enhances the {photography_style} aesthetic. Documentary-style realism meets commercial polish at 8K resolution. {type_specific_params} NEGATIVE: {negative_prompt}"""
            ),
            ImageType.UGC_STYLE_PHOTOS: (
                """Document an authentic moment of {product} in everyday use, captured in {phone_camera_style} aesthetic with {natural_lighting}. The scene shows {everyday_context} with {casual_styling} creating genuine, unpolished charm. Applied {filter_effect} adds {social_elements} for social media appeal. The narrative feels spontaneous and relatable, perfect for {social_media_platform} in {aspect_ratio} format. Intentionally imperfect yet engaging at high resolution. {type_specific_params} NEGATIVE: {negative_prompt}"""
            ),
            ImageType.NEGATIVE_SPACE_BANNER: (
                """Design a minimalist scene where {product} breathes in abundant white space, positioned according to {composition_rule} for {text_space_location} flexibility. The product occupies only {space_percentage} of the frame, creating dramatic visual tension. The {color_scheme} background uses {shadow_treatment} for subtle depth. Clean {brand_aesthetic} follows {design_principle} philosophy. Professional banner layout optimized for digital advertising at 8K resolution. {type_specific_params} NEGATIVE: {negative_prompt}"""
            ),
            ImageType.SHOP_THE_LOOK_FLAT_LAY: (
                """Curate an editorial scene where {product} anchors a lifestyle narrative, artfully styled with {accessory_1}, {accessory_2}, and {accessory_3}. The {styling_principle} unfolds on {surface_type} with {overhead_lighting} creating {shadow_depth} for dimensionality. Careful {color_coordination} and {spacing_rhythm} create visual harmony. Include {lifestyle_props} to complete the aspirational aesthetic. The scene evokes {magazine_style} editorial spreads that inspire purchase desire. Shoppable content photography at 8K resolution. {type_specific_params} NEGATIVE: {negative_prompt}"""
            ),
        }

    # ==========================================================================
    # Core Agent Methods
    # ==========================================================================

    def create_product_profile(
        self, product_data: Dict[str, Any]
    ) -> ProductProfile:
        """
        Use Product Interpreter Agent to create comprehensive product profile with exact JSON structure

        Args:
            product_data: Raw product information dictionary

        Returns:
            ProductProfile: Structured product profile
        """

        prompt = f"""
        You are a Product Marketing Specialist. Analyze the following product information 
        and create a comprehensive marketing profile in EXACT JSON format.
        
        Raw Product Data:
        {json.dumps(product_data, indent=2)}
        
        REQUIRED: Generate a JSON response with EXACTLY these fields:
        {{
            "product_name": "Clean and marketable product name",
            "category": "Specific product category",
            "key_features": ["feature1", "feature2", "feature3"],
            "accessories": ["accessory1", "accessory2", "accessory3"],
            "objectives": ["objective1", "objective2", "objective3"],
            "suggested_image_types": [1, 2, 3]
        }}
        
        Guidelines:
        - product_name: Extract or refine the product name for marketing
        - category: Identify specific product category 
        - key_features: List 3-5 main product features
        - accessories: List items that come with or complement the product
        - objectives: List 3-5 marketing objectives for this product
        - suggested_image_types: Array of numbers 1-10 representing the most suitable ImageType enum values
        
        ImageType Reference:
        1=MASTER_PRODUCT_SHOT, 2=WHATS_IN_THE_BOX_FLAT_LAY, 3=EXTREME_MACRO_DETAIL, 
        4=COLOR_STYLE_VARIATIONS, 5=ON_FOOT_SIZE_COMPARISONS, 6=ADD_A_MODEL_TWO_IMAGE_COMPOSITE,
        7=LIFESTYLE_ACTION_SHOT, 8=UGC_STYLE_PHOTOS, 9=NEGATIVE_SPACE_BANNER, 10=SHOP_THE_LOOK_FLAT_LAY
        
        Return ONLY the JSON object, no additional text or formatting.
        """

        self.logger.info(
            f"Creating product profile for: {product_data.get('name', 'Unknown Product')}"
        )

        try:
            # Run the agent to analyze the product
            analysis_result = self.product_interpreter_agent.run(
                prompt
            )

            # Parse the JSON response from the agent
            try:
                parsed_json = json.loads(analysis_result.strip())
            except json.JSONDecodeError:
                # Fallback parsing if JSON is not properly formatted
                self.logger.warning(
                    "Failed to parse JSON from agent response, using fallback parsing"
                )
                # Intelligent fallback that suggests image types based on product category and features
                suggested_types = (
                    self._get_intelligent_image_suggestions(
                        product_data
                    )
                )
                parsed_json = {
                    "product_name": product_data.get(
                        "name", "Unknown Product"
                    ),
                    "category": product_data.get(
                        "category", "General"
                    ),
                    "key_features": product_data.get(
                        "features",
                        ["Feature 1", "Feature 2", "Feature 3"],
                    ),
                    "accessories": product_data.get(
                        "accessories", ["Standard accessories"]
                    ),
                    "objectives": product_data.get(
                        "objectives",
                        [
                            "Increase brand awareness",
                            "Drive sales",
                            "Showcase features",
                        ],
                    ),
                    "suggested_image_types": suggested_types,
                }

            # Create structured ProductProfile with the exact required fields
            profile = ProductProfile(
                product_name=parsed_json["product_name"],
                category=parsed_json["category"],
                key_features=parsed_json["key_features"],
                accessories=parsed_json["accessories"],
                objectives=parsed_json["objectives"],
                suggested_image_types=parsed_json[
                    "suggested_image_types"
                ],
            )

            # Save product profile
            self.product_profiles[profile.product_id] = profile
            self._save_product_profile(profile)

            self.logger.info(
                f"Product profile created: {profile.product_id}"
            )
            return profile

        except Exception as e:
            self.logger.error(
                f"Error creating product profile: {str(e)}"
            )
            raise

    def select_image_type(
        self,
        product_profile: ProductProfile,
        interactive: bool = True,
    ) -> ImageType:
        """
        Use Image Type Selector Agent to guide image type selection with suggested types

        Args:
            product_profile: Product profile to analyze
            interactive: Whether to use interactive selection

        Returns:
            ImageType: Selected image type
        """

        if interactive:
            return self._interactive_image_selection(
                product_profile.suggested_image_types
            )

        # AI-powered selection based on product profile and suggested types
        prompt = f"""
        You are a Marketing Strategy Expert. Based on the product profile below, 
        recommend the most effective marketing image type from the suggested types.
        
        Product Profile:
        - Name: {product_profile.product_name}
        - Category: {product_profile.category}
        - Key Features: {', '.join(product_profile.key_features)}
        - Accessories: {', '.join(product_profile.accessories)}
        - Objectives: {', '.join(product_profile.objectives)}
        - Suggested Image Types: {product_profile.suggested_image_types}
        
        Available Image Types (with numbers):
        1. MASTER_PRODUCT_SHOT - High-resolution studio product photography
        2. WHATS_IN_THE_BOX_FLAT_LAY - Top-down arrangement with all included items
        3. EXTREME_MACRO_DETAIL - Ultra close-up detail shots
        4. COLOR_STYLE_VARIATIONS - Multiple color/style options display
        5. ON_FOOT_SIZE_COMPARISONS - Size comparison photos with models
        6. ADD_A_MODEL_TWO_IMAGE_COMPOSITE - Split image with and without model
        7. LIFESTYLE_ACTION_SHOT - Dynamic action photography
        8. UGC_STYLE_PHOTOS - Authentic user-generated content style
        9. NEGATIVE_SPACE_BANNER - Product with space for text overlay
        10. SHOP_THE_LOOK_FLAT_LAY - Complete styling flat lay arrangement
        
        From the suggested types {product_profile.suggested_image_types}, recommend the best choice.
        
        Respond with ONLY the number (1-10) of the recommended image type.
        """

        try:
            recommendation = self.image_selector_agent.run(prompt)

            # Parse recommendation to extract image type number
            try:
                type_number = int(recommendation.strip())
                if 1 <= type_number <= 10:
                    selected_type = ImageType(type_number)
                    self.logger.info(
                        f"AI recommended image type: {selected_type}"
                    )
                    return selected_type
            except (ValueError, TypeError):
                pass

            # Fallback to first suggested type if available
            if product_profile.suggested_image_types:
                fallback_type = ImageType(
                    product_profile.suggested_image_types[0]
                )
                self.logger.warning(
                    f"Could not parse AI recommendation, using first suggested type: {fallback_type}"
                )
                return fallback_type

            # Final fallback
            self.logger.warning(
                "Could not parse AI recommendation, defaulting to MASTER_PRODUCT_SHOT"
            )
            return ImageType.MASTER_PRODUCT_SHOT

        except Exception as e:
            self.logger.error(
                f"Error in image type selection: {str(e)}"
            )
            return ImageType.MASTER_PRODUCT_SHOT

    def _interactive_image_selection(
        self, suggested_types: List[int] = None
    ) -> ImageType:
        """Interactive console-based image type selection"""

        # Rich styled header
        title = Text(
            "MARKETING IMAGE TYPE SELECTION", style="bold cyan"
        )
        panel = Panel(
            Align.center(title), border_style="cyan", box=box.ROUNDED
        )
        console.print("\n")
        console.print(panel)

        # Create image types table
        image_table = Table(
            title="[bold yellow]Available Marketing Image Types[/bold yellow]"
        )
        image_table.add_column("#", style="cyan", width=3)
        image_table.add_column("Type", style="magenta bold", width=30)
        image_table.add_column("Description", style="white")
        image_table.add_column("Status", style="green", width=12)

        image_options = [
            (
                1,
                ImageType.MASTER_PRODUCT_SHOT,
                "High-resolution studio product photography",
            ),
            (
                2,
                ImageType.WHATS_IN_THE_BOX_FLAT_LAY,
                "Top-down arrangement with all included items",
            ),
            (
                3,
                ImageType.EXTREME_MACRO_DETAIL,
                "Ultra close-up detail shots",
            ),
            (
                4,
                ImageType.COLOR_STYLE_VARIATIONS,
                "Multiple color/style options display",
            ),
            (
                5,
                ImageType.ON_FOOT_SIZE_COMPARISONS,
                "Size comparison photos with models",
            ),
            (
                6,
                ImageType.ADD_A_MODEL_TWO_IMAGE_COMPOSITE,
                "Split image with and without model",
            ),
            (
                7,
                ImageType.LIFESTYLE_ACTION_SHOT,
                "Dynamic action photography",
            ),
            (
                8,
                ImageType.UGC_STYLE_PHOTOS,
                "Authentic user-generated content style",
            ),
            (
                9,
                ImageType.NEGATIVE_SPACE_BANNER,
                "Product with space for text overlay",
            ),
            (
                10,
                ImageType.SHOP_THE_LOOK_FLAT_LAY,
                "Complete styling flat lay arrangement",
            ),
        ]

        for num, img_type, description in image_options:
            suggested_marker = (
                "[bold green]★ SUGGESTED[/bold green]"
                if suggested_types and num in suggested_types
                else ""
            )
            image_name = img_type.name.replace("_", " ").title()
            image_table.add_row(
                str(num),
                image_name,
                description,
                suggested_marker or "Available",
            )

        console.print("\n")
        console.print(image_table)

        if suggested_types:
            suggestion_text = Text(
                f"★ Suggested types for this product: {suggested_types}",
                style="bold yellow",
            )
            console.print("\n")
            console.print(
                Panel(suggestion_text, border_style="yellow")
            )

        while True:
            try:
                choice = Prompt.ask(
                    "\n[bold cyan]Select image type[/bold cyan]",
                    choices=[str(i) for i in range(1, 11)],
                )

                if choice.isdigit() and 1 <= int(choice) <= 10:
                    choice_num = int(choice)
                    selected_type = ImageType(choice_num)
                    type_name = selected_type.name.replace(
                        "_", " "
                    ).title()
                    console.print(
                        f"\n[bold green]✓ Selected: {type_name}[/bold green]"
                    )
                    return selected_type
                else:
                    console.print(
                        "[red]Please enter a number between 1 and 10.[/red]"
                    )

            except KeyboardInterrupt:
                console.print(
                    "\n\n[red]Operation cancelled by user.[/red]"
                )
                exit(0)
            except Exception as e:
                console.print(
                    f"[red]Invalid input. Please try again. ({str(e)})[/red]"
                )

    def generate_custom_prompt(
        self,
        product_profile: ProductProfile,
        image_type: ImageType,
        custom_requirements: str = "",
    ) -> str:
        """
        Use Prompt Generator Agent to create customized generation prompt using exact templates

        Args:
            product_profile: Product information
            image_type: Type of marketing image to create
            custom_requirements: Additional custom requirements

        Returns:
            str: Customized prompt for image generation
        """

        base_template = self.prompt_templates[image_type]

        # Create IMAGE-TYPE-SPECIFIC parameters for truly different prompts
        prompt_params = self._get_image_type_specific_params(
            product_profile, image_type
        )

        # Apply template with parameters
        try:
            customized_prompt = base_template.format(**prompt_params)
        except KeyError as e:
            self.logger.warning(
                f"Missing template parameter {e}, using base template"
            )
            customized_prompt = base_template

        # Add custom requirements if provided
        if custom_requirements:
            customized_prompt += (
                f"\n\nAdditional Requirements: {custom_requirements}"
            )

        # Use Prompt Generator Agent to enhance the prompt with professional e-commerce focus
        enhancement_prompt = f"""
        You are a professional e-commerce visual prompt engineer specializing in market-ready, photorealistic product imagery.
        
        Enhance this prompt for Gemini 2.5 Flash to generate a HIGHLY DISTINCTIVE, professional e-commerce image.
        
        Base Prompt:
        {customized_prompt}
        
        CRITICAL ENHANCEMENTS:
        1. Transform into vivid scene description with environmental details
        2. Add exact camera settings: f-stop, ISO, shutter speed, lens focal length
        3. Specify 8K resolution, color accuracy, trust-building visual elements
        4. Make this {image_type.name} completely unique through:
           - Type-specific composition techniques
           - Distinctive lighting setups
           - Targeted post-processing style
        5. Ensure market-ready quality for Amazon, Shopify, social media
        
        Image Type: {image_type.name} - must be unmistakably different from other types
        
        Return ONLY the enhanced prompt. No explanations or commentary.
        """

        try:
            enhanced_prompt = self.prompt_generator_agent.run(
                enhancement_prompt
            )
            self.logger.info(
                f"Generated custom prompt for Step_{image_type.value}"
            )
            return enhanced_prompt

        except Exception as e:
            self.logger.error(f"Error enhancing prompt: {str(e)}")
            return customized_prompt  # Return original if enhancement fails

    def generate_marketing_image(
        self,
        product_profile: ProductProfile,
        image_type: ImageType,
        custom_prompt: str,
        master_image_path: Optional[str] = None,
    ) -> str:
        """
        Use Image Generation Agent to create marketing image - follows nano-banana.py exact pattern

        Args:
            product_profile: Product information
            image_type: Type of marketing image
            custom_prompt: Generated prompt for image creation
            master_image_path: Path to master reference image

        Returns:
            str: Path to generated image file (auto-saved by swarms) or text content
        """

        try:
            # Add multiple unique identifiers to prevent caching issues
            unique_id = str(uuid.uuid4())[:8]
            timestamp = time.strftime(
                "%Y%m%d_%H%M%S_%f"
            )  # Include microseconds for higher uniqueness
            random_suffix = str(uuid.uuid4())[
                :12
            ]  # Longer random suffix
            cache_buster = f"NOCACHE_{int(time.time() * 1000000)}"  # Timestamp in microseconds

            # ENHANCED API-LEVEL CACHE BUSTING
            import random

            session_nonce = str(uuid.uuid4())
            generation_nonce = str(uuid.uuid4())
            random_factor = random.randint(100000, 999999)
            api_cache_buster = f"API_UNIQUE_{int(time.time() * 1000000)}_{random_factor}"

            # Create a highly unique prompt that prevents any form of caching
            # Make it clear this should generate an image, not text
            enhanced_prompt = (
                f"GENERATE IMAGE: {custom_prompt}\n\n"
                f"[UNIQUE_GENERATION_REQUEST]\n"
                f"RequestID: {unique_id}_{timestamp}_{image_type.value}\n"
                f"RandomSeed: {random_suffix}\n"
                f"CacheBuster: {cache_buster}\n"
                f"SessionNonce: {session_nonce}\n"
                f"GenerationNonce: {generation_nonce}\n"
                f"APICacheBuster: {api_cache_buster}\n"
                f"ProductContext: {product_profile.product_name}_{product_profile.category}\n"
                f"[END_UNIQUE_CONTEXT]\n"
                f"IMPORTANT: Generate the actual image, do not provide text explanations."
            )

            self.logger.info(
                f"🚀 Starting FRESH image generation for Step_{image_type.value} with unique ID: {unique_id}"
            )
            self.logger.info(
                f"🔥 Enhanced API-level cache busting: {api_cache_buster}"
            )
            self.logger.info(
                f"📏 Prompt length: {len(enhanced_prompt)} characters"
            )

            # 🆕 CREATE FRESH AGENT FOR THIS REQUEST - PREVENTS GOOGLE API CACHING
            fresh_agent = self._create_fresh_image_agent()
            self.logger.info(
                f"🔄 Created fresh agent: {fresh_agent.agent_name} (Temp: {fresh_agent.temperature:.3f})"
            )

            # Run the FRESH image generation agent with enhanced cache busting
            if master_image_path and os.path.exists(
                master_image_path
            ):
                result = fresh_agent.run(
                    task=enhanced_prompt, img=master_image_path
                )
                self.logger.info(
                    f"✨ Generated Step_{image_type.value} with master image reference using FRESH agent (ID: {unique_id})"
                )
            else:
                result = fresh_agent.run(task=enhanced_prompt)
                self.logger.info(
                    f"✨ Generated Step_{image_type.value} without master image using FRESH agent (ID: {unique_id})"
                )

            # Log response details for debugging
            result_str = str(result)
            self.logger.info(
                f"Agent response length: {len(result_str)} characters"
            )
            self.logger.info(
                f"Response starts with: {result_str[:100]}..."
            )
            self.logger.info(
                f"Response ends with: ...{result_str[-100:]}"
            )

            # Create organized directory structure for this product and image type
            product_dir = (
                self.save_directory
                / "outputs"
                / f"{product_profile.product_name.replace(' ', '_')}"
            )
            image_type_dir = (
                product_dir
                / f"Step_{image_type.value}_{image_type.name.lower()}"
            )
            image_type_dir.mkdir(parents=True, exist_ok=True)

            result_str = str(result).strip()

            # Check if swarms returned a file path (gemini_output_img_handler should have converted base64 to path)

            # First check: Is this a valid file path that exists?
            if result_str.endswith(
                (
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".webp",
                    ".bmp",
                    ".tiff",
                )
            ) and os.path.exists(result_str):

                # Found the auto-generated image file path from swarms
                saved_path = Path(result_str)
                file_extension = saved_path.suffix
                meaningful_filename = f"{product_profile.product_name.replace(' ', '_')}_Step_{image_type.value}_{timestamp}_{unique_id}"
                meaningful_path = (
                    image_type_dir
                    / f"{meaningful_filename}{file_extension}"
                )

                # Move the file to organized location
                shutil.move(str(saved_path), str(meaningful_path))
                self.logger.info(
                    f"Image moved from {result_str} to organized location: {meaningful_path}"
                )
                self.logger.info(
                    f"Unique filename generated: {meaningful_filename}{file_extension}"
                )

                # Display success message with Rich
                success_panel = Panel(
                    f"[bold green]🎉 IMAGE SUCCESSFULLY GENERATED AND SAVED![/bold green]\n\n"
                    f"📁 Location: {meaningful_path}\n"
                    f"🎨 Image Type: {image_type.name.replace('_', ' ').title()}\n"
                    f"📦 Product: {product_profile.product_name}\n"
                    f"⏰ Generated: {timestamp}",
                    title="[bold cyan]📸 Image Generation Complete[/bold cyan]",
                    border_style="green",
                    expand=False,
                )
                console.print("\n")
                console.print(success_panel)

                return str(meaningful_path)

            # Second check: Does this look like base64 image data?
            elif (
                "data:image" in result_str and "base64" in result_str
            ):

                # Found base64 image data - extract it from the mixed text response
                self.logger.info(
                    "Detected base64 image data in text response, extracting and converting to file..."
                )

                # Extract the base64 data URI using regex
                data_uri_pattern = (
                    r"data:image/[^;]+;base64,[A-Za-z0-9+/]+=*"
                )
                match = re.search(data_uri_pattern, result_str)

                if match:
                    extracted_base64 = match.group(0)
                    self.logger.info(
                        f"Successfully extracted base64 data URI: {len(extracted_base64)} characters"
                    )

                    # 🚨 GLOBAL DUPLICATE DETECTION - Check against all previous generations
                    is_duplicate = self._track_base64_globally(
                        extracted_base64
                    )
                    if is_duplicate:
                        self.logger.error(
                            "❌ DUPLICATE BASE64 CONTENT! This exact image was generated before!"
                        )
                        self.logger.error(
                            "💡 This indicates Google API caching issue - fresh agent creation may need adjustment"
                        )
                        # Continue processing but log the issue for analysis

                    filename_prefix = f"{product_profile.product_name.replace(' ', '_')}_Step_{image_type.value}_{timestamp}_{unique_id}"

                    converted_image_path = (
                        self._convert_base64_to_file(
                            base64_data=extracted_base64,
                            output_dir=image_type_dir,
                            filename_prefix=filename_prefix,
                        )
                    )

                    if converted_image_path:
                        # Display success message with Rich
                        success_panel = Panel(
                            f"[bold green]🎉 BASE64 IMAGE CONVERTED AND SAVED![/bold green]\n\n"
                            f"📁 Location: {converted_image_path}\n"
                            f"🎨 Image Type: {image_type.name.replace('_', ' ').title()}\n"
                            f"📦 Product: {product_profile.product_name}\n"
                            f"🔑 Unique ID: {unique_id}\n"
                            f"⏰ Generated: {timestamp}",
                            title="[bold cyan]📸 Base64 Conversion Complete[/bold cyan]",
                            border_style="green",
                            expand=False,
                        )
                        console.print("\n")
                        console.print(success_panel)

                        return converted_image_path
                    else:
                        # Base64 conversion failed
                        self.logger.error(
                            "Failed to convert base64 data to image file"
                        )
                else:
                    self.logger.warning(
                        "Could not extract valid base64 data URI from response"
                    )

            # Third check: Is this pure base64 data (without data URI prefix)?
            elif len(result_str) > 1000 and re.match(
                r"^[A-Za-z0-9+/]+=*$",
                result_str.replace("\n", "").replace(" ", "").strip(),
            ):

                # Found pure base64 image data - convert it to file
                self.logger.info(
                    "Detected pure base64 image data, converting to file..."
                )

                # 🚨 GLOBAL DUPLICATE DETECTION - Check against all previous generations
                is_duplicate = self._track_base64_globally(
                    result_str.strip()
                )
                if is_duplicate:
                    self.logger.error(
                        "❌ DUPLICATE BASE64 CONTENT! This exact image was generated before!"
                    )
                    self.logger.error(
                        "💡 This indicates Google API caching issue - fresh agent creation may need adjustment"
                    )
                    # Continue processing but log the issue for analysis

                filename_prefix = f"{product_profile.product_name.replace(' ', '_')}_Step_{image_type.value}_{timestamp}_{unique_id}"

                converted_image_path = self._convert_base64_to_file(
                    base64_data=result_str.strip(),
                    output_dir=image_type_dir,
                    filename_prefix=filename_prefix,
                )

                if converted_image_path:
                    # Display success message with Rich
                    success_panel = Panel(
                        f"[bold green]🎉 BASE64 IMAGE CONVERTED AND SAVED![/bold green]\n\n"
                        f"📁 Location: {converted_image_path}\n"
                        f"🎨 Image Type: {image_type.name.replace('_', ' ').title()}\n"
                        f"📦 Product: {product_profile.product_name}\n"
                        f"🔑 Unique ID: {unique_id}\n"
                        f"⏰ Generated: {timestamp}",
                        title="[bold cyan]📸 Base64 Conversion Complete[/bold cyan]",
                        border_style="green",
                        expand=False,
                    )
                    console.print("\n")
                    console.print(success_panel)

                    return converted_image_path
                else:
                    # Base64 conversion failed
                    self.logger.error(
                        "Failed to convert base64 data to image file"
                    )

            # Fourth check: Fallback for unexpected response format
            self.logger.warning(
                f"Unexpected response format. Length: {len(result_str)} characters. First 200 chars: {result_str[:200]}"
            )

            # Save as text content for debugging since we couldn't handle the response
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_filename = f"{product_profile.product_name.replace(' ', '_')}_Step_{image_type.value}_{timestamp}_debug.txt"
            output_path = image_type_dir / output_filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("Raw Agent Response (Debug):\n")
                f.write(f"Length: {len(result_str)} characters\n")
                f.write(f"First 500 chars: {result_str[:500]}\n")
                f.write(f"Last 500 chars: {result_str[-500:]}\n")
                f.write(f"\nFull Response:\n{result_str}")

            self.logger.info(f"Debug content saved to: {output_path}")

            # Show warning panel
            warning_panel = Panel(
                f"[bold yellow]⚠️ UNEXPECTED RESPONSE FORMAT[/bold yellow]\n\n"
                f"Could not process the agent's response as an image.\n"
                f"Debug information saved to: {output_path}\n"
                f"Response length: {len(result_str)} characters",
                title="[bold bright_yellow]🔧 Debug Info[/bold bright_yellow]",
                border_style="bright_yellow",
                expand=False,
            )
            console.print("\n")
            console.print(warning_panel)

            return str(output_path)

        except Exception as e:
            self.logger.error(
                f"Error generating marketing image: {str(e)}"
            )
            raise

    def process_output_and_feedback(
        self, generated_result: str, job: MarketingJob
    ) -> Dict[str, Any]:
        """
        Use Output Handler & Feedback Agent to process results and gather feedback

        Args:
            generated_result: The generated marketing content
            job: Marketing job information

        Returns:
            Dict containing processed output and feedback analysis
        """

        feedback_prompt = f"""
        You are a Marketing Quality Assurance Expert. Analyze the generated marketing 
        content and provide comprehensive feedback and recommendations.
        
        Job Details:
        - Product: {job.product_profile.product_name}
        - Image Type: {job.image_type.value}
        - Category: {job.product_profile.category}
        - Key Features: {', '.join(job.product_profile.key_features)}
        - Objectives: {', '.join(job.product_profile.objectives)}
        - Custom Requirements: {job.custom_requirements}
        
        Generated Content:
        {generated_result}
        
        Please provide:
        1. Quality Assessment (1-10 score)
        2. Brand Alignment Analysis
        3. Target Audience Appropriateness
        4. Marketing Effectiveness Evaluation
        5. Improvement Recommendations
        6. Next Steps Suggestions
        
        Format as a structured report for the marketing team.
        """

        try:
            feedback_analysis = self.output_handler_agent.run(
                feedback_prompt
            )

            result = {
                "job_id": job.job_id,
                "product_name": job.product_profile.product_name,
                "image_type": f"Step_{job.image_type.value}",
                "generated_content_path": generated_result,
                "feedback_analysis": feedback_analysis,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "completed",
            }

            # Save feedback report
            feedback_path = (
                self.save_directory
                / "jobs"
                / f"{job.job_id}_feedback.json"
            )
            with open(feedback_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

            self.logger.info(
                f"Feedback analysis completed for job: {job.job_id}"
            )
            return result

        except Exception as e:
            self.logger.error(
                f"Error processing output and feedback: {str(e)}"
            )
            raise

    # ==========================================================================
    # Workflow Orchestration Methods
    # ==========================================================================

    def run_marketing_campaign(
        self,
        product_data: Dict[str, Any],
        image_types: Optional[List[ImageType]] = None,
        custom_requirements: str = "",
        master_image_path: Optional[str] = None,
        interactive: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Complete marketing campaign workflow

        Args:
            product_data: Raw product information
            image_types: List of image types to generate (None for interactive selection)
            custom_requirements: Additional requirements
            master_image_path: Path to master reference image
            interactive: Enable interactive mode

        Returns:
            List of completed marketing jobs with results
        """

        self.logger.info("Starting marketing campaign workflow")

        try:
            # Step 1: Create product profile
            # Rich progress for Step 1
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                console=console,
            ) as progress:
                task1 = progress.add_task(
                    "🔥 STEP 1: Analyzing Product Information...",
                    total=1,
                )
                product_profile = self.create_product_profile(
                    product_data
                )
                progress.update(task1, completed=1)
            print(
                f" Product Profile Created: {product_profile.product_name}"
            )

            # Step 2: Select image types
            print("\n<� STEP 2: Selecting Marketing Image Types...")
            if image_types is None:
                if interactive:
                    image_types = [
                        self.select_image_type(
                            product_profile, interactive=True
                        )
                    ]

                    # Ask if user wants to generate multiple types
                    while True:
                        more = (
                            input(
                                "\nWould you like to generate another image type? (y/n): "
                            )
                            .strip()
                            .lower()
                        )
                        if more in ["y", "yes"]:
                            image_types.append(
                                self.select_image_type(
                                    product_profile, interactive=True
                                )
                            )
                        elif more in ["n", "no"]:
                            break
                        else:
                            print(
                                "Please enter 'y' for yes or 'n' for no."
                            )
                else:
                    image_types = [
                        self.select_image_type(
                            product_profile, interactive=False
                        )
                    ]

            print(
                f" Selected {len(image_types)} image types for generation"
            )

            # Step 3: Generate marketing materials
            results = []

            for i, image_type in enumerate(image_types, 1):
                image_name = image_type.name.replace("_", " ").title()
                print(f"\n⚡ STEP 3.{i}: Generating {image_name}...")

                # Create marketing job
                job = MarketingJob(
                    job_id=str(uuid.uuid4()),
                    product_profile=product_profile,
                    image_type=image_type,
                    custom_requirements=custom_requirements,
                )

                self.active_jobs[job.job_id] = job

                # Generate custom prompt
                print("  � Creating customized prompt...")
                custom_prompt = self.generate_custom_prompt(
                    product_profile, image_type, custom_requirements
                )

                # Generate marketing image
                print("  � Generating marketing content...")
                generated_result = self.generate_marketing_image(
                    product_profile,
                    image_type,
                    custom_prompt,
                    master_image_path,
                )

                # Process output and feedback
                print(
                    "  � Processing results and generating feedback..."
                )
                final_result = self.process_output_and_feedback(
                    generated_result, job
                )

                results.append(final_result)
                print(
                    f" {image_type.name.replace('_', ' ').title()} completed successfully"
                )

            # Step 4: Campaign summary
            print("\n<� CAMPAIGN COMPLETED!")
            print(
                f"Generated {len(results)} marketing assets for {product_profile.product_name}"
            )
            print(f"Results saved in: {self.save_directory}")

            return results

        except Exception as e:
            self.logger.error(
                f"Error in marketing campaign workflow: {str(e)}"
            )
            raise

    def batch_process_products(
        self,
        products_data: List[Dict[str, Any]],
        default_image_types: List[ImageType] = None,
    ) -> List[List[Dict[str, Any]]]:
        """
        Process multiple products in batch mode

        Args:
            products_data: List of product information dictionaries
            default_image_types: Default image types for batch processing

        Returns:
            List of campaign results for each product
        """

        if default_image_types is None:
            default_image_types = [
                ImageType.MASTER_PRODUCT_SHOT,
                ImageType.LIFESTYLE_ACTION_SHOT,
            ]

        self.logger.info(
            f"Starting batch processing for {len(products_data)} products"
        )

        batch_results = []

        for i, product_data in enumerate(products_data, 1):
            print(f"\n{'='*60}")
            print(f"PROCESSING PRODUCT {i} of {len(products_data)}")
            print(f"{'='*60}")

            try:
                results = self.run_marketing_campaign(
                    product_data=product_data,
                    image_types=default_image_types,
                    interactive=False,
                )
                batch_results.append(results)

            except Exception as e:
                self.logger.error(
                    f"Error processing product {i}: {str(e)}"
                )
                batch_results.append([])

        print("\n<� BATCH PROCESSING COMPLETED!")
        print(f"Processed {len(products_data)} products")
        print(
            f"Total assets generated: {sum(len(results) for results in batch_results)}"
        )

        return batch_results

    # ==========================================================================
    # State Management & Utility Methods
    # ==========================================================================

    def _save_product_profile(self, profile: ProductProfile):
        """Save product profile to disk"""
        profile_path = (
            self.save_directory
            / "products"
            / f"{profile.product_id}.json"
        )
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(asdict(profile), f, indent=2)

    def load_product_profile(
        self, product_id: str
    ) -> Optional[ProductProfile]:
        """Load product profile from disk"""
        profile_path = (
            self.save_directory / "products" / f"{product_id}.json"
        )

        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ProductProfile(**data)

        return None

    def list_available_profiles(self) -> List[str]:
        """List all available product profiles"""
        profiles_dir = self.save_directory / "products"
        return [f.stem for f in profiles_dir.glob("*.json")]

    def set_master_image(self, product_id: str, image_path: str):
        """Set master reference image for a product with enhanced management"""
        if os.path.exists(image_path):
            # Copy image to master_images directory for consistency management
            master_dir = self.save_directory / "master_images"

            # Generate consistent naming
            image_extension = Path(image_path).suffix
            master_filename = f"{product_id}_master{image_extension}"
            master_copy_path = master_dir / master_filename

            # Copy the file
            shutil.copy2(image_path, master_copy_path)

            # Store reference and update product profile if exists
            self.master_images[product_id] = str(master_copy_path)

            if product_id in self.product_profiles:
                self.product_profiles[
                    product_id
                ].master_image_path = str(master_copy_path)
                self._save_product_profile(
                    self.product_profiles[product_id]
                )

            self.logger.info(
                f"Master image set for product {product_id}: {master_copy_path}"
            )
            return str(master_copy_path)
        else:
            raise FileNotFoundError(
                f"Master image not found: {image_path}"
            )

    def get_master_image_path(self, product_id: str) -> Optional[str]:
        """Get master image path for a product"""
        return self.master_images.get(product_id)

    def ensure_visual_consistency(
        self, product_profile: ProductProfile, image_type: ImageType
    ) -> bool:
        """Check if master image is required for visual consistency"""
        master_required_types = [
            ImageType.WHATS_IN_THE_BOX_FLAT_LAY,
            ImageType.COLOR_STYLE_VARIATIONS,
            ImageType.ADD_A_MODEL_TWO_IMAGE_COMPOSITE,
        ]
        return image_type in master_required_types

    def get_campaign_statistics(self) -> Dict[str, Any]:
        """Get statistics about completed campaigns"""
        stats = {
            "total_products": len(self.product_profiles),
            "total_jobs": len(self.active_jobs),
            "completed_jobs": len(
                [
                    j
                    for j in self.active_jobs.values()
                    if j.status == "completed"
                ]
            ),
            "image_types_generated": {},
            "save_directory": str(self.save_directory),
        }

        for job in self.active_jobs.values():
            image_type = f"Step_{job.image_type.value}"
            stats["image_types_generated"][image_type] = (
                stats["image_types_generated"].get(image_type, 0) + 1
            )

        return stats


# ==========================================================================
# Console Interface Functions
# ==========================================================================


def display_welcome_banner():
    """Display welcome banner with Rich styling"""
    # Create main title
    title = Text("🚀 PRODUCT MARKETING AGENCY", style="bold magenta")
    subtitle = Text("Multi-Agent System", style="bold cyan")

    # Create feature list
    features_table = Table(
        show_header=False, show_edge=False, pad_edge=False, box=None
    )
    features_table.add_column(style="bright_blue bold")
    features_table.add_column(style="white")

    features_table.add_row("⚡", "6 Specialized AI Agents")
    features_table.add_row("📸", "10 Marketing Image Types")
    features_table.add_row("🔄", "Interactive & Batch Processing")
    features_table.add_row("🎨", "Visual Consistency Management")
    features_table.add_row("📊", "Comprehensive Feedback System")

    # Create powered by text
    powered_by = Text(
        "Powered by Swarms Framework | Advanced AI Marketing Content Generation",
        style="dim italic",
    )

    # Create the main panel content
    console.print("\n")
    console.print(
        Panel(
            Align.center(f"{title}\n{subtitle}"),
            title="[bold green]Welcome[/bold green]",
            border_style="bright_magenta",
            box=box.DOUBLE,
        )
    )
    console.print(features_table)
    console.print(
        Panel(
            Align.center(powered_by),
            subtitle="[dim]Ready to create amazing marketing content![/dim]",
            border_style="bright_magenta",
            box=box.SIMPLE,
        )
    )
    return


def get_product_information_interactive() -> Dict[str, Any]:
    """Smart product information parser that handles unstructured bulk input"""
    # Rich styled header
    title = Text("🚀 PRODUCT MARKETING AGENCY", style="bold magenta")
    subtitle = Text("Information Setup", style="bold cyan")

    header_panel = Panel(
        Align.center(f"{title}\n{subtitle}"),
        border_style="magenta",
        box=box.ROUNDED,
    )

    console.print("\n")
    console.print(header_panel)

    # Create information requirements table
    req_table = Table(
        title="[bold green]📋 REQUIRED INFORMATION[/bold green]"
    )
    req_table.add_column("Field", style="green bold")
    req_table.add_column("Description", style="white")

    req_table.add_row("✅ Product Name", "The name of your product")
    req_table.add_row(
        "✅ Product Category", "Electronics, Fashion, Food, etc."
    )
    req_table.add_row(
        "✅ Product Description", "Brief description of the product"
    )
    req_table.add_row(
        "✅ Key Features", "Main features (list with dashes)"
    )
    req_table.add_row(
        "✅ Target Audience", "Who will buy this product"
    )

    # Create optional information table
    opt_table = Table(
        title="[bold yellow]📝 OPTIONAL INFORMATION[/bold yellow]"
    )
    opt_table.add_column("Field", style="yellow bold")
    opt_table.add_column("Description", style="white")

    opt_table.add_row("🎨 Brand Colors", "Hex codes or color names")
    opt_table.add_row("💰 Price Range", "e.g., $50-100 or $299")
    opt_table.add_row(
        "⭐ Unique Selling Points", "What makes it special"
    )
    opt_table.add_row(
        "📐 Custom Requirements", "Any special requirements"
    )
    opt_table.add_row(
        "🖼️ Master Image Path", "Path to reference image"
    )

    console.print("\n")
    console.print(req_table)
    console.print("\n")
    console.print(opt_table)

    # Smart input panel
    smart_input_text = Text(
        "💡 SMART INPUT: Paste everything in any format - AI will understand!",
        style="bold blue",
    )
    smart_panel = Panel(
        Align.center(smart_input_text),
        border_style="blue",
        box=box.ROUNDED,
    )

    console.print("\n")
    console.print(smart_panel)

    # Example input panel with syntax highlighting
    example_text = """Product Name: AirPods Pro Max Elite
Product Category: Electronics
Product Description: Premium wireless headphones with spatial audio
Key Features:
- Active noise cancellation
- Spatial audio technology
- 40-hour battery life

Target Audience: Audio professionals and tech enthusiasts
Brand Colors: #1d1d1f, #f5f5f7, #007aff
Price Range: $549-599
Unique Selling Points:
- Industry-leading noise cancellation
- Studio-quality sound reproduction

Custom Requirements: Focus on premium materials
Master Reference Image Path: /path/to/image.jpg"""

    example_syntax = Syntax(
        example_text, "yaml", theme="monokai", line_numbers=False
    )
    example_panel = Panel(
        example_syntax,
        title="[bold cyan]📥 EXAMPLE INPUT FORMAT[/bold cyan]",
        border_style="cyan",
    )

    console.print("\n")
    console.print(example_panel)

    # Input instruction panel
    input_instruction = Panel(
        "[bold white]📝 PASTE YOUR PRODUCT INFORMATION BELOW:[/bold white]\n[dim](Press Enter twice when finished)[/dim]",
        border_style="white",
        box=box.SIMPLE,
    )

    console.print("\n")
    console.print(input_instruction)
    console.print("[dim]⬇" * 60 + "[/dim]")

    # Collect all input lines
    lines = []
    empty_count = 0

    while True:
        try:
            line = input()
            if not line.strip():
                empty_count += 1
                if empty_count >= 2:  # Two empty lines = end input
                    break
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            console.print("\n[red]❌ Input cancelled by user.[/red]")
            return get_product_information_interactive()

    # Join all lines into one text for intelligent parsing
    full_text = " ".join(lines).strip()

    if not full_text:
        console.print(
            "\n[red]❌ No input received. Please try again.[/red]"
        )
        return get_product_information_interactive()

    # Analysis status with Rich
    with Status(
        f"[bold green]🔍 Analyzing your input ({len(full_text)} characters)...",
        console=console,
    ) as status:
        status.update(
            "[bold blue]🤖 AI Agent is extracting structured information..."
        )
        time.sleep(1)

    product_data = {}

    # Smart parsing using the Product Interpreter Agent
    from swarms import Agent

    parser_agent = Agent(
        agent_name="Smart-Input-Parser",
        agent_description="Extracts structured product information from unstructured text",
        model_name="gemini/gemini-2.5-flash",
        max_loops=1,
        dynamic_temperature_enabled=True,
    )

    parsing_prompt = f"""
    You are an expert product information extractor. Extract structured data from the following unstructured product information text.

    INPUT TEXT:
    {full_text}

    Extract and return ONLY a JSON object with these exact fields (no additional text or explanations):
    {{
        "name": "product name",
        "category": "product category", 
        "description": "product description",
        "features": ["feature1", "feature2", "feature3"],
        "target_audience": "target audience description",
        "brand_colors": ["#color1", "#color2"],
        "price_range": "price range",
        "usp": ["usp1", "usp2"],
        "custom_requirements": "any custom requirements mentioned",
        "master_image_path": "image path if mentioned or empty string"
    }}

    EXTRACTION RULES:
    1. Extract product name from "Product Name:" or infer from context
    2. Find category from "Product Category:" or infer (Electronics, Fashion, etc.)
    3. Get description from "Product Description:" or similar phrases
    4. Extract features from lists with "-" bullets or numbered items
    5. Find target audience from "Target Audience:" or similar
    6. Extract hex color codes (#123456) or color names
    7. Find price information ($X-Y or $X format)
    8. Extract USPs/selling points from relevant sections
    9. Get custom requirements if mentioned
    10. Find image path if provided

    Return ONLY the JSON object, no other text.
    """

    try:
        result = parser_agent.run(parsing_prompt)

        # Try to extract JSON from the result
        import json
        import re

        # Look for JSON object in the response
        json_match = re.search(r"\{.*\}", result, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                parsed_data = json.loads(json_str)

                # Validate and clean the parsed data
                product_data = {
                    "name": str(parsed_data.get("name", "")).strip(),
                    "category": (
                        str(parsed_data.get("category", "")).strip()
                    ),
                    "description": (
                        str(
                            parsed_data.get("description", "")
                        ).strip()
                    ),
                    "features": [
                        str(f).strip()
                        for f in parsed_data.get("features", [])
                        if str(f).strip()
                    ],
                    "target_audience": (
                        str(
                            parsed_data.get("target_audience", "")
                        ).strip()
                    ),
                    "brand_colors": [
                        str(c).strip()
                        for c in parsed_data.get("brand_colors", [])
                        if str(c).strip()
                    ],
                    "price_range": (
                        str(
                            parsed_data.get("price_range", "")
                        ).strip()
                    ),
                    "usp": [
                        str(u).strip()
                        for u in parsed_data.get("usp", [])
                        if str(u).strip()
                    ],
                    "custom_requirements": (
                        str(
                            parsed_data.get("custom_requirements", "")
                        ).strip()
                    ),
                    "master_image_path": (
                        str(
                            parsed_data.get("master_image_path", "")
                        ).strip()
                    ),
                }

                console.print(
                    "[bold green]✅ AI parsing successful![/bold green]"
                )

            except json.JSONDecodeError:
                console.print(
                    "[yellow]⚠️ AI response format issue, using fallback parsing...[/yellow]"
                )
                product_data = fallback_manual_parsing(full_text)
        else:
            console.print(
                "[yellow]⚠️ No JSON found in AI response, using fallback parsing...[/yellow]"
            )
            product_data = fallback_manual_parsing(full_text)

    except Exception as e:
        console.print(f"[red]⚠️ AI parsing failed: {str(e)}[/red]")
        console.print(
            "[yellow]🔧 Using fallback manual parsing...[/yellow]"
        )
        product_data = fallback_manual_parsing(full_text)

    # Set defaults for empty fields
    if not product_data.get("features"):
        product_data["features"] = []
    if not product_data.get("brand_colors"):
        product_data["brand_colors"] = ["#000000", "#FFFFFF"]
    if not product_data.get("usp"):
        product_data["usp"] = []
    if "custom_requirements" not in product_data:
        product_data["custom_requirements"] = ""
    if "master_image_path" not in product_data:
        product_data["master_image_path"] = ""

    # Display parsed information using Rich table
    info_table = Table(
        title="[bold green]📊 EXTRACTED PRODUCT INFORMATION[/bold green]"
    )
    info_table.add_column("Field", style="cyan bold", width=20)
    info_table.add_column("Value", style="white")

    info_table.add_row("📦 Name", product_data.get("name", "N/A"))
    info_table.add_row(
        "🏷️ Category", product_data.get("category", "N/A")
    )
    info_table.add_row(
        "📝 Description", product_data.get("description", "N/A")
    )

    # Features handling
    features = product_data.get("features", [])
    if features:
        features_display = "\n".join(
            [
                f"{i}. {feature}"
                for i, feature in enumerate(features[:3], 1)
            ]
        )
        if len(features) > 3:
            features_display += (
                f"\n... and {len(features) - 3} more features"
            )
        info_table.add_row(
            f"⚙️ Features ({len(features)})", features_display
        )
    else:
        info_table.add_row("⚙️ Features", "None specified")

    info_table.add_row(
        "👥 Target Audience",
        product_data.get("target_audience", "N/A"),
    )

    # Brand colors
    if product_data.get("brand_colors"):
        colors_str = ", ".join(product_data["brand_colors"])
        info_table.add_row("🎨 Brand Colors", colors_str)

    info_table.add_row(
        "💰 Price Range", product_data.get("price_range", "N/A")
    )

    # USPs handling
    usps = product_data.get("usp", [])
    if usps:
        usps_display = "\n".join(
            [f"{i}. {usp}" for i, usp in enumerate(usps[:2], 1)]
        )
        if len(usps) > 2:
            usps_display += f"\n... and {len(usps) - 2} more USPs"
        info_table.add_row(f"⭐ USPs ({len(usps)})", usps_display)

    # Optional fields
    if product_data.get("custom_requirements"):
        info_table.add_row(
            "📐 Custom Requirements",
            product_data["custom_requirements"],
        )

    if product_data.get("master_image_path"):
        info_table.add_row(
            "🖼️ Master Image", product_data["master_image_path"]
        )

    console.print("\n")
    console.print(info_table)

    # Auto-confirm if all required data is present
    required_fields = [
        "name",
        "category",
        "description",
        "target_audience",
    ]
    missing_fields = [
        field
        for field in required_fields
        if not product_data.get(field)
    ]

    if not missing_fields:
        success_panel = Panel(
            "[bold green]🎉 ALL REQUIRED INFORMATION SUCCESSFULLY EXTRACTED![/bold green]\n[green]✅ Ready to generate marketing content![/green]",
            border_style="green",
            box=box.ROUNDED,
        )
        console.print("\n")
        console.print(success_panel)
        return product_data
    else:
        warning_text = f"⚠️ MISSING INFORMATION: {', '.join(missing_fields)}\nThe system can still work with incomplete information."
        warning_panel = Panel(
            warning_text,
            title="[yellow]Warning[/yellow]",
            border_style="yellow",
        )
        console.print("\n")
        console.print(warning_panel)

        confirm = Confirm.ask(
            "\n[bold cyan]🤔 Proceed with available information?[/bold cyan]"
        )
        if confirm:
            console.print(
                "[green]✅ Proceeding with available information...[/green]"
            )
            return product_data
        else:
            console.print(
                "[yellow]🔄 Please provide the information again with missing details.[/yellow]"
            )
            return get_product_information_interactive()


def fallback_manual_parsing(text: str) -> Dict[str, Any]:
    """Fallback manual parsing when AI parsing fails"""
    import re

    product_data = {}
    text_lower = text.lower()

    # Extract product name
    name_patterns = [
        r"product name[:\s]+([^.\n]+)",
        r"name[:\s]+([^.\n]+)",
        r"^([A-Z][^.]*(?:pro|max|elite|plus)[^.]*)",  # Common product naming patterns
    ]

    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            product_data["name"] = match.group(1).strip()
            break

    # Extract category
    category_patterns = [
        r"product category[:\s]+([^.\n]+)",
        r"category[:\s]+([^.\n]+)",
    ]

    for pattern in category_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            product_data["category"] = match.group(1).strip()
            break

    # If no explicit category, try to infer
    if "category" not in product_data:
        if any(
            word in text_lower
            for word in ["headphone", "audio", "speaker", "earphone"]
        ):
            product_data["category"] = "Electronics"
        elif any(
            word in text_lower
            for word in ["shoe", "sneaker", "boot", "clothing"]
        ):
            product_data["category"] = "Fashion"
        elif any(
            word in text_lower
            for word in ["food", "drink", "beverage"]
        ):
            product_data["category"] = "Food & Beverage"

    # Extract description
    desc_patterns = [
        r"product description[:\s]+([^.\n]+)",
        r"description[:\s]+([^.\n]+)",
    ]

    for pattern in desc_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            product_data["description"] = match.group(1).strip()
            break

    # Extract target audience
    audience_patterns = [
        r"target audience[:\s]+([^.\n]+)",
        r"audience[:\s]+([^.\n]+)",
    ]

    for pattern in audience_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            product_data["target_audience"] = match.group(1).strip()
            break

    # Extract features (lines starting with -)
    features = re.findall(r"-\s*(.+)", text)
    product_data["features"] = [
        f.strip() for f in features if f.strip()
    ]

    # Extract colors (hex codes)
    colors = re.findall(r"#[0-9a-fA-F]{6}", text)
    product_data["brand_colors"] = colors if colors else []

    # Extract price range
    price_match = re.search(r"\$[\d,]+-[\d,]+|\$[\d,]+", text)
    if price_match:
        product_data["price_range"] = price_match.group()

    # Extract USPs (look for selling points)
    usp_section = re.search(
        r"unique selling points?[:\s]*(.*?)(?=\n\n|\nCustom|\nMaster|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if usp_section:
        usps = re.findall(r"-\s*(.+)", usp_section.group(1))
        product_data["usp"] = [u.strip() for u in usps if u.strip()]

    return product_data
