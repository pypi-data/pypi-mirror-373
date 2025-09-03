```mermaid
flowchart TD
    root["equilibrium IDS"]

    n1[equilibrium]
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
    n5(time_slice)
    n1 --> n5
    class n5 complexNode
    n6(boundary)
    n5 --> n6
    class n6 complexNode
    n7[type]
    n6 --> n7
    class n7 leafNode
    n8[outline]
    n6 --> n8
    class n8 normalNode
    n9[r]
    n8 --> n9
    class n9 leafNode
    n10[z]
    n8 --> n10
    class n10 leafNode
    n11[psi_norm]
    n6 --> n11
    class n11 leafNode
    n12[psi]
    n6 --> n12
    class n12 leafNode
    n13[geometric_axis]
    n6 --> n13
    class n13 normalNode
    n14[r]
    n13 --> n14
    class n14 leafNode
    n15[z]
    n13 --> n15
    class n15 leafNode
    n16[minor_radius]
    n6 --> n16
    class n16 leafNode
    n17[elongation]
    n6 --> n17
    class n17 leafNode
    n18[triangularity]
    n6 --> n18
    class n18 leafNode
    n19[triangularity_upper]
    n6 --> n19
    class n19 leafNode
    n20[triangularity_lower]
    n6 --> n20
    class n20 leafNode
    n21[squareness_upper_inner]
    n6 --> n21
    class n21 leafNode
    n22[squareness_upper_outer]
    n6 --> n22
    class n22 leafNode
    n23[squareness_lower_inner]
    n6 --> n23
    class n23 leafNode
    n24[squareness_lower_outer]
    n6 --> n24
    class n24 leafNode
    n25[closest_wall_point]
    n6 --> n25
    class n25 normalNode
    n26[r]
    n25 --> n26
    class n26 leafNode
    n27[z]
    n25 --> n27
    class n27 leafNode
    n28[distance]
    n25 --> n28
    class n28 leafNode
    n29[dr_dz_zero_point]
    n6 --> n29
    class n29 normalNode
    n30[r]
    n29 --> n30
    class n30 leafNode
    n31[z]
    n29 --> n31
    class n31 leafNode
    n32(gap)
    n6 --> n32
    class n32 complexNode
    n33[name]
    n32 --> n33
    class n33 leafNode
    n34[description]
    n32 --> n34
    class n34 leafNode
    n35[r]
    n32 --> n35
    class n35 leafNode
    n36[z]
    n32 --> n36
    class n36 leafNode
    n37[angle]
    n32 --> n37
    class n37 leafNode
    n38[value]
    n32 --> n38
    class n38 leafNode
    n39[rho_tor]
    n6 --> n39
    class n39 leafNode
    n40[phi]
    n6 --> n40
    class n40 leafNode
    n41[phi_poloidal_current]
    n6 --> n41
    class n41 leafNode
    n42[contour_tree]
    n5 --> n42
    class n42 normalNode
    n43[node]
    n42 --> n43
    class n43 normalNode
    n44[critical_type]
    n43 --> n44
    class n44 leafNode
    n45[r]
    n43 --> n45
    class n45 leafNode
    n46[z]
    n43 --> n46
    class n46 leafNode
    n47[psi]
    n43 --> n47
    class n47 leafNode
    n48[levelset]
    n43 --> n48
    class n48 normalNode
    n49[r]
    n48 --> n49
    class n49 leafNode
    n50[z]
    n48 --> n50
    class n50 leafNode
    n51[edges]
    n42 --> n51
    class n51 leafNode
    n52(constraints)
    n5 --> n52
    class n52 complexNode
    n53(b_field_tor_vacuum_r)
    n52 --> n53
    class n53 complexNode
    n54[measured]
    n53 --> n54
    class n54 leafNode
    n55[source]
    n53 --> n55
    class n55 leafNode
    n56[time_measurement]
    n53 --> n56
    class n56 leafNode
    n57[exact]
    n53 --> n57
    class n57 leafNode
    n58[weight]
    n53 --> n58
    class n58 leafNode
    n59[reconstructed]
    n53 --> n59
    class n59 leafNode
    n60[chi_squared]
    n53 --> n60
    class n60 leafNode
    n61(b_field_pol_probe)
    n52 --> n61
    class n61 complexNode
    n62[measured]
    n61 --> n62
    class n62 leafNode
    n63[source]
    n61 --> n63
    class n63 leafNode
    n64[time_measurement]
    n61 --> n64
    class n64 leafNode
    n65[exact]
    n61 --> n65
    class n65 leafNode
    n66[weight]
    n61 --> n66
    class n66 leafNode
    n67[reconstructed]
    n61 --> n67
    class n67 leafNode
    n68[chi_squared]
    n61 --> n68
    class n68 leafNode
    n69(diamagnetic_flux)
    n52 --> n69
    class n69 complexNode
    n70[measured]
    n69 --> n70
    class n70 leafNode
    n71[source]
    n69 --> n71
    class n71 leafNode
    n72[time_measurement]
    n69 --> n72
    class n72 leafNode
    n73[exact]
    n69 --> n73
    class n73 leafNode
    n74[weight]
    n69 --> n74
    class n74 leafNode
    n75[reconstructed]
    n69 --> n75
    class n75 leafNode
    n76[chi_squared]
    n69 --> n76
    class n76 leafNode
    n77(faraday_angle)
    n52 --> n77
    class n77 complexNode
    n78[measured]
    n77 --> n78
    class n78 leafNode
    n79[source]
    n77 --> n79
    class n79 leafNode
    n80[time_measurement]
    n77 --> n80
    class n80 leafNode
    n81[exact]
    n77 --> n81
    class n81 leafNode
    n82[weight]
    n77 --> n82
    class n82 leafNode
    n83[reconstructed]
    n77 --> n83
    class n83 leafNode
    n84[chi_squared]
    n77 --> n84
    class n84 leafNode
    n85(mse_polarization_angle)
    n52 --> n85
    class n85 complexNode
    n86[measured]
    n85 --> n86
    class n86 leafNode
    n87[source]
    n85 --> n87
    class n87 leafNode
    n88[time_measurement]
    n85 --> n88
    class n88 leafNode
    n89[exact]
    n85 --> n89
    class n89 leafNode
    n90[weight]
    n85 --> n90
    class n90 leafNode
    n91[reconstructed]
    n85 --> n91
    class n91 leafNode
    n92[chi_squared]
    n85 --> n92
    class n92 leafNode
    n93(flux_loop)
    n52 --> n93
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
    n97[exact]
    n93 --> n97
    class n97 leafNode
    n98[weight]
    n93 --> n98
    class n98 leafNode
    n99[reconstructed]
    n93 --> n99
    class n99 leafNode
    n100[chi_squared]
    n93 --> n100
    class n100 leafNode
    n101(ip)
    n52 --> n101
    class n101 complexNode
    n102[measured]
    n101 --> n102
    class n102 leafNode
    n103[source]
    n101 --> n103
    class n103 leafNode
    n104[time_measurement]
    n101 --> n104
    class n104 leafNode
    n105[exact]
    n101 --> n105
    class n105 leafNode
    n106[weight]
    n101 --> n106
    class n106 leafNode
    n107[reconstructed]
    n101 --> n107
    class n107 leafNode
    n108[chi_squared]
    n101 --> n108
    class n108 leafNode
    n109[iron_core_segment]
    n52 --> n109
    class n109 normalNode
    n110(magnetization_r)
    n109 --> n110
    class n110 complexNode
    n111[measured]
    n110 --> n111
    class n111 leafNode
    n112[source]
    n110 --> n112
    class n112 leafNode
    n113[time_measurement]
    n110 --> n113
    class n113 leafNode
    n114[exact]
    n110 --> n114
    class n114 leafNode
    n115[weight]
    n110 --> n115
    class n115 leafNode
    n116[reconstructed]
    n110 --> n116
    class n116 leafNode
    n117[chi_squared]
    n110 --> n117
    class n117 leafNode
    n118(magnetization_z)
    n109 --> n118
    class n118 complexNode
    n119[measured]
    n118 --> n119
    class n119 leafNode
    n120[source]
    n118 --> n120
    class n120 leafNode
    n121[time_measurement]
    n118 --> n121
    class n121 leafNode
    n122[exact]
    n118 --> n122
    class n122 leafNode
    n123[weight]
    n118 --> n123
    class n123 leafNode
    n124[reconstructed]
    n118 --> n124
    class n124 leafNode
    n125[chi_squared]
    n118 --> n125
    class n125 leafNode
    n126(n_e)
    n52 --> n126
    class n126 complexNode
    n127[measured]
    n126 --> n127
    class n127 leafNode
    n128[position]
    n126 --> n128
    class n128 normalNode
    n129[r]
    n128 --> n129
    class n129 leafNode
    n130[phi]
    n128 --> n130
    class n130 leafNode
    n131[z]
    n128 --> n131
    class n131 leafNode
    n132[rho_tor_norm]
    n128 --> n132
    class n132 leafNode
    n133[psi]
    n128 --> n133
    class n133 leafNode
    n134[source]
    n126 --> n134
    class n134 leafNode
    n135[time_measurement]
    n126 --> n135
    class n135 leafNode
    n136[exact]
    n126 --> n136
    class n136 leafNode
    n137[weight]
    n126 --> n137
    class n137 leafNode
    n138[reconstructed]
    n126 --> n138
    class n138 leafNode
    n139[chi_squared]
    n126 --> n139
    class n139 leafNode
    n140(n_e_line)
    n52 --> n140
    class n140 complexNode
    n141[measured]
    n140 --> n141
    class n141 leafNode
    n142[source]
    n140 --> n142
    class n142 leafNode
    n143[time_measurement]
    n140 --> n143
    class n143 leafNode
    n144[exact]
    n140 --> n144
    class n144 leafNode
    n145[weight]
    n140 --> n145
    class n145 leafNode
    n146[reconstructed]
    n140 --> n146
    class n146 leafNode
    n147[chi_squared]
    n140 --> n147
    class n147 leafNode
    n148(pf_current)
    n52 --> n148
    class n148 complexNode
    n149[measured]
    n148 --> n149
    class n149 leafNode
    n150[source]
    n148 --> n150
    class n150 leafNode
    n151[time_measurement]
    n148 --> n151
    class n151 leafNode
    n152[exact]
    n148 --> n152
    class n152 leafNode
    n153[weight]
    n148 --> n153
    class n153 leafNode
    n154[reconstructed]
    n148 --> n154
    class n154 leafNode
    n155[chi_squared]
    n148 --> n155
    class n155 leafNode
    n156(pf_passive_current)
    n52 --> n156
    class n156 complexNode
    n157[measured]
    n156 --> n157
    class n157 leafNode
    n158[source]
    n156 --> n158
    class n158 leafNode
    n159[time_measurement]
    n156 --> n159
    class n159 leafNode
    n160[exact]
    n156 --> n160
    class n160 leafNode
    n161[weight]
    n156 --> n161
    class n161 leafNode
    n162[reconstructed]
    n156 --> n162
    class n162 leafNode
    n163[chi_squared]
    n156 --> n163
    class n163 leafNode
    n164(pressure)
    n52 --> n164
    class n164 complexNode
    n165[measured]
    n164 --> n165
    class n165 leafNode
    n166[position]
    n164 --> n166
    class n166 normalNode
    n167[r]
    n166 --> n167
    class n167 leafNode
    n168[phi]
    n166 --> n168
    class n168 leafNode
    n169[z]
    n166 --> n169
    class n169 leafNode
    n170[rho_tor_norm]
    n166 --> n170
    class n170 leafNode
    n171[psi]
    n166 --> n171
    class n171 leafNode
    n172[source]
    n164 --> n172
    class n172 leafNode
    n173[time_measurement]
    n164 --> n173
    class n173 leafNode
    n174[exact]
    n164 --> n174
    class n174 leafNode
    n175[weight]
    n164 --> n175
    class n175 leafNode
    n176[reconstructed]
    n164 --> n176
    class n176 leafNode
    n177[chi_squared]
    n164 --> n177
    class n177 leafNode
    n178(pressure_rotational)
    n52 --> n178
    class n178 complexNode
    n179[measured]
    n178 --> n179
    class n179 leafNode
    n180[position]
    n178 --> n180
    class n180 normalNode
    n181[r]
    n180 --> n181
    class n181 leafNode
    n182[phi]
    n180 --> n182
    class n182 leafNode
    n183[z]
    n180 --> n183
    class n183 leafNode
    n184[rho_tor_norm]
    n180 --> n184
    class n184 leafNode
    n185[psi]
    n180 --> n185
    class n185 leafNode
    n186[source]
    n178 --> n186
    class n186 leafNode
    n187[time_measurement]
    n178 --> n187
    class n187 leafNode
    n188[exact]
    n178 --> n188
    class n188 leafNode
    n189[weight]
    n178 --> n189
    class n189 leafNode
    n190[reconstructed]
    n178 --> n190
    class n190 leafNode
    n191[chi_squared]
    n178 --> n191
    class n191 leafNode
    n192(q)
    n52 --> n192
    class n192 complexNode
    n193[measured]
    n192 --> n193
    class n193 leafNode
    n194[position]
    n192 --> n194
    class n194 normalNode
    n195[r]
    n194 --> n195
    class n195 leafNode
    n196[phi]
    n194 --> n196
    class n196 leafNode
    n197[z]
    n194 --> n197
    class n197 leafNode
    n198[rho_tor_norm]
    n194 --> n198
    class n198 leafNode
    n199[psi]
    n194 --> n199
    class n199 leafNode
    n200[source]
    n192 --> n200
    class n200 leafNode
    n201[time_measurement]
    n192 --> n201
    class n201 leafNode
    n202[exact]
    n192 --> n202
    class n202 leafNode
    n203[weight]
    n192 --> n203
    class n203 leafNode
    n204[reconstructed]
    n192 --> n204
    class n204 leafNode
    n205[chi_squared]
    n192 --> n205
    class n205 leafNode
    n206(j_phi)
    n52 --> n206
    class n206 complexNode
    n207[measured]
    n206 --> n207
    class n207 leafNode
    n208[position]
    n206 --> n208
    class n208 normalNode
    n209[r]
    n208 --> n209
    class n209 leafNode
    n210[phi]
    n208 --> n210
    class n210 leafNode
    n211[z]
    n208 --> n211
    class n211 leafNode
    n212[rho_tor_norm]
    n208 --> n212
    class n212 leafNode
    n213[psi]
    n208 --> n213
    class n213 leafNode
    n214[source]
    n206 --> n214
    class n214 leafNode
    n215[time_measurement]
    n206 --> n215
    class n215 leafNode
    n216[exact]
    n206 --> n216
    class n216 leafNode
    n217[weight]
    n206 --> n217
    class n217 leafNode
    n218[reconstructed]
    n206 --> n218
    class n218 leafNode
    n219[chi_squared]
    n206 --> n219
    class n219 leafNode
    n220(j_parallel)
    n52 --> n220
    class n220 complexNode
    n221[measured]
    n220 --> n221
    class n221 leafNode
    n222[position]
    n220 --> n222
    class n222 normalNode
    n223[r]
    n222 --> n223
    class n223 leafNode
    n224[phi]
    n222 --> n224
    class n224 leafNode
    n225[z]
    n222 --> n225
    class n225 leafNode
    n226[rho_tor_norm]
    n222 --> n226
    class n226 leafNode
    n227[psi]
    n222 --> n227
    class n227 leafNode
    n228[source]
    n220 --> n228
    class n228 leafNode
    n229[time_measurement]
    n220 --> n229
    class n229 leafNode
    n230[exact]
    n220 --> n230
    class n230 leafNode
    n231[weight]
    n220 --> n231
    class n231 leafNode
    n232[reconstructed]
    n220 --> n232
    class n232 leafNode
    n233[chi_squared]
    n220 --> n233
    class n233 leafNode
    n234(x_point)
    n52 --> n234
    class n234 complexNode
    n235[position_measured]
    n234 --> n235
    class n235 normalNode
    n236[r]
    n235 --> n236
    class n236 leafNode
    n237[z]
    n235 --> n237
    class n237 leafNode
    n238[source]
    n234 --> n238
    class n238 leafNode
    n239[time_measurement]
    n234 --> n239
    class n239 leafNode
    n240[exact]
    n234 --> n240
    class n240 leafNode
    n241[weight]
    n234 --> n241
    class n241 leafNode
    n242[position_reconstructed]
    n234 --> n242
    class n242 normalNode
    n243[r]
    n242 --> n243
    class n243 leafNode
    n244[z]
    n242 --> n244
    class n244 leafNode
    n245[chi_squared_r]
    n234 --> n245
    class n245 leafNode
    n246[chi_squared_z]
    n234 --> n246
    class n246 leafNode
    n247(strike_point)
    n52 --> n247
    class n247 complexNode
    n248[position_measured]
    n247 --> n248
    class n248 normalNode
    n249[r]
    n248 --> n249
    class n249 leafNode
    n250[z]
    n248 --> n250
    class n250 leafNode
    n251[source]
    n247 --> n251
    class n251 leafNode
    n252[time_measurement]
    n247 --> n252
    class n252 leafNode
    n253[exact]
    n247 --> n253
    class n253 leafNode
    n254[weight]
    n247 --> n254
    class n254 leafNode
    n255[position_reconstructed]
    n247 --> n255
    class n255 normalNode
    n256[r]
    n255 --> n256
    class n256 leafNode
    n257[z]
    n255 --> n257
    class n257 leafNode
    n258[chi_squared_r]
    n247 --> n258
    class n258 leafNode
    n259[chi_squared_z]
    n247 --> n259
    class n259 leafNode
    n260[chi_squared_reduced]
    n52 --> n260
    class n260 leafNode
    n261[freedom_degrees_n]
    n52 --> n261
    class n261 leafNode
    n262[constraints_n]
    n52 --> n262
    class n262 leafNode
    n263(global_quantities)
    n5 --> n263
    class n263 complexNode
    n264[beta_pol]
    n263 --> n264
    class n264 leafNode
    n265[beta_tor]
    n263 --> n265
    class n265 leafNode
    n266[beta_tor_norm]
    n263 --> n266
    class n266 leafNode
    n267[ip]
    n263 --> n267
    class n267 leafNode
    n268[li_3]
    n263 --> n268
    class n268 leafNode
    n269[volume]
    n263 --> n269
    class n269 leafNode
    n270[area]
    n263 --> n270
    class n270 leafNode
    n271[surface]
    n263 --> n271
    class n271 leafNode
    n272[length_pol]
    n263 --> n272
    class n272 leafNode
    n273[psi_axis]
    n263 --> n273
    class n273 leafNode
    n274[psi_magnetic_axis]
    n263 --> n274
    class n274 leafNode
    n275[psi_boundary]
    n263 --> n275
    class n275 leafNode
    n276[rho_tor_boundary]
    n263 --> n276
    class n276 leafNode
    n277[magnetic_axis]
    n263 --> n277
    class n277 normalNode
    n278[r]
    n277 --> n278
    class n278 leafNode
    n279[z]
    n277 --> n279
    class n279 leafNode
    n280[b_field_phi]
    n277 --> n280
    class n280 leafNode
    n281[current_centre]
    n263 --> n281
    class n281 normalNode
    n282[r]
    n281 --> n282
    class n282 leafNode
    n283[z]
    n281 --> n283
    class n283 leafNode
    n284[velocity_z]
    n281 --> n284
    class n284 leafNode
    n285[q_axis]
    n263 --> n285
    class n285 leafNode
    n286[q_95]
    n263 --> n286
    class n286 leafNode
    n287[q_min]
    n263 --> n287
    class n287 normalNode
    n288[value]
    n287 --> n288
    class n288 leafNode
    n289[rho_tor_norm]
    n287 --> n289
    class n289 leafNode
    n290[psi_norm]
    n287 --> n290
    class n290 leafNode
    n291[psi]
    n287 --> n291
    class n291 leafNode
    n292[energy_mhd]
    n263 --> n292
    class n292 leafNode
    n293[psi_external_average]
    n263 --> n293
    class n293 leafNode
    n294[v_external]
    n263 --> n294
    class n294 leafNode
    n295[plasma_inductance]
    n263 --> n295
    class n295 leafNode
    n296[plasma_resistance]
    n263 --> n296
    class n296 leafNode
    n297(profiles_1d)
    n5 --> n297
    class n297 complexNode
    n298[psi]
    n297 --> n298
    class n298 leafNode
    n299[psi_norm]
    n297 --> n299
    class n299 leafNode
    n300[phi]
    n297 --> n300
    class n300 leafNode
    n301[pressure]
    n297 --> n301
    class n301 leafNode
    n302[f]
    n297 --> n302
    class n302 leafNode
    n303[dpressure_dpsi]
    n297 --> n303
    class n303 leafNode
    n304[f_df_dpsi]
    n297 --> n304
    class n304 leafNode
    n305[j_phi]
    n297 --> n305
    class n305 leafNode
    n306[j_parallel]
    n297 --> n306
    class n306 leafNode
    n307[q]
    n297 --> n307
    class n307 leafNode
    n308[magnetic_shear]
    n297 --> n308
    class n308 leafNode
    n309[r_inboard]
    n297 --> n309
    class n309 leafNode
    n310[r_outboard]
    n297 --> n310
    class n310 leafNode
    n311[rho_tor]
    n297 --> n311
    class n311 leafNode
    n312[rho_tor_norm]
    n297 --> n312
    class n312 leafNode
    n313[dpsi_drho_tor]
    n297 --> n313
    class n313 leafNode
    n314[geometric_axis]
    n297 --> n314
    class n314 normalNode
    n315[r]
    n314 --> n315
    class n315 leafNode
    n316[z]
    n314 --> n316
    class n316 leafNode
    n317[elongation]
    n297 --> n317
    class n317 leafNode
    n318[triangularity_upper]
    n297 --> n318
    class n318 leafNode
    n319[triangularity_lower]
    n297 --> n319
    class n319 leafNode
    n320[squareness_upper_inner]
    n297 --> n320
    class n320 leafNode
    n321[squareness_upper_outer]
    n297 --> n321
    class n321 leafNode
    n322[squareness_lower_inner]
    n297 --> n322
    class n322 leafNode
    n323[squareness_lower_outer]
    n297 --> n323
    class n323 leafNode
    n324[volume]
    n297 --> n324
    class n324 leafNode
    n325[rho_volume_norm]
    n297 --> n325
    class n325 leafNode
    n326[dvolume_dpsi]
    n297 --> n326
    class n326 leafNode
    n327[dvolume_drho_tor]
    n297 --> n327
    class n327 leafNode
    n328[area]
    n297 --> n328
    class n328 leafNode
    n329[darea_dpsi]
    n297 --> n329
    class n329 leafNode
    n330[darea_drho_tor]
    n297 --> n330
    class n330 leafNode
    n331[surface]
    n297 --> n331
    class n331 leafNode
    n332[trapped_fraction]
    n297 --> n332
    class n332 leafNode
    n333[gm1]
    n297 --> n333
    class n333 leafNode
    n334[gm2]
    n297 --> n334
    class n334 leafNode
    n335[gm3]
    n297 --> n335
    class n335 leafNode
    n336[gm4]
    n297 --> n336
    class n336 leafNode
    n337[gm5]
    n297 --> n337
    class n337 leafNode
    n338[gm6]
    n297 --> n338
    class n338 leafNode
    n339[gm7]
    n297 --> n339
    class n339 leafNode
    n340[gm8]
    n297 --> n340
    class n340 leafNode
    n341[gm9]
    n297 --> n341
    class n341 leafNode
    n342[b_field_average]
    n297 --> n342
    class n342 leafNode
    n343[b_field_min]
    n297 --> n343
    class n343 leafNode
    n344[b_field_max]
    n297 --> n344
    class n344 leafNode
    n345[beta_pol]
    n297 --> n345
    class n345 leafNode
    n346[mass_density]
    n297 --> n346
    class n346 leafNode
    n347(profiles_2d)
    n5 --> n347
    class n347 complexNode
    n348[type]
    n347 --> n348
    class n348 normalNode
    n349[name]
    n348 --> n349
    class n349 leafNode
    n350[index]
    n348 --> n350
    class n350 leafNode
    n351[description]
    n348 --> n351
    class n351 leafNode
    n352[grid_type]
    n347 --> n352
    class n352 normalNode
    n353[name]
    n352 --> n353
    class n353 leafNode
    n354[index]
    n352 --> n354
    class n354 leafNode
    n355[description]
    n352 --> n355
    class n355 leafNode
    n356[grid]
    n347 --> n356
    class n356 normalNode
    n357[dim1]
    n356 --> n357
    class n357 leafNode
    n358[dim2]
    n356 --> n358
    class n358 leafNode
    n359[volume_element]
    n356 --> n359
    class n359 leafNode
    n360[r]
    n347 --> n360
    class n360 leafNode
    n361[z]
    n347 --> n361
    class n361 leafNode
    n362[psi]
    n347 --> n362
    class n362 leafNode
    n363[theta]
    n347 --> n363
    class n363 leafNode
    n364[phi]
    n347 --> n364
    class n364 leafNode
    n365[j_phi]
    n347 --> n365
    class n365 leafNode
    n366[j_parallel]
    n347 --> n366
    class n366 leafNode
    n367[b_field_r]
    n347 --> n367
    class n367 leafNode
    n368[b_field_phi]
    n347 --> n368
    class n368 leafNode
    n369[b_field_z]
    n347 --> n369
    class n369 leafNode
    n370(coordinate_system)
    n5 --> n370
    class n370 complexNode
    n371[grid_type]
    n370 --> n371
    class n371 normalNode
    n372[name]
    n371 --> n372
    class n372 leafNode
    n373[index]
    n371 --> n373
    class n373 leafNode
    n374[description]
    n371 --> n374
    class n374 leafNode
    n375[grid]
    n370 --> n375
    class n375 normalNode
    n376[dim1]
    n375 --> n376
    class n376 leafNode
    n377[dim2]
    n375 --> n377
    class n377 leafNode
    n378[volume_element]
    n375 --> n378
    class n378 leafNode
    n379[r]
    n370 --> n379
    class n379 leafNode
    n380[z]
    n370 --> n380
    class n380 leafNode
    n381[jacobian]
    n370 --> n381
    class n381 leafNode
    n382[tensor_covariant]
    n370 --> n382
    class n382 leafNode
    n383[tensor_contravariant]
    n370 --> n383
    class n383 leafNode
    n384[convergence]
    n5 --> n384
    class n384 normalNode
    n385[iterations_n]
    n384 --> n385
    class n385 leafNode
    n386[grad_shafranov_deviation_expression]
    n384 --> n386
    class n386 normalNode
    n387[name]
    n386 --> n387
    class n387 leafNode
    n388[index]
    n386 --> n388
    class n388 leafNode
    n389[description]
    n386 --> n389
    class n389 leafNode
    n390[grad_shafranov_deviation_value]
    n384 --> n390
    class n390 leafNode
    n391[result]
    n384 --> n391
    class n391 normalNode
    n392[name]
    n391 --> n392
    class n392 leafNode
    n393[index]
    n391 --> n393
    class n393 leafNode
    n394[description]
    n391 --> n394
    class n394 leafNode
    n395[time]
    n5 --> n395
    class n395 leafNode
    n396[time]
    n1 --> n396
    class n396 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```