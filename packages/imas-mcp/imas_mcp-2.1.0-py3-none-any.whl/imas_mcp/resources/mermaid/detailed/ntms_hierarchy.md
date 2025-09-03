```mermaid
flowchart TD
    root["ntms IDS"]

    n1[ntms]
    root --> n1
    class n1 normalNode
    n2[vacuum_toroidal_field]
    n1 --> n2
    class n2 normalNode
    n3[r0]
    n2 --> n3
    class n3 leafNode
    n4[b0]
    n2 --> n4
    class n4 leafNode
    n5[time_slice]
    n1 --> n5
    class n5 normalNode
    n6(mode)
    n5 --> n6
    class n6 complexNode
    n7(onset)
    n6 --> n7
    class n7 complexNode
    n8[width]
    n7 --> n8
    class n8 leafNode
    n9[time_onset]
    n7 --> n9
    class n9 leafNode
    n10[time_offset]
    n7 --> n10
    class n10 leafNode
    n11[phase]
    n7 --> n11
    class n11 leafNode
    n12[n_phi]
    n7 --> n12
    class n12 leafNode
    n13[m_pol]
    n7 --> n13
    class n13 leafNode
    n14[cause]
    n7 --> n14
    class n14 leafNode
    n15[width]
    n6 --> n15
    class n15 leafNode
    n16[dwidth_dt]
    n6 --> n16
    class n16 leafNode
    n17[phase]
    n6 --> n17
    class n17 leafNode
    n18[dphase_dt]
    n6 --> n18
    class n18 leafNode
    n19[frequency]
    n6 --> n19
    class n19 leafNode
    n20[dfrequency_dt]
    n6 --> n20
    class n20 leafNode
    n21[n_phi]
    n6 --> n21
    class n21 leafNode
    n22[m_pol]
    n6 --> n22
    class n22 leafNode
    n23[deltaw]
    n6 --> n23
    class n23 normalNode
    n24[value]
    n23 --> n24
    class n24 leafNode
    n25[name]
    n23 --> n25
    class n25 leafNode
    n26[torque]
    n6 --> n26
    class n26 normalNode
    n27[value]
    n26 --> n27
    class n27 leafNode
    n28[name]
    n26 --> n28
    class n28 leafNode
    n29[calculation_method]
    n6 --> n29
    class n29 leafNode
    n30[delta_diff]
    n6 --> n30
    class n30 leafNode
    n31[rho_tor_norm]
    n6 --> n31
    class n31 leafNode
    n32[rho_tor]
    n6 --> n32
    class n32 leafNode
    n33(detailed_evolution)
    n6 --> n33
    class n33 complexNode
    n34[time_detailed]
    n33 --> n34
    class n34 leafNode
    n35[width]
    n33 --> n35
    class n35 leafNode
    n36[dwidth_dt]
    n33 --> n36
    class n36 leafNode
    n37[phase]
    n33 --> n37
    class n37 leafNode
    n38[dphase_dt]
    n33 --> n38
    class n38 leafNode
    n39[frequency]
    n33 --> n39
    class n39 leafNode
    n40[dfrequency_dt]
    n33 --> n40
    class n40 leafNode
    n41[n_phi]
    n33 --> n41
    class n41 leafNode
    n42[m_pol]
    n33 --> n42
    class n42 leafNode
    n43[deltaw]
    n33 --> n43
    class n43 normalNode
    n44[value]
    n43 --> n44
    class n44 leafNode
    n45[name]
    n43 --> n45
    class n45 leafNode
    n46[torque]
    n33 --> n46
    class n46 normalNode
    n47[value]
    n46 --> n47
    class n47 leafNode
    n48[name]
    n46 --> n48
    class n48 leafNode
    n49[calculation_method]
    n33 --> n49
    class n49 leafNode
    n50[delta_diff]
    n33 --> n50
    class n50 leafNode
    n51[rho_tor_norm]
    n33 --> n51
    class n51 leafNode
    n52[rho_tor]
    n33 --> n52
    class n52 leafNode
    n53[time]
    n5 --> n53
    class n53 leafNode
    n54[time]
    n1 --> n54
    class n54 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```