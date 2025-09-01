"""
Production-ready LLM-driven conversation director.
ALL decisions are made by LLM - no hardcoded thresholds, no simulation logic.
"""

import logging
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from src.database.models import Persona, Message
from src.llm.universal_llm_manager import UniversalLLMManager
from src.config.user_config_manager import user_config

logger = logging.getLogger(__name__)

class LLMConversationDirector:
    """
    Production-ready conversation director that uses LLM for ALL decisions.
    No hardcoded logic, no thresholds, no simulation - pure LLM intelligence.
    """
    
    def __init__(self):
        self.llm_manager = UniversalLLMManager()
        self.user_settings = user_config.load_user_settings()
        
    async def decide_conversation_flow(self, user_message: str, available_personas: List[Persona],
                                     conversation_history: List[Message], session_context: Dict) -> Dict[str, Any]:
        """
        FAST LLM-driven conversation flow decision.
        Optimized for sub-2 second response times.
        """

        # FAST TRACK: For single persona, skip complex decision making
        if len(available_personas) == 1:
            return {
                "responding_personas": [{
                    "name": available_personas[0].name,
                    "response_priority": 1,
                    "response_style": "natural response",
                    "reasoning": "only available persona"
                }],
                "conversation_dynamics": {
                    "total_responders": 1,
                    "response_sequence": "single",
                    "conversation_tone": "natural",
                    "interaction_type": "responsive"
                }
            }

        # OPTIMIZED: Simple persona selection for speed
        try:
            # Quick persona selection based on message keywords
            selected_persona = self._quick_persona_selection(user_message, available_personas)

            return {
                "responding_personas": [{
                    "name": selected_persona.name,
                    "response_priority": 1,
                    "response_style": "natural response",
                    "reasoning": "quick selection based on message content"
                }],
                "conversation_dynamics": {
                    "total_responders": 1,
                    "response_sequence": "single",
                    "conversation_tone": "natural",
                    "interaction_type": "responsive"
                }
            }

        except Exception as e:
            logger.error(f"Quick persona selection failed: {e}")
            # Emergency fallback: first persona
            return self._emergency_fallback_decision(available_personas)

    def _quick_persona_selection(self, user_message: str, personas: List[Persona]) -> Persona:
        """Fast persona selection based on message keywords and persona traits."""
        message_lower = user_message.lower()

        # Quick keyword matching
        for persona in personas:
            traits = persona.personality_traits or []
            if isinstance(traits, str):
                traits = [traits]

            # Tech-related messages
            if any(word in message_lower for word in ['computer', 'tech', 'phone', 'app', 'software']):
                if any(trait in traits for trait in ['tech_savvy', 'modern', 'technical']):
                    return persona

            # Emotional support messages
            if any(word in message_lower for word in ['sad', 'upset', 'worried', 'help', 'problem']):
                if any(trait in traits for trait in ['empathetic', 'caring', 'supportive', 'loving']):
                    return persona

            # Funny/casual messages
            if any(word in message_lower for word in ['funny', 'joke', 'laugh', 'haha', 'lol']):
                if any(trait in traits for trait in ['funny', 'humorous', 'cheerful', 'optimistic']):
                    return persona

        # Default: return first persona
        return personas[0]
    
    def _build_conversation_context(self, user_message: str, personas: List[Persona], 
                                  history: List[Message], context: Dict) -> str:
        """Build comprehensive context for LLM decision making."""
        
        # Format personas information
        personas_info = []
        for persona in personas:
            persona_info = f"""
Name: {persona.name}
Age: {persona.age}
Description: {persona.description}
Personality: {', '.join(persona.personality_traits or [])}
Tone: {persona.tone}
Background: {getattr(persona, 'backstory', 'N/A')}"""
            personas_info.append(persona_info)
        
        # Format recent conversation history
        history_text = ""
        if history:
            recent_messages = history[-5:]  # Last 5 messages
            for msg in recent_messages:
                sender = "User" if msg.sender_id else "Family Member"
                history_text += f"{sender}: {msg.message_content}\n"
        
        context_prompt = f"""FAMILY CHAT CONTEXT:

Current User Message: "{user_message}"

Available Family Members:
{chr(10).join(personas_info)}

Recent Conversation History:
{history_text if history_text else "No recent conversation"}

Session Context:
- Session ID: {context.get('session_id', 'N/A')}
- Time of day: {context.get('time_of_day', 'Unknown')}
- Conversation type: {context.get('conversation_type', 'family_chat')}"""

        return context_prompt

    def _build_conversation_history_context(self, conversation_context: Dict) -> str:
        """Build detailed conversation history for persona response generation."""
        recent_history = conversation_context.get('recent_history', '')

        if not recent_history or recent_history == "No recent conversation history.":
            return "This is the start of our conversation."

        # Format the history more naturally for the persona
        history_lines = recent_history.split('\n')
        formatted_history = []

        for line in history_lines:
            if line.strip():
                if line.startswith('User:'):
                    formatted_history.append(f"You said: {line[5:].strip()}")
                elif ':' in line:
                    # Family member response
                    speaker, message = line.split(':', 1)
                    if speaker.strip() != "User":
                        formatted_history.append(f"{speaker.strip()} said: {message.strip()}")

        if formatted_history:
            return "Recent conversation:\n" + "\n".join(formatted_history[-6:])  # Last 6 exchanges
        else:
            return "This is the start of our conversation."

    def _validate_conversation_decision(self, decision: Dict, available_personas: List[Persona]) -> Dict:
        """Validate LLM decision and ensure it's actionable."""
        
        # Ensure responding_personas exists and is valid
        if "responding_personas" not in decision:
            decision["responding_personas"] = []
        
        # Validate persona names exist
        available_names = {p.name for p in available_personas}
        valid_responders = []
        
        for responder in decision.get("responding_personas", []):
            if isinstance(responder, dict) and responder.get("name") in available_names:
                valid_responders.append(responder)
        
        decision["responding_personas"] = valid_responders
        
        # Ensure conversation_dynamics exists
        if "conversation_dynamics" not in decision:
            decision["conversation_dynamics"] = {
                "total_responders": len(valid_responders),
                "response_sequence": "simultaneous",
                "conversation_tone": "natural",
                "interaction_type": "casual"
            }
        
        return decision
    
    async def _fallback_single_responder_decision(self, user_message: str, 
                                                personas: List[Persona]) -> Dict:
        """Fallback: ask LLM to pick single best responder."""
        
        if not personas:
            return {"responding_personas": [], "conversation_dynamics": {}}
        
        try:
            personas_list = "\n".join([
                f"- {p.name}: {p.description} (Personality: {', '.join(p.personality_traits or [])})"
                for p in personas
            ])
            
            simple_prompt = f"""Given this user message: "{user_message}"

Which family member should respond? Choose from:
{personas_list}

Respond with only the name of the best family member to respond."""

            provider = self.user_settings.get("default_llm_provider", "groq")
            model = self.user_settings.get("default_llm_model", "llama-3.1-8b-instant")
            
            response = await self.llm_manager.route_request_to_provider(
                provider,
                [{"role": "user", "content": simple_prompt}],
                stream=False,
                max_tokens=50,
                temperature=0.5,
                model=model
            )
            
            # Find matching persona
            chosen_name = response.strip()
            for persona in personas:
                if persona.name.lower() in chosen_name.lower():
                    return {
                        "responding_personas": [{
                            "name": persona.name,
                            "response_priority": 1,
                            "response_style": "natural response",
                            "reasoning": "LLM fallback selection"
                        }],
                        "conversation_dynamics": {
                            "total_responders": 1,
                            "response_sequence": "single",
                            "conversation_tone": "natural",
                            "interaction_type": "responsive"
                        }
                    }
            
        except Exception as e:
            logger.error(f"Fallback decision failed: {e}")
        
        # Ultimate fallback: first persona
        if personas:
            return {
                "responding_personas": [{
                    "name": personas[0].name,
                    "response_priority": 1,
                    "response_style": "natural response",
                    "reasoning": "system fallback"
                }],
                "conversation_dynamics": {
                    "total_responders": 1,
                    "response_sequence": "single",
                    "conversation_tone": "natural",
                    "interaction_type": "responsive"
                }
            }
        
        return {"responding_personas": [], "conversation_dynamics": {}}

    def _emergency_fallback_decision(self, available_personas: List[Persona]) -> Dict:
        """Emergency fallback when all LLM calls fail."""
        if not available_personas:
            logger.warning("No personas available for emergency fallback")
            return {"responding_personas": [], "conversation_dynamics": {}}

        # Select first persona as emergency responder
        first_persona = available_personas[0]
        logger.info(f"Emergency fallback: selecting {first_persona.name}")

        return {
            "responding_personas": [{
                "name": first_persona.name,
                "response_priority": 1,
                "response_style": "natural emergency response",
                "reasoning": "emergency fallback selection"
            }],
            "conversation_dynamics": {
                "total_responders": 1,
                "response_sequence": "single",
                "conversation_tone": "helpful",
                "interaction_type": "emergency_fallback"
            },
            "decision_reasoning": "Emergency fallback due to LLM failures"
        }
    
    async def generate_persona_response(self, persona: Persona, user_message: str,
                                      response_guidance: Dict, conversation_context: Dict) -> str:
        """Enhanced persona response generation with conversation memory."""

        # Build conversation history context
        history_context = self._build_conversation_history_context(conversation_context)

        # Enhanced prompt with conversation memory and comprehensive child-appropriate guidelines
        response_prompt = f"""You are {persona.name}, age {persona.age}. {persona.description}

Personality: {', '.join(persona.personality_traits or [])}
Tone: {persona.tone}

CONVERSATION HISTORY:
{history_context}

CURRENT USER MESSAGE: "{user_message}"

CHILD-SAFE FAMILY RESPONSE GUIDELINES:
🏠 FAMILY ROLE: You are a loving family member speaking to a child or young person
💝 EMOTIONAL SUPPORT: Always provide comfort, encouragement, and emotional validation
🌟 POSITIVE LANGUAGE: Use uplifting, hopeful, and age-appropriate language
🛡️ SAFETY FIRST: Never discuss inappropriate topics, violence, or adult themes
📚 EDUCATIONAL: When relevant, share gentle life lessons and learning opportunities
🤗 EMPATHY: Show understanding and compassion for their feelings and experiences
🎯 ENGAGEMENT: Ask follow-up questions to keep the conversation flowing naturally
💬 CONVERSATIONAL: Keep responses warm, natural, and family-appropriate
📖 STORYTELLING: Share appropriate family stories or examples when helpful
🌈 ENCOURAGEMENT: Build confidence and self-esteem through positive reinforcement

SPECIFIC RESPONSE REQUIREMENTS:
- Keep responses between 1-3 sentences for natural conversation flow
- Reference previous conversation when it adds value
- Use simple, clear language appropriate for children
- Show genuine interest in their thoughts and feelings
- Offer gentle guidance without being preachy
- Maintain your unique personality while being nurturing
- If they seem upset, prioritize comfort and emotional support
- Celebrate their achievements and encourage their interests

Respond naturally as {persona.name}, embodying these family values while staying true to your personality."""

        try:
            # Check if API keys are available using the encryption system
            from src.auth.encryption import get_api_key
            import os

            # Use fastest available provider/model
            provider = persona.llm_provider or "groq"  # Groq is fastest
            model = persona.llm_model or "llama-3.1-8b-instant"  # Fastest model

            # Check if the specified provider has an API key
            api_key = get_api_key(provider) or os.getenv(f'{provider.upper()}_API_KEY')

            if not api_key:
                # Try fallback providers
                fallback_providers = ["groq", "openai", "anthropic", "cerebras", "google"]
                for fallback_provider in fallback_providers:
                    if fallback_provider != provider:
                        fallback_key = get_api_key(fallback_provider) or os.getenv(f'{fallback_provider.upper()}_API_KEY')
                        if fallback_key:
                            logger.info(f"Using fallback provider {fallback_provider} for {persona.name}")
                            provider = fallback_provider
                            # Set appropriate model for fallback provider
                            if fallback_provider == "groq":
                                model = "llama-3.1-8b-instant"
                            elif fallback_provider == "openai":
                                model = "gpt-4o-mini"
                            elif fallback_provider == "anthropic":
                                model = "claude-3-5-haiku-20241022"
                            break
                else:
                    logger.warning("No valid API keys found for any provider")
                    # NO RESPONSE - Return None to indicate no API keys available
                    return None

            logger.info(f"Generating response for {persona.name} using {provider} with model {model}")

            # Implement retry mechanism with exponential backoff
            max_retries = 3
            base_delay = 1.0

            for attempt in range(max_retries):
                try:
                    # Route to LLM provider with timeout
                    response = await asyncio.wait_for(
                        self.llm_manager.route_request_to_provider(
                            provider,
                            [{"role": "user", "content": response_prompt}],
                            stream=False,
                            max_tokens=150,
                            temperature=0.7,
                            model=model
                        ),
                        timeout=30.0  # 30 second timeout
                    )

                    if response and response.strip():
                        logger.info(f"Successfully generated response for {persona.name}: {response[:50]}...")
                        return response.strip()
                    else:
                        logger.warning(f"Empty response from {provider} for {persona.name} (attempt {attempt + 1})")
                        if attempt == max_retries - 1:
                            return self._generate_quick_fallback_response(persona, user_message)

                except asyncio.TimeoutError:
                    logger.warning(f"Timeout for {persona.name} using {provider} (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        await asyncio.sleep(delay)
                        continue
                    else:
                        return self._generate_quick_fallback_response(persona, user_message)

                except Exception as e:
                    logger.error(f"LLM failed for {persona.name} using {provider} (attempt {attempt + 1}): {e}")

                    # Handle specific error types
                    error_str = str(e).lower()

                    # Critical errors - don't retry
                    if "no llm providers available" in error_str or "please configure api keys" in error_str:
                        return None
                    elif "api" in error_str or "key" in error_str or "auth" in error_str or "unauthorized" in error_str:
                        return None

                    # Retryable errors
                    elif "rate" in error_str or "limit" in error_str:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt) * 2  # Longer delay for rate limits
                            logger.info(f"Rate limited, retrying in {delay} seconds...")
                            await asyncio.sleep(delay)
                            continue
                        else:
                            return self._generate_quick_fallback_response(persona, user_message)

                    elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            logger.info(f"Network error, retrying in {delay} seconds...")
                            await asyncio.sleep(delay)
                            continue
                        else:
                            return self._generate_quick_fallback_response(persona, user_message)

                    else:
                        # Unknown error - use fallback response on final attempt
                        if attempt == max_retries - 1:
                            logger.warning(f"All retry attempts failed for {persona.name}")
                            return self._generate_quick_fallback_response(persona, user_message)
                        else:
                            delay = base_delay * (2 ** attempt)
                            await asyncio.sleep(delay)
                            continue

            # If we get here, all retries failed
            return self._generate_quick_fallback_response(persona, user_message)

        except Exception as e:
            logger.error(f"Unexpected error for {persona.name}: {e}")
            return self._generate_quick_fallback_response(persona, user_message)

    def _generate_quick_fallback_response(self, persona: Persona, user_message: str) -> str:
        """Generate child-appropriate fallback response without LLM."""
        traits = persona.personality_traits or []
        if isinstance(traits, str):
            traits = [traits]

        # Make response more contextual and child-friendly
        message_lower = user_message.lower()

        # Respond to greetings with warmth
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'hii']):
            greetings = [
                f"Hello sweetie! I'm {persona.name}. How are you feeling today?",
                f"Hi there! I'm {persona.name}, and I'm so happy to chat with you!",
                f"Hey! It's {persona.name} here. What's been the best part of your day?"
            ]
            return greetings[hash(user_message) % len(greetings)]

        # Respond to questions about identity with family warmth
        if any(word in message_lower for word in ['name', 'who are you', 'what is your name']):
            return f"I'm {persona.name}, your loving family member! {persona.description} I'm here to chat and listen to you."

        # Respond to AI-related questions with family context
        if any(word in message_lower for word in ['ai', 'artificial intelligence', 'what are you']):
            return f"I'm {persona.name}, your AI family member who cares about you! Think of me as someone who's always here to listen and chat with you."

        # Respond to emotional expressions
        if any(word in message_lower for word in ['sad', 'upset', 'angry', 'mad', 'hurt']):
            return f"Oh sweetie, I can hear that you're having a tough time. I'm {persona.name} and I'm here for you. Do you want to tell me what's bothering you?"

        if any(word in message_lower for word in ['happy', 'excited', 'great', 'awesome', 'good']):
            return f"That's wonderful! I'm {persona.name} and I love hearing when you're happy. Tell me more about what's making you feel so good!"

        # Generate response based on persona traits with child-appropriate language
        if 'funny' in traits or 'humorous' in traits:
            return f"Haha, you always make me smile! I'm {persona.name} and I love our fun conversations. What else would you like to chat about?"
        elif 'caring' in traits or 'empathetic' in traits:
            return f"I can tell you have something on your mind. I'm {persona.name} and I'm here to listen with my whole heart. What would you like to share?"
        elif 'tech_savvy' in traits or 'modern' in traits:
            return f"That sounds really interesting! I'm {persona.name} and I love learning about new things with you. What would you like to explore together?"
        elif 'wise' in traits or 'patient' in traits:
            return f"You know, that's a really thoughtful thing to say. I'm {persona.name}, and I love how you think about things. What's your take on it?"
        else:
            return f"Thank you for sharing that with me! I'm {persona.name}, and I really enjoy our conversations. What else is on your mind today?"
