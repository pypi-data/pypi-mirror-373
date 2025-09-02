"""Captcha utilities for Eastmoney API."""

from random import SystemRandom

from ddddocr import DdddOcr

# Initialize OCR
ocr = DdddOcr(show_ad=False)


def generate_random_number() -> float:
    """Generate a cryptographically secure random number.

    Returns:
        A random float between 0.0 and 1.0
    """
    cryptogen = SystemRandom()
    return cryptogen.random()


def recognize_captcha(image_content: bytes) -> str:
    """Recognize captcha from image content.

    Args:
        image_content: Raw image bytes

    Returns:
        Recognized captcha text
    """
    return ocr.classification(image_content)  # type: ignore
