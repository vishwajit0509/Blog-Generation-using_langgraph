from langgraph.graph import StateGraph, START, END
from src.llms.groqllm import GroqLLM
from src.states.blogstate import BlogState
from src.nodes.blog_node import BlogNode

class GraphBuilder:
    def __init__(self, llm):
        self.llm = llm
        self.graph = StateGraph(BlogState)

    def build_topic_graph(self):
        """Build a simple graph for blog generation with just topic (English)."""
        self.blog_node_obj = BlogNode(self.llm)

        self.graph.add_node("title_creation", self.blog_node_obj.title_creation)
        self.graph.add_node("content_generation", self.blog_node_obj.content_generation)

        self.graph.add_edge(START, "title_creation")
        self.graph.add_edge("title_creation", "content_generation")
        self.graph.add_edge("content_generation", END)

        return self.graph

    def build_language_graph(self):
        """Build graph for blog generation with multilingual support."""
        self.blog_node_obj = BlogNode(self.llm)

        # Common Nodes
        self.graph.add_node("title_creation", self.blog_node_obj.title_creation)
        self.graph.add_node("content_generation", self.blog_node_obj.content_generation)

        # Route node
        self.graph.add_node("route", self.blog_node_obj.route)

        # Language-specific translation nodes
        self.graph.add_node("english_translation", lambda state: self.blog_node_obj.translation({**state, "current_language": "English"}))
        self.graph.add_node("hindi_translation", lambda state: self.blog_node_obj.translation({**state, "current_language": "hindi"}))
        self.graph.add_node("french_translation", lambda state: self.blog_node_obj.translation({**state, "current_language": "french"}))
        self.graph.add_node("spanish_translation", lambda state: self.blog_node_obj.translation({**state, "current_language": "spanish"}))
        self.graph.add_node("german_translation", lambda state: self.blog_node_obj.translation({**state, "current_language": "german"}))

        # Main edges
        self.graph.add_edge(START, "title_creation")
        self.graph.add_edge("title_creation", "content_generation")
        self.graph.add_edge("content_generation", "route")

        # Conditional branching based on language
        self.graph.add_conditional_edges(
            "route",
            self.blog_node_obj.route_decision,
            {   "english":"english_translation",
                "hindi": "hindi_translation",
                "french": "french_translation",
                "spanish": "spanish_translation",
                "german": "german_translation"
            }
        )

        # Final language-specific exits
        self.graph.add_edge("english_translation", END)
        self.graph.add_edge("hindi_translation", END)
        self.graph.add_edge("french_translation", END)
        self.graph.add_edge("spanish_translation", END)
        self.graph.add_edge("german_translation", END)

        return self.graph

    def setup_graph(self, usecase):
        if usecase == "topic":
            self.build_topic_graph()

        if usecase == "language":
            self.build_language_graph()

        return self.graph.compile()

# For LangSmith/Studio direct test (optional during local testing)
if __name__ == "__main__":
    llm = GroqLLM().get_llm()
    graph_builder = GraphBuilder(llm)
    graph = graph_builder.build_language_graph().compile()
