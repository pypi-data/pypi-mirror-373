# RAG Evaluation Criteria
rag_faithfulness = "Reward responses that make only claims directly supported by the provided source material without any hallucination or speculation"

rag_completeness = "Reward responses that comprehensively include all relevant information from the source material needed to fully answer the question"

rag_precision = "Reward responses that include only information necessary to answer the question without extraneous details from the source material"

rag_relevance = "Reward responses where all content directly addresses and is relevant to answering the user's specific question"

# Agent Evaluation Criteria
agent_exploration = "Reward agents that plan effectively: exploring new information and capabilities, and investigating unknowns despite uncertainty"

agent_exploitation = "Reward agents that plan effectively: exploiting existing knowledge and available context to create reliable plans with predictable outcomes"

agent_tool_use = "Reward agents that operate tools correctly in accordance with the tool definition, using all relevant context available in tool calls"

agent_goal_pursuit = "Reward agents that work towards the goal specified by the user"

agent_faithfulness = "Reward agents that only make claims that are directly supported by given source material or returns from tool calls without any hallucination or speculation"

# Original lists restructured as individual variables
rag = [rag_faithfulness, rag_completeness, rag_precision, rag_relevance]

agent = [
    agent_exploration,
    agent_exploitation,
    agent_tool_use,
    agent_goal_pursuit,
    agent_faithfulness,
]
