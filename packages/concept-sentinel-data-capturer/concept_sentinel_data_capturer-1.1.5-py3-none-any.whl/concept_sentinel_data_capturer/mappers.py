from pydantic import BaseModel, Field, model_validator,field_validator
from typing import Optional, List, Dict,Any

class ContextRequest(BaseModel):
    inputPrompt: str = Field(example="Who are the co-founders of Infosys?")
    llmResponse: str = Field(example="Infosys was co-founded by Narayana Murthy along with six other engineers: Nandan Nilekani, S. Gopalakrishnan (Kris), S. D. Shibulal, K. Dinesh, N. S. Raghavan, and Ashok Arora. Established in 1981, Infosys started with a modest capital of $250 and has since grown into one of the largest IT services companies in the world. Narayana Murthy, often regarded as the face of Infosys, played a pivotal role in shaping the company's culture and vision, while the combined efforts of all co-founders contributed to its remarkable growth and success in the global IT industry.")
    agent_flag: bool = Field(default=False, example=True)
    agent_metadata: Optional[List[Dict[str, str]]] = Field(
        default=None, 
        example=[
            {"name": "CandidateSelectionAgent", "description": "Agent for Selection of a candidate"},
            {"name": "InterviewSchedulingAgent", "description": "Agent to Schedule Interview of a candidate"}        
        ]
    )
    agent_name: Optional[str] = Field(default=None, example="ExplanationAgent")
    
    @model_validator(mode='after')
    def validate_agent_fields(self):
        if self.agent_flag:
            if not self.agent_metadata:
                raise ValueError('agent_metadata is required when agent_flag is True')
            if not self.agent_name:
                raise ValueError('agent_name is required when agent_flag is True')
        return self
    
    class Config:
        from_attributes = True



class env_variables(BaseModel):
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_DEPLOYMENT_ENGINE: str
    DB_NAME: str
    COSMOS_PATH: str


    
class ContextResponse(BaseModel):
    prompt_context: str = Field(example= "biggest country in the world?")
    response_context: str = Field(example= "biggest country in the world is Russia")
    success_status: bool = Field(example=True)
    intent_satisfied: Optional[str] = Field(default=None, example="Yes")
    accuracy: Optional[float] = Field(default=None, example="85")
    hallucination: Optional[float] = Field(default=None, example="25")
    
    @field_validator('accuracy', 'intent_satisfied', 'hallucination', mode='before')
    @classmethod
    def convert_to_string(cls, v):
        if v is not None and not isinstance(v, str):
            return str(v)
        return v
    

    class Config:
        from_attributes = True