```mermaid
flowchart TD
    root["plasma_transport IDS"]

    n1[plasma_transport]
    root --> n1
    class n1 normalNode
    n2[midplane]
    n1 --> n2
    class n2 normalNode
    n3[name]
    n2 --> n3
    class n3 leafNode
    n4[index]
    n2 --> n4
    class n4 leafNode
    n5[description]
    n2 --> n5
    class n5 leafNode
    n6[vacuum_toroidal_field]
    n1 --> n6
    class n6 normalNode
    n7[r0]
    n6 --> n7
    class n7 leafNode
    n8[b0]
    n6 --> n8
    class n8 leafNode
    n9[grid_ggd]
    n1 --> n9
    class n9 normalNode
    n10[identifier]
    n9 --> n10
    class n10 normalNode
    n11[name]
    n10 --> n11
    class n11 leafNode
    n12[index]
    n10 --> n12
    class n12 leafNode
    n13[description]
    n10 --> n13
    class n13 leafNode
    n14[path]
    n9 --> n14
    class n14 leafNode
    n15[space]
    n9 --> n15
    class n15 normalNode
    n16[identifier]
    n15 --> n16
    class n16 normalNode
    n17[name]
    n16 --> n17
    class n17 leafNode
    n18[index]
    n16 --> n18
    class n18 leafNode
    n19[description]
    n16 --> n19
    class n19 leafNode
    n20[geometry_type]
    n15 --> n20
    class n20 normalNode
    n21[name]
    n20 --> n21
    class n21 leafNode
    n22[index]
    n20 --> n22
    class n22 leafNode
    n23[description]
    n20 --> n23
    class n23 leafNode
    n24[coordinates_type]
    n15 --> n24
    class n24 normalNode
    n25[name]
    n24 --> n25
    class n25 leafNode
    n26[index]
    n24 --> n26
    class n26 leafNode
    n27[description]
    n24 --> n27
    class n27 leafNode
    n28[objects_per_dimension]
    n15 --> n28
    class n28 normalNode
    n29[object]
    n28 --> n29
    class n29 normalNode
    n30[boundary]
    n29 --> n30
    class n30 normalNode
    n31[index]
    n30 --> n31
    class n31 leafNode
    n32[neighbours]
    n30 --> n32
    class n32 leafNode
    n33[geometry]
    n29 --> n33
    class n33 leafNode
    n34[nodes]
    n29 --> n34
    class n34 leafNode
    n35[measure]
    n29 --> n35
    class n35 leafNode
    n36[geometry_2d]
    n29 --> n36
    class n36 leafNode
    n37[geometry_content]
    n28 --> n37
    class n37 normalNode
    n38[name]
    n37 --> n38
    class n38 leafNode
    n39[index]
    n37 --> n39
    class n39 leafNode
    n40[description]
    n37 --> n40
    class n40 leafNode
    n41[grid_subset]
    n9 --> n41
    class n41 normalNode
    n42[identifier]
    n41 --> n42
    class n42 normalNode
    n43[name]
    n42 --> n43
    class n43 leafNode
    n44[index]
    n42 --> n44
    class n44 leafNode
    n45[description]
    n42 --> n45
    class n45 leafNode
    n46[dimension]
    n41 --> n46
    class n46 leafNode
    n47[element]
    n41 --> n47
    class n47 normalNode
    n48[object]
    n47 --> n48
    class n48 normalNode
    n49[space]
    n48 --> n49
    class n49 leafNode
    n50[dimension]
    n48 --> n50
    class n50 leafNode
    n51[index]
    n48 --> n51
    class n51 leafNode
    n52[base]
    n41 --> n52
    class n52 normalNode
    n53[jacobian]
    n52 --> n53
    class n53 leafNode
    n54[tensor_covariant]
    n52 --> n54
    class n54 leafNode
    n55[tensor_contravariant]
    n52 --> n55
    class n55 leafNode
    n56[metric]
    n41 --> n56
    class n56 normalNode
    n57[jacobian]
    n56 --> n57
    class n57 leafNode
    n58[tensor_covariant]
    n56 --> n58
    class n58 leafNode
    n59[tensor_contravariant]
    n56 --> n59
    class n59 leafNode
    n60[time]
    n9 --> n60
    class n60 leafNode
    n61[model]
    n1 --> n61
    class n61 normalNode
    n62[comment]
    n61 --> n62
    class n62 leafNode
    n63[identifier]
    n61 --> n63
    class n63 normalNode
    n64[name]
    n63 --> n64
    class n64 leafNode
    n65[index]
    n63 --> n65
    class n65 leafNode
    n66[description]
    n63 --> n66
    class n66 leafNode
    n67[flux_multiplier]
    n61 --> n67
    class n67 leafNode
    n68(profiles_1d)
    n61 --> n68
    class n68 complexNode
    n69(grid_d)
    n68 --> n69
    class n69 complexNode
    n70[rho_pol_norm]
    n69 --> n70
    class n70 leafNode
    n71[psi]
    n69 --> n71
    class n71 leafNode
    n72[rho_tor_norm]
    n69 --> n72
    class n72 leafNode
    n73[rho_tor]
    n69 --> n73
    class n73 leafNode
    n74[volume]
    n69 --> n74
    class n74 leafNode
    n75[area]
    n69 --> n75
    class n75 leafNode
    n76[surface]
    n69 --> n76
    class n76 leafNode
    n77[psi_magnetic_axis]
    n69 --> n77
    class n77 leafNode
    n78[psi_boundary]
    n69 --> n78
    class n78 leafNode
    n79(grid_v)
    n68 --> n79
    class n79 complexNode
    n80[rho_pol_norm]
    n79 --> n80
    class n80 leafNode
    n81[psi]
    n79 --> n81
    class n81 leafNode
    n82[rho_tor_norm]
    n79 --> n82
    class n82 leafNode
    n83[rho_tor]
    n79 --> n83
    class n83 leafNode
    n84[volume]
    n79 --> n84
    class n84 leafNode
    n85[area]
    n79 --> n85
    class n85 leafNode
    n86[surface]
    n79 --> n86
    class n86 leafNode
    n87[psi_magnetic_axis]
    n79 --> n87
    class n87 leafNode
    n88[psi_boundary]
    n79 --> n88
    class n88 leafNode
    n89(grid_flux)
    n68 --> n89
    class n89 complexNode
    n90[rho_pol_norm]
    n89 --> n90
    class n90 leafNode
    n91[psi]
    n89 --> n91
    class n91 leafNode
    n92[rho_tor_norm]
    n89 --> n92
    class n92 leafNode
    n93[rho_tor]
    n89 --> n93
    class n93 leafNode
    n94[volume]
    n89 --> n94
    class n94 leafNode
    n95[area]
    n89 --> n95
    class n95 leafNode
    n96[surface]
    n89 --> n96
    class n96 leafNode
    n97[psi_magnetic_axis]
    n89 --> n97
    class n97 leafNode
    n98[psi_boundary]
    n89 --> n98
    class n98 leafNode
    n99[conductivity_parallel]
    n68 --> n99
    class n99 leafNode
    n100[electrons]
    n68 --> n100
    class n100 normalNode
    n101[particles]
    n100 --> n101
    class n101 normalNode
    n102[d]
    n101 --> n102
    class n102 leafNode
    n103[v]
    n101 --> n103
    class n103 leafNode
    n104[flux]
    n101 --> n104
    class n104 leafNode
    n105[energy]
    n100 --> n105
    class n105 normalNode
    n106[d]
    n105 --> n106
    class n106 leafNode
    n107[v]
    n105 --> n107
    class n107 leafNode
    n108[flux]
    n105 --> n108
    class n108 leafNode
    n109[total_ion_energy]
    n68 --> n109
    class n109 normalNode
    n110[d]
    n109 --> n110
    class n110 leafNode
    n111[v]
    n109 --> n111
    class n111 leafNode
    n112[flux]
    n109 --> n112
    class n112 leafNode
    n113[momentum_phi]
    n68 --> n113
    class n113 normalNode
    n114[d]
    n113 --> n114
    class n114 leafNode
    n115[v]
    n113 --> n115
    class n115 leafNode
    n116[flux]
    n113 --> n116
    class n116 leafNode
    n117[e_field_radial]
    n68 --> n117
    class n117 leafNode
    n118(ion)
    n68 --> n118
    class n118 complexNode
    n119[element]
    n118 --> n119
    class n119 normalNode
    n120[a]
    n119 --> n120
    class n120 leafNode
    n121[z_n]
    n119 --> n121
    class n121 leafNode
    n122[atoms_n]
    n119 --> n122
    class n122 leafNode
    n123[z_ion]
    n118 --> n123
    class n123 leafNode
    n124[name]
    n118 --> n124
    class n124 leafNode
    n125[neutral_index]
    n118 --> n125
    class n125 leafNode
    n126[particles]
    n118 --> n126
    class n126 normalNode
    n127[d]
    n126 --> n127
    class n127 leafNode
    n128[v]
    n126 --> n128
    class n128 leafNode
    n129[flux]
    n126 --> n129
    class n129 leafNode
    n130[energy]
    n118 --> n130
    class n130 normalNode
    n131[d]
    n130 --> n131
    class n131 leafNode
    n132[v]
    n130 --> n132
    class n132 leafNode
    n133[flux]
    n130 --> n133
    class n133 leafNode
    n134[momentum]
    n118 --> n134
    class n134 normalNode
    n135[radial]
    n134 --> n135
    class n135 normalNode
    n136[d]
    n135 --> n136
    class n136 leafNode
    n137[v]
    n135 --> n137
    class n137 leafNode
    n138[flux]
    n135 --> n138
    class n138 leafNode
    n139[flow_damping_rate]
    n135 --> n139
    class n139 leafNode
    n140[diamagnetic]
    n134 --> n140
    class n140 normalNode
    n141[d]
    n140 --> n141
    class n141 leafNode
    n142[v]
    n140 --> n142
    class n142 leafNode
    n143[flux]
    n140 --> n143
    class n143 leafNode
    n144[flow_damping_rate]
    n140 --> n144
    class n144 leafNode
    n145[parallel]
    n134 --> n145
    class n145 normalNode
    n146[d]
    n145 --> n146
    class n146 leafNode
    n147[v]
    n145 --> n147
    class n147 leafNode
    n148[flux]
    n145 --> n148
    class n148 leafNode
    n149[flow_damping_rate]
    n145 --> n149
    class n149 leafNode
    n150[poloidal]
    n134 --> n150
    class n150 normalNode
    n151[d]
    n150 --> n151
    class n151 leafNode
    n152[v]
    n150 --> n152
    class n152 leafNode
    n153[flux]
    n150 --> n153
    class n153 leafNode
    n154[flow_damping_rate]
    n150 --> n154
    class n154 leafNode
    n155[toroidal]
    n134 --> n155
    class n155 normalNode
    n156[d]
    n155 --> n156
    class n156 leafNode
    n157[v]
    n155 --> n157
    class n157 leafNode
    n158[flux]
    n155 --> n158
    class n158 leafNode
    n159[flow_damping_rate]
    n155 --> n159
    class n159 leafNode
    n160[multiple_states_flag]
    n118 --> n160
    class n160 leafNode
    n161(state)
    n118 --> n161
    class n161 complexNode
    n162[z_min]
    n161 --> n162
    class n162 leafNode
    n163[z_max]
    n161 --> n163
    class n163 leafNode
    n164[name]
    n161 --> n164
    class n164 leafNode
    n165[vibrational_level]
    n161 --> n165
    class n165 leafNode
    n166[vibrational_mode]
    n161 --> n166
    class n166 leafNode
    n167[electron_configuration]
    n161 --> n167
    class n167 leafNode
    n168[particles]
    n161 --> n168
    class n168 normalNode
    n169[d]
    n168 --> n169
    class n169 leafNode
    n170[v]
    n168 --> n170
    class n170 leafNode
    n171[flux]
    n168 --> n171
    class n171 leafNode
    n172[energy]
    n161 --> n172
    class n172 normalNode
    n173[d]
    n172 --> n173
    class n173 leafNode
    n174[v]
    n172 --> n174
    class n174 leafNode
    n175[flux]
    n172 --> n175
    class n175 leafNode
    n176[momentum]
    n161 --> n176
    class n176 normalNode
    n177[radial]
    n176 --> n177
    class n177 normalNode
    n178[d]
    n177 --> n178
    class n178 leafNode
    n179[v]
    n177 --> n179
    class n179 leafNode
    n180[flux]
    n177 --> n180
    class n180 leafNode
    n181[flow_damping_rate]
    n177 --> n181
    class n181 leafNode
    n182[diamagnetic]
    n176 --> n182
    class n182 normalNode
    n183[d]
    n182 --> n183
    class n183 leafNode
    n184[v]
    n182 --> n184
    class n184 leafNode
    n185[flux]
    n182 --> n185
    class n185 leafNode
    n186[flow_damping_rate]
    n182 --> n186
    class n186 leafNode
    n187[parallel]
    n176 --> n187
    class n187 normalNode
    n188[d]
    n187 --> n188
    class n188 leafNode
    n189[v]
    n187 --> n189
    class n189 leafNode
    n190[flux]
    n187 --> n190
    class n190 leafNode
    n191[flow_damping_rate]
    n187 --> n191
    class n191 leafNode
    n192[poloidal]
    n176 --> n192
    class n192 normalNode
    n193[d]
    n192 --> n193
    class n193 leafNode
    n194[v]
    n192 --> n194
    class n194 leafNode
    n195[flux]
    n192 --> n195
    class n195 leafNode
    n196[flow_damping_rate]
    n192 --> n196
    class n196 leafNode
    n197[toroidal]
    n176 --> n197
    class n197 normalNode
    n198[d]
    n197 --> n198
    class n198 leafNode
    n199[v]
    n197 --> n199
    class n199 leafNode
    n200[flux]
    n197 --> n200
    class n200 leafNode
    n201[flow_damping_rate]
    n197 --> n201
    class n201 leafNode
    n202(neutral)
    n68 --> n202
    class n202 complexNode
    n203[element]
    n202 --> n203
    class n203 normalNode
    n204[a]
    n203 --> n204
    class n204 leafNode
    n205[z_n]
    n203 --> n205
    class n205 leafNode
    n206[atoms_n]
    n203 --> n206
    class n206 leafNode
    n207[name]
    n202 --> n207
    class n207 leafNode
    n208[ion_index]
    n202 --> n208
    class n208 leafNode
    n209[particles]
    n202 --> n209
    class n209 normalNode
    n210[d]
    n209 --> n210
    class n210 leafNode
    n211[v]
    n209 --> n211
    class n211 leafNode
    n212[flux]
    n209 --> n212
    class n212 leafNode
    n213[energy]
    n202 --> n213
    class n213 normalNode
    n214[d]
    n213 --> n214
    class n214 leafNode
    n215[v]
    n213 --> n215
    class n215 leafNode
    n216[flux]
    n213 --> n216
    class n216 leafNode
    n217[multiple_states_flag]
    n202 --> n217
    class n217 leafNode
    n218(state)
    n202 --> n218
    class n218 complexNode
    n219[name]
    n218 --> n219
    class n219 leafNode
    n220[vibrational_level]
    n218 --> n220
    class n220 leafNode
    n221[vibrational_mode]
    n218 --> n221
    class n221 leafNode
    n222[electron_configuration]
    n218 --> n222
    class n222 leafNode
    n223[particles]
    n218 --> n223
    class n223 normalNode
    n224[d]
    n223 --> n224
    class n224 leafNode
    n225[v]
    n223 --> n225
    class n225 leafNode
    n226[flux]
    n223 --> n226
    class n226 leafNode
    n227[energy]
    n218 --> n227
    class n227 normalNode
    n228[d]
    n227 --> n228
    class n228 leafNode
    n229[v]
    n227 --> n229
    class n229 leafNode
    n230[flux]
    n227 --> n230
    class n230 leafNode
    n231[time]
    n68 --> n231
    class n231 leafNode
    n232(ggd_fast)
    n61 --> n232
    class n232 complexNode
    n233[electrons]
    n232 --> n233
    class n233 normalNode
    n234[particle_flux_integrated]
    n233 --> n234
    class n234 normalNode
    n235[grid_index]
    n234 --> n235
    class n235 leafNode
    n236[grid_subset_index]
    n234 --> n236
    class n236 leafNode
    n237[value]
    n234 --> n237
    class n237 leafNode
    n238[power]
    n233 --> n238
    class n238 normalNode
    n239[grid_index]
    n238 --> n239
    class n239 leafNode
    n240[grid_subset_index]
    n238 --> n240
    class n240 leafNode
    n241[value]
    n238 --> n241
    class n241 leafNode
    n242[ion]
    n232 --> n242
    class n242 normalNode
    n243[element]
    n242 --> n243
    class n243 normalNode
    n244[a]
    n243 --> n244
    class n244 leafNode
    n245[z_n]
    n243 --> n245
    class n245 leafNode
    n246[atoms_n]
    n243 --> n246
    class n246 leafNode
    n247[z_ion]
    n242 --> n247
    class n247 leafNode
    n248[name]
    n242 --> n248
    class n248 leafNode
    n249[neutral_index]
    n242 --> n249
    class n249 leafNode
    n250[particle_flux_integrated]
    n242 --> n250
    class n250 normalNode
    n251[grid_index]
    n250 --> n251
    class n251 leafNode
    n252[grid_subset_index]
    n250 --> n252
    class n252 leafNode
    n253[value]
    n250 --> n253
    class n253 leafNode
    n254[neutral]
    n232 --> n254
    class n254 normalNode
    n255[element]
    n254 --> n255
    class n255 normalNode
    n256[a]
    n255 --> n256
    class n256 leafNode
    n257[z_n]
    n255 --> n257
    class n257 leafNode
    n258[atoms_n]
    n255 --> n258
    class n258 leafNode
    n259[name]
    n254 --> n259
    class n259 leafNode
    n260[ion_index]
    n254 --> n260
    class n260 leafNode
    n261[particle_flux_integrated]
    n254 --> n261
    class n261 normalNode
    n262[grid_index]
    n261 --> n262
    class n262 leafNode
    n263[grid_subset_index]
    n261 --> n263
    class n263 leafNode
    n264[value]
    n261 --> n264
    class n264 leafNode
    n265[power_ion_total]
    n232 --> n265
    class n265 normalNode
    n266[grid_index]
    n265 --> n266
    class n266 leafNode
    n267[grid_subset_index]
    n265 --> n267
    class n267 leafNode
    n268[value]
    n265 --> n268
    class n268 leafNode
    n269[energy_flux_max]
    n232 --> n269
    class n269 normalNode
    n270[grid_index]
    n269 --> n270
    class n270 leafNode
    n271[grid_subset_index]
    n269 --> n271
    class n271 leafNode
    n272[value]
    n269 --> n272
    class n272 leafNode
    n273[power]
    n232 --> n273
    class n273 normalNode
    n274[grid_index]
    n273 --> n274
    class n274 leafNode
    n275[grid_subset_index]
    n273 --> n275
    class n275 leafNode
    n276[value]
    n273 --> n276
    class n276 leafNode
    n277[time]
    n232 --> n277
    class n277 leafNode
    n278[time]
    n1 --> n278
    class n278 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```