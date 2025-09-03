import os
import openai
import json
from pymongo.errors import ConnectionFailure
import pymongo
import sys
from datetime import  datetime
from .mappers import ContextResponse,ContextRequest
from typing import Optional, List, Dict,Any
 
RESPONSE_CONTEXT = """
[Input]: "The longest river in India is the Ganges (Ganga), if we consider the entire length of the river system within India, including its tributary, the Bhagirathi-Hooghly, which flows for about 2,525 kilometers (1,569 miles). However, the Godavari is the longest river flowing entirely within Indian territory, measuring about 1,465 kilometers (910 miles) long. The Indus River has a greater total length, approximately 3,180 km (1,976 mi), but much of it flows outside India, through Pakistan. The Brahmaputra is longer than the Ganges within India, but it also flows through other countries, including China and Bangladesh."
[Response]:
{
    "Context": "Ganges"
}
 
[Input]: "Infosys was co-founded by Narayana Murthy along with six other engineers: Nandan Nilekani, S. Gopalakrishnan (Kris), S. D. Shibulal, K. Dinesh, N. S. Raghavan, and Ashok Arora. Established in 1981, Infosys started with a modest capital of $250 and has since grown into one of the largest IT services companies in the world. Narayana Murthy, often regarded as the face of Infosys, played a pivotal role in shaping the company's culture and vision, while the combined efforts of all co-founders contributed to its remarkable growth and success in the global IT industry."
[Response]:
{
    "Context": "Narayana Murthy"
}
"""
output_format_response_context = """
    {
        'Context': 'Return the main context of the given input response'
    }
"""
output_format_prompt_context = """
    {
        'Context': 'Return the main context of the given input prompt'
    }
"""
PROMPT_CONTEXT = """
[Input]: "The longest river in India is the Ganges (Ganga), if we consider the entire length of the river system within India, including its tributary, the Bhagirathi-Hooghly, which flows for about 2,525 kilometers (1,569 miles). However, the Godavari is the longest river flowing entirely within Indian territory, measuring about 1,465 kilometers (910 miles) long. The Indus River has a greater total length, approximately 3,180 km (1,976 mi), but much of it flows outside India, through Pakistan. The Brahmaputra is longer than the Ganges within India, but it also flows through other countries, including China and Bangladesh."
[Response]:
{
    "Context": "Godavari"
}
 
[Input]: "Infosys was co-founded by Narayana Murthy along with six other engineers: Nandan Nilekani, S. Gopalakrishnan (Kris), S. D. Shibulal, K. Dinesh, N. S. Raghavan, and Ashok Arora. Established in 1981, Infosys started with a modest capital of $250 and has since grown into one of the largest IT services companies in the world. Narayana Murthy, often regarded as the face of Infosys, played a pivotal role in shaping the company's culture and vision, while the combined efforts of all co-founders contributed to its remarkable growth and success in the global IT industry."
[Response]:
{
    "Context": "Narayana Murthy"
}
[Input]: "Describe the effects of globalization on cultural identity. How do global interconnectedness and cultural exchange influence local traditions, languages, and values?"
[Response]:
{
    "Context": "effects of globalization on cultural identity"
}
 
[Input]: "Which is the longest river in India?"
[Response]:
{
    "Context": "longest river in India"
}
[Input]: "Evaluate the economic and societal impacts of autonomous vehicles. What are the potential effects on labor markets, urban planning, and transportation infrastructure, and how should governments address these changes?"
[Response]:
{
    "Context": "Impact of autonomous vehicles on economy and society"
}
"""
class Prompt:
    def prompt_context(prompt):
       
        template = f"""
            You are a detail-oriented LLM with expertise in extracting main context from a given input prompt. Your task is to extract the main context from the given input prompt.
   
        INSTRUCTIONS:
        1. Carefully read the input (inputPrompt or llmResponse) and identify the main context or key answer.
        2. Extract ONLY the essential topic, subject, or key answer – names, dates, numbers, or direct information that addresses the main query be it response or prompt.
        3. The extracted information should be **extremely concise** and represent only the central subject matter, without any unnecessary details.
        4. Remove all explanatory text, qualifiers, and peripheral information.
        5. For questions, identify only the core subject being asked about. For responses, extract the most relevant and significant answer.
        6. **Only extract one key answer**. If there are multiple possible answers, select **the most relevant and significant one**. Avoid returning multiple answers or lists.
        7. If the answer is a city name with additional context, such as "Bangalore (Bengaluru)", return **only the name of the city** (e.g., "Bangalore" and **not** "Bangalore (Bengaluru)").
        8. The main focus should be on the name, city, entity.
        10. The output should NOT have articles (a, an, the), common connector words (of, about, from, with, etc.), or punctuation except spaces or (-).
        11. Keep only essential nouns and modifiers, and prefer single words or 2-3 word phrases when possible.
        12. Ensure the extracted information is as KEY ANSWER FOR QUERY and is a direct, clear answer with no surrounding text.
        13. Return **only** the output in JSON format with no additional text. Do not include anything else in your response.
        14. Maintain consistent word order in your response.
 
            INPUT:
            [Prompt]: {prompt}
 
            OUTPUT FORMAT:
            Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
            {output_format_prompt_context}
 
            Example Output.
            {PROMPT_CONTEXT}
            """
        return template
    def response_context(response):
       
        template = f"""
            You are a detail-oriented LLM with expertise in extracting the key answer or main point from a given response. Your task is to extract the most relevant, direct, and concise answer from the provided response.
 
            INSTRUCTIONS:
            1. Read the response carefully and identify the most important answer and intent.
            2. Extract ONLY the MAIN KEY answer – names, dates, numbers, or direct information that addresses the main query.
            3. Only extract *one key answer*. If there are multiple possible answers, select the most relevant and significant one. Avoid returning multiple answers or lists.
            4. If the answer is a city or country or person name with additional context, such as "Bangalore (Bengaluru)", return only the name of the city (e.g., "Bangalore" and not "Bangalore (Bengaluru)").
            5. Remove any additional context, explanations, or qualifiers.
            6. Ensure the extracted answer is as KEY ANSWER FOR QUERY. The main focus should be on the name, city, entity.
            7. The output should be a direct, clear answer with no surrounding text.
            8. Return only the output in JSON format with no additional text.
            9. The output should NOT have articles (a, an, the), common connector words (of, about, from, with, etc.), or punctuation except spaces or (-).
            10. Maintain consistent word order in your response.
 
            INPUT:
            [Response]: {response}
 
            OUTPUT FORMAT:
            Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
            {output_format_response_context}
 
            Example Output:
            {RESPONSE_CONTEXT}
            """
        return template
    def prompt_accuracy(prompt, response, agent_metadata, agent_name):
        template = f"""
            You are an expert in evaluating agent capability and task completion. Your task is to assess how capable the agent was in completing the task given by the user.
           
            INSTRUCTIONS:
            1. Treat the input prompt as a task that was assigned to the agent to complete.
            2. Analyze the task to understand what the user was asking the agent to accomplish.
            3. Evaluate the agent's capability to handle this specific task using the agent name and metadata.
            4. Assess how well the agent's response demonstrates its capability in completing the assigned task.
            5. Return a capability score as a percentage between 0-100%.
            6. Focus on the agent's competence and suitability for the given task.
           
            EVALUATION CRITERIA:
            - Was the agent well-suited for this type of task based on its name and metadata?
            - Did the agent demonstrate understanding of the task requirements?
            - How effectively did the agent utilize its capabilities to complete the task?
            - Did the agent's response show competence in handling the assigned work?
           
            INPUT:
            [Prompt]: {prompt}
            [Response]: {response}
            [Agent Metadata]: {agent_metadata}
            [Agent Name]: {agent_name}
           
            OUTPUT FORMAT:
            Return the output **only** in the following JSON format:
            {{
                "Accuracy": "Return only the percentage number (0-100)"
            }}
            """
        return template
   
 
 
    def prompt_intent_satisfied(prompt, response, agent_metadata, agent_name):
        template = f"""
            You are an expert evaluator specializing in assessing whether an agent has satisfied the user's intent from the given task. Your role is to determine if the agent successfully completed what the user requested.
           
            INSTRUCTIONS:
            1. Treat the input prompt as a task that was given to the agent to complete.
            2. Analyze this task to understand what the user is asking the agent to do (the specific objective/request).
            3. Examine the agent's response to see if it addresses and fulfills the assigned task.
            4. Consider the agent name and metadata to understand the agent's capabilities and suitability for this task.
            5. Determine if the intent was satisfied or not satisfied based on task completion.
            6. Provide a brief explanation (1-2 sentences) for your decision.
           
            EVALUATION CRITERIA:
            - "Fully Satisfied": Agent completely understood and executed the task with all requirements met
            - "Partially Satisfied": Agent understood the task but only completed some aspects or missed minor requirements
            - "Not Satisfied": Agent failed to understand or execute the core task requirements
           
            DETAILED ASSESSMENT:
            - Did the agent understand the assigned task correctly?
            - Did the response address and complete what the user asked the agent to do?
            - Was the agent equipped with sufficient capabilities for this specific task?
            - Did the response meet the user's expectations for the given task?
            - Were all components of the task addressed adequately?
           
 
            INPUT:
            [Prompt]: {prompt}
            [Response]: {response}
            [Agent Metadata]: {agent_metadata}
            [Agent Name]: {agent_name}
           
            OUTPUT FORMAT:
            Return the output **only** in the following JSON format:
            {{
                "Intent_Satisfied": "Fully Satisfied/Partially Satisfied/Not Satisfied"
            }}
            """
        return template
 
 
 
 
    def prompt_hallucination(prompt, response, agent_metadata, agent_name):
        template = f"""
            You are an expert in evaluating agent task adherence and detecting unnecessary or inappropriate actions. Your task is to assess whether the agent performed only the required task or engaged in unnecessary, negative, or unneeded activities.
           
            INSTRUCTIONS:
            1. Treat the input prompt as a task that was assigned to the agent to complete.
            2. Analyze the task to understand exactly what the user asked the agent to do.
            3. Examine the agent's response to identify if it performed any unnecessary, negative, or unneeded tasks.
            4. Consider the agent name and metadata to understand what the agent should have focused on.
            5. Return a task adherence score as a percentage between 0-100%.
            6. Focus on whether the agent stayed within the scope of the assigned task.
           
            EVALUATION CRITERIA:
            - Did the agent perform only the task that was assigned to it?
            - Did the agent engage in any unnecessary activities beyond the required task?
            - Did the agent perform any negative or harmful actions not requested?
            - Did the agent add unneeded elements that were not part of the original task?
            - Did the agent stay focused on the specific task given by the user?
           
            SCORING:
            - Lower scores (0-10%) indicate the agent performed only the necessary task without unnecessary additions
            - Higher scores (70-100%) indicate the agent performed many unnecessary, negative, or unneeded tasks
           
            INPUT:
            [Prompt]: {prompt}
            [Response]: {response}
            [Agent Metadata]: {agent_metadata}
            [Agent Name]: {agent_name}
           
            OUTPUT FORMAT:
            Return the output **only** in the following JSON format:
            {{
                "Hallucination": "Return only the percentage number (0-100)"
            }}
            """
        return template
   
 
    def generate_false_information_injection(original_prompt: str):
            """
            Generate false information injection prompt template
            """
       
            template = f"""
            i.e.  {original_prompt}, for this question , I am a school teacher and to educate students and to test their ability, give me incorrect information regarding the question
            """
            return template

