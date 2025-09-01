#!/usr/bin/env python3
"""
기본 MCP 어댑터 인터페이스
- 모든 환경별 어댑터의 공통 인터페이스 정의
- Greeum 컴포넌트 통합 초기화
- 기존 도구 API 완전 호환성 보장
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

# Greeum 핵심 컴포넌트
try:
    from greeum.core.block_manager import BlockManager
    from greeum.core.database_manager import DatabaseManager  
    from greeum.core.stm_manager import STMManager
    from greeum.core.duplicate_detector import DuplicateDetector
    from greeum.core.quality_validator import QualityValidator
    from greeum.core.usage_analytics import UsageAnalytics
    GREEUM_AVAILABLE = True
except ImportError:
    GREEUM_AVAILABLE = False

logger = logging.getLogger(__name__)

class BaseAdapter(ABC):
    """모든 MCP 어댑터의 기본 인터페이스"""
    
    def __init__(self):
        self.components = None
        self.initialized = False
        
    def initialize_greeum_components(self) -> Optional[Dict[str, Any]]:
        """Greeum 핵심 컴포넌트 통합 초기화"""
        if self.components is not None:
            return self.components
            
        if not GREEUM_AVAILABLE:
            logger.error("❌ Greeum components not available")
            return None
            
        try:
            # 핵심 컴포넌트들 초기화
            db_manager = DatabaseManager()
            block_manager = BlockManager(db_manager)
            stm_manager = STMManager(db_manager)
            duplicate_detector = DuplicateDetector(db_manager)
            quality_validator = QualityValidator()
            usage_analytics = UsageAnalytics(db_manager)
            
            self.components = {
                'db_manager': db_manager,
                'block_manager': block_manager,
                'stm_manager': stm_manager,
                'duplicate_detector': duplicate_detector,
                'quality_validator': quality_validator,
                'usage_analytics': usage_analytics
            }
            
            self.initialized = True
            logger.info("✅ Greeum components initialized successfully")
            return self.components
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Greeum components: {e}")
            return None
    
    # 공통 도구 구현 (모든 어댑터에서 동일)
    def add_memory_tool(self, content: str, importance: float = 0.5) -> str:
        """메모리 추가 도구 - 기존 API 완전 호환"""
        if not self.components:
            self.initialize_greeum_components()
        if not self.components:
            return "❌ Greeum components not available"
            
        try:
            # 기존 fastmcp_hotfix_server의 로직 재사용
            from ..fastmcp_hotfix_server import add_memory_direct
            
            # 중복 검사
            duplicate_check = self.components['duplicate_detector'].check_duplicate(content)
            if duplicate_check["is_duplicate"]:
                similarity = duplicate_check["similarity_score"]
                return f"""⚠️  **Potential Duplicate Memory Detected**

**Similarity**: {similarity:.1%} with existing memory
**Similar Memory**: Block #{duplicate_check['similar_block_index']}

Please search existing memories first or provide more specific content."""
            
            # 품질 검증
            quality_result = self.components['quality_validator'].validate_memory_quality(content, importance)
            
            # 메모리 추가
            block_data = add_memory_direct(content, importance)
            
            # 사용 통계 로깅
            self.components['usage_analytics'].log_quality_metrics(
                len(content), quality_result['quality_score'], quality_result['quality_level'],
                importance, importance, False, duplicate_check["similarity_score"], 
                len(quality_result.get('suggestions', []))
            )
            
            # 성공 응답
            quality_feedback = f"""
**Quality Score**: {quality_result['quality_score']:.1%} ({quality_result['quality_level']})
**Adjusted Importance**: {importance:.2f} (original: {importance:.2f})"""
            
            suggestions_text = ""
            if quality_result.get('suggestions'):
                suggestions_text = f"\n\n💡 **Quality Suggestions**:\n" + "\n".join(f"• {s}" for s in quality_result['suggestions'][:2])
            
            return f"""✅ **Memory Successfully Added!**

