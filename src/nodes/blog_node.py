from src.states.blogstate import BlogState
from langchain_core.messages import SystemMessage, HumanMessage
from src.states.blogstate import Blog

class BlogNode:
    """
    A class to represent the  blog node
    """

    def __init__(self,llm):
        self.llm = llm

    def title_creation(self,state:BlogState):
        """
        create the title
        """
        if "topic" in state and state["topic"]:
            prompt="""
                   You are aan expert blog content writer.Use markdown formatting . Generate a blog title for the {topic}.This title should be creative

                 """
            
            system_messgae= prompt.format(topic=state["topic"])
            response = self.llm.invoke(system_messgae)
            return {"blog":{"title":response.content}}
        
    def content_generation(self,state:BlogState):
        if "topic" in state and state["topic"]:
            system_prompt = """You are expert blog writer. Use Markdown formatting.
            Generate a detailed blog content with detailed breakdown for the {topic}""" 
            system_message = system_prompt.format(topic=state["topic"])
            response = self.llm.invoke(system_message)
            return {"blog": {"title": state['blog']['title'], "content": response.content}} 

    def translation(self, state: BlogState):
        """
        Translate the content to the specified language.
    
    Args:
        state: BlogState containing 'blog' and 'current_language'
        
    Returns:
        dict: Translated blog content with same structure
        """
        translation_prompt = """
    You are an expert translator. Translate the following blog content into {current_language}:
    - Maintain the original tone, style, and formatting
    - Keep all markdown formatting intact
    - Adapt cultural references appropriately
    - Do not change the structure or headings
    
    ORIGINAL CONTENT:
    {blog_content}
    
    TRANSLATION:
    """

    # Prepare the messages properly for the chat model
        messages = [
        SystemMessage(content="You are a professional translator."),
        HumanMessage(
            content=translation_prompt.format(
                current_language=state['current_language'],
                blog_content=state['blog']['content']
            )
        )
    ]
    
        try:
        # First try without structured output to see if translation works
            translation_result = self.llm.invoke(messages)
        
            return {
            "blog": {
                "title": state['blog']['title'],  # Keep original title or translate separately
                "content": translation_result.content
            }
        }
        
        except Exception as e:
        # Fallback to non-structured output if structured fails
            print(f"Structured output failed, trying regular translation: {str(e)}")
            translation_result = self.llm.invoke(messages)
        
            return {
             "blog": {
                "title": state['blog']['title'],
                "content": translation_result.content
            }
        }

    def route(self,state:BlogState):
        return {"current_language":state['current_language']}


    def route_decision(self, state: BlogState):
        """
        Route the content to the respective translation function.
        """
        if state["current_language"] == "hindi":
            return "hindi"
        elif state["current_language"] == "french":
            return "french"
        else:
            return state["current_language"]
    
        
        