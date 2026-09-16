"""
Dynamic Prompt Engine - Maira Dash
Generates rich, highly diverse, non-repeating prompts for ChatGPT image generation.

Persona & Demographics:
- 23-year-old Indian woman, single girl, curvy pear-shaped physique
- Social media influencer, fashion model, student, fitness model
- Passions & Themes:
  - Fitness, gym, workout, yoga, jogging, active lifestyle
  - Fashion modeling, chic styling, modern western and Indian traditional attire
  - Student life, campus, library study, creative workspaces
  - Dancing, nightclub, night out, rooftop lounges, cinema/movies
  - Foodie adventures: fast foods (burgers, fries, momos), aesthetic cafes, fine dining hotels, street food
  - Odisha tourist gems: Konark, Puri beach, Lingaraj, Chilika, Daringbadi, Simlipal
  - Travel across India: Kashmir, Mumbai, Delhi, Jaipur, Kerala, Hyderabad, Bangalore, Uttarakhand, Northeast, Nepal
  - International travel: Dubai, Thailand, Vietnam, UK, US, Canada, New Zealand, China, Japan
  - Nature, forests, hill stations, beaches, waterfalls

Guarantees:
- Strictly enforces 9:16 vertical mobile aspect ratio (1024x1792 portrait orientation)
- Outfits contextually harmonize with the scene while varying dynamically
- Tracks history in 'logs/prompt_history.json' to ensure prompts never repeat consecutively
"""

import random
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("AgentLogger")

