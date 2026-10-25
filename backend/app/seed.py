"""Demo catalog (home electronics & appliances). Runs automatically on first start when the DB is empty.

Brands are fictional. Images are placeholders from picsum.photos - replace image_url/images with real photos.
"""
from sqlalchemy import func, select

from .database import SessionLocal
from .models import Category, Product


def img(seed: str, w: int = 900, h: int = 900) -> str:
    return f"https://picsum.photos/seed/{seed}/{w}/{h}"


CATEGORIES = [
    ("Kitchen", "kitchen"),
    ("Laundry & Dishwashing", "laundry"),
    ("Cooling & Heating", "climate"),
    ("Cleaning", "cleaning"),
    ("TV & Audio", "tv-audio"),
    ("Smart Home", "smart-home"),
]

# name, category, price $, brand, energy rating, warranty months, stock, short description, specs
P = [
    ("Air Fryer XL 5.5L", "kitchen", 129, "CasaChef", "", 24, 40,
     "Crisp, golden results with up to 85% less oil. Eight one-touch presets and a dishwasher-safe basket make weeknight dinners effortless.",
     {"Capacity": "5.5 L", "Power": "1700 W", "Presets": "8", "Temperature": "80–200 °C"}),
    ("Smart Espresso Machine 15 Bar", "kitchen", 349, "CasaChef", "", 24, 18,
     "Café-quality espresso at home. Built-in conical grinder, steam wand and app control for your favourite recipes.",
     {"Pressure": "15 bar", "Water tank": "1.8 L", "Grinder": "Built-in conical", "Connectivity": "Wi-Fi + app"}),
    ("Stand Mixer 1000W", "kitchen", 279, "CasaChef", "", 36, 22,
     "A powerhouse for dough, batter and whipping. Tilt-head design, 5 L stainless bowl and three attachments included.",
     {"Power": "1000 W", "Bowl": "5 L stainless steel", "Speeds": "10 + pulse", "Attachments": "Hook, whisk, beater"}),
    ("Glass Electric Kettle 1.7L", "kitchen", 39, "CasaChef", "", 24, 120,
     "Fast-boil borosilicate glass kettle with blue LED, auto shut-off and boil-dry protection.",
     {"Capacity": "1.7 L", "Power": "2200 W", "Material": "Borosilicate glass", "Safety": "Auto shut-off"}),
    ("French Door Refrigerator 520L", "kitchen", 1499, "FrostLine", "C", 60, 8,
     "Generous no-frost fridge-freezer with water dispenser, dual cooling and a quiet inverter compressor.",
     {"Capacity": "520 L", "Cooling": "Dual no-frost", "Noise": "38 dB", "Dimensions": "91 × 70 × 178 cm"}),
    ("Microwave Oven 28L with Grill", "kitchen", 169, "CasaChef", "", 24, 35,
     "Reheat, defrost, grill and cook with 10 auto menus and a 28 L cavity that fits a large dinner plate.",
     {"Capacity": "28 L", "Power": "900 W + 1000 W grill", "Auto menus": "10", "Control": "Digital + dial"}),

    ("Front-Load Washing Machine 9kg", "laundry", 649, "PureWash", "A", 60, 14,
     "Inverter motor, steam hygiene cycle and 1400 rpm spin. Quiet, efficient and gentle on fabrics.",
     {"Capacity": "9 kg", "Spin": "1400 rpm", "Programmes": "16", "Noise (wash)": "49 dB"}),
    ("Heat Pump Tumble Dryer 8kg", "laundry", 799, "PureWash", "A", 60, 10,
     "Energy-saving heat pump technology dries gently at low temperature, saving up to 50% energy vs. a vented dryer.",
     {"Capacity": "8 kg", "Type": "Heat pump", "Programmes": "14", "Drum": "Reverse tumble"}),
    ("Dishwasher 14 Place Settings", "laundry", 599, "PureWash", "B", 36, 16,
     "Spotless results with a third rack, half-load option and a 44 dB whisper-quiet motor.",
     {"Capacity": "14 place settings", "Programmes": "8", "Noise": "44 dB", "Extras": "3rd cutlery rack"}),
    ("Washer-Dryer Combo 10/6kg", "laundry", 899, "PureWash", "B", 48, 9,
     "Wash and dry in a single machine. Ideal for apartments: one footprint, 10 kg wash and 6 kg dry capacity.",
     {"Wash / dry": "10 kg / 6 kg", "Spin": "1400 rpm", "Wi-Fi": "Yes", "Steam": "Yes"}),

    ("Inverter Air Conditioner 12000 BTU", "climate", 599, "AeroCool", "A", 36, 20,
     "Cool in summer, heat in winter with a quiet inverter compressor and Wi-Fi control from your phone.",
     {"Capacity": "12,000 BTU", "Mode": "Cooling + heating", "Noise": "24 dB (indoor)", "Wi-Fi": "Yes"}),
    ("HEPA Air Purifier", "climate", 189, "AeroCool", "", 24, 32,
     "True HEPA H13 filtration removes 99.97% of dust, pollen and smoke particles. Covers rooms up to 40 m².",
     {"Filter": "True HEPA H13", "Coverage": "40 m²", "CADR": "320 m³/h", "Noise": "22–52 dB"}),
    ("Ceramic Tower Heater 2000W", "climate", 69, "AeroCool", "", 24, 55,
     "Safe, fast-heating tower with thermostat, oscillation, remote control and tip-over protection.",
     {"Power": "2000 W", "Settings": "3 + eco", "Timer": "12 h", "Safety": "Tip-over + overheat"}),
    ("Dehumidifier 20L/day", "climate", 219, "AeroCool", "B", 24, 18,
     "Keeps damp and mould away with a 20 L/day capacity, laundry mode and continuous drainage option.",
     {"Capacity": "20 L/day", "Tank": "4 L", "Humidity range": "30–80%", "Modes": "Auto, laundry, continuous"}),
    ("Quiet Tower Fan", "climate", 89, "AeroCool", "", 24, 60,
     "Slim 105 cm tower fan with 5 speeds, natural-wind mode and a 8-hour timer, whisper-quiet at night.",
     {"Height": "105 cm", "Speeds": "5", "Timer": "8 h", "Remote": "Yes"}),

    ("Cordless Stick Vacuum", "cleaning", 299, "PureWash", "", 24, 28,
     "60-minute runtime, anti-tangle brush and a washable HEPA filter. Converts to a handheld in one click.",
     {"Runtime": "Up to 60 min", "Suction": "25,000 Pa", "Bin": "0.8 L", "Battery": "Removable, 2500 mAh"}),
    ("Robot Vacuum & Mop", "cleaning", 449, "NovaSmart", "", 24, 15,
     "LiDAR mapping, self-emptying dock and a vibrating mop. Schedule rooms and set no-go zones in the app.",
     {"Suction": "5000 Pa", "Navigation": "LiDAR", "Dock": "Self-emptying", "Runtime": "180 min"}),
    ("Steam Mop 1500W", "cleaning", 79, "PureWash", "", 24, 40,
     "Sanitises sealed floors with just water. Heats in 30 seconds and comes with two washable pads.",
     {"Power": "1500 W", "Tank": "400 ml", "Heat-up": "30 s", "Cable": "5 m"}),
    ("Handheld Car & Home Vacuum", "cleaning", 49, "PureWash", "", 12, 85,
     "Compact, powerful and cordless, with crevice and brush tools for car seats, sofas and shelves.",
     {"Suction": "9000 Pa", "Runtime": "25 min", "Charging": "USB-C", "Weight": "0.7 kg"}),

    ('55" 4K Smart TV', "tv-audio", 499, "SonicHome", "F", 24, 12,
     "Vivid 4K HDR display with built-in streaming apps, voice remote and three HDMI ports (one eARC).",
     {"Screen": "55 inch", "Resolution": "3840 × 2160 (4K)", "HDR": "HDR10 / HLG", "Refresh": "60 Hz"}),
    ("Soundbar 2.1 with Wireless Subwoofer", "tv-audio", 199, "SonicHome", "", 24, 30,
     "Fill the room with deep bass and clear dialogue. HDMI eARC, Bluetooth 5.3 and three sound modes.",
     {"Power": "300 W", "Channels": "2.1", "Connectivity": "HDMI eARC, Bluetooth, optical", "Subwoofer": "Wireless"}),
    ("Waterproof Bluetooth Speaker", "tv-audio", 59, "SonicHome", "", 12, 90,
     "360° sound, IP67 waterproof and dustproof, with 20 hours of playtime. Take it from the kitchen to the garden.",
     {"Battery": "20 h", "Rating": "IP67", "Bluetooth": "5.3", "Charging": "USB-C"}),

    ("Smart Thermostat", "smart-home", 129, "NovaSmart", "", 24, 45,
     "Learns your routine and cuts heating costs. Works with major voice assistants and remote control via app.",
     {"Display": "Colour touch", "Connectivity": "Wi-Fi", "Compatibility": "Most 24 V systems", "Voice": "Alexa / Google"}),
    ("2K Video Doorbell", "smart-home", 149, "NovaSmart", "", 24, 38,
     "See who's at the door in crisp 2K with night vision, two-way talk and instant motion alerts.",
     {"Video": "2K HDR", "Night vision": "Yes", "Power": "Battery or wired", "Storage": "Cloud or microSD"}),
    ("Smart Plug 4-Pack", "smart-home", 34, "NovaSmart", "", 12, 150,
     "Control lamps and appliances from your phone, set schedules and monitor energy use.",
     {"Pack": "4 plugs", "Load": "10 A / 2300 W", "Connectivity": "Wi-Fi 2.4 GHz", "Energy monitor": "Yes"}),
    ("Wi-Fi 6 Mesh Router (3-Pack)", "smart-home", 229, "NovaSmart", "", 36, 25,
     "Blanket your whole home in fast, stable Wi-Fi 6. Covers up to 480 m² with seamless roaming.",
     {"Standard": "Wi-Fi 6 (AX3000)", "Coverage": "480 m²", "Ports": "2 × Gigabit per unit", "Setup": "App, 5 minutes"}),
]

