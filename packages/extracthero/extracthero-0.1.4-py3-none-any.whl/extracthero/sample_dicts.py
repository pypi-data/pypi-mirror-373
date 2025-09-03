

sample_page_dict = {
    "store_name": "Example Store",
    "promo_banner": "🔥 Flash Sale: Up to 50% off! 🔥",
    "products": [
        {
            "title": "Wireless Keyboard Pro",
            "description": (
                "Ergonomic backlit keyboard with rechargeable battery "
                "and adjustable tilt."
            ),
            "list_price": "€59.99",
            "current_price": "€49.99",
            "rating": 4.5,                       # pulled from data-rating="4.5"
            "availability": "In Stock",
            "features": [
                "Bluetooth 5.0",
                "USB-C charging",
                "Full-size layout",
            ],
            "primary": True                      # hero product flag (optional)
        },
        {
            "title": "USB-C Hub",
            "description": (
                "6-in-1 hub with HDMI, Ethernet, SD-card reader and two USB-A ports."
            ),
            "current_price": "€29.50",
            "availability": "Only 3 left!",
            "primary": False
        },
        {
            "title": "Gaming Mouse",
            "description": "High-precision mouse with RGB lighting.",
            "current_price": "$35.00",
            "availability": "Out of Stock",
            "primary": False
        }
    ],
    "newsletter_signup": True,
    "copyright": "© 2025 Example Store"
}