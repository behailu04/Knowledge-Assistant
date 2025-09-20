"""
Prompt templates for different LangChain operations
"""
from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class PromptTemplates:
    """Collection of prompt templates for various operations"""
    
    @staticmethod
    def get_qa_prompt() -> PromptTemplate:
        """Get the standard QA prompt template"""
        template = """
        You are a helpful AI assistant with access to a knowledge base. Use the following pieces of context to answer the user's question accurately and comprehensively.

        Context:
        {context}

        Question: {question}

        Instructions:
        1. Answer the question based on the provided context
        2. If the context doesn't contain enough information to answer the question, say so clearly
        3. Include relevant citations or references to the source documents
        4. Be concise but complete in your response
        5. If you're uncertain about any part of your answer, indicate your confidence level

        Answer:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    @staticmethod
    def get_conversational_prompt() -> PromptTemplate:
        """Get the conversational prompt template"""
        template = """
        You are a helpful AI assistant having a conversation with a user. Use the following pieces of context and chat history to provide a natural, helpful response.

        Context:
        {context}

        Chat History:
        {chat_history}

        Human: {question}

        Instructions:
        1. Respond naturally as if in a conversation
        2. Use the context to provide accurate information
        3. Reference the chat history for context
        4. Be helpful and engaging
        5. If you don't know something, say so

        AI:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )
    
    @staticmethod
    def get_multi_hop_prompt() -> PromptTemplate:
        """Get the multi-hop reasoning prompt template"""
        template = """
        You are an AI assistant that performs multi-hop reasoning to answer complex questions. You have access to a knowledge base and can search for information in multiple steps.

        Current Step: {current_step}
        Total Steps: {total_steps}
        
        Previous Context:
        {previous_context}

        Current Question/Sub-question: {question}

        Instructions:
        1. Think step by step about what information you need
        2. Search for relevant information if needed
        3. Analyze and synthesize the information
        4. Determine if you need more information or can provide an answer
        5. Be explicit about your reasoning process

        Reasoning Process:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["current_step", "total_steps", "previous_context", "question"]
        )
    
    @staticmethod
    def get_self_consistency_prompt() -> PromptTemplate:
        """Get the self-consistency prompt template"""
        template = """
        You are an AI assistant that provides detailed reasoning for complex questions. Consider multiple perspectives and provide a thorough analysis.

        Question: {question}

        Context: {context}

        Instructions:
        1. Think through the question from multiple angles
        2. Consider different interpretations and approaches
        3. Provide detailed reasoning for your answer
        4. Be explicit about any assumptions or limitations
        5. If uncertain, explain your uncertainty

        Detailed Reasoning:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["question", "context"]
        )
    
    @staticmethod
    def get_query_decomposition_prompt() -> PromptTemplate:
        """Get the query decomposition prompt template"""
        template = """
        Decompose the following complex question into simpler sub-questions that can be answered independently or in sequence.

        Original Question: {question}

        Instructions:
        1. Break down the question into 2-4 sub-questions
        2. Each sub-question should be answerable independently
        3. Indicate the type of each sub-question (retrieval, analysis, comparison, etc.)
        4. Specify the priority and dependencies
        5. Ensure the sub-questions together answer the original question

        Sub-questions:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["question"]
        )
    
    @staticmethod
    def get_synthesis_prompt() -> PromptTemplate:
        """Get the synthesis prompt template"""
        template = """
        Synthesize the following information to provide a comprehensive answer to the question.

        Question: {question}

        Information Sources:
        {sources}

        Instructions:
        1. Combine information from all sources
        2. Identify common themes and patterns
        3. Resolve any contradictions
        4. Provide a coherent, comprehensive answer
        5. Cite specific sources when appropriate

        Synthesized Answer:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["question", "sources"]
        )
    
    @staticmethod
    def get_verification_prompt() -> PromptTemplate:
        """Get the verification prompt template"""
        template = """
        Verify the following answer against the provided sources and assess its accuracy.

        Question: {question}

        Answer: {answer}

        Sources: {sources}

        Instructions:
        1. Check if the answer is supported by the sources
        2. Identify any unsupported claims
        3. Assess the overall accuracy and completeness
        4. Provide a confidence score (0-1)
        5. Suggest improvements if needed

        Verification:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["question", "answer", "sources"]
        )
    
    @staticmethod
    def get_summarization_prompt() -> PromptTemplate:
        """Get the summarization prompt template"""
        template = """
        Summarize the following documents while preserving key information and context.

        Documents:
        {documents}

        Instructions:
        1. Extract the main points from each document
        2. Preserve important details and context
        3. Maintain the original meaning
        4. Keep the summary concise but comprehensive
        5. Include relevant metadata

        Summary:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["documents"]
        )
    
    @staticmethod
    def get_entity_extraction_prompt() -> PromptTemplate:
        """Get the entity extraction prompt template"""
        template = """
        Extract key entities and concepts from the following text.

        Text: {text}

        Instructions:
        1. Identify named entities (people, places, organizations, etc.)
        2. Extract key concepts and topics
        3. Identify relationships between entities
        4. Categorize entities by type
        5. Provide confidence scores for each extraction

        Extracted Entities:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["text"]
        )
    
    @staticmethod
    def get_custom_prompt(template: str, input_variables: List[str]) -> PromptTemplate:
        """Create a custom prompt template"""
        return PromptTemplate(
            template=template,
            input_variables=input_variables
        )
    
    @staticmethod
    def get_prompt_by_type(prompt_type: str) -> PromptTemplate:
        """Get a prompt template by type"""
        prompt_map = {
            "qa": PromptTemplates.get_qa_prompt,
            "conversational": PromptTemplates.get_conversational_prompt,
            "multi_hop": PromptTemplates.get_multi_hop_prompt,
            "self_consistency": PromptTemplates.get_self_consistency_prompt,
            "query_decomposition": PromptTemplates.get_query_decomposition_prompt,
            "synthesis": PromptTemplates.get_synthesis_prompt,
            "verification": PromptTemplates.get_verification_prompt,
            "summarization": PromptTemplates.get_summarization_prompt,
            "entity_extraction": PromptTemplates.get_entity_extraction_prompt
        }
        
        if prompt_type not in prompt_map:
            logger.warning(f"Unknown prompt type: {prompt_type}, using QA prompt")
            return PromptTemplates.get_qa_prompt()
        
        return prompt_map[prompt_type]()
    
    @staticmethod
    def format_prompt_with_context(prompt: PromptTemplate, 
                                 question: str, 
                                 context: str,
                                 **kwargs) -> str:
        """Format a prompt with context and additional variables"""
        try:
            # Prepare input variables
            input_vars = {
                "question": question,
                "context": context,
                **kwargs
            }
            
            # Filter to only include variables that the prompt expects
            filtered_vars = {
                k: v for k, v in input_vars.items() 
                if k in prompt.input_variables
            }
            
            return prompt.format(**filtered_vars)
            
        except Exception as e:
            logger.error(f"Error formatting prompt: {e}")
            return f"Error formatting prompt: {str(e)}"
