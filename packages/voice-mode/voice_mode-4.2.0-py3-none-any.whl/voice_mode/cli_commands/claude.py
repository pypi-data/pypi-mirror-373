"""CLI commands for Claude Code message extraction."""

import click
import json
import os
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from voice_mode.tools.claude_thinking import (
    find_claude_log_file,
    extract_messages_from_log,
    extract_thinking_from_messages
)

logger = logging.getLogger("voice-mode")


@click.group(name='claude')
def claude_group():
    """Extract messages from Claude Code conversation logs."""
    pass


@claude_group.command(name='messages')
@click.option('--last-n', '-n', default=2, type=int,
              help='Number of recent messages to extract (default: 2)')
@click.option('--type', '-t', 'message_types', multiple=True,
              type=click.Choice(['user', 'assistant']),
              help='Filter by message type (can specify multiple)')
@click.option('--format', '-f', 
              type=click.Choice(['full', 'text', 'thinking']),
              default='full',
              help='Output format: full (complete), text (text only), thinking (thinking only)')
@click.option('--working-dir', '-d', type=click.Path(exists=True),
              help='Working directory to find logs for (defaults to CWD)')
@click.option('--output', '-o', type=click.Path(),
              help='Save output to file')
@click.option('--json', 'as_json', is_flag=True,
              help='Output as JSON (overrides format)')
def messages_command(last_n: int, message_types: tuple, format: str,
                    working_dir: Optional[str], output: Optional[str],
                    as_json: bool):
    """
    Extract recent messages from Claude Code logs.
    
    Examples:
    
        voicemode claude messages
        
        voicemode claude messages -n 5 --format thinking
        
        voicemode claude messages --type assistant --format text
        
        voicemode claude messages --json -o messages.json
    """
    # Find log file
    log_file = find_claude_log_file(working_dir)
    if not log_file:
        click.echo(f"Error: Could not find Claude Code logs for directory: {working_dir or os.getcwd()}", err=True)
        return
    
    # Extract messages
    message_type_list = list(message_types) if message_types else None
    messages = extract_messages_from_log(log_file, last_n, message_type_list)
    
    if not messages:
        click.echo("No messages found in recent logs", err=True)
        return
    
    # Format output
    if as_json:
        content = json.dumps(messages, indent=2)
    elif format == 'thinking':
        thinking_texts = extract_thinking_from_messages(messages)
        if not thinking_texts:
            click.echo("No thinking content found", err=True)
            return
        content = "\n\n=== Next Thinking ===\n\n".join(thinking_texts)
    elif format == 'text':
        result = []
        for msg in messages:
            content_text = []
            content_items = msg.get('content', [])
            logger.debug(f"Message has {len(content_items)} content items")
            for item in content_items:
                if isinstance(item, dict):
                    item_type = item.get('type')
                    logger.debug(f"Content item type: {item_type}")
                    if item_type == 'text':
                        text = item.get('text', '')
                        if text:
                            content_text.append(text)
                    elif item_type == 'thinking':
                        text = item.get('text', '')
                        if text:
                            content_text.append(f"[Thinking: {text}]")
            if content_text:
                result.append(f"{msg['type'].title()}: {' '.join(content_text)}")
        content = "\n\n".join(result)
    else:  # full format
        # Format as human-readable
        result = []
        for i, msg in enumerate(messages, 1):
            result.append(f"=== Message {i} ===")
            result.append(f"Type: {msg['type']}")
            result.append(f"Timestamp: {msg.get('timestamp', 'Unknown')}")
            if msg.get('model'):
                result.append(f"Model: {msg['model']}")
            
            # Format content
            content_items = msg.get('content', [])
            if content_items:
                result.append("Content:")
                for item in content_items:
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
        content = "\n".join(result).strip()
    
    # Output
    if output:
        Path(output).write_text(content)
        click.echo(f"Output saved to {output}")
    else:
        # Debug: ensure content is printed
        logger.debug(f"About to output {len(content)} characters")
        click.echo(content)
        logger.debug("Output complete")


@claude_group.command(name='thinking')
@click.option('--last-n', '-n', default=1, type=int,
              help='Number of messages to search for thinking (default: 1)')
@click.option('--working-dir', '-d', type=click.Path(exists=True),
              help='Working directory to find logs for (defaults to CWD)')
def thinking_command(last_n: int, working_dir: Optional[str]):
    """
    Extract only thinking content from Claude Code logs.
    
    Convenience command equivalent to:
    voicemode claude messages --format thinking --type assistant
    
    Examples:
    
        voicemode claude thinking
        
        voicemode claude thinking -n 3
    """
    # Delegate to messages command with thinking format
    ctx = click.get_current_context()
    ctx.invoke(messages_command,
               last_n=last_n,
               message_types=('assistant',),
               format='thinking',
               working_dir=working_dir,
               output=None,
               as_json=False)


@claude_group.command(name='check')
def check_command():
    """
    Check if Claude Code context is available.
    
    Shows information about the Claude Code environment including:
    - Whether Claude Code logs are accessible
    - Current working directory
    - Log file location if found
    - Last update time
    
    Example:
        voicemode claude check
    """
    working_dir = os.getcwd()
    log_file = find_claude_log_file(working_dir)
    
    click.echo(f"Working Directory: {working_dir}")
    click.echo(f"Claude Logs Found: {'Yes' if log_file else 'No'}")
    
    if log_file:
        click.echo(f"Log File: {log_file}")
        click.echo(f"Log Size: {log_file.stat().st_size:,} bytes")
        
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        now = datetime.now()
        age = now - mtime
        
        if age.total_seconds() < 60:
            click.echo(f"Last Updated: {int(age.total_seconds())} seconds ago")
        elif age.total_seconds() < 3600:
            click.echo(f"Last Updated: {int(age.total_seconds() / 60)} minutes ago")
        else:
            click.echo(f"Last Updated: {int(age.total_seconds() / 3600)} hours ago")
    else:
        project_dir = working_dir.replace('/', '-')
        expected_path = Path.home() / '.claude' / 'projects' / project_dir
        click.echo(f"Expected Log Location: {expected_path}")
        click.echo("Note: Logs are only created when using Claude Code (claude.ai/code)")