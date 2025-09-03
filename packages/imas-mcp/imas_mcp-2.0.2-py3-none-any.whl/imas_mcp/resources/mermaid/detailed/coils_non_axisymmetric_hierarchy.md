```mermaid
flowchart TD
    root["coils_non_axisymmetric IDS"]

    n1[coils_non_axisymmetric]
    root --> n1
    class n1 normalNode
    n2(coil)
    n1 --> n2
    class n2 complexNode
    n3[name]
    n2 --> n3
    class n3 leafNode
    n4[description]
    n2 --> n4
    class n4 leafNode
    n5[identifier]
    n2 --> n5
    class n5 leafNode
    n6[conductor]
    n2 --> n6
    class n6 normalNode
    n7[elements]
    n6 --> n7
    class n7 normalNode
    n8[types]
    n7 --> n8
    class n8 leafNode
    n9[start_points]
    n7 --> n9
    class n9 normalNode
    n10[r]
    n9 --> n10
    class n10 leafNode
    n11[phi]
    n9 --> n11
    class n11 leafNode
    n12[z]
    n9 --> n12
    class n12 leafNode
    n13[intermediate_points]
    n7 --> n13
    class n13 normalNode
    n14[r]
    n13 --> n14
    class n14 leafNode
    n15[phi]
    n13 --> n15
    class n15 leafNode
    n16[z]
    n13 --> n16
    class n16 leafNode
    n17[end_points]
    n7 --> n17
    class n17 normalNode
    n18[r]
    n17 --> n18
    class n18 leafNode
    n19[phi]
    n17 --> n19
    class n19 leafNode
    n20[z]
    n17 --> n20
    class n20 leafNode
    n21[centres]
    n7 --> n21
    class n21 normalNode
    n22[r]
    n21 --> n22
    class n22 leafNode
    n23[phi]
    n21 --> n23
    class n23 leafNode
    n24[z]
    n21 --> n24
    class n24 leafNode
    n25(cross_section)
    n6 --> n25
    class n25 complexNode
    n26[geometry_type]
    n25 --> n26
    class n26 normalNode
    n27[name]
    n26 --> n27
    class n27 leafNode
    n28[index]
    n26 --> n28
    class n28 leafNode
    n29[description]
    n26 --> n29
    class n29 leafNode
    n30[width]
    n25 --> n30
    class n30 leafNode
    n31[height]
    n25 --> n31
    class n31 leafNode
    n32[radius_inner]
    n25 --> n32
    class n32 leafNode
    n33[outline]
    n25 --> n33
    class n33 normalNode
    n34[normal]
    n33 --> n34
    class n34 leafNode
    n35[binormal]
    n33 --> n35
    class n35 leafNode
    n36[area]
    n25 --> n36
    class n36 leafNode
    n37[resistance]
    n6 --> n37
    class n37 leafNode
    n38[voltage]
    n6 --> n38
    class n38 normalNode
    n39[data]
    n38 --> n39
    class n39 leafNode
    n40[time]
    n38 --> n40
    class n40 leafNode
    n41[turns]
    n2 --> n41
    class n41 leafNode
    n42[resistance]
    n2 --> n42
    class n42 leafNode
    n43[current]
    n2 --> n43
    class n43 normalNode
    n44[data]
    n43 --> n44
    class n44 leafNode
    n45[time]
    n43 --> n45
    class n45 leafNode
    n46[voltage]
    n2 --> n46
    class n46 normalNode
    n47[data]
    n46 --> n47
    class n47 leafNode
    n48[time]
    n46 --> n48
    class n48 leafNode
    n49[latency]
    n1 --> n49
    class n49 leafNode
    n50[time]
    n1 --> n50
    class n50 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```