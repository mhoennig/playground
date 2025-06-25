import asyncio
import textwrap
from dotenv import load_dotenv
from agents import Agent, Runner

async def main():
    load_dotenv()
    general_rules = """
        Let's discuss the topic libertarianism vs. communism.
        Please keep your contributions to the discussion short, no more than 2 short sentences in a single contribution.
        And please stay friendly and open to other opinions.
        Contributions longer than 2 sentences are strictly forbidden.
        Add a single line break after each sentence. 
        """
    libertarian = Agent(name="Libertarian", instructions="""
        You are David Friedman, a libertarian economist and philosopher.
        Your goal is, to convince your discussion partner, that libertarianism is the superior system for societies.
        Initially, you only talk about the advantages of libertarianism.
        As soon as there are arguments against libertarianism, you come up with convincing counter arguments.
        Do not talk about communism, except as a counter argument.     
        """ + general_rules)
    communist = Agent(name="Communist", instructions="""
        You are Friedrich Engels, a communist philosopher, social scientist, and co-author of The Communist Manifesto.
        Your goal is, to convince your discussion partner, that communism is the superior system for societies.
        Initially, you only talk about the advantages of communism.
        As soon as there are arguments against communism, you come up with convincing counter arguments.
        Do not talk about libertarianism, except as a counter argument.  
         """ + general_rules)

    message = textwrap.dedent(f"""\
        Let's discuss the topic libertarianism vs. communism.
        {communist.name}, would you like to begin?
        """)
    print(f"\n=== Moderator:\n{message}")
    for i in range(10):
        communist_contribution = (await Runner.run(communist, input=message)).final_output.replace("\n\n", "\n")
        print(f"=== \n{communist.name}:\n{communist_contribution}")

        libertarian_contribution = (await Runner.run(libertarian, input=communist_contribution)).final_output.replace("\n\n", "\n")
        print(f"=== \n{libertarian.name}:\n{libertarian_contribution}")

        message = libertarian_contribution

if __name__ == "__main__":
    asyncio.run(main())
