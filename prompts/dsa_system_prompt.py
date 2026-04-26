"""
DSA-focused system prompts for LLM.
Implements comprehensive mentoring behavior patterns.
"""
def get_dsa_system_prompt():
    """Return comprehensive DSA mentoring system prompt."""
    return """
You are a senior Data Structures and Algorithms mentor and competitive programming coach.

ROLE:
- Act as an expert DSA mentor with deep knowledge of algorithmic thinking
- Explain concepts clearly with practical examples
- Guide through problem-solving methodologies
- Analyze time/space complexity thoroughly
- Compare approaches (brute force vs optimized)
- Provide code samples in Python and JavaScript
- Identify patterns and related problems
- Maintain conversational history per session

BEHAVIOR:
1. CONCEPT EXPLANATION:
   - Define terms precisely
   - Explain with examples and diagrams (describe verbally)
   - Relate to real-world analogies
   - Highlight key properties and trade-offs

2. PROBLEM SOLVING:
   - Start with brute force approach
   - Identify inefficiencies
   - Explain optimization strategy
   - Provide step-by-step solution
   - Validate with examples

3. CODE IMPLEMENTATION:
   - Write clean, commented code
   - Python and JavaScript both preferred
   - Explain each section
   - Handle edge cases explicitly
   - Include test cases

4. COMPLEXITY ANALYSIS:
   - Time complexity: worst, average, best cases
   - Space complexity analysis
   - Big O notation explanation
   - Comparison with alternatives

5. FOLLOW-UP GUIDANCE:
   - Suggest similar problems
   - Recommend practice platforms
   - Propose variations to explore
   - Advise on common pitfalls

RESPONSE FORMAT:
[Concept] Brief explanation
[Approach] Step-by-step methodology
[Complexity] Time & space analysis with reasoning
[Code] Production-ready implementation
[Suggestions] Related problems and practice strategies

TONE:
- Encouraging but precise
- Patient with explanations
- Challenge when appropriate
- Professional and knowledgeable
"""

def get_problem_solving_template():
    """Template for structured problem-solving responses."""
    return {
        "concept": "",
        "approach": [],
        "complexity": {
            "time": "",
            "space": "",
            "analysis": ""
        },
        "code_samples": [],
        "edge_cases": [],
        "related_problems": [],
        "practice_suggestions": []
    }

def format_complexity_analysis(time_complexity: str, space_complexity: str, explanation: str):
    """Format complexity analysis for consistent presentation."""
    return f"""
Time Complexity: {time_complexity}
Space Complexity: {space_complexity}

Analysis:
{explanation}
    """

# Pre-defined DSA patterns and their explanations
DSA_PATTERNS = {
    "sliding_window": {
        "name": "Sliding Window",
        "use_cases": ["Subarray problems", "String manipulation", "Optimal subarray"],
        "complexity": "O(n) time, O(1) space",
        "key_insight": "Maintain a window that satisfies certain conditions"
    },
    "two_pointers": {
        "name": "Two Pointers",
        "use_cases": ["Sorted arrays", "Linked lists", "Pair problems"],
        "complexity": "O(n) time, O(1) space",
        "key_insight": "Use two indices to traverse data structure"
    },
    "binary_search": {
        "name": "Binary Search",
        "use_cases": ["Sorted data", "Search optimization", "Decision problems"],
        "complexity": "O(log n) time, O(1) space",
        "key_insight": "Divide and conquer on sorted data"
    },
    "dynamic_programming": {
        "name": "Dynamic Programming",
        "use_cases": ["Optimization problems", "Overlapping subproblems", "Memoization"],
        "complexity": "Varies: O(n^2) to O(2^n)",
        "key_insight": "Break down into overlapping subproblems"
    },
    "graph_traversal": {
        "name": "Graph Traversal",
        "use_cases": ["Network problems", "Path finding", "Connected components"],
        "complexity": "O(V + E) for BFS/DFS",
        "key_insight": "Systematically explore graph structure"
    }
}

# Common DSA concepts with explanations
DSA_CONCEPTS = {
    "array": {
        "definition": "Contiguous memory allocation for same-type elements",
        "complexities": {
            "access": "O(1)",
            "search": "O(n)",
            "insertion": "O(n)",
            "deletion": "O(n)"
        },
        "pros": ["Fast access", "Cache friendly"],
        "cons": ["Fixed size", "Costly insertions/deletions"]
    },
    "linked_list": {
        "definition": "Linear collection of nodes with pointers",
        "complexities": {
            "access": "O(n)",
            "search": "O(n)",
            "insertion": "O(1)",
            "deletion": "O(1)"
        },
        "pros": ["Dynamic size", "Easy insertions"],
        "cons": ["No random access", "Extra memory for pointers"]
    },
    "stack": {
        "definition": "LIFO (Last In First Out) data structure",
        "complexities": {
            "push": "O(1)",
            "pop": "O(1)",
            "peek": "O(1)"
        },
        "use_cases": ["Function calls", "Undo operations", "Expression evaluation"]
    },
    "queue": {
        "definition": "FIFO (First In First Out) data structure",
        "complexities": {
            "enqueue": "O(1)",
            "dequeue": "O(1)",
            "peek": "O(1)"
        },
        "use_cases": ["Order processing", "Breadth-first search", "Buffering"]
    },
    "binary_tree": {
        "definition": "Hierarchical structure with at most 2 children per node",
        "complexities": {
            "traversal": "O(n)",
            "search_bst": "O(log n) average",
            "insert_bst": "O(log n) average"
        },
        "types": ["Binary Search Tree", "AVL Tree", "Red-Black Tree"]
    },
    "graph": {
        "definition": "Vertices connected by edges",
        "representations": {
            "adjacency_list": "O(V + E) space",
            "adjacency_matrix": "O(V^2) space"
        },
        "traversals": ["BFS", "DFS"],
        "algorithms": ["Dijkstra", "Bellman-Ford", "Floyd-Warshall"]
    }
}