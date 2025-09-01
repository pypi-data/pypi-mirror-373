"""Simplified unified AI provider."""

import os
import subprocess
import json
from ...logger import get_logger

logger = get_logger()


class UnifiedAIProvider:
    """Simplified unified AI provider."""
    
    # Provider-specific hard maximum context token limits
    PROVIDER_MAX_CONTEXT_TOKENS = {
        'local': 32000,       # Ollama hard maximum
        'openai': 400000,     # OpenAI GPT-5 only (400k tokens)
        'gemini': 1000000,    # Gemini hard maximum (1M tokens)
        'anthropic': 200000   # Anthropic hard maximum (200k tokens)
    }
    
    
    # Conservative defaults
    DEFAULT_MAX_CONTEXT_TOKENS = 32000
    MAX_PREDICT_TOKENS = 64000  # Default max output tokens
    
    # Schema for commit organization JSON structure  
    COMMIT_SCHEMA = {
        "type": "object",
        "properties": {
            "commits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "hunk_ids": {"type": "array", "items": {"type": "string"}},
                        "rationale": {"type": "string"}
                    },
                    "required": ["message", "hunk_ids", "rationale"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["commits"],
        "additionalProperties": False
    }
    
    # Gemini-compatible schema (without additionalProperties)
    GEMINI_SCHEMA = {
        "type": "object",
        "properties": {
            "commits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "hunk_ids": {"type": "array", "items": {"type": "string"}},
                        "rationale": {"type": "string"}
                    },
                    "required": ["message", "hunk_ids", "rationale"]
                }
            }
        },
        "required": ["commits"]
    }
    
    def __init__(self, config):
        self.config = config
        self.provider_type = config.ai.provider.lower()
        # Set provider-specific maximum context tokens
        self.MAX_CONTEXT_TOKENS = self.PROVIDER_MAX_CONTEXT_TOKENS.get(
            self.provider_type, 
            self.DEFAULT_MAX_CONTEXT_TOKENS
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count using tiktoken for all providers."""
        try:
            import tiktoken
            
            # Use tiktoken for all providers - it provides much more accurate 
            # token estimation than character-based heuristics
            # cl100k_base is used by GPT-4, GPT-3.5-turbo and is a good general tokenizer
            encoding = tiktoken.get_encoding('cl100k_base')
            token_count = len(encoding.encode(text))
            # Ensure minimum of 1 token for consistency with fallback behavior
            return max(1, token_count)
                
        except ImportError:
            # Fall back to heuristic if tiktoken not available
            logger.warning("tiktoken not available, using fallback token estimation")
        except Exception as e:
            # Fall back to heuristic on any tiktoken error
            logger.warning(f"tiktoken error ({e}), using fallback token estimation")
        
        # Fallback heuristic only when tiktoken fails
        # More conservative estimation for code/diffs: 1 token ≈ 3 characters
        # This overestimates to ensure we don't truncate prompts
        return max(1, int(len(text) // 3))
    
    def _calculate_dynamic_params(self, prompt: str) -> dict:
        """Calculate optimal token parameters based on prompt size for any provider."""
        prompt_tokens = self._estimate_tokens(prompt)
        
        # Get provider-specific context limit
        provider_limit = self.PROVIDER_MAX_CONTEXT_TOKENS.get(
            self.provider_type, 
            self.DEFAULT_MAX_CONTEXT_TOKENS
        )
        
        # Check if prompt exceeds our maximum supported context
        if prompt_tokens > provider_limit - 2000:  # Reserve 2000 for response
            raise Exception(f"Diff is too large ({prompt_tokens} tokens). Maximum supported: {provider_limit - 2000} tokens. Consider breaking down your changes into smaller commits.")
        
        # Ensure context window is always sufficient for prompt + substantial response buffer
        # Use larger buffer for complex tasks and be more conservative
        response_buffer = max(2000, (prompt_tokens // 3) + 2000)  # Scale buffer with prompt size
        context_needed = prompt_tokens + response_buffer
        
        # Ensure we never exceed hard limits but always accommodate the full prompt
        max_tokens = min(context_needed, provider_limit)
        
        # If context_needed exceeds provider_limit, we must fit within limits
        # but ensure response space is reasonable
        if context_needed > provider_limit:
            # Reserve at least 1000 tokens for response, use rest for prompt
            max_tokens = provider_limit
            response_buffer = min(response_buffer, 1000)
        
        # Set prediction tokens based on expected response size
        response_tokens = min(response_buffer, self.config.ai.max_predict_tokens)
        
        return {
            "prompt_tokens": prompt_tokens,
            "max_tokens": max_tokens,
            "response_tokens": response_tokens,
            "context_needed": context_needed
        }
    
    def _calculate_ollama_params(self, prompt: str) -> dict:
        """Calculate optimal num_ctx and num_predict for Ollama based on prompt size."""
        params = self._calculate_dynamic_params(prompt)
        
        # Get the provider-specific limit
        provider_limit = self.PROVIDER_MAX_CONTEXT_TOKENS.get('local', 32000)
        
        # For large prompts, use the full context window to maximize capacity
        # For smaller prompts, optimize for efficiency
        estimated_prompt_tokens = params["prompt_tokens"]
        
        # If the dynamic calculation already uses most of the context window,
        # just use the maximum to avoid weird intermediate values
        if params["max_tokens"] > provider_limit * 0.8:
            num_ctx = provider_limit
        else:
            # Use 15% safety margin since token estimation may be imperfect
            min_context_needed = int(estimated_prompt_tokens * 1.15) + 1000  # 15% safety margin + response space
            num_ctx = max(params["max_tokens"], min_context_needed)
            # Respect absolute maximum
            num_ctx = min(num_ctx, provider_limit)
        
        return {
            "num_ctx": num_ctx,
            "num_predict": params["response_tokens"]
        }
        
    def generate(self, prompt: str) -> str:
        """Generate response using the configured AI provider."""
        
        if self.provider_type == "local":
            return self._generate_local(prompt)
        elif self.provider_type == "openai":
            return self._generate_openai(prompt)
        elif self.provider_type == "anthropic":
            return self._generate_anthropic(prompt)
        elif self.provider_type == "gemini":
            return self._generate_gemini(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider_type}")
    
    def _generate_local(self, prompt: str) -> str:
        """Generate using local Ollama with structured output enforcement."""
        try:
            # Calculate optimal parameters based on prompt size
            ollama_params = self._calculate_ollama_params(prompt)
            
            # Check if model supports native reasoning (currently only gpt-oss models)
            supports_reasoning = "gpt-oss" in self.config.ai.model.lower()
            
            # Prepare the prompt with reasoning directive if supported
            if supports_reasoning and self.config.ai.reasoning:
                # Map our reasoning levels to gpt-oss levels
                reasoning_map = {
                    "minimal": "low",    # Map minimal to low for gpt-oss
                    "low": "low",
                    "medium": "medium",
                    "high": "high"
                }
                reasoning_level = reasoning_map.get(self.config.ai.reasoning, "medium")
                
                # Add reasoning directive to system prompt
                # gpt-oss models recognize "Reasoning: level" in system prompts
                system_prompt = f"Reasoning: {reasoning_level}\n\n"
                full_prompt = system_prompt + prompt
                logger.debug(f"Using gpt-oss model with native reasoning level: {reasoning_level}")
            else:
                full_prompt = prompt
                
                # Log warning if reasoning was requested but model doesn't support it
                if self.config.ai.reasoning and not supports_reasoning:
                    logger.warning(f"Model {self.config.ai.model} does not support native reasoning. "
                                 f"Reasoning parameter '{self.config.ai.reasoning}' will be ignored. "
                                 f"Consider using gpt-oss models for native reasoning support.")
            
            payload = {
                "model": self.config.ai.model,
                "prompt": full_prompt,
                "stream": False,
                "format": self.COMMIT_SCHEMA,  # Enforce JSON structure
                "options": {
                    "num_ctx": ollama_params["num_ctx"],
                    "num_predict": ollama_params["num_predict"],
                    "temperature": 0.1,  # Keep consistent temperature
                    "top_p": 0.95,       # Keep consistent top_p
                    "top_k": 20,         # Keep consistent top_k
                    "repeat_penalty": 1.1,  # Prevent repetitive explanations
                    "stop": ["\n\nHuman:", "User:", "Assistant:", "Note:"]  # Stop conversational patterns
                }
            }
            
            # Increase timeout for large contexts - be more generous for integration tests
            # Scale timeout based on context size to handle very large diffs
            if ollama_params["num_ctx"] > 20000:
                timeout = 7200  # 120 minutes for very large contexts
            elif ollama_params["num_ctx"] > 8000:
                timeout = 1800   # 30 minutes for large contexts
            else:
                timeout = 900   # 15 minutes for normal contexts
            
            result = subprocess.run([
                "curl", "-s", "-X", "POST", "http://localhost:11434/api/generate",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(payload)
            ], capture_output=True, text=True, timeout=timeout)
            
            if result.returncode != 0:
                if result.returncode == 7:
                    raise Exception("Ollama request failed: Could not connect to Ollama server at localhost:11434. Please ensure Ollama is running.")
                else:
                    raise Exception(f"Ollama request failed: {result.stderr}")
            
            response = json.loads(result.stdout)
            
            # Check if response was truncated
            response_text = response.get('response', '')
            if response.get('done', True) is False:
                logger.warning(f"Response may have been truncated. Used {ollama_params['num_ctx']} context tokens.")
            
            # Parse and normalize to array format for tests/consumers
            try:
                parsed = json.loads(response_text)
                if isinstance(parsed, dict) and "commits" in parsed and isinstance(parsed["commits"], list):
                    # Always return the commits array as JSON
                    return json.dumps(parsed["commits"])
                elif isinstance(parsed, list):
                    # Already an array of commit objects
                    return json.dumps(parsed)
                else:
                    return response_text
            except json.JSONDecodeError:
                return response_text  # Return as-is if not JSON
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Ollama request timed out after {timeout} seconds. Try reducing diff size or using a faster model.")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response from Ollama: {e}")
        except Exception as e:
            raise Exception(f"Local AI generation failed: {e}")
    
    def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI Responses API with GPT-5 models only."""
        try:
            import openai

            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise Exception("OPENAI_API_KEY environment variable not set")

            # Validate model is GPT-5
            if not self.config.ai.model.startswith('gpt-5'):
                raise Exception(
                    f"Model {self.config.ai.model} is not supported. Only GPT-5 models (gpt-5, gpt-5-mini, gpt-5-nano) are supported."
                )

            # Calculate dynamic parameters
            params = self._calculate_dynamic_params(prompt)

            # GPT-5 context limit is 400k tokens
            model_context_limit = 400000

            # Check if prompt exceeds model context limit
            if params["prompt_tokens"] > model_context_limit - 1000:  # Reserve 1000 for response
                raise Exception(
                    f"Prompt ({params['prompt_tokens']} tokens) exceeds {self.config.ai.model} context limit ({model_context_limit}). Consider reducing diff size."
                )

            # Warn if prompt is large but manageable
            if params["prompt_tokens"] > model_context_limit * 0.7:
                logger.warning(
                    f"Large prompt ({params['prompt_tokens']} tokens) approaching {self.config.ai.model} context limit."
                )

            client = openai.OpenAI(api_key=api_key)

            # Map reasoning effort (pass through all valid values, including 'minimal')
            reasoning = self.config.ai.reasoning
            reasoning_param = {"effort": reasoning} if reasoning else None

            # Build the request parameters for Responses API
            # Structured outputs for Responses API are configured under text.format
            response_params = {
                "model": self.config.ai.model,
                # Responses API expects `input` for text input
                "input": prompt,
                # Use dynamically calculated response tokens within our cap
                "max_output_tokens": params.get("response_tokens", self.config.ai.max_predict_tokens),
                # Enforce structured JSON output via Responses API text.format
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "commit_plan",
                        "schema": self.COMMIT_SCHEMA,
                        "strict": True,
                    }
                },
            }
            if reasoning_param is not None:
                response_params["reasoning"] = reasoning_param

            # Call the responses API
            try:
                response = client.responses.create(**response_params)
                logger.debug(
                    f"Successfully used responses API for {self.config.ai.model} with {self.config.ai.reasoning} reasoning"
                )
            except Exception as e:
                raise Exception(f"OpenAI responses API call failed: {e}")

            # If the SDK exposes output_text, prefer it; otherwise fall back safely
            try:
                content = getattr(response, "output_text", None)
                if not content:
                    # Fallback to extracting from output structure
                    # response.output is a list of Output objects with .content
                    if hasattr(response, "output") and response.output:
                        first = response.output[0]
                        if hasattr(first, "content") and first.content:
                            # Each content item may be text/json parts
                            part = first.content[0]
                            # Try common attributes
                            text = getattr(part, "text", None) or getattr(part, "content", None)
                            content = text if isinstance(text, str) else None
                if not content:
                    # As a last resort, try choices/message shape (older clients)
                    if hasattr(response, "choices") and response.choices:
                        choice0 = response.choices[0]
                        msg = getattr(choice0, "message", None)
                        content = getattr(msg, "content", None) if msg else None
            except Exception:
                content = None

            if not content:
                raise Exception("Failed to extract content from OpenAI response")

            return content  # JSON string per json_schema enforcement

        except ImportError:
            raise Exception("OpenAI library not installed. Run: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI generation failed: {e}")
    
    def _generate_anthropic(self, prompt: str) -> str:
        """Generate using Anthropic API with structured output enforcement."""
        try:
            import anthropic
            
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise Exception("ANTHROPIC_API_KEY environment variable not set")
            
            # Calculate dynamic parameters
            params = self._calculate_dynamic_params(prompt)
            
            # Use provider-level context limit
            model_context_limit = self.PROVIDER_MAX_CONTEXT_TOKENS.get('anthropic', 200000)
            
            # Check if prompt exceeds model context limit
            if params["prompt_tokens"] > model_context_limit - 4000:  # Reserve 4000 for response
                raise Exception(f"Prompt ({params['prompt_tokens']} tokens) exceeds {self.config.ai.model} context limit ({model_context_limit}). Consider reducing diff size.")
            
            # Warn if prompt is large but manageable
            if params["prompt_tokens"] > model_context_limit * 0.8:
                logger.warning(f"Large prompt ({params['prompt_tokens']} tokens) approaching {self.config.ai.model} context limit.")
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Use tool-based structured output for reliable JSON
            tools = [{
                "name": "commit_organizer",
                "description": "Organize git commits into structured format",
                "input_schema": self.COMMIT_SCHEMA
            }]
            
            # Map reasoning effort to thinking budget for Claude models
            # Claude uses budget_tokens for extended thinking
            extra_headers = {}
            if self.config.ai.reasoning:
                reasoning_map = {
                    "minimal": 1000,    # Minimal thinking
                    "low": 5000,        # Low thinking budget
                    "medium": 15000,    # Medium thinking budget (default)
                    "high": 30000       # High thinking budget
                }
                budget_tokens = reasoning_map.get(self.config.ai.reasoning, 15000)
                # Enable interleaved thinking beta
                extra_headers["anthropic-beta"] = "interleaved-thinking-2025-05-14"
                logger.debug(f"Using Claude extended thinking with budget_tokens={budget_tokens} for reasoning={self.config.ai.reasoning}")
            
            response = client.messages.create(
                model=self.config.ai.model,
                max_tokens=self.config.ai.max_predict_tokens,
                tools=tools,
                tool_choice={"type": "tool", "name": "commit_organizer"},
                messages=[{"role": "user", "content": prompt}],
                timeout=120.0,  # Add explicit timeout
                extra_headers=extra_headers if extra_headers else None
            )
            
            # Extract structured data from tool use
            for content in response.content:
                if content.type == "tool_use" and content.name == "commit_organizer":
                    # Return the full structured response, not just the commits array
                    structured_data = content.input
                    return json.dumps(structured_data)
            
            # Fallback if no tool use found
            if response.content and response.content[0].type == "text":
                return response.content[0].text
            
            raise Exception("No valid response content found")
            
        except ImportError:
            raise Exception("Anthropic library not installed. Run: pip install anthropic")
        except Exception as e:
            raise Exception(f"Anthropic generation failed: {e}")
    
    def _generate_gemini(self, prompt: str) -> str:
        """Generate using Google Gemini API with structured output enforcement."""
        try:
            from google import genai
            from google.genai import types
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise Exception("GEMINI_API_KEY environment variable not set")
            
            # Calculate dynamic parameters
            params = self._calculate_dynamic_params(prompt)
            
            # Use provider-level context limit
            model_context_limit = self.PROVIDER_MAX_CONTEXT_TOKENS.get('gemini', 1000000)
            
            # Check if prompt exceeds model context limit
            if params["prompt_tokens"] > model_context_limit - 4000:  # Reserve 4000 for response
                raise Exception(f"Prompt ({params['prompt_tokens']} tokens) exceeds {self.config.ai.model} context limit ({model_context_limit}). Consider reducing diff size.")
            
            # Warn if prompt is large but manageable
            if params["prompt_tokens"] > model_context_limit * 0.8:
                logger.warning(f"Large prompt ({params['prompt_tokens']} tokens) approaching {self.config.ai.model} context limit.")
            
            # Map reasoning effort to thinking budget for Gemini models that support it
            # Only specific models support thinking (gemini-2.0-flash-thinking-exp, etc.)
            thinking_budget = None
            model_lower = self.config.ai.model.lower()
            supports_thinking = "thinking" in model_lower or "2.5" in model_lower
            
            if self.config.ai.reasoning and supports_thinking:
                reasoning_map = {
                    "minimal": 0,       # Disable thinking for minimal (if supported)
                    "low": 1024,        # Low thinking budget
                    "medium": 8192,     # Medium thinking budget (default)
                    "high": 24576       # High thinking budget
                }
                thinking_budget = reasoning_map.get(self.config.ai.reasoning, 8192)
                # For models that require thinking, minimal will use low
                if thinking_budget == 0 and supports_thinking:
                    thinking_budget = 1024
                    logger.debug(f"Model {self.config.ai.model} requires thinking, using low budget instead of disabling")
                logger.debug(f"Using Gemini thinking budget={thinking_budget} for reasoning={self.config.ai.reasoning}")
            
            # Create client
            client = genai.Client(api_key=api_key)
            
            # Build config with JSON output
            config_params = {
                "maxOutputTokens": self.config.ai.max_predict_tokens,
                "temperature": 0.1,  # Lower temperature for more structured output
                "topP": 0.95,       # Higher top_p for better instruction following
                "topK": 20,         # Lower top_k for more focused responses
                "responseMimeType": "application/json",  # Force JSON output
                "responseSchema": self.GEMINI_SCHEMA  # Use Gemini-compatible schema
            }
            
            # Add thinking config only for models that support it
            if thinking_budget is not None and supports_thinking:
                config_params["thinkingConfig"] = types.ThinkingConfig(thinkingBudget=thinking_budget)
            
            config = types.GenerateContentConfig(**config_params)
            
            # Generate response
            response = client.models.generate_content(
                model=self.config.ai.model,
                contents=prompt,
                config=config
            )
            
            # Extract text from response
            response_text = response.text
            
            # Parse the JSON response and return the full structure
            try:
                parsed = json.loads(response_text)
                if isinstance(parsed, dict) and "commits" in parsed:
                    return json.dumps(parsed)  # Return full dict
                elif isinstance(parsed, list):
                    # Wrap list in expected format
                    return json.dumps({"commits": parsed})
                else:
                    return response_text
            except json.JSONDecodeError:
                return response_text  # Return as-is if not JSON
            
        except ImportError:
            raise Exception("Google Generative AI library not installed. Run: pip install google-genai")
        except Exception as e:
            raise Exception(f"Google Gemini generation failed: {e}")