THEMES = {
    "fitness_workout_yoga": [
        "in a modern high-end gym, holding light dumbbells during an energizing workout session, smiling confidently with glowing fit skin",
        "practicing peaceful morning yoga on a scenic outdoor wooden deck overlooking green nature, in a graceful yoga pose, radiant morning sunbeams, showing healthy flexibility and fitness posture",
        "enjoying an early morning jog on a scenic tree-lined park running path, high ponytail, energetic and refreshing sunrise vibe",
        "in a chic sunlit pilates and wellness studio, stretching on a yoga mat, glowing healthy complexion, confident and inspiring fitness model pose",
        "at an aesthetic post-workout juice bar, holding a fresh green detox smoothie with a joyful radiant smile"
    ],
    "fashion_modeling_glamour": [
        "posing for an editorial fashion photoshoot in a modern sunlit minimalist studio, sophisticated expression and high-fashion modeling pose",
        "in an exquisite traditional Indian festive photoshoot, with delicate golden embroidery and matching traditional earrings, gracefully smiling",
        "standing against a heritage architectural sandstone archway, glowing with timeless Indian beauty and graceful poise",
        "posing on a vibrant urban street in chic modern fashion, with fashionable sunglasses, looking like a top fashion influencer",
        "modeling beside an exotic luxury resort turquoise infinity pool, gentle breeze playing with her hair, glamorous and effortless model aesthetic"
    ],
    "student_campus_life": [
        "sitting in a grand sunlit university library at a polished wooden study desk, reading books with her laptop open, smart glasses, smiling warmly",
        "walking across a lush green college campus courtyard with a stylish backpack over one shoulder, holding study notebooks, cheerful and approachable college student vibe",
        "working productively on an aesthetic cafe table with a modern laptop, highlighter pens, and an iced latte, focused yet cheerful student lifestyle moment",
        "hanging out on college campus lawn under shady flowering trees with classmates, candid laughter and youthful student energy"
    ],
    "nightlife_club_dance": [
        "at an upscale high-energy dance club with vibrant ambient neon lights and party atmosphere, dancing happily with joyful expression",
        "enjoying an exciting night out at a chic open-air rooftop cocktail lounge overlooking dazzling city skyline lights, holding a colorful mocktail, smiling radiantly",
        "on a fun weekend cinema and movie date night at a luxury cinema theatre lounge, holding gourmet popcorn, bright cheerful smile",
        "celebrating at an aesthetic music lounge with friends, soft warm party bokeh lights, dancing gracefully and radiating glamorous influencer charisma"
    ],
    "food_dining_fastfood": [
        "sitting at a trendy aesthetic diner booth happily enjoying delicious fast food, with a gourmet cheese burger, crispy french fries, and a tall milkshake, candid joyful expression",
        "at a vibrant street food promenade, tasting delicious hot steamed momos with spicy chutney, candid happy foodie smile in an authentic lively atmosphere",
        "enjoying an exquisite fine dining experience at a 5-star luxury hotel restaurant, beautifully set candlelit table with artisan cuisine",
        "at a charming sunlit brunch cafe on a garden patio, enjoying fresh Belgian waffles, avocado toast, and cappuccino with latte art, glowing morning aesthetics",
        "stopping by a trendy dessert boutique, happily enjoying a colorful boba bubble tea and artisan gelato scoop, playful and cute expression"
    ],
    "odisha_heritage_beaches": [
        "visiting the majestic Konark Sun Temple in Odisha, standing near the ancient carved stone chariot wheels, morning golden light illuminating the historic Kalinga architecture",
        "walking along the pristine shoreline of Puri Golden Beach, gentle ocean waves lapping at the sand, cool sea breeze with a vibrant golden sunrise reflecting on the Bay of Bengal",
        "at the grand entrance of Puri Jagannath Temple, holding hands in peaceful respectful Namaste, traditional temple architecture in the backdrop, serene spiritual glow",
        "standing at the ancient Lingaraj Temple in Bhubaneswar, surrounded by sacred sandstone carvings and tranquil spiritual ambiance",
        "on a scenic eco-tourism wooden boat exploring the tranquil blue waters of Chilika Lake, migratory birds and scenic coastal hills in the background",
        "standing on the misty pine-covered hilltops of Daringbadi (the Kashmir of Odisha), surrounded by lush coffee plantations and cool morning mountain mist",
        "exploring the lush green sal forests and waterfall mist of Simlipal National Park, standing on a wooden footbridge surrounded by pristine tropical nature",
        "walking on the picturesque Marine Drive road between Puri and Konark, ocean breeze blowing her hair, scenic coastal road with coconut palms"
    ],
    "india_travel": [
        "in the breathtaking snowy paradise of Gulmarg, Kashmir, standing against majestic snow-covered Himalayan peaks",
        "on a romantic decorated wooden Shikara boat ride on the calm waters of Dal Lake in Srinagar, Kashmir, surrounded by floating lotus gardens and misty mountains",
        "walking along Mumbai's iconic Marine Drive promenade at sunset, overlooking the Arabian Sea and the Queen's Necklace skyline, cool sea breeze and lively city vibes",
        "exploring the grand royal courtyards of Amer Fort in Jaipur, Rajasthan, intricate Rajput architecture and sandstone pavilions",
        "relaxing on the sundeck of a traditional luxury houseboat cruising the serene palm-fringed backwaters of Alleppey, Kerala, tranquil tropical scenery",
        "in a vibrant aesthetic cafe in South Delhi, lush greenery and artistic decor, enjoying artisan coffee",
        "standing near the iconic Charminar in Hyderabad, exploring the historic pearl bazaars and heritage culture",
        "enjoying a morning walk in Bangalore's lush green Cubbon Park, bamboo groves and heritage red buildings, fresh morning air and vibrant lifestyle",
        "at a serene yoga ashram riverbank in Rishikesh, Uttarakhand, overlooking the holy emerald Ganges river and suspension bridge at sunrise",
        "exploring the breathtaking living root bridges and misty waterfalls of Cherrapunji, Meghalaya in Northeast India, lush green rainforest beauty",
        "at Patan Durbar Square in Nepal, surrounded by historic carved wooden temples and ancient pagoda architecture with misty Himalayan backdrop"
    ],
    "international_travel": [
        "on the deck of a luxury yacht cruising past the futuristic skyscrapers of Dubai Marina, with the iconic Burj Khalifa skyline in the background",
        "on a thrilling golden desert safari in Dubai, standing atop soft red sand dunes during golden hour",
        "on a tropical white-sand beach in Phuket, Thailand, crystal-clear turquoise waters and dramatic limestone karst islands in the background",
        "cruising on a scenic wooden junk boat through the emerald waters and towering limestone pillars of Ha Long Bay, Vietnam, serene morning mist",
        "walking through the magical lantern-lit ancient streets of Hoi An, Vietnam, colorful silk lanterns glowing around her, vibrant evening travel atmosphere",
        "standing near London's iconic Tower Bridge along the River Thames in the UK, classic British travel aesthetic",
        "at the vibrant, glowing heart of Times Square in New York City, USA, surrounded by colorful giant billboard lights",
        "at the edge of pristine turquoise Lake Louise in Banff National Park, Canada, majestic snow-dusted Rocky Mountains and tall pine trees reflected in the water",
        "standing at the panoramic lakefront viewpoint in Queenstown, New Zealand, deep blue glacial lake and soaring mountain peaks under clear blue sky",
        "walking along the iconic traditional wooden street of Gion in Kyoto, Japan, with red Torii gates and blooming cherry blossom trees in the background",
        "standing along the historic Shanghai Bund waterfront in China, admiring the futuristic illuminated Pudong skyline across the river at dusk"
    ],
    "nature_forest_hillstations": [
        "standing on a tranquil mountain hill station viewpoint overlooking rolling clouds and mist-filled green valleys, cool mountain air, relaxed peaceful smile",
        "walking along a peaceful forest trail with tall sun-dappled pine trees, gentle rays of sunlight filtering through the green forest canopy",
        "sitting on a smooth river stone beside a crystal-clear mountain stream, dipping feet near fresh water, surrounded by lush green flora and peaceful nature",
        "watching the sunset from a scenic coastal clifftop, golden amber sunlight bathing the sea and rocky shoreline, deeply peaceful and grateful expression"
    ]
}

