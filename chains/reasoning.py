"""
LangChain Reasoning Chains
Handles LLM interactions and structured reasoning
"""
from langchain_community.chat_models import ChatPerplexity
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from config.settings import LLMConfig
from config.prompts import PromptTemplates
from models.schemas import HealthOverview, SymptomAnalysis


class ReasoningChains:
    """Manages LangChain reasoning chains for health analysis"""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize reasoning chains
        
        Args:
            config: LLM configuration settings
        """
        self.config = config
        
        # Initialize LLM
        self.llm = ChatPerplexity(
            pplx_api_key=config.api_key,
            model=config.model,
            temperature=config.temperature,
            streaming=config.streaming
        )
        
        # Setup parsers
        self.reasoning_parser = PydanticOutputParser(pydantic_object=HealthOverview)
        self.string_parser = StrOutputParser()
        
        # Build chains
        self._build_chains()
    
    def _build_chains(self):
        """Build LangChain LCEL chains"""
        
        # Chain 1: Structured Reasoning
        reasoning_prompt = PromptTemplates.get_reasoning_prompt()
        
        self.reasoning_chain = (
            {
                "conversation": lambda x: x["conversation"],
                "user_input": lambda x: x["user_input"],
                "format_instructions": lambda _: self.reasoning_parser.get_format_instructions()
            }
            | reasoning_prompt
            | self.llm
            | self.reasoning_parser
        )
        
        # Chain 2: Conversational Response
        response_prompt = PromptTemplates.get_conversational_prompt()
        
        self.response_chain = (
            response_prompt
            | self.llm
            | self.string_parser
        )
    
    async def analyze_and_respond(
        self, 
        conversation: str, 
        user_input: str
    ) -> tuple[HealthOverview, str]:
        """
        Two-step reasoning process:
        1. Generate structured health analysis
        2. Convert to conversational response
        
        Args:
            conversation: Full conversation history
            user_input: Latest user message
            
        Returns:
            Tuple of (structured_analysis, conversational_response)
        """
        try:
            # Step 1: Structured reasoning
            structured = await self.reasoning_chain.ainvoke({
                "conversation": conversation,
                "user_input": user_input
            })
            
            # Step 2: Conversational response generation
            response = await self.response_chain.ainvoke({
                "structured_analysis": structured.model_dump_json(indent=2),
                "user_input": user_input
            })
            
            return structured, response
        
        except Exception as e:
            # Return safe fallback on any error
            print(f"⚠️  Reasoning error: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> tuple[HealthOverview, str]:
        """
        Generate safe fallback response when LLM fails
        
        Returns:
            Tuple of (fallback_structured, fallback_message)
        """
        fallback_structured = HealthOverview(
            health_overview="Unable to fully analyze, please consult vet",
            symptom_analysis=SymptomAnalysis(
                symptoms_identified=["Unable to parse"],
                severity_indicators=[],
                duration=None,
                pet_type=None,
                age_mentioned=None
            ),
            risk_level="MODERATE",
            recommendations=["Please consult with a veterinarian"],
            safety_flags=["This is not professional veterinary advice"],
            requires_vet=True
        )
        
        fallback_response = PromptTemplates.get_clarification_prompt()
        
        return fallback_structured, fallback_response
