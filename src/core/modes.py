"""LLM interaction modes for educational AI system."""
from typing import List, Dict, Optional
from .hybrid_retriever import HybridRetriever
from .llm_client import LLMClient
from .prompts import get_system_prompt


class EducationalModes:
    """Implements 4 educational AI modes: Mark, Explain, Example, Flashcards."""
    
    def __init__(
        self,
        retriever: HybridRetriever,
        llm_client: LLMClient,
        default_grade_level: str = "high"
    ):
        """Initialize educational modes."""
        self.retriever = retriever
        self.llm = llm_client
        self.default_grade_level = default_grade_level
    
    def _format_context(self, chunks: List[tuple]) -> str:
        """Format retrieved chunks into context string for LLM."""
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, (chunk, score) in enumerate(chunks, 1):
            text = chunk['text']
            metadata = chunk.get('metadata', {})
            subject = metadata.get('subject', 'Unknown')
            grade = metadata.get('grade_level', 'Unknown')
            
            context_parts.append(
                f"[Source {i} - {subject}, Grade {grade}]\n{text}"
            )
        
        return "\n\n".join(context_parts)
    
    def mark(
        self,
        student_answer: str,
        question: str,
        grade_level: Optional[str] = None,
        top_k: int = 3
    ) -> Dict[str, any]:
        """Mark mode: Give feedback on student's answer."""
        chunks = self.retriever.search(question, top_k=top_k)
        context = self._format_context(chunks)
        
        system_prompt = get_system_prompt(
            mode="mark",
            grade_level=grade_level or self.default_grade_level
        )
        
        user_message = f"""Question: {question}

Student's Answer:
{student_answer}

Please evaluate this answer and provide constructive feedback."""
        
        result = self.llm.generate(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context,
            temperature=0.3
        )
        
        return {
            "response": result.get("response"),
            "context_used": len(chunks),
            "tokens_used": result.get("tokens_used", 0),
            "error": result.get("error")
        }
    
    def explain(
        self,
        query: str,
        grade_level: Optional[str] = None,
        top_k: int = 3
    ) -> Dict[str, any]:
        """Explain mode: Simplify and clarify concepts."""
        chunks = self.retriever.search(query, top_k=top_k)
        context = self._format_context(chunks)
        
        system_prompt = get_system_prompt(
            mode="explain",
            grade_level=grade_level or self.default_grade_level
        )
        
        user_message = f"""Please explain this concept: {query}

Help me understand it clearly."""
        
        result = self.llm.generate(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context,
            temperature=0.7
        )
        
        return {
            "response": result.get("response"),
            "context_used": len(chunks),
            "tokens_used": result.get("tokens_used", 0),
            "error": result.get("error")
        }
    
    def example(
        self,
        topic: str,
        grade_level: Optional[str] = None,
        top_k: int = 3
    ) -> Dict[str, any]:
        """Example mode: Generate practice problems and examples."""
        chunks = self.retriever.search(topic, top_k=top_k)
        context = self._format_context(chunks)
        
        system_prompt = get_system_prompt(
            mode="example",
            grade_level=grade_level or self.default_grade_level
        )
        
        user_message = f"""Topic: {topic}

Please create practice problems and examples to help me practice this concept."""
        
        result = self.llm.generate(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context,
            temperature=0.8,
            max_tokens=1500
        )
        
        return {
            "response": result.get("response"),
            "context_used": len(chunks),
            "tokens_used": result.get("tokens_used", 0),
            "error": result.get("error")
        }
    
    def flashcards(
        self,
        topic: str,
        grade_level: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, any]:
        """Flashcards mode: Generate study flashcards."""
        chunks = self.retriever.search(topic, top_k=top_k)
        context = self._format_context(chunks)
        
        system_prompt = get_system_prompt(
            mode="flashcards",
            grade_level=grade_level or self.default_grade_level
        )
        
        user_message = f"""Topic: {topic}

Please create study flashcards covering the key concepts I need to know."""
        
        result = self.llm.generate(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context,
            temperature=0.5,
            max_tokens=1500
        )
        
        return {
            "response": result.get("response"),
            "context_used": len(chunks),
            "tokens_used": result.get("tokens_used", 0),
            "error": result.get("error")
        }