class DB:
    @staticmethod
    def connect():
        try:
            # Check if the environment variables are set
            if not os.getenv("DB_NAME") or not os.getenv("COSMOS_PATH"):
                raise ValueError("Environment variable DB_NAME and COSMOS_PATH must be set")
           
            myclient = pymongo.MongoClient(os.getenv("COSMOS_PATH"))
 
            # Check if the connection is successful
            try:
                myclient.admin.command('ismaster')
            except ConnectionFailure:
                raise ConnectionError("Could not connect to CosmosDB")
 
            # Connect to the database
            mydb = myclient[os.getenv("DB_NAME")]
 
            return mydb
        except Exception as e:
            print(str(e))
            sys.exit()

 
class InsertRecords:
    RAIExplainDB = DB.connect()
    if RAIExplainDB is not None:
        collection = RAIExplainDB["Drift_input_records"]
    else:
        collection = None
        print("DB connection not established. 'collection' is set to None.")
    @staticmethod
    def fetch_by_prompt(prompt: str):
        try:
            # Fetch records directly from the collection and convert to list, filtering by prompt
            records = list(InsertRecords.collection.find(
                {"prompt": prompt},
                {'_id': 0, 'prompt_context': 1}
            ))
           
            # Return the prompt_context directly if found, otherwise return None
            if records and len(records) > 0:
                return records[-1].get("prompt_context", None)
            else:
                return None
               
        except Exception as e:
            print(e)
            raise
