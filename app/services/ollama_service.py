"""
Ollama Service - LLM inference using Ollama
"""
from typing import List, Dict, Any, Optional
import ollama
from app.config import settings


class OllamaService:
    """Service for interacting with Ollama LLM"""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.temperature = settings.ollama_temperature
        self.max_tokens = settings.ollama_max_tokens

        # Initialize Ollama client with base URL
        self.client = ollama.Client(host=self.base_url)

        # System prompt for RAG chat
        self.system_prompt = """Eres un asistente útil que responde preguntas basándote SOLAMENTE en el contexto proporcionado.

REGLAS IMPORTANTES:
1. Responde SOLO usando información del contexto proporcionado
2. Si la respuesta no está en el contexto, di "No tengo esa información en el documento"
3. Sé conciso y directo
4. Cita partes relevantes del contexto cuando sea apropiado
5. Responde en el mismo idioma de la pregunta
6. No inventes información que no esté en el contexto

Contexto del documento:
{context}

Conversación:
{chat_history}

Pregunta del usuario: {query}

Respuesta:"""

    def query(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Query Ollama model with a prompt
        """
        try:
            response = self.client.chat(
                model=model or self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': temperature or self.temperature,
                    'num_predict': max_tokens or self.max_tokens,
                    'top_p': 0.9
                }
            )

            return response['message']['content']

        except Exception as e:
            raise Exception(f"Error querying Ollama: {str(e)}")

    def chat(
        self,
        query: str,
        context_chunks: List[str],
        chat_history: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Chat with context from RAG
        system_instruction: Optional custom system instruction (overrides default)
        """
        # Format context
        context = "\n\n---\n\n".join(context_chunks)

        # Format chat history
        history_text = ""
        if chat_history:
            for msg in chat_history[-5:]:  # Last 5 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'user':
                    history_text += f"Usuario: {content}\n"
                elif role == 'assistant':
                    history_text += f"Asistente: {content}\n"

        # Use custom system instruction if provided, otherwise use default
        if system_instruction:
            # Custom instruction - user provides full control
            prompt = f"""{system_instruction}

Contexto del documento:
{context}

Conversación previa:
{history_text if history_text else "Esta es la primera pregunta."}

Pregunta del usuario: {query}

Respuesta:"""
        else:
            # Default system prompt
            prompt = self.system_prompt.format(
                context=context,
                chat_history=history_text if history_text else "Esta es la primera pregunta.",
                query=query
            )

        # Query model
        return self.query(prompt)

    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Ollama"""
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': 'Say "OK" if you are working.'
                }],
                options={
                    'temperature': 0.1,
                    'num_predict': 10
                }
            )

            return {
                "status": "success",
                "model": self.model,
                "response": response['message']['content']
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Singleton instance
ollama_service = OllamaService()
