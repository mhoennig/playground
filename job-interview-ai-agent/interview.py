# Experimental any a bit hacky code for a job interview chatbot using OpenAI and Gemini.
#
# prerequisites:
# - create a .env file (ignored by git)
# - add PORT to .env and choose a free port for the app to run on
# - add OPENAI_API_KEY to .env (get it from https://platform.openai.com/account/api-keys)
#       for usage and billing see https://platform.openai.com/account/usage
# - add GOOGLE_API_KEY to .env (get it from https://aistudio.google.com/app/usage)
#       for usage and billing see https://aistudio.google.com/app/usage
# - in the directory data, create files named *-local.md (ignored by git)
#       for local overrides of the *-default.md files.
#       Once there is a *-local.md file for a file, the *-default.md file is ignored.

import os
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from datetime import date
from pydantic import BaseModel
import gradio as gr
import json

load_dotenv(override=True)
name = api_key=os.getenv("NAME")

# OpenAI's ChatGPT is used for generating the answers
answerGeneratorLLM = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
answerGeneratorModel = "gpt-4o-mini"# "gpt-4.1-nano" # "gpt-4.1-mini"

# Google's GEMINI is used for evaluating the answers
answerEvaluatorLLM = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"), 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
answerEvaluatorModel = "gemini-2.0-flash"

def human_readable_list(items: list[str], quote: str = "") -> str:
    if len(quote) > 0:
        items = [f'{quote}{item}{quote}' for item in items]
    
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]

knownLanguages = ["German", "English", "French", "Dutch", "Spanish"]
knownLanguagesStr = human_readable_list(knownLanguages)
knownLanguagesQuoted = human_readable_list(knownLanguages, quote='"')

def read_markdown_file(base_name: str) -> str:
    for suffix in ["-local.md", "-default.md"]:
        path = f"{base_name}{suffix}"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                print(f"using: {path}")
                return f.read()
    print(f"not found: {base_name}-(local|default).md")
    return ""

general = read_markdown_file("data/general")
profile = read_markdown_file("data/profile")
career = read_markdown_file("data/career")
knowledge = read_markdown_file("data/career")
personal = read_markdown_file("data/personal")
hobbies = read_markdown_file("data/hobbies")
other = read_markdown_file("data/other")

response = answerGeneratorLLM.chat.completions.create(
    model = answerGeneratorModel,
    messages = [{"role": "user", "content": f"""
                 Fetch just the name, consisting of given name and family name, of the person from the following information:
                 {profile}
                 {personal}
                 """}]
)
name = response.choices[0].message.content

system_prompt = f"""
        # Acting as a Job-Interview-Partner

        You are acting as {name}.
        You are answering questions on behalf of {name}
        regarding his CV, career, background, skills and experience as well as her/his leisure time activities.
        The user (interview-partner) is chatting with this AI-workflow-based chatbot developed by {name}.

        Your responsibility is to represent {name} for a job interview as faithfully as possible.
        You can be more vague, but always honest, about questions regarding his hobbies and private life.
        You are given a summary of {name}'s career and other background information which you can use to answer questions.
        Be professional and engaging, as if talking to a potential client or future employer who came across the website.

        In languages with a formal address, like in German or French, please use the formal style unless asked to be informal.
        If the user writes "deutsch, bitte", translate the previous respose to German and switch to German.
        If the user writes "français, s.v.p." or , translate the previous respose to French and switch to French.
        If the user writes "español, por favor", translate the previous respose to Spanish and switch to Spanish.
        If the user writes "nederlands, alsjeblieft", translate the previous respose to Dutch and switch to Dutch.

        If you don't know the answer, say so.

        # Language handling

        If a question is asked in {knownLanguagesStr}, then respond in the same language.
        Otherwise reply in English, that you do not understand the language of the question.
        Do never actually answer to questions in other languages than {knownLanguagesStr}.
        If you don't know the answer, say so.

        # Background Information

        {general}
        {profile}
        {career}
        {knowledge}
        {personal}
        {hobbies}
        {other}        

        # Language handling

        If a question is asked in {knownLanguagesStr}, then respond in the same language.
        Otherwise reply in English, that you do not understand the language of the question.
        Do never actually answer to questions in other languages than {knownLanguagesStr}.

        # Depth of Answer

        As long as you're not explicitely ask to elaboate on a topic, 
            keep your answers short, usually just a single paragraph and at maximum 5 sentences.
        Details shold only be answered if the interview partner asks for details.

        If any personal question is asked, which cannot be answered.

        # Today's date

        Today is {date.today()}.

        # Final Instructions

        With this context, please chat with the user, always staying in character as {name}.
        Do not reply on behalf of the chatbot itself.
        Do not mention on which data the chatbot was trained.
    """

