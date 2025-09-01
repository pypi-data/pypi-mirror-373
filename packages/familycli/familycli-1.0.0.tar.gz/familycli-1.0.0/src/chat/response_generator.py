
import asyncio
import logging
import json
from typing import List, Optional, Dict, Any, Tuple
from src.database.db_manager import DatabaseManager
from src.database.models import Persona, Message, Session
from src.llm.universal_llm_manager import UniversalLLMManager
from src.config.config_manager import ConfigManager
from src.llm.model_validator import model_validator

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Production-grade response generator with AI-driven persona selection and emotional intelligence."""

    def __init__(self, config_dir: str = "src/config"):
        self.llm_manager = UniversalLLMManager()
        self.config_manager = ConfigManager(config_dir)
        self.persona_config = self._load_persona_config()
        self.conversation_memory = {}

    def _load_persona_config(self) -> Dict:
        """Load persona configuration with selection rules."""
        try:
            return self.config_manager.load('default_personas')
        except Exception as e:
            logger.error(f"Failed to load persona config: {e}")
            return {"personas": [], "persona_selection_rules": {}}

    async def detect_mood(self, message: str) -> str:
        """
        Production-grade mood detection using LLM with fallback to keyword analysis.
        """
        prompt = f"""Analyze the emotional tone of this message and respond with ONLY one word from: happy, sad, angry, confused, neutral.

Message: "{message}"

Response:"""

        try:
            result = await self.llm_manager.route_request_to_provider(
                self.llm_manager.default_provider,
                [{"role": "user", "content": prompt}],
                stream=False,
                max_tokens=10,
                temperature=0.1
            )

            if result:
                result_lower = result.strip().lower()
                for mood in ['happy', 'sad', 'angry', 'confused', 'neutral']:
                    if mood in result_lower:
                        return mood

        except Exception as e:
            logger.warning(f"LLM mood detection failed: {e}, falling back to keyword analysis")

        # Fallback to keyword-based detection
        mood_map = {
            'happy': ['happy', 'joy', 'excited', 'love', 'great', 'awesome', 'wonderful', 'amazing'],
            'sad': ['sad', 'down', 'unhappy', 'depressed', 'upset', 'disappointed', 'hurt'],
            'angry': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated', 'pissed'],
            'confused': ['confused', 'lost', 'unsure', 'don\'t understand', 'unclear', 'puzzled'],
            'neutral': []
        }

        message_lower = message.lower()
        for mood, keywords in mood_map.items():
            if any(word in message_lower for word in keywords):
                return mood
        return 'neutral'

    async def select_responder(self, session_id: int, personas: List[Persona], last_message: str, context: Optional[Dict] = None) -> Persona:
        """
        AI-driven persona selection based on context, mood, relationships, and conversation dynamics.
        """
        if not personas:
            raise ValueError("No personas available for response")

        # Analyze message for intelligent selection
        analysis = await self._analyze_message_for_selection(last_message, context)

        # Get conversation history for context
        conversation_context = self._get_conversation_context(session_id)

        # Score personas based on multiple factors
        persona_scores = await self._score_personas_for_response(
            personas, analysis, conversation_context, context
        )

        # Select best persona based on scores
        best_persona = max(persona_scores, key=persona_scores.get)

        # Update conversation memory
        self._update_conversation_memory(session_id, best_persona.name, analysis)

        return best_persona

    async def _analyze_message_for_selection(self, message: str, context: Optional[Dict] = None) -> Dict:
        """Analyze message using LLM to determine optimal persona selection factors."""
        try:
            analysis_prompt = f"""Analyze this family chat message and provide a JSON response with the following structure:
{{
    "mood": "happy|sad|angry|confused|excited|neutral",
    "topics": ["list", "of", "main", "topics"],
    "emotional_intensity": "low|medium|high",
    "requires_support": true/false,
    "requires_humor": true/false,
    "requires_practical_advice": true/false,
    "conversation_type": "casual|serious|emotional|technical|creative"
}}

Message: "{message}"

