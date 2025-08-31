"""MCP Recommender Server Implementation."""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("MCP Recommender")

class MCPRecommender:
    def __init__(self):
        self.mcps: List[Dict] = []
        self.functional_keywords: Dict[str, List[str]] = {}
        self.load_data()
    
    def load_data(self):
        """Load MCP database and functional keywords."""
        try:
            # Load MCP database
            data_dir = Path(__file__).parent / "data"
            
            # Load functional keywords
            keywords_path = data_dir / "functional_keywords.json"
            if keywords_path.exists():
                with open(keywords_path, 'r', encoding='utf-8') as f:
                    self.functional_keywords = json.load(f)
            
            # Load MCP database
            db_path = data_dir / "mcp_database.json"
            if db_path.exists():
                with open(db_path, 'r', encoding='utf-8') as f:
                    self.mcps = json.load(f)
            else:
                # Fallback: create sample data for testing
                self.mcps = self.create_sample_data()
                
        except Exception as e:
            print(f"Error loading data: {e}")
            self.mcps = self.create_sample_data()
    
    def create_sample_data(self) -> List[Dict]:
        """Create sample MCP data for testing purposes."""
        return [
            {
                "category": "Databases",
                "name": "modelcontextprotocol/server-sqlite",
                "github_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite",
                "short_description": "SQLite database operations with built-in analysis features",
                "detailed_description": "This server provides a secure and efficient way to interact with local SQLite databases. It supports schema inspection, read/write queries, and includes advanced tools for data analysis and visualization directly within your MCP client."
            },
            {
                "category": "Web Services",
                "name": "sxhxliang/mcp-access-point",
                "github_url": "https://github.com/sxhxliang/mcp-access-point",
                "short_description": "Turn a web service into an MCP server in one click without making any code changes",
                "detailed_description": "MCP Access Point allows you to quickly convert any web API into an MCP server without modifying existing code. Perfect for integrating third-party services into your MCP workflow."
            },
            {
                "category": "File Systems",
                "name": "modelcontextprotocol/server-filesystem",
                "github_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
                "short_description": "Secure file system operations for local development",
                "detailed_description": "Provides secure access to local file systems with read/write capabilities, directory traversal, and file management operations. Includes safety features to prevent unauthorized access."
            }
        ]
    
    def expand_query_with_keywords(self, query: str) -> List[str]:
        """Expand user query with functional keywords."""
        query_lower = query.lower()
        expanded_terms = [query_lower]
        
        # Add original query terms
        query_terms = re.findall(r'\w+', query_lower)
        expanded_terms.extend(query_terms)
        
        # Check functional keywords mapping
        for function, keywords in self.functional_keywords.items():
            if any(term in query_lower for term in keywords):
                expanded_terms.extend(keywords)
        
        return list(set(expanded_terms))  # Remove duplicates
    
    def calculate_relevance_score(self, mcp: Dict, search_terms: List[str]) -> int:
        """Calculate relevance score for an MCP based on search terms."""
        score = 0
        
        # Combine all searchable text
        searchable_text = f"{mcp['name']} {mcp['short_description']} {mcp['detailed_description']} {mcp['category']}".lower()
        
        for term in search_terms:
            term_lower = term.lower()
            
            # Name matches get highest score
            if term_lower in mcp['name'].lower():
                score += 10
            
            # Category matches get high score
            if term_lower in mcp['category'].lower():
                score += 8
            
            # Short description matches get medium score
            if term_lower in mcp['short_description'].lower():
                score += 5
            
            # Detailed description matches get lower score
            if term_lower in mcp['detailed_description'].lower():
                score += 2
            
            # Exact phrase matches in any field get bonus
            if term_lower in searchable_text:
                score += 1
        
        return score
    
    def filter_mcps(self, category: Optional[str] = None, language: Optional[str] = None) -> List[Dict]:
        """Filter MCPs based on category and language."""
        filtered = self.mcps
        
        if category:
            filtered = [mcp for mcp in filtered if category.lower() in mcp['category'].lower()]
        
        if language:
            # Filter by language mentioned in description or name
            filtered = [mcp for mcp in filtered 
                       if language.lower() in f"{mcp['name']} {mcp['short_description']} {mcp['detailed_description']}".lower()]
        
        return filtered
    
    def search_mcps(self, query: str, limit: int = 5, category: Optional[str] = None, language: Optional[str] = None) -> List[Tuple[Dict, int]]:
        """Search for MCPs based on query and return scored results."""
        # Filter MCPs first
        filtered_mcps = self.filter_mcps(category, language)
        
        # Expand query with functional keywords
        search_terms = self.expand_query_with_keywords(query)
        
        # Calculate scores for each MCP
        scored_mcps = []
        for mcp in filtered_mcps:
            score = self.calculate_relevance_score(mcp, search_terms)
            if score > 0:  # Only include MCPs with some relevance
                scored_mcps.append((mcp, score))
        
        # Sort by score (descending) and limit results
        scored_mcps.sort(key=lambda x: x[1], reverse=True)
        return scored_mcps[:limit]
    
    def format_recommendations(self, scored_mcps: List[Tuple[Dict, int]], query: str) -> str:
        """Format search results as Markdown."""
        if not scored_mcps:
            return f"### No MCP recommendations found for '{query}'\n\nTry using different keywords or check the available categories."
        
        result = f"### Top {len(scored_mcps)} MCP Recommendations for '{query}':\n\n"
        
        for i, (mcp, score) in enumerate(scored_mcps, 1):
            result += f"**{i}. {mcp['name']}**\n"
            result += f"* **Category:** {mcp['category']}\n"
            result += f"* **Description:** {mcp['short_description']}\n"
            result += f"* **GitHub:** [{mcp['github_url']}]({mcp['github_url']})\n"
            result += f"* **Relevance Score:** {score}\n"
            
            # Add detailed description if available and different from short
            if mcp['detailed_description'] and mcp['detailed_description'] != mcp['short_description']:
                # Truncate long descriptions
                detailed = mcp['detailed_description'][:200]
                if len(mcp['detailed_description']) > 200:
                    detailed += "..."
                result += f"* **Details:** {detailed}\n"
            
            result += "\n"
        
        return result

