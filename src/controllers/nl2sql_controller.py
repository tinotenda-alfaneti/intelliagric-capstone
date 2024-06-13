from flask import request, jsonify
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src import OPENAI_API_KEY, api, Resource, fields

#TODO: Replace with actual Database credentials for the ecommerce
db_user = "root"
db_password = ""
db_host = "localhost"
db_name = "shoppn"
MODEL = "gpt-3.5-turbo"

# Connect to SQL Database
db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

llm = ChatOpenAI(model=MODEL, temperature=0, openai_api_key=OPENAI_API_KEY)
generate_query = create_sql_query_chain(llm, db)

# Define the final prompt template
final_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
)

# Define the chain for NL2SQL execution
rephrase_answer = final_prompt | llm | StrOutputParser()
execute_query = QuerySQLDataBaseTool(db=db)

ns_query_ecommerce = api.namespace('query-ecommerce', description='Natural Language ecommerce query operations')

# Define the models for Swagger documentation
ecommerce_query_model = api.model('EcommerceQuery', {
    'message': fields.String(required=True, description='User input message for querying the ecommerce database')
})

response_model = api.model('QueryResponse', {
    'response': fields.String(description='Response from the NL2SQL query')
})

@ns_query_ecommerce.route('/')
class EcommerceQueryResource(Resource):
    @ns_query_ecommerce.expect(ecommerce_query_model)
    @ns_query_ecommerce.response(200, 'Success', response_model)
    def post(self):
        """Handles natural language to SQL queries for the ecommerce database."""
        json_data = request.get_json()
        message = json_data.get('message')

        # Generate SQL query from natural language question
        query = generate_query.invoke({"question": message})

        # Execute the SQL query
        result = execute_query.invoke(query)
        response = rephrase_answer.invoke({"question": message, "query": query, "result": result})
        return jsonify({"response": response})

# Add the namespace to the API
api.add_namespace(ns_query_ecommerce, path='/query-ecommerce')