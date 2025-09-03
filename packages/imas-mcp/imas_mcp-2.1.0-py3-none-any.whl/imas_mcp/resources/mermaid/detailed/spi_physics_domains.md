```mermaid
flowchart LR
    root["spi"]

    d1["Other<br/>(90 paths)"]
    root --> d1
    p1_1["injector"]
    d1 --> p1_1
    class p1_1 pathNode
    p1_2["name"]
    d1 --> p1_2
    class p1_2 pathNode
    p1_3["description"]
    d1 --> p1_3
    class p1_3 pathNode
    p1_4["optical_pellet_di..."]
    d1 --> p1_4
    class p1_4 pathNode
    p1_5["position"]
    d1 --> p1_5
    class p1_5 pathNode
    p1_6["r"]
    d1 --> p1_6
    class p1_6 pathNode
    more1["...and 84 more paths"]
    d1 --> more1
    class more1 moreNode
    class d1 domainNode
    d2["Temporal Evolution<br/>(15 paths)"]
    root --> d2
    p2_1["r"]
    d2 --> p2_1
    class p2_1 pathNode
    p2_2["phi"]
    d2 --> p2_2
    class p2_2 pathNode
    p2_3["z"]
    d2 --> p2_3
    class p2_3 pathNode
    p2_4["velocity_r"]
    d2 --> p2_4
    class p2_4 pathNode
    p2_5["velocity_z"]
    d2 --> p2_5
    class p2_5 pathNode
    p2_6["velocity_phi"]
    d2 --> p2_6
    class p2_6 pathNode
    more2["...and 9 more paths"]
    d2 --> more2
    class more2 moreNode
    class d2 domainNode

    classDef domainNode fill:#e8f5e8,stroke:#4caf50
    classDef pathNode fill:#fff8e1,stroke:#ff9800
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```