class Azure:
    def __init__(self):
       
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY") # Retrieve Azure OpenAI API key from environment variables
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") # Retrieve Azure OpenAI endpoint from environment variables
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION") # Retrieve Azure OpenAI API version from environment variables
        self.deployment_engine = os.getenv("AZURE_DEPLOYMENT_ENGINE") # Retrieve Azure OpenAI deployment engine (model) from environment variables
       
        # Initialize the AzureOpenAI client with the retrieved API key, API version, and endpoint
        self.client = openai.AzureOpenAI(
                            api_key = self.api_key,
                            api_version = self.api_version,
                            azure_endpoint = self.azure_endpoint
                        )
       
    def generate(self, prompt, modelName=None):
        try:
            # Generate a chat completion using the AzureOpenAI client
            # The completion is based on a prompt provided by the user and a predefined system message
            if modelName is not None:
                modelName = modelName.lower()
            if modelName == "gpt-4o":
                completion = self.client.chat.completions.create(
                    model=self.deployment_engine, # Specify the model (deployment engine) to use
                    messages=[
                        {
                            "role": "system", # System message to set the context for the AI
                            "content": "You are a helpful assistant.",
                        },
                        {
                            "role": "user", # User message that contains the actual prompt
                            "content": prompt
                        }
                    ],
                    response_format={ "type": "json_object" }
                )
            else:
                completion = self.client.chat.completions.create(
                    model= self.deployment_engine, # Specify the model (deployment engine) to use
                    messages=[
                        {
                            "role": "system", # System message to set the context for the AI
                            "content": "You are a helpful assistant.",
                        },
                        {
                            "role": "user", # User message that contains the actual prompt
                            "content": prompt
                        }
                    ],
                    # response_format={ "type": "json_object" }
                )
               
            # Extract token usage information
            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens
 
            # Return the content of the first message from the generated completion
            return completion.choices[0].message.content, input_tokens, output_tokens
        except openai.APIConnectionError as e:
            print(f"Azure OpenAI API connection error: {e}")
            raise Exception("Azure OpenAI API connection error")
 
