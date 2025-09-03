```mermaid
flowchart TD
    root["plasma_profiles IDS"]

    n1(plasma_profiles)
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
    n9(global_quantities)
    n1 --> n9
    class n9 complexNode
    n10[ip]
    n9 --> n10
    class n10 leafNode
    n11[current_non_inductive]
    n9 --> n11
    class n11 leafNode
    n12[current_bootstrap]
    n9 --> n12
    class n12 leafNode
    n13[v_loop]
    n9 --> n13
    class n13 leafNode
    n14[li_3]
    n9 --> n14
    class n14 leafNode
    n15[beta_tor]
    n9 --> n15
    class n15 leafNode
    n16[beta_tor_norm]
    n9 --> n16
    class n16 leafNode
    n17[beta_pol]
    n9 --> n17
    class n17 leafNode
    n18[energy_diamagnetic]
    n9 --> n18
    class n18 leafNode
    n19[z_eff_resistive]
    n9 --> n19
    class n19 leafNode
    n20[t_e_peaking]
    n9 --> n20
    class n20 leafNode
    n21[t_i_average_peaking]
    n9 --> n21
    class n21 leafNode
    n22[resistive_psi_losses]
    n9 --> n22
    class n22 leafNode
    n23[ejima]
    n9 --> n23
    class n23 leafNode
    n24[t_e_volume_average]
    n9 --> n24
    class n24 leafNode
    n25[n_e_volume_average]
    n9 --> n25
    class n25 leafNode
    n26[ion]
    n9 --> n26
    class n26 normalNode
    n27[t_i_volume_average]
    n26 --> n27
    class n27 leafNode
    n28[n_i_volume_average]
    n26 --> n28
    class n28 leafNode
    n29[ion_time_slice]
    n9 --> n29
    class n29 leafNode
    n30(profiles_1d)
    n1 --> n30
    class n30 complexNode
    n31(grid)
    n30 --> n31
    class n31 complexNode
    n32[rho_pol_norm]
    n31 --> n32
    class n32 leafNode
    n33[psi]
    n31 --> n33
    class n33 leafNode
    n34[rho_tor_norm]
    n31 --> n34
    class n34 leafNode
    n35[rho_tor]
    n31 --> n35
    class n35 leafNode
    n36[volume]
    n31 --> n36
    class n36 leafNode
    n37[area]
    n31 --> n37
    class n37 leafNode
    n38[surface]
    n31 --> n38
    class n38 leafNode
    n39[psi_magnetic_axis]
    n31 --> n39
    class n39 leafNode
    n40[psi_boundary]
    n31 --> n40
    class n40 leafNode
    n41(electrons)
    n30 --> n41
    class n41 complexNode
    n42[temperature]
    n41 --> n42
    class n42 leafNode
    n43[temperature_validity]
    n41 --> n43
    class n43 leafNode
    n44(temperature_fit)
    n41 --> n44
    class n44 complexNode
    n45[measured]
    n44 --> n45
    class n45 leafNode
    n46[source]
    n44 --> n46
    class n46 leafNode
    n47[time_measurement]
    n44 --> n47
    class n47 leafNode
    n48[time_measurement_slice_method]
    n44 --> n48
    class n48 normalNode
    n49[name]
    n48 --> n49
    class n49 leafNode
    n50[index]
    n48 --> n50
    class n50 leafNode
    n51[description]
    n48 --> n51
    class n51 leafNode
    n52[time_measurement_width]
    n44 --> n52
    class n52 leafNode
    n53[local]
    n44 --> n53
    class n53 leafNode
    n54[rho_tor_norm]
    n44 --> n54
    class n54 leafNode
    n55[rho_pol_norm]
    n44 --> n55
    class n55 leafNode
    n56[weight]
    n44 --> n56
    class n56 leafNode
    n57[reconstructed]
    n44 --> n57
    class n57 leafNode
    n58[chi_squared]
    n44 --> n58
    class n58 leafNode
    n59[parameters]
    n44 --> n59
    class n59 leafNode
    n60[density]
    n41 --> n60
    class n60 leafNode
    n61[density_validity]
    n41 --> n61
    class n61 leafNode
    n62(density_fit)
    n41 --> n62
    class n62 complexNode
    n63[measured]
    n62 --> n63
    class n63 leafNode
    n64[source]
    n62 --> n64
    class n64 leafNode
    n65[time_measurement]
    n62 --> n65
    class n65 leafNode
    n66[time_measurement_slice_method]
    n62 --> n66
    class n66 normalNode
    n67[name]
    n66 --> n67
    class n67 leafNode
    n68[index]
    n66 --> n68
    class n68 leafNode
    n69[description]
    n66 --> n69
    class n69 leafNode
    n70[time_measurement_width]
    n62 --> n70
    class n70 leafNode
    n71[local]
    n62 --> n71
    class n71 leafNode
    n72[rho_tor_norm]
    n62 --> n72
    class n72 leafNode
    n73[rho_pol_norm]
    n62 --> n73
    class n73 leafNode
    n74[weight]
    n62 --> n74
    class n74 leafNode
    n75[reconstructed]
    n62 --> n75
    class n75 leafNode
    n76[chi_squared]
    n62 --> n76
    class n76 leafNode
    n77[parameters]
    n62 --> n77
    class n77 leafNode
    n78[density_thermal]
    n41 --> n78
    class n78 leafNode
    n79[density_fast]
    n41 --> n79
    class n79 leafNode
    n80[pressure]
    n41 --> n80
    class n80 leafNode
    n81[pressure_thermal]
    n41 --> n81
    class n81 leafNode
    n82[pressure_fast_perpendicular]
    n41 --> n82
    class n82 leafNode
    n83[pressure_fast_parallel]
    n41 --> n83
    class n83 leafNode
    n84[collisionality_norm]
    n41 --> n84
    class n84 leafNode
    n85(ion)
    n30 --> n85
    class n85 complexNode
    n86[element]
    n85 --> n86
    class n86 normalNode
    n87[a]
    n86 --> n87
    class n87 leafNode
    n88[z_n]
    n86 --> n88
    class n88 leafNode
    n89[atoms_n]
    n86 --> n89
    class n89 leafNode
    n90[z_ion]
    n85 --> n90
    class n90 leafNode
    n91[name]
    n85 --> n91
    class n91 leafNode
    n92[neutral_index]
    n85 --> n92
    class n92 leafNode
    n93[z_ion_1d]
    n85 --> n93
    class n93 leafNode
    n94[z_ion_square_1d]
    n85 --> n94
    class n94 leafNode
    n95[temperature]
    n85 --> n95
    class n95 leafNode
    n96[temperature_validity]
    n85 --> n96
    class n96 leafNode
    n97(temperature_fit)
    n85 --> n97
    class n97 complexNode
    n98[measured]
    n97 --> n98
    class n98 leafNode
    n99[source]
    n97 --> n99
    class n99 leafNode
    n100[time_measurement]
    n97 --> n100
    class n100 leafNode
    n101[time_measurement_slice_method]
    n97 --> n101
    class n101 normalNode
    n102[name]
    n101 --> n102
    class n102 leafNode
    n103[index]
    n101 --> n103
    class n103 leafNode
    n104[description]
    n101 --> n104
    class n104 leafNode
    n105[time_measurement_width]
    n97 --> n105
    class n105 leafNode
    n106[local]
    n97 --> n106
    class n106 leafNode
    n107[rho_tor_norm]
    n97 --> n107
    class n107 leafNode
    n108[rho_pol_norm]
    n97 --> n108
    class n108 leafNode
    n109[weight]
    n97 --> n109
    class n109 leafNode
    n110[reconstructed]
    n97 --> n110
    class n110 leafNode
    n111[chi_squared]
    n97 --> n111
    class n111 leafNode
    n112[parameters]
    n97 --> n112
    class n112 leafNode
    n113[density]
    n85 --> n113
    class n113 leafNode
    n114[density_validity]
    n85 --> n114
    class n114 leafNode
    n115(density_fit)
    n85 --> n115
    class n115 complexNode
    n116[measured]
    n115 --> n116
    class n116 leafNode
    n117[source]
    n115 --> n117
    class n117 leafNode
    n118[time_measurement]
    n115 --> n118
    class n118 leafNode
    n119[time_measurement_slice_method]
    n115 --> n119
    class n119 normalNode
    n120[name]
    n119 --> n120
    class n120 leafNode
    n121[index]
    n119 --> n121
    class n121 leafNode
    n122[description]
    n119 --> n122
    class n122 leafNode
    n123[time_measurement_width]
    n115 --> n123
    class n123 leafNode
    n124[local]
    n115 --> n124
    class n124 leafNode
    n125[rho_tor_norm]
    n115 --> n125
    class n125 leafNode
    n126[rho_pol_norm]
    n115 --> n126
    class n126 leafNode
    n127[weight]
    n115 --> n127
    class n127 leafNode
    n128[reconstructed]
    n115 --> n128
    class n128 leafNode
    n129[chi_squared]
    n115 --> n129
    class n129 leafNode
    n130[parameters]
    n115 --> n130
    class n130 leafNode
    n131[density_thermal]
    n85 --> n131
    class n131 leafNode
    n132[density_fast]
    n85 --> n132
    class n132 leafNode
    n133[pressure]
    n85 --> n133
    class n133 leafNode
    n134[pressure_thermal]
    n85 --> n134
    class n134 leafNode
    n135[pressure_fast_perpendicular]
    n85 --> n135
    class n135 leafNode
    n136[pressure_fast_parallel]
    n85 --> n136
    class n136 leafNode
    n137[rotation_frequency_tor]
    n85 --> n137
    class n137 leafNode
    n138[velocity]
    n85 --> n138
    class n138 normalNode
    n139[radial]
    n138 --> n139
    class n139 leafNode
    n140[diamagnetic]
    n138 --> n140
    class n140 leafNode
    n141[parallel]
    n138 --> n141
    class n141 leafNode
    n142[poloidal]
    n138 --> n142
    class n142 leafNode
    n143[toroidal]
    n138 --> n143
    class n143 leafNode
    n144[multiple_states_flag]
    n85 --> n144
    class n144 leafNode
    n145(state)
    n85 --> n145
    class n145 complexNode
    n146[z_min]
    n145 --> n146
    class n146 leafNode
    n147[z_max]
    n145 --> n147
    class n147 leafNode
    n148[z_average]
    n145 --> n148
    class n148 leafNode
    n149[z_square_average]
    n145 --> n149
    class n149 leafNode
    n150[z_average_1d]
    n145 --> n150
    class n150 leafNode
    n151[z_average_square_1d]
    n145 --> n151
    class n151 leafNode
    n152[ionisation_potential]
    n145 --> n152
    class n152 leafNode
    n153[name]
    n145 --> n153
    class n153 leafNode
    n154[electron_configuration]
    n145 --> n154
    class n154 leafNode
    n155[vibrational_level]
    n145 --> n155
    class n155 leafNode
    n156[vibrational_mode]
    n145 --> n156
    class n156 leafNode
    n157[rotation_frequency_tor]
    n145 --> n157
    class n157 leafNode
    n158[velocity]
    n145 --> n158
    class n158 normalNode
    n159[radial]
    n158 --> n159
    class n159 leafNode
    n160[diamagnetic]
    n158 --> n160
    class n160 leafNode
    n161[parallel]
    n158 --> n161
    class n161 leafNode
    n162[poloidal]
    n158 --> n162
    class n162 leafNode
    n163[toroidal]
    n158 --> n163
    class n163 leafNode
    n164[temperature]
    n145 --> n164
    class n164 leafNode
    n165[density]
    n145 --> n165
    class n165 leafNode
    n166(density_fit)
    n145 --> n166
    class n166 complexNode
    n167[measured]
    n166 --> n167
    class n167 leafNode
    n168[source]
    n166 --> n168
    class n168 leafNode
    n169[time_measurement]
    n166 --> n169
    class n169 leafNode
    n170[time_measurement_slice_method]
    n166 --> n170
    class n170 normalNode
    n171[name]
    n170 --> n171
    class n171 leafNode
    n172[index]
    n170 --> n172
    class n172 leafNode
    n173[description]
    n170 --> n173
    class n173 leafNode
    n174[time_measurement_width]
    n166 --> n174
    class n174 leafNode
    n175[local]
    n166 --> n175
    class n175 leafNode
    n176[rho_tor_norm]
    n166 --> n176
    class n176 leafNode
    n177[rho_pol_norm]
    n166 --> n177
    class n177 leafNode
    n178[weight]
    n166 --> n178
    class n178 leafNode
    n179[reconstructed]
    n166 --> n179
    class n179 leafNode
    n180[chi_squared]
    n166 --> n180
    class n180 leafNode
    n181[parameters]
    n166 --> n181
    class n181 leafNode
    n182[density_thermal]
    n145 --> n182
    class n182 leafNode
    n183[density_fast]
    n145 --> n183
    class n183 leafNode
    n184[pressure]
    n145 --> n184
    class n184 leafNode
    n185[pressure_thermal]
    n145 --> n185
    class n185 leafNode
    n186[pressure_fast_perpendicular]
    n145 --> n186
    class n186 leafNode
    n187[pressure_fast_parallel]
    n145 --> n187
    class n187 leafNode
    n188(neutral)
    n30 --> n188
    class n188 complexNode
    n189[element]
    n188 --> n189
    class n189 normalNode
    n190[a]
    n189 --> n190
    class n190 leafNode
    n191[z_n]
    n189 --> n191
    class n191 leafNode
    n192[atoms_n]
    n189 --> n192
    class n192 leafNode
    n193[name]
    n188 --> n193
    class n193 leafNode
    n194[ion_index]
    n188 --> n194
    class n194 leafNode
    n195[temperature]
    n188 --> n195
    class n195 leafNode
    n196[density]
    n188 --> n196
    class n196 leafNode
    n197[density_thermal]
    n188 --> n197
    class n197 leafNode
    n198[density_fast]
    n188 --> n198
    class n198 leafNode
    n199[pressure]
    n188 --> n199
    class n199 leafNode
    n200[pressure_thermal]
    n188 --> n200
    class n200 leafNode
    n201[pressure_fast_perpendicular]
    n188 --> n201
    class n201 leafNode
    n202[pressure_fast_parallel]
    n188 --> n202
    class n202 leafNode
    n203[multiple_states_flag]
    n188 --> n203
    class n203 leafNode
    n204(state)
    n188 --> n204
    class n204 complexNode
    n205[name]
    n204 --> n205
    class n205 leafNode
    n206[electron_configuration]
    n204 --> n206
    class n206 leafNode
    n207[vibrational_level]
    n204 --> n207
    class n207 leafNode
    n208[vibrational_mode]
    n204 --> n208
    class n208 leafNode
    n209[neutral_type]
    n204 --> n209
    class n209 normalNode
    n210[name]
    n209 --> n210
    class n210 leafNode
    n211[index]
    n209 --> n211
    class n211 leafNode
    n212[description]
    n209 --> n212
    class n212 leafNode
    n213[temperature]
    n204 --> n213
    class n213 leafNode
    n214[density]
    n204 --> n214
    class n214 leafNode
    n215[density_thermal]
    n204 --> n215
    class n215 leafNode
    n216[density_fast]
    n204 --> n216
    class n216 leafNode
    n217[pressure]
    n204 --> n217
    class n217 leafNode
    n218[pressure_thermal]
    n204 --> n218
    class n218 leafNode
    n219[pressure_fast_perpendicular]
    n204 --> n219
    class n219 leafNode
    n220[pressure_fast_parallel]
    n204 --> n220
    class n220 leafNode
    n221[t_i_average]
    n30 --> n221
    class n221 leafNode
    n222(t_i_average_fit)
    n30 --> n222
    class n222 complexNode
    n223[measured]
    n222 --> n223
    class n223 leafNode
    n224[source]
    n222 --> n224
    class n224 leafNode
    n225[time_measurement]
    n222 --> n225
    class n225 leafNode
    n226[time_measurement_slice_method]
    n222 --> n226
    class n226 normalNode
    n227[name]
    n226 --> n227
    class n227 leafNode
    n228[index]
    n226 --> n228
    class n228 leafNode
    n229[description]
    n226 --> n229
    class n229 leafNode
    n230[time_measurement_width]
    n222 --> n230
    class n230 leafNode
    n231[local]
    n222 --> n231
    class n231 leafNode
    n232[rho_tor_norm]
    n222 --> n232
    class n232 leafNode
    n233[rho_pol_norm]
    n222 --> n233
    class n233 leafNode
    n234[weight]
    n222 --> n234
    class n234 leafNode
    n235[reconstructed]
    n222 --> n235
    class n235 leafNode
    n236[chi_squared]
    n222 --> n236
    class n236 leafNode
    n237[parameters]
    n222 --> n237
    class n237 leafNode
    n238[n_i_total_over_n_e]
    n30 --> n238
    class n238 leafNode
    n239[n_i_thermal_total]
    n30 --> n239
    class n239 leafNode
    n240[momentum_phi]
    n30 --> n240
    class n240 leafNode
    n241[zeff]
    n30 --> n241
    class n241 leafNode
    n242(zeff_fit)
    n30 --> n242
    class n242 complexNode
    n243[measured]
    n242 --> n243
    class n243 leafNode
    n244[source]
    n242 --> n244
    class n244 leafNode
    n245[time_measurement]
    n242 --> n245
    class n245 leafNode
    n246[time_measurement_slice_method]
    n242 --> n246
    class n246 normalNode
    n247[name]
    n246 --> n247
    class n247 leafNode
    n248[index]
    n246 --> n248
    class n248 leafNode
    n249[description]
    n246 --> n249
    class n249 leafNode
    n250[time_measurement_width]
    n242 --> n250
    class n250 leafNode
    n251[local]
    n242 --> n251
    class n251 leafNode
    n252[rho_tor_norm]
    n242 --> n252
    class n252 leafNode
    n253[rho_pol_norm]
    n242 --> n253
    class n253 leafNode
    n254[weight]
    n242 --> n254
    class n254 leafNode
    n255[reconstructed]
    n242 --> n255
    class n255 leafNode
    n256[chi_squared]
    n242 --> n256
    class n256 leafNode
    n257[parameters]
    n242 --> n257
    class n257 leafNode
    n258[pressure_ion_total]
    n30 --> n258
    class n258 leafNode
    n259[pressure_thermal]
    n30 --> n259
    class n259 leafNode
    n260[pressure_perpendicular]
    n30 --> n260
    class n260 leafNode
    n261[pressure_parallel]
    n30 --> n261
    class n261 leafNode
    n262[j_total]
    n30 --> n262
    class n262 leafNode
    n263[current_parallel_inside]
    n30 --> n263
    class n263 leafNode
    n264[j_phi]
    n30 --> n264
    class n264 leafNode
    n265[j_ohmic]
    n30 --> n265
    class n265 leafNode
    n266[j_non_inductive]
    n30 --> n266
    class n266 leafNode
    n267[j_bootstrap]
    n30 --> n267
    class n267 leafNode
    n268[conductivity_parallel]
    n30 --> n268
    class n268 leafNode
    n269[e_field]
    n30 --> n269
    class n269 normalNode
    n270[radial]
    n269 --> n270
    class n270 leafNode
    n271[diamagnetic]
    n269 --> n271
    class n271 leafNode
    n272[parallel]
    n269 --> n272
    class n272 leafNode
    n273[poloidal]
    n269 --> n273
    class n273 leafNode
    n274[toroidal]
    n269 --> n274
    class n274 leafNode
    n275[phi_potential]
    n30 --> n275
    class n275 leafNode
    n276[rotation_frequency_tor_sonic]
    n30 --> n276
    class n276 leafNode
    n277[q]
    n30 --> n277
    class n277 leafNode
    n278[magnetic_shear]
    n30 --> n278
    class n278 leafNode
    n279[time]
    n30 --> n279
    class n279 leafNode
    n280(profiles_2d)
    n1 --> n280
    class n280 complexNode
    n281[grid_type]
    n280 --> n281
    class n281 normalNode
    n282[name]
    n281 --> n282
    class n282 leafNode
    n283[index]
    n281 --> n283
    class n283 leafNode
    n284[description]
    n281 --> n284
    class n284 leafNode
    n285[grid]
    n280 --> n285
    class n285 normalNode
    n286[dim1]
    n285 --> n286
    class n286 leafNode
    n287[dim2]
    n285 --> n287
    class n287 leafNode
    n288[volume_element]
    n285 --> n288
    class n288 leafNode
    n289(ion)
    n280 --> n289
    class n289 complexNode
    n290[element]
    n289 --> n290
    class n290 normalNode
    n291[a]
    n290 --> n291
    class n291 leafNode
    n292[z_n]
    n290 --> n292
    class n292 leafNode
    n293[atoms_n]
    n290 --> n293
    class n293 leafNode
    n294[z_ion]
    n289 --> n294
    class n294 leafNode
    n295[name]
    n289 --> n295
    class n295 leafNode
    n296[ion_index]
    n289 --> n296
    class n296 leafNode
    n297[temperature]
    n289 --> n297
    class n297 leafNode
    n298[density]
    n289 --> n298
    class n298 leafNode
    n299[density_thermal]
    n289 --> n299
    class n299 leafNode
    n300[density_fast]
    n289 --> n300
    class n300 leafNode
    n301[pressure]
    n289 --> n301
    class n301 leafNode
    n302[pressure_thermal]
    n289 --> n302
    class n302 leafNode
    n303[pressure_fast_perpendicular]
    n289 --> n303
    class n303 leafNode
    n304[pressure_fast_parallel]
    n289 --> n304
    class n304 leafNode
    n305[rotation_frequency_tor]
    n289 --> n305
    class n305 leafNode
    n306[velocity]
    n289 --> n306
    class n306 normalNode
    n307[radial]
    n306 --> n307
    class n307 leafNode
    n308[diamagnetic]
    n306 --> n308
    class n308 leafNode
    n309[parallel]
    n306 --> n309
    class n309 leafNode
    n310[poloidal]
    n306 --> n310
    class n310 leafNode
    n311[toroidal]
    n306 --> n311
    class n311 leafNode
    n312[multiple_states_flag]
    n289 --> n312
    class n312 leafNode
    n313(state)
    n289 --> n313
    class n313 complexNode
    n314[z_min]
    n313 --> n314
    class n314 leafNode
    n315[z_max]
    n313 --> n315
    class n315 leafNode
    n316[z_average]
    n313 --> n316
    class n316 leafNode
    n317[z_square_average]
    n313 --> n317
    class n317 leafNode
    n318[ionisation_potential]
    n313 --> n318
    class n318 leafNode
    n319[name]
    n313 --> n319
    class n319 leafNode
    n320[electron_configuration]
    n313 --> n320
    class n320 leafNode
    n321[vibrational_level]
    n313 --> n321
    class n321 leafNode
    n322[vibrational_mode]
    n313 --> n322
    class n322 leafNode
    n323[rotation_frequency_tor]
    n313 --> n323
    class n323 leafNode
    n324[temperature]
    n313 --> n324
    class n324 leafNode
    n325[density]
    n313 --> n325
    class n325 leafNode
    n326[density_thermal]
    n313 --> n326
    class n326 leafNode
    n327[density_fast]
    n313 --> n327
    class n327 leafNode
    n328[pressure]
    n313 --> n328
    class n328 leafNode
    n329[pressure_thermal]
    n313 --> n329
    class n329 leafNode
    n330[pressure_fast_perpendicular]
    n313 --> n330
    class n330 leafNode
    n331[pressure_fast_parallel]
    n313 --> n331
    class n331 leafNode
    n332[t_i_average]
    n280 --> n332
    class n332 leafNode
    n333[n_i_total_over_n_e]
    n280 --> n333
    class n333 leafNode
    n334[n_i_thermal_total]
    n280 --> n334
    class n334 leafNode
    n335[momentum_phi]
    n280 --> n335
    class n335 leafNode
    n336[zeff]
    n280 --> n336
    class n336 leafNode
    n337[pressure_ion_total]
    n280 --> n337
    class n337 leafNode
    n338[pressure_thermal]
    n280 --> n338
    class n338 leafNode
    n339[pressure_perpendicular]
    n280 --> n339
    class n339 leafNode
    n340[pressure_parallel]
    n280 --> n340
    class n340 leafNode
    n341[time]
    n280 --> n341
    class n341 leafNode
    n342[grid_ggd]
    n1 --> n342
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
    n347[path]
    n342 --> n347
    class n347 leafNode
    n348[space]
    n342 --> n348
    class n348 normalNode
    n349[identifier]
    n348 --> n349
    class n349 normalNode
    n350[name]
    n349 --> n350
    class n350 leafNode
    n351[index]
    n349 --> n351
    class n351 leafNode
    n352[description]
    n349 --> n352
    class n352 leafNode
    n353[geometry_type]
    n348 --> n353
    class n353 normalNode
    n354[name]
    n353 --> n354
    class n354 leafNode
    n355[index]
    n353 --> n355
    class n355 leafNode
    n356[description]
    n353 --> n356
    class n356 leafNode
    n357[coordinates_type]
    n348 --> n357
    class n357 normalNode
    n358[name]
    n357 --> n358
    class n358 leafNode
    n359[index]
    n357 --> n359
    class n359 leafNode
    n360[description]
    n357 --> n360
    class n360 leafNode
    n361[objects_per_dimension]
    n348 --> n361
    class n361 normalNode
    n362[object]
    n361 --> n362
    class n362 normalNode
    n363[boundary]
    n362 --> n363
    class n363 normalNode
    n364[index]
    n363 --> n364
    class n364 leafNode
    n365[neighbours]
    n363 --> n365
    class n365 leafNode
    n366[geometry]
    n362 --> n366
    class n366 leafNode
    n367[nodes]
    n362 --> n367
    class n367 leafNode
    n368[measure]
    n362 --> n368
    class n368 leafNode
    n369[geometry_2d]
    n362 --> n369
    class n369 leafNode
    n370[geometry_content]
    n361 --> n370
    class n370 normalNode
    n371[name]
    n370 --> n371
    class n371 leafNode
    n372[index]
    n370 --> n372
    class n372 leafNode
    n373[description]
    n370 --> n373
    class n373 leafNode
    n374[grid_subset]
    n342 --> n374
    class n374 normalNode
    n375[identifier]
    n374 --> n375
    class n375 normalNode
    n376[name]
    n375 --> n376
    class n376 leafNode
    n377[index]
    n375 --> n377
    class n377 leafNode
    n378[description]
    n375 --> n378
    class n378 leafNode
    n379[dimension]
    n374 --> n379
    class n379 leafNode
    n380[element]
    n374 --> n380
    class n380 normalNode
    n381[object]
    n380 --> n381
    class n381 normalNode
    n382[space]
    n381 --> n382
    class n382 leafNode
    n383[dimension]
    n381 --> n383
    class n383 leafNode
    n384[index]
    n381 --> n384
    class n384 leafNode
    n385[base]
    n374 --> n385
    class n385 normalNode
    n386[jacobian]
    n385 --> n386
    class n386 leafNode
    n387[tensor_covariant]
    n385 --> n387
    class n387 leafNode
    n388[tensor_contravariant]
    n385 --> n388
    class n388 leafNode
    n389[metric]
    n374 --> n389
    class n389 normalNode
    n390[jacobian]
    n389 --> n390
    class n390 leafNode
    n391[tensor_covariant]
    n389 --> n391
    class n391 leafNode
    n392[tensor_contravariant]
    n389 --> n392
    class n392 leafNode
    n393[time]
    n342 --> n393
    class n393 leafNode
    n394[ggd_fast]
    n1 --> n394
    class n394 normalNode
    n395[electrons]
    n394 --> n395
    class n395 normalNode
    n396[temperature]
    n395 --> n396
    class n396 normalNode
    n397[grid_index]
    n396 --> n397
    class n397 leafNode
    n398[grid_subset_index]
    n396 --> n398
    class n398 leafNode
    n399[value]
    n396 --> n399
    class n399 leafNode
    n400[density]
    n395 --> n400
    class n400 normalNode
    n401[grid_index]
    n400 --> n401
    class n401 leafNode
    n402[grid_subset_index]
    n400 --> n402
    class n402 leafNode
    n403[value]
    n400 --> n403
    class n403 leafNode
    n404(ion)
    n394 --> n404
    class n404 complexNode
    n405[element]
    n404 --> n405
    class n405 normalNode
    n406[a]
    n405 --> n406
    class n406 leafNode
    n407[z_n]
    n405 --> n407
    class n407 leafNode
    n408[atoms_n]
    n405 --> n408
    class n408 leafNode
    n409[z_ion]
    n404 --> n409
    class n409 leafNode
    n410[name]
    n404 --> n410
    class n410 leafNode
    n411[neutral_index]
    n404 --> n411
    class n411 leafNode
    n412[content]
    n404 --> n412
    class n412 normalNode
    n413[grid_index]
    n412 --> n413
    class n413 leafNode
    n414[grid_subset_index]
    n412 --> n414
    class n414 leafNode
    n415[value]
    n412 --> n415
    class n415 leafNode
    n416[temperature]
    n404 --> n416
    class n416 normalNode
    n417[grid_index]
    n416 --> n417
    class n417 leafNode
    n418[grid_subset_index]
    n416 --> n418
    class n418 leafNode
    n419[value]
    n416 --> n419
    class n419 leafNode
    n420[density]
    n404 --> n420
    class n420 normalNode
    n421[grid_index]
    n420 --> n421
    class n421 leafNode
    n422[grid_subset_index]
    n420 --> n422
    class n422 leafNode
    n423[value]
    n420 --> n423
    class n423 leafNode
    n424[energy_thermal]
    n394 --> n424
    class n424 normalNode
    n425[grid_index]
    n424 --> n425
    class n425 leafNode
    n426[grid_subset_index]
    n424 --> n426
    class n426 leafNode
    n427[value]
    n424 --> n427
    class n427 leafNode
    n428[time]
    n394 --> n428
    class n428 leafNode
    n429[covariance]
    n1 --> n429
    class n429 normalNode
    n430[description]
    n429 --> n430
    class n430 leafNode
    n431[rows_uri]
    n429 --> n431
    class n431 leafNode
    n432[data]
    n429 --> n432
    class n432 leafNode
    n433[statistics]
    n1 --> n433
    class n433 normalNode
    n434[quantity_2d]
    n433 --> n434
    class n434 normalNode
    n435[path]
    n434 --> n435
    class n435 leafNode
    n436[statistics_type]
    n434 --> n436
    class n436 normalNode
    n437[identifier]
    n436 --> n437
    class n437 normalNode
    n438[name]
    n437 --> n438
    class n438 leafNode
    n439[index]
    n437 --> n439
    class n439 leafNode
    n440[description]
    n437 --> n440
    class n440 leafNode
    n441[value]
    n436 --> n441
    class n441 leafNode
    n442[grid_subset_index]
    n436 --> n442
    class n442 leafNode
    n443[grid_index]
    n436 --> n443
    class n443 leafNode
    n444[uq_input_path]
    n436 --> n444
    class n444 leafNode
    n445[distribution]
    n434 --> n445
    class n445 normalNode
    n446[bins]
    n445 --> n446
    class n446 leafNode
    n447[probability]
    n445 --> n447
    class n447 leafNode
    n448[uq_input_2d]
    n433 --> n448
    class n448 normalNode
    n449[path]
    n448 --> n449
    class n449 leafNode
    n450[distribution]
    n448 --> n450
    class n450 normalNode
    n451[bins]
    n450 --> n451
    class n451 leafNode
    n452[probability]
    n450 --> n452
    class n452 leafNode
    n453[time_width]
    n433 --> n453
    class n453 leafNode
    n454[time]
    n433 --> n454
    class n454 leafNode
    n455[time]
    n1 --> n455
    class n455 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```