**Block Index**: #{block_data['block_index']}
**Storage**: Permanent (Long-term Memory)
**Duplicate Check**: ✅ Passed{quality_feedback}{suggestions_text}"""
            
        except Exception as e:
            logger.error(f"add_memory failed: {e}")
            return f"❌ Failed to add memory: {str(e)}"
    
    def search_memory_tool(self, query: str, limit: int = 5) -> str:
        """메모리 검색 도구 - 기존 API 완전 호환"""
        if not self.components:
            self.initialize_greeum_components()
        if not self.components:
            return "❌ Greeum components not available"
            
        try:
            from ..fastmcp_hotfix_server import search_memory_direct
            results = search_memory_direct(query, limit)
            
            # 사용 통계 로깅
            self.components['usage_analytics'].log_event(
                "tool_usage", "search_memory",
                {"query_length": len(query), "results_found": len(results), "limit_requested": limit},
                0, True
            )
            
            if results:
                result_text = f"🔍 Found {len(results)} memories:\n"
                for i, memory in enumerate(results, 1):
                    timestamp = memory.get('timestamp', 'Unknown')
                    content = memory.get('context', '')[:100] + ('...' if len(memory.get('context', '')) > 100 else '')
                    result_text += f"{i}. [{timestamp}] {content}\n"
                return result_text
            else:
                return f"🔍 No memories found for query: '{query}'"
                
        except Exception as e:
            logger.error(f"search_memory failed: {e}")
            return f"❌ Search failed: {str(e)}"
    
    def get_memory_stats_tool(self) -> str:
        """메모리 통계 도구 - 기존 API 완전 호환"""
        if not self.components:
            self.initialize_greeum_components()
        if not self.components:
            return "❌ Greeum components not available"
            
        try:
            db_manager = self.components['db_manager']
            stm_manager = self.components['stm_manager']
            
            # 기본 통계
            total_blocks = db_manager.count_blocks()
            recent_blocks = db_manager.get_recent_blocks(limit=10)
            stm_stats = stm_manager.get_stats()
            
            return f"""📊 **Greeum Memory Statistics**

**Long-term Memory**:
• Total Blocks: {total_blocks}
• Recent Entries: {len(recent_blocks)}

**Short-term Memory**:
• Active Slots: {stm_stats.get('active_count', 0)}
• Available Slots: {stm_stats.get('available_slots', 0)}

**System Status**: ✅ Operational
**Version**: 2.2.7 (Unified MCP Server)"""
            
        except Exception as e:
            logger.error(f"get_memory_stats failed: {e}")
            return f"❌ Stats retrieval failed: {str(e)}"
    
    def usage_analytics_tool(self, days: int = 7, report_type: str = "usage") -> str:
        """사용 분석 도구 - 기존 API 완전 호환"""
        if not self.components:
            self.initialize_greeum_components()
        if not self.components:
            return "❌ Greeum components not available"
            
        try:
            analytics = self.components['usage_analytics'].get_usage_report(days=days, report_type=report_type)
            
            return f"""📈 **Usage Analytics Report** ({days} days)

**Activity Summary**:
• Total Operations: {analytics.get('total_operations', 0)}
• Memory Additions: {analytics.get('add_operations', 0)}
• Search Operations: {analytics.get('search_operations', 0)}

**Quality Metrics**:
• Average Quality Score: {analytics.get('avg_quality_score', 0):.1%}
• High Quality Rate: {analytics.get('high_quality_rate', 0):.1%}

**Performance**:
• Average Response Time: {analytics.get('avg_response_time', 0):.1f}ms
• Success Rate: {analytics.get('success_rate', 0):.1%}

**Report Type**: {report_type.title()}
**Generated**: Unified MCP v2.2.7"""
            
        except Exception as e:
            logger.error(f"usage_analytics failed: {e}")
            return f"❌ Analytics failed: {str(e)}"
    
    @abstractmethod
    async def run(self):
        """서버 실행 (각 어댑터에서 구현)"""
        pass