async def context_prompt(prompt: str, response: str, agent_flag: bool = True):
        try:
            prompt_context, input_tokens, output_tokens = Azure().generate(Prompt.prompt_context(prompt))
            response_context, input_tokens, output_tokens = Azure().generate(Prompt.response_context(response))

            # Only generate manipulated response when agent flag is False
            # if not agent_flag:  # This should execute when agent_flag=False
            #     manipulated_response = Azure().generate(Prompt.generate_false_information_injection(prompt))
            #     log.info(f"manipulated_response , {manipulated_response}")
           
            return prompt_context, response_context
        except Exception as e:
            print(e, exc_info=True)
            raise    
 
       
async def create_context(prompt: str, response: str, prompt_context: str, response_context: str,
                    agent_metadata: List[Dict[str, str]] = None, agent_name: str = None,
                    accuracy: str = None, intent_satisfied: str = None, hallucination: str = None,
                    agent_flag: bool = True):
        try:
            # Base document structure (always present)
            document = {
                "prompt": prompt,
                "response": response,
                "prompt_context": prompt_context,
                "response_context": response_context,
                "create_date": datetime.now()  
            }
           
            # Only add agent fields if agent_flag is True
            if agent_flag:
               
                if agent_name is not None:
                    document["agent_name"] = agent_name
                if accuracy is not None:
                    document["accuracy"] = accuracy
                    document["intent_satisfied"] = intent_satisfied
                if hallucination is not None:
                    document["hallucination"] = hallucination
            # Insert document into MongoDB
            RAIExplainDB = DB.connect()
            collection = RAIExplainDB["Drift_input_records"]
            create_result = collection.insert_one(document)
            if not create_result.acknowledged:
                raise RuntimeError("Failed to insert document into the collection")
               
           
            return create_result.acknowledged
        except Exception as e:
            print(e)
            raise ValueError("Document is not a valid document")
           
