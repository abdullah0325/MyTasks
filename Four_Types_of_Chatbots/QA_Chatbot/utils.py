
import logging.config
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser 
import logging
import os 
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


logging.basicConfig(
    filename='app.log',          # Log file name
    filemode='a',                # Append mode; use 'w' for overwrite
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    level=logging.INFO           # Set the logging level
)


def get_response(question):
    if question:
        try:
            model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
            prompt = ChatPromptTemplate.from_template("Answer the question: {question}")
            output_parser = StrOutputParser()
            qa_chain = prompt |model | output_parser

            response = qa_chain.invoke({"question": question})

            logging.info("Response generated successfully.")
            return response
        except Exception as e:
            logging.error("Error occurred: %s", e)
            raise e
    else:
        logging.warning("No question provided.")
        return "Please ask a question."



if __name__ == "__main__":
    user_input = input("Enter a question: ")
    rewponse = get_response(user_input)
    print(rewponse)