"""
LLM Wrapper for Google Gemini
Provides chat and JSON extraction capabilities with retry logic.
"""
import os
import json
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import google.generativeai as genai


class GeminiLLM:
    """Wrapper for Google Gemini API with retry logic and error handling."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """Initialize the Gemini LLM."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "No API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable."
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Send a chat message and get a response.
        
        Args:
            prompt: The user's message
            system_prompt: Optional system instructions
            temperature: Creativity level (0-1)
            
        Returns:
            The model's response text
        """
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
        
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                    )
                )
                
                if response.text:
                    return response.text
                else:
                    # Handle empty response
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    return ""
                    
            except Exception as e:
                error_msg = str(e)
                print(f"[LLM] Attempt {attempt + 1} failed: {error_msg}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise RuntimeError(f"LLM request failed after {self.max_retries} attempts: {error_msg}")
        
        return ""
    
    async def chat_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Send a chat message and parse the response as JSON.
        
        Args:
            prompt: The user's message
            system_prompt: Optional system instructions
            temperature: Creativity level (0-1)
            
        Returns:
            Parsed JSON response as a dictionary
        """
        # Add JSON instruction to system prompt
        json_instruction = "IMPORTANT: Your response must be valid JSON only. No markdown, no explanations, just the JSON object."
        
        if system_prompt:
            full_system = f"{system_prompt}\n\n{json_instruction}"
        else:
            full_system = json_instruction
        
        for attempt in range(self.max_retries):
            try:
                response_text = await self.chat(
                    prompt,
                    system_prompt=full_system,
                    temperature=temperature,
                )
                
                # Clean up the response
                cleaned = self._extract_json(response_text)
                
                # Parse JSON
                result = json.loads(cleaned)
                return result
                
            except json.JSONDecodeError as e:
                print(f"[LLM] JSON parse error (attempt {attempt + 1}): {e}")
                print(f"[LLM] Raw response: {response_text[:500]}...")
                
                if attempt < self.max_retries - 1:
                    # Try again with stronger JSON instruction
                    await asyncio.sleep(self.retry_delay)
                    prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON, no other text."
                else:
                    # Return empty dict on final failure
                    print("[LLM] Failed to parse JSON, returning empty dict")
                    return {}
            
            except Exception as e:
                print(f"[LLM] Error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    return {}
        
        return {}
    
    def _extract_json(self, text: str) -> str:
        """Extract and fix JSON from text that might have markdown or errors."""
        text = text.strip()
        
        # Remove markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        
        # Find JSON object boundaries
        start = text.find("{")
        end = text.rfind("}")
        
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
        
        # Fix common JSON issues
        text = self._fix_json_errors(text)
        
        return text
    
    def _fix_json_errors(self, text: str) -> str:
        """Attempt to fix common JSON errors from LLM output."""
        import re
        
        # Fix truncated strings (missing closing quote)
        # Look for patterns like: "email": "something without closing quote
        # followed by a newline and another field
        lines = text.split("\n")
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check if line has an unclosed string
            # Count quotes (ignoring escaped ones)
            quote_count = len(re.findall(r'(?<!\\)"', line))
            
            if quote_count % 2 == 1:
                # Odd number of quotes - likely unclosed string
                # Try to close it before any trailing comma or content
                line = line.rstrip()
                if line.endswith(","):
                    line = line[:-1] + '",'
                elif not line.endswith('"'):
                    line = line + '"'
            
            fixed_lines.append(line)
        
        text = "\n".join(fixed_lines)
        
        # Fix control characters in strings
        # Remove any control characters except \n, \r, \t
        def clean_string_content(match):
            content = match.group(1)
            # Remove problematic control characters
            cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content)
            return f'"{cleaned}"'
        
        text = re.sub(r'"([^"]*)"', clean_string_content, text)
        
        return text


# Create a singleton instance
llm = GeminiLLM()