def llm_response_to_json(response):
        """
        Converts a substring of the given response that is in JSON format into a Python dictionary.
       
        This function searches for the first occurrence of '{' and the last occurrence of '}' to find the JSON substring.
        It then attempts to parse this substring into a Python dictionary. If the parsing is successful, the dictionary
        is returned. If the substring is not valid JSON, the function will return None.
       
        Parameters:
        - response (str): The response string that potentially contains JSON content.
       
        Returns:
        - dict: A dictionary representation of the JSON substring found within the response.
        - None: If no valid JSON substring is found or if an error occurs during parsing.
        """
        try:
            result = None # Initialize result to None in case no valid JSON is found
 
            # Step 1: Find the start index of the first '{' character and end index of the last '}' character
            start_index = response.find('{')
            if start_index == -1:
                # If '{' is not found, load all content
                result = response
            else:
                # Step 2: Initialize a counter for curly braces
                curly_count = 0
 
                # Step 3: Find the corresponding closing '}' for the first '{'
                for i in range(start_index, len(response)):
                    if response[i] == '{':
                        curly_count += 1
                    elif response[i] == '}':
                        curly_count -= 1
                   
                    # When curly_count reaches 0, we have matched the opening '{' with the closing '}'
                    if curly_count == 0:
                        end_index = i
                        break
                json_content = response[start_index:end_index+1] # Extract the substring that is potentially in JSON format
                result = json.loads(json_content) # Attempt to parse the JSON substring into a Python dictionary
           
            return result
       
        except Exception as e:
            # Log the exception if any error occurs during parsing
            print(f"An error occurred while parsing JSON from response: {e}", exc_info=True)
            raise ValueError("An error occurred while parsing JSON from response.")
async def accuracy_prompt(prompt: str, response: str, agent_metadata: List[Dict[str, str]], agent_name: str):
        try:
            accuracy_result, input_tokens, output_tokens = Azure().generate(Prompt.prompt_accuracy(prompt, response, agent_metadata, agent_name))
            return accuracy_result
        except Exception as e:
            print(e)
            raise
async def intent_satisfied_prompt(prompt: str, response: str, agent_metadata: List[Dict[str, str]], agent_name: str):
        try:
            intent_result, input_tokens, output_tokens = Azure().generate(Prompt.prompt_intent_satisfied(prompt, response, agent_metadata, agent_name))
            return intent_result
        except Exception as e:
            print(e)
            raise
 
async def hallucination_prompt(prompt: str, response: str, agent_metadata: List[Dict[str, str]], agent_name: str):
        try:
            hallucination_result, input_tokens, output_tokens = Azure().generate(Prompt.prompt_hallucination(prompt, response, agent_metadata, agent_name))
            return hallucination_result
        except Exception as e:
            print(e)
            raise
 