CAMERA_ANGLES = [
    "Vertical 9:16 mobile portrait orientation, full environmental shot capturing her natural curvy pear-shaped silhouette and breathtaking surroundings",
    "Vertical 9:16 cinematic eye-level portrait with natural 35mm lens depth of field, creamy soft bokeh background",
    "Vertical 9:16 dynamic candid low-angle perspective, confident posture, full height and stylish outfit details",
    "Vertical 9:16 medium-close candid shot, highlighting her radiant facial features, warm expressive eyes, and natural skin texture",
    "Vertical 9:16 vertical travel-influencer lifestyle shot with authentic ambient framing and natural depth"
]

EXPRESSIONS = [
    "smiling radiantly and radiating positive, cheerful influencer energy",
    "confident, charming, and stylish expression with an effortless friendly smile",
    "relaxed, peaceful smile, in complete harmony with her beautiful surroundings",
    "candid happy laugh, looking naturally engaged, vibrant, and full of life",
    "serene, thoughtful, and deeply grateful expression looking toward the golden horizon"
]

OUTFITS_BY_CATEGORY = {
    "fitness_workout_yoga": [
        "wearing stylish matching athletic fitness gym wear with high-waisted leggings and sports crop top accentuating her curvy pear-shaped physique",
        "wearing high-performance yoga activewear in a soft pastel tone with breathable fabric and athletic silhouette",
        "wearing a trendy athleisure running outfit with sleek sneakers, athletic shorts, and sporty top"
    ],
    "fashion_modeling_glamour": [
        "wearing a stunning high-fashion bodycon dress highlighting her natural curves and pear-shaped silhouette",
        "wearing an exquisite pastel pink designer lehenga with delicate golden embroidery and statement jewelry",
        "wearing a contemporary designer saree with an elegant modern blouse and graceful drape",
        "wearing chic modern streetwear featuring tailored high-waisted trousers and a stylish fitted corset top"
    ],
    "student_campus_life": [
        "wearing a cute casual collegiate outfit with fitted denim and a stylish cozy cardigan",
        "wearing smart-casual university attire with chic spectacles and a soft pastel pullover",
        "wearing trendy campus streetwear with a stylish canvas tote and clean sneakers"
    ],
    "nightlife_club_dance": [
        "wearing a glamorous sparkling party dress flattering her curvy pear-shaped silhouette",
        "wearing an alluring bodycon evening dress with chic heels and subtle shimmering jewelry",
        "wearing a stylish sleek modern clubwear outfit radiating confident nightlife glamour"
    ],
    "food_dining_fastfood": [
        "wearing a chic, casual brunch outfit with a flattering top and fashionable accessories",
        "wearing an elegant evening dinner dress suitable for fine dining luxury ambiance",
        "wearing a cute aesthetic pastel sweater and trendy jeans enjoying foodie moments"
    ],
    "odisha_heritage_beaches": [
        "wearing an elegant traditional Indian kurta with tasteful embroidery and silver jhumka earrings",
        "wearing a breezy floral resort sundress with coastal elegance",
        "wearing a graceful Odisha handloom saree with authentic cultural charm"
    ],
    "india_travel": [
        "wearing a stylish warm winter coat with a soft Kashmiri pashmina wrap and cozy woolen beanie",
        "wearing a vibrant contemporary ethnic fusion outfit with traditional accents",
        "wearing chic travel layers with comfortable walking boots and stylish sunglasses"
    ],
    "international_travel": [
        "wearing a sophisticated beige trench coat and ankle boots looking like a chic globe-trotter",
        "wearing an ultra-stylish jetsetter luxury travel ensemble with designer sunglasses",
        "wearing a chic summer resort outfit with a wide-brim sun hat and breezy fabrics"
    ],
    "nature_forest_hillstations": [
        "wearing a cozy oversized knit sweater with snug leggings and outdoor boots",
        "wearing a lightweight outdoor adventure jacket with sporty casual layers",
        "wearing a comfortable scenic viewpoint outfit with warm autumn tones"
    ]
}

