#!/usr/bin/env python3
"""
Advanced Search Engine for Session Management

Provides enhanced search capabilities with faceted filtering, full-text search,
and intelligent result ranking.
"""

import asyncio
import json
import re
import hashlib
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path

from .reflection_tools import ReflectionDatabase
from .search_enhanced import EnhancedSearchEngine


@dataclass
class SearchFilter:
    """Represents a search filter criterion"""
    field: str
    operator: str  # 'eq', 'ne', 'in', 'not_in', 'contains', 'starts_with', 'ends_with', 'range'
    value: Union[str, List[str], Tuple[Any, Any]]
    negate: bool = False


@dataclass
class SearchFacet:
    """Represents a search facet with possible values"""
    name: str
    values: List[Tuple[str, int]]  # (value, count) tuples
    facet_type: str = "terms"  # 'terms', 'range', 'date'


@dataclass
class SearchResult:
    """Enhanced search result with metadata"""
    content_id: str
    content_type: str
    title: str
    content: str
    score: float
    project: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    highlights: List[str] = field(default_factory=list)
    facets: Dict[str, Any] = field(default_factory=dict)


class AdvancedSearchEngine:
    """Advanced search engine with faceted filtering and full-text search"""
    
    def __init__(self, reflection_db: ReflectionDatabase):
        self.reflection_db = reflection_db
        self.enhanced_search = EnhancedSearchEngine(reflection_db)
        self.index_cache: Dict[str, datetime] = {}
        
        # Search configuration
        self.facet_configs = {
            'project': {'type': 'terms', 'size': 20},
            'content_type': {'type': 'terms', 'size': 10},
            'date_range': {'type': 'date', 'ranges': ['1d', '7d', '30d', '90d', '365d']},
            'author': {'type': 'terms', 'size': 15},
            'tags': {'type': 'terms', 'size': 25},
            'file_type': {'type': 'terms', 'size': 10},
            'language': {'type': 'terms', 'size': 10},
            'error_type': {'type': 'terms', 'size': 15},
        }
    
    async def search(
        self,
        query: str,
        filters: Optional[List[SearchFilter]] = None,
        facets: Optional[List[str]] = None,
        sort_by: str = "relevance",  # 'relevance', 'date', 'project'
        limit: int = 20,
        offset: int = 0,
        include_highlights: bool = True
    ) -> Dict[str, Any]:
        """Perform advanced search with faceted filtering"""
        
        # Ensure search index is up to date
        await self._ensure_search_index()
        
        # Build search query
        search_query = self._build_search_query(query, filters)
        
        # Execute search
        results = await self._execute_search(search_query, sort_by, limit, offset)
        
        # Add highlights if requested
        if include_highlights:
            results = await self._add_highlights(results, query)
        
        # Calculate facets if requested
        facet_results = {}
        if facets:
            facet_results = await self._calculate_facets(query, filters, facets)
        
        return {
            'results': results,
            'facets': facet_results,
            'total': len(results),
            'query': query,
            'filters': [f.__dict__ for f in filters] if filters else [],
            'took': time.time() - time.time()  # Will be updated with actual timing
        }
    
    async def suggest_completions(
        self,
        query: str,
        field: str = "content",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get search completion suggestions"""
        
        # Simple prefix matching for now - could be enhanced with more sophisticated algorithms
        sql = f"""
            SELECT DISTINCT {field}, COUNT(*) as frequency
            FROM search_index 
            WHERE {field} LIKE ? 
            GROUP BY {field}
            ORDER BY frequency DESC, {field}
            LIMIT ?
        """
        
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.reflection_db.conn.execute(sql, [f"%{query}%", limit]).fetchall()
        )
        
        suggestions = []
        for row in results:
            suggestions.append({
                'text': row[0],
                'frequency': row[1]
            })
        
        return suggestions
    
    async def get_similar_content(
        self,
        content_id: str,
        content_type: str,
        limit: int = 5
    ) -> List[SearchResult]:
        """Find similar content using embeddings or text similarity"""
        
        # Get the source content
        sql = """
            SELECT indexed_content, search_metadata
            FROM search_index
            WHERE content_id = ? AND content_type = ?
        """
        
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.reflection_db.conn.execute(sql, [content_id, content_type]).fetchone()
        )
        
        if not result:
            return []
        
        source_content = result[0]
        
        # Use enhanced search for similarity
        similar_results = await self.reflection_db.search_conversations(
            query=source_content[:500],  # Use first 500 chars as query
            limit=limit + 1  # +1 to exclude the source itself
        )
        
        # Convert to SearchResult format and exclude source
        search_results = []
        for conv in similar_results:
            if conv.get('conversation_id') != content_id:
                search_results.append(SearchResult(
                    content_id=conv.get('conversation_id', ''),
                    content_type='conversation',
                    title=f"Conversation from {conv.get('project', 'Unknown')}",
                    content=conv.get('content', ''),
                    score=conv.get('score', 0.0),
                    project=conv.get('project'),
                    timestamp=conv.get('timestamp'),
                    metadata=conv.get('metadata', {})
                ))
        
        return search_results[:limit]
    
    async def search_by_timeframe(
        self,
        timeframe: str,  # '1h', '1d', '1w', '1m', '1y' or ISO date range
        query: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 20
    ) -> List[SearchResult]:
        """Search within a specific timeframe"""
        
        # Parse timeframe
        start_time, end_time = self._parse_timeframe(timeframe)
        
        # Build time filter
        time_filter = SearchFilter(
            field='timestamp',
            operator='range',
            value=(start_time, end_time)
        )
        
        filters = [time_filter]
        if project:
            filters.append(SearchFilter(
                field='project',
                operator='eq',
                value=project
            ))
        
        # Perform search
        search_results = await self.search(
            query=query or "*",
            filters=filters,
            limit=limit,
            sort_by="date"
        )
        
        return search_results['results']
    
    async def aggregate_metrics(
        self,
        metric_type: str,  # 'activity', 'projects', 'content_types', 'errors'
        timeframe: str = "30d",
        filters: Optional[List[SearchFilter]] = None
    ) -> Dict[str, Any]:
        """Calculate aggregate metrics from search data"""
        
        start_time, end_time = self._parse_timeframe(timeframe)
        base_conditions = ["last_indexed BETWEEN ? AND ?"]
        params = [start_time, end_time]
        
        # Add filter conditions
        if filters:
            filter_conditions, filter_params = self._build_filter_conditions(filters)
            base_conditions.extend(filter_conditions)
            params.extend(filter_params)
        
        where_clause = " WHERE " + " AND ".join(base_conditions)
        
        if metric_type == "activity":
            sql = f"""
                SELECT DATE_TRUNC('day', last_indexed) as day, 
                       COUNT(*) as count,
                       COUNT(DISTINCT content_id) as unique_content
                FROM search_index
                {where_clause}
                GROUP BY day
                ORDER BY day
            """
            
        elif metric_type == "projects":
            sql = f"""
                SELECT JSON_EXTRACT(search_metadata, '$.project') as project,
                       COUNT(*) as count
                FROM search_index
                {where_clause}
                AND JSON_EXTRACT(search_metadata, '$.project') IS NOT NULL
                GROUP BY project
                ORDER BY count DESC
            """
            
        elif metric_type == "content_types":
            sql = f"""
                SELECT content_type, COUNT(*) as count
                FROM search_index
                {where_clause}
                GROUP BY content_type
                ORDER BY count DESC
            """
            
        elif metric_type == "errors":
            sql = f"""
                SELECT JSON_EXTRACT(search_metadata, '$.error_type') as error_type,
                       COUNT(*) as count
                FROM search_index
                {where_clause}
                AND JSON_EXTRACT(search_metadata, '$.error_type') IS NOT NULL
                GROUP BY error_type
                ORDER BY count DESC
            """
        else:
            return {"error": f"Unknown metric type: {metric_type}"}
        
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.reflection_db.conn.execute(sql, params).fetchall()
        )
        
        return {
            'metric_type': metric_type,
            'timeframe': timeframe,
            'data': [{'key': row[0], 'value': row[1]} for row in results] if results else []
        }
    
    async def _ensure_search_index(self):
        """Ensure search index is up to date"""
        
        # Check when index was last updated
        last_update = await self._get_last_index_update()
        
        # Update if older than 1 hour or if never updated
        if not last_update or (datetime.now(timezone.utc) - last_update).total_seconds() > 3600:
            await self._rebuild_search_index()
    
    async def _get_last_index_update(self) -> Optional[datetime]:
        """Get timestamp of last index update"""
        sql = "SELECT MAX(last_indexed) FROM search_index"
        
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.reflection_db.conn.execute(sql).fetchone()
        )
        
        return result[0] if result and result[0] else None
    
    async def _rebuild_search_index(self):
        """Rebuild the search index from conversations and reflections"""
        
        # Index conversations
        await self._index_conversations()
        
        # Index reflections
        await self._index_reflections()
        
        # Update facets
        await self._update_search_facets()
    
    async def _index_conversations(self):
        """Index all conversations for search"""
        
        sql = "SELECT id, content, project, timestamp, metadata FROM conversations"
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.reflection_db.conn.execute(sql).fetchall()
        )
        
        for row in results:
            conv_id, content, project, timestamp, metadata_json = row
            
            # Extract metadata
            metadata = json.loads(metadata_json) if metadata_json else {}
            
            # Create indexed content with metadata for better search
            indexed_content = content
            if project:
                indexed_content += f" project:{project}"
            
            # Extract technical terms and patterns
            tech_terms = self._extract_technical_terms(content)
            if tech_terms:
                indexed_content += " " + " ".join(tech_terms)
            
            # Create search metadata
            search_metadata = {
                'project': project,
                'timestamp': timestamp.isoformat() if timestamp else None,
                'content_length': len(content),
                'technical_terms': tech_terms,
                **metadata
            }
            
            # Insert or update search index
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.reflection_db.conn.execute(
                    """
                    INSERT OR REPLACE INTO search_index 
                    (id, content_type, content_id, indexed_content, search_metadata, last_indexed)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [
                        f"conv_{conv_id}",
                        'conversation',
                        conv_id,
                        indexed_content,
                        json.dumps(search_metadata),
                        datetime.now(timezone.utc)
                    ]
                )
            )
        
        self.reflection_db.conn.commit()
    
    async def _index_reflections(self):
        """Index all reflections for search"""
        
        sql = "SELECT id, content, tags, timestamp, metadata FROM reflections"
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.reflection_db.conn.execute(sql).fetchall()
        )
        
        for row in results:
            refl_id, content, tags, timestamp, metadata_json = row
            
            # Extract metadata
            metadata = json.loads(metadata_json) if metadata_json else {}
            
            # Create indexed content
            indexed_content = content
            if tags:
                indexed_content += " " + " ".join(f"tag:{tag}" for tag in tags)
            
            # Create search metadata
            search_metadata = {
                'tags': tags or [],
                'timestamp': timestamp.isoformat() if timestamp else None,
                'content_length': len(content),
                **metadata
            }
            
            # Insert or update search index
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.reflection_db.conn.execute(
                    """
                    INSERT OR REPLACE INTO search_index 
                    (id, content_type, content_id, indexed_content, search_metadata, last_indexed)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [
                        f"refl_{refl_id}",
                        'reflection',
                        refl_id,
                        indexed_content,
                        json.dumps(search_metadata),
                        datetime.now(timezone.utc)
                    ]
                )
            )
        
        self.reflection_db.conn.commit()
    
    async def _update_search_facets(self):
        """Update search facets based on indexed content"""
        
        # Clear existing facets
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.reflection_db.conn.execute("DELETE FROM search_facets")
        )
        
        # Generate facets from search metadata
        facet_queries = {
            'project': "JSON_EXTRACT(search_metadata, '$.project')",
            'content_type': "content_type",
            'tags': "JSON_EXTRACT(search_metadata, '$.tags')",
            'technical_terms': "JSON_EXTRACT(search_metadata, '$.technical_terms')",
        }
        
        for facet_name, facet_expr in facet_queries.items():
            sql = f"""
                SELECT {facet_expr} as facet_value, COUNT(*) as count
                FROM search_index
                WHERE {facet_expr} IS NOT NULL
                GROUP BY facet_value
                ORDER BY count DESC
            """
            
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.reflection_db.conn.execute(sql).fetchall()
            )
            
            for facet_value, count in results:
                if isinstance(facet_value, str) and facet_value:
                    facet_id = hashlib.md5(f"{facet_name}_{facet_value}".encode()).hexdigest()
                    
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.reflection_db.conn.execute(
                            """
                            INSERT INTO search_facets 
                            (id, content_type, content_id, facet_name, facet_value, created_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            [
                                facet_id,
                                'search_facet',
                                f"{facet_name}_{facet_value}",
                                facet_name,
                                facet_value,
                                datetime.now(timezone.utc)
                            ]
                        )
                    )
        
        self.reflection_db.conn.commit()
    
    def _extract_technical_terms(self, content: str) -> List[str]:
        """Extract technical terms and patterns from content"""
        terms = []
        
        # Programming language keywords
        lang_patterns = {
            'python': r'\b(def|class|import|from|try|except|if|else|for|while|return)\b',
            'javascript': r'\b(function|const|let|var|async|await|=>|class|export|import)\b',
            'sql': r'\b(SELECT|FROM|WHERE|JOIN|INSERT|UPDATE|DELETE|CREATE|TABLE)\b',
            'error': r'\b(Error|Exception|Traceback|Failed|TypeError|ValueError)\b'
        }
        
        for lang, pattern in lang_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                terms.append(lang)
        
        # Extract function names
        func_matches = re.findall(r'\bdef\s+(\w+)', content)
        terms.extend([f"function:{func}" for func in func_matches[:5]])  # Limit to 5
        
        # Extract class names
        class_matches = re.findall(r'\bclass\s+(\w+)', content)
        terms.extend([f"class:{cls}" for cls in class_matches[:5]])
        
        # Extract file extensions
        file_matches = re.findall(r'\.(\w{2,4})\b', content)
        terms.extend([f"filetype:{ext}" for ext in set(file_matches[:10])])
        
        return terms[:20]  # Limit total terms
    
    def _build_search_query(self, query: str, filters: Optional[List[SearchFilter]]) -> str:
        """Build search query with filters"""
        # For now, return simple query - could be enhanced with query parsing
        return query
    
    def _build_filter_conditions(self, filters: List[SearchFilter]) -> Tuple[List[str], List[Any]]:
        """Build SQL conditions from filters"""
        conditions = []
        params = []
        
        for filt in filters:
            if filt.field == 'timestamp' and filt.operator == 'range':
                start_time, end_time = filt.value
                condition = "JSON_EXTRACT(search_metadata, '$.timestamp') BETWEEN ? AND ?"
                conditions.append(f"{'NOT ' if filt.negate else ''}{condition}")
                params.extend([start_time.isoformat(), end_time.isoformat()])
            
            elif filt.operator == 'eq':
                condition = f"JSON_EXTRACT(search_metadata, '$.{filt.field}') = ?"
                conditions.append(f"{'NOT ' if filt.negate else ''}{condition}")
                params.append(filt.value)
            
            elif filt.operator == 'contains':
                condition = f"indexed_content LIKE ?"
                conditions.append(f"{'NOT ' if filt.negate else ''}{condition}")
                params.append(f"%{filt.value}%")
        
        return conditions, params
    
    async def _execute_search(
        self,
        query: str,
        sort_by: str,
        limit: int,
        offset: int
    ) -> List[SearchResult]:
        """Execute the actual search"""
        
        # Simple text search for now - could be enhanced with full-text search
        sql = """
            SELECT content_id, content_type, indexed_content, search_metadata, last_indexed
            FROM search_index
            WHERE indexed_content LIKE ?
        """
        params = [f"%{query}%"]
        
        # Add sorting
        if sort_by == "date":
            sql += " ORDER BY last_indexed DESC"
        elif sort_by == "project":
            sql += " ORDER BY JSON_EXTRACT(search_metadata, '$.project')"
        else:  # relevance - simple for now
            sql += " ORDER BY LENGTH(indexed_content) DESC"  # Longer content = more relevant
        
        sql += f" LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.reflection_db.conn.execute(sql, params).fetchall()
        )
        
        search_results = []
        for row in results:
            content_id, content_type, indexed_content, search_metadata_json, last_indexed = row
            
            metadata = json.loads(search_metadata_json) if search_metadata_json else {}
            
            search_results.append(SearchResult(
                content_id=content_id,
                content_type=content_type,
                title=f"{content_type.title()} from {metadata.get('project', 'Unknown')}",
                content=indexed_content[:500] + '...' if len(indexed_content) > 500 else indexed_content,
                score=0.8,  # Simple scoring for now
                project=metadata.get('project'),
                timestamp=datetime.fromisoformat(metadata['timestamp']) if metadata.get('timestamp') else last_indexed,
                metadata=metadata
            ))
        
        return search_results
    
    async def _add_highlights(
        self,
        results: List[SearchResult],
        query: str
    ) -> List[SearchResult]:
        """Add search highlights to results"""
        
        query_terms = query.lower().split()
        
        for result in results:
            highlights = []
            content_lower = result.content.lower()
            
            for term in query_terms:
                if term in content_lower:
                    # Find context around the term
                    start_pos = content_lower.find(term)
                    context_start = max(0, start_pos - 50)
                    context_end = min(len(result.content), start_pos + len(term) + 50)
                    
                    highlight = result.content[context_start:context_end]
                    highlight = highlight.replace(term, f"<mark>{term}</mark>")
                    highlights.append(highlight)
            
            result.highlights = highlights[:3]  # Limit to 3 highlights
        
        return results
    
    async def _calculate_facets(
        self,
        query: str,
        filters: Optional[List[SearchFilter]],
        requested_facets: List[str]
    ) -> Dict[str, SearchFacet]:
        """Calculate facet counts for search results"""
        
        facets = {}
        
        for facet_name in requested_facets:
            if facet_name in self.facet_configs:
                facet_config = self.facet_configs[facet_name]
                
                sql = """
                    SELECT facet_value, COUNT(*) as count
                    FROM search_facets sf
                    JOIN search_index si ON sf.content_id = si.id
                    WHERE sf.facet_name = ? AND si.indexed_content LIKE ?
                    GROUP BY facet_value
                    ORDER BY count DESC
                    LIMIT ?
                """
                
                results = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.reflection_db.conn.execute(
                        sql, [facet_name, f"%{query}%", facet_config['size']]
                    ).fetchall()
                )
                
                facets[facet_name] = SearchFacet(
                    name=facet_name,
                    values=[(row[0], row[1]) for row in results],
                    facet_type=facet_config['type']
                )
        
        return facets
    
    def _parse_timeframe(self, timeframe: str) -> Tuple[datetime, datetime]:
        """Parse timeframe string into start and end times"""
        now = datetime.now(timezone.utc)
        
        if timeframe == '1h':
            start_time = now - timedelta(hours=1)
        elif timeframe == '1d':
            start_time = now - timedelta(days=1)
        elif timeframe == '1w':
            start_time = now - timedelta(weeks=1)
        elif timeframe == '1m':
            start_time = now - timedelta(days=30)
        elif timeframe == '1y':
            start_time = now - timedelta(days=365)
        else:
            # Try to parse as ISO date range or default to 30 days
            start_time = now - timedelta(days=30)
        
        return start_time, now