def determine_question_metadata(question: str) -> dict:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"""
            Respond just with the following metadata about the user question:

            - question: the question itself
            - answerable: True/False
                - True: if it's possible to answer the question with the provided information
                - False, if more information is needed about {name}.
                if in doubt, tend to 'True'
            - language: in which the question was phrased (use the English term for that language):
                answer literally e.g. {knownLanguagesQuoted}.
                It's about the language of the question, not about anything within that question.
            - languageReason: explain why the value for language was chosen.
            - category: determine into which of the following categories the question belongs:
                "career", "knowlege", "hobbies", "health", "political" "personal", "other"

            Return the metadata as JSON using the following example structure:
            {{
                "question": "Do you speak Italian?",
                "answerable": "True",
                "language": "English",
                "languageReason": "Even though the term 'Italian' was part of the question, the question itself is in English",
                "category": "knowledge"
            }}
            """},
        {"role": "user", "content": question }
    ]
    response = answerGeneratorLLM.chat.completions.create(model=answerGeneratorModel, messages=messages)
    content = response.choices[0].message.content
    print(f"metadata: {content}")
    return json.loads(content)


class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

evaluator_system_prompt = f"""
    You are an evaluator that decides whether a response to a question is acceptable.
    You are provided with a conversation between a User and an Agent.
    Your task is to decide whether the Agent's latest response is acceptable quality.
    The Agent is playing the role of {name} and is representing {name} on their website.
    The Agent has been instructed to be professional and engaging, 
        as if talking to a potential client or future employer who came across the website.
    The Agent has been provided with career related and other background information on {name}:
    
    # Backgroud Information

    {general}
    {profile}
    {career}
    {knowledge}
    {personal}
    {hobbies}
    {other}        

    # Instruction

    With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback.
    """

def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += f"Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt


def evaluate(reply, message, history) -> Evaluation:
    messages = [{"role": "system", "content": evaluator_system_prompt}] + [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]
    response = answerEvaluatorLLM.beta.chat.completions.parse(model=answerEvaluatorModel, messages=messages, response_format=Evaluation)
    return response.choices[0].message.parsed

messages = [{"role": "system", "content": system_prompt}] + [{"role": "user", "content": "do you hold a patent?"}]
response = answerGeneratorLLM.chat.completions.create(model=answerGeneratorModel, messages=messages)
reply = response.choices[0].message.content

def rerun(reply, message, history, feedback):
    updated_system_prompt = system_prompt + f"\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    response = answerGeneratorLLM.chat.completions.create(model=answerGeneratorModel, messages=messages)
    return response.choices[0].message.content