LIGHTING_BY_SLOT = {
    "morning": "radiant early morning golden hour light, soft morning rays filtering through, refreshing and bright aesthetic",
    "noon": "vibrant natural midday ambient sunlight, crisp textures, high clarity, clean and energizing atmosphere",
    "afternoon": "warm, gentle afternoon sun with golden amber tones, cozy and inviting ambiance",
    "evening": "spectacular sunset twilight, rich amber, crimson and violet sky, dramatic cinematic golden hour rim light",
    "night": "soothing ambient nighttime lighting, subtle warm fairy lights or city lights bokeh, deep peaceful night atmosphere"
}

class PromptEngine:
    def __init__(self, history_file="logs/prompt_history.json"):
        self.history_file = Path(history_file).resolve()
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history(self, history):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history[-100:], f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save prompt history: {e}")

    def generate_prompt(self, slot_key, slot_label):
        """
        Generates a non-repeating, highly specific 9:16 vertical prompt
        matching the time of day and Maira Dash's persona, physique, and interests.
        """
        history = self._load_history()
        recently_used_categories = [h.get("category") for h in history[-4:]]

        # Prioritize unused categories to ensure continuous variety
        available_categories = [cat for cat in THEMES.keys() if cat not in recently_used_categories]
        if not available_categories:
            available_categories = list(THEMES.keys())

        chosen_cat = random.choice(available_categories)
        chosen_scene = random.choice(THEMES[chosen_cat])
        chosen_angle = random.choice(CAMERA_ANGLES)
        chosen_expression = random.choice(EXPRESSIONS)
        
        # Contextually matched outfits
        cat_outfits = OUTFITS_BY_CATEGORY.get(chosen_cat, [
            "wearing a stylish high-fashion outfit highlighting her curvy pear-shaped physique"
        ])
        chosen_outfit = random.choice(cat_outfits)
        lighting = LIGHTING_BY_SLOT.get(slot_key, "beautiful natural lighting")

        # Compose prompt strictly requesting 9:16 aspect ratio & character fidelity
        prompt_text = (
            f"A photorealistic, highly detailed vertical portrait of the 23-year-old Indian woman from the reference photo, "
            f"maintaining her exact face, warm brown eyes, radiant smile, and natural curvy pear-shaped physique, {chosen_scene}. "
            f"She is {chosen_outfit}, {chosen_expression}. "
            f"{chosen_angle}. "
            f"Lighting: {lighting}. "
            "STRICT ASPECT RATIO REQUIREMENT: Must be in vertical 9:16 aspect ratio (portrait mobile phone format, 1024x1792). "
            "High resolution 8k photography, authentic lifelike human skin texture, natural anatomy, vibrant rich colors."
        )

        # Save to history
        record = {
            "timestamp": datetime.now().isoformat(),
            "slot": slot_key,
            "label": slot_label,
            "category": chosen_cat,
            "scene": chosen_scene[:80],
            "prompt": prompt_text
        }
        history.append(record)
        self._save_history(history)

        logger.info(f"Generated dynamic prompt for [{slot_label}] (Category: {chosen_cat}):\n--> {chosen_scene[:100]}...")
        return prompt_text

if __name__ == "__main__":
    engine = PromptEngine()
    for slot in ["morning", "noon", "afternoon", "evening", "night"]:
        p = engine.generate_prompt(slot, slot.capitalize())
        print(f"\n--- {slot.upper()} ---")
        print(p)
