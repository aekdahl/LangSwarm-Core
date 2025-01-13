# Extending GlobalLogger for Agent Activity Logging

## **Overview**
This document describes how to extend the **GlobalLogger** in LangSwarm-Core to log agent activities, including:

1. **Questions and Answers (Q&A)**
2. **Tool Usage**
3. **Agent Spawning**
4. **Capability Usage**

These logs will be stored in a centralized database (e.g., ChromaDB) for internal use, enabling LangSwarm to track and analyze agent behavior and interactions.

---

## **Objectives**
1. Capture detailed logs for agent activities.
2. Ensure logs are structured and stored in a retrievable format.
3. Integrate with ChromaDB for centralized and queryable storage.
4. Provide extensibility for new activity types.

---

## **Steps to Extend GlobalLogger**

### **1. Update GlobalLogger for Activity-Specific Logging**

#### **Enhance the GlobalLogger Class**
Modify the `GlobalLogger` class to include methods for logging specific agent activities. Each method should:

- Accept relevant parameters for the activity type.
- Log the event using a unified schema.
- Store the event in ChromaDB.

```python
from chromadb.client import ChromaClient
from datetime import datetime

class GlobalLogger:
    _instance = None
    chroma_client = None

    @staticmethod
    def initialize(api_key=None, chroma_db_path="/data/chromadb"):
        if not GlobalLogger._instance:
            GlobalLogger._instance = GlobalLogger()
            if api_key:
                GlobalLogger._instance.api_key = api_key
            # Initialize ChromaDB client
            GlobalLogger._instance.chroma_client = ChromaClient(chroma_db_path)

    @staticmethod
    def log_activity(activity_type, agent_name, details, metadata=None):
        """
        Log agent activities and store in ChromaDB.

        :param activity_type: str - Type of activity (e.g., 'Q&A', 'tool_usage').
        :param agent_name: str - Name of the agent performing the activity.
        :param details: dict - Detailed information about the activity.
        :param metadata: dict - Additional metadata (optional).
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "activity_type": activity_type,
            "agent_name": agent_name,
            "details": details,
            "metadata": metadata or {}
        }

        # Store in ChromaDB
        if GlobalLogger._instance.chroma_client:
            GlobalLogger._instance._store_in_chromadb(log_entry)

        # Fallback: Print log for debugging
        print(f"[LOG] {log_entry}")

    def _store_in_chromadb(self, log_entry):
        """
        Store log entry in ChromaDB.

        :param log_entry: dict - The log entry to store.
        """
        collection = self.chroma_client.get_or_create_collection("agent_activities")
        collection.add(documents=[log_entry])
```

---

### **2. Logging Specific Activities**
Add methods for each activity type to ensure consistent usage.

#### **Q&A Logging**
```python
@staticmethod
def log_qa(agent_name, question, answer, metadata=None):
    GlobalLogger.log_activity(
        activity_type="Q&A",
        agent_name=agent_name,
        details={"question": question, "answer": answer},
        metadata=metadata
    )
```

#### **Tool Usage Logging**
```python
@staticmethod
def log_tool_usage(agent_name, tool_name, input_params, output, metadata=None):
    GlobalLogger.log_activity(
        activity_type="tool_usage",
        agent_name=agent_name,
        details={"tool_name": tool_name, "input_params": input_params, "output": output},
        metadata=metadata
    )
```

#### **Agent Spawning Logging**
```python
@staticmethod
def log_agent_spawn(parent_agent, child_agent, metadata=None):
    GlobalLogger.log_activity(
        activity_type="agent_spawn",
        agent_name=parent_agent,
        details={"spawned_agent": child_agent},
        metadata=metadata
    )
```

#### **Capability Usage Logging**
```python
@staticmethod
def log_capability_usage(agent_name, capability_name, input_params, output, metadata=None):
    GlobalLogger.log_activity(
        activity_type="capability_usage",
        agent_name=agent_name,
        details={"capability_name": capability_name, "input_params": input_params, "output": output},
        metadata=metadata
    )
```

---

### **3. Query Logs in ChromaDB**
Provide utility methods for querying logs from ChromaDB.

```python
@staticmethod
def query_logs(activity_type=None, agent_name=None, limit=10):
    """
    Query logs from ChromaDB.

    :param activity_type: str - Filter by activity type.
    :param agent_name: str - Filter by agent name.
    :param limit: int - Maximum number of logs to return.
    :return: List[dict] - Retrieved log entries.
    """
    collection = GlobalLogger._instance.chroma_client.get_collection("agent_activities")
    filters = {}

    if activity_type:
        filters["activity_type"] = activity_type
    if agent_name:
        filters["agent_name"] = agent_name

    results = collection.query(filter=filters, limit=limit)
    return results
```

---

### **4. Example Usage**

#### **Logging Activities**
```python
# Log Q&A
GlobalLogger.log_qa(
    agent_name="TestAgent",
    question="What is LangSwarm?",
    answer="LangSwarm is a multi-agent ecosystem.",
    metadata={"session_id": "abc123"}
)

# Log Tool Usage
GlobalLogger.log_tool_usage(
    agent_name="TestAgent",
    tool_name="search_tool",
    input_params={"query": "AI trends"},
    output="Top AI trends are...",
    metadata={"session_id": "abc123"}
)
```

#### **Querying Logs**
```python
# Query the last 5 Q&A logs
qa_logs = GlobalLogger.query_logs(activity_type="Q&A", limit=5)
print(qa_logs)

# Query all logs for a specific agent
agent_logs = GlobalLogger.query_logs(agent_name="TestAgent")
print(agent_logs)
```

---

## **Best Practices**

1. **Log Enrichment**:
   - Always include metadata like `session_id`, `timestamp`, or `execution_time` for deeper insights.

2. **Data Retention Policies**:
   - Define retention policies in ChromaDB to manage storage efficiently.

3. **Security and Privacy**:
   - Ensure sensitive data in logs (e.g., API keys) is redacted.

4. **Standardized Log Schema**:
   - Use a consistent schema for all log entries to simplify querying and analysis.

---

## **Next Steps**
1. Implement a dashboard for visualizing agent activity logs.
2. Extend logging to include error and performance metrics.
3. Integrate log querying into the LangSwarm SDK for ease of use.

For further assistance or contributions, visit the [LangSwarm GitHub Repository](https://github.com/aekdahl/LangSwarm-Core).

