```mermaid
flowchart LR
    root["sawteeth"]

    d1["Other<br/>(44 paths)"]
    root --> d1
    p1_1["vacuum_toroidal_f..."]
    d1 --> p1_1
    class p1_1 pathNode
    p1_2["r0"]
    d1 --> p1_2
    class p1_2 pathNode
    p1_3["profiles_1d"]
    d1 --> p1_3
    class p1_3 pathNode
    p1_4["grid"]
    d1 --> p1_4
    class p1_4 pathNode
    p1_5["rho_tor_norm"]
    d1 --> p1_5
    class p1_5 pathNode
    p1_6["rho_tor"]
    d1 --> p1_6
    class p1_6 pathNode
    more1["...and 38 more paths"]
    d1 --> more1
    class more1 moreNode
    class d1 domainNode
    d2["Temporal Evolution<br/>(9 paths)"]
    root --> d2
    p2_1["b0"]
    d2 --> p2_1
    class p2_1 pathNode
    p2_2["crash_trigger"]
    d2 --> p2_2
    class p2_2 pathNode
    p2_3["magnetic_shear_q1"]
    d2 --> p2_3
    class p2_3 pathNode
    p2_4["rho_tor_norm_q1"]
    d2 --> p2_4
    class p2_4 pathNode
    p2_5["rho_tor_norm_inve..."]
    d2 --> p2_5
    class p2_5 pathNode
    p2_6["rho_tor_norm_mixing"]
    d2 --> p2_6
    class p2_6 pathNode
    more2["...and 3 more paths"]
    d2 --> more2
    class more2 moreNode
    class d2 domainNode

    classDef domainNode fill:#e8f5e8,stroke:#4caf50
    classDef pathNode fill:#fff8e1,stroke:#ff9800
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```