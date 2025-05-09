import json
import re

class Translator:
    def __init__(self, translation_table_path='translation_table.json', debug=False):
        """Initialize the translator with a translation table."""
        self.debug = debug
        with open(translation_table_path, 'r') as f:
            self.table = json.load(f)
        
        # Create a reverse translation table
        self.reverse_table = {v: k for k, v in self.table.items()}
        
        # Create additional reverse mappings for case-insensitive and variations
        self.extended_reverse = {
            '0': 'o', 'O': 'o',  # o → 0
            '1': 'i', 'I': 'i',  # i → 1
            '3': 'e', 'E': 'e',  # e → 3
            '4': 'a', 'A': 'a',  # a → 4
            '7': 't', 'T': 't',  # t → 7
            '_': ' ',            # space → underscore
            '5': 's', 'S': 's',  # For other common substitutions
            '6': 'g', 'G': 'g', 
            '8': 'b', 'B': 'b',
            '9': 'g', 'G': 'g',
            '2': 'z', 'Z': 'z'
        }
        
        # Common character names for proper case normalization
        self.character_names = [
            "HOUSE", "FOREMAN", "CAMERON", "WILSON", 
            "CHASE", "CUDDY", "THIRTEEN", "TAUB"
        ]
        
        if self.debug:
            print(f"Loaded Basic Leet translation table with {len(self.table)} character mappings")
    
    def set_debug(self, debug):
        """Set debug mode on or off."""
        self.debug = debug
    
    def to_leetspeak(self, text):
        """Convert normal text to Basic Leet (vowels to numbers)."""
        result = ""
        chars_converted = 0
        
        for char in text.lower():
            if char in self.table:
                result += self.table[char]
                chars_converted += 1
            else:
                result += char
        
        if self.debug:
            print(f"Converted {chars_converted}/{len(text)} characters to Basic Leet")
            print(f"Original: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            print(f"Leetspeak: '{result[:100]}{'...' if len(result) > 100 else ''}'")
        return result
    
    def from_leetspeak(self, leetspeak):
        """Convert Basic Leet back to normal text with extended character handling."""
        if not leetspeak:
            return ""
        
        # First pass: direct replacements from our standard table
        result = leetspeak
        replacements_made = 0
        
        # Replace leet characters with normal ones
        for leet, normal in self.reverse_table.items():
            old_result = result
            result = result.replace(leet, normal)
            if old_result != result and self.debug:
                replacements_count = old_result.count(leet)
                replacements_made += replacements_count
                print(f"Replaced {replacements_count} occurrences of '{leet}' with '{normal}'")
        
        # Second pass: handle extended leet characters that might appear in responses
        for leet, normal in self.extended_reverse.items():
            old_result = result
            result = result.replace(leet, normal)
            if old_result != result and self.debug:
                replacements_count = old_result.count(leet)
                replacements_made += replacements_count
                print(f"Replaced {replacements_count} occurrences of extended '{leet}' with '{normal}'")
        
        # Third pass: fix numeric wording that might not have been caught
        numeric_fixes = {
            'io': '10', 'ii': '11', 'iz': '12', 'ie': '13', 'ia': '14', 
            'is': '15', 'ig': '16', 'it': '17', 'ib': '18', 'ig': '19',
            'zo': '20', 'zi': '21', 'zz': '22', 'ze': '23', 'za': '24',
            'zs': '25', 'zg': '26', 'zt': '27', 'zb': '28', 'zg': '29',
            'eo': '30', 'ei': '31',
            'ao': '40', 'sooo': '5000', 'iooo': '1000'
        }
        
        for leet, normal in numeric_fixes.items():
            pattern = r'\b' + re.escape(leet) + r'\b'
            old_result = result
            result = re.sub(pattern, normal, result)
            if old_result != result and self.debug:
                replacements_count = len(re.findall(pattern, old_result))
                replacements_made += replacements_count
                print(f"Replaced {replacements_count} occurrences of numeric '{leet}' with '{normal}'")
        
        if self.debug:
            print(f"Made {replacements_made} total leetspeak replacements during decoding")
        return result
    
    def contains_leetspeak(self, text):
        """Check if text contains leetspeak characters (numbers, etc.)"""
        # Look for numbers and other leet characters
        leet_indicators = re.search(r'[0-9_]', text)
        return bool(leet_indicators)
    
    def extract_leetspeak(self, response):
        """Extract leetspeak content from the Gemini response with improved extraction."""
        # Store the extraction method for debugging
        extraction_method = "none"
        
        # First check if response is empty
        if not response or len(response.strip()) == 0:
            if self.debug:
                print("Empty response received")
            return ""
        
        # Remove markdown code block markers
        response = re.sub(r'```(?:markdown)?|```', '', response)
        
        # STRATEGY 1: Extract House's dialogue (script format)
        # This looks for all House's dialogue in the script, including multiline content
        house_dialogue = []
        house_pattern = re.compile(r'(?:^|\n)\s*(?:HOUSE|HoUse)(?:\s*:|\.)?(?:\s*\([^)]*\))?\s*(.*?)(?=(?:^|\n)\s*(?:FOREMAN|CAMERON|WILSON|CHASE|CUDDY|$))', 
                                 re.DOTALL | re.MULTILINE | re.IGNORECASE)
        house_matches = house_pattern.finditer(response)
        
        for match in house_matches:
            dialogue = match.group(1).strip()
            if dialogue and self.contains_leetspeak(dialogue):
                house_dialogue.append(dialogue)
        
        if house_dialogue:
            extraction_method = "house_dialogue"
            if self.debug:
                print(f"Found {len(house_dialogue)} House dialogue segments")
            
            # Now check for bullet points within the House dialogue
            combined_dialogue = "\n".join(house_dialogue)
            bullet_pattern = re.compile(r'(?:^|\n)\s*[•*-]\s*(.*?)(?=(?:^|\n)\s*[•*-]|\Z)', 
                                      re.DOTALL | re.MULTILINE)
            bullet_matches = bullet_pattern.findall(combined_dialogue)
            
            if bullet_matches:
                extraction_method = "bullets_in_house_dialogue"
                if self.debug:
                    print(f"Found {len(bullet_matches)} bullet points in House's dialogue")
                
                # Make sure we get complete bullet points
                full_content = self._extract_full_bullet_content(combined_dialogue)
                if full_content:
                    return full_content
                return combined_dialogue
            
            # If no bullet points, return all of House's dialogue
            return combined_dialogue
        
        # STRATEGY 2: Look for bullet points anywhere
        # This captures all bullet points in the response
        if '•' in response or '*' in response or '-' in response:
            full_content = self._extract_full_bullet_content(response)
            if full_content:
                extraction_method = "bullet_points"
                if self.debug:
                    print(f"Extracted bullet points from response")
                return full_content
        
        # STRATEGY 3: Look for code blocks
        # This captures content in code blocks (```code```)
        code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)```', response, re.DOTALL)
        if code_blocks:
            extraction_method = "code_blocks"
            code_content = []
            for block in code_blocks:
                if self.contains_leetspeak(block):
                    code_content.append(block)
            
            if code_content:
                if self.debug:
                    print(f"Found {len(code_content)} code blocks with leetspeak")
                return "\n\n".join(code_content)
        
        # STRATEGY 4: Extract any paragraphs containing leetspeak
        # This looks for paragraphs with numbers (likely leetspeak)
        leet_paragraphs = []
        paragraphs = re.split(r'\n\s*\n', response)
        for para in paragraphs:
            if self.contains_leetspeak(para):
                leet_paragraphs.append(para)
        
        if leet_paragraphs:
            extraction_method = "leet_paragraphs"
            if self.debug:
                print(f"Found {len(leet_paragraphs)} paragraphs with leetspeak")
            return "\n\n".join(leet_paragraphs)
        
        # STRATEGY 5: If all above fail, return the full response
        if self.debug:
            print("No specific leetspeak pattern found, returning full response")
        extraction_method = "full_response"
        return response
    
    def _extract_full_bullet_content(self, text):
        """Helper method to extract complete bullet points from text."""
        # Find all bullet markers and their positions
        bullet_markers = list(re.finditer(r'(?:^|\n)\s*[•*-]\s+', text))
        
        if not bullet_markers:
            return None
        
        # Extract complete bullet points
        bullet_points = []
        for i, marker in enumerate(bullet_markers):
            start = marker.end()
            # If this is the last bullet point, go to the end of the text
            if i == len(bullet_markers) - 1:
                end = len(text)
            else:
                # Otherwise, go to the start of the next bullet point
                end = bullet_markers[i + 1].start()
            
            # Get the content of this bullet point
            content = text[start:end].strip()
            if content:
                bullet_points.append(content)
        
        if bullet_points:
            return "\n\n".join(bullet_points)
        return None
    
    def normalize_character_names(self, text):
        """Convert mixed-case character names to proper case"""
        for name in self.character_names:
            # Create pattern to match name in any case variation
            pattern = re.compile(r'\b' + ''.join(f'[{c.lower()}{c.upper()}]' for c in name) + r'\b', re.IGNORECASE)
            # Replace with proper case
            text = pattern.sub(name, text)
        return text
    
    def clean_stage_directions(self, text):
        """Remove stage directions and clean up script formatting"""
        # Remove parenthetical stage directions
        text = re.sub(r'\([^)]*\)', '', text)
        # Remove square bracket notes
        text = re.sub(r'\[[^\]]*\]', '', text)
        # Normalize line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text
    
    def process_response(self, response):
        """Extract leetspeak from response and convert to normal text."""
        if self.debug:
            print("Processing response...")
        
        # Extract content
        extracted = self.extract_leetspeak(response)
        
        # Skip House's narration and stage directions
        cleaned = re.sub(r'(?:HOUSE|HoUse|H0use)\s*\([^)]*\)', '', extracted, flags=re.IGNORECASE)  # Remove House's actions
        cleaned = re.sub(r'^(?:HOUSE|HoUse|H0use)\s*(?::)?\s*', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)  # Remove "HOUSE:" prefix
        
        # Clean up the text
        cleaned = self.clean_stage_directions(cleaned)
        
        # Convert to normal text
        decoded = self.from_leetspeak(cleaned)
        
        # Normalize character names to proper case
        decoded = self.normalize_character_names(decoded)
        
        # Remove any remaining markdown code block markers (backticks)
        decoded = re.sub(r'```(?:markdown)?|```', '', decoded)
        
        # Remove [SCENE START] and [SCENE END] markers
        decoded = re.sub(r'\[SCENE (?:START|END)\]', '', decoded)
        
        # Format into proper paragraphs and clean up excessive newlines
        decoded = re.sub(r'\n{3,}', '\n\n', decoded)
        
        return decoded.strip() 