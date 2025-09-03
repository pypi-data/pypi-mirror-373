```mermaid
flowchart TD
    root["distributions IDS"]

    n1[distributions]
    root --> n1
    class n1 normalNode
    n2(distribution)
    n1 --> n2
    class n2 complexNode
    n3[wave]
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
    n10[process]
    n2 --> n10
    class n10 normalNode
    n11[type]
    n10 --> n11
    class n11 normalNode
    n12[name]
    n11 --> n12
    class n12 leafNode
    n13[index]
    n11 --> n13
    class n13 leafNode
    n14[description]
    n11 --> n14
    class n14 leafNode
    n15[reactant_energy]
    n10 --> n15
    class n15 normalNode
    n16[name]
    n15 --> n16
    class n16 leafNode
    n17[index]
    n15 --> n17
    class n17 leafNode
    n18[description]
    n15 --> n18
    class n18 leafNode
    n19[nbi_energy]
    n10 --> n19
    class n19 normalNode
    n20[name]
    n19 --> n20
    class n20 leafNode
    n21[index]
    n19 --> n21
    class n21 leafNode
    n22[description]
    n19 --> n22
    class n22 leafNode
    n23[nbi_unit]
    n10 --> n23
    class n23 leafNode
    n24[nbi_beamlets_group]
    n10 --> n24
    class n24 leafNode
    n25[gyro_type]
    n2 --> n25
    class n25 leafNode
    n26[species]
    n2 --> n26
    class n26 normalNode
    n27[type]
    n26 --> n27
    class n27 normalNode
    n28[name]
    n27 --> n28
    class n28 leafNode
    n29[index]
    n27 --> n29
    class n29 leafNode
    n30[description]
    n27 --> n30
    class n30 leafNode
    n31[ion]
    n26 --> n31
    class n31 normalNode
    n32[element]
    n31 --> n32
    class n32 normalNode
    n33[a]
    n32 --> n33
    class n33 leafNode
    n34[z_n]
    n32 --> n34
    class n34 leafNode
    n35[atoms_n]
    n32 --> n35
    class n35 leafNode
    n36[z_ion]
    n31 --> n36
    class n36 leafNode
    n37[name]
    n31 --> n37
    class n37 leafNode
    n38(state)
    n31 --> n38
    class n38 complexNode
    n39[z_min]
    n38 --> n39
    class n39 leafNode
    n40[z_max]
    n38 --> n40
    class n40 leafNode
    n41[name]
    n38 --> n41
    class n41 leafNode
    n42[electron_configuration]
    n38 --> n42
    class n42 leafNode
    n43[vibrational_level]
    n38 --> n43
    class n43 leafNode
    n44[vibrational_mode]
    n38 --> n44
    class n44 leafNode
    n45[neutral]
    n26 --> n45
    class n45 normalNode
    n46[element]
    n45 --> n46
    class n46 normalNode
    n47[a]
    n46 --> n47
    class n47 leafNode
    n48[z_n]
    n46 --> n48
    class n48 leafNode
    n49[atoms_n]
    n46 --> n49
    class n49 leafNode
    n50[name]
    n45 --> n50
    class n50 leafNode
    n51[state]
    n45 --> n51
    class n51 normalNode
    n52[name]
    n51 --> n52
    class n52 leafNode
    n53[electron_configuration]
    n51 --> n53
    class n53 leafNode
    n54[vibrational_level]
    n51 --> n54
    class n54 leafNode
    n55[vibrational_mode]
    n51 --> n55
    class n55 leafNode
    n56[neutral_type]
    n51 --> n56
    class n56 normalNode
    n57[name]
    n56 --> n57
    class n57 leafNode
    n58[index]
    n56 --> n58
    class n58 leafNode
    n59[description]
    n56 --> n59
    class n59 leafNode
    n60(global_quantities)
    n2 --> n60
    class n60 complexNode
    n61[particles_n]
    n60 --> n61
    class n61 leafNode
    n62[particles_fast_n]
    n60 --> n62
    class n62 leafNode
    n63[energy]
    n60 --> n63
    class n63 leafNode
    n64[energy_fast]
    n60 --> n64
    class n64 leafNode
    n65[energy_fast_parallel]
    n60 --> n65
    class n65 leafNode
    n66[torque_tor_j_radial]
    n60 --> n66
    class n66 leafNode
    n67[current_phi]
    n60 --> n67
    class n67 leafNode
    n68[power_first_orbit]
    n60 --> n68
    class n68 leafNode
    n69[power_rotation]
    n60 --> n69
    class n69 leafNode
    n70[power_charge_exchange]
    n60 --> n70
    class n70 leafNode
    n71[collisions]
    n60 --> n71
    class n71 normalNode
    n72[electrons]
    n71 --> n72
    class n72 normalNode
    n73[power_thermal]
    n72 --> n73
    class n73 leafNode
    n74[power_fast]
    n72 --> n74
    class n74 leafNode
    n75[torque_thermal_phi]
    n72 --> n75
    class n75 leafNode
    n76[torque_fast_phi]
    n72 --> n76
    class n76 leafNode
    n77(ion)
    n71 --> n77
    class n77 complexNode
    n78[element]
    n77 --> n78
    class n78 normalNode
    n79[a]
    n78 --> n79
    class n79 leafNode
    n80[z_n]
    n78 --> n80
    class n80 leafNode
    n81[atoms_n]
    n78 --> n81
    class n81 leafNode
    n82[z_ion]
    n77 --> n82
    class n82 leafNode
    n83[name]
    n77 --> n83
    class n83 leafNode
    n84[neutral_index]
    n77 --> n84
    class n84 leafNode
    n85[power_thermal]
    n77 --> n85
    class n85 leafNode
    n86[power_fast]
    n77 --> n86
    class n86 leafNode
    n87[torque_thermal_phi]
    n77 --> n87
    class n87 leafNode
    n88[torque_fast_phi]
    n77 --> n88
    class n88 leafNode
    n89[multiple_states_flag]
    n77 --> n89
    class n89 leafNode
    n90(state)
    n77 --> n90
    class n90 complexNode
    n91[z_min]
    n90 --> n91
    class n91 leafNode
    n92[z_max]
    n90 --> n92
    class n92 leafNode
    n93[name]
    n90 --> n93
    class n93 leafNode
    n94[electron_configuration]
    n90 --> n94
    class n94 leafNode
    n95[vibrational_level]
    n90 --> n95
    class n95 leafNode
    n96[vibrational_mode]
    n90 --> n96
    class n96 leafNode
    n97[power_thermal]
    n90 --> n97
    class n97 leafNode
    n98[power_fast]
    n90 --> n98
    class n98 leafNode
    n99[torque_thermal_phi]
    n90 --> n99
    class n99 leafNode
    n100[torque_fast_phi]
    n90 --> n100
    class n100 leafNode
    n101[thermalization]
    n60 --> n101
    class n101 normalNode
    n102[particles]
    n101 --> n102
    class n102 leafNode
    n103[power]
    n101 --> n103
    class n103 leafNode
    n104[torque]
    n101 --> n104
    class n104 leafNode
    n105[source]
    n60 --> n105
    class n105 normalNode
    n106[identifier]
    n105 --> n106
    class n106 normalNode
    n107[type]
    n106 --> n107
    class n107 normalNode
    n108[name]
    n107 --> n108
    class n108 leafNode
    n109[index]
    n107 --> n109
    class n109 leafNode
    n110[description]
    n107 --> n110
    class n110 leafNode
    n111[wave_index]
    n106 --> n111
    class n111 leafNode
    n112[process_index]
    n106 --> n112
    class n112 leafNode
    n113[particles]
    n105 --> n113
    class n113 leafNode
    n114[power]
    n105 --> n114
    class n114 leafNode
    n115[torque_phi]
    n105 --> n115
    class n115 leafNode
    n116[time]
    n60 --> n116
    class n116 leafNode
    n117(profiles_1d)
    n2 --> n117
    class n117 complexNode
    n118(grid)
    n117 --> n118
    class n118 complexNode
    n119[rho_tor_norm]
    n118 --> n119
    class n119 leafNode
    n120[rho_tor]
    n118 --> n120
    class n120 leafNode
    n121[rho_pol_norm]
    n118 --> n121
    class n121 leafNode
    n122[psi]
    n118 --> n122
    class n122 leafNode
    n123[volume]
    n118 --> n123
    class n123 leafNode
    n124[area]
    n118 --> n124
    class n124 leafNode
    n125[surface]
    n118 --> n125
    class n125 leafNode
    n126[psi_magnetic_axis]
    n118 --> n126
    class n126 leafNode
    n127[psi_boundary]
    n118 --> n127
    class n127 leafNode
    n128[fast_filter]
    n117 --> n128
    class n128 normalNode
    n129[method]
    n128 --> n129
    class n129 normalNode
    n130[name]
    n129 --> n130
    class n130 leafNode
    n131[index]
    n129 --> n131
    class n131 leafNode
    n132[description]
    n129 --> n132
    class n132 leafNode
    n133[energy]
    n128 --> n133
    class n133 leafNode
    n134[density]
    n117 --> n134
    class n134 leafNode
    n135[density_fast]
    n117 --> n135
    class n135 leafNode
    n136[pressure]
    n117 --> n136
    class n136 leafNode
    n137[pressure_fast]
    n117 --> n137
    class n137 leafNode
    n138[pressure_fast_parallel]
    n117 --> n138
    class n138 leafNode
    n139[pressure_fast_perpendicular]
    n117 --> n139
    class n139 leafNode
    n140[current_phi]
    n117 --> n140
    class n140 leafNode
    n141[current_fast_phi]
    n117 --> n141
    class n141 leafNode
    n142[torque_phi_j_radial]
    n117 --> n142
    class n142 leafNode
    n143[collisions]
    n117 --> n143
    class n143 normalNode
    n144[electrons]
    n143 --> n144
    class n144 normalNode
    n145[power_thermal]
    n144 --> n145
    class n145 leafNode
    n146[power_fast]
    n144 --> n146
    class n146 leafNode
    n147[torque_thermal_phi]
    n144 --> n147
    class n147 leafNode
    n148[torque_fast_phi]
    n144 --> n148
    class n148 leafNode
    n149(ion)
    n143 --> n149
    class n149 complexNode
    n150[element]
    n149 --> n150
    class n150 normalNode
    n151[a]
    n150 --> n151
    class n151 leafNode
    n152[z_n]
    n150 --> n152
    class n152 leafNode
    n153[atoms_n]
    n150 --> n153
    class n153 leafNode
    n154[z_ion]
    n149 --> n154
    class n154 leafNode
    n155[name]
    n149 --> n155
    class n155 leafNode
    n156[neutral_index]
    n149 --> n156
    class n156 leafNode
    n157[power_thermal]
    n149 --> n157
    class n157 leafNode
    n158[power_fast]
    n149 --> n158
    class n158 leafNode
    n159[torque_thermal_phi]
    n149 --> n159
    class n159 leafNode
    n160[torque_fast_phi]
    n149 --> n160
    class n160 leafNode
    n161[multiple_states_flag]
    n149 --> n161
    class n161 leafNode
    n162(state)
    n149 --> n162
    class n162 complexNode
    n163[z_min]
    n162 --> n163
    class n163 leafNode
    n164[z_max]
    n162 --> n164
    class n164 leafNode
    n165[name]
    n162 --> n165
    class n165 leafNode
    n166[electron_configuration]
    n162 --> n166
    class n166 leafNode
    n167[vibrational_level]
    n162 --> n167
    class n167 leafNode
    n168[vibrational_mode]
    n162 --> n168
    class n168 leafNode
    n169[power_thermal]
    n162 --> n169
    class n169 leafNode
    n170[power_fast]
    n162 --> n170
    class n170 leafNode
    n171[torque_thermal_phi]
    n162 --> n171
    class n171 leafNode
    n172[torque_fast_phi]
    n162 --> n172
    class n172 leafNode
    n173[thermalization]
    n117 --> n173
    class n173 normalNode
    n174[particles]
    n173 --> n174
    class n174 leafNode
    n175[energy]
    n173 --> n175
    class n175 leafNode
    n176[momentum_phi]
    n173 --> n176
    class n176 leafNode
    n177[source]
    n117 --> n177
    class n177 normalNode
    n178[identifier]
    n177 --> n178
    class n178 normalNode
    n179[type]
    n178 --> n179
    class n179 normalNode
    n180[name]
    n179 --> n180
    class n180 leafNode
    n181[index]
    n179 --> n181
    class n181 leafNode
    n182[description]
    n179 --> n182
    class n182 leafNode
    n183[wave_index]
    n178 --> n183
    class n183 leafNode
    n184[process_index]
    n178 --> n184
    class n184 leafNode
    n185[particles]
    n177 --> n185
    class n185 leafNode
    n186[energy]
    n177 --> n186
    class n186 leafNode
    n187[momentum_phi]
    n177 --> n187
    class n187 leafNode
    n188(trapped)
    n117 --> n188
    class n188 complexNode
    n189[density]
    n188 --> n189
    class n189 leafNode
    n190[density_fast]
    n188 --> n190
    class n190 leafNode
    n191[pressure]
    n188 --> n191
    class n191 leafNode
    n192[pressure_fast]
    n188 --> n192
    class n192 leafNode
    n193[pressure_fast_parallel]
    n188 --> n193
    class n193 leafNode
    n194[pressure_fast_perpendicular]
    n188 --> n194
    class n194 leafNode
    n195[current_phi]
    n188 --> n195
    class n195 leafNode
    n196[current_fast_phi]
    n188 --> n196
    class n196 leafNode
    n197[torque_phi_j_radial]
    n188 --> n197
    class n197 leafNode
    n198[collisions]
    n188 --> n198
    class n198 normalNode
    n199[electrons]
    n198 --> n199
    class n199 normalNode
    n200[power_thermal]
    n199 --> n200
    class n200 leafNode
    n201[power_fast]
    n199 --> n201
    class n201 leafNode
    n202[torque_thermal_phi]
    n199 --> n202
    class n202 leafNode
    n203[torque_fast_phi]
    n199 --> n203
    class n203 leafNode
    n204(ion)
    n198 --> n204
    class n204 complexNode
    n205[element]
    n204 --> n205
    class n205 normalNode
    n206[a]
    n205 --> n206
    class n206 leafNode
    n207[z_n]
    n205 --> n207
    class n207 leafNode
    n208[atoms_n]
    n205 --> n208
    class n208 leafNode
    n209[z_ion]
    n204 --> n209
    class n209 leafNode
    n210[name]
    n204 --> n210
    class n210 leafNode
    n211[neutral_index]
    n204 --> n211
    class n211 leafNode
    n212[power_thermal]
    n204 --> n212
    class n212 leafNode
    n213[power_fast]
    n204 --> n213
    class n213 leafNode
    n214[torque_thermal_phi]
    n204 --> n214
    class n214 leafNode
    n215[torque_fast_phi]
    n204 --> n215
    class n215 leafNode
    n216[multiple_states_flag]
    n204 --> n216
    class n216 leafNode
    n217(state)
    n204 --> n217
    class n217 complexNode
    n218[z_min]
    n217 --> n218
    class n218 leafNode
    n219[z_max]
    n217 --> n219
    class n219 leafNode
    n220[name]
    n217 --> n220
    class n220 leafNode
    n221[electron_configuration]
    n217 --> n221
    class n221 leafNode
    n222[vibrational_level]
    n217 --> n222
    class n222 leafNode
    n223[vibrational_mode]
    n217 --> n223
    class n223 leafNode
    n224[power_thermal]
    n217 --> n224
    class n224 leafNode
    n225[power_fast]
    n217 --> n225
    class n225 leafNode
    n226[torque_thermal_phi]
    n217 --> n226
    class n226 leafNode
    n227[torque_fast_phi]
    n217 --> n227
    class n227 leafNode
    n228[source]
    n188 --> n228
    class n228 normalNode
    n229[identifier]
    n228 --> n229
    class n229 normalNode
    n230[type]
    n229 --> n230
    class n230 normalNode
    n231[name]
    n230 --> n231
    class n231 leafNode
    n232[index]
    n230 --> n232
    class n232 leafNode
    n233[description]
    n230 --> n233
    class n233 leafNode
    n234[wave_index]
    n229 --> n234
    class n234 leafNode
    n235[process_index]
    n229 --> n235
    class n235 leafNode
    n236[particles]
    n228 --> n236
    class n236 leafNode
    n237[energy]
    n228 --> n237
    class n237 leafNode
    n238[momentum_phi]
    n228 --> n238
    class n238 leafNode
    n239(co_passing)
    n117 --> n239
    class n239 complexNode
    n240[density]
    n239 --> n240
    class n240 leafNode
    n241[density_fast]
    n239 --> n241
    class n241 leafNode
    n242[pressure]
    n239 --> n242
    class n242 leafNode
    n243[pressure_fast]
    n239 --> n243
    class n243 leafNode
    n244[pressure_fast_parallel]
    n239 --> n244
    class n244 leafNode
    n245[pressure_fast_perpendicular]
    n239 --> n245
    class n245 leafNode
    n246[current_phi]
    n239 --> n246
    class n246 leafNode
    n247[current_fast_phi]
    n239 --> n247
    class n247 leafNode
    n248[torque_phi_j_radial]
    n239 --> n248
    class n248 leafNode
    n249[collisions]
    n239 --> n249
    class n249 normalNode
    n250[electrons]
    n249 --> n250
    class n250 normalNode
    n251[power_thermal]
    n250 --> n251
    class n251 leafNode
    n252[power_fast]
    n250 --> n252
    class n252 leafNode
    n253[torque_thermal_phi]
    n250 --> n253
    class n253 leafNode
    n254[torque_fast_phi]
    n250 --> n254
    class n254 leafNode
    n255(ion)
    n249 --> n255
    class n255 complexNode
    n256[element]
    n255 --> n256
    class n256 normalNode
    n257[a]
    n256 --> n257
    class n257 leafNode
    n258[z_n]
    n256 --> n258
    class n258 leafNode
    n259[atoms_n]
    n256 --> n259
    class n259 leafNode
    n260[z_ion]
    n255 --> n260
    class n260 leafNode
    n261[name]
    n255 --> n261
    class n261 leafNode
    n262[neutral_index]
    n255 --> n262
    class n262 leafNode
    n263[power_thermal]
    n255 --> n263
    class n263 leafNode
    n264[power_fast]
    n255 --> n264
    class n264 leafNode
    n265[torque_thermal_phi]
    n255 --> n265
    class n265 leafNode
    n266[torque_fast_phi]
    n255 --> n266
    class n266 leafNode
    n267[multiple_states_flag]
    n255 --> n267
    class n267 leafNode
    n268(state)
    n255 --> n268
    class n268 complexNode
    n269[z_min]
    n268 --> n269
    class n269 leafNode
    n270[z_max]
    n268 --> n270
    class n270 leafNode
    n271[name]
    n268 --> n271
    class n271 leafNode
    n272[electron_configuration]
    n268 --> n272
    class n272 leafNode
    n273[vibrational_level]
    n268 --> n273
    class n273 leafNode
    n274[vibrational_mode]
    n268 --> n274
    class n274 leafNode
    n275[power_thermal]
    n268 --> n275
    class n275 leafNode
    n276[power_fast]
    n268 --> n276
    class n276 leafNode
    n277[torque_thermal_phi]
    n268 --> n277
    class n277 leafNode
    n278[torque_fast_phi]
    n268 --> n278
    class n278 leafNode
    n279[source]
    n239 --> n279
    class n279 normalNode
    n280[identifier]
    n279 --> n280
    class n280 normalNode
    n281[type]
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
    n285[wave_index]
    n280 --> n285
    class n285 leafNode
    n286[process_index]
    n280 --> n286
    class n286 leafNode
    n287[particles]
    n279 --> n287
    class n287 leafNode
    n288[energy]
    n279 --> n288
    class n288 leafNode
    n289[momentum_phi]
    n279 --> n289
    class n289 leafNode
    n290(counter_passing)
    n117 --> n290
    class n290 complexNode
    n291[density]
    n290 --> n291
    class n291 leafNode
    n292[density_fast]
    n290 --> n292
    class n292 leafNode
    n293[pressure]
    n290 --> n293
    class n293 leafNode
    n294[pressure_fast]
    n290 --> n294
    class n294 leafNode
    n295[pressure_fast_parallel]
    n290 --> n295
    class n295 leafNode
    n296[pressure_fast_perpendicular]
    n290 --> n296
    class n296 leafNode
    n297[current_phi]
    n290 --> n297
    class n297 leafNode
    n298[current_fast_phi]
    n290 --> n298
    class n298 leafNode
    n299[torque_phi_j_radial]
    n290 --> n299
    class n299 leafNode
    n300[collisions]
    n290 --> n300
    class n300 normalNode
    n301[electrons]
    n300 --> n301
    class n301 normalNode
    n302[power_thermal]
    n301 --> n302
    class n302 leafNode
    n303[power_fast]
    n301 --> n303
    class n303 leafNode
    n304[torque_thermal_phi]
    n301 --> n304
    class n304 leafNode
    n305[torque_fast_phi]
    n301 --> n305
    class n305 leafNode
    n306(ion)
    n300 --> n306
    class n306 complexNode
    n307[element]
    n306 --> n307
    class n307 normalNode
    n308[a]
    n307 --> n308
    class n308 leafNode
    n309[z_n]
    n307 --> n309
    class n309 leafNode
    n310[atoms_n]
    n307 --> n310
    class n310 leafNode
    n311[z_ion]
    n306 --> n311
    class n311 leafNode
    n312[name]
    n306 --> n312
    class n312 leafNode
    n313[neutral_index]
    n306 --> n313
    class n313 leafNode
    n314[power_thermal]
    n306 --> n314
    class n314 leafNode
    n315[power_fast]
    n306 --> n315
    class n315 leafNode
    n316[torque_thermal_phi]
    n306 --> n316
    class n316 leafNode
    n317[torque_fast_phi]
    n306 --> n317
    class n317 leafNode
    n318[multiple_states_flag]
    n306 --> n318
    class n318 leafNode
    n319(state)
    n306 --> n319
    class n319 complexNode
    n320[z_min]
    n319 --> n320
    class n320 leafNode
    n321[z_max]
    n319 --> n321
    class n321 leafNode
    n322[name]
    n319 --> n322
    class n322 leafNode
    n323[electron_configuration]
    n319 --> n323
    class n323 leafNode
    n324[vibrational_level]
    n319 --> n324
    class n324 leafNode
    n325[vibrational_mode]
    n319 --> n325
    class n325 leafNode
    n326[power_thermal]
    n319 --> n326
    class n326 leafNode
    n327[power_fast]
    n319 --> n327
    class n327 leafNode
    n328[torque_thermal_phi]
    n319 --> n328
    class n328 leafNode
    n329[torque_fast_phi]
    n319 --> n329
    class n329 leafNode
    n330[source]
    n290 --> n330
    class n330 normalNode
    n331[identifier]
    n330 --> n331
    class n331 normalNode
    n332[type]
    n331 --> n332
    class n332 normalNode
    n333[name]
    n332 --> n333
    class n333 leafNode
    n334[index]
    n332 --> n334
    class n334 leafNode
    n335[description]
    n332 --> n335
    class n335 leafNode
    n336[wave_index]
    n331 --> n336
    class n336 leafNode
    n337[process_index]
    n331 --> n337
    class n337 leafNode
    n338[particles]
    n330 --> n338
    class n338 leafNode
    n339[energy]
    n330 --> n339
    class n339 leafNode
    n340[momentum_phi]
    n330 --> n340
    class n340 leafNode
    n341[time]
    n117 --> n341
    class n341 leafNode
    n342(profiles_2d)
    n2 --> n342
    class n342 complexNode
    n343(grid)
    n342 --> n343
    class n343 complexNode
    n344[type]
    n343 --> n344
    class n344 normalNode
    n345[name]
    n344 --> n345
    class n345 leafNode
    n346[index]
    n344 --> n346
    class n346 leafNode
    n347[description]
    n344 --> n347
    class n347 leafNode
    n348[r]
    n343 --> n348
    class n348 leafNode
    n349[z]
    n343 --> n349
    class n349 leafNode
    n350[theta_straight]
    n343 --> n350
    class n350 leafNode
    n351[theta_geometric]
    n343 --> n351
    class n351 leafNode
    n352[rho_tor_norm]
    n343 --> n352
    class n352 leafNode
    n353[rho_tor]
    n343 --> n353
    class n353 leafNode
    n354[psi]
    n343 --> n354
    class n354 leafNode
    n355[volume]
    n343 --> n355
    class n355 leafNode
    n356[area]
    n343 --> n356
    class n356 leafNode
    n357[density]
    n342 --> n357
    class n357 leafNode
    n358[density_fast]
    n342 --> n358
    class n358 leafNode
    n359[pressure]
    n342 --> n359
    class n359 leafNode
    n360[pressure_fast]
    n342 --> n360
    class n360 leafNode
    n361[pressure_fast_parallel]
    n342 --> n361
    class n361 leafNode
    n362[pressure_fast_perpendicular]
    n342 --> n362
    class n362 leafNode
    n363[current_phi]
    n342 --> n363
    class n363 leafNode
    n364[current_fast_phi]
    n342 --> n364
    class n364 leafNode
    n365[torque_phi_j_radial]
    n342 --> n365
    class n365 leafNode
    n366[collisions]
    n342 --> n366
    class n366 normalNode
    n367[electrons]
    n366 --> n367
    class n367 normalNode
    n368[power_thermal]
    n367 --> n368
    class n368 leafNode
    n369[power_fast]
    n367 --> n369
    class n369 leafNode
    n370[torque_thermal_phi]
    n367 --> n370
    class n370 leafNode
    n371[torque_fast_phi]
    n367 --> n371
    class n371 leafNode
    n372(ion)
    n366 --> n372
    class n372 complexNode
    n373[element]
    n372 --> n373
    class n373 normalNode
    n374[a]
    n373 --> n374
    class n374 leafNode
    n375[z_n]
    n373 --> n375
    class n375 leafNode
    n376[atoms_n]
    n373 --> n376
    class n376 leafNode
    n377[z_ion]
    n372 --> n377
    class n377 leafNode
    n378[name]
    n372 --> n378
    class n378 leafNode
    n379[neutral_index]
    n372 --> n379
    class n379 leafNode
    n380[power_thermal]
    n372 --> n380
    class n380 leafNode
    n381[power_fast]
    n372 --> n381
    class n381 leafNode
    n382[torque_thermal_phi]
    n372 --> n382
    class n382 leafNode
    n383[torque_fast_phi]
    n372 --> n383
    class n383 leafNode
    n384[multiple_states_flag]
    n372 --> n384
    class n384 leafNode
    n385(state)
    n372 --> n385
    class n385 complexNode
    n386[z_min]
    n385 --> n386
    class n386 leafNode
    n387[z_max]
    n385 --> n387
    class n387 leafNode
    n388[name]
    n385 --> n388
    class n388 leafNode
    n389[electron_configuration]
    n385 --> n389
    class n389 leafNode
    n390[vibrational_level]
    n385 --> n390
    class n390 leafNode
    n391[vibrational_mode]
    n385 --> n391
    class n391 leafNode
    n392[power_thermal]
    n385 --> n392
    class n392 leafNode
    n393[power_fast]
    n385 --> n393
    class n393 leafNode
    n394[torque_thermal_phi]
    n385 --> n394
    class n394 leafNode
    n395[torque_fast_phi]
    n385 --> n395
    class n395 leafNode
    n396(trapped)
    n342 --> n396
    class n396 complexNode
    n397[density]
    n396 --> n397
    class n397 leafNode
    n398[density_fast]
    n396 --> n398
    class n398 leafNode
    n399[pressure]
    n396 --> n399
    class n399 leafNode
    n400[pressure_fast]
    n396 --> n400
    class n400 leafNode
    n401[pressure_fast_parallel]
    n396 --> n401
    class n401 leafNode
    n402[pressure_fast_perpendicular]
    n396 --> n402
    class n402 leafNode
    n403[current_phi]
    n396 --> n403
    class n403 leafNode
    n404[current_fast_phi]
    n396 --> n404
    class n404 leafNode
    n405[torque_phi_j_radial]
    n396 --> n405
    class n405 leafNode
    n406[collisions]
    n396 --> n406
    class n406 normalNode
    n407[electrons]
    n406 --> n407
    class n407 normalNode
    n408[power_thermal]
    n407 --> n408
    class n408 leafNode
    n409[power_fast]
    n407 --> n409
    class n409 leafNode
    n410[torque_thermal_phi]
    n407 --> n410
    class n410 leafNode
    n411[torque_fast_phi]
    n407 --> n411
    class n411 leafNode
    n412(ion)
    n406 --> n412
    class n412 complexNode
    n413[element]
    n412 --> n413
    class n413 normalNode
    n414[a]
    n413 --> n414
    class n414 leafNode
    n415[z_n]
    n413 --> n415
    class n415 leafNode
    n416[atoms_n]
    n413 --> n416
    class n416 leafNode
    n417[z_ion]
    n412 --> n417
    class n417 leafNode
    n418[name]
    n412 --> n418
    class n418 leafNode
    n419[neutral_index]
    n412 --> n419
    class n419 leafNode
    n420[power_thermal]
    n412 --> n420
    class n420 leafNode
    n421[power_fast]
    n412 --> n421
    class n421 leafNode
    n422[torque_thermal_phi]
    n412 --> n422
    class n422 leafNode
    n423[torque_fast_phi]
    n412 --> n423
    class n423 leafNode
    n424[multiple_states_flag]
    n412 --> n424
    class n424 leafNode
    n425(state)
    n412 --> n425
    class n425 complexNode
    n426[z_min]
    n425 --> n426
    class n426 leafNode
    n427[z_max]
    n425 --> n427
    class n427 leafNode
    n428[name]
    n425 --> n428
    class n428 leafNode
    n429[electron_configuration]
    n425 --> n429
    class n429 leafNode
    n430[vibrational_level]
    n425 --> n430
    class n430 leafNode
    n431[vibrational_mode]
    n425 --> n431
    class n431 leafNode
    n432[power_thermal]
    n425 --> n432
    class n432 leafNode
    n433[power_fast]
    n425 --> n433
    class n433 leafNode
    n434[torque_thermal_phi]
    n425 --> n434
    class n434 leafNode
    n435[torque_fast_tor]
    n425 --> n435
    class n435 leafNode
    n436[torque_fast_phi]
    n425 --> n436
    class n436 leafNode
    n437(co_passing)
    n342 --> n437
    class n437 complexNode
    n438[density]
    n437 --> n438
    class n438 leafNode
    n439[density_fast]
    n437 --> n439
    class n439 leafNode
    n440[pressure]
    n437 --> n440
    class n440 leafNode
    n441[pressure_fast]
    n437 --> n441
    class n441 leafNode
    n442[pressure_fast_parallel]
    n437 --> n442
    class n442 leafNode
    n443[pressure_fast_perpendicular]
    n437 --> n443
    class n443 leafNode
    n444[current_phi]
    n437 --> n444
    class n444 leafNode
    n445[current_fast_phi]
    n437 --> n445
    class n445 leafNode
    n446[torque_phi_j_radial]
    n437 --> n446
    class n446 leafNode
    n447[collisions]
    n437 --> n447
    class n447 normalNode
    n448[electrons]
    n447 --> n448
    class n448 normalNode
    n449[power_thermal]
    n448 --> n449
    class n449 leafNode
    n450[power_fast]
    n448 --> n450
    class n450 leafNode
    n451[torque_thermal_phi]
    n448 --> n451
    class n451 leafNode
    n452[torque_fast_phi]
    n448 --> n452
    class n452 leafNode
    n453(ion)
    n447 --> n453
    class n453 complexNode
    n454[element]
    n453 --> n454
    class n454 normalNode
    n455[a]
    n454 --> n455
    class n455 leafNode
    n456[z_n]
    n454 --> n456
    class n456 leafNode
    n457[atoms_n]
    n454 --> n457
    class n457 leafNode
    n458[z_ion]
    n453 --> n458
    class n458 leafNode
    n459[name]
    n453 --> n459
    class n459 leafNode
    n460[neutral_index]
    n453 --> n460
    class n460 leafNode
    n461[power_thermal]
    n453 --> n461
    class n461 leafNode
    n462[power_fast]
    n453 --> n462
    class n462 leafNode
    n463[torque_thermal_phi]
    n453 --> n463
    class n463 leafNode
    n464[torque_fast_phi]
    n453 --> n464
    class n464 leafNode
    n465[multiple_states_flag]
    n453 --> n465
    class n465 leafNode
    n466(state)
    n453 --> n466
    class n466 complexNode
    n467[z_min]
    n466 --> n467
    class n467 leafNode
    n468[z_max]
    n466 --> n468
    class n468 leafNode
    n469[name]
    n466 --> n469
    class n469 leafNode
    n470[electron_configuration]
    n466 --> n470
    class n470 leafNode
    n471[vibrational_level]
    n466 --> n471
    class n471 leafNode
    n472[vibrational_mode]
    n466 --> n472
    class n472 leafNode
    n473[power_thermal]
    n466 --> n473
    class n473 leafNode
    n474[power_fast]
    n466 --> n474
    class n474 leafNode
    n475[torque_thermal_phi]
    n466 --> n475
    class n475 leafNode
    n476[torque_fast_tor]
    n466 --> n476
    class n476 leafNode
    n477[torque_fast_phi]
    n466 --> n477
    class n477 leafNode
    n478(counter_passing)
    n342 --> n478
    class n478 complexNode
    n479[density]
    n478 --> n479
    class n479 leafNode
    n480[density_fast]
    n478 --> n480
    class n480 leafNode
    n481[pressure]
    n478 --> n481
    class n481 leafNode
    n482[pressure_fast]
    n478 --> n482
    class n482 leafNode
    n483[pressure_fast_parallel]
    n478 --> n483
    class n483 leafNode
    n484[pressure_fast_perpendicular]
    n478 --> n484
    class n484 leafNode
    n485[current_phi]
    n478 --> n485
    class n485 leafNode
    n486[current_fast_phi]
    n478 --> n486
    class n486 leafNode
    n487[torque_phi_j_radial]
    n478 --> n487
    class n487 leafNode
    n488[collisions]
    n478 --> n488
    class n488 normalNode
    n489[electrons]
    n488 --> n489
    class n489 normalNode
    n490[power_thermal]
    n489 --> n490
    class n490 leafNode
    n491[power_fast]
    n489 --> n491
    class n491 leafNode
    n492[torque_thermal_phi]
    n489 --> n492
    class n492 leafNode
    n493[torque_fast_phi]
    n489 --> n493
    class n493 leafNode
    n494(ion)
    n488 --> n494
    class n494 complexNode
    n495[element]
    n494 --> n495
    class n495 normalNode
    n496[a]
    n495 --> n496
    class n496 leafNode
    n497[z_n]
    n495 --> n497
    class n497 leafNode
    n498[atoms_n]
    n495 --> n498
    class n498 leafNode
    n499[z_ion]
    n494 --> n499
    class n499 leafNode
    n500[name]
    n494 --> n500
    class n500 leafNode
    n501[neutral_index]
    n494 --> n501
    class n501 leafNode
    n502[power_thermal]
    n494 --> n502
    class n502 leafNode
    n503[power_fast]
    n494 --> n503
    class n503 leafNode
    n504[torque_thermal_phi]
    n494 --> n504
    class n504 leafNode
    n505[torque_fast_phi]
    n494 --> n505
    class n505 leafNode
    n506[multiple_states_flag]
    n494 --> n506
    class n506 leafNode
    n507(state)
    n494 --> n507
    class n507 complexNode
    n508[z_min]
    n507 --> n508
    class n508 leafNode
    n509[z_max]
    n507 --> n509
    class n509 leafNode
    n510[name]
    n507 --> n510
    class n510 leafNode
    n511[electron_configuration]
    n507 --> n511
    class n511 leafNode
    n512[vibrational_level]
    n507 --> n512
    class n512 leafNode
    n513[vibrational_mode]
    n507 --> n513
    class n513 leafNode
    n514[power_thermal]
    n507 --> n514
    class n514 leafNode
    n515[power_fast]
    n507 --> n515
    class n515 leafNode
    n516[torque_thermal_phi]
    n507 --> n516
    class n516 leafNode
    n517[torque_fast_tor]
    n507 --> n517
    class n517 leafNode
    n518[torque_fast_phi]
    n507 --> n518
    class n518 leafNode
    n519[time]
    n342 --> n519
    class n519 leafNode
    n520[is_delta_f]
    n2 --> n520
    class n520 leafNode
    n521(markers)
    n2 --> n521
    class n521 complexNode
    n522[coordinate_identifier]
    n521 --> n522
    class n522 normalNode
    n523[name]
    n522 --> n523
    class n523 leafNode
    n524[index]
    n522 --> n524
    class n524 leafNode
    n525[description]
    n522 --> n525
    class n525 leafNode
    n526[weights]
    n521 --> n526
    class n526 leafNode
    n527[positions]
    n521 --> n527
    class n527 leafNode
    n528[orbit_integrals]
    n521 --> n528
    class n528 normalNode
    n529[expressions]
    n528 --> n529
    class n529 leafNode
    n530[n_phi]
    n528 --> n530
    class n530 leafNode
    n531[m_pol]
    n528 --> n531
    class n531 leafNode
    n532[bounce_harmonics]
    n528 --> n532
    class n532 leafNode
    n533[values]
    n528 --> n533
    class n533 leafNode
    n534[orbit_integrals_instant]
    n521 --> n534
    class n534 normalNode
    n535[expressions]
    n534 --> n535
    class n535 leafNode
    n536[time_orbit]
    n534 --> n536
    class n536 leafNode
    n537[values]
    n534 --> n537
    class n537 leafNode
    n538[toroidal_mode]
    n521 --> n538
    class n538 leafNode
    n539[time]
    n521 --> n539
    class n539 leafNode
    n540[vacuum_toroidal_field]
    n1 --> n540
    class n540 normalNode
    n541[r0]
    n540 --> n541
    class n541 leafNode
    n542[b0]
    n540 --> n542
    class n542 leafNode
    n543[magnetic_axis]
    n1 --> n543
    class n543 normalNode
    n544[r]
    n543 --> n544
    class n544 leafNode
    n545[z]
    n543 --> n545
    class n545 leafNode
    n546[time]
    n1 --> n546
    class n546 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```