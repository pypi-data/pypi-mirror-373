"""
Session Cache Parser

Parses Claude Code .jsonl session files to extract conversation history,
tool usage patterns, token metrics, and usage insights.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator

from .models import (
    SessionMessage, ToolUsage, TokenMetrics, SessionAnalysis,
    MessageRole, MessageType, FileAccessPattern, CacheConfig
)

logger = logging.getLogger(__name__)


class SessionCacheParser:
    """Parser for Claude Code session cache files (.jsonl format)."""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize parser with optional configuration."""
        self.config = config or CacheConfig()
        self.stats = {
            'files_parsed': 0,
            'messages_parsed': 0,
            'errors_encountered': 0,
            'parse_time_seconds': 0.0
        }
    
    def parse_session_file(self, file_path: Path) -> Optional[SessionAnalysis]:
        """
        Parse a single .jsonl session file.
        
        Args:
            file_path: Path to the .jsonl session file
            
        Returns:
            SessionAnalysis object or None if parsing fails
        """
        start_time = datetime.now()
        
        try:
            if not file_path.exists():
                logger.warning(f"Session file not found: {file_path}")
                return None
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.max_file_size_mb:
                logger.warning(f"Session file too large ({file_size_mb:.1f}MB): {file_path}")
                return None
            
            logger.info(f"Parsing session file: {file_path}")
            
            messages = list(self._parse_messages(file_path))
            if not messages:
                logger.warning(f"No valid messages found in: {file_path}")
                return None
            
            analysis = self._analyze_session(messages, file_path)
            
            # Update stats
            self.stats['files_parsed'] += 1
            self.stats['messages_parsed'] += len(messages)
            self.stats['parse_time_seconds'] += (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Parsed {len(messages)} messages from session {analysis.session_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error parsing session file {file_path}: {e}")
            self.stats['errors_encountered'] += 1
            return None
    
    def _parse_messages(self, file_path: Path) -> Iterator[SessionMessage]:
        """
        Parse messages from .jsonl file.
        
        Args:
            file_path: Path to .jsonl file
            
        Yields:
            SessionMessage objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        message = self._parse_message_data(data)
                        if message:
                            yield message
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON on line {line_num} in {file_path}: {e}")
                        continue
                    except Exception as e:
                        logger.warning(f"Error parsing line {line_num} in {file_path}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return
    
    def _parse_message_data(self, data: Dict[str, Any]) -> Optional[SessionMessage]:
        """
        Parse a single message from JSON data.
        
        Args:
            data: JSON data for a single message
            
        Returns:
            SessionMessage object or None if parsing fails
        """
        try:
            # Extract basic fields
            uuid = data.get('uuid')
            if not uuid:
                return None
            
            parent_uuid = data.get('parentUuid')
            session_id = data.get('sessionId')
            timestamp_str = data.get('timestamp')
            
            if not timestamp_str:
                return None
            
            # Parse timestamp
            timestamp = self._parse_timestamp(timestamp_str)
            if not timestamp:
                return None
            
            # Determine message type and role
            message_type = MessageType(data.get('type', 'user'))
            
            # Extract message content and role
            message_data = data.get('message', {})
            role_str = message_data.get('role', 'user')
            role = MessageRole(role_str)
            content = message_data.get('content', '')
            
            # Parse token metrics
            token_metrics = None
            usage_data = message_data.get('usage')
            if usage_data:
                token_metrics = self._parse_token_metrics(usage_data)
            
            # Parse tool usage
            tool_usage = []
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                        tool = self._parse_tool_usage(item, timestamp)
                        if tool:
                            tool_usage.append(tool)
            
            return SessionMessage(
                uuid=uuid,
                parent_uuid=parent_uuid,
                message_type=message_type,
                role=role,
                content=content,
                timestamp=timestamp,
                token_metrics=token_metrics,
                tool_usage=tool_usage,
                request_id=data.get('requestId'),
                session_id=session_id,
                git_branch=data.get('gitBranch'),
                working_directory=data.get('cwd')
            )
            
        except Exception as e:
            logger.warning(f"Error parsing message data: {e}")
            return None
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object."""
        try:
            # Handle ISO format timestamps
            if 'T' in timestamp_str:
                if timestamp_str.endswith('Z'):
                    return datetime.fromisoformat(timestamp_str[:-1]).replace(tzinfo=timezone.utc)
                else:
                    return datetime.fromisoformat(timestamp_str)
            else:
                # Handle other formats if needed
                return datetime.fromisoformat(timestamp_str)
                
        except Exception as e:
            logger.warning(f"Error parsing timestamp '{timestamp_str}': {e}")
            return None
    
    def _parse_token_metrics(self, usage_data: Dict[str, Any]) -> TokenMetrics:
        """Parse token usage metrics."""
        cache_creation = usage_data.get('cache_creation', {})
        
        return TokenMetrics(
            input_tokens=usage_data.get('input_tokens', 0),
            output_tokens=usage_data.get('output_tokens', 0),
            cache_creation_input_tokens=usage_data.get('cache_creation_input_tokens', 0),
            cache_read_input_tokens=usage_data.get('cache_read_input_tokens', 0),
            ephemeral_5m_input_tokens=cache_creation.get('ephemeral_5m_input_tokens', 0),
            ephemeral_1h_input_tokens=cache_creation.get('ephemeral_1h_input_tokens', 0)
        )
    
    def _parse_tool_usage(self, tool_data: Dict[str, Any], timestamp: datetime) -> Optional[ToolUsage]:
        """Parse tool usage information."""
        try:
            return ToolUsage(
                tool_name=tool_data.get('name', 'unknown'),
                tool_id=tool_data.get('id', ''),
                parameters=tool_data.get('input', {}),
                timestamp=timestamp,
                success=True  # Assume success unless we have error info
            )
        except Exception as e:
            logger.warning(f"Error parsing tool usage: {e}")
            return None
    
    def _analyze_session(self, messages: List[SessionMessage], file_path: Path) -> SessionAnalysis:
        """
        Analyze parsed messages to create session analysis.
        
        Args:
            messages: List of parsed messages
            file_path: Original file path for reference
            
        Returns:
            SessionAnalysis object
        """
        if not messages:
            raise ValueError("No messages to analyze")
        
        # Basic session info
        session_id = messages[0].session_id or file_path.stem
        start_time = min(msg.timestamp for msg in messages)
        end_time = max(msg.timestamp for msg in messages)
        
        # Calculate metrics
        total_tokens = sum(msg.estimated_tokens for msg in messages)
        
        # Extract file operations
        file_operations = []
        for msg in messages:
            file_operations.extend(
                tool for tool in msg.tool_usage 
                if tool.is_file_operation
            )
        
        # Count context switches
        context_switches = sum(1 for msg in messages if msg.is_context_switch)
        
        # Calculate cache efficiency
        token_metrics_list = [msg.token_metrics for msg in messages if msg.token_metrics]
        cache_efficiency = 0.0
        if token_metrics_list:
            total_cache_read = sum(tm.cache_read_input_tokens for tm in token_metrics_list)
            total_cache_creation = sum(tm.cache_creation_input_tokens for tm in token_metrics_list)
            if total_cache_creation > 0:
                cache_efficiency = total_cache_read / total_cache_creation
        
        # Extract unique values
        working_directories = list(set(
            msg.working_directory for msg in messages 
            if msg.working_directory
        ))
        
        git_branches = list(set(
            msg.git_branch for msg in messages 
            if msg.git_branch
        ))
        
        # Calculate average response time (simplified)
        total_duration = (end_time - start_time).total_seconds()
        average_response_time = total_duration / len(messages) if messages else 0
        
        return SessionAnalysis(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            total_messages=len(messages),
            total_tokens=total_tokens,
            file_operations=file_operations,
            context_switches=context_switches,
            average_response_time=average_response_time,
            cache_efficiency=cache_efficiency,
            working_directories=working_directories,
            git_branches=git_branches
        )
    
    def analyze_file_access_patterns(self, sessions: List[SessionAnalysis]) -> List[FileAccessPattern]:
        """
        Analyze file access patterns across multiple sessions.
        
        Args:
            sessions: List of session analyses
            
        Returns:
            List of file access patterns
        """
        file_access_map: Dict[str, Dict[str, Any]] = {}
        
        for session in sessions:
            for tool_usage in session.file_operations:
                file_path = tool_usage.file_path
                if not file_path:
                    continue
                
                if file_path not in file_access_map:
                    file_access_map[file_path] = {
                        'count': 0,
                        'first_access': tool_usage.timestamp,
                        'last_access': tool_usage.timestamp,
                        'operations': set(),
                        'total_size': 0
                    }
                
                entry = file_access_map[file_path]
                entry['count'] += 1
                entry['first_access'] = min(entry['first_access'], tool_usage.timestamp)
                entry['last_access'] = max(entry['last_access'], tool_usage.timestamp)
                entry['operations'].add(tool_usage.tool_name)
                
                if tool_usage.result_size:
                    entry['total_size'] += tool_usage.result_size
        
        # Convert to FileAccessPattern objects
        patterns = []
        for file_path, data in file_access_map.items():
            pattern = FileAccessPattern(
                file_path=file_path,
                access_count=data['count'],
                first_access=data['first_access'],
                last_access=data['last_access'],
                operation_types=list(data['operations']),
                total_read_size=data['total_size']
            )
            patterns.append(pattern)
        
        # Sort by access frequency
        patterns.sort(key=lambda p: p.access_count, reverse=True)
        return patterns
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get parsing statistics."""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset parsing statistics."""
        self.stats = {
            'files_parsed': 0,
            'messages_parsed': 0,
            'errors_encountered': 0,
            'parse_time_seconds': 0.0
        }