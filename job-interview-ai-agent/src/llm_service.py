"""
Language Model Service for the Job Interview AI Agent.
"""
from typing import List, Dict, Any
import json
from openai import OpenAI
from .config import settings
from .models import Evaluation, QuestionMetadata, ChatMessage
from .mcp_tools import handle_mcp_tool_calls, mcp_tools

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
            {"role": "user", "content": question},
            {"role": "user", "content": self._get_metadata_prompt()},
        ]
        response = self.answer_generator.chat.completions.create(
            model=settings.answer_generator.model_name,
            messages=messages
        )
        content = response.choices[0].message.content
        print(f"metadata: {content}")
        return QuestionMetadata.model_validate_json(content)
    
    def generate_answer(self, message: str, history: List[Dict[str, str]], system_prompt: str) -> str:
        """Generate an answer using the answer generator."""
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]

        while True:
            response = self.answer_generator.chat.completions.create(
                model=settings.answer_generator.model_name,
                messages=messages,
                tools = mcp_tools,
                tool_choice = "auto"
            )

            finish_reason = response.choices[0].finish_reason
            print(f"finish reason({message}): ", finish_reason)
            if finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = handle_mcp_tool_calls(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                break

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
        parsed = response.choices[0].message.parsed
        print(f"evaluation: {parsed}")
        return parsed
    
    def _get_metadata_prompt(self) -> str:
        """Get the prompt for metadata analysis."""
        return f"""
            Respond just with the following metadata about the user question:

            - question: the question itself
            - coverage: Percentage (0-100)
                - 100%: if background information regarding this question is fully given 
                - 70%: if sufficient background information regarding this question is given
                - 60%: if there is just vague background information regarding this question
                - 50%: if you're unsure if sufficient background information is given regarding this question
                - 30%: if very insufficient background information regarding this question is given
                - 0%: if no background information regarding this question is given
                If the topic of the question is part of the background information, then the coverage percentage should be at least 50%.
                Only if there is absolutely no information about the topic of the question, then the coverage percentage should be below 30%.
                Legal issues not to answer are irrelevant for this measure, just answer if information is given that could be used to answer the question.
                If the result for coverage is 0%, then doublecheck if there is really no background information available about the topic of the question.
            - recruiter: Percentage (0-100)
                - 100%: if the question is a typical question asked by a recruiter in Germany
                - 50%: if the question is a question that a recruiter would ask in Germany, but not very typical
                - 0%: if the question is a question that a recruiter would never ask in Germany
                Also consider the German laws which might restrict the questions that recruiter should not ask
                and an applicant must not even answer correctly.
            - language: in which the question was phrased (use the English term for that language)
            - category: determine into which category the question belongs:
                "career", "profile", "knowlege", "hobbies", "health", "political", "personal", "other"

            Return the metadata as pureand proper JSON without any additional markup.
            """
    
    def _get_evaluation_prompt(self, reply: str, message: str, history: List[Dict[str, str]]) -> str:
        """Get the prompt for response evaluation."""
        return f"Here's the conversation between the User and the Agent: \n\n{history}\n\n" + \
               f"Here's the latest message from the User: \n\n{message}\n\n" + \
               f"Here's the latest response from the Agent: \n\n{reply}\n\n" + \
               f"Please evaluate the response, replying with whether it is acceptable and your feedback.\n\n" + \
               f"Jusge harshly, if the response does not look perfect."