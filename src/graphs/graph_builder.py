from langgraph.graph import StateGraph, START, END
from src.llms.groqllm import GroqLLM
from src.states.blogstate import BlogState, Language
from src.nodes.blog_node import BlogNode
from pydub import AudioSegment
import os
from typing import Dict, Any

# Configure audio converter path
AudioSegment.converter = "C:\\ffmpeg\\bin\\ffmpeg.exe"  # replace path if different

class GraphBuilder:
    """Builds and configures blog generation workflows based on use cases."""
    
    def __init__(self, llm):
        self.llm = llm
        self.graph = StateGraph(BlogState)
        self.blog_node = BlogNode(self.llm)
        self._reset_graph()

    def _reset_graph(self):
        """Reset the graph for new workflow construction"""
        self.graph = StateGraph(BlogState)

    def _add_translation_nodes(self):
        """Add language translation nodes to the graph"""
        for lang in Language:
            self.graph.add_node(
                f"{lang.value}_translation",
                lambda state, lang=lang: self.blog_node.translation({
                    **state,
                    "current_language": lang.value
                })
            )

    def build_topic_graph(self) -> StateGraph:
        """Build basic topic-to-blog workflow"""
        self._reset_graph()
        
        self.graph.add_node("title_creation", self.blog_node.title_creation)
        self.graph.add_node("content_generation", self.blog_node.content_generation)

        self.graph.add_edge(START, "title_creation")
        self.graph.add_edge("title_creation", "content_generation")
        self.graph.add_edge("content_generation", END)

        return self.graph

    def build_language_graph(self) -> StateGraph:
        """Build workflow with language translation support"""
        self._reset_graph()
        
        self.graph.add_node("title_creation", self.blog_node.title_creation)
        self.graph.add_node("content_generation", self.blog_node.content_generation)
        self.graph.add_node("route", self.blog_node.route)

        self._add_translation_nodes()

        # Define workflow edges
        self.graph.add_edge(START, "title_creation")
        self.graph.add_edge("title_creation", "content_generation")
        self.graph.add_edge("content_generation", "route")

        # Conditional routing based on language
        self.graph.add_conditional_edges(
            "route",
            self.blog_node.route_decision,
            {lang.value: f"{lang.value}_translation" for lang in Language}
        )

        # Connect all translation nodes to END
        for lang in Language:
            self.graph.add_edge(f"{lang.value}_translation", END)

        return self.graph

    def build_voice_graph(self) -> StateGraph:
        """Build workflow with voice input/output support"""
        self._reset_graph()
        
        # Add core nodes
        self.graph.add_node("voice_input", self.blog_node.voice_input_node)
        self.graph.add_node("title_creation", self.blog_node.title_creation)
        self.graph.add_node("content_generation", self.blog_node.content_generation)
        self.graph.add_node("route", self.blog_node.route)
        self.graph.add_node("voice_output", self.blog_node.voice_output_node)

        self._add_translation_nodes()

        # Define workflow edges
        self.graph.add_edge(START, "voice_input")
        self.graph.add_edge("voice_input", "title_creation")
        self.graph.add_edge("title_creation", "content_generation")
        self.graph.add_edge("content_generation", "route")

        # Conditional routing based on language
        self.graph.add_conditional_edges(
            "route",
            self.blog_node.route_decision,
            {lang.value: f"{lang.value}_translation" for lang in Language}
        )

        # Connect translations to voice output
        for lang in Language:
            self.graph.add_edge(f"{lang.value}_translation", "voice_output")
        
        self.graph.add_edge("voice_output", END)

        return self.graph

    def setup_graph(self, usecase: str) -> Any:
        """
        Configure and compile the appropriate workflow graph.
        
        Args:
            usecase: One of 'topic', 'language', or 'voice'
            
        Returns:
            Compiled graph ready for execution
        """
        usecase = usecase.lower()
        if usecase == "topic":
            graph = self.build_topic_graph()
        elif usecase == "language":
            graph = self.build_language_graph()
        elif usecase == "voice":
            graph = self.build_voice_graph()
        else:
            raise ValueError(f"Invalid usecase: {usecase}. Must be 'topic', 'language', or 'voice'")

        return graph.compile()


if __name__ == "__main__":
    # Test the voice workflow
    llm = GroqLLM().get_llm()
    graph_builder = GraphBuilder(llm)
    graph = graph_builder.setup_graph("voice")
    print("Voice workflow graph compiled successfully")