# Initialize the recommender
recommender = MCPRecommender()

@mcp.tool()
def recommend_mcp(
    query: str,
    limit: int = 5,
    category: str = None,
    language: str = None
) -> str:
    """
    Recommend MCP servers based on your development needs.
    
    Args:
        query: Description of the functionality you need (e.g., "database operations", "web scraping", "file management")
        limit: Maximum number of recommendations to return (default: 5)
        category: Filter by specific category (optional)
        language: Filter by programming language (optional)
    
    Returns:
        Formatted markdown string with MCP recommendations
    """
    try:
        # Validate inputs
        if not query or not query.strip():
            return "### Error\nPlease provide a query describing what functionality you need."
        
        if limit < 1 or limit > 20:
            limit = 5
        
        # Search for recommendations
        scored_mcps = recommender.search_mcps(
            query=query.strip(),
            limit=limit,
            category=category,
            language=language
        )
        
        # Format and return results
        return recommender.format_recommendations(scored_mcps, query)
        
    except Exception as e:
        return f"### Error\nAn error occurred while searching for recommendations: {str(e)}"

@mcp.tool()
def list_categories() -> str:
    """
    List all available MCP categories.
    
    Returns:
        Formatted list of available categories
    """
    try:
        categories = set(mcp['category'] for mcp in recommender.mcps)
        categories_list = sorted(categories)
        
        result = "### Available MCP Categories:\n\n"
        for i, category in enumerate(categories_list, 1):
            # Count MCPs in each category
            count = sum(1 for mcp in recommender.mcps if mcp['category'] == category)
            result += f"{i}. **{category}** ({count} MCPs)\n"
        
        result += f"\n**Total:** {len(recommender.mcps)} MCPs across {len(categories_list)} categories"
        return result
        
    except Exception as e:
        return f"### Error\nAn error occurred while listing categories: {str(e)}"

@mcp.tool()
def get_functional_keywords() -> str:
    """
    Show available functional keyword mappings for better search results.
    
    Returns:
        Formatted list of functional keywords
    """
    try:
        if not recommender.functional_keywords:
            return "### No functional keywords available\nThe keyword mapping database is not loaded."
        
        result = "### Functional Keywords Mapping:\n\n"
        result += "Use these terms in your queries for better results:\n\n"
        
        for function, keywords in recommender.functional_keywords.items():
            result += f"**{function.title()}:**\n"
            result += f"  - Keywords: {', '.join(keywords[:8])}"  # Show first 8 keywords
            if len(keywords) > 8:
                result += f" (and {len(keywords) - 8} more)"
            result += "\n\n"
        
        return result
        
    except Exception as e:
        return f"### Error\nAn error occurred while retrieving keywords: {str(e)}"

def create_server():
    """Create and return the MCP server instance."""
    return mcp