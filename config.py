# config.py

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}

SUPPORTED_TEXT_FORMATS = {".txt", ".md", ".json", ".csv", ".xls", ".xlsx", ".html", ".docx", ".pdf"}
GPT4_OUTPUT_PRICE_PER_1000 = 0.06

# Detailed templates used for layout generation
REFERENCE_LAYOUT = {
    "book_title": "[BOOK-TITLE]",
    "modules": [
        {
            "module_title": "MODULE 1 TITLE",
            "value_proposition": "MODULE 1 SELLING POINT",
            "module_description": "A concise and engaging description of why this module is compelling."
        }
    ]
}

R_SUMMARY = "Rational template summary: ensure robust planning and validation."
A_SUMMARY = "Answer template summary: provide actionable structure."
SUBCONSCIOUS_SUMMARY = "Subconscious template summary: trigger deep introspection."
