"""
LangGraph-based agent for DSA problem solving.
Implements stateful conversation management with memory and context.
"""
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import uuid
import json

# Type definitions for state management
class ChatState(TypedDict):
    """Graph state for conversation management."""
    session_id: str
    messages: List[Dict[str, Any]]
    current_problem: Optional[str]
    current_topic: Optional[str]
    difficulty_level: str
    problem_history: List[str]
    response: Optional[str]
    complexity_analysis: Optional[Dict[str, str]]
    code_samples: List[Dict[str, str]]
    follow_up_suggestions: List[str]
    metadata: Dict[str, Any]

class DSAConversationAgent:
    """Manages stateful DSA conversations using LangGraph."""

    def __init__(self, llm_client, system_prompt):
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()

    def _create_workflow(self) -> StateGraph:
        """Create LangGraph workflow for DSA conversations."""
        workflow = StateGraph(ChatState)

        # Define nodes
        workflow.add_node("initializer", self._initialize_conversation)
        workflow.add_node("analyzer", self._analyze_problem)
        workflow.add_node("responder", self._generate_response)
        workflow.add_node("updater", self._update_state)

        # Define edges
        workflow.set_entry_point("initializer")
        workflow.add_edge("initializer", "analyzer")
        workflow.add_edge("analyzer", "responder")
        workflow.add_edge("responder", "updater")
        workflow.add_edge("updater", END)

        return workflow

    def _initialize_conversation(self, state: ChatState) -> ChatState:
        """Initialize or retrieve conversation state."""
        if not state.get("session_id"):
            state["session_id"] = str(uuid.uuid4())

        if not state.get("messages"):
            state["messages"] = [
                {"role": "system", "content": self.system_prompt}
            ]

        state["metadata"] = {
            "created_at": "now",
            "updated_at": "now",
            "status": "initialized"
        }

        return state

    def _analyze_problem(self, state: ChatState) -> ChatState:
        """Analyze current problem and determine appropriate strategy."""
        last_message = state["messages"][-1]
        if last_message["role"] != "user":
            return state

        content = last_message["content"]

        # Simple pattern detection (placeholder for actual analysis)
        state["current_problem"] = content
        state["difficulty_level"] = self._estimate_difficulty(content)
        state["current_topic"] = self._detect_topic(content)
        state["problem_history"].append(content)

        return state

    def _generate_response(self, state: ChatState) -> ChatState:
        """Generate response using LLM."""
        try:
            # Use the last user message
            user_message = state["messages"][-1]
            if user_message["role"] != "user":
                return state

            # Build messages for LLM
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in state["messages"]
            ]

            # Generate response (simplified - in reality would use streaming)
            # This is a placeholder for actual Azure OpenAI call
            response_content = self._simulate_llm_response(state)

            # Parse structured response
            response_data = self._parse_structured_response(response_content, state)

            state["response"] = response_data["text"]
            state["complexity_analysis"] = response_data.get("complexity")
            state["code_samples"] = response_data.get("code_samples", [])
            state["follow_up_suggestions"] = response_data.get("suggestions", [])

            # Add assistant message to history
            state["messages"].append({
                "role": "assistant",
                "content": response_data["text"]
            })

            state["metadata"]["last_response_at"] = "now"

        except Exception as e:
            state["response"] = f"Error generating response: {str(e)}"
            state["metadata"]["error"] = str(e)

        return state

    def _simulate_llm_response(self, state: ChatState) -> str:
        """Simulate LLM response for demonstration."""
        problem = state.get("current_problem", "general")

        if "binary search" in problem.lower():
            return """
Let me explain Binary Search, a fundamental algorithm for searching in sorted arrays.

**Concept:**
Binary Search is an efficient algorithm for finding an item in a sorted array.
It works by repeatedly dividing the search interval in half.

**Approach:**
1. Compare the target value with the middle element
2. If equal, we found the target
3. If target is smaller, search the left half
4. If target is larger, search the right half
5. Repeat until found or interval is empty

**Time Complexity:** O(log n)
**Space Complexity:** O(1) for iterative, O(log n) for recursive

**Python Implementation:**
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

**Suggestions:**
- Try implementing recursive binary search
- Practice with variations like finding first/last occurrence
- Explore problems like "Search in Rotated Sorted Array"
"""
        else:
            return f"""
I'd be happy to help you understand: {problem}

Let me break this down step by step:

1. First, let's understand the problem requirements
2. We'll identify the underlying data structure or algorithm pattern
3. I'll provide a conceptual explanation
4. We'll analyze time and space complexity
5. I'll provide code samples in Python and JavaScript

Would you like me to focus on a specific aspect of this topic?
"""

    def _parse_structured_response(self, response_text: str, state: ChatState) -> Dict:
        """Parse LLM response into structured format."""
        # In production, this would use structured output from LLM
        # For now, we'll parse heuristically

        return {
            "text": response_text,
            "complexity": {
                "time": self._extract_complexity(response_text, "time"),
                "space": self._extract_complexity(response_text, "space"),
                "analysis": self._extract_analysis(response_text)
            } if "Time Complexity" in response_text else None,
            "code_samples": self._extract_code_samples(response_text),
            "suggestions": self._extract_suggestions(response_text)
        }

    def _extract_complexity(self, text: str, complexity_type: str) -> str:
        """Extract complexity from response text."""
        import re

        pattern = r"Time Complexity: ([^\n]+)" if complexity_type == "time" else r"Space Complexity: ([^\n]+)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else "Not analyzed"

    def _extract_analysis(self, text: str) -> str:
        """Extract complexity analysis from response."""
        # Look for Analysis section
        if "Analysis:" in text:
            parts = text.split("Analysis:")
            if len(parts) > 1:
                return parts[1].strip()
        return ""

    def _extract_code_samples(self, text: str) -> List[Dict[str, str]]:
        """Extract code samples from response text."""
        import re

        samples = []
        code_blocks = re.findall(r'```(\w+)\n([\s\S]*?)```', text)

        for language, code in code_blocks:
            samples.append({
                "language": language,
                "code": code.strip(),
                "description": ""  # Could extract from preceding text
            })

        return samples

    def _extract_suggestions(self, text: str) -> List[str]:
        """Extract suggestions from response text."""
        suggestions = []
        lines = text.split("\n")

        for line in lines:
            if any(keyword in line.lower() for keyword in ["try", "practice", "suggest", "explore"]):
                suggestion = line.strip()
                if suggestion and suggestion != "Suggestions:":
                    suggestions.append(suggestion.lstrip("* ").strip())

        return suggestions

    def _update_state(self, state: ChatState) -> ChatState:
        """Update conversation state and metadata."""
        state["metadata"]["updated_at"] = "now"
        state["metadata"]["message_count"] = len(state["messages"])

        return state

    async def process_message(self, message: str, session_id: Optional[str] = None) -> Dict:
        """Process a new message and return structured response."""
        # Initialize state
        initial_state: ChatState = {
            "session_id": session_id or str(uuid.uuid4()),
            "messages": [],
            "current_problem": None,
            "current_topic": None,
            "difficulty_level": "intermediate",
            "problem_history": [],
            "response": None,
            "complexity_analysis": None,
            "code_samples": [],
            "follow_up_suggestions": [],
            "metadata": {}
        }

        # Add user message
        initial_state["messages"].append({
            "role": "user",
            "content": message
        })

        # Run workflow
        result = await self.app.ainvoke(initial_state)

        return {
            "session_id": result["session_id"],
            "response": result["response"],
            "complexity": result["complexity_analysis"],
            "code_samples": result["code_samples"],
            "suggestions": result["follow_up_suggestions"],
            "metadata": result["metadata"]
        }