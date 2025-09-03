```mermaid
flowchart TD
    root["waves IDS"]

    n1[waves]
    root --> n1
    class n1 normalNode
    n2(coherent_wave)
    n1 --> n2
    class n2 complexNode
    n3[identifier]
    n2 --> n3
    class n3 normalNode
    n4[type]
    n3 --> n4
    class n4 normalNode
    n5[name]
    n4 --> n5
    class n5 leafNode
    n6[index]
    n4 --> n6
    class n6 leafNode
    n7[description]
    n4 --> n7
    class n7 leafNode
    n8[antenna_name]
    n3 --> n8
    class n8 leafNode
    n9[index_in_antenna]
    n3 --> n9
    class n9 leafNode
    n10[wave_solver_type]
    n2 --> n10
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
    n14(global_quantities)
    n2 --> n14
    class n14 complexNode
    n15[frequency]
    n14 --> n15
    class n15 leafNode
    n16[n_phi]
    n14 --> n16
    class n16 leafNode
    n17[power]
    n14 --> n17
    class n17 leafNode
    n18[power_n_phi]
    n14 --> n18
    class n18 leafNode
    n19[current_phi]
    n14 --> n19
    class n19 leafNode
    n20[current_phi_n_phi]
    n14 --> n20
    class n20 leafNode
    n21[electrons]
    n14 --> n21
    class n21 normalNode
    n22[power_thermal]
    n21 --> n22
    class n22 leafNode
    n23[power_thermal_n_phi]
    n21 --> n23
    class n23 leafNode
    n24[power_fast]
    n21 --> n24
    class n24 leafNode
    n25[power_fast_n_phi]
    n21 --> n25
    class n25 leafNode
    n26[distribution_assumption]
    n21 --> n26
    class n26 leafNode
    n27(ion)
    n14 --> n27
    class n27 complexNode
    n28[element]
    n27 --> n28
    class n28 normalNode
    n29[a]
    n28 --> n29
    class n29 leafNode
    n30[z_n]
    n28 --> n30
    class n30 leafNode
    n31[atoms_n]
    n28 --> n31
    class n31 leafNode
    n32[z_ion]
    n27 --> n32
    class n32 leafNode
    n33[name]
    n27 --> n33
    class n33 leafNode
    n34[power_thermal]
    n27 --> n34
    class n34 leafNode
    n35[power_thermal_n_phi]
    n27 --> n35
    class n35 leafNode
    n36[power_fast]
    n27 --> n36
    class n36 leafNode
    n37[power_fast_n_phi]
    n27 --> n37
    class n37 leafNode
    n38[multiple_states_flag]
    n27 --> n38
    class n38 leafNode
    n39[distribution_assumption]
    n27 --> n39
    class n39 leafNode
    n40(state)
    n27 --> n40
    class n40 complexNode
    n41[z_min]
    n40 --> n41
    class n41 leafNode
    n42[z_max]
    n40 --> n42
    class n42 leafNode
    n43[name]
    n40 --> n43
    class n43 leafNode
    n44[electron_configuration]
    n40 --> n44
    class n44 leafNode
    n45[vibrational_level]
    n40 --> n45
    class n45 leafNode
    n46[vibrational_mode]
    n40 --> n46
    class n46 leafNode
    n47[power_thermal]
    n40 --> n47
    class n47 leafNode
    n48[power_thermal_n_phi]
    n40 --> n48
    class n48 leafNode
    n49[power_fast]
    n40 --> n49
    class n49 leafNode
    n50[power_fast_n_phi]
    n40 --> n50
    class n50 leafNode
    n51[time]
    n14 --> n51
    class n51 leafNode
    n52(profiles_1d)
    n2 --> n52
    class n52 complexNode
    n53(grid)
    n52 --> n53
    class n53 complexNode
    n54[rho_tor_norm]
    n53 --> n54
    class n54 leafNode
    n55[rho_tor]
    n53 --> n55
    class n55 leafNode
    n56[rho_pol_norm]
    n53 --> n56
    class n56 leafNode
    n57[psi]
    n53 --> n57
    class n57 leafNode
    n58[volume]
    n53 --> n58
    class n58 leafNode
    n59[area]
    n53 --> n59
    class n59 leafNode
    n60[surface]
    n53 --> n60
    class n60 leafNode
    n61[psi_magnetic_axis]
    n53 --> n61
    class n61 leafNode
    n62[psi_boundary]
    n53 --> n62
    class n62 leafNode
    n63[n_phi]
    n52 --> n63
    class n63 leafNode
    n64[power_density]
    n52 --> n64
    class n64 leafNode
    n65[power_density_n_phi]
    n52 --> n65
    class n65 leafNode
    n66[power_inside]
    n52 --> n66
    class n66 leafNode
    n67[power_inside_n_phi]
    n52 --> n67
    class n67 leafNode
    n68[current_phi_inside]
    n52 --> n68
    class n68 leafNode
    n69[current_phi_inside_n_phi]
    n52 --> n69
    class n69 leafNode
    n70[current_parallel_density]
    n52 --> n70
    class n70 leafNode
    n71[current_parallel_density_n_phi]
    n52 --> n71
    class n71 leafNode
    n72[e_field_n_phi]
    n52 --> n72
    class n72 normalNode
    n73[plus]
    n72 --> n73
    class n73 normalNode
    n74[amplitude]
    n73 --> n74
    class n74 leafNode
    n75[phase]
    n73 --> n75
    class n75 leafNode
    n76[minus]
    n72 --> n76
    class n76 normalNode
    n77[amplitude]
    n76 --> n77
    class n77 leafNode
    n78[phase]
    n76 --> n78
    class n78 leafNode
    n79[parallel]
    n72 --> n79
    class n79 normalNode
    n80[amplitude]
    n79 --> n80
    class n80 leafNode
    n81[phase]
    n79 --> n81
    class n81 leafNode
    n82[k_perpendicular]
    n52 --> n82
    class n82 leafNode
    n83(electrons)
    n52 --> n83
    class n83 complexNode
    n84[power_density_thermal]
    n83 --> n84
    class n84 leafNode
    n85[power_density_thermal_n_phi]
    n83 --> n85
    class n85 leafNode
    n86[power_density_fast]
    n83 --> n86
    class n86 leafNode
    n87[power_density_fast_n_phi]
    n83 --> n87
    class n87 leafNode
    n88[power_inside_thermal]
    n83 --> n88
    class n88 leafNode
    n89[power_inside_thermal_n_phi]
    n83 --> n89
    class n89 leafNode
    n90[power_inside_fast]
    n83 --> n90
    class n90 leafNode
    n91[power_inside_fast_n_phi]
    n83 --> n91
    class n91 leafNode
    n92(ion)
    n52 --> n92
    class n92 complexNode
    n93[element]
    n92 --> n93
    class n93 normalNode
    n94[a]
    n93 --> n94
    class n94 leafNode
    n95[z_n]
    n93 --> n95
    class n95 leafNode
    n96[atoms_n]
    n93 --> n96
    class n96 leafNode
    n97[z_ion]
    n92 --> n97
    class n97 leafNode
    n98[name]
    n92 --> n98
    class n98 leafNode
    n99[power_density_thermal]
    n92 --> n99
    class n99 leafNode
    n100[power_density_thermal_n_phi]
    n92 --> n100
    class n100 leafNode
    n101[power_density_fast]
    n92 --> n101
    class n101 leafNode
    n102[power_density_fast_n_phi]
    n92 --> n102
    class n102 leafNode
    n103[power_inside_thermal]
    n92 --> n103
    class n103 leafNode
    n104[power_inside_thermal_n_phi]
    n92 --> n104
    class n104 leafNode
    n105[power_inside_fast]
    n92 --> n105
    class n105 leafNode
    n106[power_inside_fast_n_phi]
    n92 --> n106
    class n106 leafNode
    n107[multiple_states_flag]
    n92 --> n107
    class n107 leafNode
    n108(state)
    n92 --> n108
    class n108 complexNode
    n109[z_min]
    n108 --> n109
    class n109 leafNode
    n110[z_max]
    n108 --> n110
    class n110 leafNode
    n111[name]
    n108 --> n111
    class n111 leafNode
    n112[electron_configuration]
    n108 --> n112
    class n112 leafNode
    n113[vibrational_level]
    n108 --> n113
    class n113 leafNode
    n114[vibrational_mode]
    n108 --> n114
    class n114 leafNode
    n115[power_density_thermal]
    n108 --> n115
    class n115 leafNode
    n116[power_density_thermal_n_phi]
    n108 --> n116
    class n116 leafNode
    n117[power_density_fast]
    n108 --> n117
    class n117 leafNode
    n118[power_density_fast_n_phi]
    n108 --> n118
    class n118 leafNode
    n119[power_inside_thermal]
    n108 --> n119
    class n119 leafNode
    n120[power_inside_thermal_n_phi]
    n108 --> n120
    class n120 leafNode
    n121[power_inside_fast]
    n108 --> n121
    class n121 leafNode
    n122[power_inside_fast_n_phi]
    n108 --> n122
    class n122 leafNode
    n123[time]
    n52 --> n123
    class n123 leafNode
    n124(profiles_2d)
    n2 --> n124
    class n124 complexNode
    n125(grid)
    n124 --> n125
    class n125 complexNode
    n126[type]
    n125 --> n126
    class n126 normalNode
    n127[name]
    n126 --> n127
    class n127 leafNode
    n128[index]
    n126 --> n128
    class n128 leafNode
    n129[description]
    n126 --> n129
    class n129 leafNode
    n130[r]
    n125 --> n130
    class n130 leafNode
    n131[z]
    n125 --> n131
    class n131 leafNode
    n132[theta_straight]
    n125 --> n132
    class n132 leafNode
    n133[theta_geometric]
    n125 --> n133
    class n133 leafNode
    n134[rho_tor_norm]
    n125 --> n134
    class n134 leafNode
    n135[rho_tor]
    n125 --> n135
    class n135 leafNode
    n136[psi]
    n125 --> n136
    class n136 leafNode
    n137[volume]
    n125 --> n137
    class n137 leafNode
    n138[area]
    n125 --> n138
    class n138 leafNode
    n139[n_phi]
    n124 --> n139
    class n139 leafNode
    n140[power_density]
    n124 --> n140
    class n140 leafNode
    n141[power_density_n_phi]
    n124 --> n141
    class n141 leafNode
    n142[e_field_n_phi]
    n124 --> n142
    class n142 normalNode
    n143[plus]
    n142 --> n143
    class n143 normalNode
    n144[amplitude]
    n143 --> n144
    class n144 leafNode
    n145[phase]
    n143 --> n145
    class n145 leafNode
    n146[minus]
    n142 --> n146
    class n146 normalNode
    n147[amplitude]
    n146 --> n147
    class n147 leafNode
    n148[phase]
    n146 --> n148
    class n148 leafNode
    n149[parallel]
    n142 --> n149
    class n149 normalNode
    n150[amplitude]
    n149 --> n150
    class n150 leafNode
    n151[phase]
    n149 --> n151
    class n151 leafNode
    n152[electrons]
    n124 --> n152
    class n152 normalNode
    n153[power_density_thermal]
    n152 --> n153
    class n153 leafNode
    n154[power_density_thermal_n_phi]
    n152 --> n154
    class n154 leafNode
    n155[power_density_fast]
    n152 --> n155
    class n155 leafNode
    n156[power_density_fast_n_phi]
    n152 --> n156
    class n156 leafNode
    n157(ion)
    n124 --> n157
    class n157 complexNode
    n158[element]
    n157 --> n158
    class n158 normalNode
    n159[a]
    n158 --> n159
    class n159 leafNode
    n160[z_n]
    n158 --> n160
    class n160 leafNode
    n161[atoms_n]
    n158 --> n161
    class n161 leafNode
    n162[z_ion]
    n157 --> n162
    class n162 leafNode
    n163[name]
    n157 --> n163
    class n163 leafNode
    n164[power_density_thermal]
    n157 --> n164
    class n164 leafNode
    n165[power_density_thermal_n_phi]
    n157 --> n165
    class n165 leafNode
    n166[power_density_fast]
    n157 --> n166
    class n166 leafNode
    n167[power_density_fast_n_phi]
    n157 --> n167
    class n167 leafNode
    n168[multiple_states_flag]
    n157 --> n168
    class n168 leafNode
    n169(state)
    n157 --> n169
    class n169 complexNode
    n170[z_min]
    n169 --> n170
    class n170 leafNode
    n171[z_max]
    n169 --> n171
    class n171 leafNode
    n172[name]
    n169 --> n172
    class n172 leafNode
    n173[electron_configuration]
    n169 --> n173
    class n173 leafNode
    n174[vibrational_level]
    n169 --> n174
    class n174 leafNode
    n175[vibrational_mode]
    n169 --> n175
    class n175 leafNode
    n176[power_density_thermal]
    n169 --> n176
    class n176 leafNode
    n177[power_density_thermal_n_phi]
    n169 --> n177
    class n177 leafNode
    n178[power_density_fast]
    n169 --> n178
    class n178 leafNode
    n179[power_density_fast_n_phi]
    n169 --> n179
    class n179 leafNode
    n180[time]
    n124 --> n180
    class n180 leafNode
    n181[beam_tracing]
    n2 --> n181
    class n181 normalNode
    n182(beam)
    n181 --> n182
    class n182 complexNode
    n183[power_initial]
    n182 --> n183
    class n183 leafNode
    n184[length]
    n182 --> n184
    class n184 leafNode
    n185(position)
    n182 --> n185
    class n185 complexNode
    n186[r]
    n185 --> n186
    class n186 leafNode
    n187[z]
    n185 --> n187
    class n187 leafNode
    n188[phi]
    n185 --> n188
    class n188 leafNode
    n189[psi]
    n185 --> n189
    class n189 leafNode
    n190[rho_tor_norm]
    n185 --> n190
    class n190 leafNode
    n191[theta]
    n185 --> n191
    class n191 leafNode
    n192(wave_vector)
    n182 --> n192
    class n192 complexNode
    n193[k_r]
    n192 --> n193
    class n193 leafNode
    n194[k_z]
    n192 --> n194
    class n194 leafNode
    n195[k_phi]
    n192 --> n195
    class n195 leafNode
    n196[k_r_norm]
    n192 --> n196
    class n196 leafNode
    n197[k_z_norm]
    n192 --> n197
    class n197 leafNode
    n198[k_phi_norm]
    n192 --> n198
    class n198 leafNode
    n199[n_parallel]
    n192 --> n199
    class n199 leafNode
    n200[n_perpendicular]
    n192 --> n200
    class n200 leafNode
    n201[n_phi]
    n192 --> n201
    class n201 leafNode
    n202[varying_n_phi]
    n192 --> n202
    class n202 leafNode
    n203[e_field]
    n182 --> n203
    class n203 normalNode
    n204[plus]
    n203 --> n204
    class n204 normalNode
    n205[real]
    n204 --> n205
    class n205 leafNode
    n206[imaginary]
    n204 --> n206
    class n206 leafNode
    n207[minus]
    n203 --> n207
    class n207 normalNode
    n208[real]
    n207 --> n208
    class n208 leafNode
    n209[imaginary]
    n207 --> n209
    class n209 leafNode
    n210[parallel]
    n203 --> n210
    class n210 normalNode
    n211[real]
    n210 --> n211
    class n211 leafNode
    n212[imaginary]
    n210 --> n212
    class n212 leafNode
    n213[power_flow_norm]
    n182 --> n213
    class n213 normalNode
    n214[perpendicular]
    n213 --> n214
    class n214 leafNode
    n215[parallel]
    n213 --> n215
    class n215 leafNode
    n216[electrons]
    n182 --> n216
    class n216 normalNode
    n217[power]
    n216 --> n217
    class n217 leafNode
    n218(ion)
    n182 --> n218
    class n218 complexNode
    n219[element]
    n218 --> n219
    class n219 normalNode
    n220[a]
    n219 --> n220
    class n220 leafNode
    n221[z_n]
    n219 --> n221
    class n221 leafNode
    n222[atoms_n]
    n219 --> n222
    class n222 leafNode
    n223[z_ion]
    n218 --> n223
    class n223 leafNode
    n224[name]
    n218 --> n224
    class n224 leafNode
    n225[power]
    n218 --> n225
    class n225 leafNode
    n226[multiple_states_flag]
    n218 --> n226
    class n226 leafNode
    n227(state)
    n218 --> n227
    class n227 complexNode
    n228[z_min]
    n227 --> n228
    class n228 leafNode
    n229[z_max]
    n227 --> n229
    class n229 leafNode
    n230[name]
    n227 --> n230
    class n230 leafNode
    n231[electron_configuration]
    n227 --> n231
    class n231 leafNode
    n232[vibrational_level]
    n227 --> n232
    class n232 leafNode
    n233[vibrational_mode]
    n227 --> n233
    class n233 leafNode
    n234[power]
    n227 --> n234
    class n234 leafNode
    n235[spot]
    n182 --> n235
    class n235 normalNode
    n236[size]
    n235 --> n236
    class n236 leafNode
    n237[angle]
    n235 --> n237
    class n237 leafNode
    n238[phase]
    n182 --> n238
    class n238 normalNode
    n239[curvature]
    n238 --> n239
    class n239 leafNode
    n240[angle]
    n238 --> n240
    class n240 leafNode
    n241[time]
    n181 --> n241
    class n241 leafNode
    n242[full_wave]
    n2 --> n242
    class n242 normalNode
    n243[grid]
    n242 --> n243
    class n243 normalNode
    n244[identifier]
    n243 --> n244
    class n244 normalNode
    n245[name]
    n244 --> n245
    class n245 leafNode
    n246[index]
    n244 --> n246
    class n246 leafNode
    n247[description]
    n244 --> n247
    class n247 leafNode
    n248[path]
    n243 --> n248
    class n248 leafNode
    n249[space]
    n243 --> n249
    class n249 normalNode
    n250[identifier]
    n249 --> n250
    class n250 normalNode
    n251[name]
    n250 --> n251
    class n251 leafNode
    n252[index]
    n250 --> n252
    class n252 leafNode
    n253[description]
    n250 --> n253
    class n253 leafNode
    n254[geometry_type]
    n249 --> n254
    class n254 normalNode
    n255[name]
    n254 --> n255
    class n255 leafNode
    n256[index]
    n254 --> n256
    class n256 leafNode
    n257[description]
    n254 --> n257
    class n257 leafNode
    n258[coordinates_type]
    n249 --> n258
    class n258 normalNode
    n259[name]
    n258 --> n259
    class n259 leafNode
    n260[index]
    n258 --> n260
    class n260 leafNode
    n261[description]
    n258 --> n261
    class n261 leafNode
    n262[objects_per_dimension]
    n249 --> n262
    class n262 normalNode
    n263[object]
    n262 --> n263
    class n263 normalNode
    n264[boundary]
    n263 --> n264
    class n264 normalNode
    n265[index]
    n264 --> n265
    class n265 leafNode
    n266[neighbours]
    n264 --> n266
    class n266 leafNode
    n267[geometry]
    n263 --> n267
    class n267 leafNode
    n268[nodes]
    n263 --> n268
    class n268 leafNode
    n269[measure]
    n263 --> n269
    class n269 leafNode
    n270[geometry_2d]
    n263 --> n270
    class n270 leafNode
    n271[geometry_content]
    n262 --> n271
    class n271 normalNode
    n272[name]
    n271 --> n272
    class n272 leafNode
    n273[index]
    n271 --> n273
    class n273 leafNode
    n274[description]
    n271 --> n274
    class n274 leafNode
    n275[grid_subset]
    n243 --> n275
    class n275 normalNode
    n276[identifier]
    n275 --> n276
    class n276 normalNode
    n277[name]
    n276 --> n277
    class n277 leafNode
    n278[index]
    n276 --> n278
    class n278 leafNode
    n279[description]
    n276 --> n279
    class n279 leafNode
    n280[dimension]
    n275 --> n280
    class n280 leafNode
    n281[element]
    n275 --> n281
    class n281 normalNode
    n282[object]
    n281 --> n282
    class n282 normalNode
    n283[space]
    n282 --> n283
    class n283 leafNode
    n284[dimension]
    n282 --> n284
    class n284 leafNode
    n285[index]
    n282 --> n285
    class n285 leafNode
    n286[base]
    n275 --> n286
    class n286 normalNode
    n287[jacobian]
    n286 --> n287
    class n287 leafNode
    n288[tensor_covariant]
    n286 --> n288
    class n288 leafNode
    n289[tensor_contravariant]
    n286 --> n289
    class n289 leafNode
    n290[metric]
    n275 --> n290
    class n290 normalNode
    n291[jacobian]
    n290 --> n291
    class n291 leafNode
    n292[tensor_covariant]
    n290 --> n292
    class n292 leafNode
    n293[tensor_contravariant]
    n290 --> n293
    class n293 leafNode
    n294[e_field]
    n242 --> n294
    class n294 normalNode
    n295[plus]
    n294 --> n295
    class n295 normalNode
    n296[grid_index]
    n295 --> n296
    class n296 leafNode
    n297[grid_subset_index]
    n295 --> n297
    class n297 leafNode
    n298[values]
    n295 --> n298
    class n298 leafNode
    n299[coefficients]
    n295 --> n299
    class n299 leafNode
    n300[minus]
    n294 --> n300
    class n300 normalNode
    n301[grid_index]
    n300 --> n301
    class n301 leafNode
    n302[grid_subset_index]
    n300 --> n302
    class n302 leafNode
    n303[values]
    n300 --> n303
    class n303 leafNode
    n304[coefficients]
    n300 --> n304
    class n304 leafNode
    n305[parallel]
    n294 --> n305
    class n305 normalNode
    n306[grid_index]
    n305 --> n306
    class n306 leafNode
    n307[grid_subset_index]
    n305 --> n307
    class n307 leafNode
    n308[values]
    n305 --> n308
    class n308 leafNode
    n309[coefficients]
    n305 --> n309
    class n309 leafNode
    n310[normal]
    n294 --> n310
    class n310 normalNode
    n311[grid_index]
    n310 --> n311
    class n311 leafNode
    n312[grid_subset_index]
    n310 --> n312
    class n312 leafNode
    n313[values]
    n310 --> n313
    class n313 leafNode
    n314[coefficients]
    n310 --> n314
    class n314 leafNode
    n315[bi_normal]
    n294 --> n315
    class n315 normalNode
    n316[grid_index]
    n315 --> n316
    class n316 leafNode
    n317[grid_subset_index]
    n315 --> n317
    class n317 leafNode
    n318[values]
    n315 --> n318
    class n318 leafNode
    n319[coefficients]
    n315 --> n319
    class n319 leafNode
    n320[b_field]
    n242 --> n320
    class n320 normalNode
    n321[parallel]
    n320 --> n321
    class n321 normalNode
    n322[grid_index]
    n321 --> n322
    class n322 leafNode
    n323[grid_subset_index]
    n321 --> n323
    class n323 leafNode
    n324[values]
    n321 --> n324
    class n324 leafNode
    n325[coefficients]
    n321 --> n325
    class n325 leafNode
    n326[normal]
    n320 --> n326
    class n326 normalNode
    n327[grid_index]
    n326 --> n327
    class n327 leafNode
    n328[grid_subset_index]
    n326 --> n328
    class n328 leafNode
    n329[values]
    n326 --> n329
    class n329 leafNode
    n330[coefficients]
    n326 --> n330
    class n330 leafNode
    n331[bi_normal]
    n320 --> n331
    class n331 normalNode
    n332[grid_index]
    n331 --> n332
    class n332 leafNode
    n333[grid_subset_index]
    n331 --> n333
    class n333 leafNode
    n334[values]
    n331 --> n334
    class n334 leafNode
    n335[coefficients]
    n331 --> n335
    class n335 leafNode
    n336[k_perpendicular]
    n242 --> n336
    class n336 normalNode
    n337[grid_index]
    n336 --> n337
    class n337 leafNode
    n338[grid_subset_index]
    n336 --> n338
    class n338 leafNode
    n339[values]
    n336 --> n339
    class n339 leafNode
    n340[coefficients]
    n336 --> n340
    class n340 leafNode
    n341[time]
    n242 --> n341
    class n341 leafNode
    n342[vacuum_toroidal_field]
    n1 --> n342
    class n342 normalNode
    n343[r0]
    n342 --> n343
    class n343 leafNode
    n344[b0]
    n342 --> n344
    class n344 leafNode
    n345[magnetic_axis]
    n1 --> n345
    class n345 normalNode
    n346[r]
    n345 --> n346
    class n346 leafNode
    n347[z]
    n345 --> n347
    class n347 leafNode
    n348[time]
    n1 --> n348
    class n348 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```