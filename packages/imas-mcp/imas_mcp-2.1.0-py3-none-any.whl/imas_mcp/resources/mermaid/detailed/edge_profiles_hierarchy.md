```mermaid
flowchart TD
    root["edge_profiles IDS"]

    n1(edge_profiles)
    root --> n1
    class n1 complexNode
    n2[vacuum_toroidal_field]
    n1 --> n2
    class n2 normalNode
    n3[r0]
    n2 --> n3
    class n3 leafNode
    n4[b0]
    n2 --> n4
    class n4 leafNode
    n5[midplane]
    n1 --> n5
    class n5 normalNode
    n6[name]
    n5 --> n6
    class n6 leafNode
    n7[index]
    n5 --> n7
    class n7 leafNode
    n8[description]
    n5 --> n8
    class n8 leafNode
    n9(profiles_1d)
    n1 --> n9
    class n9 complexNode
    n10(grid)
    n9 --> n10
    class n10 complexNode
    n11[rho_pol_norm]
    n10 --> n11
    class n11 leafNode
    n12[psi]
    n10 --> n12
    class n12 leafNode
    n13[rho_tor_norm]
    n10 --> n13
    class n13 leafNode
    n14[rho_tor]
    n10 --> n14
    class n14 leafNode
    n15[volume]
    n10 --> n15
    class n15 leafNode
    n16[area]
    n10 --> n16
    class n16 leafNode
    n17[psi_magnetic_axis]
    n10 --> n17
    class n17 leafNode
    n18[psi_boundary]
    n10 --> n18
    class n18 leafNode
    n19(electrons)
    n9 --> n19
    class n19 complexNode
    n20[temperature]
    n19 --> n20
    class n20 leafNode
    n21[temperature_validity]
    n19 --> n21
    class n21 leafNode
    n22(temperature_fit)
    n19 --> n22
    class n22 complexNode
    n23[measured]
    n22 --> n23
    class n23 leafNode
    n24[source]
    n22 --> n24
    class n24 leafNode
    n25[time_measurement]
    n22 --> n25
    class n25 leafNode
    n26[time_measurement_slice_method]
    n22 --> n26
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
    n30[time_measurement_width]
    n22 --> n30
    class n30 leafNode
    n31[local]
    n22 --> n31
    class n31 leafNode
    n32[rho_tor_norm]
    n22 --> n32
    class n32 leafNode
    n33[rho_pol_norm]
    n22 --> n33
    class n33 leafNode
    n34[weight]
    n22 --> n34
    class n34 leafNode
    n35[reconstructed]
    n22 --> n35
    class n35 leafNode
    n36[chi_squared]
    n22 --> n36
    class n36 leafNode
    n37[parameters]
    n22 --> n37
    class n37 leafNode
    n38[density]
    n19 --> n38
    class n38 leafNode
    n39[density_validity]
    n19 --> n39
    class n39 leafNode
    n40(density_fit)
    n19 --> n40
    class n40 complexNode
    n41[measured]
    n40 --> n41
    class n41 leafNode
    n42[source]
    n40 --> n42
    class n42 leafNode
    n43[time_measurement]
    n40 --> n43
    class n43 leafNode
    n44[time_measurement_slice_method]
    n40 --> n44
    class n44 normalNode
    n45[name]
    n44 --> n45
    class n45 leafNode
    n46[index]
    n44 --> n46
    class n46 leafNode
    n47[description]
    n44 --> n47
    class n47 leafNode
    n48[time_measurement_width]
    n40 --> n48
    class n48 leafNode
    n49[local]
    n40 --> n49
    class n49 leafNode
    n50[rho_tor_norm]
    n40 --> n50
    class n50 leafNode
    n51[rho_pol_norm]
    n40 --> n51
    class n51 leafNode
    n52[weight]
    n40 --> n52
    class n52 leafNode
    n53[reconstructed]
    n40 --> n53
    class n53 leafNode
    n54[chi_squared]
    n40 --> n54
    class n54 leafNode
    n55[parameters]
    n40 --> n55
    class n55 leafNode
    n56[density_thermal]
    n19 --> n56
    class n56 leafNode
    n57[density_fast]
    n19 --> n57
    class n57 leafNode
    n58[pressure]
    n19 --> n58
    class n58 leafNode
    n59[pressure_thermal]
    n19 --> n59
    class n59 leafNode
    n60[pressure_fast_perpendicular]
    n19 --> n60
    class n60 leafNode
    n61[pressure_fast_parallel]
    n19 --> n61
    class n61 leafNode
    n62[collisionality_norm]
    n19 --> n62
    class n62 leafNode
    n63(ion)
    n9 --> n63
    class n63 complexNode
    n64[element]
    n63 --> n64
    class n64 normalNode
    n65[a]
    n64 --> n65
    class n65 leafNode
    n66[z_n]
    n64 --> n66
    class n66 leafNode
    n67[atoms_n]
    n64 --> n67
    class n67 leafNode
    n68[z_ion]
    n63 --> n68
    class n68 leafNode
    n69[name]
    n63 --> n69
    class n69 leafNode
    n70[neutral_index]
    n63 --> n70
    class n70 leafNode
    n71[z_ion_1d]
    n63 --> n71
    class n71 leafNode
    n72[z_ion_square_1d]
    n63 --> n72
    class n72 leafNode
    n73[temperature]
    n63 --> n73
    class n73 leafNode
    n74[temperature_validity]
    n63 --> n74
    class n74 leafNode
    n75(temperature_fit)
    n63 --> n75
    class n75 complexNode
    n76[measured]
    n75 --> n76
    class n76 leafNode
    n77[source]
    n75 --> n77
    class n77 leafNode
    n78[time_measurement]
    n75 --> n78
    class n78 leafNode
    n79[time_measurement_slice_method]
    n75 --> n79
    class n79 normalNode
    n80[name]
    n79 --> n80
    class n80 leafNode
    n81[index]
    n79 --> n81
    class n81 leafNode
    n82[description]
    n79 --> n82
    class n82 leafNode
    n83[time_measurement_width]
    n75 --> n83
    class n83 leafNode
    n84[local]
    n75 --> n84
    class n84 leafNode
    n85[rho_tor_norm]
    n75 --> n85
    class n85 leafNode
    n86[rho_pol_norm]
    n75 --> n86
    class n86 leafNode
    n87[weight]
    n75 --> n87
    class n87 leafNode
    n88[reconstructed]
    n75 --> n88
    class n88 leafNode
    n89[chi_squared]
    n75 --> n89
    class n89 leafNode
    n90[parameters]
    n75 --> n90
    class n90 leafNode
    n91[density]
    n63 --> n91
    class n91 leafNode
    n92[density_validity]
    n63 --> n92
    class n92 leafNode
    n93(density_fit)
    n63 --> n93
    class n93 complexNode
    n94[measured]
    n93 --> n94
    class n94 leafNode
    n95[source]
    n93 --> n95
    class n95 leafNode
    n96[time_measurement]
    n93 --> n96
    class n96 leafNode
    n97[time_measurement_slice_method]
    n93 --> n97
    class n97 normalNode
    n98[name]
    n97 --> n98
    class n98 leafNode
    n99[index]
    n97 --> n99
    class n99 leafNode
    n100[description]
    n97 --> n100
    class n100 leafNode
    n101[time_measurement_width]
    n93 --> n101
    class n101 leafNode
    n102[local]
    n93 --> n102
    class n102 leafNode
    n103[rho_tor_norm]
    n93 --> n103
    class n103 leafNode
    n104[rho_pol_norm]
    n93 --> n104
    class n104 leafNode
    n105[weight]
    n93 --> n105
    class n105 leafNode
    n106[reconstructed]
    n93 --> n106
    class n106 leafNode
    n107[chi_squared]
    n93 --> n107
    class n107 leafNode
    n108[parameters]
    n93 --> n108
    class n108 leafNode
    n109[density_thermal]
    n63 --> n109
    class n109 leafNode
    n110[density_fast]
    n63 --> n110
    class n110 leafNode
    n111[pressure]
    n63 --> n111
    class n111 leafNode
    n112[pressure_thermal]
    n63 --> n112
    class n112 leafNode
    n113[pressure_fast_perpendicular]
    n63 --> n113
    class n113 leafNode
    n114[pressure_fast_parallel]
    n63 --> n114
    class n114 leafNode
    n115[rotation_frequency_tor]
    n63 --> n115
    class n115 leafNode
    n116[velocity]
    n63 --> n116
    class n116 normalNode
    n117[radial]
    n116 --> n117
    class n117 leafNode
    n118[diamagnetic]
    n116 --> n118
    class n118 leafNode
    n119[parallel]
    n116 --> n119
    class n119 leafNode
    n120[poloidal]
    n116 --> n120
    class n120 leafNode
    n121[toroidal]
    n116 --> n121
    class n121 leafNode
    n122[multiple_states_flag]
    n63 --> n122
    class n122 leafNode
    n123(state)
    n63 --> n123
    class n123 complexNode
    n124[z_min]
    n123 --> n124
    class n124 leafNode
    n125[z_max]
    n123 --> n125
    class n125 leafNode
    n126[z_average]
    n123 --> n126
    class n126 leafNode
    n127[z_square_average]
    n123 --> n127
    class n127 leafNode
    n128[z_average_1d]
    n123 --> n128
    class n128 leafNode
    n129[z_average_square_1d]
    n123 --> n129
    class n129 leafNode
    n130[ionization_potential]
    n123 --> n130
    class n130 leafNode
    n131[name]
    n123 --> n131
    class n131 leafNode
    n132[electron_configuration]
    n123 --> n132
    class n132 leafNode
    n133[vibrational_level]
    n123 --> n133
    class n133 leafNode
    n134[vibrational_mode]
    n123 --> n134
    class n134 leafNode
    n135[rotation_frequency_tor]
    n123 --> n135
    class n135 leafNode
    n136[temperature]
    n123 --> n136
    class n136 leafNode
    n137[density]
    n123 --> n137
    class n137 leafNode
    n138(density_fit)
    n123 --> n138
    class n138 complexNode
    n139[measured]
    n138 --> n139
    class n139 leafNode
    n140[source]
    n138 --> n140
    class n140 leafNode
    n141[time_measurement]
    n138 --> n141
    class n141 leafNode
    n142[time_measurement_slice_method]
    n138 --> n142
    class n142 normalNode
    n143[name]
    n142 --> n143
    class n143 leafNode
    n144[index]
    n142 --> n144
    class n144 leafNode
    n145[description]
    n142 --> n145
    class n145 leafNode
    n146[time_measurement_width]
    n138 --> n146
    class n146 leafNode
    n147[local]
    n138 --> n147
    class n147 leafNode
    n148[rho_tor_norm]
    n138 --> n148
    class n148 leafNode
    n149[rho_pol_norm]
    n138 --> n149
    class n149 leafNode
    n150[weight]
    n138 --> n150
    class n150 leafNode
    n151[reconstructed]
    n138 --> n151
    class n151 leafNode
    n152[chi_squared]
    n138 --> n152
    class n152 leafNode
    n153[parameters]
    n138 --> n153
    class n153 leafNode
    n154[density_thermal]
    n123 --> n154
    class n154 leafNode
    n155[density_fast]
    n123 --> n155
    class n155 leafNode
    n156[pressure]
    n123 --> n156
    class n156 leafNode
    n157[pressure_thermal]
    n123 --> n157
    class n157 leafNode
    n158[pressure_fast_perpendicular]
    n123 --> n158
    class n158 leafNode
    n159[pressure_fast_parallel]
    n123 --> n159
    class n159 leafNode
    n160(neutral)
    n9 --> n160
    class n160 complexNode
    n161[element]
    n160 --> n161
    class n161 normalNode
    n162[a]
    n161 --> n162
    class n162 leafNode
    n163[z_n]
    n161 --> n163
    class n163 leafNode
    n164[atoms_n]
    n161 --> n164
    class n164 leafNode
    n165[name]
    n160 --> n165
    class n165 leafNode
    n166[ion_index]
    n160 --> n166
    class n166 leafNode
    n167[temperature]
    n160 --> n167
    class n167 leafNode
    n168[density]
    n160 --> n168
    class n168 leafNode
    n169[density_thermal]
    n160 --> n169
    class n169 leafNode
    n170[density_fast]
    n160 --> n170
    class n170 leafNode
    n171[pressure]
    n160 --> n171
    class n171 leafNode
    n172[pressure_thermal]
    n160 --> n172
    class n172 leafNode
    n173[pressure_fast_perpendicular]
    n160 --> n173
    class n173 leafNode
    n174[pressure_fast_parallel]
    n160 --> n174
    class n174 leafNode
    n175[multiple_states_flag]
    n160 --> n175
    class n175 leafNode
    n176(state)
    n160 --> n176
    class n176 complexNode
    n177[name]
    n176 --> n177
    class n177 leafNode
    n178[electron_configuration]
    n176 --> n178
    class n178 leafNode
    n179[vibrational_level]
    n176 --> n179
    class n179 leafNode
    n180[vibrational_mode]
    n176 --> n180
    class n180 leafNode
    n181[neutral_type]
    n176 --> n181
    class n181 normalNode
    n182[name]
    n181 --> n182
    class n182 leafNode
    n183[index]
    n181 --> n183
    class n183 leafNode
    n184[description]
    n181 --> n184
    class n184 leafNode
    n185[temperature]
    n176 --> n185
    class n185 leafNode
    n186[density]
    n176 --> n186
    class n186 leafNode
    n187[density_thermal]
    n176 --> n187
    class n187 leafNode
    n188[density_fast]
    n176 --> n188
    class n188 leafNode
    n189[pressure]
    n176 --> n189
    class n189 leafNode
    n190[pressure_thermal]
    n176 --> n190
    class n190 leafNode
    n191[pressure_fast_perpendicular]
    n176 --> n191
    class n191 leafNode
    n192[pressure_fast_parallel]
    n176 --> n192
    class n192 leafNode
    n193[t_i_average]
    n9 --> n193
    class n193 leafNode
    n194(t_i_average_fit)
    n9 --> n194
    class n194 complexNode
    n195[measured]
    n194 --> n195
    class n195 leafNode
    n196[source]
    n194 --> n196
    class n196 leafNode
    n197[time_measurement]
    n194 --> n197
    class n197 leafNode
    n198[time_measurement_slice_method]
    n194 --> n198
    class n198 normalNode
    n199[name]
    n198 --> n199
    class n199 leafNode
    n200[index]
    n198 --> n200
    class n200 leafNode
    n201[description]
    n198 --> n201
    class n201 leafNode
    n202[time_measurement_width]
    n194 --> n202
    class n202 leafNode
    n203[local]
    n194 --> n203
    class n203 leafNode
    n204[rho_tor_norm]
    n194 --> n204
    class n204 leafNode
    n205[rho_pol_norm]
    n194 --> n205
    class n205 leafNode
    n206[weight]
    n194 --> n206
    class n206 leafNode
    n207[reconstructed]
    n194 --> n207
    class n207 leafNode
    n208[chi_squared]
    n194 --> n208
    class n208 leafNode
    n209[parameters]
    n194 --> n209
    class n209 leafNode
    n210[n_i_total_over_n_e]
    n9 --> n210
    class n210 leafNode
    n211[n_i_thermal_total]
    n9 --> n211
    class n211 leafNode
    n212[momentum_phi]
    n9 --> n212
    class n212 leafNode
    n213[zeff]
    n9 --> n213
    class n213 leafNode
    n214(zeff_fit)
    n9 --> n214
    class n214 complexNode
    n215[measured]
    n214 --> n215
    class n215 leafNode
    n216[source]
    n214 --> n216
    class n216 leafNode
    n217[time_measurement]
    n214 --> n217
    class n217 leafNode
    n218[time_measurement_slice_method]
    n214 --> n218
    class n218 normalNode
    n219[name]
    n218 --> n219
    class n219 leafNode
    n220[index]
    n218 --> n220
    class n220 leafNode
    n221[description]
    n218 --> n221
    class n221 leafNode
    n222[time_measurement_width]
    n214 --> n222
    class n222 leafNode
    n223[local]
    n214 --> n223
    class n223 leafNode
    n224[rho_tor_norm]
    n214 --> n224
    class n224 leafNode
    n225[rho_pol_norm]
    n214 --> n225
    class n225 leafNode
    n226[weight]
    n214 --> n226
    class n226 leafNode
    n227[reconstructed]
    n214 --> n227
    class n227 leafNode
    n228[chi_squared]
    n214 --> n228
    class n228 leafNode
    n229[parameters]
    n214 --> n229
    class n229 leafNode
    n230[pressure_ion_total]
    n9 --> n230
    class n230 leafNode
    n231[pressure_thermal]
    n9 --> n231
    class n231 leafNode
    n232[pressure_perpendicular]
    n9 --> n232
    class n232 leafNode
    n233[pressure_parallel]
    n9 --> n233
    class n233 leafNode
    n234[j_total]
    n9 --> n234
    class n234 leafNode
    n235[current_parallel_inside]
    n9 --> n235
    class n235 leafNode
    n236[j_phi]
    n9 --> n236
    class n236 leafNode
    n237[j_ohmic]
    n9 --> n237
    class n237 leafNode
    n238[j_non_inductive]
    n9 --> n238
    class n238 leafNode
    n239[j_bootstrap]
    n9 --> n239
    class n239 leafNode
    n240[conductivity_parallel]
    n9 --> n240
    class n240 leafNode
    n241[e_field]
    n9 --> n241
    class n241 normalNode
    n242[radial]
    n241 --> n242
    class n242 leafNode
    n243[diamagnetic]
    n241 --> n243
    class n243 leafNode
    n244[parallel]
    n241 --> n244
    class n244 leafNode
    n245[poloidal]
    n241 --> n245
    class n245 leafNode
    n246[toroidal]
    n241 --> n246
    class n246 leafNode
    n247[phi_potential]
    n9 --> n247
    class n247 leafNode
    n248[rotation_frequency_tor_sonic]
    n9 --> n248
    class n248 leafNode
    n249[q]
    n9 --> n249
    class n249 leafNode
    n250[magnetic_shear]
    n9 --> n250
    class n250 leafNode
    n251[time]
    n9 --> n251
    class n251 leafNode
    n252[grid_ggd]
    n1 --> n252
    class n252 normalNode
    n253[identifier]
    n252 --> n253
    class n253 normalNode
    n254[name]
    n253 --> n254
    class n254 leafNode
    n255[index]
    n253 --> n255
    class n255 leafNode
    n256[description]
    n253 --> n256
    class n256 leafNode
    n257[path]
    n252 --> n257
    class n257 leafNode
    n258[space]
    n252 --> n258
    class n258 normalNode
    n259[identifier]
    n258 --> n259
    class n259 normalNode
    n260[name]
    n259 --> n260
    class n260 leafNode
    n261[index]
    n259 --> n261
    class n261 leafNode
    n262[description]
    n259 --> n262
    class n262 leafNode
    n263[geometry_type]
    n258 --> n263
    class n263 normalNode
    n264[name]
    n263 --> n264
    class n264 leafNode
    n265[index]
    n263 --> n265
    class n265 leafNode
    n266[description]
    n263 --> n266
    class n266 leafNode
    n267[coordinates_type]
    n258 --> n267
    class n267 normalNode
    n268[name]
    n267 --> n268
    class n268 leafNode
    n269[index]
    n267 --> n269
    class n269 leafNode
    n270[description]
    n267 --> n270
    class n270 leafNode
    n271[objects_per_dimension]
    n258 --> n271
    class n271 normalNode
    n272[object]
    n271 --> n272
    class n272 normalNode
    n273[boundary]
    n272 --> n273
    class n273 normalNode
    n274[index]
    n273 --> n274
    class n274 leafNode
    n275[neighbours]
    n273 --> n275
    class n275 leafNode
    n276[geometry]
    n272 --> n276
    class n276 leafNode
    n277[nodes]
    n272 --> n277
    class n277 leafNode
    n278[measure]
    n272 --> n278
    class n278 leafNode
    n279[geometry_2d]
    n272 --> n279
    class n279 leafNode
    n280[geometry_content]
    n271 --> n280
    class n280 normalNode
    n281[name]
    n280 --> n281
    class n281 leafNode
    n282[index]
    n280 --> n282
    class n282 leafNode
    n283[description]
    n280 --> n283
    class n283 leafNode
    n284[grid_subset]
    n252 --> n284
    class n284 normalNode
    n285[identifier]
    n284 --> n285
    class n285 normalNode
    n286[name]
    n285 --> n286
    class n286 leafNode
    n287[index]
    n285 --> n287
    class n287 leafNode
    n288[description]
    n285 --> n288
    class n288 leafNode
    n289[dimension]
    n284 --> n289
    class n289 leafNode
    n290[element]
    n284 --> n290
    class n290 normalNode
    n291[object]
    n290 --> n291
    class n291 normalNode
    n292[space]
    n291 --> n292
    class n292 leafNode
    n293[dimension]
    n291 --> n293
    class n293 leafNode
    n294[index]
    n291 --> n294
    class n294 leafNode
    n295[base]
    n284 --> n295
    class n295 normalNode
    n296[jacobian]
    n295 --> n296
    class n296 leafNode
    n297[tensor_covariant]
    n295 --> n297
    class n297 leafNode
    n298[tensor_contravariant]
    n295 --> n298
    class n298 leafNode
    n299[metric]
    n284 --> n299
    class n299 normalNode
    n300[jacobian]
    n299 --> n300
    class n300 leafNode
    n301[tensor_covariant]
    n299 --> n301
    class n301 leafNode
    n302[tensor_contravariant]
    n299 --> n302
    class n302 leafNode
    n303[time]
    n252 --> n303
    class n303 leafNode
    n304[ggd_fast]
    n1 --> n304
    class n304 normalNode
    n305[electrons]
    n304 --> n305
    class n305 normalNode
    n306[temperature]
    n305 --> n306
    class n306 normalNode
    n307[grid_index]
    n306 --> n307
    class n307 leafNode
    n308[grid_subset_index]
    n306 --> n308
    class n308 leafNode
    n309[value]
    n306 --> n309
    class n309 leafNode
    n310[density]
    n305 --> n310
    class n310 normalNode
    n311[grid_index]
    n310 --> n311
    class n311 leafNode
    n312[grid_subset_index]
    n310 --> n312
    class n312 leafNode
    n313[value]
    n310 --> n313
    class n313 leafNode
    n314(ion)
    n304 --> n314
    class n314 complexNode
    n315[element]
    n314 --> n315
    class n315 normalNode
    n316[a]
    n315 --> n316
    class n316 leafNode
    n317[z_n]
    n315 --> n317
    class n317 leafNode
    n318[atoms_n]
    n315 --> n318
    class n318 leafNode
    n319[z_ion]
    n314 --> n319
    class n319 leafNode
    n320[name]
    n314 --> n320
    class n320 leafNode
    n321[neutral_index]
    n314 --> n321
    class n321 leafNode
    n322[content]
    n314 --> n322
    class n322 normalNode
    n323[grid_index]
    n322 --> n323
    class n323 leafNode
    n324[grid_subset_index]
    n322 --> n324
    class n324 leafNode
    n325[value]
    n322 --> n325
    class n325 leafNode
    n326[temperature]
    n314 --> n326
    class n326 normalNode
    n327[grid_index]
    n326 --> n327
    class n327 leafNode
    n328[grid_subset_index]
    n326 --> n328
    class n328 leafNode
    n329[value]
    n326 --> n329
    class n329 leafNode
    n330[density]
    n314 --> n330
    class n330 normalNode
    n331[grid_index]
    n330 --> n331
    class n331 leafNode
    n332[grid_subset_index]
    n330 --> n332
    class n332 leafNode
    n333[value]
    n330 --> n333
    class n333 leafNode
    n334[energy_thermal]
    n304 --> n334
    class n334 normalNode
    n335[grid_index]
    n334 --> n335
    class n335 leafNode
    n336[grid_subset_index]
    n334 --> n336
    class n336 leafNode
    n337[value]
    n334 --> n337
    class n337 leafNode
    n338[time]
    n304 --> n338
    class n338 leafNode
    n339[statistics]
    n1 --> n339
    class n339 normalNode
    n340[quantity_2d]
    n339 --> n340
    class n340 normalNode
    n341[path]
    n340 --> n341
    class n341 leafNode
    n342[statistics_type]
    n340 --> n342
    class n342 normalNode
    n343[identifier]
    n342 --> n343
    class n343 normalNode
    n344[name]
    n343 --> n344
    class n344 leafNode
    n345[index]
    n343 --> n345
    class n345 leafNode
    n346[description]
    n343 --> n346
    class n346 leafNode
    n347[value]
    n342 --> n347
    class n347 leafNode
    n348[grid_subset_index]
    n342 --> n348
    class n348 leafNode
    n349[grid_index]
    n342 --> n349
    class n349 leafNode
    n350[uq_input_path]
    n342 --> n350
    class n350 leafNode
    n351[distribution]
    n340 --> n351
    class n351 normalNode
    n352[bins]
    n351 --> n352
    class n352 leafNode
    n353[probability]
    n351 --> n353
    class n353 leafNode
    n354[uq_input_2d]
    n339 --> n354
    class n354 normalNode
    n355[path]
    n354 --> n355
    class n355 leafNode
    n356[distribution]
    n354 --> n356
    class n356 normalNode
    n357[bins]
    n356 --> n357
    class n357 leafNode
    n358[probability]
    n356 --> n358
    class n358 leafNode
    n359[time_width]
    n339 --> n359
    class n359 leafNode
    n360[time]
    n339 --> n360
    class n360 leafNode
    n361[time]
    n1 --> n361
    class n361 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```