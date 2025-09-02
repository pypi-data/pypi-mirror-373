import re
import json
from pathlib import Path
from typing import Tuple, Dict

import google.generativeai as genai
from rich.syntax import Syntax

# ==============================================================================
# CORE LOGIC & PARSING (No changes here)
# ==============================================================================

CONFLICT_BLOCK_RE = re.compile(
    r"<<<<<<< (?:HEAD|ours).*\n(.*?)\n=======\n(.*?)\n>>>>>>> .*\n?",
    re.S
)

def parse_first_conflict(text: str) -> Tuple[str, str, str, str] | None:
    match = CONFLICT_BLOCK_RE.search(text)
    if not match:
        return None
    
    head_version = match.group(1).strip()
    incoming_version = match.group(2).strip()
    
    start_index = match.start()
    end_index = match.end()
    content_before = text[:start_index]
    content_after = text[end_index:]
    
    return head_version, incoming_version, content_before, content_after

def replace_first_conflict_with(text: str, merged: str) -> str:
    if not merged.endswith('\n'):
        merged += '\n'
    return CONFLICT_BLOCK_RE.sub(merged, text, count=1)

def get_file_language(filename: str) -> str:
    extension_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.java': 'Java', '.go': 'Go', '.rs': 'Rust', '.html': 'HTML',
        '.css': 'CSS', '.json': 'JSON', '.md': 'Markdown',
    }
    extension = Path(filename).suffix.lower()
    return extension_map.get(extension, "text")

# ==============================================================================
# AI INTERACTION (Synchronous versions for the simple CLI)
# ==============================================================================

def call_gemini_for_resolution(prompt: str, model_name: str) -> Dict:
    # ... (This function remains unchanged for the CLI tool)
    try:
        model = genai.GenerativeModel(model_name)
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        resp = model.generate_content(prompt, generation_config=generation_config)
        response_text = resp.text or "{}"
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON object found in the AI response.")
        json_string = match.group(0)
        return json.loads(json_string)
    except Exception as e:
        raise RuntimeError(f"Sync AI Error: {e}")

def call_gemini_for_explanation(prompt: str, model_name: str) -> str:
    # ... (This function remains unchanged for the CLI tool)
    model = genai.GenerativeModel(model_name)
    resp = model.generate_content(prompt)
    return resp.text or ""
    
# ==============================================================================
# ASYNCHRONOUS AI INTERACTION (NEW: For the TUI)
# ==============================================================================

async def async_call_gemini_for_resolution(prompt: str, model_name: str) -> Dict:
    """Asynchronously calls the Gemini API for resolution."""
    try:
        model = genai.GenerativeModel(model_name)
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        # Use the async method
        resp = await model.generate_content_async(prompt, generation_config=generation_config)
        response_text = resp.text or "{}"
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON object found in the AI response.")
        json_string = match.group(0)
        return json.loads(json_string)
    except Exception as e:
        raise RuntimeError(f"Async AI Error: {e}")

async def async_call_gemini_for_explanation(prompt: str, model_name: str) -> str:
    """Asynchronously calls the Gemini API for an explanation."""
    model = genai.GenerativeModel(model_name)
    resp = await model.generate_content_async(prompt)
    return resp.text or ""


# ==============================================================================
# PROMPT ENGINEERING (No changes here)
# ==============================================================================

def get_resolve_prompt(filename: str, head: str, incoming: str, strategy: str) -> str:
    # ... (This function remains unchanged)
    language = get_file_language(filename)
    strategy_instructions = {
        "cautious": "When in doubt, preserve both changes and add comments explaining the potential issue. Prioritize safety and clarity.",
        "aggressive": "Prioritize creating the most concise and modern code. If one change is clearly outdated, discard it in favor of the more significant logical change.",
    }
    return f"""
    You are an expert Senior Software Architect resolving a Git merge conflict in a {language} file named '{filename}'.
    Your task is to analyze the two conflicting code versions and provide an intelligent resolution as a JSON object.
    STRATEGY: {strategy.upper()}
    {strategy_instructions.get(strategy, "")}
    RULES:
    1. Analyze the intent and logic of both code versions.
    2. Your goal is to logically merge the changes, not just pick one.
    3. The `confidence_score` should be an integer between 0 and 100, representing your confidence that the merge is correct and requires no human intervention. A score of 95+ means you are almost certain the merge is perfect. A score below 70 means a human should definitely review it.
    4. Your final output MUST be ONLY a valid JSON object with two keys: "resolved_code" (string) and "confidence_score" (integer).
    ---
    CONFLICTING CODE BLOCK 1 (Current/Ours version):
    {head}
    ---
    CONFLICTING CODE BLOCK 2 (Incoming/Theirs version):
    {incoming}
    ---
    Provide the resolution as a valid JSON object:
    """

def get_explain_prompt(filename: str, head: str, incoming: str) -> str:
    # ... (This function remains unchanged)
    language = get_file_language(filename)
    return f"""
    You are an expert Senior Software Architect explaining a Git merge conflict in a {language} file named '{filename}'.
    Your task is to analyze the two conflicting code versions and explain the situation clearly to a developer.
    RULES:
    1. Identify the likely cause of the conflict (e.g., "Both branches modified the same function...").
    2. Explain the intent of the changes in both the "Current/Ours version" and the "Incoming/Theirs version".
    3. Suggest a logical path to resolution.
    4. Your explanation should be concise, clear, and formatted in Markdown.
    ---
    CONFLICTING CODE BLOCK 1 (Current/Ours version):
    {head}
    ---
    CONFLICTING CODE BLOCK 2 (Incoming/Theirs version):
    {incoming}
    ---
    Provide your explanation:
    """