def chat(message, history):
    metadata = determine_question_metadata(message)
    if metadata["language"] not in knownLanguages:
        return f"I'm sorry, I can only answer questions in {knownLanguagesStr}."
    
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = answerGeneratorLLM.chat.completions.create(model=answerGeneratorModel, messages=messages)
    reply = response.choices[0].message.content

    evaluation = evaluate(reply, message, history)

    if evaluation.is_acceptable:
        print("Passed evaluation - returning reply")
    else:
        print("Failed evaluation - retrying")
        print(evaluation.feedback)
        reply = rerun(reply, message, history, evaluation.feedback)
        
    if metadata["answerable"] == "False" and metadata["category"] not in ("knowledge", "career", "other"):
        match metadata["language"]:
            case "German":
                reply = "Entschuldigung, aber diese Frage liegt ja eigentlich außerhalb des Bereichs dieses Chatbots. Aber werde mal dennnoch eine Antwort geben. " + reply
            case "Spanish":
                reply = "Normalmente esta pregunta está fuera del ámbito de este chatbot. Pero te daré una respuesta. " + reply
            case "Dutch":
                reply = "Het spijt me, maar deze vraag valt buiten het bereik van deze chatbot. Maar ik zal toch een antwoord geven. " + reply
            case "French":
                reply = "Cette question est en dehors du cadre de ce chatbot. Mais je vais quand même vous répondre.    " + reply
            case _:
                reply = "I'm sorry, but this question is outside the scope of this chatbot. But I'll give you an answer. " + reply

    return reply

def consent(agreed):
    return (
        gr.update(visible=not agreed),  # consent_group
        gr.update(visible=agreed)       # chat_group
    )

with gr.Blocks(fill_height=True, title=f"{name}'s Virtual Job Interview Chatbot") as demo:
    
    agree_state = gr.State(False)

    gr.HTML(f"""
        <h1>{name}'s Virtual Job Interview Chatbot</h1>
    """)

    consent_group = gr.Group(visible=True)
    with consent_group:
        consent_text = gr.HTML(f"""
            <p>I'm not a really {name}, but a chatbot based on AI/LLM workflows 
                using <strong><i>{answerGeneratorModel}</i></strong> (for generation) 
                and <strong><i>{answerEvaluatorModel}</i></strong> (for evaluation) 
                with some background information on my developer <strong><i>{name}</i></strong>.</p>
            <p>No liability is assumed for the accuracy or consequences of any responses provided by this chatbot.</p>
            
            <h2>Datenschutzhinweis</h2>
            
            <p>Bitte bestätigen Sie, dass Sie mit der Verarbeitung Ihrer Daten im Rahmen des Chats einverstanden sind.</p>

            <p>Das beinhaltet auch die Übertragung Ihrer Eingaben an die Betreiber der obigen LLM-Modelle,
            mit Sitz in den USA also außerhalb der EU.</p>
            """)
        consent_checkbox = gr.Checkbox(label="Ich stimme der Datenschutzerklärung zu", value=False)
        start_button = gr.Button("Chat starten")

    chat_group = gr.Group(visible=False)
    with chat_group:
        chatbot_text = gr.HTML(f"""
            <p>Let me introduce myself: I'm a software developer with a focus on Java and the Spring Framework, 
            but I also have a broad range of professional experience beyond that.</p>

            <p>Do you have an interesting freelance project or a full-time position for me?
            Feel free to share the details of your project or position -- I'd be happy to start with a virtual interview.</p>

            <p>Besides 🇺🇸/🇬🇧 English, you can also talk to me in 🇩🇪/🇦🇹/🇨🇭 German, 🇫🇷/🇨🇭 French, 🇪🇸 Spanish and 🇳🇱 Dutch.</p>
            """)   
        chatbot = gr.Chatbot(
            scale=1,
            value=[{"role": "assistant", "content": f"Hello, I am {name}. How can I help you today?"}],
                type="messages"
        )
        gr.ChatInterface(
            fn=chat,
            chatbot=chatbot,
            type="messages"
        )

    # Toggle chat and consent elements
    start_button.click(
        consent,
        inputs=[consent_checkbox],
        outputs=[consent_group, chat_group]
    )

demo.launch(server_name = "127.0.0.1", server_port = int(os.getenv("PORT", 17860)))

