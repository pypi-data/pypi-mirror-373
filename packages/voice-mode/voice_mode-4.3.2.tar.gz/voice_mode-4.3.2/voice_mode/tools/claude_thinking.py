"""Claude Code message extraction tools for Think Out Loud mode and conversation analysis."""

import json
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from voice_mode.server import mcp
from voice_mode.config import THINK_OUT_LOUD_ENABLED

logger = logging.getLogger("voice-mode")


def find_claude_log_file(working_dir: Optional[str] = None) -> Optional[Path]:
    """Find the current Claude Code conversation log file.
    
    Args:
        working_dir: The working directory (defaults to CWD)
        
    Returns:
        Path to the most recent JSONL log file, or None if not found
    """
    if working_dir is None:
        working_dir = os.getcwd()
    
    logger.debug(f"Looking for Claude logs in working_dir: {working_dir}")
    
    # Transform path: /Users/admin/Code/github.com/project → -Users-admin-Code-github-com-project
    # Note: Both slashes and dots are replaced with hyphens
    project_dir = working_dir.replace('/', '-').replace('.', '-')
    logger.debug(f"Transformed project dir: {project_dir}")
    
    # Build path to Claude logs
    claude_base = Path.home() / '.claude' / 'projects'
    log_dir = claude_base / project_dir
    logger.debug(f"Claude log directory: {log_dir}")
    
    if not log_dir.exists():
        logger.warning(f"Claude log directory does not exist: {log_dir}")
        return None
    
    # Find most recent .jsonl file
    log_files = sorted(
        log_dir.glob('*.jsonl'), 
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if log_files:
        logger.info(f"Found {len(log_files)} Claude log files, using most recent: {log_files[0].name}")
        return log_files[0]
    else:
        logger.warning(f"No .jsonl files found in {log_dir}")
        return None


def extract_messages_from_log(log_file: Path, last_n: int = 2, message_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Extract messages from Claude Code JSONL log.
    
    Args:
        log_file: Path to the JSONL log file
        last_n: Number of most recent messages to return (default: 2)
        message_types: Optional list of message types to filter ('user', 'assistant', 'system')
                      If None, returns all message types
        
    Returns:
        List of messages with metadata
    """
    logger.debug(f"Extracting {last_n} messages from {log_file}, types={message_types}")
    messages = []
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        logger.debug(f"Read {len(lines)} lines from log file")
            
        # Process lines in reverse to get most recent first
        for i, line in enumerate(reversed(lines)):
            if not line.strip():
                continue
                
            try:
                entry = json.loads(line)
                entry_type = entry.get('type')
                
                # Filter by message type if specified
                if message_types and entry_type not in message_types:
                    continue
                
                # Extract user or assistant messages
                if entry_type in ['user', 'assistant']:
                    logger.debug(f"Found {entry_type} message at line {len(lines) - i}")
                    message = entry.get('message', {})
                    
                    # Build message info
                    message_info = {
                        'type': entry_type,
                        'role': message.get('role'),
                        'content': message.get('content', []),
                        'timestamp': entry.get('timestamp'),
                        'uuid': entry.get('uuid'),
                        'model': message.get('model') if entry_type == 'assistant' else None
                    }
                    
                    # Add usage info for assistant messages
                    if entry_type == 'assistant' and 'usage' in message:
                        message_info['usage'] = message['usage']
                    
                    messages.append(message_info)
                    
                    if len(messages) >= last_n:
                        logger.info(f"Extracted {len(messages)} messages successfully")
                        return messages
                        
            except json.JSONDecodeError as e:
                logger.debug(f"Skipping invalid JSON at line {len(lines) - i}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error reading log file {log_file}: {e}")
    
    logger.info(f"Extracted {len(messages)} messages (requested {last_n})")    
    return messages


def extract_thinking_from_messages(messages: List[Dict[str, Any]]) -> List[str]:
    """Extract thinking content from a list of messages.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        List of thinking text strings
    """
    thinking_texts = []
    
    for message in messages:
        if message.get('type') == 'assistant':
            content = message.get('content', [])
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'thinking':
                    text = item.get('text', '').strip()
                    if text:
                        thinking_texts.append(text)
    
    return thinking_texts


@mcp.tool
def get_claude_messages(
    last_n: int = 2,
    working_dir: Optional[str] = None,
    message_types: Optional[List[str]] = None,
    format: str = "full"
) -> str:
    """Extract messages from Claude Code conversation logs.
    
    This tool reads Claude Code's conversation logs to extract recent messages
    for Think Out Loud mode and conversation analysis.
    
    Args:
        last_n: Number of most recent messages to return (default: 2)
        working_dir: Working directory to find logs for (defaults to CWD)
        message_types: Optional list to filter by type ('user', 'assistant'). 
                       If None, returns all types.
        format: Output format - 'full' (complete message), 'text' (just text content),
                'thinking' (just thinking content)
        
    Returns:
        The extracted messages in the requested format
    """
    logger.debug(f"get_claude_messages called: last_n={last_n}, working_dir={working_dir}, types={message_types}, format={format}")
    
    # Check if Think Out Loud mode is enabled
    if not THINK_OUT_LOUD_ENABLED:
        logger.warning("Think Out Loud mode is not enabled")
        return "Think Out Loud mode is not enabled. Set VOICEMODE_THINK_OUT_LOUD=true to enable."
    
    # Find the log file
    log_file = find_claude_log_file(working_dir)
    if not log_file:
        return f"Could not find Claude Code logs for directory: {working_dir or os.getcwd()}"
    
    # Extract messages
    messages = extract_messages_from_log(log_file, last_n, message_types)
    
    if not messages:
        return f"No messages found in recent Claude Code logs."
    
    # Format output based on requested format
    if format == "thinking":
        # Extract only thinking content
        thinking_texts = extract_thinking_from_messages(messages)
        if not thinking_texts:
            return "No thinking content found in recent messages."
        if len(thinking_texts) == 1:
            return thinking_texts[0]
        return "\n\n=== Next Thinking ===\n\n".join(thinking_texts)
    
    elif format == "text":
        # Extract just the text content
        result = []
        for msg in messages:
            content_text = []
            for item in msg.get('content', []):
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        content_text.append(item.get('text', ''))
                    elif item.get('type') == 'thinking':
                        content_text.append(f"[Thinking: {item.get('text', '')}]")
            if content_text:
                result.append(f"{msg['type'].title()}: {' '.join(content_text)}")
        return "\n\n".join(result)
    
    else:  # format == "full"
        # Return complete message structure
        result = []
        for i, msg in enumerate(messages, 1):
            result.append(f"=== Message {i} ===")
            result.append(f"Type: {msg['type']}")
            result.append(f"Timestamp: {msg.get('timestamp', 'Unknown')}")
            if msg.get('model'):
                result.append(f"Model: {msg['model']}")
            
            # Format content
            content = msg.get('content', [])
            if content:
                result.append("Content:")
                for item in content:
                    if isinstance(item, dict):
                        item_type = item.get('type', 'unknown')
                        if item_type == 'text':
                            result.append(f"  [Text]: {item.get('text', '')}")
                        elif item_type == 'thinking':
                            result.append(f"  [Thinking]: {item.get('text', '')}")
                        elif item_type == 'tool_use':
                            result.append(f"  [Tool Use]: {item.get('name', '')}")
                        elif item_type == 'tool_result':
                            result.append(f"  [Tool Result]: {item.get('content', '')[:100]}...")
            result.append("")
        
        return "\n".join(result).strip()


@mcp.tool
def check_claude_context() -> str:
    """Check if running in Claude Code context.
    
    Returns information about the Claude Code environment including:
    - Whether Claude Code logs are accessible
    - Current working directory
    - Log file location if found
    """
    working_dir = os.getcwd()
    log_file = find_claude_log_file(working_dir)
    
    result = []
    result.append(f"Working Directory: {working_dir}")
    result.append(f"Claude Logs Found: {'Yes' if log_file else 'No'}")
    
    if log_file:
        result.append(f"Log File: {log_file}")
        result.append(f"Log Size: {log_file.stat().st_size:,} bytes")
        
        # Check for recent activity
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        now = datetime.now()
        age = now - mtime
        
        if age.total_seconds() < 60:
            result.append(f"Last Updated: {int(age.total_seconds())} seconds ago")
        elif age.total_seconds() < 3600:
            result.append(f"Last Updated: {int(age.total_seconds() / 60)} minutes ago")
        else:
            result.append(f"Last Updated: {int(age.total_seconds() / 3600)} hours ago")
    else:
        project_dir = working_dir.replace('/', '-')
        expected_path = Path.home() / '.claude' / 'projects' / project_dir
        result.append(f"Expected Log Location: {expected_path}")
        result.append("Note: Logs are only created when using Claude Code (claude.ai/code)")
    
    return "\n".join(result)