FEATURES = (
    "\n\n• Free delivery on orders over $99\n• 30-day returns\n• Manufacturer warranty included\n"
    "• Installation & recycling of your old appliance available at checkout (coming soon)"
)


def slugify(s: str) -> str:
    return "-".join("".join(c.lower() if c.isalnum() else " " for c in s).split())


def seed() -> None:
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(Product)):
            return
        cats = {}
        for name, slug in CATEGORIES:
            c = Category(name=name, slug=slug, image_url=img(f"volta-cat-{slug}", 800, 1000))
            db.add(c)
            cats[slug] = c
        db.flush()
        for name, cat, price, brand, energy, warranty, stock, desc, specs in P:
            slug = slugify(name)
            db.add(
                Product(
                    name=name,
                    slug=slug,
                    description=desc + FEATURES,
                    price_cents=price * 100,
                    image_url=img(slug),
                    images=[img(slug), img(slug + "-2"), img(slug + "-3"), img(slug + "-4")],
                    stock=stock,
                    brand=brand,
                    energy_rating=energy,
                    warranty_months=warranty,
                    specs=specs,
                    category_id=cats[cat].id,
                )
            )
        db.commit()


if __name__ == "__main__":
    from database import Base, engine

    Base.metadata.create_all(engine)
    seed()
    print("Seeded.")
