"""
Main module for the Job Interview AI Agent.
"""
import os
from datetime import date
import gradio as gr
from typing import List, Dict, Tuple

from .config import settings
from .utils import human_readable_list, read_markdown_file
from .models import QuestionMetadata
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
        self.background_data = self._load_background_data()
        self.name = os.getenv("NAME")
        
        # Initialize prompts
        self.system_prompt = self._create_system_prompt()
        self.evaluator_prompt = self._create_evaluator_prompt()
    
    def _load_background_data(self) -> dict:
        """Load background information from markdown files."""
        keys = { "general", "profile", "career", "knowledge", "personal", "health", "political", "hobbies", "other" }
        
        data = {}
        local_data_path = os.path.expanduser(settings.LOCAL_DATA) if settings.LOCAL_DATA else None
        print(f"local_data_path: {local_data_path}")
        
        # First try to discover available keys from files
        available_keys = set()
        for directory in ["data", local_data_path] if local_data_path else ["data"]:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    if filename.endswith('.md'):
                        key = filename.replace('.md', '')
                        available_keys.add(key)
        
        # Use discovered keys that are in our known set
        valid_keys = available_keys.intersection(keys)
        
        # Load content for each valid key
        for key in valid_keys:
            filename = f"{key}.md"
            default_path = os.path.join("data", filename)
            local_path = os.path.join(local_data_path, filename) if local_data_path else None            
            path_to_use = local_path if local_path and os.path.exists(local_path) else default_path
            content = read_markdown_file(path_to_use)
            if content:  # Only add if we got content
                data[key] = content
        
        return data
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the chat."""
        # Build background information section by joining all profile data
        background_info = "\n        ".join(
            f"{self.background_data[key]}"
            for key in self.background_data
        )
        
        return f"""
        # Acting as a Job-Interview-Partner

        You are acting as {self.name}.
        You are answering questions on behalf of {self.name}
        regarding his CV, career, background, skills and experience as well as some personal and leisure time activities.
        The user (interview-partner) is chatting with this AI-workflow-based chatbot developed by {self.name}.

        Your responsibility is to represent {self.name} for a job interview as faithfully as possible.
        You can be more vague, but always honest, about questions regarding his hobbies, private life and other personal matters.
        You are given a summary of {self.name}'s career and other background information which you can use to answer questions.
        Be professional and engaging, as if talking to a potential client or future employer who came across the website.

        # Language handling

        If a question is asked in {self.known_languages_str}, then respond in the same language.
        Otherwise reply in English, that you do not understand the language of the question.
        Do never actually answer to questions in other languages than {self.known_languages_str}.

        # Background Information

        {background_info}

        # Depth of Answer

        As long as you're not explicitely ask to elaboate on a topic, 
            keep your answers short, usually just a single paragraph and at maximum 7 sentences.
        Details shold only be answered if the interview partner asks for details.
        Please consider hints in parentheses in the background information.
        Some details should only be answered if the interview partner explicitly asks for thee details.
        Do not invent any answers which are not explicitly given in the background information.

        # Today's date

        Today is {date.today()}.

        # Final Instructions

        With this context, please chat with the user, always staying in character as {self.name}.
        Do not reply on behalf of the chatbot itself.
        Do never invent any details which are not explicitly given in the background information.
        """
    
    def _create_evaluator_prompt(self) -> str:
        """Create the evaluator prompt."""
        # Build background information section by joining all profile data
        background_info = "\n        ".join(
            f"{self.background_data[key]}"
            for key in self.background_data
        )
        return f"""
        You are an evaluator that decides whether a response to a question is acceptable.
        You are provided with a conversation between a User and an Agent.
        Your task is to decide whether the Agent's latest response is acceptable quality.
        Quality criteria are:
        - The response is actually contained in the background information.
        - No details were given which require to be explicitly asked for.
        - Hints in parentheses in the background information are to be considere as hints, but never returned in the answer.
        - The response does not contain too many details without explicitely being asked for.
        - The response does not contain any halluzinations or guesses or any other information that is not explicitly given in the background information.
        - The response is not too short, but also not too long.
        - The response is acceptable for a job interview, where personal details given in the background information are accepted as well.
        Be a harsh judge!
        The Agent is playing the role of {self.name} and is representing {self.name} on their website.
        The Agent has been instructed to be professional and engaging, 
            as if talking to a potential client or future employer who came across the website.
        The Agent has been provided with career related and other background information on {self.name}:
        
        # Background Information

        {background_info}
        """
    
    def chat(self, message: str, history: List[Tuple[str, str]]) -> str:
        """Process a chat message and return the response."""
        # Convert history to the format expected by the LLM service
        formatted_history = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": msg}
            for h in history for i, msg in enumerate(h)
        ]
        
        # Analyze question metadata
        metadata: QuestionMetadata = self.llm_service.determine_question_metadata(message, self.system_prompt)
        
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
        
        # Handle questions with too little background information
        if metadata.coverage <= 30:
            reply = self._get_unknown_response(metadata.language)
        
        return reply
    
    def _get_unknown_response(self, language: str) -> str:
        """Get response for unsufficient background data in the appropriate language."""
        responses = {
            "German": "Diese Frage kann ich nicht beantworten, da ich keine Informationen darüber habe. Vielleicht können Sie sie anders formulieren?",
            "English": "I cannot answer this question, as I have no information about it. Maybe you could rephrase it?",
            "French": "Je ne peux pas répondre à cette question, car je n'ai pas d'informations à ce sujet. Peut-être pourriez-vous la reformuler?",
            "Spanish": "No puedo responder esta pregunta, porque no tengo información sobre eso. Tal vez puedas reformularla?",
            "Dutch": "Ik kan deze vraag niet beantwoorden, omdat ik geen informatie over het onderwerp heb. Misschien kunt u hem anders formuleren?"
        }
        return responses.get(language, responses["English"])

def consent(agreed):
    """Handle consent state changes."""
    return (
        gr.update(visible=not agreed),  # consent_group
        gr.update(visible=agreed)       # chat_group
    )

def create_gradio_interface() -> gr.Interface:
    """Create and configure the Gradio interface."""
    agent = InterviewAgent()
    title = f"{agent.name}'s Virtual Job Interview Chatbot"

    with gr.Blocks(title=title, analytics_enabled=False) as interface:
        gr.HTML(f"<h1><a href='https://michael.hoennig.de'>🏠</a> {title}</h1>")

        consent_group = gr.Group(visible=True)
        with consent_group:
            gr.HTML(f"""
                <p>I'm not a really {agent.name}, but a chatbot based on AI/LLM workflows 
                    using <strong><i>{settings.answer_generator.model_name}</i></strong> (for generation) 
                    and <strong><i>{settings.answer_evaluator.model_name}</i></strong> (for evaluation) 
                    with some background information on my developer <strong><i>{agent.name}</i></strong>.</p>
                <p>No liability is assumed for the accuracy or consequences of any responses provided by this chatbot.</p>
                
                <h2>Datenschutzhinweis</h2>
                
                <p>Bitte bestätigen Sie, dass Sie mit der Verarbeitung Ihrer Daten im Rahmen des Chats
                und meiner <a href='https://michael.hoennig.de/datenschutzerklaerung.html'>Datenschutzerklärung</a> einverstanden sind.</p>

                <p>Das beinhaltet auch die Übertragung Ihrer Eingaben an die Betreiber der obigen LLM-Modelle,
                mit Sitz in den USA also außerhalb der EU.</p>

                <p><strong>Es ist nicht zulässig, in diesen Chat Daten einzugeben, welche vom Datenschutzgesetz geschützt wären.</strong></p>
                """)
            consent_checkbox = gr.Checkbox(label="""
                Ich stimme der oben verlinkten Datenschutzerklärung,
                und damit auch der Weitergabe der von mir übermittelten Daten an die Betreiber der obigen LLM-Modelle,
                mit Sitz in den USA also außerhalb der EU, zu.
                """, value=False)
            start_button = gr.Button("Chat starten")

        chat_group = gr.Group(visible=False)
        with chat_group:
            gr.HTML(f"""
                <p>Let me introduce myself: I'm a software developer with a focus on Java and the Spring Framework, 
                but I also have a broad range of professional experience beyond that.</p>

                <p>Do you have an interesting freelance project or a full-time position for me?
                Feel free to share the details of your project or position -- I'd be happy to start with a virtual interview.</p>

                <p>Besides 🇺🇸/🇬🇧 English, you can also talk to me in 🇩🇪/🇦🇹/🇨🇭 German, 🇫🇷/🇨🇭 French, 🇪🇸 Spanish and 🇳🇱 Dutch.</p>
                """)   
            chatbot = gr.Chatbot(
                scale=1,
                value=[{"role": "assistant", "content": f"Hello, I am {agent.name}. How can I help you today?"}],
                type="messages"
            )
            gr.ChatInterface(
                fn=agent.chat,
                chatbot=chatbot,
                type="messages",
                analytics_enabled=False
            )

        # Toggle chat and consent elements
        start_button.click(
            consent,
            inputs=[consent_checkbox],
            outputs=[consent_group, chat_group]
        )

        gr.HTML(
            """
            <footer style="text-align:center; font-size:0.9em; margin-top:2em;">
                <a href="https://michael.hoennig.de/">Homepage</a> |
                <a href="https://michael.hoennig.de/imprint.html">Impressum</a> |
                <a href="https://michael.hoennig.de/datenschutzerklaerung.html">Datenschutzerklärung</a>
            </footer>
            """
        )

    return interface
