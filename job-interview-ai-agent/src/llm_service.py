"""
Language Model Service for the Job Interview AI Agent.
"""
from typing import List, Dict, Any
import json
from openai import OpenAI
from .config import settings
from .models import Evaluation, QuestionMetadata, ChatMessage

class LLMService:
    """Service for interacting with Language Models."""
    
    def __init__(self):
        """Initialize LLM clients."""
        self.answer_generator = OpenAI(
            api_key=settings.answer_generator.api_key
        )
        
        self.answer_evaluator = OpenAI(
            api_key=settings.answer_evaluator.api_key,
            base_url=settings.answer_evaluator.base_url
        )
    
    def determine_question_metadata(self, question: str, system_prompt: str) -> QuestionMetadata:
        """Analyze question metadata using the answer generator."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": self._get_metadata_prompt()},
            {"role": "user", "content": question}
        ]
        
        response = self.answer_generator.chat.completions.create(
            model=settings.answer_generator.model_name,
            messages=messages
        )
        content = response.choices[0].message.content
        return QuestionMetadata.parse_raw(content)
    
    def generate_answer(self, message: str, history: List[Dict[str, str]], system_prompt: str) -> str:
        """Generate an answer using the answer generator."""
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
        response = self.answer_generator.chat.completions.create(
            model=settings.answer_generator.model_name,
            messages=messages
        )
        return response.choices[0].message.content
    
    def evaluate_response(self, reply: str, message: str, history: List[Dict[str, str]], evaluator_prompt: str) -> Evaluation:
        """Evaluate a response using the answer evaluator."""
        messages = [
            {"role": "system", "content": evaluator_prompt},
            {"role": "user", "content": self._get_evaluation_prompt(reply, message, history)}
        ]
        
        response = self.answer_evaluator.beta.chat.completions.parse(
            model=settings.answer_evaluator.model_name,
            messages=messages,
            response_format=Evaluation
        )
        return response.choices[0].message.parsed
    
    def _get_metadata_prompt(self) -> str:
        """Get the prompt for metadata analysis."""
        return f"""
            Respond just with the following metadata about the user question:

            - question: the question itself
            - answerable: True/False
                - True: if it's possible to answer the question with the provided information
                - False, if more information is needed
                if in doubt, tend to 'True'
            - language: in which the question was phrased (use the English term for that language)
            - languageReason: explain why the value for language was chosen
            - category: determine into which category the question belongs:
                "career", "knowlege", "hobbies", "health", "political" "personal", "other"

            Return the metadata as JSON.
            """
    
    def _get_evaluation_prompt(self, reply: str, message: str, history: List[Dict[str, str]]) -> str:
        """Get the prompt for response evaluation."""
        return f"Here's the conversation between the User and the Agent: \n\n{history}\n\n" + \
               f"Here's the latest message from the User: \n\n{message}\n\n" + \
               f"Here's the latest response from the Agent: \n\n{reply}\n\n" + \
               f"Please evaluate the response, replying with whether it is acceptable and your feedback." 