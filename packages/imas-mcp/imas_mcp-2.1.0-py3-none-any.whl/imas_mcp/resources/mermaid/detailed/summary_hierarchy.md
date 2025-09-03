```mermaid
flowchart TD
    root["summary IDS"]

    n1(summary)
    root --> n1
    class n1 complexNode
    n2[type]
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
    n6[machine]
    n1 --> n6
    class n6 leafNode
    n7[pulse]
    n1 --> n7
    class n7 leafNode
    n8[pulse_time_begin]
    n1 --> n8
    class n8 leafNode
    n9[pulse_time_begin_epoch]
    n1 --> n9
    class n9 normalNode
    n10[seconds]
    n9 --> n10
    class n10 leafNode
    n11[nanoseconds]
    n9 --> n11
    class n11 leafNode
    n12[pulse_time_end_epoch]
    n1 --> n12
    class n12 normalNode
    n13[seconds]
    n12 --> n13
    class n13 leafNode
    n14[nanoseconds]
    n12 --> n14
    class n14 leafNode
    n15[pulse_processing_time_begin]
    n1 --> n15
    class n15 leafNode
    n16[description]
    n1 --> n16
    class n16 leafNode
    n17[simulation]
    n1 --> n17
    class n17 normalNode
    n18[time_begin]
    n17 --> n18
    class n18 leafNode
    n19[time_step]
    n17 --> n19
    class n19 leafNode
    n20[time_end]
    n17 --> n20
    class n20 leafNode
    n21[workflow]
    n17 --> n21
    class n21 leafNode
    n22[tag]
    n1 --> n22
    class n22 normalNode
    n23[name]
    n22 --> n23
    class n23 leafNode
    n24[comment]
    n22 --> n24
    class n24 leafNode
    n25[configuration]
    n1 --> n25
    class n25 normalNode
    n26[value]
    n25 --> n26
    class n26 leafNode
    n27[source]
    n25 --> n27
    class n27 leafNode
    n28[magnetic_shear_flag]
    n1 --> n28
    class n28 normalNode
    n29[value]
    n28 --> n29
    class n29 leafNode
    n30[source]
    n28 --> n30
    class n30 leafNode
    n31[stationary_phase_flag]
    n1 --> n31
    class n31 normalNode
    n32[value]
    n31 --> n32
    class n32 leafNode
    n33[source]
    n31 --> n33
    class n33 leafNode
    n34[midplane]
    n1 --> n34
    class n34 normalNode
    n35[name]
    n34 --> n35
    class n35 leafNode
    n36[index]
    n34 --> n36
    class n36 leafNode
    n37[description]
    n34 --> n37
    class n37 leafNode
    n38(composition)
    n1 --> n38
    class n38 complexNode
    n39[hydrogen]
    n38 --> n39
    class n39 normalNode
    n40[value]
    n39 --> n40
    class n40 leafNode
    n41[source]
    n39 --> n41
    class n41 leafNode
    n42[deuterium]
    n38 --> n42
    class n42 normalNode
    n43[value]
    n42 --> n43
    class n43 leafNode
    n44[source]
    n42 --> n44
    class n44 leafNode
    n45[tritium]
    n38 --> n45
    class n45 normalNode
    n46[value]
    n45 --> n46
    class n46 leafNode
    n47[source]
    n45 --> n47
    class n47 leafNode
    n48[deuterium_tritium]
    n38 --> n48
    class n48 normalNode
    n49[value]
    n48 --> n49
    class n49 leafNode
    n50[source]
    n48 --> n50
    class n50 leafNode
    n51[helium_3]
    n38 --> n51
    class n51 normalNode
    n52[value]
    n51 --> n52
    class n52 leafNode
    n53[source]
    n51 --> n53
    class n53 leafNode
    n54[helium_4]
    n38 --> n54
    class n54 normalNode
    n55[value]
    n54 --> n55
    class n55 leafNode
    n56[source]
    n54 --> n56
    class n56 leafNode
    n57[beryllium]
    n38 --> n57
    class n57 normalNode
    n58[value]
    n57 --> n58
    class n58 leafNode
    n59[source]
    n57 --> n59
    class n59 leafNode
    n60[boron]
    n38 --> n60
    class n60 normalNode
    n61[value]
    n60 --> n61
    class n61 leafNode
    n62[source]
    n60 --> n62
    class n62 leafNode
    n63[lithium]
    n38 --> n63
    class n63 normalNode
    n64[value]
    n63 --> n64
    class n64 leafNode
    n65[source]
    n63 --> n65
    class n65 leafNode
    n66[carbon]
    n38 --> n66
    class n66 normalNode
    n67[value]
    n66 --> n67
    class n67 leafNode
    n68[source]
    n66 --> n68
    class n68 leafNode
    n69[nitrogen]
    n38 --> n69
    class n69 normalNode
    n70[value]
    n69 --> n70
    class n70 leafNode
    n71[source]
    n69 --> n71
    class n71 leafNode
    n72[neon]
    n38 --> n72
    class n72 normalNode
    n73[value]
    n72 --> n73
    class n73 leafNode
    n74[source]
    n72 --> n74
    class n74 leafNode
    n75[argon]
    n38 --> n75
    class n75 normalNode
    n76[value]
    n75 --> n76
    class n76 leafNode
    n77[source]
    n75 --> n77
    class n77 leafNode
    n78[xenon]
    n38 --> n78
    class n78 normalNode
    n79[value]
    n78 --> n79
    class n79 leafNode
    n80[source]
    n78 --> n80
    class n80 leafNode
    n81[oxygen]
    n38 --> n81
    class n81 normalNode
    n82[value]
    n81 --> n82
    class n82 leafNode
    n83[source]
    n81 --> n83
    class n83 leafNode
    n84[tungsten]
    n38 --> n84
    class n84 normalNode
    n85[value]
    n84 --> n85
    class n85 leafNode
    n86[source]
    n84 --> n86
    class n86 leafNode
    n87[iron]
    n38 --> n87
    class n87 normalNode
    n88[value]
    n87 --> n88
    class n88 leafNode
    n89[source]
    n87 --> n89
    class n89 leafNode
    n90[krypton]
    n38 --> n90
    class n90 normalNode
    n91[value]
    n90 --> n91
    class n91 leafNode
    n92[source]
    n90 --> n92
    class n92 leafNode
    n93(global_quantities)
    n1 --> n93
    class n93 complexNode
    n94[ip]
    n93 --> n94
    class n94 normalNode
    n95[value]
    n94 --> n95
    class n95 leafNode
    n96[source]
    n94 --> n96
    class n96 leafNode
    n97[current_non_inductive]
    n93 --> n97
    class n97 normalNode
    n98[value]
    n97 --> n98
    class n98 leafNode
    n99[source]
    n97 --> n99
    class n99 leafNode
    n100[current_bootstrap]
    n93 --> n100
    class n100 normalNode
    n101[value]
    n100 --> n101
    class n101 leafNode
    n102[source]
    n100 --> n102
    class n102 leafNode
    n103[current_ohm]
    n93 --> n103
    class n103 normalNode
    n104[value]
    n103 --> n104
    class n104 leafNode
    n105[source]
    n103 --> n105
    class n105 leafNode
    n106[current_alignment]
    n93 --> n106
    class n106 normalNode
    n107[value]
    n106 --> n107
    class n107 leafNode
    n108[source]
    n106 --> n108
    class n108 leafNode
    n109[v_loop]
    n93 --> n109
    class n109 normalNode
    n110[value]
    n109 --> n110
    class n110 leafNode
    n111[source]
    n109 --> n111
    class n111 leafNode
    n112[li_3]
    n93 --> n112
    class n112 normalNode
    n113[value]
    n112 --> n113
    class n113 leafNode
    n114[source]
    n112 --> n114
    class n114 leafNode
    n115[li_3_mhd]
    n93 --> n115
    class n115 normalNode
    n116[value]
    n115 --> n116
    class n116 leafNode
    n117[source]
    n115 --> n117
    class n117 leafNode
    n118[beta_tor]
    n93 --> n118
    class n118 normalNode
    n119[value]
    n118 --> n119
    class n119 leafNode
    n120[source]
    n118 --> n120
    class n120 leafNode
    n121[beta_tor_mhd]
    n93 --> n121
    class n121 normalNode
    n122[value]
    n121 --> n122
    class n122 leafNode
    n123[source]
    n121 --> n123
    class n123 leafNode
    n124[beta_tor_norm]
    n93 --> n124
    class n124 normalNode
    n125[value]
    n124 --> n125
    class n125 leafNode
    n126[source]
    n124 --> n126
    class n126 leafNode
    n127[beta_tor_norm_mhd]
    n93 --> n127
    class n127 normalNode
    n128[value]
    n127 --> n128
    class n128 leafNode
    n129[source]
    n127 --> n129
    class n129 leafNode
    n130[beta_tor_thermal_norm]
    n93 --> n130
    class n130 normalNode
    n131[value]
    n130 --> n131
    class n131 leafNode
    n132[source]
    n130 --> n132
    class n132 leafNode
    n133[beta_pol]
    n93 --> n133
    class n133 normalNode
    n134[value]
    n133 --> n134
    class n134 leafNode
    n135[source]
    n133 --> n135
    class n135 leafNode
    n136[beta_pol_mhd]
    n93 --> n136
    class n136 normalNode
    n137[value]
    n136 --> n137
    class n137 leafNode
    n138[source]
    n136 --> n138
    class n138 leafNode
    n139[energy_diamagnetic]
    n93 --> n139
    class n139 normalNode
    n140[value]
    n139 --> n140
    class n140 leafNode
    n141[source]
    n139 --> n141
    class n141 leafNode
    n142[denergy_diamagnetic_dt]
    n93 --> n142
    class n142 normalNode
    n143[value]
    n142 --> n143
    class n143 leafNode
    n144[source]
    n142 --> n144
    class n144 leafNode
    n145[energy_total]
    n93 --> n145
    class n145 normalNode
    n146[value]
    n145 --> n146
    class n146 leafNode
    n147[source]
    n145 --> n147
    class n147 leafNode
    n148[energy_mhd]
    n93 --> n148
    class n148 normalNode
    n149[value]
    n148 --> n149
    class n149 leafNode
    n150[source]
    n148 --> n150
    class n150 leafNode
    n151[energy_thermal]
    n93 --> n151
    class n151 normalNode
    n152[value]
    n151 --> n152
    class n152 leafNode
    n153[source]
    n151 --> n153
    class n153 leafNode
    n154[energy_ion_total_thermal]
    n93 --> n154
    class n154 normalNode
    n155[value]
    n154 --> n155
    class n155 leafNode
    n156[source]
    n154 --> n156
    class n156 leafNode
    n157[energy_electrons_thermal]
    n93 --> n157
    class n157 normalNode
    n158[value]
    n157 --> n158
    class n158 leafNode
    n159[source]
    n157 --> n159
    class n159 leafNode
    n160[denergy_thermal_dt]
    n93 --> n160
    class n160 normalNode
    n161[value]
    n160 --> n161
    class n161 leafNode
    n162[source]
    n160 --> n162
    class n162 leafNode
    n163[energy_b_field_pol]
    n93 --> n163
    class n163 normalNode
    n164[value]
    n163 --> n164
    class n164 leafNode
    n165[source]
    n163 --> n165
    class n165 leafNode
    n166[energy_fast_perpendicular]
    n93 --> n166
    class n166 normalNode
    n167[value]
    n166 --> n167
    class n167 leafNode
    n168[source]
    n166 --> n168
    class n168 leafNode
    n169[energy_fast_parallel]
    n93 --> n169
    class n169 normalNode
    n170[value]
    n169 --> n170
    class n170 leafNode
    n171[source]
    n169 --> n171
    class n171 leafNode
    n172[volume]
    n93 --> n172
    class n172 normalNode
    n173[value]
    n172 --> n173
    class n173 leafNode
    n174[source]
    n172 --> n174
    class n174 leafNode
    n175[h_mode]
    n93 --> n175
    class n175 normalNode
    n176[value]
    n175 --> n176
    class n176 leafNode
    n177[source]
    n175 --> n177
    class n177 leafNode
    n178[r0]
    n93 --> n178
    class n178 normalNode
    n179[value]
    n178 --> n179
    class n179 leafNode
    n180[source]
    n178 --> n180
    class n180 leafNode
    n181[b0]
    n93 --> n181
    class n181 normalNode
    n182[value]
    n181 --> n182
    class n182 leafNode
    n183[source]
    n181 --> n183
    class n183 leafNode
    n184[fusion_gain]
    n93 --> n184
    class n184 normalNode
    n185[value]
    n184 --> n185
    class n185 leafNode
    n186[source]
    n184 --> n186
    class n186 leafNode
    n187[h_98]
    n93 --> n187
    class n187 normalNode
    n188[value]
    n187 --> n188
    class n188 leafNode
    n189[source]
    n187 --> n189
    class n189 leafNode
    n190[tau_energy]
    n93 --> n190
    class n190 normalNode
    n191[value]
    n190 --> n191
    class n191 leafNode
    n192[source]
    n190 --> n192
    class n192 leafNode
    n193[tau_helium]
    n93 --> n193
    class n193 normalNode
    n194[value]
    n193 --> n194
    class n194 leafNode
    n195[source]
    n193 --> n195
    class n195 leafNode
    n196[tau_resistive]
    n93 --> n196
    class n196 normalNode
    n197[value]
    n196 --> n197
    class n197 leafNode
    n198[source]
    n196 --> n198
    class n198 leafNode
    n199[tau_energy_98]
    n93 --> n199
    class n199 normalNode
    n200[value]
    n199 --> n200
    class n200 leafNode
    n201[source]
    n199 --> n201
    class n201 leafNode
    n202[ratio_tau_helium_fuel]
    n93 --> n202
    class n202 normalNode
    n203[value]
    n202 --> n203
    class n203 leafNode
    n204[source]
    n202 --> n204
    class n204 leafNode
    n205[resistance]
    n93 --> n205
    class n205 normalNode
    n206[value]
    n205 --> n206
    class n206 leafNode
    n207[source]
    n205 --> n207
    class n207 leafNode
    n208[q_95]
    n93 --> n208
    class n208 normalNode
    n209[value]
    n208 --> n209
    class n209 leafNode
    n210[source]
    n208 --> n210
    class n210 leafNode
    n211[power_ohm]
    n93 --> n211
    class n211 normalNode
    n212[value]
    n211 --> n212
    class n212 leafNode
    n213[source]
    n211 --> n213
    class n213 leafNode
    n214[power_steady]
    n93 --> n214
    class n214 normalNode
    n215[value]
    n214 --> n215
    class n215 leafNode
    n216[source]
    n214 --> n216
    class n216 leafNode
    n217[power_radiated]
    n93 --> n217
    class n217 normalNode
    n218[value]
    n217 --> n218
    class n218 leafNode
    n219[source]
    n217 --> n219
    class n219 leafNode
    n220[power_radiated_inside_lcfs]
    n93 --> n220
    class n220 normalNode
    n221[value]
    n220 --> n221
    class n221 leafNode
    n222[source]
    n220 --> n222
    class n222 leafNode
    n223[power_radiated_outside_lcfs]
    n93 --> n223
    class n223 normalNode
    n224[value]
    n223 --> n224
    class n224 leafNode
    n225[source]
    n223 --> n225
    class n225 leafNode
    n226[power_line]
    n93 --> n226
    class n226 normalNode
    n227[value]
    n226 --> n227
    class n227 leafNode
    n228[source]
    n226 --> n228
    class n228 leafNode
    n229[power_bremsstrahlung]
    n93 --> n229
    class n229 normalNode
    n230[value]
    n229 --> n230
    class n230 leafNode
    n231[source]
    n229 --> n231
    class n231 leafNode
    n232[power_synchrotron]
    n93 --> n232
    class n232 normalNode
    n233[value]
    n232 --> n233
    class n233 leafNode
    n234[source]
    n232 --> n234
    class n234 leafNode
    n235[power_loss]
    n93 --> n235
    class n235 normalNode
    n236[value]
    n235 --> n236
    class n236 leafNode
    n237[source]
    n235 --> n237
    class n237 leafNode
    n238[greenwald_fraction]
    n93 --> n238
    class n238 normalNode
    n239[value]
    n238 --> n239
    class n239 leafNode
    n240[source]
    n238 --> n240
    class n240 leafNode
    n241[fusion_fluence]
    n93 --> n241
    class n241 normalNode
    n242[value]
    n241 --> n242
    class n242 leafNode
    n243[source]
    n241 --> n243
    class n243 leafNode
    n244[psi_external_average]
    n93 --> n244
    class n244 normalNode
    n245[value]
    n244 --> n245
    class n245 leafNode
    n246[source]
    n244 --> n246
    class n246 leafNode
    n247(local)
    n1 --> n247
    class n247 complexNode
    n248(magnetic_axis)
    n247 --> n248
    class n248 complexNode
    n249[position]
    n248 --> n249
    class n249 normalNode
    n250[rho_tor_norm]
    n249 --> n250
    class n250 leafNode
    n251[rho_tor]
    n249 --> n251
    class n251 leafNode
    n252[psi]
    n249 --> n252
    class n252 leafNode
    n253[r]
    n249 --> n253
    class n253 leafNode
    n254[z]
    n249 --> n254
    class n254 leafNode
    n255[t_e]
    n248 --> n255
    class n255 normalNode
    n256[value]
    n255 --> n256
    class n256 leafNode
    n257[source]
    n255 --> n257
    class n257 leafNode
    n258[t_i_average]
    n248 --> n258
    class n258 normalNode
    n259[value]
    n258 --> n259
    class n259 leafNode
    n260[source]
    n258 --> n260
    class n260 leafNode
    n261[n_e]
    n248 --> n261
    class n261 normalNode
    n262[value]
    n261 --> n262
    class n262 leafNode
    n263[source]
    n261 --> n263
    class n263 leafNode
    n264(n_i)
    n248 --> n264
    class n264 complexNode
    n265[hydrogen]
    n264 --> n265
    class n265 normalNode
    n266[value]
    n265 --> n266
    class n266 leafNode
    n267[source]
    n265 --> n267
    class n267 leafNode
    n268[deuterium]
    n264 --> n268
    class n268 normalNode
    n269[value]
    n268 --> n269
    class n269 leafNode
    n270[source]
    n268 --> n270
    class n270 leafNode
    n271[tritium]
    n264 --> n271
    class n271 normalNode
    n272[value]
    n271 --> n272
    class n272 leafNode
    n273[source]
    n271 --> n273
    class n273 leafNode
    n274[deuterium_tritium]
    n264 --> n274
    class n274 normalNode
    n275[value]
    n274 --> n275
    class n275 leafNode
    n276[source]
    n274 --> n276
    class n276 leafNode
    n277[helium_3]
    n264 --> n277
    class n277 normalNode
    n278[value]
    n277 --> n278
    class n278 leafNode
    n279[source]
    n277 --> n279
    class n279 leafNode
    n280[helium_4]
    n264 --> n280
    class n280 normalNode
    n281[value]
    n280 --> n281
    class n281 leafNode
    n282[source]
    n280 --> n282
    class n282 leafNode
    n283[beryllium]
    n264 --> n283
    class n283 normalNode
    n284[value]
    n283 --> n284
    class n284 leafNode
    n285[source]
    n283 --> n285
    class n285 leafNode
    n286[boron]
    n264 --> n286
    class n286 normalNode
    n287[value]
    n286 --> n287
    class n287 leafNode
    n288[source]
    n286 --> n288
    class n288 leafNode
    n289[lithium]
    n264 --> n289
    class n289 normalNode
    n290[value]
    n289 --> n290
    class n290 leafNode
    n291[source]
    n289 --> n291
    class n291 leafNode
    n292[carbon]
    n264 --> n292
    class n292 normalNode
    n293[value]
    n292 --> n293
    class n293 leafNode
    n294[source]
    n292 --> n294
    class n294 leafNode
    n295[nitrogen]
    n264 --> n295
    class n295 normalNode
    n296[value]
    n295 --> n296
    class n296 leafNode
    n297[source]
    n295 --> n297
    class n297 leafNode
    n298[neon]
    n264 --> n298
    class n298 normalNode
    n299[value]
    n298 --> n299
    class n299 leafNode
    n300[source]
    n298 --> n300
    class n300 leafNode
    n301[argon]
    n264 --> n301
    class n301 normalNode
    n302[value]
    n301 --> n302
    class n302 leafNode
    n303[source]
    n301 --> n303
    class n303 leafNode
    n304[xenon]
    n264 --> n304
    class n304 normalNode
    n305[value]
    n304 --> n305
    class n305 leafNode
    n306[source]
    n304 --> n306
    class n306 leafNode
    n307[oxygen]
    n264 --> n307
    class n307 normalNode
    n308[value]
    n307 --> n308
    class n308 leafNode
    n309[source]
    n307 --> n309
    class n309 leafNode
    n310[tungsten]
    n264 --> n310
    class n310 normalNode
    n311[value]
    n310 --> n311
    class n311 leafNode
    n312[source]
    n310 --> n312
    class n312 leafNode
    n313[iron]
    n264 --> n313
    class n313 normalNode
    n314[value]
    n313 --> n314
    class n314 leafNode
    n315[source]
    n313 --> n315
    class n315 leafNode
    n316[krypton]
    n264 --> n316
    class n316 normalNode
    n317[value]
    n316 --> n317
    class n317 leafNode
    n318[source]
    n316 --> n318
    class n318 leafNode
    n319[n_i_total]
    n248 --> n319
    class n319 normalNode
    n320[value]
    n319 --> n320
    class n320 leafNode
    n321[source]
    n319 --> n321
    class n321 leafNode
    n322[zeff]
    n248 --> n322
    class n322 normalNode
    n323[value]
    n322 --> n323
    class n323 leafNode
    n324[source]
    n322 --> n324
    class n324 leafNode
    n325[momentum_phi]
    n248 --> n325
    class n325 normalNode
    n326[value]
    n325 --> n326
    class n326 leafNode
    n327[source]
    n325 --> n327
    class n327 leafNode
    n328(velocity_phi)
    n248 --> n328
    class n328 complexNode
    n329[hydrogen]
    n328 --> n329
    class n329 normalNode
    n330[value]
    n329 --> n330
    class n330 leafNode
    n331[source]
    n329 --> n331
    class n331 leafNode
    n332[deuterium]
    n328 --> n332
    class n332 normalNode
    n333[value]
    n332 --> n333
    class n333 leafNode
    n334[source]
    n332 --> n334
    class n334 leafNode
    n335[tritium]
    n328 --> n335
    class n335 normalNode
    n336[value]
    n335 --> n336
    class n336 leafNode
    n337[source]
    n335 --> n337
    class n337 leafNode
    n338[deuterium_tritium]
    n328 --> n338
    class n338 normalNode
    n339[value]
    n338 --> n339
    class n339 leafNode
    n340[source]
    n338 --> n340
    class n340 leafNode
    n341[helium_3]
    n328 --> n341
    class n341 normalNode
    n342[value]
    n341 --> n342
    class n342 leafNode
    n343[source]
    n341 --> n343
    class n343 leafNode
    n344[helium_4]
    n328 --> n344
    class n344 normalNode
    n345[value]
    n344 --> n345
    class n345 leafNode
    n346[source]
    n344 --> n346
    class n346 leafNode
    n347[beryllium]
    n328 --> n347
    class n347 normalNode
    n348[value]
    n347 --> n348
    class n348 leafNode
    n349[source]
    n347 --> n349
    class n349 leafNode
    n350[lithium]
    n328 --> n350
    class n350 normalNode
    n351[value]
    n350 --> n351
    class n351 leafNode
    n352[source]
    n350 --> n352
    class n352 leafNode
    n353[carbon]
    n328 --> n353
    class n353 normalNode
    n354[value]
    n353 --> n354
    class n354 leafNode
    n355[source]
    n353 --> n355
    class n355 leafNode
    n356[nitrogen]
    n328 --> n356
    class n356 normalNode
    n357[value]
    n356 --> n357
    class n357 leafNode
    n358[source]
    n356 --> n358
    class n358 leafNode
    n359[neon]
    n328 --> n359
    class n359 normalNode
    n360[value]
    n359 --> n360
    class n360 leafNode
    n361[source]
    n359 --> n361
    class n361 leafNode
    n362[argon]
    n328 --> n362
    class n362 normalNode
    n363[value]
    n362 --> n363
    class n363 leafNode
    n364[source]
    n362 --> n364
    class n364 leafNode
    n365[xenon]
    n328 --> n365
    class n365 normalNode
    n366[value]
    n365 --> n366
    class n366 leafNode
    n367[source]
    n365 --> n367
    class n367 leafNode
    n368[oxygen]
    n328 --> n368
    class n368 normalNode
    n369[value]
    n368 --> n369
    class n369 leafNode
    n370[source]
    n368 --> n370
    class n370 leafNode
    n371[tungsten]
    n328 --> n371
    class n371 normalNode
    n372[value]
    n371 --> n372
    class n372 leafNode
    n373[source]
    n371 --> n373
    class n373 leafNode
    n374[iron]
    n328 --> n374
    class n374 normalNode
    n375[value]
    n374 --> n375
    class n375 leafNode
    n376[source]
    n374 --> n376
    class n376 leafNode
    n377[krypton]
    n328 --> n377
    class n377 normalNode
    n378[value]
    n377 --> n378
    class n378 leafNode
    n379[source]
    n377 --> n379
    class n379 leafNode
    n380[q]
    n248 --> n380
    class n380 normalNode
    n381[value]
    n380 --> n381
    class n381 leafNode
    n382[source]
    n380 --> n382
    class n382 leafNode
    n383[magnetic_shear]
    n248 --> n383
    class n383 normalNode
    n384[value]
    n383 --> n384
    class n384 leafNode
    n385[source]
    n383 --> n385
    class n385 leafNode
    n386[b_field_tor]
    n248 --> n386
    class n386 normalNode
    n387[value]
    n386 --> n387
    class n387 leafNode
    n388[source]
    n386 --> n388
    class n388 leafNode
    n389[b_field_phi]
    n248 --> n389
    class n389 normalNode
    n390[value]
    n389 --> n390
    class n390 leafNode
    n391[source]
    n389 --> n391
    class n391 leafNode
    n392[e_field_parallel]
    n248 --> n392
    class n392 normalNode
    n393[value]
    n392 --> n393
    class n393 leafNode
    n394[source]
    n392 --> n394
    class n394 leafNode
    n395(separatrix)
    n247 --> n395
    class n395 complexNode
    n396[position]
    n395 --> n396
    class n396 normalNode
    n397[rho_tor_norm]
    n396 --> n397
    class n397 leafNode
    n398[rho_tor]
    n396 --> n398
    class n398 leafNode
    n399[psi]
    n396 --> n399
    class n399 leafNode
    n400[t_e]
    n395 --> n400
    class n400 normalNode
    n401[value]
    n400 --> n401
    class n401 leafNode
    n402[source]
    n400 --> n402
    class n402 leafNode
    n403[t_i_average]
    n395 --> n403
    class n403 normalNode
    n404[value]
    n403 --> n404
    class n404 leafNode
    n405[source]
    n403 --> n405
    class n405 leafNode
    n406[n_e]
    n395 --> n406
    class n406 normalNode
    n407[value]
    n406 --> n407
    class n407 leafNode
    n408[source]
    n406 --> n408
    class n408 leafNode
    n409(n_i)
    n395 --> n409
    class n409 complexNode
    n410[hydrogen]
    n409 --> n410
    class n410 normalNode
    n411[value]
    n410 --> n411
    class n411 leafNode
    n412[source]
    n410 --> n412
    class n412 leafNode
    n413[deuterium]
    n409 --> n413
    class n413 normalNode
    n414[value]
    n413 --> n414
    class n414 leafNode
    n415[source]
    n413 --> n415
    class n415 leafNode
    n416[tritium]
    n409 --> n416
    class n416 normalNode
    n417[value]
    n416 --> n417
    class n417 leafNode
    n418[source]
    n416 --> n418
    class n418 leafNode
    n419[deuterium_tritium]
    n409 --> n419
    class n419 normalNode
    n420[value]
    n419 --> n420
    class n420 leafNode
    n421[source]
    n419 --> n421
    class n421 leafNode
    n422[helium_3]
    n409 --> n422
    class n422 normalNode
    n423[value]
    n422 --> n423
    class n423 leafNode
    n424[source]
    n422 --> n424
    class n424 leafNode
    n425[helium_4]
    n409 --> n425
    class n425 normalNode
    n426[value]
    n425 --> n426
    class n426 leafNode
    n427[source]
    n425 --> n427
    class n427 leafNode
    n428[beryllium]
    n409 --> n428
    class n428 normalNode
    n429[value]
    n428 --> n429
    class n429 leafNode
    n430[source]
    n428 --> n430
    class n430 leafNode
    n431[boron]
    n409 --> n431
    class n431 normalNode
    n432[value]
    n431 --> n432
    class n432 leafNode
    n433[source]
    n431 --> n433
    class n433 leafNode
    n434[lithium]
    n409 --> n434
    class n434 normalNode
    n435[value]
    n434 --> n435
    class n435 leafNode
    n436[source]
    n434 --> n436
    class n436 leafNode
    n437[carbon]
    n409 --> n437
    class n437 normalNode
    n438[value]
    n437 --> n438
    class n438 leafNode
    n439[source]
    n437 --> n439
    class n439 leafNode
    n440[nitrogen]
    n409 --> n440
    class n440 normalNode
    n441[value]
    n440 --> n441
    class n441 leafNode
    n442[source]
    n440 --> n442
    class n442 leafNode
    n443[neon]
    n409 --> n443
    class n443 normalNode
    n444[value]
    n443 --> n444
    class n444 leafNode
    n445[source]
    n443 --> n445
    class n445 leafNode
    n446[argon]
    n409 --> n446
    class n446 normalNode
    n447[value]
    n446 --> n447
    class n447 leafNode
    n448[source]
    n446 --> n448
    class n448 leafNode
    n449[xenon]
    n409 --> n449
    class n449 normalNode
    n450[value]
    n449 --> n450
    class n450 leafNode
    n451[source]
    n449 --> n451
    class n451 leafNode
    n452[oxygen]
    n409 --> n452
    class n452 normalNode
    n453[value]
    n452 --> n453
    class n453 leafNode
    n454[source]
    n452 --> n454
    class n454 leafNode
    n455[tungsten]
    n409 --> n455
    class n455 normalNode
    n456[value]
    n455 --> n456
    class n456 leafNode
    n457[source]
    n455 --> n457
    class n457 leafNode
    n458[iron]
    n409 --> n458
    class n458 normalNode
    n459[value]
    n458 --> n459
    class n459 leafNode
    n460[source]
    n458 --> n460
    class n460 leafNode
    n461[krypton]
    n409 --> n461
    class n461 normalNode
    n462[value]
    n461 --> n462
    class n462 leafNode
    n463[source]
    n461 --> n463
    class n463 leafNode
    n464[n_i_total]
    n395 --> n464
    class n464 normalNode
    n465[value]
    n464 --> n465
    class n465 leafNode
    n466[source]
    n464 --> n466
    class n466 leafNode
    n467[zeff]
    n395 --> n467
    class n467 normalNode
    n468[value]
    n467 --> n468
    class n468 leafNode
    n469[source]
    n467 --> n469
    class n469 leafNode
    n470[momentum_phi]
    n395 --> n470
    class n470 normalNode
    n471[value]
    n470 --> n471
    class n471 leafNode
    n472[source]
    n470 --> n472
    class n472 leafNode
    n473(velocity_phi)
    n395 --> n473
    class n473 complexNode
    n474[hydrogen]
    n473 --> n474
    class n474 normalNode
    n475[value]
    n474 --> n475
    class n475 leafNode
    n476[source]
    n474 --> n476
    class n476 leafNode
    n477[deuterium]
    n473 --> n477
    class n477 normalNode
    n478[value]
    n477 --> n478
    class n478 leafNode
    n479[source]
    n477 --> n479
    class n479 leafNode
    n480[tritium]
    n473 --> n480
    class n480 normalNode
    n481[value]
    n480 --> n481
    class n481 leafNode
    n482[source]
    n480 --> n482
    class n482 leafNode
    n483[deuterium_tritium]
    n473 --> n483
    class n483 normalNode
    n484[value]
    n483 --> n484
    class n484 leafNode
    n485[source]
    n483 --> n485
    class n485 leafNode
    n486[helium_3]
    n473 --> n486
    class n486 normalNode
    n487[value]
    n486 --> n487
    class n487 leafNode
    n488[source]
    n486 --> n488
    class n488 leafNode
    n489[helium_4]
    n473 --> n489
    class n489 normalNode
    n490[value]
    n489 --> n490
    class n490 leafNode
    n491[source]
    n489 --> n491
    class n491 leafNode
    n492[beryllium]
    n473 --> n492
    class n492 normalNode
    n493[value]
    n492 --> n493
    class n493 leafNode
    n494[source]
    n492 --> n494
    class n494 leafNode
    n495[lithium]
    n473 --> n495
    class n495 normalNode
    n496[value]
    n495 --> n496
    class n496 leafNode
    n497[source]
    n495 --> n497
    class n497 leafNode
    n498[carbon]
    n473 --> n498
    class n498 normalNode
    n499[value]
    n498 --> n499
    class n499 leafNode
    n500[source]
    n498 --> n500
    class n500 leafNode
    n501[nitrogen]
    n473 --> n501
    class n501 normalNode
    n502[value]
    n501 --> n502
    class n502 leafNode
    n503[source]
    n501 --> n503
    class n503 leafNode
    n504[neon]
    n473 --> n504
    class n504 normalNode
    n505[value]
    n504 --> n505
    class n505 leafNode
    n506[source]
    n504 --> n506
    class n506 leafNode
    n507[argon]
    n473 --> n507
    class n507 normalNode
    n508[value]
    n507 --> n508
    class n508 leafNode
    n509[source]
    n507 --> n509
    class n509 leafNode
    n510[xenon]
    n473 --> n510
    class n510 normalNode
    n511[value]
    n510 --> n511
    class n511 leafNode
    n512[source]
    n510 --> n512
    class n512 leafNode
    n513[oxygen]
    n473 --> n513
    class n513 normalNode
    n514[value]
    n513 --> n514
    class n514 leafNode
    n515[source]
    n513 --> n515
    class n515 leafNode
    n516[tungsten]
    n473 --> n516
    class n516 normalNode
    n517[value]
    n516 --> n517
    class n517 leafNode
    n518[source]
    n516 --> n518
    class n518 leafNode
    n519[iron]
    n473 --> n519
    class n519 normalNode
    n520[value]
    n519 --> n520
    class n520 leafNode
    n521[source]
    n519 --> n521
    class n521 leafNode
    n522[krypton]
    n473 --> n522
    class n522 normalNode
    n523[value]
    n522 --> n523
    class n523 leafNode
    n524[source]
    n522 --> n524
    class n524 leafNode
    n525[q]
    n395 --> n525
    class n525 normalNode
    n526[value]
    n525 --> n526
    class n526 leafNode
    n527[source]
    n525 --> n527
    class n527 leafNode
    n528[magnetic_shear]
    n395 --> n528
    class n528 normalNode
    n529[value]
    n528 --> n529
    class n529 leafNode
    n530[source]
    n528 --> n530
    class n530 leafNode
    n531[e_field_parallel]
    n395 --> n531
    class n531 normalNode
    n532[value]
    n531 --> n532
    class n532 leafNode
    n533[source]
    n531 --> n533
    class n533 leafNode
    n534(separatrix_average)
    n247 --> n534
    class n534 complexNode
    n535[position]
    n534 --> n535
    class n535 normalNode
    n536[rho_tor_norm]
    n535 --> n536
    class n536 leafNode
    n537[rho_tor]
    n535 --> n537
    class n537 leafNode
    n538[psi]
    n535 --> n538
    class n538 leafNode
    n539[t_e]
    n534 --> n539
    class n539 normalNode
    n540[value]
    n539 --> n540
    class n540 leafNode
    n541[source]
    n539 --> n541
    class n541 leafNode
    n542[t_i_average]
    n534 --> n542
    class n542 normalNode
    n543[value]
    n542 --> n543
    class n543 leafNode
    n544[source]
    n542 --> n544
    class n544 leafNode
    n545[n_e]
    n534 --> n545
    class n545 normalNode
    n546[value]
    n545 --> n546
    class n546 leafNode
    n547[source]
    n545 --> n547
    class n547 leafNode
    n548(n_i)
    n534 --> n548
    class n548 complexNode
    n549[hydrogen]
    n548 --> n549
    class n549 normalNode
    n550[value]
    n549 --> n550
    class n550 leafNode
    n551[source]
    n549 --> n551
    class n551 leafNode
    n552[deuterium]
    n548 --> n552
    class n552 normalNode
    n553[value]
    n552 --> n553
    class n553 leafNode
    n554[source]
    n552 --> n554
    class n554 leafNode
    n555[tritium]
    n548 --> n555
    class n555 normalNode
    n556[value]
    n555 --> n556
    class n556 leafNode
    n557[source]
    n555 --> n557
    class n557 leafNode
    n558[deuterium_tritium]
    n548 --> n558
    class n558 normalNode
    n559[value]
    n558 --> n559
    class n559 leafNode
    n560[source]
    n558 --> n560
    class n560 leafNode
    n561[helium_3]
    n548 --> n561
    class n561 normalNode
    n562[value]
    n561 --> n562
    class n562 leafNode
    n563[source]
    n561 --> n563
    class n563 leafNode
    n564[helium_4]
    n548 --> n564
    class n564 normalNode
    n565[value]
    n564 --> n565
    class n565 leafNode
    n566[source]
    n564 --> n566
    class n566 leafNode
    n567[beryllium]
    n548 --> n567
    class n567 normalNode
    n568[value]
    n567 --> n568
    class n568 leafNode
    n569[source]
    n567 --> n569
    class n569 leafNode
    n570[boron]
    n548 --> n570
    class n570 normalNode
    n571[value]
    n570 --> n571
    class n571 leafNode
    n572[source]
    n570 --> n572
    class n572 leafNode
    n573[lithium]
    n548 --> n573
    class n573 normalNode
    n574[value]
    n573 --> n574
    class n574 leafNode
    n575[source]
    n573 --> n575
    class n575 leafNode
    n576[carbon]
    n548 --> n576
    class n576 normalNode
    n577[value]
    n576 --> n577
    class n577 leafNode
    n578[source]
    n576 --> n578
    class n578 leafNode
    n579[nitrogen]
    n548 --> n579
    class n579 normalNode
    n580[value]
    n579 --> n580
    class n580 leafNode
    n581[source]
    n579 --> n581
    class n581 leafNode
    n582[neon]
    n548 --> n582
    class n582 normalNode
    n583[value]
    n582 --> n583
    class n583 leafNode
    n584[source]
    n582 --> n584
    class n584 leafNode
    n585[argon]
    n548 --> n585
    class n585 normalNode
    n586[value]
    n585 --> n586
    class n586 leafNode
    n587[source]
    n585 --> n587
    class n587 leafNode
    n588[xenon]
    n548 --> n588
    class n588 normalNode
    n589[value]
    n588 --> n589
    class n589 leafNode
    n590[source]
    n588 --> n590
    class n590 leafNode
    n591[oxygen]
    n548 --> n591
    class n591 normalNode
    n592[value]
    n591 --> n592
    class n592 leafNode
    n593[source]
    n591 --> n593
    class n593 leafNode
    n594[tungsten]
    n548 --> n594
    class n594 normalNode
    n595[value]
    n594 --> n595
    class n595 leafNode
    n596[source]
    n594 --> n596
    class n596 leafNode
    n597[iron]
    n548 --> n597
    class n597 normalNode
    n598[value]
    n597 --> n598
    class n598 leafNode
    n599[source]
    n597 --> n599
    class n599 leafNode
    n600[krypton]
    n548 --> n600
    class n600 normalNode
    n601[value]
    n600 --> n601
    class n601 leafNode
    n602[source]
    n600 --> n602
    class n602 leafNode
    n603[n_i_total]
    n534 --> n603
    class n603 normalNode
    n604[value]
    n603 --> n604
    class n604 leafNode
    n605[source]
    n603 --> n605
    class n605 leafNode
    n606[zeff]
    n534 --> n606
    class n606 normalNode
    n607[value]
    n606 --> n607
    class n607 leafNode
    n608[source]
    n606 --> n608
    class n608 leafNode
    n609[momentum_phi]
    n534 --> n609
    class n609 normalNode
    n610[value]
    n609 --> n610
    class n610 leafNode
    n611[source]
    n609 --> n611
    class n611 leafNode
    n612(velocity_phi)
    n534 --> n612
    class n612 complexNode
    n613[hydrogen]
    n612 --> n613
    class n613 normalNode
    n614[value]
    n613 --> n614
    class n614 leafNode
    n615[source]
    n613 --> n615
    class n615 leafNode
    n616[deuterium]
    n612 --> n616
    class n616 normalNode
    n617[value]
    n616 --> n617
    class n617 leafNode
    n618[source]
    n616 --> n618
    class n618 leafNode
    n619[tritium]
    n612 --> n619
    class n619 normalNode
    n620[value]
    n619 --> n620
    class n620 leafNode
    n621[source]
    n619 --> n621
    class n621 leafNode
    n622[deuterium_tritium]
    n612 --> n622
    class n622 normalNode
    n623[value]
    n622 --> n623
    class n623 leafNode
    n624[source]
    n622 --> n624
    class n624 leafNode
    n625[helium_3]
    n612 --> n625
    class n625 normalNode
    n626[value]
    n625 --> n626
    class n626 leafNode
    n627[source]
    n625 --> n627
    class n627 leafNode
    n628[helium_4]
    n612 --> n628
    class n628 normalNode
    n629[value]
    n628 --> n629
    class n629 leafNode
    n630[source]
    n628 --> n630
    class n630 leafNode
    n631[beryllium]
    n612 --> n631
    class n631 normalNode
    n632[value]
    n631 --> n632
    class n632 leafNode
    n633[source]
    n631 --> n633
    class n633 leafNode
    n634[lithium]
    n612 --> n634
    class n634 normalNode
    n635[value]
    n634 --> n635
    class n635 leafNode
    n636[source]
    n634 --> n636
    class n636 leafNode
    n637[carbon]
    n612 --> n637
    class n637 normalNode
    n638[value]
    n637 --> n638
    class n638 leafNode
    n639[source]
    n637 --> n639
    class n639 leafNode
    n640[nitrogen]
    n612 --> n640
    class n640 normalNode
    n641[value]
    n640 --> n641
    class n641 leafNode
    n642[source]
    n640 --> n642
    class n642 leafNode
    n643[neon]
    n612 --> n643
    class n643 normalNode
    n644[value]
    n643 --> n644
    class n644 leafNode
    n645[source]
    n643 --> n645
    class n645 leafNode
    n646[argon]
    n612 --> n646
    class n646 normalNode
    n647[value]
    n646 --> n647
    class n647 leafNode
    n648[source]
    n646 --> n648
    class n648 leafNode
    n649[xenon]
    n612 --> n649
    class n649 normalNode
    n650[value]
    n649 --> n650
    class n650 leafNode
    n651[source]
    n649 --> n651
    class n651 leafNode
    n652[oxygen]
    n612 --> n652
    class n652 normalNode
    n653[value]
    n652 --> n653
    class n653 leafNode
    n654[source]
    n652 --> n654
    class n654 leafNode
    n655[tungsten]
    n612 --> n655
    class n655 normalNode
    n656[value]
    n655 --> n656
    class n656 leafNode
    n657[source]
    n655 --> n657
    class n657 leafNode
    n658[iron]
    n612 --> n658
    class n658 normalNode
    n659[value]
    n658 --> n659
    class n659 leafNode
    n660[source]
    n658 --> n660
    class n660 leafNode
    n661[krypton]
    n612 --> n661
    class n661 normalNode
    n662[value]
    n661 --> n662
    class n662 leafNode
    n663[source]
    n661 --> n663
    class n663 leafNode
    n664[q]
    n534 --> n664
    class n664 normalNode
    n665[value]
    n664 --> n665
    class n665 leafNode
    n666[source]
    n664 --> n666
    class n666 leafNode
    n667[magnetic_shear]
    n534 --> n667
    class n667 normalNode
    n668[value]
    n667 --> n668
    class n668 leafNode
    n669[source]
    n667 --> n669
    class n669 leafNode
    n670[e_field_parallel]
    n534 --> n670
    class n670 normalNode
    n671[value]
    n670 --> n671
    class n671 leafNode
    n672[source]
    n670 --> n672
    class n672 leafNode
    n673(pedestal)
    n247 --> n673
    class n673 complexNode
    n674[position]
    n673 --> n674
    class n674 normalNode
    n675[rho_tor_norm]
    n674 --> n675
    class n675 leafNode
    n676[rho_tor]
    n674 --> n676
    class n676 leafNode
    n677[psi]
    n674 --> n677
    class n677 leafNode
    n678[t_e]
    n673 --> n678
    class n678 normalNode
    n679[value]
    n678 --> n679
    class n679 leafNode
    n680[source]
    n678 --> n680
    class n680 leafNode
    n681[t_i_average]
    n673 --> n681
    class n681 normalNode
    n682[value]
    n681 --> n682
    class n682 leafNode
    n683[source]
    n681 --> n683
    class n683 leafNode
    n684[n_e]
    n673 --> n684
    class n684 normalNode
    n685[value]
    n684 --> n685
    class n685 leafNode
    n686[source]
    n684 --> n686
    class n686 leafNode
    n687(n_i)
    n673 --> n687
    class n687 complexNode
    n688[hydrogen]
    n687 --> n688
    class n688 normalNode
    n689[value]
    n688 --> n689
    class n689 leafNode
    n690[source]
    n688 --> n690
    class n690 leafNode
    n691[deuterium]
    n687 --> n691
    class n691 normalNode
    n692[value]
    n691 --> n692
    class n692 leafNode
    n693[source]
    n691 --> n693
    class n693 leafNode
    n694[tritium]
    n687 --> n694
    class n694 normalNode
    n695[value]
    n694 --> n695
    class n695 leafNode
    n696[source]
    n694 --> n696
    class n696 leafNode
    n697[deuterium_tritium]
    n687 --> n697
    class n697 normalNode
    n698[value]
    n697 --> n698
    class n698 leafNode
    n699[source]
    n697 --> n699
    class n699 leafNode
    n700[helium_3]
    n687 --> n700
    class n700 normalNode
    n701[value]
    n700 --> n701
    class n701 leafNode
    n702[source]
    n700 --> n702
    class n702 leafNode
    n703[helium_4]
    n687 --> n703
    class n703 normalNode
    n704[value]
    n703 --> n704
    class n704 leafNode
    n705[source]
    n703 --> n705
    class n705 leafNode
    n706[beryllium]
    n687 --> n706
    class n706 normalNode
    n707[value]
    n706 --> n707
    class n707 leafNode
    n708[source]
    n706 --> n708
    class n708 leafNode
    n709[boron]
    n687 --> n709
    class n709 normalNode
    n710[value]
    n709 --> n710
    class n710 leafNode
    n711[source]
    n709 --> n711
    class n711 leafNode
    n712[lithium]
    n687 --> n712
    class n712 normalNode
    n713[value]
    n712 --> n713
    class n713 leafNode
    n714[source]
    n712 --> n714
    class n714 leafNode
    n715[carbon]
    n687 --> n715
    class n715 normalNode
    n716[value]
    n715 --> n716
    class n716 leafNode
    n717[source]
    n715 --> n717
    class n717 leafNode
    n718[nitrogen]
    n687 --> n718
    class n718 normalNode
    n719[value]
    n718 --> n719
    class n719 leafNode
    n720[source]
    n718 --> n720
    class n720 leafNode
    n721[neon]
    n687 --> n721
    class n721 normalNode
    n722[value]
    n721 --> n722
    class n722 leafNode
    n723[source]
    n721 --> n723
    class n723 leafNode
    n724[argon]
    n687 --> n724
    class n724 normalNode
    n725[value]
    n724 --> n725
    class n725 leafNode
    n726[source]
    n724 --> n726
    class n726 leafNode
    n727[xenon]
    n687 --> n727
    class n727 normalNode
    n728[value]
    n727 --> n728
    class n728 leafNode
    n729[source]
    n727 --> n729
    class n729 leafNode
    n730[oxygen]
    n687 --> n730
    class n730 normalNode
    n731[value]
    n730 --> n731
    class n731 leafNode
    n732[source]
    n730 --> n732
    class n732 leafNode
    n733[tungsten]
    n687 --> n733
    class n733 normalNode
    n734[value]
    n733 --> n734
    class n734 leafNode
    n735[source]
    n733 --> n735
    class n735 leafNode
    n736[iron]
    n687 --> n736
    class n736 normalNode
    n737[value]
    n736 --> n737
    class n737 leafNode
    n738[source]
    n736 --> n738
    class n738 leafNode
    n739[krypton]
    n687 --> n739
    class n739 normalNode
    n740[value]
    n739 --> n740
    class n740 leafNode
    n741[source]
    n739 --> n741
    class n741 leafNode
    n742[n_i_total]
    n673 --> n742
    class n742 normalNode
    n743[value]
    n742 --> n743
    class n743 leafNode
    n744[source]
    n742 --> n744
    class n744 leafNode
    n745[zeff]
    n673 --> n745
    class n745 normalNode
    n746[value]
    n745 --> n746
    class n746 leafNode
    n747[source]
    n745 --> n747
    class n747 leafNode
    n748[momentum_phi]
    n673 --> n748
    class n748 normalNode
    n749[value]
    n748 --> n749
    class n749 leafNode
    n750[source]
    n748 --> n750
    class n750 leafNode
    n751(velocity_phi)
    n673 --> n751
    class n751 complexNode
    n752[hydrogen]
    n751 --> n752
    class n752 normalNode
    n753[value]
    n752 --> n753
    class n753 leafNode
    n754[source]
    n752 --> n754
    class n754 leafNode
    n755[deuterium]
    n751 --> n755
    class n755 normalNode
    n756[value]
    n755 --> n756
    class n756 leafNode
    n757[source]
    n755 --> n757
    class n757 leafNode
    n758[tritium]
    n751 --> n758
    class n758 normalNode
    n759[value]
    n758 --> n759
    class n759 leafNode
    n760[source]
    n758 --> n760
    class n760 leafNode
    n761[deuterium_tritium]
    n751 --> n761
    class n761 normalNode
    n762[value]
    n761 --> n762
    class n762 leafNode
    n763[source]
    n761 --> n763
    class n763 leafNode
    n764[helium_3]
    n751 --> n764
    class n764 normalNode
    n765[value]
    n764 --> n765
    class n765 leafNode
    n766[source]
    n764 --> n766
    class n766 leafNode
    n767[helium_4]
    n751 --> n767
    class n767 normalNode
    n768[value]
    n767 --> n768
    class n768 leafNode
    n769[source]
    n767 --> n769
    class n769 leafNode
    n770[beryllium]
    n751 --> n770
    class n770 normalNode
    n771[value]
    n770 --> n771
    class n771 leafNode
    n772[source]
    n770 --> n772
    class n772 leafNode
    n773[lithium]
    n751 --> n773
    class n773 normalNode
    n774[value]
    n773 --> n774
    class n774 leafNode
    n775[source]
    n773 --> n775
    class n775 leafNode
    n776[carbon]
    n751 --> n776
    class n776 normalNode
    n777[value]
    n776 --> n777
    class n777 leafNode
    n778[source]
    n776 --> n778
    class n778 leafNode
    n779[nitrogen]
    n751 --> n779
    class n779 normalNode
    n780[value]
    n779 --> n780
    class n780 leafNode
    n781[source]
    n779 --> n781
    class n781 leafNode
    n782[neon]
    n751 --> n782
    class n782 normalNode
    n783[value]
    n782 --> n783
    class n783 leafNode
    n784[source]
    n782 --> n784
    class n784 leafNode
    n785[argon]
    n751 --> n785
    class n785 normalNode
    n786[value]
    n785 --> n786
    class n786 leafNode
    n787[source]
    n785 --> n787
    class n787 leafNode
    n788[xenon]
    n751 --> n788
    class n788 normalNode
    n789[value]
    n788 --> n789
    class n789 leafNode
    n790[source]
    n788 --> n790
    class n790 leafNode
    n791[oxygen]
    n751 --> n791
    class n791 normalNode
    n792[value]
    n791 --> n792
    class n792 leafNode
    n793[source]
    n791 --> n793
    class n793 leafNode
    n794[tungsten]
    n751 --> n794
    class n794 normalNode
    n795[value]
    n794 --> n795
    class n795 leafNode
    n796[source]
    n794 --> n796
    class n796 leafNode
    n797[iron]
    n751 --> n797
    class n797 normalNode
    n798[value]
    n797 --> n798
    class n798 leafNode
    n799[source]
    n797 --> n799
    class n799 leafNode
    n800[krypton]
    n751 --> n800
    class n800 normalNode
    n801[value]
    n800 --> n801
    class n801 leafNode
    n802[source]
    n800 --> n802
    class n802 leafNode
    n803[q]
    n673 --> n803
    class n803 normalNode
    n804[value]
    n803 --> n804
    class n804 leafNode
    n805[source]
    n803 --> n805
    class n805 leafNode
    n806[magnetic_shear]
    n673 --> n806
    class n806 normalNode
    n807[value]
    n806 --> n807
    class n807 leafNode
    n808[source]
    n806 --> n808
    class n808 leafNode
    n809[e_field_parallel]
    n673 --> n809
    class n809 normalNode
    n810[value]
    n809 --> n810
    class n810 leafNode
    n811[source]
    n809 --> n811
    class n811 leafNode
    n812(itb)
    n247 --> n812
    class n812 complexNode
    n813[position]
    n812 --> n813
    class n813 normalNode
    n814[rho_tor_norm]
    n813 --> n814
    class n814 leafNode
    n815[rho_tor]
    n813 --> n815
    class n815 leafNode
    n816[psi]
    n813 --> n816
    class n816 leafNode
    n817[t_e]
    n812 --> n817
    class n817 normalNode
    n818[value]
    n817 --> n818
    class n818 leafNode
    n819[source]
    n817 --> n819
    class n819 leafNode
    n820[t_i_average]
    n812 --> n820
    class n820 normalNode
    n821[value]
    n820 --> n821
    class n821 leafNode
    n822[source]
    n820 --> n822
    class n822 leafNode
    n823[n_e]
    n812 --> n823
    class n823 normalNode
    n824[value]
    n823 --> n824
    class n824 leafNode
    n825[source]
    n823 --> n825
    class n825 leafNode
    n826(n_i)
    n812 --> n826
    class n826 complexNode
    n827[hydrogen]
    n826 --> n827
    class n827 normalNode
    n828[value]
    n827 --> n828
    class n828 leafNode
    n829[source]
    n827 --> n829
    class n829 leafNode
    n830[deuterium]
    n826 --> n830
    class n830 normalNode
    n831[value]
    n830 --> n831
    class n831 leafNode
    n832[source]
    n830 --> n832
    class n832 leafNode
    n833[tritium]
    n826 --> n833
    class n833 normalNode
    n834[value]
    n833 --> n834
    class n834 leafNode
    n835[source]
    n833 --> n835
    class n835 leafNode
    n836[deuterium_tritium]
    n826 --> n836
    class n836 normalNode
    n837[value]
    n836 --> n837
    class n837 leafNode
    n838[source]
    n836 --> n838
    class n838 leafNode
    n839[helium_3]
    n826 --> n839
    class n839 normalNode
    n840[value]
    n839 --> n840
    class n840 leafNode
    n841[source]
    n839 --> n841
    class n841 leafNode
    n842[helium_4]
    n826 --> n842
    class n842 normalNode
    n843[value]
    n842 --> n843
    class n843 leafNode
    n844[source]
    n842 --> n844
    class n844 leafNode
    n845[beryllium]
    n826 --> n845
    class n845 normalNode
    n846[value]
    n845 --> n846
    class n846 leafNode
    n847[source]
    n845 --> n847
    class n847 leafNode
    n848[boron]
    n826 --> n848
    class n848 normalNode
    n849[value]
    n848 --> n849
    class n849 leafNode
    n850[source]
    n848 --> n850
    class n850 leafNode
    n851[lithium]
    n826 --> n851
    class n851 normalNode
    n852[value]
    n851 --> n852
    class n852 leafNode
    n853[source]
    n851 --> n853
    class n853 leafNode
    n854[carbon]
    n826 --> n854
    class n854 normalNode
    n855[value]
    n854 --> n855
    class n855 leafNode
    n856[source]
    n854 --> n856
    class n856 leafNode
    n857[nitrogen]
    n826 --> n857
    class n857 normalNode
    n858[value]
    n857 --> n858
    class n858 leafNode
    n859[source]
    n857 --> n859
    class n859 leafNode
    n860[neon]
    n826 --> n860
    class n860 normalNode
    n861[value]
    n860 --> n861
    class n861 leafNode
    n862[source]
    n860 --> n862
    class n862 leafNode
    n863[argon]
    n826 --> n863
    class n863 normalNode
    n864[value]
    n863 --> n864
    class n864 leafNode
    n865[source]
    n863 --> n865
    class n865 leafNode
    n866[xenon]
    n826 --> n866
    class n866 normalNode
    n867[value]
    n866 --> n867
    class n867 leafNode
    n868[source]
    n866 --> n868
    class n868 leafNode
    n869[oxygen]
    n826 --> n869
    class n869 normalNode
    n870[value]
    n869 --> n870
    class n870 leafNode
    n871[source]
    n869 --> n871
    class n871 leafNode
    n872[tungsten]
    n826 --> n872
    class n872 normalNode
    n873[value]
    n872 --> n873
    class n873 leafNode
    n874[source]
    n872 --> n874
    class n874 leafNode
    n875[iron]
    n826 --> n875
    class n875 normalNode
    n876[value]
    n875 --> n876
    class n876 leafNode
    n877[source]
    n875 --> n877
    class n877 leafNode
    n878[krypton]
    n826 --> n878
    class n878 normalNode
    n879[value]
    n878 --> n879
    class n879 leafNode
    n880[source]
    n878 --> n880
    class n880 leafNode
    n881[n_i_total]
    n812 --> n881
    class n881 normalNode
    n882[value]
    n881 --> n882
    class n882 leafNode
    n883[source]
    n881 --> n883
    class n883 leafNode
    n884[zeff]
    n812 --> n884
    class n884 normalNode
    n885[value]
    n884 --> n885
    class n885 leafNode
    n886[source]
    n884 --> n886
    class n886 leafNode
    n887[momentum_phi]
    n812 --> n887
    class n887 normalNode
    n888[value]
    n887 --> n888
    class n888 leafNode
    n889[source]
    n887 --> n889
    class n889 leafNode
    n890(velocity_phi)
    n812 --> n890
    class n890 complexNode
    n891[hydrogen]
    n890 --> n891
    class n891 normalNode
    n892[value]
    n891 --> n892
    class n892 leafNode
    n893[source]
    n891 --> n893
    class n893 leafNode
    n894[deuterium]
    n890 --> n894
    class n894 normalNode
    n895[value]
    n894 --> n895
    class n895 leafNode
    n896[source]
    n894 --> n896
    class n896 leafNode
    n897[tritium]
    n890 --> n897
    class n897 normalNode
    n898[value]
    n897 --> n898
    class n898 leafNode
    n899[source]
    n897 --> n899
    class n899 leafNode
    n900[deuterium_tritium]
    n890 --> n900
    class n900 normalNode
    n901[value]
    n900 --> n901
    class n901 leafNode
    n902[source]
    n900 --> n902
    class n902 leafNode
    n903[helium_3]
    n890 --> n903
    class n903 normalNode
    n904[value]
    n903 --> n904
    class n904 leafNode
    n905[source]
    n903 --> n905
    class n905 leafNode
    n906[helium_4]
    n890 --> n906
    class n906 normalNode
    n907[value]
    n906 --> n907
    class n907 leafNode
    n908[source]
    n906 --> n908
    class n908 leafNode
    n909[beryllium]
    n890 --> n909
    class n909 normalNode
    n910[value]
    n909 --> n910
    class n910 leafNode
    n911[source]
    n909 --> n911
    class n911 leafNode
    n912[lithium]
    n890 --> n912
    class n912 normalNode
    n913[value]
    n912 --> n913
    class n913 leafNode
    n914[source]
    n912 --> n914
    class n914 leafNode
    n915[carbon]
    n890 --> n915
    class n915 normalNode
    n916[value]
    n915 --> n916
    class n916 leafNode
    n917[source]
    n915 --> n917
    class n917 leafNode
    n918[nitrogen]
    n890 --> n918
    class n918 normalNode
    n919[value]
    n918 --> n919
    class n919 leafNode
    n920[source]
    n918 --> n920
    class n920 leafNode
    n921[neon]
    n890 --> n921
    class n921 normalNode
    n922[value]
    n921 --> n922
    class n922 leafNode
    n923[source]
    n921 --> n923
    class n923 leafNode
    n924[argon]
    n890 --> n924
    class n924 normalNode
    n925[value]
    n924 --> n925
    class n925 leafNode
    n926[source]
    n924 --> n926
    class n926 leafNode
    n927[xenon]
    n890 --> n927
    class n927 normalNode
    n928[value]
    n927 --> n928
    class n928 leafNode
    n929[source]
    n927 --> n929
    class n929 leafNode
    n930[oxygen]
    n890 --> n930
    class n930 normalNode
    n931[value]
    n930 --> n931
    class n931 leafNode
    n932[source]
    n930 --> n932
    class n932 leafNode
    n933[tungsten]
    n890 --> n933
    class n933 normalNode
    n934[value]
    n933 --> n934
    class n934 leafNode
    n935[source]
    n933 --> n935
    class n935 leafNode
    n936[iron]
    n890 --> n936
    class n936 normalNode
    n937[value]
    n936 --> n937
    class n937 leafNode
    n938[source]
    n936 --> n938
    class n938 leafNode
    n939[krypton]
    n890 --> n939
    class n939 normalNode
    n940[value]
    n939 --> n940
    class n940 leafNode
    n941[source]
    n939 --> n941
    class n941 leafNode
    n942[q]
    n812 --> n942
    class n942 normalNode
    n943[value]
    n942 --> n943
    class n943 leafNode
    n944[source]
    n942 --> n944
    class n944 leafNode
    n945[magnetic_shear]
    n812 --> n945
    class n945 normalNode
    n946[value]
    n945 --> n946
    class n946 leafNode
    n947[source]
    n945 --> n947
    class n947 leafNode
    n948[e_field_parallel]
    n812 --> n948
    class n948 normalNode
    n949[value]
    n948 --> n949
    class n949 leafNode
    n950[source]
    n948 --> n950
    class n950 leafNode
    n951(limiter)
    n247 --> n951
    class n951 complexNode
    n952[name]
    n951 --> n952
    class n952 normalNode
    n953[value]
    n952 --> n953
    class n953 leafNode
    n954[source]
    n952 --> n954
    class n954 leafNode
    n955[t_e]
    n951 --> n955
    class n955 normalNode
    n956[value]
    n955 --> n956
    class n956 leafNode
    n957[source]
    n955 --> n957
    class n957 leafNode
    n958[t_i_average]
    n951 --> n958
    class n958 normalNode
    n959[value]
    n958 --> n959
    class n959 leafNode
    n960[source]
    n958 --> n960
    class n960 leafNode
    n961[n_e]
    n951 --> n961
    class n961 normalNode
    n962[value]
    n961 --> n962
    class n962 leafNode
    n963[source]
    n961 --> n963
    class n963 leafNode
    n964(n_i)
    n951 --> n964
    class n964 complexNode
    n965[hydrogen]
    n964 --> n965
    class n965 normalNode
    n966[value]
    n965 --> n966
    class n966 leafNode
    n967[source]
    n965 --> n967
    class n967 leafNode
    n968[deuterium]
    n964 --> n968
    class n968 normalNode
    n969[value]
    n968 --> n969
    class n969 leafNode
    n970[source]
    n968 --> n970
    class n970 leafNode
    n971[tritium]
    n964 --> n971
    class n971 normalNode
    n972[value]
    n971 --> n972
    class n972 leafNode
    n973[source]
    n971 --> n973
    class n973 leafNode
    n974[deuterium_tritium]
    n964 --> n974
    class n974 normalNode
    n975[value]
    n974 --> n975
    class n975 leafNode
    n976[source]
    n974 --> n976
    class n976 leafNode
    n977[helium_3]
    n964 --> n977
    class n977 normalNode
    n978[value]
    n977 --> n978
    class n978 leafNode
    n979[source]
    n977 --> n979
    class n979 leafNode
    n980[helium_4]
    n964 --> n980
    class n980 normalNode
    n981[value]
    n980 --> n981
    class n981 leafNode
    n982[source]
    n980 --> n982
    class n982 leafNode
    n983[beryllium]
    n964 --> n983
    class n983 normalNode
    n984[value]
    n983 --> n984
    class n984 leafNode
    n985[source]
    n983 --> n985
    class n985 leafNode
    n986[boron]
    n964 --> n986
    class n986 normalNode
    n987[value]
    n986 --> n987
    class n987 leafNode
    n988[source]
    n986 --> n988
    class n988 leafNode
    n989[lithium]
    n964 --> n989
    class n989 normalNode
    n990[value]
    n989 --> n990
    class n990 leafNode
    n991[source]
    n989 --> n991
    class n991 leafNode
    n992[carbon]
    n964 --> n992
    class n992 normalNode
    n993[value]
    n992 --> n993
    class n993 leafNode
    n994[source]
    n992 --> n994
    class n994 leafNode
    n995[nitrogen]
    n964 --> n995
    class n995 normalNode
    n996[value]
    n995 --> n996
    class n996 leafNode
    n997[source]
    n995 --> n997
    class n997 leafNode
    n998[neon]
    n964 --> n998
    class n998 normalNode
    n999[value]
    n998 --> n999
    class n999 leafNode
    n1000[source]
    n998 --> n1000
    class n1000 leafNode
    n1001[argon]
    n964 --> n1001
    class n1001 normalNode
    n1002[value]
    n1001 --> n1002
    class n1002 leafNode
    n1003[source]
    n1001 --> n1003
    class n1003 leafNode
    n1004[xenon]
    n964 --> n1004
    class n1004 normalNode
    n1005[value]
    n1004 --> n1005
    class n1005 leafNode
    n1006[source]
    n1004 --> n1006
    class n1006 leafNode
    n1007[oxygen]
    n964 --> n1007
    class n1007 normalNode
    n1008[value]
    n1007 --> n1008
    class n1008 leafNode
    n1009[source]
    n1007 --> n1009
    class n1009 leafNode
    n1010[tungsten]
    n964 --> n1010
    class n1010 normalNode
    n1011[value]
    n1010 --> n1011
    class n1011 leafNode
    n1012[source]
    n1010 --> n1012
    class n1012 leafNode
    n1013[iron]
    n964 --> n1013
    class n1013 normalNode
    n1014[value]
    n1013 --> n1014
    class n1014 leafNode
    n1015[source]
    n1013 --> n1015
    class n1015 leafNode
    n1016[krypton]
    n964 --> n1016
    class n1016 normalNode
    n1017[value]
    n1016 --> n1017
    class n1017 leafNode
    n1018[source]
    n1016 --> n1018
    class n1018 leafNode
    n1019[n_i_total]
    n951 --> n1019
    class n1019 normalNode
    n1020[value]
    n1019 --> n1020
    class n1020 leafNode
    n1021[source]
    n1019 --> n1021
    class n1021 leafNode
    n1022[zeff]
    n951 --> n1022
    class n1022 normalNode
    n1023[value]
    n1022 --> n1023
    class n1023 leafNode
    n1024[source]
    n1022 --> n1024
    class n1024 leafNode
    n1025[flux_expansion]
    n951 --> n1025
    class n1025 normalNode
    n1026[value]
    n1025 --> n1026
    class n1026 leafNode
    n1027[source]
    n1025 --> n1027
    class n1027 leafNode
    n1028[power_flux_peak]
    n951 --> n1028
    class n1028 normalNode
    n1029[value]
    n1028 --> n1029
    class n1029 leafNode
    n1030[source]
    n1028 --> n1030
    class n1030 leafNode
    n1031(divertor_target)
    n247 --> n1031
    class n1031 complexNode
    n1032[name]
    n1031 --> n1032
    class n1032 normalNode
    n1033[value]
    n1032 --> n1033
    class n1033 leafNode
    n1034[source]
    n1032 --> n1034
    class n1034 leafNode
    n1035[t_e]
    n1031 --> n1035
    class n1035 normalNode
    n1036[value]
    n1035 --> n1036
    class n1036 leafNode
    n1037[source]
    n1035 --> n1037
    class n1037 leafNode
    n1038[t_i_average]
    n1031 --> n1038
    class n1038 normalNode
    n1039[value]
    n1038 --> n1039
    class n1039 leafNode
    n1040[source]
    n1038 --> n1040
    class n1040 leafNode
    n1041[n_e]
    n1031 --> n1041
    class n1041 normalNode
    n1042[value]
    n1041 --> n1042
    class n1042 leafNode
    n1043[source]
    n1041 --> n1043
    class n1043 leafNode
    n1044(n_i)
    n1031 --> n1044
    class n1044 complexNode
    n1045[hydrogen]
    n1044 --> n1045
    class n1045 normalNode
    n1046[value]
    n1045 --> n1046
    class n1046 leafNode
    n1047[source]
    n1045 --> n1047
    class n1047 leafNode
    n1048[deuterium]
    n1044 --> n1048
    class n1048 normalNode
    n1049[value]
    n1048 --> n1049
    class n1049 leafNode
    n1050[source]
    n1048 --> n1050
    class n1050 leafNode
    n1051[tritium]
    n1044 --> n1051
    class n1051 normalNode
    n1052[value]
    n1051 --> n1052
    class n1052 leafNode
    n1053[source]
    n1051 --> n1053
    class n1053 leafNode
    n1054[deuterium_tritium]
    n1044 --> n1054
    class n1054 normalNode
    n1055[value]
    n1054 --> n1055
    class n1055 leafNode
    n1056[source]
    n1054 --> n1056
    class n1056 leafNode
    n1057[helium_3]
    n1044 --> n1057
    class n1057 normalNode
    n1058[value]
    n1057 --> n1058
    class n1058 leafNode
    n1059[source]
    n1057 --> n1059
    class n1059 leafNode
    n1060[helium_4]
    n1044 --> n1060
    class n1060 normalNode
    n1061[value]
    n1060 --> n1061
    class n1061 leafNode
    n1062[source]
    n1060 --> n1062
    class n1062 leafNode
    n1063[beryllium]
    n1044 --> n1063
    class n1063 normalNode
    n1064[value]
    n1063 --> n1064
    class n1064 leafNode
    n1065[source]
    n1063 --> n1065
    class n1065 leafNode
    n1066[boron]
    n1044 --> n1066
    class n1066 normalNode
    n1067[value]
    n1066 --> n1067
    class n1067 leafNode
    n1068[source]
    n1066 --> n1068
    class n1068 leafNode
    n1069[lithium]
    n1044 --> n1069
    class n1069 normalNode
    n1070[value]
    n1069 --> n1070
    class n1070 leafNode
    n1071[source]
    n1069 --> n1071
    class n1071 leafNode
    n1072[carbon]
    n1044 --> n1072
    class n1072 normalNode
    n1073[value]
    n1072 --> n1073
    class n1073 leafNode
    n1074[source]
    n1072 --> n1074
    class n1074 leafNode
    n1075[nitrogen]
    n1044 --> n1075
    class n1075 normalNode
    n1076[value]
    n1075 --> n1076
    class n1076 leafNode
    n1077[source]
    n1075 --> n1077
    class n1077 leafNode
    n1078[neon]
    n1044 --> n1078
    class n1078 normalNode
    n1079[value]
    n1078 --> n1079
    class n1079 leafNode
    n1080[source]
    n1078 --> n1080
    class n1080 leafNode
    n1081[argon]
    n1044 --> n1081
    class n1081 normalNode
    n1082[value]
    n1081 --> n1082
    class n1082 leafNode
    n1083[source]
    n1081 --> n1083
    class n1083 leafNode
    n1084[xenon]
    n1044 --> n1084
    class n1084 normalNode
    n1085[value]
    n1084 --> n1085
    class n1085 leafNode
    n1086[source]
    n1084 --> n1086
    class n1086 leafNode
    n1087[oxygen]
    n1044 --> n1087
    class n1087 normalNode
    n1088[value]
    n1087 --> n1088
    class n1088 leafNode
    n1089[source]
    n1087 --> n1089
    class n1089 leafNode
    n1090[tungsten]
    n1044 --> n1090
    class n1090 normalNode
    n1091[value]
    n1090 --> n1091
    class n1091 leafNode
    n1092[source]
    n1090 --> n1092
    class n1092 leafNode
    n1093[iron]
    n1044 --> n1093
    class n1093 normalNode
    n1094[value]
    n1093 --> n1094
    class n1094 leafNode
    n1095[source]
    n1093 --> n1095
    class n1095 leafNode
    n1096[krypton]
    n1044 --> n1096
    class n1096 normalNode
    n1097[value]
    n1096 --> n1097
    class n1097 leafNode
    n1098[source]
    n1096 --> n1098
    class n1098 leafNode
    n1099[n_i_total]
    n1031 --> n1099
    class n1099 normalNode
    n1100[value]
    n1099 --> n1100
    class n1100 leafNode
    n1101[source]
    n1099 --> n1101
    class n1101 leafNode
    n1102[zeff]
    n1031 --> n1102
    class n1102 normalNode
    n1103[value]
    n1102 --> n1103
    class n1103 leafNode
    n1104[source]
    n1102 --> n1104
    class n1104 leafNode
    n1105[flux_expansion]
    n1031 --> n1105
    class n1105 normalNode
    n1106[value]
    n1105 --> n1106
    class n1106 leafNode
    n1107[source]
    n1105 --> n1107
    class n1107 leafNode
    n1108[power_flux_peak]
    n1031 --> n1108
    class n1108 normalNode
    n1109[value]
    n1108 --> n1109
    class n1109 leafNode
    n1110[source]
    n1108 --> n1110
    class n1110 leafNode
    n1111[r_eff_norm_2_3]
    n247 --> n1111
    class n1111 normalNode
    n1112[effective_helical_ripple]
    n1111 --> n1112
    class n1112 normalNode
    n1113[value]
    n1112 --> n1113
    class n1113 leafNode
    n1114[source]
    n1112 --> n1114
    class n1114 leafNode
    n1115[plateau_factor]
    n1111 --> n1115
    class n1115 normalNode
    n1116[value]
    n1115 --> n1116
    class n1116 leafNode
    n1117[source]
    n1115 --> n1117
    class n1117 leafNode
    n1118[iota]
    n1111 --> n1118
    class n1118 normalNode
    n1119[value]
    n1118 --> n1119
    class n1119 leafNode
    n1120[source]
    n1118 --> n1120
    class n1120 leafNode
    n1121(boundary)
    n1 --> n1121
    class n1121 complexNode
    n1122[type]
    n1121 --> n1122
    class n1122 normalNode
    n1123[value]
    n1122 --> n1123
    class n1123 leafNode
    n1124[source]
    n1122 --> n1124
    class n1124 leafNode
    n1125[geometric_axis_r]
    n1121 --> n1125
    class n1125 normalNode
    n1126[value]
    n1125 --> n1126
    class n1126 leafNode
    n1127[source]
    n1125 --> n1127
    class n1127 leafNode
    n1128[geometric_axis_z]
    n1121 --> n1128
    class n1128 normalNode
    n1129[value]
    n1128 --> n1129
    class n1129 leafNode
    n1130[source]
    n1128 --> n1130
    class n1130 leafNode
    n1131[magnetic_axis_r]
    n1121 --> n1131
    class n1131 normalNode
    n1132[value]
    n1131 --> n1132
    class n1132 leafNode
    n1133[source]
    n1131 --> n1133
    class n1133 leafNode
    n1134[magnetic_axis_z]
    n1121 --> n1134
    class n1134 normalNode
    n1135[value]
    n1134 --> n1135
    class n1135 leafNode
    n1136[source]
    n1134 --> n1136
    class n1136 leafNode
    n1137[minor_radius]
    n1121 --> n1137
    class n1137 normalNode
    n1138[value]
    n1137 --> n1138
    class n1138 leafNode
    n1139[source]
    n1137 --> n1139
    class n1139 leafNode
    n1140[elongation]
    n1121 --> n1140
    class n1140 normalNode
    n1141[value]
    n1140 --> n1141
    class n1141 leafNode
    n1142[source]
    n1140 --> n1142
    class n1142 leafNode
    n1143[triangularity_upper]
    n1121 --> n1143
    class n1143 normalNode
    n1144[value]
    n1143 --> n1144
    class n1144 leafNode
    n1145[source]
    n1143 --> n1145
    class n1145 leafNode
    n1146[triangularity_lower]
    n1121 --> n1146
    class n1146 normalNode
    n1147[value]
    n1146 --> n1147
    class n1147 leafNode
    n1148[source]
    n1146 --> n1148
    class n1148 leafNode
    n1149[strike_point_inner_r]
    n1121 --> n1149
    class n1149 normalNode
    n1150[value]
    n1149 --> n1150
    class n1150 leafNode
    n1151[source]
    n1149 --> n1151
    class n1151 leafNode
    n1152[strike_point_inner_z]
    n1121 --> n1152
    class n1152 normalNode
    n1153[value]
    n1152 --> n1153
    class n1153 leafNode
    n1154[source]
    n1152 --> n1154
    class n1154 leafNode
    n1155[strike_point_outer_r]
    n1121 --> n1155
    class n1155 normalNode
    n1156[value]
    n1155 --> n1156
    class n1156 leafNode
    n1157[source]
    n1155 --> n1157
    class n1157 leafNode
    n1158[strike_point_outer_z]
    n1121 --> n1158
    class n1158 normalNode
    n1159[value]
    n1158 --> n1159
    class n1159 leafNode
    n1160[source]
    n1158 --> n1160
    class n1160 leafNode
    n1161[strike_point_configuration]
    n1121 --> n1161
    class n1161 normalNode
    n1162[value]
    n1161 --> n1162
    class n1162 leafNode
    n1163[source]
    n1161 --> n1163
    class n1163 leafNode
    n1164[gap_limiter_wall]
    n1121 --> n1164
    class n1164 normalNode
    n1165[value]
    n1164 --> n1165
    class n1165 leafNode
    n1166[source]
    n1164 --> n1166
    class n1166 leafNode
    n1167[distance_inner_outer_separatrices]
    n1121 --> n1167
    class n1167 normalNode
    n1168[value]
    n1167 --> n1168
    class n1168 leafNode
    n1169[source]
    n1167 --> n1169
    class n1169 leafNode
    n1170[x_point_main]
    n1121 --> n1170
    class n1170 normalNode
    n1171[r]
    n1170 --> n1171
    class n1171 leafNode
    n1172[z]
    n1170 --> n1172
    class n1172 leafNode
    n1173[source]
    n1170 --> n1173
    class n1173 leafNode
    n1174[pedestal_fits]
    n1 --> n1174
    class n1174 normalNode
    n1175(mtanh)
    n1174 --> n1175
    class n1175 complexNode
    n1176(n_e)
    n1175 --> n1176
    class n1176 complexNode
    n1177[separatrix]
    n1176 --> n1177
    class n1177 normalNode
    n1178[value]
    n1177 --> n1178
    class n1178 leafNode
    n1179[source]
    n1177 --> n1179
    class n1179 leafNode
    n1180[pedestal_height]
    n1176 --> n1180
    class n1180 normalNode
    n1181[value]
    n1180 --> n1181
    class n1181 leafNode
    n1182[source]
    n1180 --> n1182
    class n1182 leafNode
    n1183[pedestal_width]
    n1176 --> n1183
    class n1183 normalNode
    n1184[value]
    n1183 --> n1184
    class n1184 leafNode
    n1185[source]
    n1183 --> n1185
    class n1185 leafNode
    n1186[pedestal_position]
    n1176 --> n1186
    class n1186 normalNode
    n1187[value]
    n1186 --> n1187
    class n1187 leafNode
    n1188[source]
    n1186 --> n1188
    class n1188 leafNode
    n1189[offset]
    n1176 --> n1189
    class n1189 normalNode
    n1190[value]
    n1189 --> n1190
    class n1190 leafNode
    n1191[source]
    n1189 --> n1191
    class n1191 leafNode
    n1192[d_dpsi_norm]
    n1176 --> n1192
    class n1192 normalNode
    n1193[value]
    n1192 --> n1193
    class n1193 leafNode
    n1194[source]
    n1192 --> n1194
    class n1194 leafNode
    n1195[d_dpsi_norm_max]
    n1176 --> n1195
    class n1195 normalNode
    n1196[value]
    n1195 --> n1196
    class n1196 leafNode
    n1197[source]
    n1195 --> n1197
    class n1197 leafNode
    n1198[d_dpsi_norm_max_position]
    n1176 --> n1198
    class n1198 normalNode
    n1199[value]
    n1198 --> n1199
    class n1199 leafNode
    n1200[source]
    n1198 --> n1200
    class n1200 leafNode
    n1201(t_e)
    n1175 --> n1201
    class n1201 complexNode
    n1202[pedestal_height]
    n1201 --> n1202
    class n1202 normalNode
    n1203[value]
    n1202 --> n1203
    class n1203 leafNode
    n1204[source]
    n1202 --> n1204
    class n1204 leafNode
    n1205[pedestal_width]
    n1201 --> n1205
    class n1205 normalNode
    n1206[value]
    n1205 --> n1206
    class n1206 leafNode
    n1207[source]
    n1205 --> n1207
    class n1207 leafNode
    n1208[pedestal_position]
    n1201 --> n1208
    class n1208 normalNode
    n1209[value]
    n1208 --> n1209
    class n1209 leafNode
    n1210[source]
    n1208 --> n1210
    class n1210 leafNode
    n1211[offset]
    n1201 --> n1211
    class n1211 normalNode
    n1212[value]
    n1211 --> n1212
    class n1212 leafNode
    n1213[source]
    n1211 --> n1213
    class n1213 leafNode
    n1214[d_dpsi_norm]
    n1201 --> n1214
    class n1214 normalNode
    n1215[value]
    n1214 --> n1215
    class n1215 leafNode
    n1216[source]
    n1214 --> n1216
    class n1216 leafNode
    n1217[d_dpsi_norm_max]
    n1201 --> n1217
    class n1217 normalNode
    n1218[value]
    n1217 --> n1218
    class n1218 leafNode
    n1219[source]
    n1217 --> n1219
    class n1219 leafNode
    n1220[d_dpsi_norm_max_position]
    n1201 --> n1220
    class n1220 normalNode
    n1221[value]
    n1220 --> n1221
    class n1221 leafNode
    n1222[source]
    n1220 --> n1222
    class n1222 leafNode
    n1223(pressure_electron)
    n1175 --> n1223
    class n1223 complexNode
    n1224[separatrix]
    n1223 --> n1224
    class n1224 normalNode
    n1225[value]
    n1224 --> n1225
    class n1225 leafNode
    n1226[source]
    n1224 --> n1226
    class n1226 leafNode
    n1227[pedestal_height]
    n1223 --> n1227
    class n1227 normalNode
    n1228[value]
    n1227 --> n1228
    class n1228 leafNode
    n1229[source]
    n1227 --> n1229
    class n1229 leafNode
    n1230[pedestal_width]
    n1223 --> n1230
    class n1230 normalNode
    n1231[value]
    n1230 --> n1231
    class n1231 leafNode
    n1232[source]
    n1230 --> n1232
    class n1232 leafNode
    n1233[pedestal_position]
    n1223 --> n1233
    class n1233 normalNode
    n1234[value]
    n1233 --> n1234
    class n1234 leafNode
    n1235[source]
    n1233 --> n1235
    class n1235 leafNode
    n1236[offset]
    n1223 --> n1236
    class n1236 normalNode
    n1237[value]
    n1236 --> n1237
    class n1237 leafNode
    n1238[source]
    n1236 --> n1238
    class n1238 leafNode
    n1239[d_dpsi_norm]
    n1223 --> n1239
    class n1239 normalNode
    n1240[value]
    n1239 --> n1240
    class n1240 leafNode
    n1241[source]
    n1239 --> n1241
    class n1241 leafNode
    n1242[d_dpsi_norm_max]
    n1223 --> n1242
    class n1242 normalNode
    n1243[value]
    n1242 --> n1243
    class n1243 leafNode
    n1244[source]
    n1242 --> n1244
    class n1244 leafNode
    n1245[d_dpsi_norm_max_position]
    n1223 --> n1245
    class n1245 normalNode
    n1246[value]
    n1245 --> n1246
    class n1246 leafNode
    n1247[source]
    n1245 --> n1247
    class n1247 leafNode
    n1248[energy_thermal_pedestal_electron]
    n1175 --> n1248
    class n1248 normalNode
    n1249[value]
    n1248 --> n1249
    class n1249 leafNode
    n1250[source]
    n1248 --> n1250
    class n1250 leafNode
    n1251[energy_thermal_pedestal_ion]
    n1175 --> n1251
    class n1251 normalNode
    n1252[value]
    n1251 --> n1252
    class n1252 leafNode
    n1253[source]
    n1251 --> n1253
    class n1253 leafNode
    n1254[volume_inside_pedestal]
    n1175 --> n1254
    class n1254 normalNode
    n1255[value]
    n1254 --> n1255
    class n1255 leafNode
    n1256[source]
    n1254 --> n1256
    class n1256 leafNode
    n1257[alpha_electron_pedestal_max]
    n1175 --> n1257
    class n1257 normalNode
    n1258[value]
    n1257 --> n1258
    class n1258 leafNode
    n1259[source]
    n1257 --> n1259
    class n1259 leafNode
    n1260[alpha_electron_pedestal_max_position]
    n1175 --> n1260
    class n1260 normalNode
    n1261[value]
    n1260 --> n1261
    class n1261 leafNode
    n1262[source]
    n1260 --> n1262
    class n1262 leafNode
    n1263[beta_pol_pedestal_top_electron_average]
    n1175 --> n1263
    class n1263 normalNode
    n1264[value]
    n1263 --> n1264
    class n1264 leafNode
    n1265[source]
    n1263 --> n1265
    class n1265 leafNode
    n1266[beta_pol_pedestal_top_electron_lfs]
    n1175 --> n1266
    class n1266 normalNode
    n1267[value]
    n1266 --> n1267
    class n1267 leafNode
    n1268[source]
    n1266 --> n1268
    class n1268 leafNode
    n1269[beta_pol_pedestal_top_electron_hfs]
    n1175 --> n1269
    class n1269 normalNode
    n1270[value]
    n1269 --> n1270
    class n1270 leafNode
    n1271[source]
    n1269 --> n1271
    class n1271 leafNode
    n1272[nustar_pedestal_top_electron]
    n1175 --> n1272
    class n1272 normalNode
    n1273[value]
    n1272 --> n1273
    class n1273 leafNode
    n1274[source]
    n1272 --> n1274
    class n1274 leafNode
    n1275[rhostar_pedestal_top_electron_lfs]
    n1175 --> n1275
    class n1275 normalNode
    n1276[value]
    n1275 --> n1276
    class n1276 leafNode
    n1277[source]
    n1275 --> n1277
    class n1277 leafNode
    n1278[rhostar_pedestal_top_electron_hfs]
    n1175 --> n1278
    class n1278 normalNode
    n1279[value]
    n1278 --> n1279
    class n1279 leafNode
    n1280[source]
    n1278 --> n1280
    class n1280 leafNode
    n1281[rhostar_pedestal_top_electron_magnetic_axis]
    n1175 --> n1281
    class n1281 normalNode
    n1282[value]
    n1281 --> n1282
    class n1282 leafNode
    n1283[source]
    n1281 --> n1283
    class n1283 leafNode
    n1284[b_field_pol_pedestal_top_average]
    n1175 --> n1284
    class n1284 normalNode
    n1285[value]
    n1284 --> n1285
    class n1285 leafNode
    n1286[source]
    n1284 --> n1286
    class n1286 leafNode
    n1287[b_field_pol_pedestal_top_hfs]
    n1175 --> n1287
    class n1287 normalNode
    n1288[value]
    n1287 --> n1288
    class n1288 leafNode
    n1289[source]
    n1287 --> n1289
    class n1289 leafNode
    n1290[b_field_pol_pedestal_top_lfs]
    n1175 --> n1290
    class n1290 normalNode
    n1291[value]
    n1290 --> n1291
    class n1291 leafNode
    n1292[source]
    n1290 --> n1292
    class n1292 leafNode
    n1293[b_field_pedestal_top_hfs]
    n1175 --> n1293
    class n1293 normalNode
    n1294[value]
    n1293 --> n1294
    class n1294 leafNode
    n1295[source]
    n1293 --> n1295
    class n1295 leafNode
    n1296[b_field_pedestal_top_lfs]
    n1175 --> n1296
    class n1296 normalNode
    n1297[value]
    n1296 --> n1297
    class n1297 leafNode
    n1298[source]
    n1296 --> n1298
    class n1298 leafNode
    n1299[b_field_tor_pedestal_top_hfs]
    n1175 --> n1299
    class n1299 normalNode
    n1300[value]
    n1299 --> n1300
    class n1300 leafNode
    n1301[source]
    n1299 --> n1301
    class n1301 leafNode
    n1302[b_field_tor_pedestal_top_lfs]
    n1175 --> n1302
    class n1302 normalNode
    n1303[value]
    n1302 --> n1303
    class n1303 leafNode
    n1304[source]
    n1302 --> n1304
    class n1304 leafNode
    n1305[coulomb_factor_pedestal_top]
    n1175 --> n1305
    class n1305 normalNode
    n1306[value]
    n1305 --> n1306
    class n1306 leafNode
    n1307[source]
    n1305 --> n1307
    class n1307 leafNode
    n1308[stability]
    n1175 --> n1308
    class n1308 normalNode
    n1309[alpha_experimental]
    n1308 --> n1309
    class n1309 normalNode
    n1310[value]
    n1309 --> n1310
    class n1310 leafNode
    n1311[source]
    n1309 --> n1311
    class n1311 leafNode
    n1312[bootstrap_current_sauter]
    n1308 --> n1312
    class n1312 normalNode
    n1313[alpha_critical]
    n1312 --> n1313
    class n1313 normalNode
    n1314[value]
    n1313 --> n1314
    class n1314 leafNode
    n1315[source]
    n1313 --> n1315
    class n1315 leafNode
    n1316[alpha_ratio]
    n1312 --> n1316
    class n1316 normalNode
    n1317[value]
    n1316 --> n1317
    class n1317 leafNode
    n1318[source]
    n1316 --> n1318
    class n1318 leafNode
    n1319[t_e_pedestal_top_critical]
    n1312 --> n1319
    class n1319 normalNode
    n1320[value]
    n1319 --> n1320
    class n1320 leafNode
    n1321[source]
    n1319 --> n1321
    class n1321 leafNode
    n1322[bootstrap_current_hager]
    n1308 --> n1322
    class n1322 normalNode
    n1323[alpha_critical]
    n1322 --> n1323
    class n1323 normalNode
    n1324[value]
    n1323 --> n1324
    class n1324 leafNode
    n1325[source]
    n1323 --> n1325
    class n1325 leafNode
    n1326[alpha_ratio]
    n1322 --> n1326
    class n1326 normalNode
    n1327[value]
    n1326 --> n1327
    class n1327 leafNode
    n1328[source]
    n1326 --> n1328
    class n1328 leafNode
    n1329[t_e_pedestal_top_critical]
    n1322 --> n1329
    class n1329 normalNode
    n1330[value]
    n1329 --> n1330
    class n1330 leafNode
    n1331[source]
    n1329 --> n1331
    class n1331 leafNode
    n1332[parameters]
    n1175 --> n1332
    class n1332 leafNode
    n1333(linear)
    n1174 --> n1333
    class n1333 complexNode
    n1334(n_e)
    n1333 --> n1334
    class n1334 complexNode
    n1335[separatrix]
    n1334 --> n1335
    class n1335 normalNode
    n1336[value]
    n1335 --> n1336
    class n1336 leafNode
    n1337[source]
    n1335 --> n1337
    class n1337 leafNode
    n1338[pedestal_height]
    n1334 --> n1338
    class n1338 normalNode
    n1339[value]
    n1338 --> n1339
    class n1339 leafNode
    n1340[source]
    n1338 --> n1340
    class n1340 leafNode
    n1341[pedestal_width]
    n1334 --> n1341
    class n1341 normalNode
    n1342[value]
    n1341 --> n1342
    class n1342 leafNode
    n1343[source]
    n1341 --> n1343
    class n1343 leafNode
    n1344[pedestal_position]
    n1334 --> n1344
    class n1344 normalNode
    n1345[value]
    n1344 --> n1345
    class n1345 leafNode
    n1346[source]
    n1344 --> n1346
    class n1346 leafNode
    n1347[offset]
    n1334 --> n1347
    class n1347 normalNode
    n1348[value]
    n1347 --> n1348
    class n1348 leafNode
    n1349[source]
    n1347 --> n1349
    class n1349 leafNode
    n1350[d_dpsi_norm]
    n1334 --> n1350
    class n1350 normalNode
    n1351[value]
    n1350 --> n1351
    class n1351 leafNode
    n1352[source]
    n1350 --> n1352
    class n1352 leafNode
    n1353[d_dpsi_norm_max]
    n1334 --> n1353
    class n1353 normalNode
    n1354[value]
    n1353 --> n1354
    class n1354 leafNode
    n1355[source]
    n1353 --> n1355
    class n1355 leafNode
    n1356(t_e)
    n1333 --> n1356
    class n1356 complexNode
    n1357[pedestal_height]
    n1356 --> n1357
    class n1357 normalNode
    n1358[value]
    n1357 --> n1358
    class n1358 leafNode
    n1359[source]
    n1357 --> n1359
    class n1359 leafNode
    n1360[pedestal_width]
    n1356 --> n1360
    class n1360 normalNode
    n1361[value]
    n1360 --> n1361
    class n1361 leafNode
    n1362[source]
    n1360 --> n1362
    class n1362 leafNode
    n1363[pedestal_position]
    n1356 --> n1363
    class n1363 normalNode
    n1364[value]
    n1363 --> n1364
    class n1364 leafNode
    n1365[source]
    n1363 --> n1365
    class n1365 leafNode
    n1366[offset]
    n1356 --> n1366
    class n1366 normalNode
    n1367[value]
    n1366 --> n1367
    class n1367 leafNode
    n1368[source]
    n1366 --> n1368
    class n1368 leafNode
    n1369[d_dpsi_norm]
    n1356 --> n1369
    class n1369 normalNode
    n1370[value]
    n1369 --> n1370
    class n1370 leafNode
    n1371[source]
    n1369 --> n1371
    class n1371 leafNode
    n1372[d_dpsi_norm_max]
    n1356 --> n1372
    class n1372 normalNode
    n1373[value]
    n1372 --> n1373
    class n1373 leafNode
    n1374[source]
    n1372 --> n1374
    class n1374 leafNode
    n1375(pressure_electron)
    n1333 --> n1375
    class n1375 complexNode
    n1376[separatrix]
    n1375 --> n1376
    class n1376 normalNode
    n1377[value]
    n1376 --> n1377
    class n1377 leafNode
    n1378[source]
    n1376 --> n1378
    class n1378 leafNode
    n1379[pedestal_height]
    n1375 --> n1379
    class n1379 normalNode
    n1380[value]
    n1379 --> n1380
    class n1380 leafNode
    n1381[source]
    n1379 --> n1381
    class n1381 leafNode
    n1382[pedestal_width]
    n1375 --> n1382
    class n1382 normalNode
    n1383[value]
    n1382 --> n1383
    class n1383 leafNode
    n1384[source]
    n1382 --> n1384
    class n1384 leafNode
    n1385[pedestal_position]
    n1375 --> n1385
    class n1385 normalNode
    n1386[value]
    n1385 --> n1386
    class n1386 leafNode
    n1387[source]
    n1385 --> n1387
    class n1387 leafNode
    n1388[offset]
    n1375 --> n1388
    class n1388 normalNode
    n1389[value]
    n1388 --> n1389
    class n1389 leafNode
    n1390[source]
    n1388 --> n1390
    class n1390 leafNode
    n1391[d_dpsi_norm]
    n1375 --> n1391
    class n1391 normalNode
    n1392[value]
    n1391 --> n1392
    class n1392 leafNode
    n1393[source]
    n1391 --> n1393
    class n1393 leafNode
    n1394[d_dpsi_norm_max]
    n1375 --> n1394
    class n1394 normalNode
    n1395[value]
    n1394 --> n1395
    class n1395 leafNode
    n1396[source]
    n1394 --> n1396
    class n1396 leafNode
    n1397[d_dpsi_norm_max_position]
    n1375 --> n1397
    class n1397 normalNode
    n1398[value]
    n1397 --> n1398
    class n1398 leafNode
    n1399[source]
    n1397 --> n1399
    class n1399 leafNode
    n1400[energy_thermal_pedestal_electron]
    n1333 --> n1400
    class n1400 normalNode
    n1401[value]
    n1400 --> n1401
    class n1401 leafNode
    n1402[source]
    n1400 --> n1402
    class n1402 leafNode
    n1403[energy_thermal_pedestal_ion]
    n1333 --> n1403
    class n1403 normalNode
    n1404[value]
    n1403 --> n1404
    class n1404 leafNode
    n1405[source]
    n1403 --> n1405
    class n1405 leafNode
    n1406[volume_inside_pedestal]
    n1333 --> n1406
    class n1406 normalNode
    n1407[value]
    n1406 --> n1407
    class n1407 leafNode
    n1408[source]
    n1406 --> n1408
    class n1408 leafNode
    n1409[beta_pol_pedestal_top_electron_average]
    n1333 --> n1409
    class n1409 normalNode
    n1410[value]
    n1409 --> n1410
    class n1410 leafNode
    n1411[source]
    n1409 --> n1411
    class n1411 leafNode
    n1412[beta_pol_pedestal_top_electron_lfs]
    n1333 --> n1412
    class n1412 normalNode
    n1413[value]
    n1412 --> n1413
    class n1413 leafNode
    n1414[source]
    n1412 --> n1414
    class n1414 leafNode
    n1415[beta_pol_pedestal_top_electron_hfs]
    n1333 --> n1415
    class n1415 normalNode
    n1416[value]
    n1415 --> n1416
    class n1416 leafNode
    n1417[source]
    n1415 --> n1417
    class n1417 leafNode
    n1418[nustar_pedestal_top_electron]
    n1333 --> n1418
    class n1418 normalNode
    n1419[value]
    n1418 --> n1419
    class n1419 leafNode
    n1420[source]
    n1418 --> n1420
    class n1420 leafNode
    n1421[rhostar_pedestal_top_electron_lfs]
    n1333 --> n1421
    class n1421 normalNode
    n1422[value]
    n1421 --> n1422
    class n1422 leafNode
    n1423[source]
    n1421 --> n1423
    class n1423 leafNode
    n1424[rhostar_pedestal_top_electron_hfs]
    n1333 --> n1424
    class n1424 normalNode
    n1425[value]
    n1424 --> n1425
    class n1425 leafNode
    n1426[source]
    n1424 --> n1426
    class n1426 leafNode
    n1427[rhostar_pedestal_top_electron_magnetic_axis]
    n1333 --> n1427
    class n1427 normalNode
    n1428[value]
    n1427 --> n1428
    class n1428 leafNode
    n1429[source]
    n1427 --> n1429
    class n1429 leafNode
    n1430[b_field_pol_pedestal_top_average]
    n1333 --> n1430
    class n1430 normalNode
    n1431[value]
    n1430 --> n1431
    class n1431 leafNode
    n1432[source]
    n1430 --> n1432
    class n1432 leafNode
    n1433[b_field_pol_pedestal_top_hfs]
    n1333 --> n1433
    class n1433 normalNode
    n1434[value]
    n1433 --> n1434
    class n1434 leafNode
    n1435[source]
    n1433 --> n1435
    class n1435 leafNode
    n1436[b_field_pol_pedestal_top_lfs]
    n1333 --> n1436
    class n1436 normalNode
    n1437[value]
    n1436 --> n1437
    class n1437 leafNode
    n1438[source]
    n1436 --> n1438
    class n1438 leafNode
    n1439[b_field_pedestal_top_hfs]
    n1333 --> n1439
    class n1439 normalNode
    n1440[value]
    n1439 --> n1440
    class n1440 leafNode
    n1441[source]
    n1439 --> n1441
    class n1441 leafNode
    n1442[b_field_pedestal_top_lfs]
    n1333 --> n1442
    class n1442 normalNode
    n1443[value]
    n1442 --> n1443
    class n1443 leafNode
    n1444[source]
    n1442 --> n1444
    class n1444 leafNode
    n1445[b_field_tor_pedestal_top_hfs]
    n1333 --> n1445
    class n1445 normalNode
    n1446[value]
    n1445 --> n1446
    class n1446 leafNode
    n1447[source]
    n1445 --> n1447
    class n1447 leafNode
    n1448[b_field_tor_pedestal_top_lfs]
    n1333 --> n1448
    class n1448 normalNode
    n1449[value]
    n1448 --> n1449
    class n1449 leafNode
    n1450[source]
    n1448 --> n1450
    class n1450 leafNode
    n1451[coulomb_factor_pedestal_top]
    n1333 --> n1451
    class n1451 normalNode
    n1452[value]
    n1451 --> n1452
    class n1452 leafNode
    n1453[source]
    n1451 --> n1453
    class n1453 leafNode
    n1454[parameters]
    n1333 --> n1454
    class n1454 leafNode
    n1455(line_average)
    n1 --> n1455
    class n1455 complexNode
    n1456[t_e]
    n1455 --> n1456
    class n1456 normalNode
    n1457[value]
    n1456 --> n1457
    class n1457 leafNode
    n1458[source]
    n1456 --> n1458
    class n1458 leafNode
    n1459[t_i_average]
    n1455 --> n1459
    class n1459 normalNode
    n1460[value]
    n1459 --> n1460
    class n1460 leafNode
    n1461[source]
    n1459 --> n1461
    class n1461 leafNode
    n1462[n_e]
    n1455 --> n1462
    class n1462 normalNode
    n1463[value]
    n1462 --> n1463
    class n1463 leafNode
    n1464[source]
    n1462 --> n1464
    class n1464 leafNode
    n1465[dn_e_dt]
    n1455 --> n1465
    class n1465 normalNode
    n1466[value]
    n1465 --> n1466
    class n1466 leafNode
    n1467[source]
    n1465 --> n1467
    class n1467 leafNode
    n1468(n_i)
    n1455 --> n1468
    class n1468 complexNode
    n1469[hydrogen]
    n1468 --> n1469
    class n1469 normalNode
    n1470[value]
    n1469 --> n1470
    class n1470 leafNode
    n1471[source]
    n1469 --> n1471
    class n1471 leafNode
    n1472[deuterium]
    n1468 --> n1472
    class n1472 normalNode
    n1473[value]
    n1472 --> n1473
    class n1473 leafNode
    n1474[source]
    n1472 --> n1474
    class n1474 leafNode
    n1475[tritium]
    n1468 --> n1475
    class n1475 normalNode
    n1476[value]
    n1475 --> n1476
    class n1476 leafNode
    n1477[source]
    n1475 --> n1477
    class n1477 leafNode
    n1478[deuterium_tritium]
    n1468 --> n1478
    class n1478 normalNode
    n1479[value]
    n1478 --> n1479
    class n1479 leafNode
    n1480[source]
    n1478 --> n1480
    class n1480 leafNode
    n1481[helium_3]
    n1468 --> n1481
    class n1481 normalNode
    n1482[value]
    n1481 --> n1482
    class n1482 leafNode
    n1483[source]
    n1481 --> n1483
    class n1483 leafNode
    n1484[helium_4]
    n1468 --> n1484
    class n1484 normalNode
    n1485[value]
    n1484 --> n1485
    class n1485 leafNode
    n1486[source]
    n1484 --> n1486
    class n1486 leafNode
    n1487[beryllium]
    n1468 --> n1487
    class n1487 normalNode
    n1488[value]
    n1487 --> n1488
    class n1488 leafNode
    n1489[source]
    n1487 --> n1489
    class n1489 leafNode
    n1490[boron]
    n1468 --> n1490
    class n1490 normalNode
    n1491[value]
    n1490 --> n1491
    class n1491 leafNode
    n1492[source]
    n1490 --> n1492
    class n1492 leafNode
    n1493[lithium]
    n1468 --> n1493
    class n1493 normalNode
    n1494[value]
    n1493 --> n1494
    class n1494 leafNode
    n1495[source]
    n1493 --> n1495
    class n1495 leafNode
    n1496[carbon]
    n1468 --> n1496
    class n1496 normalNode
    n1497[value]
    n1496 --> n1497
    class n1497 leafNode
    n1498[source]
    n1496 --> n1498
    class n1498 leafNode
    n1499[nitrogen]
    n1468 --> n1499
    class n1499 normalNode
    n1500[value]
    n1499 --> n1500
    class n1500 leafNode
    n1501[source]
    n1499 --> n1501
    class n1501 leafNode
    n1502[neon]
    n1468 --> n1502
    class n1502 normalNode
    n1503[value]
    n1502 --> n1503
    class n1503 leafNode
    n1504[source]
    n1502 --> n1504
    class n1504 leafNode
    n1505[argon]
    n1468 --> n1505
    class n1505 normalNode
    n1506[value]
    n1505 --> n1506
    class n1506 leafNode
    n1507[source]
    n1505 --> n1507
    class n1507 leafNode
    n1508[xenon]
    n1468 --> n1508
    class n1508 normalNode
    n1509[value]
    n1508 --> n1509
    class n1509 leafNode
    n1510[source]
    n1508 --> n1510
    class n1510 leafNode
    n1511[oxygen]
    n1468 --> n1511
    class n1511 normalNode
    n1512[value]
    n1511 --> n1512
    class n1512 leafNode
    n1513[source]
    n1511 --> n1513
    class n1513 leafNode
    n1514[tungsten]
    n1468 --> n1514
    class n1514 normalNode
    n1515[value]
    n1514 --> n1515
    class n1515 leafNode
    n1516[source]
    n1514 --> n1516
    class n1516 leafNode
    n1517[iron]
    n1468 --> n1517
    class n1517 normalNode
    n1518[value]
    n1517 --> n1518
    class n1518 leafNode
    n1519[source]
    n1517 --> n1519
    class n1519 leafNode
    n1520[krypton]
    n1468 --> n1520
    class n1520 normalNode
    n1521[value]
    n1520 --> n1521
    class n1521 leafNode
    n1522[source]
    n1520 --> n1522
    class n1522 leafNode
    n1523[n_i_total]
    n1455 --> n1523
    class n1523 normalNode
    n1524[value]
    n1523 --> n1524
    class n1524 leafNode
    n1525[source]
    n1523 --> n1525
    class n1525 leafNode
    n1526[zeff]
    n1455 --> n1526
    class n1526 normalNode
    n1527[value]
    n1526 --> n1527
    class n1527 leafNode
    n1528[source]
    n1526 --> n1528
    class n1528 leafNode
    n1529[meff_hydrogenic]
    n1455 --> n1529
    class n1529 normalNode
    n1530[value]
    n1529 --> n1530
    class n1530 leafNode
    n1531[source]
    n1529 --> n1531
    class n1531 leafNode
    n1532[isotope_fraction_hydrogen]
    n1455 --> n1532
    class n1532 normalNode
    n1533[value]
    n1532 --> n1533
    class n1533 leafNode
    n1534[source]
    n1532 --> n1534
    class n1534 leafNode
    n1535(volume_average)
    n1 --> n1535
    class n1535 complexNode
    n1536[t_e]
    n1535 --> n1536
    class n1536 normalNode
    n1537[value]
    n1536 --> n1537
    class n1537 leafNode
    n1538[source]
    n1536 --> n1538
    class n1538 leafNode
    n1539[t_i_average]
    n1535 --> n1539
    class n1539 normalNode
    n1540[value]
    n1539 --> n1540
    class n1540 leafNode
    n1541[source]
    n1539 --> n1541
    class n1541 leafNode
    n1542[n_e]
    n1535 --> n1542
    class n1542 normalNode
    n1543[value]
    n1542 --> n1543
    class n1543 leafNode
    n1544[source]
    n1542 --> n1544
    class n1544 leafNode
    n1545[dn_e_dt]
    n1535 --> n1545
    class n1545 normalNode
    n1546[value]
    n1545 --> n1546
    class n1546 leafNode
    n1547[source]
    n1545 --> n1547
    class n1547 leafNode
    n1548(n_i)
    n1535 --> n1548
    class n1548 complexNode
    n1549[hydrogen]
    n1548 --> n1549
    class n1549 normalNode
    n1550[value]
    n1549 --> n1550
    class n1550 leafNode
    n1551[source]
    n1549 --> n1551
    class n1551 leafNode
    n1552[deuterium]
    n1548 --> n1552
    class n1552 normalNode
    n1553[value]
    n1552 --> n1553
    class n1553 leafNode
    n1554[source]
    n1552 --> n1554
    class n1554 leafNode
    n1555[tritium]
    n1548 --> n1555
    class n1555 normalNode
    n1556[value]
    n1555 --> n1556
    class n1556 leafNode
    n1557[source]
    n1555 --> n1557
    class n1557 leafNode
    n1558[deuterium_tritium]
    n1548 --> n1558
    class n1558 normalNode
    n1559[value]
    n1558 --> n1559
    class n1559 leafNode
    n1560[source]
    n1558 --> n1560
    class n1560 leafNode
    n1561[helium_3]
    n1548 --> n1561
    class n1561 normalNode
    n1562[value]
    n1561 --> n1562
    class n1562 leafNode
    n1563[source]
    n1561 --> n1563
    class n1563 leafNode
    n1564[helium_4]
    n1548 --> n1564
    class n1564 normalNode
    n1565[value]
    n1564 --> n1565
    class n1565 leafNode
    n1566[source]
    n1564 --> n1566
    class n1566 leafNode
    n1567[beryllium]
    n1548 --> n1567
    class n1567 normalNode
    n1568[value]
    n1567 --> n1568
    class n1568 leafNode
    n1569[source]
    n1567 --> n1569
    class n1569 leafNode
    n1570[boron]
    n1548 --> n1570
    class n1570 normalNode
    n1571[value]
    n1570 --> n1571
    class n1571 leafNode
    n1572[source]
    n1570 --> n1572
    class n1572 leafNode
    n1573[lithium]
    n1548 --> n1573
    class n1573 normalNode
    n1574[value]
    n1573 --> n1574
    class n1574 leafNode
    n1575[source]
    n1573 --> n1575
    class n1575 leafNode
    n1576[carbon]
    n1548 --> n1576
    class n1576 normalNode
    n1577[value]
    n1576 --> n1577
    class n1577 leafNode
    n1578[source]
    n1576 --> n1578
    class n1578 leafNode
    n1579[nitrogen]
    n1548 --> n1579
    class n1579 normalNode
    n1580[value]
    n1579 --> n1580
    class n1580 leafNode
    n1581[source]
    n1579 --> n1581
    class n1581 leafNode
    n1582[neon]
    n1548 --> n1582
    class n1582 normalNode
    n1583[value]
    n1582 --> n1583
    class n1583 leafNode
    n1584[source]
    n1582 --> n1584
    class n1584 leafNode
    n1585[argon]
    n1548 --> n1585
    class n1585 normalNode
    n1586[value]
    n1585 --> n1586
    class n1586 leafNode
    n1587[source]
    n1585 --> n1587
    class n1587 leafNode
    n1588[xenon]
    n1548 --> n1588
    class n1588 normalNode
    n1589[value]
    n1588 --> n1589
    class n1589 leafNode
    n1590[source]
    n1588 --> n1590
    class n1590 leafNode
    n1591[oxygen]
    n1548 --> n1591
    class n1591 normalNode
    n1592[value]
    n1591 --> n1592
    class n1592 leafNode
    n1593[source]
    n1591 --> n1593
    class n1593 leafNode
    n1594[tungsten]
    n1548 --> n1594
    class n1594 normalNode
    n1595[value]
    n1594 --> n1595
    class n1595 leafNode
    n1596[source]
    n1594 --> n1596
    class n1596 leafNode
    n1597[iron]
    n1548 --> n1597
    class n1597 normalNode
    n1598[value]
    n1597 --> n1598
    class n1598 leafNode
    n1599[source]
    n1597 --> n1599
    class n1599 leafNode
    n1600[krypton]
    n1548 --> n1600
    class n1600 normalNode
    n1601[value]
    n1600 --> n1601
    class n1601 leafNode
    n1602[source]
    n1600 --> n1602
    class n1602 leafNode
    n1603[n_i_total]
    n1535 --> n1603
    class n1603 normalNode
    n1604[value]
    n1603 --> n1604
    class n1604 leafNode
    n1605[source]
    n1603 --> n1605
    class n1605 leafNode
    n1606[zeff]
    n1535 --> n1606
    class n1606 normalNode
    n1607[value]
    n1606 --> n1607
    class n1607 leafNode
    n1608[source]
    n1606 --> n1608
    class n1608 leafNode
    n1609[meff_hydrogenic]
    n1535 --> n1609
    class n1609 normalNode
    n1610[value]
    n1609 --> n1610
    class n1610 leafNode
    n1611[source]
    n1609 --> n1611
    class n1611 leafNode
    n1612[isotope_fraction_hydrogen]
    n1535 --> n1612
    class n1612 normalNode
    n1613[value]
    n1612 --> n1613
    class n1613 leafNode
    n1614[source]
    n1612 --> n1614
    class n1614 leafNode
    n1615(disruption)
    n1 --> n1615
    class n1615 complexNode
    n1616[time]
    n1615 --> n1616
    class n1616 normalNode
    n1617[value]
    n1616 --> n1617
    class n1617 leafNode
    n1618[source]
    n1616 --> n1618
    class n1618 leafNode
    n1619[time_radiated_power_max]
    n1615 --> n1619
    class n1619 normalNode
    n1620[value]
    n1619 --> n1620
    class n1620 leafNode
    n1621[source]
    n1619 --> n1621
    class n1621 leafNode
    n1622[time_half_ip]
    n1615 --> n1622
    class n1622 normalNode
    n1623[value]
    n1622 --> n1623
    class n1623 leafNode
    n1624[source]
    n1622 --> n1624
    class n1624 leafNode
    n1625[vertical_displacement]
    n1615 --> n1625
    class n1625 normalNode
    n1626[value]
    n1625 --> n1626
    class n1626 leafNode
    n1627[source]
    n1625 --> n1627
    class n1627 leafNode
    n1628[mitigation_valve]
    n1615 --> n1628
    class n1628 normalNode
    n1629[value]
    n1628 --> n1629
    class n1629 leafNode
    n1630[source]
    n1628 --> n1630
    class n1630 leafNode
    n1631[decay_times]
    n1615 --> n1631
    class n1631 normalNode
    n1632[ip]
    n1631 --> n1632
    class n1632 normalNode
    n1633[linear_20_80]
    n1632 --> n1633
    class n1633 normalNode
    n1634[value]
    n1633 --> n1634
    class n1634 leafNode
    n1635[source]
    n1633 --> n1635
    class n1635 leafNode
    n1636[linear_custom]
    n1632 --> n1636
    class n1636 normalNode
    n1637[x1]
    n1636 --> n1637
    class n1637 leafNode
    n1638[x2]
    n1636 --> n1638
    class n1638 leafNode
    n1639[decay_time]
    n1636 --> n1639
    class n1639 normalNode
    n1640[value]
    n1639 --> n1640
    class n1640 leafNode
    n1641[source]
    n1639 --> n1641
    class n1641 leafNode
    n1642[exponential]
    n1632 --> n1642
    class n1642 normalNode
    n1643[value]
    n1642 --> n1643
    class n1643 leafNode
    n1644[source]
    n1642 --> n1644
    class n1644 leafNode
    n1645[current_runaways]
    n1631 --> n1645
    class n1645 normalNode
    n1646[linear_20_80]
    n1645 --> n1646
    class n1646 normalNode
    n1647[value]
    n1646 --> n1647
    class n1647 leafNode
    n1648[source]
    n1646 --> n1648
    class n1648 leafNode
    n1649[linear_custom]
    n1645 --> n1649
    class n1649 normalNode
    n1650[x1]
    n1649 --> n1650
    class n1650 leafNode
    n1651[x2]
    n1649 --> n1651
    class n1651 leafNode
    n1652[decay_time]
    n1649 --> n1652
    class n1652 normalNode
    n1653[value]
    n1652 --> n1653
    class n1653 leafNode
    n1654[source]
    n1652 --> n1654
    class n1654 leafNode
    n1655[exponential]
    n1645 --> n1655
    class n1655 normalNode
    n1656[value]
    n1655 --> n1656
    class n1656 leafNode
    n1657[source]
    n1655 --> n1657
    class n1657 leafNode
    n1658[t_e_volume_average]
    n1631 --> n1658
    class n1658 normalNode
    n1659[linear_20_80]
    n1658 --> n1659
    class n1659 normalNode
    n1660[value]
    n1659 --> n1660
    class n1660 leafNode
    n1661[source]
    n1659 --> n1661
    class n1661 leafNode
    n1662[linear_custom]
    n1658 --> n1662
    class n1662 normalNode
    n1663[x1]
    n1662 --> n1663
    class n1663 leafNode
    n1664[x2]
    n1662 --> n1664
    class n1664 leafNode
    n1665[decay_time]
    n1662 --> n1665
    class n1665 normalNode
    n1666[value]
    n1665 --> n1666
    class n1666 leafNode
    n1667[source]
    n1665 --> n1667
    class n1667 leafNode
    n1668[exponential]
    n1658 --> n1668
    class n1668 normalNode
    n1669[value]
    n1668 --> n1669
    class n1669 leafNode
    n1670[source]
    n1668 --> n1670
    class n1670 leafNode
    n1671[t_e_magnetic_axis]
    n1631 --> n1671
    class n1671 normalNode
    n1672[linear_20_80]
    n1671 --> n1672
    class n1672 normalNode
    n1673[value]
    n1672 --> n1673
    class n1673 leafNode
    n1674[source]
    n1672 --> n1674
    class n1674 leafNode
    n1675[linear_custom]
    n1671 --> n1675
    class n1675 normalNode
    n1676[x1]
    n1675 --> n1676
    class n1676 leafNode
    n1677[x2]
    n1675 --> n1677
    class n1677 leafNode
    n1678[decay_time]
    n1675 --> n1678
    class n1678 normalNode
    n1679[value]
    n1678 --> n1679
    class n1679 leafNode
    n1680[source]
    n1678 --> n1680
    class n1680 leafNode
    n1681[exponential]
    n1671 --> n1681
    class n1681 normalNode
    n1682[value]
    n1681 --> n1682
    class n1682 leafNode
    n1683[source]
    n1681 --> n1683
    class n1683 leafNode
    n1684[energy_thermal]
    n1631 --> n1684
    class n1684 normalNode
    n1685[linear_20_80]
    n1684 --> n1685
    class n1685 normalNode
    n1686[value]
    n1685 --> n1686
    class n1686 leafNode
    n1687[source]
    n1685 --> n1687
    class n1687 leafNode
    n1688[linear_custom]
    n1684 --> n1688
    class n1688 normalNode
    n1689[x1]
    n1688 --> n1689
    class n1689 leafNode
    n1690[x2]
    n1688 --> n1690
    class n1690 leafNode
    n1691[decay_time]
    n1688 --> n1691
    class n1691 normalNode
    n1692[value]
    n1691 --> n1692
    class n1692 leafNode
    n1693[source]
    n1691 --> n1693
    class n1693 leafNode
    n1694[exponential]
    n1684 --> n1694
    class n1694 normalNode
    n1695[value]
    n1694 --> n1695
    class n1695 leafNode
    n1696[source]
    n1694 --> n1696
    class n1696 leafNode
    n1697[elms]
    n1 --> n1697
    class n1697 normalNode
    n1698[frequency]
    n1697 --> n1698
    class n1698 normalNode
    n1699[value]
    n1698 --> n1699
    class n1699 leafNode
    n1700[source]
    n1698 --> n1700
    class n1700 leafNode
    n1701[type]
    n1697 --> n1701
    class n1701 normalNode
    n1702[value]
    n1701 --> n1702
    class n1702 leafNode
    n1703[source]
    n1701 --> n1703
    class n1703 leafNode
    n1704[fusion]
    n1 --> n1704
    class n1704 normalNode
    n1705[power]
    n1704 --> n1705
    class n1705 normalNode
    n1706[value]
    n1705 --> n1706
    class n1706 leafNode
    n1707[source]
    n1705 --> n1707
    class n1707 leafNode
    n1708[current]
    n1704 --> n1708
    class n1708 normalNode
    n1709[value]
    n1708 --> n1709
    class n1709 leafNode
    n1710[source]
    n1708 --> n1710
    class n1710 leafNode
    n1711[neutron_rates]
    n1704 --> n1711
    class n1711 normalNode
    n1712[total]
    n1711 --> n1712
    class n1712 normalNode
    n1713[value]
    n1712 --> n1713
    class n1713 leafNode
    n1714[source]
    n1712 --> n1714
    class n1714 leafNode
    n1715[thermal]
    n1711 --> n1715
    class n1715 normalNode
    n1716[value]
    n1715 --> n1716
    class n1716 leafNode
    n1717[source]
    n1715 --> n1717
    class n1717 leafNode
    n1718[dd]
    n1711 --> n1718
    class n1718 normalNode
    n1719[total]
    n1718 --> n1719
    class n1719 normalNode
    n1720[value]
    n1719 --> n1720
    class n1720 leafNode
    n1721[source]
    n1719 --> n1721
    class n1721 leafNode
    n1722[thermal]
    n1718 --> n1722
    class n1722 normalNode
    n1723[value]
    n1722 --> n1723
    class n1723 leafNode
    n1724[source]
    n1722 --> n1724
    class n1724 leafNode
    n1725[beam_thermal]
    n1718 --> n1725
    class n1725 normalNode
    n1726[value]
    n1725 --> n1726
    class n1726 leafNode
    n1727[source]
    n1725 --> n1727
    class n1727 leafNode
    n1728[beam_beam]
    n1718 --> n1728
    class n1728 normalNode
    n1729[value]
    n1728 --> n1729
    class n1729 leafNode
    n1730[source]
    n1728 --> n1730
    class n1730 leafNode
    n1731[dt]
    n1711 --> n1731
    class n1731 normalNode
    n1732[total]
    n1731 --> n1732
    class n1732 normalNode
    n1733[value]
    n1732 --> n1733
    class n1733 leafNode
    n1734[source]
    n1732 --> n1734
    class n1734 leafNode
    n1735[thermal]
    n1731 --> n1735
    class n1735 normalNode
    n1736[value]
    n1735 --> n1736
    class n1736 leafNode
    n1737[source]
    n1735 --> n1737
    class n1737 leafNode
    n1738[beam_thermal]
    n1731 --> n1738
    class n1738 normalNode
    n1739[value]
    n1738 --> n1739
    class n1739 leafNode
    n1740[source]
    n1738 --> n1740
    class n1740 leafNode
    n1741[beam_beam]
    n1731 --> n1741
    class n1741 normalNode
    n1742[value]
    n1741 --> n1742
    class n1742 leafNode
    n1743[source]
    n1741 --> n1743
    class n1743 leafNode
    n1744[tt]
    n1711 --> n1744
    class n1744 normalNode
    n1745[total]
    n1744 --> n1745
    class n1745 normalNode
    n1746[value]
    n1745 --> n1746
    class n1746 leafNode
    n1747[source]
    n1745 --> n1747
    class n1747 leafNode
    n1748[thermal]
    n1744 --> n1748
    class n1748 normalNode
    n1749[value]
    n1748 --> n1749
    class n1749 leafNode
    n1750[source]
    n1748 --> n1750
    class n1750 leafNode
    n1751[beam_thermal]
    n1744 --> n1751
    class n1751 normalNode
    n1752[value]
    n1751 --> n1752
    class n1752 leafNode
    n1753[source]
    n1751 --> n1753
    class n1753 leafNode
    n1754[beam_beam]
    n1744 --> n1754
    class n1754 normalNode
    n1755[value]
    n1754 --> n1755
    class n1755 leafNode
    n1756[source]
    n1754 --> n1756
    class n1756 leafNode
    n1757[neutron_power_total]
    n1704 --> n1757
    class n1757 normalNode
    n1758[value]
    n1757 --> n1758
    class n1758 leafNode
    n1759[source]
    n1757 --> n1759
    class n1759 leafNode
    n1760(gas_injection_rates)
    n1 --> n1760
    class n1760 complexNode
    n1761[total]
    n1760 --> n1761
    class n1761 normalNode
    n1762[value]
    n1761 --> n1762
    class n1762 leafNode
    n1763[source]
    n1761 --> n1763
    class n1763 leafNode
    n1764[midplane]
    n1760 --> n1764
    class n1764 normalNode
    n1765[value]
    n1764 --> n1765
    class n1765 leafNode
    n1766[source]
    n1764 --> n1766
    class n1766 leafNode
    n1767[top]
    n1760 --> n1767
    class n1767 normalNode
    n1768[value]
    n1767 --> n1768
    class n1768 leafNode
    n1769[source]
    n1767 --> n1769
    class n1769 leafNode
    n1770[bottom]
    n1760 --> n1770
    class n1770 normalNode
    n1771[value]
    n1770 --> n1771
    class n1771 leafNode
    n1772[source]
    n1770 --> n1772
    class n1772 leafNode
    n1773[hydrogen]
    n1760 --> n1773
    class n1773 normalNode
    n1774[value]
    n1773 --> n1774
    class n1774 leafNode
    n1775[source]
    n1773 --> n1775
    class n1775 leafNode
    n1776[deuterium]
    n1760 --> n1776
    class n1776 normalNode
    n1777[value]
    n1776 --> n1777
    class n1777 leafNode
    n1778[source]
    n1776 --> n1778
    class n1778 leafNode
    n1779[tritium]
    n1760 --> n1779
    class n1779 normalNode
    n1780[value]
    n1779 --> n1780
    class n1780 leafNode
    n1781[source]
    n1779 --> n1781
    class n1781 leafNode
    n1782[helium_3]
    n1760 --> n1782
    class n1782 normalNode
    n1783[value]
    n1782 --> n1783
    class n1783 leafNode
    n1784[source]
    n1782 --> n1784
    class n1784 leafNode
    n1785[helium_4]
    n1760 --> n1785
    class n1785 normalNode
    n1786[value]
    n1785 --> n1786
    class n1786 leafNode
    n1787[source]
    n1785 --> n1787
    class n1787 leafNode
    n1788[impurity_seeding]
    n1760 --> n1788
    class n1788 normalNode
    n1789[value]
    n1788 --> n1789
    class n1789 leafNode
    n1790[source]
    n1788 --> n1790
    class n1790 leafNode
    n1791[beryllium]
    n1760 --> n1791
    class n1791 normalNode
    n1792[value]
    n1791 --> n1792
    class n1792 leafNode
    n1793[source]
    n1791 --> n1793
    class n1793 leafNode
    n1794[lithium]
    n1760 --> n1794
    class n1794 normalNode
    n1795[value]
    n1794 --> n1795
    class n1795 leafNode
    n1796[source]
    n1794 --> n1796
    class n1796 leafNode
    n1797[carbon]
    n1760 --> n1797
    class n1797 normalNode
    n1798[value]
    n1797 --> n1798
    class n1798 leafNode
    n1799[source]
    n1797 --> n1799
    class n1799 leafNode
    n1800[oxygen]
    n1760 --> n1800
    class n1800 normalNode
    n1801[value]
    n1800 --> n1801
    class n1801 leafNode
    n1802[source]
    n1800 --> n1802
    class n1802 leafNode
    n1803[nitrogen]
    n1760 --> n1803
    class n1803 normalNode
    n1804[value]
    n1803 --> n1804
    class n1804 leafNode
    n1805[source]
    n1803 --> n1805
    class n1805 leafNode
    n1806[neon]
    n1760 --> n1806
    class n1806 normalNode
    n1807[value]
    n1806 --> n1807
    class n1807 leafNode
    n1808[source]
    n1806 --> n1808
    class n1808 leafNode
    n1809[argon]
    n1760 --> n1809
    class n1809 normalNode
    n1810[value]
    n1809 --> n1810
    class n1810 leafNode
    n1811[source]
    n1809 --> n1811
    class n1811 leafNode
    n1812[xenon]
    n1760 --> n1812
    class n1812 normalNode
    n1813[value]
    n1812 --> n1813
    class n1813 leafNode
    n1814[source]
    n1812 --> n1814
    class n1814 leafNode
    n1815[krypton]
    n1760 --> n1815
    class n1815 normalNode
    n1816[value]
    n1815 --> n1816
    class n1816 leafNode
    n1817[source]
    n1815 --> n1817
    class n1817 leafNode
    n1818[methane]
    n1760 --> n1818
    class n1818 normalNode
    n1819[value]
    n1818 --> n1819
    class n1819 leafNode
    n1820[source]
    n1818 --> n1820
    class n1820 leafNode
    n1821[methane_carbon_13]
    n1760 --> n1821
    class n1821 normalNode
    n1822[value]
    n1821 --> n1822
    class n1822 leafNode
    n1823[source]
    n1821 --> n1823
    class n1823 leafNode
    n1824[methane_deuterated]
    n1760 --> n1824
    class n1824 normalNode
    n1825[value]
    n1824 --> n1825
    class n1825 leafNode
    n1826[source]
    n1824 --> n1826
    class n1826 leafNode
    n1827[silane]
    n1760 --> n1827
    class n1827 normalNode
    n1828[value]
    n1827 --> n1828
    class n1828 leafNode
    n1829[source]
    n1827 --> n1829
    class n1829 leafNode
    n1830[ethylene]
    n1760 --> n1830
    class n1830 normalNode
    n1831[value]
    n1830 --> n1831
    class n1831 leafNode
    n1832[source]
    n1830 --> n1832
    class n1832 leafNode
    n1833[ethane]
    n1760 --> n1833
    class n1833 normalNode
    n1834[value]
    n1833 --> n1834
    class n1834 leafNode
    n1835[source]
    n1833 --> n1835
    class n1835 leafNode
    n1836[propane]
    n1760 --> n1836
    class n1836 normalNode
    n1837[value]
    n1836 --> n1837
    class n1837 leafNode
    n1838[source]
    n1836 --> n1838
    class n1838 leafNode
    n1839[ammonia]
    n1760 --> n1839
    class n1839 normalNode
    n1840[value]
    n1839 --> n1840
    class n1840 leafNode
    n1841[source]
    n1839 --> n1841
    class n1841 leafNode
    n1842[ammonia_deuterated]
    n1760 --> n1842
    class n1842 normalNode
    n1843[value]
    n1842 --> n1843
    class n1843 leafNode
    n1844[source]
    n1842 --> n1844
    class n1844 leafNode
    n1845(gas_injection_accumulated)
    n1 --> n1845
    class n1845 complexNode
    n1846[total]
    n1845 --> n1846
    class n1846 normalNode
    n1847[value]
    n1846 --> n1847
    class n1847 leafNode
    n1848[source]
    n1846 --> n1848
    class n1848 leafNode
    n1849[midplane]
    n1845 --> n1849
    class n1849 normalNode
    n1850[value]
    n1849 --> n1850
    class n1850 leafNode
    n1851[source]
    n1849 --> n1851
    class n1851 leafNode
    n1852[top]
    n1845 --> n1852
    class n1852 normalNode
    n1853[value]
    n1852 --> n1853
    class n1853 leafNode
    n1854[source]
    n1852 --> n1854
    class n1854 leafNode
    n1855[bottom]
    n1845 --> n1855
    class n1855 normalNode
    n1856[value]
    n1855 --> n1856
    class n1856 leafNode
    n1857[source]
    n1855 --> n1857
    class n1857 leafNode
    n1858[hydrogen]
    n1845 --> n1858
    class n1858 normalNode
    n1859[value]
    n1858 --> n1859
    class n1859 leafNode
    n1860[source]
    n1858 --> n1860
    class n1860 leafNode
    n1861[deuterium]
    n1845 --> n1861
    class n1861 normalNode
    n1862[value]
    n1861 --> n1862
    class n1862 leafNode
    n1863[source]
    n1861 --> n1863
    class n1863 leafNode
    n1864[tritium]
    n1845 --> n1864
    class n1864 normalNode
    n1865[value]
    n1864 --> n1865
    class n1865 leafNode
    n1866[source]
    n1864 --> n1866
    class n1866 leafNode
    n1867[helium_3]
    n1845 --> n1867
    class n1867 normalNode
    n1868[value]
    n1867 --> n1868
    class n1868 leafNode
    n1869[source]
    n1867 --> n1869
    class n1869 leafNode
    n1870[helium_4]
    n1845 --> n1870
    class n1870 normalNode
    n1871[value]
    n1870 --> n1871
    class n1871 leafNode
    n1872[source]
    n1870 --> n1872
    class n1872 leafNode
    n1873[impurity_seeding]
    n1845 --> n1873
    class n1873 normalNode
    n1874[value]
    n1873 --> n1874
    class n1874 leafNode
    n1875[source]
    n1873 --> n1875
    class n1875 leafNode
    n1876[beryllium]
    n1845 --> n1876
    class n1876 normalNode
    n1877[value]
    n1876 --> n1877
    class n1877 leafNode
    n1878[source]
    n1876 --> n1878
    class n1878 leafNode
    n1879[lithium]
    n1845 --> n1879
    class n1879 normalNode
    n1880[value]
    n1879 --> n1880
    class n1880 leafNode
    n1881[source]
    n1879 --> n1881
    class n1881 leafNode
    n1882[carbon]
    n1845 --> n1882
    class n1882 normalNode
    n1883[value]
    n1882 --> n1883
    class n1883 leafNode
    n1884[source]
    n1882 --> n1884
    class n1884 leafNode
    n1885[oxygen]
    n1845 --> n1885
    class n1885 normalNode
    n1886[value]
    n1885 --> n1886
    class n1886 leafNode
    n1887[source]
    n1885 --> n1887
    class n1887 leafNode
    n1888[nitrogen]
    n1845 --> n1888
    class n1888 normalNode
    n1889[value]
    n1888 --> n1889
    class n1889 leafNode
    n1890[source]
    n1888 --> n1890
    class n1890 leafNode
    n1891[neon]
    n1845 --> n1891
    class n1891 normalNode
    n1892[value]
    n1891 --> n1892
    class n1892 leafNode
    n1893[source]
    n1891 --> n1893
    class n1893 leafNode
    n1894[argon]
    n1845 --> n1894
    class n1894 normalNode
    n1895[value]
    n1894 --> n1895
    class n1895 leafNode
    n1896[source]
    n1894 --> n1896
    class n1896 leafNode
    n1897[xenon]
    n1845 --> n1897
    class n1897 normalNode
    n1898[value]
    n1897 --> n1898
    class n1898 leafNode
    n1899[source]
    n1897 --> n1899
    class n1899 leafNode
    n1900[krypton]
    n1845 --> n1900
    class n1900 normalNode
    n1901[value]
    n1900 --> n1901
    class n1901 leafNode
    n1902[source]
    n1900 --> n1902
    class n1902 leafNode
    n1903[methane]
    n1845 --> n1903
    class n1903 normalNode
    n1904[value]
    n1903 --> n1904
    class n1904 leafNode
    n1905[source]
    n1903 --> n1905
    class n1905 leafNode
    n1906[methane_carbon_13]
    n1845 --> n1906
    class n1906 normalNode
    n1907[value]
    n1906 --> n1907
    class n1907 leafNode
    n1908[source]
    n1906 --> n1908
    class n1908 leafNode
    n1909[methane_deuterated]
    n1845 --> n1909
    class n1909 normalNode
    n1910[value]
    n1909 --> n1910
    class n1910 leafNode
    n1911[source]
    n1909 --> n1911
    class n1911 leafNode
    n1912[silane]
    n1845 --> n1912
    class n1912 normalNode
    n1913[value]
    n1912 --> n1913
    class n1913 leafNode
    n1914[source]
    n1912 --> n1914
    class n1914 leafNode
    n1915[ethylene]
    n1845 --> n1915
    class n1915 normalNode
    n1916[value]
    n1915 --> n1916
    class n1916 leafNode
    n1917[source]
    n1915 --> n1917
    class n1917 leafNode
    n1918[ethane]
    n1845 --> n1918
    class n1918 normalNode
    n1919[value]
    n1918 --> n1919
    class n1919 leafNode
    n1920[source]
    n1918 --> n1920
    class n1920 leafNode
    n1921[propane]
    n1845 --> n1921
    class n1921 normalNode
    n1922[value]
    n1921 --> n1922
    class n1922 leafNode
    n1923[source]
    n1921 --> n1923
    class n1923 leafNode
    n1924[ammonia]
    n1845 --> n1924
    class n1924 normalNode
    n1925[value]
    n1924 --> n1925
    class n1925 leafNode
    n1926[source]
    n1924 --> n1926
    class n1926 leafNode
    n1927[ammonia_deuterated]
    n1845 --> n1927
    class n1927 normalNode
    n1928[value]
    n1927 --> n1928
    class n1928 leafNode
    n1929[source]
    n1927 --> n1929
    class n1929 leafNode
    n1930(gas_injection_prefill)
    n1 --> n1930
    class n1930 complexNode
    n1931[total]
    n1930 --> n1931
    class n1931 normalNode
    n1932[value]
    n1931 --> n1932
    class n1932 leafNode
    n1933[source]
    n1931 --> n1933
    class n1933 leafNode
    n1934[midplane]
    n1930 --> n1934
    class n1934 normalNode
    n1935[value]
    n1934 --> n1935
    class n1935 leafNode
    n1936[source]
    n1934 --> n1936
    class n1936 leafNode
    n1937[top]
    n1930 --> n1937
    class n1937 normalNode
    n1938[value]
    n1937 --> n1938
    class n1938 leafNode
    n1939[source]
    n1937 --> n1939
    class n1939 leafNode
    n1940[bottom]
    n1930 --> n1940
    class n1940 normalNode
    n1941[value]
    n1940 --> n1941
    class n1941 leafNode
    n1942[source]
    n1940 --> n1942
    class n1942 leafNode
    n1943[hydrogen]
    n1930 --> n1943
    class n1943 normalNode
    n1944[value]
    n1943 --> n1944
    class n1944 leafNode
    n1945[source]
    n1943 --> n1945
    class n1945 leafNode
    n1946[deuterium]
    n1930 --> n1946
    class n1946 normalNode
    n1947[value]
    n1946 --> n1947
    class n1947 leafNode
    n1948[source]
    n1946 --> n1948
    class n1948 leafNode
    n1949[tritium]
    n1930 --> n1949
    class n1949 normalNode
    n1950[value]
    n1949 --> n1950
    class n1950 leafNode
    n1951[source]
    n1949 --> n1951
    class n1951 leafNode
    n1952[helium_3]
    n1930 --> n1952
    class n1952 normalNode
    n1953[value]
    n1952 --> n1953
    class n1953 leafNode
    n1954[source]
    n1952 --> n1954
    class n1954 leafNode
    n1955[helium_4]
    n1930 --> n1955
    class n1955 normalNode
    n1956[value]
    n1955 --> n1956
    class n1956 leafNode
    n1957[source]
    n1955 --> n1957
    class n1957 leafNode
    n1958[impurity_seeding]
    n1930 --> n1958
    class n1958 normalNode
    n1959[value]
    n1958 --> n1959
    class n1959 leafNode
    n1960[source]
    n1958 --> n1960
    class n1960 leafNode
    n1961[beryllium]
    n1930 --> n1961
    class n1961 normalNode
    n1962[value]
    n1961 --> n1962
    class n1962 leafNode
    n1963[source]
    n1961 --> n1963
    class n1963 leafNode
    n1964[lithium]
    n1930 --> n1964
    class n1964 normalNode
    n1965[value]
    n1964 --> n1965
    class n1965 leafNode
    n1966[source]
    n1964 --> n1966
    class n1966 leafNode
    n1967[carbon]
    n1930 --> n1967
    class n1967 normalNode
    n1968[value]
    n1967 --> n1968
    class n1968 leafNode
    n1969[source]
    n1967 --> n1969
    class n1969 leafNode
    n1970[oxygen]
    n1930 --> n1970
    class n1970 normalNode
    n1971[value]
    n1970 --> n1971
    class n1971 leafNode
    n1972[source]
    n1970 --> n1972
    class n1972 leafNode
    n1973[nitrogen]
    n1930 --> n1973
    class n1973 normalNode
    n1974[value]
    n1973 --> n1974
    class n1974 leafNode
    n1975[source]
    n1973 --> n1975
    class n1975 leafNode
    n1976[neon]
    n1930 --> n1976
    class n1976 normalNode
    n1977[value]
    n1976 --> n1977
    class n1977 leafNode
    n1978[source]
    n1976 --> n1978
    class n1978 leafNode
    n1979[argon]
    n1930 --> n1979
    class n1979 normalNode
    n1980[value]
    n1979 --> n1980
    class n1980 leafNode
    n1981[source]
    n1979 --> n1981
    class n1981 leafNode
    n1982[xenon]
    n1930 --> n1982
    class n1982 normalNode
    n1983[value]
    n1982 --> n1983
    class n1983 leafNode
    n1984[source]
    n1982 --> n1984
    class n1984 leafNode
    n1985[krypton]
    n1930 --> n1985
    class n1985 normalNode
    n1986[value]
    n1985 --> n1986
    class n1986 leafNode
    n1987[source]
    n1985 --> n1987
    class n1987 leafNode
    n1988[methane]
    n1930 --> n1988
    class n1988 normalNode
    n1989[value]
    n1988 --> n1989
    class n1989 leafNode
    n1990[source]
    n1988 --> n1990
    class n1990 leafNode
    n1991[methane_carbon_13]
    n1930 --> n1991
    class n1991 normalNode
    n1992[value]
    n1991 --> n1992
    class n1992 leafNode
    n1993[source]
    n1991 --> n1993
    class n1993 leafNode
    n1994[methane_deuterated]
    n1930 --> n1994
    class n1994 normalNode
    n1995[value]
    n1994 --> n1995
    class n1995 leafNode
    n1996[source]
    n1994 --> n1996
    class n1996 leafNode
    n1997[silane]
    n1930 --> n1997
    class n1997 normalNode
    n1998[value]
    n1997 --> n1998
    class n1998 leafNode
    n1999[source]
    n1997 --> n1999
    class n1999 leafNode
    n2000[ethylene]
    n1930 --> n2000
    class n2000 normalNode
    n2001[value]
    n2000 --> n2001
    class n2001 leafNode
    n2002[source]
    n2000 --> n2002
    class n2002 leafNode
    n2003[ethane]
    n1930 --> n2003
    class n2003 normalNode
    n2004[value]
    n2003 --> n2004
    class n2004 leafNode
    n2005[source]
    n2003 --> n2005
    class n2005 leafNode
    n2006[propane]
    n1930 --> n2006
    class n2006 normalNode
    n2007[value]
    n2006 --> n2007
    class n2007 leafNode
    n2008[source]
    n2006 --> n2008
    class n2008 leafNode
    n2009[ammonia]
    n1930 --> n2009
    class n2009 normalNode
    n2010[value]
    n2009 --> n2010
    class n2010 leafNode
    n2011[source]
    n2009 --> n2011
    class n2011 leafNode
    n2012[ammonia_deuterated]
    n1930 --> n2012
    class n2012 normalNode
    n2013[value]
    n2012 --> n2013
    class n2013 leafNode
    n2014[source]
    n2012 --> n2014
    class n2014 leafNode
    n2015(heating_current_drive)
    n1 --> n2015
    class n2015 complexNode
    n2016(ec)
    n2015 --> n2016
    class n2016 complexNode
    n2017[frequency]
    n2016 --> n2017
    class n2017 normalNode
    n2018[value]
    n2017 --> n2018
    class n2018 leafNode
    n2019[source]
    n2017 --> n2019
    class n2019 leafNode
    n2020[position]
    n2016 --> n2020
    class n2020 normalNode
    n2021[value]
    n2020 --> n2021
    class n2021 leafNode
    n2022[source]
    n2020 --> n2022
    class n2022 leafNode
    n2023[polarization]
    n2016 --> n2023
    class n2023 normalNode
    n2024[value]
    n2023 --> n2024
    class n2024 leafNode
    n2025[source]
    n2023 --> n2025
    class n2025 leafNode
    n2026[harmonic]
    n2016 --> n2026
    class n2026 normalNode
    n2027[value]
    n2026 --> n2027
    class n2027 leafNode
    n2028[source]
    n2026 --> n2028
    class n2028 leafNode
    n2029[phi]
    n2016 --> n2029
    class n2029 normalNode
    n2030[value]
    n2029 --> n2030
    class n2030 leafNode
    n2031[source]
    n2029 --> n2031
    class n2031 leafNode
    n2032[angle_pol]
    n2016 --> n2032
    class n2032 normalNode
    n2033[value]
    n2032 --> n2033
    class n2033 leafNode
    n2034[source]
    n2032 --> n2034
    class n2034 leafNode
    n2035[power]
    n2016 --> n2035
    class n2035 normalNode
    n2036[value]
    n2035 --> n2036
    class n2036 leafNode
    n2037[source]
    n2035 --> n2037
    class n2037 leafNode
    n2038[power_launched]
    n2016 --> n2038
    class n2038 normalNode
    n2039[value]
    n2038 --> n2039
    class n2039 leafNode
    n2040[source]
    n2038 --> n2040
    class n2040 leafNode
    n2041[current]
    n2016 --> n2041
    class n2041 normalNode
    n2042[value]
    n2041 --> n2042
    class n2042 leafNode
    n2043[source]
    n2041 --> n2043
    class n2043 leafNode
    n2044[energy_fast]
    n2016 --> n2044
    class n2044 normalNode
    n2045[value]
    n2044 --> n2045
    class n2045 leafNode
    n2046[source]
    n2044 --> n2046
    class n2046 leafNode
    n2047(nbi)
    n2015 --> n2047
    class n2047 complexNode
    n2048[species]
    n2047 --> n2048
    class n2048 normalNode
    n2049[a]
    n2048 --> n2049
    class n2049 normalNode
    n2050[value]
    n2049 --> n2050
    class n2050 leafNode
    n2051[source]
    n2049 --> n2051
    class n2051 leafNode
    n2052[z_n]
    n2048 --> n2052
    class n2052 normalNode
    n2053[value]
    n2052 --> n2053
    class n2053 leafNode
    n2054[source]
    n2052 --> n2054
    class n2054 leafNode
    n2055[name]
    n2048 --> n2055
    class n2055 normalNode
    n2056[value]
    n2055 --> n2056
    class n2056 leafNode
    n2057[source]
    n2055 --> n2057
    class n2057 leafNode
    n2058[power]
    n2047 --> n2058
    class n2058 normalNode
    n2059[value]
    n2058 --> n2059
    class n2059 leafNode
    n2060[source]
    n2058 --> n2060
    class n2060 leafNode
    n2061[power_launched]
    n2047 --> n2061
    class n2061 normalNode
    n2062[value]
    n2061 --> n2062
    class n2062 leafNode
    n2063[source]
    n2061 --> n2063
    class n2063 leafNode
    n2064[current]
    n2047 --> n2064
    class n2064 normalNode
    n2065[value]
    n2064 --> n2065
    class n2065 leafNode
    n2066[source]
    n2064 --> n2066
    class n2066 leafNode
    n2067[position]
    n2047 --> n2067
    class n2067 normalNode
    n2068[r]
    n2067 --> n2068
    class n2068 normalNode
    n2069[value]
    n2068 --> n2069
    class n2069 leafNode
    n2070[source]
    n2068 --> n2070
    class n2070 leafNode
    n2071[z]
    n2067 --> n2071
    class n2071 normalNode
    n2072[value]
    n2071 --> n2072
    class n2072 leafNode
    n2073[source]
    n2071 --> n2073
    class n2073 leafNode
    n2074[phi]
    n2067 --> n2074
    class n2074 normalNode
    n2075[value]
    n2074 --> n2075
    class n2075 leafNode
    n2076[source]
    n2074 --> n2076
    class n2076 leafNode
    n2077[tangency_radius]
    n2047 --> n2077
    class n2077 normalNode
    n2078[value]
    n2077 --> n2078
    class n2078 leafNode
    n2079[source]
    n2077 --> n2079
    class n2079 leafNode
    n2080[angle]
    n2047 --> n2080
    class n2080 normalNode
    n2081[value]
    n2080 --> n2081
    class n2081 leafNode
    n2082[source]
    n2080 --> n2082
    class n2082 leafNode
    n2083[direction]
    n2047 --> n2083
    class n2083 normalNode
    n2084[value]
    n2083 --> n2084
    class n2084 leafNode
    n2085[source]
    n2083 --> n2085
    class n2085 leafNode
    n2086[energy]
    n2047 --> n2086
    class n2086 normalNode
    n2087[value]
    n2086 --> n2087
    class n2087 leafNode
    n2088[source]
    n2086 --> n2088
    class n2088 leafNode
    n2089[beam_current_fraction]
    n2047 --> n2089
    class n2089 normalNode
    n2090[value]
    n2089 --> n2090
    class n2090 leafNode
    n2091[source]
    n2089 --> n2091
    class n2091 leafNode
    n2092[beam_power_fraction]
    n2047 --> n2092
    class n2092 normalNode
    n2093[value]
    n2092 --> n2093
    class n2093 leafNode
    n2094[source]
    n2092 --> n2094
    class n2094 leafNode
    n2095(ic)
    n2015 --> n2095
    class n2095 complexNode
    n2096[frequency]
    n2095 --> n2096
    class n2096 normalNode
    n2097[value]
    n2096 --> n2097
    class n2097 leafNode
    n2098[source]
    n2096 --> n2098
    class n2098 leafNode
    n2099[position]
    n2095 --> n2099
    class n2099 normalNode
    n2100[value]
    n2099 --> n2100
    class n2100 leafNode
    n2101[source]
    n2099 --> n2101
    class n2101 leafNode
    n2102[n_phi]
    n2095 --> n2102
    class n2102 normalNode
    n2103[value]
    n2102 --> n2103
    class n2103 leafNode
    n2104[source]
    n2102 --> n2104
    class n2104 leafNode
    n2105[k_perpendicular]
    n2095 --> n2105
    class n2105 normalNode
    n2106[value]
    n2105 --> n2106
    class n2106 leafNode
    n2107[source]
    n2105 --> n2107
    class n2107 leafNode
    n2108[e_field_plus_minus_ratio]
    n2095 --> n2108
    class n2108 normalNode
    n2109[value]
    n2108 --> n2109
    class n2109 leafNode
    n2110[source]
    n2108 --> n2110
    class n2110 leafNode
    n2111[harmonic]
    n2095 --> n2111
    class n2111 normalNode
    n2112[value]
    n2111 --> n2112
    class n2112 leafNode
    n2113[source]
    n2111 --> n2113
    class n2113 leafNode
    n2114[phase]
    n2095 --> n2114
    class n2114 normalNode
    n2115[value]
    n2114 --> n2115
    class n2115 leafNode
    n2116[source]
    n2114 --> n2116
    class n2116 leafNode
    n2117[power]
    n2095 --> n2117
    class n2117 normalNode
    n2118[value]
    n2117 --> n2118
    class n2118 leafNode
    n2119[source]
    n2117 --> n2119
    class n2119 leafNode
    n2120[power_launched]
    n2095 --> n2120
    class n2120 normalNode
    n2121[value]
    n2120 --> n2121
    class n2121 leafNode
    n2122[source]
    n2120 --> n2122
    class n2122 leafNode
    n2123[current]
    n2095 --> n2123
    class n2123 normalNode
    n2124[value]
    n2123 --> n2124
    class n2124 leafNode
    n2125[source]
    n2123 --> n2125
    class n2125 leafNode
    n2126[energy_fast]
    n2095 --> n2126
    class n2126 normalNode
    n2127[value]
    n2126 --> n2127
    class n2127 leafNode
    n2128[source]
    n2126 --> n2128
    class n2128 leafNode
    n2129(lh)
    n2015 --> n2129
    class n2129 complexNode
    n2130[frequency]
    n2129 --> n2130
    class n2130 normalNode
    n2131[value]
    n2130 --> n2131
    class n2131 leafNode
    n2132[source]
    n2130 --> n2132
    class n2132 leafNode
    n2133[position]
    n2129 --> n2133
    class n2133 normalNode
    n2134[value]
    n2133 --> n2134
    class n2134 leafNode
    n2135[source]
    n2133 --> n2135
    class n2135 leafNode
    n2136[n_parallel]
    n2129 --> n2136
    class n2136 normalNode
    n2137[value]
    n2136 --> n2137
    class n2137 leafNode
    n2138[source]
    n2136 --> n2138
    class n2138 leafNode
    n2139[power]
    n2129 --> n2139
    class n2139 normalNode
    n2140[value]
    n2139 --> n2140
    class n2140 leafNode
    n2141[source]
    n2139 --> n2141
    class n2141 leafNode
    n2142[power_launched]
    n2129 --> n2142
    class n2142 normalNode
    n2143[value]
    n2142 --> n2143
    class n2143 leafNode
    n2144[source]
    n2142 --> n2144
    class n2144 leafNode
    n2145[current]
    n2129 --> n2145
    class n2145 normalNode
    n2146[value]
    n2145 --> n2146
    class n2146 leafNode
    n2147[source]
    n2145 --> n2147
    class n2147 leafNode
    n2148[energy_fast]
    n2129 --> n2148
    class n2148 normalNode
    n2149[value]
    n2148 --> n2149
    class n2149 leafNode
    n2150[source]
    n2148 --> n2150
    class n2150 leafNode
    n2151[power_ec]
    n2015 --> n2151
    class n2151 normalNode
    n2152[value]
    n2151 --> n2152
    class n2152 leafNode
    n2153[source]
    n2151 --> n2153
    class n2153 leafNode
    n2154[power_launched_ec]
    n2015 --> n2154
    class n2154 normalNode
    n2155[value]
    n2154 --> n2155
    class n2155 leafNode
    n2156[source]
    n2154 --> n2156
    class n2156 leafNode
    n2157[power_nbi]
    n2015 --> n2157
    class n2157 normalNode
    n2158[value]
    n2157 --> n2158
    class n2158 leafNode
    n2159[source]
    n2157 --> n2159
    class n2159 leafNode
    n2160[power_launched_nbi]
    n2015 --> n2160
    class n2160 normalNode
    n2161[value]
    n2160 --> n2161
    class n2161 leafNode
    n2162[source]
    n2160 --> n2162
    class n2162 leafNode
    n2163[power_launched_nbi_co_injected_ratio]
    n2015 --> n2163
    class n2163 normalNode
    n2164[value]
    n2163 --> n2164
    class n2164 leafNode
    n2165[source]
    n2163 --> n2165
    class n2165 leafNode
    n2166[power_ic]
    n2015 --> n2166
    class n2166 normalNode
    n2167[value]
    n2166 --> n2167
    class n2167 leafNode
    n2168[source]
    n2166 --> n2168
    class n2168 leafNode
    n2169[power_launched_ic]
    n2015 --> n2169
    class n2169 normalNode
    n2170[value]
    n2169 --> n2170
    class n2170 leafNode
    n2171[source]
    n2169 --> n2171
    class n2171 leafNode
    n2172[power_lh]
    n2015 --> n2172
    class n2172 normalNode
    n2173[value]
    n2172 --> n2173
    class n2173 leafNode
    n2174[source]
    n2172 --> n2174
    class n2174 leafNode
    n2175[power_launched_lh]
    n2015 --> n2175
    class n2175 normalNode
    n2176[value]
    n2175 --> n2176
    class n2176 leafNode
    n2177[source]
    n2175 --> n2177
    class n2177 leafNode
    n2178[power_additional]
    n2015 --> n2178
    class n2178 normalNode
    n2179[value]
    n2178 --> n2179
    class n2179 leafNode
    n2180[source]
    n2178 --> n2180
    class n2180 leafNode
    n2181[kicks]
    n1 --> n2181
    class n2181 normalNode
    n2182[occurrence]
    n2181 --> n2182
    class n2182 normalNode
    n2183[value]
    n2182 --> n2183
    class n2183 leafNode
    n2184[source]
    n2182 --> n2184
    class n2184 leafNode
    n2185[pellets]
    n1 --> n2185
    class n2185 normalNode
    n2186[occurrence]
    n2185 --> n2186
    class n2186 normalNode
    n2187[value]
    n2186 --> n2187
    class n2187 leafNode
    n2188[source]
    n2186 --> n2188
    class n2188 leafNode
    n2189[rmps]
    n1 --> n2189
    class n2189 normalNode
    n2190[occurrence]
    n2189 --> n2190
    class n2190 normalNode
    n2191[value]
    n2190 --> n2191
    class n2191 leafNode
    n2192[source]
    n2190 --> n2192
    class n2192 leafNode
    n2193[runaways]
    n1 --> n2193
    class n2193 normalNode
    n2194[particles]
    n2193 --> n2194
    class n2194 normalNode
    n2195[value]
    n2194 --> n2195
    class n2195 leafNode
    n2196[source]
    n2194 --> n2196
    class n2196 leafNode
    n2197[current]
    n2193 --> n2197
    class n2197 normalNode
    n2198[value]
    n2197 --> n2198
    class n2198 leafNode
    n2199[source]
    n2197 --> n2199
    class n2199 leafNode
    n2200(scrape_off_layer)
    n1 --> n2200
    class n2200 complexNode
    n2201[t_e_decay_length]
    n2200 --> n2201
    class n2201 normalNode
    n2202[value]
    n2201 --> n2202
    class n2202 leafNode
    n2203[source]
    n2201 --> n2203
    class n2203 leafNode
    n2204[t_i_average_decay_length]
    n2200 --> n2204
    class n2204 normalNode
    n2205[value]
    n2204 --> n2205
    class n2205 leafNode
    n2206[source]
    n2204 --> n2206
    class n2206 leafNode
    n2207[n_e_decay_length]
    n2200 --> n2207
    class n2207 normalNode
    n2208[value]
    n2207 --> n2208
    class n2208 leafNode
    n2209[source]
    n2207 --> n2209
    class n2209 leafNode
    n2210[n_i_total_decay_length]
    n2200 --> n2210
    class n2210 normalNode
    n2211[value]
    n2210 --> n2211
    class n2211 leafNode
    n2212[source]
    n2210 --> n2212
    class n2212 leafNode
    n2213[heat_flux_e_decay_length]
    n2200 --> n2213
    class n2213 normalNode
    n2214[value]
    n2213 --> n2214
    class n2214 leafNode
    n2215[source]
    n2213 --> n2215
    class n2215 leafNode
    n2216[heat_flux_i_decay_length]
    n2200 --> n2216
    class n2216 normalNode
    n2217[value]
    n2216 --> n2217
    class n2217 leafNode
    n2218[source]
    n2216 --> n2218
    class n2218 leafNode
    n2219[power_radiated]
    n2200 --> n2219
    class n2219 normalNode
    n2220[value]
    n2219 --> n2220
    class n2220 leafNode
    n2221[source]
    n2219 --> n2221
    class n2221 leafNode
    n2222[pressure_neutral]
    n2200 --> n2222
    class n2222 normalNode
    n2223[value]
    n2222 --> n2223
    class n2223 leafNode
    n2224[source]
    n2222 --> n2224
    class n2224 leafNode
    n2225[wall]
    n1 --> n2225
    class n2225 normalNode
    n2226[material]
    n2225 --> n2226
    class n2226 normalNode
    n2227[name]
    n2226 --> n2227
    class n2227 leafNode
    n2228[index]
    n2226 --> n2228
    class n2228 leafNode
    n2229[description]
    n2226 --> n2229
    class n2229 leafNode
    n2230[evaporation]
    n2225 --> n2230
    class n2230 normalNode
    n2231[value]
    n2230 --> n2231
    class n2231 leafNode
    n2232[source]
    n2230 --> n2232
    class n2232 leafNode
    n2233[limiter]
    n1 --> n2233
    class n2233 normalNode
    n2234[material]
    n2233 --> n2234
    class n2234 normalNode
    n2235[name]
    n2234 --> n2235
    class n2235 leafNode
    n2236[index]
    n2234 --> n2236
    class n2236 leafNode
    n2237[description]
    n2234 --> n2237
    class n2237 leafNode
    n2238[time_breakdown]
    n1 --> n2238
    class n2238 normalNode
    n2239[value]
    n2238 --> n2239
    class n2239 leafNode
    n2240[source]
    n2238 --> n2240
    class n2240 leafNode
    n2241[plasma_duration]
    n1 --> n2241
    class n2241 normalNode
    n2242[value]
    n2241 --> n2242
    class n2242 leafNode
    n2243[source]
    n2241 --> n2243
    class n2243 leafNode
    n2244[time_width]
    n1 --> n2244
    class n2244 leafNode
    n2245[time]
    n1 --> n2245
    class n2245 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```