"""
Pitch Report Generator
Analyzes conversation history and generates structured feedback report
"""
from typing import List, Dict, Optional
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, llm_client, llm_model, is_groq: bool):
        self.llm_client = llm_client
        self.llm_model = llm_model
        self.is_groq = is_groq
    
    async def generate_report(self, conversation_history: List[Dict[str, str]]) -> Dict:
        """
        Generate pitch report from conversation history
        
        Returns:
            {
                "strengths": ["...", "..."],
                "weaknesses": ["...", "..."],
                "scores": {
                    "idea": 8,
                    "team": 7,
                    "market": 9,
                    "clarity": 6,
                    "moat": 5
                },
                "investment_probability": 24
            }
        """
        
        # Extract user messages (the pitch) and VC questions
        user_messages = []
        vc_questions = []
        
        for msg in conversation_history:
            if msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))
            elif msg.get("role") == "assistant":
                vc_questions.append(msg.get("content", ""))
        
        # Skip system message
        if not user_messages:
            logger.warning("No user messages in conversation history")
            return self._get_default_report()
        
        # Create evaluation prompt
        evaluation_prompt = self._create_evaluation_prompt(user_messages, vc_questions)
        
        # Get LLM evaluation
        report_json = await self._get_llm_evaluation(evaluation_prompt)
        
        return report_json
    
    def _create_evaluation_prompt(self, user_messages: List[str], vc_questions: List[str]) -> str:
        """Create prompt for LLM to evaluate the pitch"""
        
        # Build conversation text
        conversation_parts = []
        for i, user_msg in enumerate(user_messages):
            if i < len(vc_questions):
                conversation_parts.append(f"VC: {vc_questions[i]}")
            conversation_parts.append(f"Founder: {user_msg}")
        
        conversation_text = "\n".join(conversation_parts)
        
        prompt = f"""You are a VC investor evaluating a pitch conversation. Analyze the founder's responses and provide a structured evaluation.

CONVERSATION:
{conversation_text}

Evaluate the pitch on these criteria:
1. **Idea** (0-10): Quality and clarity of the business idea
2. **Market** (0-10): Market size, opportunity, and understanding
3. **Clarity** (0-10): How clearly the founder communicated their vision
4. **Moat** (0-10): Competitive advantage and defensibility

Provide your evaluation as JSON with this exact structure:
{{
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
    "scores": {{
        "idea": <0-10>,
        "market": <0-10>,
        "clarity": <0-10>,
        "moat": <0-10>
    }},
    "investment_probability": <0-100>
}}

Be harsh but fair. Only return valid JSON, no other text."""
        
        return prompt
    
    async def _get_llm_evaluation(self, prompt: str) -> Dict:
        """Get evaluation from LLM"""
        result = None
        try:
            if not self.llm_client:
                logger.warning("No LLM client available, using default report")
                return self._get_default_report()
            
            messages = [
                {"role": "system", "content": "You are a VC investor evaluating startup pitches. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ]
            
            if self.is_groq:
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                result = response.choices[0].message.content.strip()
            else:
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                result = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            report = json.loads(result)
            
            # Validate and normalize
            return self._validate_report(report)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            if result:
                logger.error(f"Response was: {result[:200]}")
            return self._get_default_report()
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return self._get_default_report()
    
    def _validate_report(self, report: Dict) -> Dict:
        """Validate and normalize report structure"""
        # Ensure all required fields exist
        default = self._get_default_report()
        
        validated = {
            "strengths": report.get("strengths", default["strengths"])[:3],  # Max 3
            "weaknesses": report.get("weaknesses", default["weaknesses"])[:3],  # Max 3
            "scores": {
                "idea": max(0, min(10, int(report.get("scores", {}).get("idea", 5)))),
                "market": max(0, min(10, int(report.get("scores", {}).get("market", 5)))),
                "clarity": max(0, min(10, int(report.get("scores", {}).get("clarity", 5)))),
                "moat": max(0, min(10, int(report.get("scores", {}).get("moat", 5))))
            },
            "investment_probability": max(0, min(100, int(report.get("investment_probability", 20))))
        }
        
        return validated
    
    def _get_default_report(self) -> Dict:
        """Default report if LLM fails"""
        return {
            "strengths": [
                "Engaged in conversation",
                "Responded to questions"
            ],
            "weaknesses": [
                "Need more clarity on business model",
                "Competitive positioning unclear"
            ],
            "scores": {
                "idea": 5,
                "market": 5,
                "clarity": 5,
                "moat": 5
            },
            "investment_probability": 20
        }

