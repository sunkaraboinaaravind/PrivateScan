import os
import traceback
import gradio as gr
from app.processor import FileProcessor
from app.ai_engine import AIEngine

# Initialize AI engine
ai = AIEngine()

# Detect Gradio 6+ version globally
IS_GRADIO_6 = int(gr.__version__.split(".")[0]) >= 6
print(f"[PrivateScan] Gradio version: {gr.__version__} (Gradio 6+: {IS_GRADIO_6})")

def load_file(file):
    """Processes uploaded file and extracts text."""
    if file is None:
        return "No file selected.", "No file loaded.", gr.update(choices=[]), "", []
    
    file_path = file.name
    file_name = os.path.basename(file_path)
    print(f"[PrivateScan] Loading file: {file_name}")
    
    try:
        res = FileProcessor.extract_text(file_path)
        extracted_text = res["text"]
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
            
        print(f"[PrivateScan] File loaded successfully. Length: {len(extracted_text)} chars")
        return metadata_str, extracted_text, gr.update(choices=models, value=models[0] if models else None), extracted_text, []
    except Exception as e:
        print(f"[PrivateScan Error] Failed to load file: {str(e)}")
        traceback.print_exc()
        return f"❌ Error loading file: {str(e)}", "No text extracted.", gr.update(choices=[]), "", []

def run_analysis(task, model, doc_text):
    """Streams Summarize, PII, or Key Info analysis to the UI."""
    print(f"[PrivateScan] Running task '{task}' with model '{model}'")
    if not doc_text or not doc_text.strip():
        yield "⚠️ Please upload a file first."
        return
    if not model or model == "No models found! Run 'ollama pull llama3.2'":
        yield "⚠️ Please select a valid Ollama model."
        return
    
    output_text = ""
    try:
        for chunk in ai.analyze_document_stream(model, doc_text, task):
            output_text += chunk
            yield output_text
    except Exception as e:
        print(f"[PrivateScan Error] Analysis failed: {str(e)}")
        traceback.print_exc()
        yield f"❌ Error during analysis: {str(e)}"

def chat_respond(user_message, history, model, doc_text):
    """Answers Q&A chat with streaming text support."""
    print(f"[PrivateScan Chat] User message: '{user_message}' using model '{model}'")
    
    # Initialize history list safely
    history = history or []
    
    if not doc_text or not doc_text.strip():
        warning_msg = "⚠️ Please upload a file first."
        if IS_GRADIO_6:
            history.append({"role": "assistant", "content": warning_msg})
        else:
            history.append(("", warning_msg))
        yield "", history
        return
        
    if not model or model == "No models found! Run 'ollama pull llama3.2'":
        warning_msg = "⚠️ Please select a valid Ollama model."
        if IS_GRADIO_6:
            history.append({"role": "assistant", "content": warning_msg})
        else:
            history.append(("", warning_msg))
        yield "", history
        return

    # Format history for the AI engine
    engine_history = []
    
    if IS_GRADIO_6:
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            engine_history.append((role, content))
    else:
        for user_msg, bot_msg in history:
            if user_msg:
                engine_history.append(("user", user_msg))
            if bot_msg:
                engine_history.append(("assistant", bot_msg))

    # Append the user's message and a placeholder for assistant response
    if IS_GRADIO_6:
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": "⌛ Thinking..."})
    else:
        history.append((user_message, "⌛ Thinking..."))
    yield "", history

    try:
        bot_message = ""
        # Stream response
        for chunk in ai.ask_question_stream(model, doc_text, user_message, engine_history):
            bot_message += chunk
            if IS_GRADIO_6:
                history[-1]["content"] = bot_message
            else:
                history[-1] = (user_message, bot_message)
            yield "", history
            
    except Exception as e:
        print(f"[PrivateScan Error] Chat failed: {str(e)}")
        traceback.print_exc()
        error_msg = f"❌ Error: {str(e)}"
        if IS_GRADIO_6:
            history[-1]["content"] = error_msg
        else:
            history[-1] = (user_message, error_msg)
        yield "", history

def check_ollama_status():
    """Checks if Ollama is connected."""
    if ai.check_connection():
        models = ai.list_local_models()
        if models:
            return "✅ Connected to Ollama", gr.update(choices=models, value=models[0])
            
        return "⚠️ Connected, but check pulled models.", gr.update(choices=["llama3.2:3b", "qwen2.5-coder:7b"])
    return "❌ Ollama is offline. Start Ollama on your machine first.", gr.update(choices=[])

# Custom CSS for dark theme
theme_css = """
body {
    background-color: #121212 !important;
    color: #e0e0e0 !important;
}
"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple", secondary_hue="cyan"), css=theme_css) as demo:
    # State variables to hold document text and chat history per session
    doc_text_state = gr.State("")
    
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
        outputs=[file_meta, doc_preview, model_selector, doc_text_state, chatbot]
    )
    
    btn_summarize.click(
        run_analysis,
        inputs=[gr.State("summarize"), model_selector, doc_text_state],
        outputs=[analysis_output]
    )
    
    btn_pii.click(
        run_analysis,
        inputs=[gr.State("pii"), model_selector, doc_text_state],
        outputs=[analysis_output]
    )
    
    btn_key_info.click(
        run_analysis,
        inputs=[gr.State("key_info"), model_selector, doc_text_state],
        outputs=[analysis_output]
    )
    
    msg_input.submit(
        chat_respond,
        inputs=[msg_input, chatbot, model_selector, doc_text_state],
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
