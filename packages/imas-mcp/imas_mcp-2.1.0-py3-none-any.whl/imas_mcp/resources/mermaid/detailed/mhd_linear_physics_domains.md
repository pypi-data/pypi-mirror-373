```mermaid
flowchart LR
    root["mhd_linear"]

    d1["Other<br/>(207 paths)"]
    root --> d1
    p1_1["model_type"]
    d1 --> p1_1
    class p1_1 pathNode
    p1_2["name"]
    d1 --> p1_2
    class p1_2 pathNode
    p1_3["index"]
    d1 --> p1_3
    class p1_3 pathNode
    p1_4["description"]
    d1 --> p1_4
    class p1_4 pathNode
    p1_5["equations"]
    d1 --> p1_5
    class p1_5 pathNode
    p1_6["name"]
    d1 --> p1_6
    class p1_6 pathNode
    more1["...and 201 more paths"]
    d1 --> more1
    class more1 moreNode
    class d1 domainNode
    d2["Temporal Evolution<br/>(1 paths)"]
    root --> d2
    p2_1["b0"]
    d2 --> p2_1
    class p2_1 pathNode
    class d2 domainNode

    classDef domainNode fill:#e8f5e8,stroke:#4caf50
    classDef pathNode fill:#fff8e1,stroke:#ff9800
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```