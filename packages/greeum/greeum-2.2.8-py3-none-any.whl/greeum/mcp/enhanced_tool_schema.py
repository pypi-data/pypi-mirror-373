#!/usr/bin/env python3
"""
Enhanced MCP Tool Schema for Greeum v2.0.5
- Provides improved tool descriptions with usage guidelines
- Includes context hints and best practices for LLM autonomous usage
- Maintains backward compatibility with existing MCP infrastructure
"""

from typing import Dict, List, Any

class EnhancedToolSchema:
    """Enhanced MCP tool schema with comprehensive usage guidance"""
    
    @staticmethod
    def get_add_memory_schema() -> Dict[str, Any]:
        """Enhanced schema for add_memory tool with detailed usage guidance"""
        return {
            "name": "add_memory",
            "description": """🧠 Add important permanent memories to long-term storage.
            
⚠️  USAGE GUIDELINES:
• ALWAYS search_memory first to avoid duplicates
• Store meaningful information, not casual conversation
• Use appropriate importance levels (see guide below)

✅ GOOD USES: user preferences, project details, decisions, recurring issues
❌ AVOID: greetings, weather, current time, temporary session info

🔍 WORKFLOW: search_memory → analyze results → add_memory (if truly new)""",
            
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Memory content (be specific and meaningful, min 10 chars)",
                        "minLength": 10
                    },
                    "importance": {
                        "type": "number",
                        "description": """Importance score guide:
• 0.9-1.0: Critical (deadlines, security, core requirements)  
• 0.7-0.8: High (preferences, key decisions, project specs)
• 0.5-0.6: Medium (general facts, useful context)
• 0.3-0.4: Low (minor details, temporary notes)""",
                        "default": 0.5,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["content"]
            },
            
            # Enhanced metadata for LLM guidance
            "usage_hints": {
                "when_to_use": [
                    "User shares personal preferences",
                    "Important project information revealed", 
                    "Key decisions made",
                    "Recurring problems identified",
                    "Solutions that worked well"
                ],
                "when_not_to_use": [
                    "Simple greetings or pleasantries",
                    "Current weather or time information",
                    "Temporary session-specific info",
                    "Information already stored (check first!)"
                ],
                "best_practices": [
                    "Search before storing to prevent duplicates",
                    "Use descriptive, searchable content",
                    "Set importance based on long-term value",
                    "Include context for future reference"
                ]
            }
        }
    
    @staticmethod
    def get_search_memory_schema() -> Dict[str, Any]:
        """Enhanced schema for search_memory tool"""
        return {
            "name": "search_memory",
            "description": """🔍 Search existing memories using keywords or semantic similarity.
            
⚠️  ALWAYS USE THIS FIRST before add_memory to avoid duplicates!

✅ USE WHEN:
• User mentions 'before', 'previous', 'remember'
• Starting new conversation (check user context)
• User asks about past discussions or projects
• Before storing new information (duplicate check)

🎯 SEARCH TIPS: Use specific keywords, try multiple terms if needed""",
            
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (use specific keywords related to the topic)",
                        "minLength": 2
                    },
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum results (5-10 recommended for performance)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["query"]
            },
            
            "usage_hints": {
                "search_strategies": [
                    "Use specific keywords from user's query",
                    "Try broader terms if specific search fails",
                    "Search for person names, project names specifically",
                    "Include both current and related topics"
                ],
                "result_handling": [
                    "Review all results for relevance",
                    "Reference found memories in your response",
                    "Note if memories seem outdated or incomplete"
                ]
            }
        }
    
    @staticmethod
    def get_stm_add_schema() -> Dict[str, Any]:
        """Enhanced schema for stm_add tool (short-term memory)"""
        return {
            "name": "stm_add", 
            "description": """🕒 Add content to short-term memory with automatic expiry.
            
USE FOR: Current session context, temporary notes, work-in-progress details

⚖️  STM vs LTM Decision:
• STM: Session-specific, temporary, will expire
• LTM: Permanent, important for future sessions

🔄 WORKFLOW: Use during session → stm_promote at end → stm_cleanup""",
            
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Temporary content for current session"
                    },
                    "ttl": {
                        "type": "string",
                        "description": "Time to live: 30m, 1h, 2h, 1d (default: 1h)",
                        "default": "1h"
                    },
                    "importance": {
                        "type": "number",
                        "description": "Importance for STM (typically 0.3-0.5)",
                        "default": 0.3,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["content"]
            }
        }
    
    @staticmethod
    def get_ltm_analyze_schema() -> Dict[str, Any]:
        """Enhanced schema for ltm_analyze tool"""
        return {
            "name": "ltm_analyze",
            "description": """📊 Analyze long-term memory patterns and trends.
            
USE PERIODICALLY to:
• Understand memory usage patterns
• Identify optimization opportunities  
• Check memory system health
• Generate insights about stored information

🎯 GREAT FOR: Memory system maintenance and optimization""",
            
            "inputSchema": {
                "type": "object",
                "properties": {
                    "trends": {
                        "type": "boolean",
                        "description": "Enable trend analysis over time",
                        "default": True
                    },
                    "period": {
                        "type": "string", 
                        "description": "Analysis period: 1w, 1m, 3m, 6m, 1y",
                        "default": "6m"
                    },
                    "output": {
                        "type": "string",
                        "description": "Output format for results",
                        "enum": ["text", "json"],
                        "default": "text"
                    }
                }
            }
        }
    
    @staticmethod
    def get_get_memory_stats_schema() -> Dict[str, Any]:
        """Enhanced schema for get_memory_stats tool"""
        return {
            "name": "get_memory_stats",
            "description": """📊 Get current memory system statistics and health status.
            
USE WHEN:
• Starting new conversations (check user context)
• Memory system seems slow or full
• Debugging memory-related issues
• Regular health checks

💡 PROVIDES: File counts, sizes, system status""",
            
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    @staticmethod
    def get_stm_promote_schema() -> Dict[str, Any]:
        """Enhanced schema for stm_promote tool"""
        return {
            "name": "stm_promote",
            "description": """🔝 Promote important short-term memories to long-term storage.
            
USE AT SESSION END:
• Review temporary memories for permanent value
• Promote important discoveries or solutions
• Clean up session-specific information

⚠️  Always use dry_run=true first to review candidates""",
            
            "inputSchema": {
                "type": "object",
                "properties": {
                    "threshold": {
                        "type": "number",
                        "description": "Importance threshold for promotion (0.8 recommended)",
                        "default": 0.8,
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Preview promotions without executing (recommended first)",
                        "default": False
                    }
                }
            }
        }
    
    @staticmethod
    def get_stm_cleanup_schema() -> Dict[str, Any]:
        """Enhanced schema for stm_cleanup tool"""
        return {
            "name": "stm_cleanup",
            "description": """🧹 Clean up short-term memory entries.
            
USE FOR MAINTENANCE:
• Remove expired entries
• Clear low-importance temporary data
• Optimize memory system performance

🔄 RECOMMENDED: Use after stm_promote at session end""",
            
            "inputSchema": {
                "type": "object",
                "properties": {
                    "smart": {
                        "type": "boolean",
                        "description": "Use intelligent cleanup (preserves important items)",
                        "default": False
                    },
                    "expired": {
                        "type": "boolean", 
                        "description": "Remove only expired entries (safest option)",
                        "default": False
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Remove items below this importance level",
                        "default": 0.2,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                }
            }
        }
    
    @staticmethod
    def get_ltm_verify_schema() -> Dict[str, Any]:
        """Enhanced schema for ltm_verify tool"""
        return {
            "name": "ltm_verify",
            "description": """🔍 Verify blockchain-like LTM integrity and detect issues.
            
USE FOR MAINTENANCE:
• Check memory system integrity
• Detect corruption or inconsistencies
• Validate blockchain-like structure

⚠️  Set repair=true only if issues detected""",
            
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repair": {
                        "type": "boolean",
                        "description": "Attempt to repair detected issues (use carefully)",
                        "default": False
                    }
                }
            }
        }
    
    @staticmethod
    def get_ltm_export_schema() -> Dict[str, Any]:
        """Enhanced schema for ltm_export tool"""
        return {
            "name": "ltm_export",
            "description": """📤 Export long-term memory data in various formats.
            
USE FOR:
• Creating backups of memory data
• Analyzing memory content externally
• Migrating to other systems
• Data portability and transparency""",
            
            "inputSchema": {
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "Export format type",
                        "enum": ["json", "blockchain", "csv"],
                        "default": "json"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Limit number of exported blocks",
                        "minimum": 1,
                        "maximum": 1000
                    }
                }
            }
        }
    
    @staticmethod
    def get_usage_analytics_schema() -> Dict[str, Any]:
        """Enhanced schema for usage_analytics tool"""
        return {
            "name": "usage_analytics",
            "description": """📊 Get comprehensive usage analytics and insights.
            
USE FOR:
• Understanding memory usage patterns
• Identifying performance bottlenecks
• Analyzing user behavior trends
• System health monitoring

💡 PROVIDES: Usage statistics, quality trends, performance insights""",
            
            "inputSchema": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Analysis period in days (1-90)",
                        "default": 7,
                        "minimum": 1,
                        "maximum": 90
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Type of analytics report",
                        "enum": ["usage", "quality", "performance", "all"],
                        "default": "usage"
                    }
                }
            }
        }
    
    @classmethod
    def get_all_enhanced_schemas(cls) -> List[Dict[str, Any]]:
        """Get enhanced tool schemas for MCP server integration (안전한 도구만)"""
        return [
            cls.get_add_memory_schema(),
            cls.get_search_memory_schema(),
            cls.get_get_memory_stats_schema(),
            cls.get_usage_analytics_schema()
            # 제거됨: ltm_analyze, ltm_verify, ltm_export, stm_add, stm_promote, stm_cleanup
            # 안전성과 보안상의 이유로 위험한 6개 도구는 MCP에서 제거됨
        ]
    
    @classmethod
    def get_tool_schema_by_name(cls, tool_name: str) -> Dict[str, Any]:
        """Get specific tool schema by name"""
        schema_methods = {
            "add_memory": cls.get_add_memory_schema,
            "search_memory": cls.get_search_memory_schema,
            "get_memory_stats": cls.get_get_memory_stats_schema,
            "usage_analytics": cls.get_usage_analytics_schema,
            "ltm_analyze": cls.get_ltm_analyze_schema,
            "ltm_verify": cls.get_ltm_verify_schema,
            "ltm_export": cls.get_ltm_export_schema,
            "stm_add": cls.get_stm_add_schema,
            "stm_promote": cls.get_stm_promote_schema,
            "stm_cleanup": cls.get_stm_cleanup_schema
        }
        
        if tool_name in schema_methods:
            return schema_methods[tool_name]()
        else:
            raise ValueError(f"Unknown tool name: {tool_name}")

if __name__ == "__main__":
    # Test schema generation
    schemas = EnhancedToolSchema.get_all_enhanced_schemas()
    
    # Debug 정보는 stderr로 출력하거나 로거 사용
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Generated {len(schemas)} enhanced tool schemas")
    
    # Sample schema 정보도 로깅으로 변경
    logger.debug("Sample add_memory schema loaded")