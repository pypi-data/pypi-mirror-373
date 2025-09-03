```mermaid
flowchart TD
    root["core_profiles IDS"]

    n1(core_profiles)
    root --> n1
    class n1 complexNode
    n2(profiles_1d)
    n1 --> n2
    class n2 complexNode
    n3(grid)
    n2 --> n3
    class n3 complexNode
    n4[rho_tor_norm]
    n3 --> n4
    class n4 leafNode
    n5[rho_tor]
    n3 --> n5
    class n5 leafNode
    n6[rho_pol_norm]
    n3 --> n6
    class n6 leafNode
    n7[psi]
    n3 --> n7
    class n7 leafNode
    n8[volume]
    n3 --> n8
    class n8 leafNode
    n9[area]
    n3 --> n9
    class n9 leafNode
    n10[surface]
    n3 --> n10
    class n10 leafNode
    n11[psi_magnetic_axis]
    n3 --> n11
    class n11 leafNode
    n12[psi_boundary]
    n3 --> n12
    class n12 leafNode
    n13(electrons)
    n2 --> n13
    class n13 complexNode
    n14[temperature]
    n13 --> n14
    class n14 leafNode
    n15[temperature_validity]
    n13 --> n15
    class n15 leafNode
    n16(temperature_fit)
    n13 --> n16
    class n16 complexNode
    n17[measured]
    n16 --> n17
    class n17 leafNode
    n18[source]
    n16 --> n18
    class n18 leafNode
    n19[time_measurement]
    n16 --> n19
    class n19 leafNode
    n20[time_measurement_slice_method]
    n16 --> n20
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
    n24[time_measurement_width]
    n16 --> n24
    class n24 leafNode
    n25[local]
    n16 --> n25
    class n25 leafNode
    n26[rho_tor_norm]
    n16 --> n26
    class n26 leafNode
    n27[weight]
    n16 --> n27
    class n27 leafNode
    n28[reconstructed]
    n16 --> n28
    class n28 leafNode
    n29[chi_squared]
    n16 --> n29
    class n29 leafNode
    n30[parameters]
    n16 --> n30
    class n30 leafNode
    n31[density]
    n13 --> n31
    class n31 leafNode
    n32[density_validity]
    n13 --> n32
    class n32 leafNode
    n33(density_fit)
    n13 --> n33
    class n33 complexNode
    n34[measured]
    n33 --> n34
    class n34 leafNode
    n35[source]
    n33 --> n35
    class n35 leafNode
    n36[time_measurement]
    n33 --> n36
    class n36 leafNode
    n37[time_measurement_slice_method]
    n33 --> n37
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
    n41[time_measurement_width]
    n33 --> n41
    class n41 leafNode
    n42[local]
    n33 --> n42
    class n42 leafNode
    n43[rho_tor_norm]
    n33 --> n43
    class n43 leafNode
    n44[weight]
    n33 --> n44
    class n44 leafNode
    n45[reconstructed]
    n33 --> n45
    class n45 leafNode
    n46[chi_squared]
    n33 --> n46
    class n46 leafNode
    n47[parameters]
    n33 --> n47
    class n47 leafNode
    n48[density_thermal]
    n13 --> n48
    class n48 leafNode
    n49[density_fast]
    n13 --> n49
    class n49 leafNode
    n50[pressure]
    n13 --> n50
    class n50 leafNode
    n51[pressure_thermal]
    n13 --> n51
    class n51 leafNode
    n52[pressure_fast_perpendicular]
    n13 --> n52
    class n52 leafNode
    n53[pressure_fast_parallel]
    n13 --> n53
    class n53 leafNode
    n54[collisionality_norm]
    n13 --> n54
    class n54 leafNode
    n55(ion)
    n2 --> n55
    class n55 complexNode
    n56[element]
    n55 --> n56
    class n56 normalNode
    n57[a]
    n56 --> n57
    class n57 leafNode
    n58[z_n]
    n56 --> n58
    class n58 leafNode
    n59[atoms_n]
    n56 --> n59
    class n59 leafNode
    n60[z_ion]
    n55 --> n60
    class n60 leafNode
    n61[name]
    n55 --> n61
    class n61 leafNode
    n62[neutral_index]
    n55 --> n62
    class n62 leafNode
    n63[z_ion_1d]
    n55 --> n63
    class n63 leafNode
    n64[z_ion_square_1d]
    n55 --> n64
    class n64 leafNode
    n65[temperature]
    n55 --> n65
    class n65 leafNode
    n66[temperature_validity]
    n55 --> n66
    class n66 leafNode
    n67(temperature_fit)
    n55 --> n67
    class n67 complexNode
    n68[measured]
    n67 --> n68
    class n68 leafNode
    n69[source]
    n67 --> n69
    class n69 leafNode
    n70[time_measurement]
    n67 --> n70
    class n70 leafNode
    n71[time_measurement_slice_method]
    n67 --> n71
    class n71 normalNode
    n72[name]
    n71 --> n72
    class n72 leafNode
    n73[index]
    n71 --> n73
    class n73 leafNode
    n74[description]
    n71 --> n74
    class n74 leafNode
    n75[time_measurement_width]
    n67 --> n75
    class n75 leafNode
    n76[local]
    n67 --> n76
    class n76 leafNode
    n77[rho_tor_norm]
    n67 --> n77
    class n77 leafNode
    n78[weight]
    n67 --> n78
    class n78 leafNode
    n79[reconstructed]
    n67 --> n79
    class n79 leafNode
    n80[chi_squared]
    n67 --> n80
    class n80 leafNode
    n81[parameters]
    n67 --> n81
    class n81 leafNode
    n82[density]
    n55 --> n82
    class n82 leafNode
    n83[density_validity]
    n55 --> n83
    class n83 leafNode
    n84(density_fit)
    n55 --> n84
    class n84 complexNode
    n85[measured]
    n84 --> n85
    class n85 leafNode
    n86[source]
    n84 --> n86
    class n86 leafNode
    n87[time_measurement]
    n84 --> n87
    class n87 leafNode
    n88[time_measurement_slice_method]
    n84 --> n88
    class n88 normalNode
    n89[name]
    n88 --> n89
    class n89 leafNode
    n90[index]
    n88 --> n90
    class n90 leafNode
    n91[description]
    n88 --> n91
    class n91 leafNode
    n92[time_measurement_width]
    n84 --> n92
    class n92 leafNode
    n93[local]
    n84 --> n93
    class n93 leafNode
    n94[rho_tor_norm]
    n84 --> n94
    class n94 leafNode
    n95[weight]
    n84 --> n95
    class n95 leafNode
    n96[reconstructed]
    n84 --> n96
    class n96 leafNode
    n97[chi_squared]
    n84 --> n97
    class n97 leafNode
    n98[parameters]
    n84 --> n98
    class n98 leafNode
    n99[density_thermal]
    n55 --> n99
    class n99 leafNode
    n100[density_fast]
    n55 --> n100
    class n100 leafNode
    n101[pressure]
    n55 --> n101
    class n101 leafNode
    n102[pressure_thermal]
    n55 --> n102
    class n102 leafNode
    n103[pressure_fast_perpendicular]
    n55 --> n103
    class n103 leafNode
    n104[pressure_fast_parallel]
    n55 --> n104
    class n104 leafNode
    n105[rotation_frequency_tor]
    n55 --> n105
    class n105 leafNode
    n106[velocity]
    n55 --> n106
    class n106 normalNode
    n107[radial]
    n106 --> n107
    class n107 leafNode
    n108[diamagnetic]
    n106 --> n108
    class n108 leafNode
    n109[parallel]
    n106 --> n109
    class n109 leafNode
    n110[poloidal]
    n106 --> n110
    class n110 leafNode
    n111[toroidal]
    n106 --> n111
    class n111 leafNode
    n112[multiple_states_flag]
    n55 --> n112
    class n112 leafNode
    n113(state)
    n55 --> n113
    class n113 complexNode
    n114[z_min]
    n113 --> n114
    class n114 leafNode
    n115[z_max]
    n113 --> n115
    class n115 leafNode
    n116[z_average]
    n113 --> n116
    class n116 leafNode
    n117[z_square_average]
    n113 --> n117
    class n117 leafNode
    n118[z_average_1d]
    n113 --> n118
    class n118 leafNode
    n119[z_average_square_1d]
    n113 --> n119
    class n119 leafNode
    n120[ionization_potential]
    n113 --> n120
    class n120 leafNode
    n121[name]
    n113 --> n121
    class n121 leafNode
    n122[electron_configuration]
    n113 --> n122
    class n122 leafNode
    n123[vibrational_level]
    n113 --> n123
    class n123 leafNode
    n124[vibrational_mode]
    n113 --> n124
    class n124 leafNode
    n125[rotation_frequency_tor]
    n113 --> n125
    class n125 leafNode
    n126[velocity]
    n113 --> n126
    class n126 normalNode
    n127[radial]
    n126 --> n127
    class n127 leafNode
    n128[diamagnetic]
    n126 --> n128
    class n128 leafNode
    n129[parallel]
    n126 --> n129
    class n129 leafNode
    n130[poloidal]
    n126 --> n130
    class n130 leafNode
    n131[toroidal]
    n126 --> n131
    class n131 leafNode
    n132[temperature]
    n113 --> n132
    class n132 leafNode
    n133[density]
    n113 --> n133
    class n133 leafNode
    n134(density_fit)
    n113 --> n134
    class n134 complexNode
    n135[measured]
    n134 --> n135
    class n135 leafNode
    n136[source]
    n134 --> n136
    class n136 leafNode
    n137[time_measurement]
    n134 --> n137
    class n137 leafNode
    n138[time_measurement_slice_method]
    n134 --> n138
    class n138 normalNode
    n139[name]
    n138 --> n139
    class n139 leafNode
    n140[index]
    n138 --> n140
    class n140 leafNode
    n141[description]
    n138 --> n141
    class n141 leafNode
    n142[time_measurement_width]
    n134 --> n142
    class n142 leafNode
    n143[local]
    n134 --> n143
    class n143 leafNode
    n144[rho_tor_norm]
    n134 --> n144
    class n144 leafNode
    n145[weight]
    n134 --> n145
    class n145 leafNode
    n146[reconstructed]
    n134 --> n146
    class n146 leafNode
    n147[chi_squared]
    n134 --> n147
    class n147 leafNode
    n148[parameters]
    n134 --> n148
    class n148 leafNode
    n149[density_thermal]
    n113 --> n149
    class n149 leafNode
    n150[density_fast]
    n113 --> n150
    class n150 leafNode
    n151[pressure]
    n113 --> n151
    class n151 leafNode
    n152[pressure_thermal]
    n113 --> n152
    class n152 leafNode
    n153[pressure_fast_perpendicular]
    n113 --> n153
    class n153 leafNode
    n154[pressure_fast_parallel]
    n113 --> n154
    class n154 leafNode
    n155(neutral)
    n2 --> n155
    class n155 complexNode
    n156[element]
    n155 --> n156
    class n156 normalNode
    n157[a]
    n156 --> n157
    class n157 leafNode
    n158[z_n]
    n156 --> n158
    class n158 leafNode
    n159[atoms_n]
    n156 --> n159
    class n159 leafNode
    n160[name]
    n155 --> n160
    class n160 leafNode
    n161[ion_index]
    n155 --> n161
    class n161 leafNode
    n162[temperature]
    n155 --> n162
    class n162 leafNode
    n163[density]
    n155 --> n163
    class n163 leafNode
    n164[density_thermal]
    n155 --> n164
    class n164 leafNode
    n165[density_fast]
    n155 --> n165
    class n165 leafNode
    n166[pressure]
    n155 --> n166
    class n166 leafNode
    n167[pressure_thermal]
    n155 --> n167
    class n167 leafNode
    n168[pressure_fast_perpendicular]
    n155 --> n168
    class n168 leafNode
    n169[pressure_fast_parallel]
    n155 --> n169
    class n169 leafNode
    n170[multiple_states_flag]
    n155 --> n170
    class n170 leafNode
    n171(state)
    n155 --> n171
    class n171 complexNode
    n172[name]
    n171 --> n172
    class n172 leafNode
    n173[electron_configuration]
    n171 --> n173
    class n173 leafNode
    n174[vibrational_level]
    n171 --> n174
    class n174 leafNode
    n175[vibrational_mode]
    n171 --> n175
    class n175 leafNode
    n176[neutral_type]
    n171 --> n176
    class n176 normalNode
    n177[name]
    n176 --> n177
    class n177 leafNode
    n178[index]
    n176 --> n178
    class n178 leafNode
    n179[description]
    n176 --> n179
    class n179 leafNode
    n180[temperature]
    n171 --> n180
    class n180 leafNode
    n181[density]
    n171 --> n181
    class n181 leafNode
    n182[density_thermal]
    n171 --> n182
    class n182 leafNode
    n183[density_fast]
    n171 --> n183
    class n183 leafNode
    n184[pressure]
    n171 --> n184
    class n184 leafNode
    n185[pressure_thermal]
    n171 --> n185
    class n185 leafNode
    n186[pressure_fast_perpendicular]
    n171 --> n186
    class n186 leafNode
    n187[pressure_fast_parallel]
    n171 --> n187
    class n187 leafNode
    n188[t_i_average]
    n2 --> n188
    class n188 leafNode
    n189(t_i_average_fit)
    n2 --> n189
    class n189 complexNode
    n190[measured]
    n189 --> n190
    class n190 leafNode
    n191[source]
    n189 --> n191
    class n191 leafNode
    n192[time_measurement]
    n189 --> n192
    class n192 leafNode
    n193[time_measurement_slice_method]
    n189 --> n193
    class n193 normalNode
    n194[name]
    n193 --> n194
    class n194 leafNode
    n195[index]
    n193 --> n195
    class n195 leafNode
    n196[description]
    n193 --> n196
    class n196 leafNode
    n197[time_measurement_width]
    n189 --> n197
    class n197 leafNode
    n198[local]
    n189 --> n198
    class n198 leafNode
    n199[rho_tor_norm]
    n189 --> n199
    class n199 leafNode
    n200[weight]
    n189 --> n200
    class n200 leafNode
    n201[reconstructed]
    n189 --> n201
    class n201 leafNode
    n202[chi_squared]
    n189 --> n202
    class n202 leafNode
    n203[parameters]
    n189 --> n203
    class n203 leafNode
    n204[n_i_total_over_n_e]
    n2 --> n204
    class n204 leafNode
    n205[n_i_thermal_total]
    n2 --> n205
    class n205 leafNode
    n206[momentum_phi]
    n2 --> n206
    class n206 leafNode
    n207[zeff]
    n2 --> n207
    class n207 leafNode
    n208(zeff_fit)
    n2 --> n208
    class n208 complexNode
    n209[measured]
    n208 --> n209
    class n209 leafNode
    n210[source]
    n208 --> n210
    class n210 leafNode
    n211[time_measurement]
    n208 --> n211
    class n211 leafNode
    n212[time_measurement_slice_method]
    n208 --> n212
    class n212 normalNode
    n213[name]
    n212 --> n213
    class n213 leafNode
    n214[index]
    n212 --> n214
    class n214 leafNode
    n215[description]
    n212 --> n215
    class n215 leafNode
    n216[time_measurement_width]
    n208 --> n216
    class n216 leafNode
    n217[local]
    n208 --> n217
    class n217 leafNode
    n218[rho_tor_norm]
    n208 --> n218
    class n218 leafNode
    n219[weight]
    n208 --> n219
    class n219 leafNode
    n220[reconstructed]
    n208 --> n220
    class n220 leafNode
    n221[chi_squared]
    n208 --> n221
    class n221 leafNode
    n222[parameters]
    n208 --> n222
    class n222 leafNode
    n223[pressure_ion_total]
    n2 --> n223
    class n223 leafNode
    n224[pressure_thermal]
    n2 --> n224
    class n224 leafNode
    n225[pressure_perpendicular]
    n2 --> n225
    class n225 leafNode
    n226[pressure_parallel]
    n2 --> n226
    class n226 leafNode
    n227[j_total]
    n2 --> n227
    class n227 leafNode
    n228[current_parallel_inside]
    n2 --> n228
    class n228 leafNode
    n229[j_phi]
    n2 --> n229
    class n229 leafNode
    n230[j_ohmic]
    n2 --> n230
    class n230 leafNode
    n231[j_non_inductive]
    n2 --> n231
    class n231 leafNode
    n232[j_bootstrap]
    n2 --> n232
    class n232 leafNode
    n233[conductivity_parallel]
    n2 --> n233
    class n233 leafNode
    n234[e_field]
    n2 --> n234
    class n234 normalNode
    n235[radial]
    n234 --> n235
    class n235 leafNode
    n236[diamagnetic]
    n234 --> n236
    class n236 leafNode
    n237[parallel]
    n234 --> n237
    class n237 leafNode
    n238[poloidal]
    n234 --> n238
    class n238 leafNode
    n239[toroidal]
    n234 --> n239
    class n239 leafNode
    n240[phi_potential]
    n2 --> n240
    class n240 leafNode
    n241[rotation_frequency_tor_sonic]
    n2 --> n241
    class n241 leafNode
    n242[q]
    n2 --> n242
    class n242 leafNode
    n243[magnetic_shear]
    n2 --> n243
    class n243 leafNode
    n244[time]
    n2 --> n244
    class n244 leafNode
    n245(profiles_2d)
    n1 --> n245
    class n245 complexNode
    n246[grid_type]
    n245 --> n246
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
    n250[grid]
    n245 --> n250
    class n250 normalNode
    n251[dim1]
    n250 --> n251
    class n251 leafNode
    n252[dim2]
    n250 --> n252
    class n252 leafNode
    n253[volume_element]
    n250 --> n253
    class n253 leafNode
    n254(ion)
    n245 --> n254
    class n254 complexNode
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
    n259[z_ion]
    n254 --> n259
    class n259 leafNode
    n260[name]
    n254 --> n260
    class n260 leafNode
    n261[ion_index]
    n254 --> n261
    class n261 leafNode
    n262[temperature]
    n254 --> n262
    class n262 leafNode
    n263[density]
    n254 --> n263
    class n263 leafNode
    n264[density_thermal]
    n254 --> n264
    class n264 leafNode
    n265[density_fast]
    n254 --> n265
    class n265 leafNode
    n266[pressure]
    n254 --> n266
    class n266 leafNode
    n267[pressure_thermal]
    n254 --> n267
    class n267 leafNode
    n268[pressure_fast_perpendicular]
    n254 --> n268
    class n268 leafNode
    n269[pressure_fast_parallel]
    n254 --> n269
    class n269 leafNode
    n270[rotation_frequency_tor]
    n254 --> n270
    class n270 leafNode
    n271[velocity]
    n254 --> n271
    class n271 normalNode
    n272[radial]
    n271 --> n272
    class n272 leafNode
    n273[diamagnetic]
    n271 --> n273
    class n273 leafNode
    n274[parallel]
    n271 --> n274
    class n274 leafNode
    n275[poloidal]
    n271 --> n275
    class n275 leafNode
    n276[toroidal]
    n271 --> n276
    class n276 leafNode
    n277[multiple_states_flag]
    n254 --> n277
    class n277 leafNode
    n278(state)
    n254 --> n278
    class n278 complexNode
    n279[z_min]
    n278 --> n279
    class n279 leafNode
    n280[z_max]
    n278 --> n280
    class n280 leafNode
    n281[z_average]
    n278 --> n281
    class n281 leafNode
    n282[z_square_average]
    n278 --> n282
    class n282 leafNode
    n283[ionization_potential]
    n278 --> n283
    class n283 leafNode
    n284[name]
    n278 --> n284
    class n284 leafNode
    n285[electron_configuration]
    n278 --> n285
    class n285 leafNode
    n286[vibrational_level]
    n278 --> n286
    class n286 leafNode
    n287[vibrational_mode]
    n278 --> n287
    class n287 leafNode
    n288[rotation_frequency_tor]
    n278 --> n288
    class n288 leafNode
    n289[temperature]
    n278 --> n289
    class n289 leafNode
    n290[density]
    n278 --> n290
    class n290 leafNode
    n291[density_thermal]
    n278 --> n291
    class n291 leafNode
    n292[density_fast]
    n278 --> n292
    class n292 leafNode
    n293[pressure]
    n278 --> n293
    class n293 leafNode
    n294[pressure_thermal]
    n278 --> n294
    class n294 leafNode
    n295[pressure_fast_perpendicular]
    n278 --> n295
    class n295 leafNode
    n296[pressure_fast_parallel]
    n278 --> n296
    class n296 leafNode
    n297[t_i_average]
    n245 --> n297
    class n297 leafNode
    n298[n_i_total_over_n_e]
    n245 --> n298
    class n298 leafNode
    n299[n_i_thermal_total]
    n245 --> n299
    class n299 leafNode
    n300[momentum_phi]
    n245 --> n300
    class n300 leafNode
    n301[zeff]
    n245 --> n301
    class n301 leafNode
    n302[pressure_ion_total]
    n245 --> n302
    class n302 leafNode
    n303[pressure_thermal]
    n245 --> n303
    class n303 leafNode
    n304[pressure_perpendicular]
    n245 --> n304
    class n304 leafNode
    n305[pressure_parallel]
    n245 --> n305
    class n305 leafNode
    n306[time]
    n245 --> n306
    class n306 leafNode
    n307(global_quantities)
    n1 --> n307
    class n307 complexNode
    n308[ip]
    n307 --> n308
    class n308 leafNode
    n309[current_non_inductive]
    n307 --> n309
    class n309 leafNode
    n310[current_bootstrap]
    n307 --> n310
    class n310 leafNode
    n311[v_loop]
    n307 --> n311
    class n311 leafNode
    n312[li_3]
    n307 --> n312
    class n312 leafNode
    n313[beta_tor]
    n307 --> n313
    class n313 leafNode
    n314[beta_tor_norm]
    n307 --> n314
    class n314 leafNode
    n315[beta_pol]
    n307 --> n315
    class n315 leafNode
    n316[energy_diamagnetic]
    n307 --> n316
    class n316 leafNode
    n317[z_eff_resistive]
    n307 --> n317
    class n317 leafNode
    n318[t_e_peaking]
    n307 --> n318
    class n318 leafNode
    n319[t_i_average_peaking]
    n307 --> n319
    class n319 leafNode
    n320[resistive_psi_losses]
    n307 --> n320
    class n320 leafNode
    n321[ejima]
    n307 --> n321
    class n321 leafNode
    n322[t_e_volume_average]
    n307 --> n322
    class n322 leafNode
    n323[n_e_volume_average]
    n307 --> n323
    class n323 leafNode
    n324[ion]
    n307 --> n324
    class n324 normalNode
    n325[t_i_volume_average]
    n324 --> n325
    class n325 leafNode
    n326[n_i_volume_average]
    n324 --> n326
    class n326 leafNode
    n327[ion_time_slice]
    n307 --> n327
    class n327 leafNode
    n328[vacuum_toroidal_field]
    n1 --> n328
    class n328 normalNode
    n329[r0]
    n328 --> n329
    class n329 leafNode
    n330[b0]
    n328 --> n330
    class n330 leafNode
    n331[covariance]
    n1 --> n331
    class n331 normalNode
    n332[description]
    n331 --> n332
    class n332 leafNode
    n333[rows_uri]
    n331 --> n333
    class n333 leafNode
    n334[data]
    n331 --> n334
    class n334 leafNode
    n335[statistics]
    n1 --> n335
    class n335 normalNode
    n336[quantity_2d]
    n335 --> n336
    class n336 normalNode
    n337[path]
    n336 --> n337
    class n337 leafNode
    n338[statistics_type]
    n336 --> n338
    class n338 normalNode
    n339[identifier]
    n338 --> n339
    class n339 normalNode
    n340[name]
    n339 --> n340
    class n340 leafNode
    n341[index]
    n339 --> n341
    class n341 leafNode
    n342[description]
    n339 --> n342
    class n342 leafNode
    n343[value]
    n338 --> n343
    class n343 leafNode
    n344[grid_subset_index]
    n338 --> n344
    class n344 leafNode
    n345[grid_index]
    n338 --> n345
    class n345 leafNode
    n346[uq_input_path]
    n338 --> n346
    class n346 leafNode
    n347[distribution]
    n336 --> n347
    class n347 normalNode
    n348[bins]
    n347 --> n348
    class n348 leafNode
    n349[probability]
    n347 --> n349
    class n349 leafNode
    n350[uq_input_2d]
    n335 --> n350
    class n350 normalNode
    n351[path]
    n350 --> n351
    class n351 leafNode
    n352[distribution]
    n350 --> n352
    class n352 normalNode
    n353[bins]
    n352 --> n353
    class n353 leafNode
    n354[probability]
    n352 --> n354
    class n354 leafNode
    n355[time_width]
    n335 --> n355
    class n355 leafNode
    n356[time]
    n335 --> n356
    class n356 leafNode
    n357[time]
    n1 --> n357
    class n357 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```