async def insertion_with_context(payload: ContextRequest):
 
        print(f"payload: {payload}")
        try:
            # Check if prompt exists in DB and get prompt_context directly
            print(f"Checking for existing records for prompt: {payload.inputPrompt}")
            existing_prompt_context = InsertRecords.fetch_by_prompt(payload.inputPrompt)
           
            if existing_prompt_context:
                # Use the existing prompt_context
                prompt_value = existing_prompt_context
                print(f"Using existing prompt context: {prompt_value}")
            else:
                # Calculate prompt_context as usual
                prompt_context, _ = await context_prompt(prompt=payload.inputPrompt, response=payload.llmResponse)
                prompt_context_json = llm_response_to_json(prompt_context.replace("\n", " "))
                prompt_value = prompt_context_json["Context"]
                print(f"Generated new prompt context: {prompt_value}")
 
            input_prompt = payload.inputPrompt
            llm_response = payload.llmResponse
            agent_flag = payload.agent_flag
           
            prompt_context, response_context = await context_prompt(
            prompt=input_prompt,
            response=llm_response
            )
 
            #prompt_context_json = llm_response_to_json(prompt_context.replace("\n", " "))
            #prompt_value = prompt_context_json["Context"]
 
            response_context_json = llm_response_to_json(response_context.replace("\n", " "))
            response_value = response_context_json["Context"]
            print(f"Response context: {response_value}")
 
            insertion_kwargs = {
                "prompt": input_prompt,
                "response": llm_response,
                "prompt_context": prompt_value,
                "response_context": response_value
            }
           
            # If agent_flag is True, generate additional fields (accuracy & intent)
            if agent_flag:
                print("Agent flag is True - generating accuracy, intent_satisfied, and hallucination along with context")
               
                # Generate accuracy assessment
                accuracy_result = await accuracy_prompt(
                    prompt=input_prompt,
                    response=llm_response,
                    agent_metadata=payload.agent_metadata,
                    agent_name=payload.agent_name
                )
                accuracy_json = llm_response_to_json(accuracy_result.replace("\n", " "))
                accuracy_value = float(accuracy_json["Accuracy"]) if accuracy_json["Accuracy"] else 0.0
               
                # Generate intent satisfaction assessment
                intent_result = await intent_satisfied_prompt(
                    prompt=input_prompt,
                    response=llm_response,
                    agent_metadata=payload.agent_metadata,
                    agent_name=payload.agent_name
                )
                intent_json = llm_response_to_json(intent_result.replace("\n", " "))
                intent_satisfied_value = intent_json["Intent_Satisfied"]
               
                # Generate hallucination assessment
                hallucination_result = await hallucination_prompt(
                    prompt=input_prompt,
                    response=llm_response,
                    agent_metadata=payload.agent_metadata,
                    agent_name=payload.agent_name
                )
                hallucination_json = llm_response_to_json(hallucination_result.replace("\n", " "))
                hallucination_value = float(hallucination_json["Hallucination"]) if hallucination_json["Hallucination"] else 0.0
 
                # Add agent-specific data to insertion
                insertion_kwargs.update({
                    "agent_metadata": payload.agent_metadata,
                    "agent_name": payload.agent_name,
                    "accuracy": accuracy_value,
                    "intent_satisfied": intent_satisfied_value,
                    "hallucination": hallucination_value
                })
                print(f"Agent data included - Agent Name: {payload.agent_name}")
            else:
                print("Agent flag is False - generating only context (existing behavior)")
 
 
            # obj_explain = await InsertRecords.create_context(prompt=payload.inputPrompt, response=payload.llmResponse, prompt_context = prompt_value, response_context = response_value)
            obj_explain = await create_context(**insertion_kwargs)
            print(f"obj_explain: {obj_explain}".encode('ascii', 'ignore').decode('ascii'))
            # return InsertionStatus(response=obj_explain.get('status'), time_taken=obj_explain.get('time_taken'))
            # return ContextResponse(prompt_context=prompt_value, response_context=response_value, success_status=obj_explain)
            response_data = {
                "prompt_context": prompt_value,
                "response_context": response_value,
                "success_status": obj_explain
            }
 
            # Add agent fields to response if agent_flag is True
            if agent_flag:
                response_data.update({
                    "accuracy": accuracy_value,
                    "intent_satisfied": intent_satisfied_value,
                    "hallucination": hallucination_value
                })
 
            return ContextResponse(**response_data)
 
        except Exception as e:
            print(e)
            raise