RepoQ
Phase 1 
Start with a basic understanding of the Repo being pasted 

Example
Repository downloaded successfully.

Files:
143

Java:
87

XML:
21

YAML:
12

Markdown:
8

Other:
15




Phase 3 : 
AST chunking of code 

Phase 4:
Questioning based on the chunks , top k similar chunks are sent as output 

part B  Phase 4 
Send the relevant chunks to LLM (using qwen2.5 3b locally) and then the LLM will answer ,instead of just throwing out the chunks 

Phase 5 
Knowledge Graphs wala dekhna hoga ek baar 
ki how the similar chunks are connected 
can use Neo4j


Phase 6:
Phase 6 — LangGraph

Now introduce agents.

Don't create 12 agents. 

Start with three:

                  User
                   │
                   ▼
              Orchestrator
              /     |      \
             /      |       \
            ▼       ▼        ▼
        Search    Graph    Debug
         Agent    Agent    Agent
Search Agent

Qdrant.

Graph Agent

Neo4j.

Debug Agent

Combines both + LLM reasoning.

For example:

"Why could /users/{id} return 500?"


Phase 7: 
Multimodal shit 

ki with screenshots also it can do it 