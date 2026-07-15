import os
import gradio as gr
from app.processor import FileProcessor
from app.ai_engine import AIEngine

# Initialize AI engine
ai = AIEngine()

# State variables
current_document_text = ""
conversation_history = []

def load_file(file):
    """Processes uploaded file and extracts text."""
    global current_document_text, conversation_history
    if file is None:
        return "No file selected.", "No file loaded.", gr.update(choices=[])
    
    # Reset state
    conversation_history = []
    
    file_path = file.name
    file_name = os.path.basename(file_path)
    
    try:
        res = FileProcessor.extract_text(file_path)
        current_document_text = res["text"]
        meta = res["metadata"]
        
        kb_size = round(meta["size_bytes"] / 1024, 2)
        metadata_str = (
            f"📄 **Name:** {meta['name']}\n"
            f"📂 **Type:** {meta['type']}\n"
            f"⚖️ **Size:** {kb_size} KB\n"
            f"📍 **Path:** {meta['path']}"
        )
        
        # Check models
        models = ai.list_local_models()
        if not models:
            models = ["No models found! Run 'ollama pull llama3.2'"]
            
        return metadata_str, current_document_text, gr.update(choices=models, value=models[0] if models else None)
    except Exception as e:
        current_document_text = ""
        return f"❌ Error loading file: {str(e)}", "No text extracted.", gr.update(choices=[])

def run_analysis(task, model):
    """Runs Summarize, PII, or Key Info analysis."""
    global current_document_text
    if not current_document_text.strip():
        return "Please upload a file first."
    if not model or model == "No models found! Run 'ollama pull llama3.2'":
        return "Please select a valid Ollama model."
    
    # We call AI engine generate
    return ai.analyze_document(model, current_document_text, task)

def chat_respond(user_message, history, model):
    """Answers Q&A chat about the document."""
    global current_document_text, conversation_history
    if not current_document_text.strip():
        return "", history + [["User", "Please upload a file first."]]
    if not model or model == "No models found! Run 'ollama pull llama3.2'":
        return "", history + [["User", "Please select a valid Ollama model."]]
    
    # Format history for engine
    engine_history = []
    for user_msg, bot_msg in history:
        engine_history.append(("user", user_msg))
        engine_history.append(("assistant", bot_msg))
        
    bot_message = ai.ask_question(model, current_document_text, user_message, engine_history)
    
    history.append((user_message, bot_message))
    return "", history

def check_ollama_status():
    """Checks if Ollama is connected."""
    if ai.check_connection():
        models = ai.list_local_models()
        if models:
            return "✅ Connected to Ollama", gr.update(choices=models, value=models[0])
        return "⚠️ Connected, but no models pulled. Run 'ollama pull llama3.2'", gr.update(choices=[])
    return "❌ Ollama is offline. Start Ollama on your machine first.", gr.update(choices=[])

# Define Custom CSS for beautiful theme
theme_css = """
body {
    background-color: #121212 !important;
    color: #e0e0e0 !important;
}
.gradio-container {
    max-width: 1200px !important;
}
"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple", secondary_hue="cyan"), css=theme_css) as demo:
    gr.Markdown(
        """
        # 🔒 PrivateScan — Web Console
        ### 100% On-Device Document & Image Analyzer. Nothing leaves your machine.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            ollama_status = gr.Textbox(label="Ollama Connection Status", value="Checking...", interactive=False)
            model_selector = gr.Dropdown(label="Select Local Model", choices=[], interactive=True)
            refresh_status_btn = gr.Button("🔄 Check/Refresh Ollama")
            
        with gr.Column(scale=2):
            file_uploader = gr.File(label="Upload or Drop File Here", file_types=[".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx", ".xls", ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".py", ".js", ".html", ".css", ".java", ".c", ".cpp"])
            file_meta = gr.Markdown("No document loaded.")

    with gr.Tab("📝 Document Preview"):
        doc_preview = gr.Textbox(label="Extracted Text", lines=15, max_lines=25, interactive=False, placeholder="Extracted text will appear here.")
        
    with gr.Tab("✨ Document Analysis"):
        with gr.Row():
            btn_summarize = gr.Button("📝 Summarize Document", variant="primary")
            btn_pii = gr.Button("🔍 Detect PII & Redact", variant="secondary")
            btn_key_info = gr.Button("🔑 Extract Key Details", variant="secondary")
        
        analysis_output = gr.Markdown(label="Analysis Results", value="Click an action button above to start analysis.")

    with gr.Tab("💬 Ask Document (Local Chat)"):
        chatbot = gr.Chatbot(label="Document Conversation Chat")
        msg_input = gr.Textbox(label="Ask a question about the document", placeholder="What are the key terms mentioned in this document?")
        clear_chat_btn = gr.ClearButton([msg_input, chatbot])

    # Connect components
    file_uploader.change(
        load_file, 
        inputs=[file_uploader], 
        outputs=[file_meta, doc_preview, model_selector]
    )
    
    btn_summarize.click(
        lambda m: run_analysis("summarize", m),
        inputs=[model_selector],
        outputs=[analysis_output]
    )
    
    btn_pii.click(
        lambda m: run_analysis("pii", m),
        inputs=[model_selector],
        outputs=[analysis_output]
    )
    
    btn_key_info.click(
        lambda m: run_analysis("key_info", m),
        inputs=[model_selector],
        outputs=[analysis_output]
    )
    
    msg_input.submit(
        chat_respond,
        inputs=[msg_input, chatbot, model_selector],
        outputs=[msg_input, chatbot]
    )
    
    refresh_status_btn.click(
        check_ollama_status,
        outputs=[ollama_status, model_selector]
    )
    
    # Run status check on load
    demo.load(check_ollama_status, outputs=[ollama_status, model_selector])

if __name__ == "__main__":
    demo.launch(inbrowser=True, server_name="127.0.0.1", server_port=7860)