Respond with ONLY the JSON, no other text."""

            response = await self.llm_manager.route_request_to_provider(
                "openai",
                [{"role": "user", "content": analysis_prompt}],
                stream=False,
                max_tokens=200,
                temperature=0.3,
                model="gpt-4o-mini"
            )

            return json.loads(response.strip())

        except Exception as e:
            logger.warning(f"Failed to analyze message with LLM: {e}")
            # Fallback to basic analysis
            return await self._basic_message_analysis(message)

    async def _basic_message_analysis(self, message: str) -> Dict:
        """Fallback message analysis using keyword detection."""
        mood = await self.detect_mood(message)

        # Basic topic detection
        topics = []
        if any(word in message.lower() for word in ['tech', 'computer', 'phone', 'app']):
            topics.append('technology')
        if any(word in message.lower() for word in ['help', 'advice', 'problem']):
            topics.append('practical_matters')
        if any(word in message.lower() for word in ['sad', 'upset', 'worried']):
            topics.append('emotional_support')

        return {
            "mood": mood,
            "topics": topics,
            "emotional_intensity": "medium",
            "requires_support": mood in ['sad', 'angry', 'confused'],
            "requires_humor": mood in ['neutral', 'happy'],
            "requires_practical_advice": 'help' in message.lower(),
            "conversation_type": "casual"
        }

    def _select_by_activity_weight(self, personas: List[Persona], context: Optional[Dict] = None) -> Persona:
        """Select persona based on activity weighting and conversation patterns."""
        if not personas:
            raise ValueError("No personas available")

        # Production-grade activity-based selection
        weights = []
        for persona in personas:
            weight = 1.0  # Base weight

            # Increase weight for personas that haven't spoken recently
            if context and 'conversation_history' in context:
                recent_speakers = []
                for msg in context['conversation_history'][-3:]:  # Last 3 messages
                    if msg.get('role') == 'assistant':
                        # Extract persona name from message (simplified)
                        recent_speakers.append(msg.get('content', '').split(':')[0])

                if persona.name not in recent_speakers:
                    weight *= 1.5  # Boost weight for personas who haven't spoken

            # Adjust weight based on personality traits
            if persona.personality_traits:
                traits = persona.personality_traits if isinstance(persona.personality_traits, list) else []
                if 'talkative' in traits:
                    weight *= 1.2
                elif 'quiet' in traits:
                    weight *= 0.8

            weights.append(weight)

        # Weighted random selection
        import random
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(personas)

        rand_val = random.uniform(0, total_weight)
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if rand_val <= cumulative:
                return personas[i]

        return personas[-1]  # Fallback

    async def generate_response(self, persona: Persona, message_content: str, context: Optional[Dict] = None) -> str:
        """
        Production-grade response generation using LLM with persona-specific instructions.
        """
        try:
            mood = await self.detect_mood(message_content)

            # Build comprehensive system prompt
            system_prompt = self._build_system_prompt(persona, mood, context)

            # Build conversation context
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_content}
            ]

            # Add conversation history if available
            if context and 'conversation_history' in context:
                # Insert history before the current message
                history_messages = context['conversation_history'][-5:]  # Last 5 messages for context
                messages = [messages[0]] + history_messages + [messages[1]]

            # Generate response using persona's preferred LLM
            provider = persona.llm_provider or self.llm_manager.default_provider

            response = await self.llm_manager.route_request_to_provider(
                provider,
                messages,
                stream=False,
                max_tokens=512,
                temperature=0.7,
                model=persona.llm_model
            )

            return response.strip() if response else f"I'm not sure how to respond to that."

        except Exception as e:
            logger.error(f"Response generation failed for persona {persona.name}: {e}")
            # Fallback response based on persona traits
            return self._generate_fallback_response(persona, message_content, mood)

    def _build_system_prompt(self, persona: Persona, mood: str, context: Optional[Dict] = None) -> str:
        """Build comprehensive system prompt for persona."""
        prompt_parts = [
            f"You are {persona.name}, a family member in a group chat.",
        ]

        if persona.age:
            prompt_parts.append(f"You are {persona.age} years old.")

        if persona.description:
            prompt_parts.append(f"Description: {persona.description}")

        if persona.backstory:
            prompt_parts.append(f"Background: {persona.backstory}")

        if persona.personality_traits is not None:
            if isinstance(persona.personality_traits, list):
                traits = ', '.join(persona.personality_traits)
            else:
                traits = str(persona.personality_traits)
            prompt_parts.append(f"Personality traits: {traits}")

        if persona.tone:
            prompt_parts.append(f"Communication tone: {persona.tone}")

        # Mood-specific instructions
        mood_instructions = {
            'sad': "The user seems sad. Show empathy, offer comfort, and be supportive.",
            'angry': "The user seems angry. Stay calm, be understanding, and help de-escalate if needed.",
            'confused': "The user seems confused. Be patient, helpful, and provide clear explanations.",
            'happy': "The user seems happy. Share in their joy and maintain the positive energy.",
            'neutral': "Respond naturally according to your personality."
        }

        prompt_parts.append(mood_instructions.get(mood, mood_instructions['neutral']))

        if persona.response_instructions:
            prompt_parts.append(f"Additional instructions: {persona.response_instructions}")

        prompt_parts.extend([
            "Respond as this character would in a family chat.",
            "Keep responses conversational, natural, and appropriate for family interaction.",
            "Do not break character or mention that you are an AI."
        ])

        return " ".join(prompt_parts)

    def _generate_fallback_response(self, persona: Persona, message_content: str, mood: str) -> str:
        """Generate fallback response when LLM fails."""
        fallback_responses = {
            'sad': [
                "I'm here for you. ❤️",
                "Sending you a big hug!",
                "Things will get better, I promise."
            ],
            'angry': [
                "Let's talk about this calmly.",
                "I understand you're upset.",
                "Take a deep breath, we can work this out."
            ],
            'confused': [
                "Let me help clarify that for you.",
                "I can explain if you'd like.",
                "What specifically are you confused about?"
            ],
            'happy': [
                "That's wonderful! 😊",
                "I'm so happy for you!",
                "Great news!"
            ],
            'neutral': [
                "I see what you mean.",
                "That's interesting.",
                "Tell me more about that."
            ]
        }

        responses = fallback_responses.get(mood, fallback_responses['neutral'])
        import random
        return random.choice(responses)

    def _score_by_topics(self, persona: Persona, topics: List[str]) -> float:
        """Score persona based on topic expertise."""
        topic_rules = self.persona_config.get('persona_selection_rules', {}).get('topic_based_selection', {})
        score = 0.0

        for topic in topics:
            preferred_personas = topic_rules.get(topic, [])
            if persona.name in preferred_personas:
                score += 2.0

        return score

    def _score_by_personality_traits(self, persona: Persona, analysis: Dict) -> float:
        """Score based on personality trait requirements."""
        score = 0.0
        traits = persona.personality_traits or []
        if isinstance(traits, str):
            traits = [traits]

        if analysis.get('requires_support') and any(trait in traits for trait in ['empathetic', 'caring', 'supportive']):
            score += 2.0
        if analysis.get('requires_humor') and any(trait in traits for trait in ['funny', 'cheerful', 'optimistic']):
            score += 2.0
        if analysis.get('requires_practical_advice') and any(trait in traits for trait in ['practical', 'organized', 'reliable']):
            score += 2.0

        return score

    def _score_by_conversation_dynamics(self, persona: Persona, conversation_context: Dict) -> float:
        """Score based on conversation dynamics to avoid repetition."""
        score = 0.0

        # Avoid consecutive responses from same persona
        last_responder = conversation_context.get('last_responder')
        if last_responder and last_responder == persona.name:
            score -= 3.0

        # Boost personas who haven't responded recently
        recent_responders = conversation_context.get('recent_responders', [])
        if persona.name not in recent_responders:
            score += 1.0

        return score

    def _score_by_relationships(self, persona: Persona, conversation_context: Dict) -> float:
        """Score based on persona relationship dynamics."""
        score = 0.0

        # Get relationship weights from config
        relationship_weights = self.persona_config.get('conversation_dynamics', {}).get('personality_interaction_weights', {})
        persona_weights = relationship_weights.get(persona.name, {})

        # Boost score based on relationship with last responder
        last_responder = conversation_context.get('last_responder')
        if last_responder and last_responder in persona_weights:
            score += persona_weights[last_responder] * 1.0

        return score

    def _get_conversation_context(self, session_id: int) -> Dict:
        """Get conversation context for persona selection."""
        memory = self.conversation_memory.get(session_id, {})

        return {
            'last_responder': memory.get('last_responder'),
            'recent_responders': memory.get('recent_responders', []),
            'conversation_flow': memory.get('conversation_flow', []),
            'topic_history': memory.get('topic_history', [])
        }

    def _update_conversation_memory(self, session_id: int, persona_name: str, analysis: Dict):
        """Update conversation memory with latest interaction."""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = {
                'recent_responders': [],
                'conversation_flow': [],
                'topic_history': []
            }

        memory = self.conversation_memory[session_id]
        memory['last_responder'] = persona_name

        # Update recent responders (keep last 5)
        if persona_name in memory['recent_responders']:
            memory['recent_responders'].remove(persona_name)
        memory['recent_responders'].insert(0, persona_name)
        memory['recent_responders'] = memory['recent_responders'][:5]

        # Update topic history
        topics = analysis.get('topics', [])
        for topic in topics:
            if topic not in memory['topic_history']:
                memory['topic_history'].append(topic)
        memory['topic_history'] = memory['topic_history'][-10:]  # Keep last 10 topics
