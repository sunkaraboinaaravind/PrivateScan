import json
import urllib.request
import urllib.error
import base64
import os

class AIEngine:
    """Manages communications with the local Ollama instance."""

    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def check_connection(self):
        """Check if the local Ollama server is running and accessible."""
        try:
            with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=3) as response:
                return response.status == 200
        except Exception:
            return False

    def list_local_models(self):
        """Fetch the list of locally pulled Ollama models."""
        try:
            with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=3) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return [model["name"] for model in data.get("models", [])]
        except Exception:
            pass
        return []

    def generate(self, model, prompt, system_prompt=None, options=None, stream_callback=None):
        """Generate a completion from Ollama. Supports streaming feedback."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        if system_prompt:
            payload["system"] = system_prompt
        if options:
            payload["options"] = options

        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers=headers, 
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as response:
                full_response = []
                for line in response:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        response_part = chunk.get("response", "")
                        full_response.append(response_part)
                        if stream_callback:
                            stream_callback(response_part)
                        if chunk.get("done", False):
                            break
                return "".join(full_response)
        except Exception as e:
            error_msg = f"\nError communicating with local AI model: {str(e)}\nMake sure Ollama is running (`ollama serve`) and the model '{model}' is installed."
            if stream_callback:
                stream_callback(error_msg)
            return error_msg

    def analyze_document(self, model, document_text, task, stream_callback=None):
        """Run standard document analysis tasks: summarize, extract_pii, extract_key_info."""
        
        # Limit text length to avoid context window blowup on small local models
        # 10k words is about 13k tokens, which is usually fine for llama3.2/phi3
        truncated = False
        max_words = 6000
        words = document_text.split()
        if len(words) > max_words:
            document_text = " ".join(words[:max_words]) + "\n\n[DOCUMENT TRUNCATED DUE TO SIZE]"
            truncated = True

        if task == "summarize":
            system_prompt = "You are a professional assistant specializing in summarizing documents cleanly and concisely."
            prompt = (
                "Please read the following document text and provide a concise, structured summary. "
                "Highlight the key topics, main findings, and important takeaways using bullet points where appropriate.\n\n"
                f"--- DOCUMENT START ---\n{document_text}\n--- DOCUMENT END ---\n\nSummary:"
            )
        elif task == "pii":
            system_prompt = "You are a cybersecurity assistant trained to detect personally identifiable information (PII) and sensitive data."
            prompt = (
                "Analyze the document text below. Identify all instances of Personally Identifiable Information (PII) "
                "or sensitive data, including but not limited to: Names, Email Addresses, Phone Numbers, Physical Addresses, "
                "Social Security Numbers (SSN), Passwords, API Keys, and Credit Card details.\n\n"
                "Return a structured list of detected PII categorized by type, followed by a redacted version of the "
                "document where all sensitive values are replaced with placeholders like [REDACTED_NAME], [REDACTED_EMAIL], etc.\n\n"
                f"--- DOCUMENT START ---\n{document_text}\n--- DOCUMENT END ---\n"
            )
        elif task == "key_info":
            system_prompt = "You are an analytical assistant specializing in structured data extraction."
            prompt = (
                "Read the document below and extract key information. Identify and list the following if present: "
                "1. Important Dates and Deadlines\n"
                "2. Names of People and Organizations\n"
                "3. Monetary Amounts and Transactions\n"
                "4. Actions Items or next steps\n"
                "5. Subject/Topic and Category of the document\n\n"
                "Format the output as a clean, readable Markdown document with headers.\n\n"
                f"--- DOCUMENT START ---\n{document_text}\n--- DOCUMENT END ---\n"
            )
        else:
            raise ValueError(f"Unknown analysis task: {task}")

        if truncated and stream_callback:
            stream_callback("[Notice: Large document detected. Text truncated to the first 6,000 words for local processing.]\n\n")

        return self.generate(model, prompt, system_prompt=system_prompt, stream_callback=stream_callback)

    def ask_question(self, model, document_text, question, conversation_history=None, stream_callback=None):
        """Ask a question about the document text, incorporating previous history if available."""
        system_prompt = (
            "You are a helpful, offline AI assistant. Answer the user's question accurately using ONLY "
            "the provided document content. If the answer cannot be found in the document, state that clearly "
            "but try to help as much as possible with details from the document. Do not make up information."
        )

        history_context = ""
        if conversation_history:
            history_context = "Previous Conversation History:\n"
            for role, msg in conversation_history[-6:]:  # limit to last 3 turns
                history_context += f"{role.capitalize()}: {msg}\n"
            history_context += "\n"

        prompt = (
            f"--- DOCUMENT CONTENT START ---\n{document_text}\n--- DOCUMENT CONTENT END ---\n\n"
            f"{history_context}"
            f"User Question: {question}\n\n"
            "Response:"
        )

        return self.generate(model, prompt, system_prompt=system_prompt, stream_callback=stream_callback)
