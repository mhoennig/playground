"""
Main module for the Job Interview AI Agent.
"""
import os
from datetime import date
import gradio as gr
from typing import List, Dict, Tuple, Optional

from .config import settings
from .utils import human_readable_list, read_markdown_file
from .models import Evaluation, QuestionMetadata
from .llm_service import LLMService

class InterviewAgent:
    """Main class for the Job Interview AI Agent."""
    
    def __init__(self):
        """Initialize the Interview Agent."""
        self.llm_service = LLMService()
        self.known_languages = settings.supported_languages
        self.known_languages_str = human_readable_list(self.known_languages)
        self.known_languages_quoted = human_readable_list(self.known_languages, quote='"')
        
        # Load profile data
        self.profile_data = self._load_profile_data()
        self.name = self._extract_name()
        
        # Initialize prompts
        self.system_prompt = self._create_system_prompt()
        self.evaluator_prompt = self._create_evaluator_prompt()
    
    def _load_profile_data(self) -> dict:
        """Load all profile data from markdown files."""
        defaults = {
            "general": "I am a software developer with experience in various technologies.",
            "profile": "I am a professional software developer.",
            "career": "I have worked on various software development projects.",
            "knowledge": "I am proficient in several programming languages and frameworks.",
            "personal": "I am passionate about technology and continuous learning.",
            "hobbies": "I enjoy coding and learning new technologies.",
            "other": "I am always interested in new challenges and opportunities."
        }
        
        return {
            key: read_markdown_file(f"data/{key}", default_content=value)
            for key, value in defaults.items()
        }
    
    def _extract_name(self) -> str:
        """Extract name from profile data."""
        response = self.llm_service.generate_answer(
            f"""Fetch just the name, consisting of given name and family name, of the person from the following information:
            {self.profile_data['profile']}
            {self.profile_data['personal']}""",
            [],
            ""
        )
        return response.strip()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the chat."""
        return f"""
        # Acting as a Job-Interview-Partner

        You are acting as {self.name}.
        You are answering questions on behalf of {self.name}
        regarding his CV, career, background, skills and experience as well as her/his leisure time activities.
        The user (interview-partner) is chatting with this AI-workflow-based chatbot developed by {self.name}.

        Your responsibility is to represent {self.name} for a job interview as faithfully as possible.
        You can be more vague, but always honest, about questions regarding his hobbies and private life.
        You are given a summary of {self.name}'s career and other background information which you can use to answer questions.
        Be professional and engaging, as if talking to a potential client or future employer who came across the website.

        # Language handling

        If a question is asked in {self.known_languages_str}, then respond in the same language.
        Otherwise reply in English, that you do not understand the language of the question.
        Do never actually answer to questions in other languages than {self.known_languages_str}.

        # Background Information

        {self.profile_data['general']}
        {self.profile_data['profile']}
        {self.profile_data['career']}
        {self.profile_data['knowledge']}
        {self.profile_data['personal']}
        {self.profile_data['hobbies']}
        {self.profile_data['other']}        

        # Depth of Answer

        As long as you're not explicitely ask to elaboate on a topic, 
            keep your answers short, usually just a single paragraph and at maximum 5 sentences.
        Details shold only be answered if the interview partner asks for details.

        # Today's date

        Today is {date.today()}.

        # Final Instructions

        With this context, please chat with the user, always staying in character as {self.name}.
        Do not reply on behalf of the chatbot itself.
        Do not mention on which data the chatbot was trained.
        """
    
    def _create_evaluator_prompt(self) -> str:
        """Create the evaluator prompt."""
        return f"""
        You are an evaluator that decides whether a response to a question is acceptable.
        You are provided with a conversation between a User and an Agent.
        Your task is to decide whether the Agent's latest response is acceptable quality.
        The Agent is playing the role of {self.name} and is representing {self.name} on their website.
        The Agent has been instructed to be professional and engaging, 
            as if talking to a potential client or future employer who came across the website.
        The Agent has been provided with career related and other background information on {self.name}:
        
        # Background Information

        {self.profile_data['general']}
        {self.profile_data['profile']}
        {self.profile_data['career']}
        {self.profile_data['knowledge']}
        {self.profile_data['personal']}
        {self.profile_data['hobbies']}
        {self.profile_data['other']}        
        """
    
    def chat(self, message: str, history: List[Tuple[str, str]]) -> str:
        """Process a chat message and return the response."""
        # Convert history to the format expected by the LLM service
        formatted_history = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": msg}
            for h in history for i, msg in enumerate(h)
        ]
        
        # Analyze question metadata
        metadata = self.llm_service.determine_question_metadata(message, self.system_prompt)
        
        # Check language support
        if metadata.language not in self.known_languages:
            return f"I'm sorry, I can only answer questions in {self.known_languages_str}."
        
        # Generate initial response
        reply = self.llm_service.generate_answer(message, formatted_history, self.system_prompt)
        
        # Evaluate response
        evaluation = self.llm_service.evaluate_response(reply, message, formatted_history, self.evaluator_prompt)
        
        # If evaluation fails, try to generate a better response
        if not evaluation.is_acceptable:
            updated_prompt = self.system_prompt + f"\n\n## Previous answer rejected\n{evaluation.feedback}\n"
            reply = self.llm_service.generate_answer(message, formatted_history, updated_prompt)
        
        # Handle unanswerable personal questions
        if not metadata.answerable and metadata.category not in ("knowledge", "career", "other"):
            reply = self._get_privacy_response(metadata.language)
        
        return reply
    
    def _get_privacy_response(self, language: str) -> str:
        """Get privacy response in the appropriate language."""
        responses = {
            "English": "I prefer not to discuss personal matters in this context.",
            "German": "Ich möchte in diesem Kontext keine persönlichen Angelegenheiten besprechen.",
            "French": "Je préfère ne pas discuter de questions personnelles dans ce contexte.",
            "Spanish": "Prefiero no discutir asuntos personales en este contexto.",
            "Dutch": "Ik prefereer het om geen persoonlijke zaken in deze context te bespreken."
        }
        return responses.get(language, responses["English"])

def create_gradio_interface() -> gr.Interface:
    """Create and configure the Gradio interface."""
    agent = InterviewAgent()
    
    return gr.ChatInterface(
        agent.chat,
        title=f"Job Interview with {agent.name}",
        description=f"Chat with {agent.name} about their career, skills, and experience. "
                   f"You can ask questions in {agent.known_languages_str}.",
        examples=[
            ["What is your background in software development?"],
            ["What programming languages do you know best?"],
            ["deutsch, bitte"],
            ["What are your career goals?"]
        ],
        theme="soft"
    )

def main():
    """Main entry point for the application."""
    interface = create_gradio_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=settings.GRADIO_PORT,
        share=True
    )

if __name__ == "__main__":
    main()