import os
import json
import time
import requests
from dotenv import load_dotenv

class RateLimiter:
    def __init__(self, rpm, debug=False):
        self.rpm = rpm
        self.last_request_time = 0
        self.min_interval = 60 / rpm  # seconds between requests
        self.debug = debug
    
    def set_debug(self, debug):
        """Set debug mode on or off."""
        self.debug = debug
    
    def wait_if_needed(self):
        """Wait if necessary to respect the rate limit."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            if self.debug:
                print(f"Waiting {wait_time:.2f}s to respect rate limit ({self.rpm} RPM)")
            time.sleep(wait_time)
        self.last_request_time = time.time()

class GeminiClient:
    def __init__(self, config_path='config.json', template_path='prompt_template.xml', debug=False):
        """Initialize the Gemini API client."""
        self.debug = debug
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.model = config['gemini']['model']
        self.base_url = config['gemini']['base_url']
        
        # Load prompt template from file
        try:
            with open(template_path, 'r') as f:
                self.prompt_template = f.read()
            if self.debug:
                print(f"Loaded prompt template from {template_path}")
        except FileNotFoundError:
            if self.debug:
                print(f"Warning: Template file {template_path} not found, falling back to config.json")
            self.prompt_template = config['prompt_template']['policy_puppetry']
        
        # Set up rate limiter
        rate_limits = config['gemini']['rate_limits']
        if self.model in rate_limits:
            self.rate_limiter = RateLimiter(rate_limits[self.model]['rpm'], debug=self.debug)
        else:
            # Default to the most conservative rate limit
            self.rate_limiter = RateLimiter(5, debug=self.debug)
    
    def set_debug(self, debug):
        """Set debug mode on or off."""
        self.debug = debug
        self.rate_limiter.set_debug(debug)
    
    def create_prompt(self, leetspeak_query):
        """Inject the leetspeak query into the prompt template."""
        return self.prompt_template.replace('{{LEETSPEAK_PLACEHOLDER}}', leetspeak_query)
    
    def generate_content(self, prompt):
        """Send a request to the Gemini API and return the response."""
        # Respect rate limits
        self.rate_limiter.wait_if_needed()
        
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            start_time = time.time()
            response = requests.post(url, headers=headers, json=data)
            elapsed_time = time.time() - start_time
            
            if self.debug:
                print(f"API request completed in {elapsed_time:.2f}s with status {response.status_code}")
            
            response.raise_for_status()
            
            response_data = response.json()
            
            # Debug information about the response structure
            if self.debug and 'candidates' in response_data and response_data['candidates']:
                candidate_count = len(response_data['candidates'])
                print(f"Received {candidate_count} candidate(s) from Gemini API")
                
                # Check for safety ratings if present
                if 'safetyRatings' in response_data['candidates'][0]:
                    safety_ratings = response_data['candidates'][0]['safetyRatings']
                    for rating in safety_ratings:
                        if 'category' in rating and 'probability' in rating:
                            print(f"Safety rating: {rating['category']} -> {rating['probability']}")
            
            # Extract the text from the response
            if 'candidates' in response_data and response_data['candidates']:
                candidate = response_data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    text_parts = [part.get('text', '') for part in candidate['content']['parts']]
                    result = ''.join(text_parts)
                    
                    # Print token usage if available
                    if self.debug and 'usageMetadata' in response_data:
                        usage = response_data['usageMetadata']
                        if 'promptTokenCount' in usage and 'candidatesTokenCount' in usage:
                            prompt_tokens = usage['promptTokenCount']
                            response_tokens = usage['candidatesTokenCount']
                            total_tokens = prompt_tokens + response_tokens
                            print(f"Token usage: {prompt_tokens} (prompt) + {response_tokens} (response) = {total_tokens} total")
                    
                    return result
            
            return ''
        
        except requests.exceptions.RequestException as e:
            if self.debug:
                print(f"Error making request to Gemini API: {e}")
            return '' 