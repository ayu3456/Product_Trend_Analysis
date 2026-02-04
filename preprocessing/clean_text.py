import re
import emoji
import logging
from typing import Optional

# Setup logging
logger = logging.getLogger(__name__)

class TextPreprocessor:
    def __init__(self):
        # Pre-compile regex for efficiency
        self.url_pattern = re.compile(r'http\S+|www\S+|https\S+')
        self.mention_pattern = re.compile(r'@\w+')
        self.hashtag_pattern = re.compile(r'#\w+')
        self.whitespace_pattern = re.compile(r'\s+')
        self.special_chars_pattern = re.compile(r'[^a-zA-Z0-9\s!\?\.]')

    def clean(self, text: str) -> str:
        """
        Cleans the input text:
        - Removes URLs
        - Removes mentions (@user)
        - Removes hashtags (#topic)
        - Converts emojis to text descriptions
        - Normalizes whitespace
        - Keeps basic punctuation for sentiment context (! ? .)
        """
        if not text:
            return ""

        try:
            # Convert emojis to text: 😄 -> :grinning_face:
            text = emoji.demojize(text)
            
            # Remove URLs
            text = self.url_pattern.sub('', text)
            
            # Remove mentions
            text = self.mention_pattern.sub('', text)
            
            # Remove hashtags (decidable if we want to keep the text but remove the #)
            # For now, let's remove the tag entirely to focus on sentiment text
            text = self.hashtag_pattern.sub('', text)
            
            # Remove special characters except basic punctuation
            text = self.special_chars_pattern.sub(' ', text)
            
            # Normalize whitespace
            text = self.whitespace_pattern.sub(' ', text).strip()
            
            # Convert to lowercase
            text = text.lower()
            
            return text
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text

if __name__ == "__main__":
    preprocessor = TextPreprocessor()
    sample = "I love this product! 😄 Check it out at https://example.com #awesome @user"
    cleaned = preprocessor.clean(sample)
    print(f"Original: {sample}")
    print(f"Cleaned: {cleaned}")
