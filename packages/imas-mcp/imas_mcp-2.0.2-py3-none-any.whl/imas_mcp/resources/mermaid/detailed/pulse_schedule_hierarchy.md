```mermaid
flowchart TD
    root["pulse_schedule IDS"]

    n1(pulse_schedule)
    root --> n1
    class n1 complexNode
    n2[ic]
    n1 --> n2
    class n2 normalNode
    n3(antenna)
    n2 --> n3
    class n3 complexNode
    n4[name]
    n3 --> n4
    class n4 leafNode
    n5[description]
    n3 --> n5
    class n5 leafNode
    n6[power_type]
    n3 --> n6
    class n6 normalNode
    n7[name]
    n6 --> n7
    class n7 leafNode
    n8[index]
    n6 --> n8
    class n8 leafNode
    n9[description]
    n6 --> n9
    class n9 leafNode
    n10[power]
    n3 --> n10
    class n10 normalNode
    n11[reference_name]
    n10 --> n11
    class n11 leafNode
    n12[reference]
    n10 --> n12
    class n12 leafNode
    n13[reference_type]
    n10 --> n13
    class n13 leafNode
    n14[envelope_type]
    n10 --> n14
    class n14 leafNode
    n15[phase]
    n3 --> n15
    class n15 normalNode
    n16[reference_name]
    n15 --> n16
    class n16 leafNode
    n17[reference]
    n15 --> n17
    class n17 leafNode
    n18[reference_type]
    n15 --> n18
    class n18 leafNode
    n19[envelope_type]
    n15 --> n19
    class n19 leafNode
    n20[frequency]
    n3 --> n20
    class n20 normalNode
    n21[reference_name]
    n20 --> n21
    class n21 leafNode
    n22[reference]
    n20 --> n22
    class n22 leafNode
    n23[reference_type]
    n20 --> n23
    class n23 leafNode
    n24[envelope_type]
    n20 --> n24
    class n24 leafNode
    n25[power]
    n2 --> n25
    class n25 normalNode
    n26[reference_name]
    n25 --> n26
    class n26 leafNode
    n27[reference]
    n25 --> n27
    class n27 leafNode
    n28[reference_type]
    n25 --> n28
    class n28 leafNode
    n29[envelope_type]
    n25 --> n29
    class n29 leafNode
    n30[mode]
    n2 --> n30
    class n30 leafNode
    n31[time]
    n2 --> n31
    class n31 leafNode
    n32[ec]
    n1 --> n32
    class n32 normalNode
    n33(beam)
    n32 --> n33
    class n33 complexNode
    n34[name]
    n33 --> n34
    class n34 leafNode
    n35[description]
    n33 --> n35
    class n35 leafNode
    n36[power_launched]
    n33 --> n36
    class n36 normalNode
    n37[reference_name]
    n36 --> n37
    class n37 leafNode
    n38[reference]
    n36 --> n38
    class n38 leafNode
    n39[reference_type]
    n36 --> n39
    class n39 leafNode
    n40[envelope_type]
    n36 --> n40
    class n40 leafNode
    n41[frequency]
    n33 --> n41
    class n41 normalNode
    n42[reference_name]
    n41 --> n42
    class n42 leafNode
    n43[reference]
    n41 --> n43
    class n43 leafNode
    n44[reference_type]
    n41 --> n44
    class n44 leafNode
    n45[envelope_type]
    n41 --> n45
    class n45 leafNode
    n46[deposition_rho_tor_norm]
    n33 --> n46
    class n46 normalNode
    n47[reference_name]
    n46 --> n47
    class n47 leafNode
    n48[reference]
    n46 --> n48
    class n48 leafNode
    n49[reference_type]
    n46 --> n49
    class n49 leafNode
    n50[envelope_type]
    n46 --> n50
    class n50 leafNode
    n51[steering_angle_pol]
    n33 --> n51
    class n51 normalNode
    n52[reference_name]
    n51 --> n52
    class n52 leafNode
    n53[reference]
    n51 --> n53
    class n53 leafNode
    n54[reference_type]
    n51 --> n54
    class n54 leafNode
    n55[envelope_type]
    n51 --> n55
    class n55 leafNode
    n56[steering_angle_tor]
    n33 --> n56
    class n56 normalNode
    n57[reference_name]
    n56 --> n57
    class n57 leafNode
    n58[reference]
    n56 --> n58
    class n58 leafNode
    n59[reference_type]
    n56 --> n59
    class n59 leafNode
    n60[envelope_type]
    n56 --> n60
    class n60 leafNode
    n61[power_launched]
    n32 --> n61
    class n61 normalNode
    n62[reference_name]
    n61 --> n62
    class n62 leafNode
    n63[reference]
    n61 --> n63
    class n63 leafNode
    n64[reference_type]
    n61 --> n64
    class n64 leafNode
    n65[envelope_type]
    n61 --> n65
    class n65 leafNode
    n66[mode]
    n32 --> n66
    class n66 leafNode
    n67[time]
    n32 --> n67
    class n67 leafNode
    n68[lh]
    n1 --> n68
    class n68 normalNode
    n69(antenna)
    n68 --> n69
    class n69 complexNode
    n70[name]
    n69 --> n70
    class n70 leafNode
    n71[power_type]
    n69 --> n71
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
    n75[power]
    n69 --> n75
    class n75 normalNode
    n76[reference_name]
    n75 --> n76
    class n76 leafNode
    n77[reference]
    n75 --> n77
    class n77 leafNode
    n78[reference_type]
    n75 --> n78
    class n78 leafNode
    n79[envelope_type]
    n75 --> n79
    class n79 leafNode
    n80[phase]
    n69 --> n80
    class n80 normalNode
    n81[reference_name]
    n80 --> n81
    class n81 leafNode
    n82[reference]
    n80 --> n82
    class n82 leafNode
    n83[reference_type]
    n80 --> n83
    class n83 leafNode
    n84[envelope_type]
    n80 --> n84
    class n84 leafNode
    n85[n_parallel]
    n69 --> n85
    class n85 normalNode
    n86[reference_name]
    n85 --> n86
    class n86 leafNode
    n87[reference]
    n85 --> n87
    class n87 leafNode
    n88[reference_type]
    n85 --> n88
    class n88 leafNode
    n89[envelope_type]
    n85 --> n89
    class n89 leafNode
    n90[frequency]
    n69 --> n90
    class n90 normalNode
    n91[reference_name]
    n90 --> n91
    class n91 leafNode
    n92[reference]
    n90 --> n92
    class n92 leafNode
    n93[reference_type]
    n90 --> n93
    class n93 leafNode
    n94[envelope_type]
    n90 --> n94
    class n94 leafNode
    n95[description]
    n69 --> n95
    class n95 leafNode
    n96[power]
    n68 --> n96
    class n96 normalNode
    n97[reference_name]
    n96 --> n97
    class n97 leafNode
    n98[reference]
    n96 --> n98
    class n98 leafNode
    n99[reference_type]
    n96 --> n99
    class n99 leafNode
    n100[envelope_type]
    n96 --> n100
    class n100 leafNode
    n101[mode]
    n68 --> n101
    class n101 leafNode
    n102[time]
    n68 --> n102
    class n102 leafNode
    n103[nbi]
    n1 --> n103
    class n103 normalNode
    n104[unit]
    n103 --> n104
    class n104 normalNode
    n105[name]
    n104 --> n105
    class n105 leafNode
    n106[description]
    n104 --> n106
    class n106 leafNode
    n107[species]
    n104 --> n107
    class n107 normalNode
    n108[element]
    n107 --> n108
    class n108 normalNode
    n109[a]
    n108 --> n109
    class n109 leafNode
    n110[z_n]
    n108 --> n110
    class n110 leafNode
    n111[atoms_n]
    n108 --> n111
    class n111 leafNode
    n112[name]
    n107 --> n112
    class n112 leafNode
    n113[fraction]
    n107 --> n113
    class n113 leafNode
    n114[power]
    n104 --> n114
    class n114 normalNode
    n115[reference_name]
    n114 --> n115
    class n115 leafNode
    n116[reference]
    n114 --> n116
    class n116 leafNode
    n117[reference_type]
    n114 --> n117
    class n117 leafNode
    n118[envelope_type]
    n114 --> n118
    class n118 leafNode
    n119[energy]
    n104 --> n119
    class n119 normalNode
    n120[reference_name]
    n119 --> n120
    class n120 leafNode
    n121[reference]
    n119 --> n121
    class n121 leafNode
    n122[reference_type]
    n119 --> n122
    class n122 leafNode
    n123[envelope_type]
    n119 --> n123
    class n123 leafNode
    n124[power]
    n103 --> n124
    class n124 normalNode
    n125[reference_name]
    n124 --> n125
    class n125 leafNode
    n126[reference]
    n124 --> n126
    class n126 leafNode
    n127[reference_type]
    n124 --> n127
    class n127 leafNode
    n128[envelope_type]
    n124 --> n128
    class n128 leafNode
    n129[mode]
    n103 --> n129
    class n129 leafNode
    n130[time]
    n103 --> n130
    class n130 leafNode
    n131(density_control)
    n1 --> n131
    class n131 complexNode
    n132[valve]
    n131 --> n132
    class n132 normalNode
    n133[name]
    n132 --> n133
    class n133 leafNode
    n134[description]
    n132 --> n134
    class n134 leafNode
    n135[flow_rate]
    n132 --> n135
    class n135 normalNode
    n136[reference_name]
    n135 --> n136
    class n136 leafNode
    n137[reference]
    n135 --> n137
    class n137 leafNode
    n138[reference_type]
    n135 --> n138
    class n138 leafNode
    n139[envelope_type]
    n135 --> n139
    class n139 leafNode
    n140[species]
    n132 --> n140
    class n140 normalNode
    n141[element]
    n140 --> n141
    class n141 normalNode
    n142[a]
    n141 --> n142
    class n142 leafNode
    n143[z_n]
    n141 --> n143
    class n143 leafNode
    n144[atoms_n]
    n141 --> n144
    class n144 leafNode
    n145[name]
    n140 --> n145
    class n145 leafNode
    n146[fraction]
    n140 --> n146
    class n146 leafNode
    n147[n_e_line]
    n131 --> n147
    class n147 normalNode
    n148[reference_name]
    n147 --> n148
    class n148 leafNode
    n149[reference]
    n147 --> n149
    class n149 leafNode
    n150[reference_type]
    n147 --> n150
    class n150 leafNode
    n151[envelope_type]
    n147 --> n151
    class n151 leafNode
    n152[n_e_line_lcfs]
    n131 --> n152
    class n152 normalNode
    n153[reference_name]
    n152 --> n153
    class n153 leafNode
    n154[reference]
    n152 --> n154
    class n154 leafNode
    n155[reference_type]
    n152 --> n155
    class n155 leafNode
    n156[envelope_type]
    n152 --> n156
    class n156 leafNode
    n157[n_e_profile_average]
    n131 --> n157
    class n157 normalNode
    n158[reference_name]
    n157 --> n158
    class n158 leafNode
    n159[reference]
    n157 --> n159
    class n159 leafNode
    n160[reference_type]
    n157 --> n160
    class n160 leafNode
    n161[envelope_type]
    n157 --> n161
    class n161 leafNode
    n162[n_e_line_of_sight]
    n131 --> n162
    class n162 normalNode
    n163[first_point]
    n162 --> n163
    class n163 normalNode
    n164[r]
    n163 --> n164
    class n164 leafNode
    n165[phi]
    n163 --> n165
    class n165 leafNode
    n166[z]
    n163 --> n166
    class n166 leafNode
    n167[second_point]
    n162 --> n167
    class n167 normalNode
    n168[r]
    n167 --> n168
    class n168 leafNode
    n169[phi]
    n167 --> n169
    class n169 leafNode
    n170[z]
    n167 --> n170
    class n170 leafNode
    n171[third_point]
    n162 --> n171
    class n171 normalNode
    n172[r]
    n171 --> n172
    class n172 leafNode
    n173[phi]
    n171 --> n173
    class n173 leafNode
    n174[z]
    n171 --> n174
    class n174 leafNode
    n175[n_e_volume_average]
    n131 --> n175
    class n175 normalNode
    n176[reference_name]
    n175 --> n176
    class n176 leafNode
    n177[reference]
    n175 --> n177
    class n177 leafNode
    n178[reference_type]
    n175 --> n178
    class n178 leafNode
    n179[envelope_type]
    n175 --> n179
    class n179 leafNode
    n180[zeff]
    n131 --> n180
    class n180 normalNode
    n181[reference_name]
    n180 --> n181
    class n181 leafNode
    n182[reference]
    n180 --> n182
    class n182 leafNode
    n183[reference_type]
    n180 --> n183
    class n183 leafNode
    n184[envelope_type]
    n180 --> n184
    class n184 leafNode
    n185[zeff_method]
    n131 --> n185
    class n185 normalNode
    n186[name]
    n185 --> n186
    class n186 leafNode
    n187[index]
    n185 --> n187
    class n187 leafNode
    n188[description]
    n185 --> n188
    class n188 leafNode
    n189[zeff_line_of_sight]
    n131 --> n189
    class n189 normalNode
    n190[first_point]
    n189 --> n190
    class n190 normalNode
    n191[r]
    n190 --> n191
    class n191 leafNode
    n192[phi]
    n190 --> n192
    class n192 leafNode
    n193[z]
    n190 --> n193
    class n193 leafNode
    n194[second_point]
    n189 --> n194
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
    n198[third_point]
    n189 --> n198
    class n198 normalNode
    n199[r]
    n198 --> n199
    class n199 leafNode
    n200[phi]
    n198 --> n200
    class n200 leafNode
    n201[z]
    n198 --> n201
    class n201 leafNode
    n202[n_t_over_n_d]
    n131 --> n202
    class n202 normalNode
    n203[reference_name]
    n202 --> n203
    class n203 leafNode
    n204[reference]
    n202 --> n204
    class n204 leafNode
    n205[reference_type]
    n202 --> n205
    class n205 leafNode
    n206[envelope_type]
    n202 --> n206
    class n206 leafNode
    n207[n_h_over_n_d]
    n131 --> n207
    class n207 normalNode
    n208[reference_name]
    n207 --> n208
    class n208 leafNode
    n209[reference]
    n207 --> n209
    class n209 leafNode
    n210[reference_type]
    n207 --> n210
    class n210 leafNode
    n211[envelope_type]
    n207 --> n211
    class n211 leafNode
    n212[ion]
    n131 --> n212
    class n212 normalNode
    n213[element]
    n212 --> n213
    class n213 normalNode
    n214[a]
    n213 --> n214
    class n214 leafNode
    n215[z_n]
    n213 --> n215
    class n215 leafNode
    n216[atoms_n]
    n213 --> n216
    class n216 leafNode
    n217[z_ion]
    n212 --> n217
    class n217 leafNode
    n218[name]
    n212 --> n218
    class n218 leafNode
    n219[n_i_volume_average]
    n212 --> n219
    class n219 normalNode
    n220[reference_name]
    n219 --> n220
    class n220 leafNode
    n221[reference]
    n219 --> n221
    class n221 leafNode
    n222[reference_type]
    n219 --> n222
    class n222 leafNode
    n223[envelope_type]
    n219 --> n223
    class n223 leafNode
    n224[mode]
    n131 --> n224
    class n224 leafNode
    n225[time]
    n131 --> n225
    class n225 leafNode
    n226(event)
    n1 --> n226
    class n226 complexNode
    n227[type]
    n226 --> n227
    class n227 normalNode
    n228[name]
    n227 --> n228
    class n228 leafNode
    n229[index]
    n227 --> n229
    class n229 leafNode
    n230[description]
    n227 --> n230
    class n230 leafNode
    n231[identifier]
    n226 --> n231
    class n231 leafNode
    n232[time_stamp]
    n226 --> n232
    class n232 leafNode
    n233[duration]
    n226 --> n233
    class n233 leafNode
    n234[acquisition_strategy]
    n226 --> n234
    class n234 normalNode
    n235[name]
    n234 --> n235
    class n235 leafNode
    n236[index]
    n234 --> n236
    class n236 leafNode
    n237[description]
    n234 --> n237
    class n237 leafNode
    n238[acquisition_state]
    n226 --> n238
    class n238 normalNode
    n239[name]
    n238 --> n239
    class n239 leafNode
    n240[index]
    n238 --> n240
    class n240 leafNode
    n241[description]
    n238 --> n241
    class n241 leafNode
    n242[provider]
    n226 --> n242
    class n242 leafNode
    n243[listeners]
    n226 --> n243
    class n243 leafNode
    n244(flux_control)
    n1 --> n244
    class n244 complexNode
    n245[ip]
    n244 --> n245
    class n245 normalNode
    n246[reference_name]
    n245 --> n246
    class n246 leafNode
    n247[reference]
    n245 --> n247
    class n247 leafNode
    n248[reference_type]
    n245 --> n248
    class n248 leafNode
    n249[envelope_type]
    n245 --> n249
    class n249 leafNode
    n250[v_loop]
    n244 --> n250
    class n250 normalNode
    n251[reference_name]
    n250 --> n251
    class n251 leafNode
    n252[reference]
    n250 --> n252
    class n252 leafNode
    n253[reference_type]
    n250 --> n253
    class n253 leafNode
    n254[envelope_type]
    n250 --> n254
    class n254 leafNode
    n255[li_3]
    n244 --> n255
    class n255 normalNode
    n256[reference_name]
    n255 --> n256
    class n256 leafNode
    n257[reference]
    n255 --> n257
    class n257 leafNode
    n258[reference_type]
    n255 --> n258
    class n258 leafNode
    n259[envelope_type]
    n255 --> n259
    class n259 leafNode
    n260[beta_tor_norm]
    n244 --> n260
    class n260 normalNode
    n261[reference_name]
    n260 --> n261
    class n261 leafNode
    n262[reference]
    n260 --> n262
    class n262 leafNode
    n263[reference_type]
    n260 --> n263
    class n263 leafNode
    n264[envelope_type]
    n260 --> n264
    class n264 leafNode
    n265[mode]
    n244 --> n265
    class n265 leafNode
    n266[time]
    n244 --> n266
    class n266 leafNode
    n267[pf_active]
    n1 --> n267
    class n267 normalNode
    n268[coil]
    n267 --> n268
    class n268 normalNode
    n269[name]
    n268 --> n269
    class n269 leafNode
    n270[description]
    n268 --> n270
    class n270 leafNode
    n271[current]
    n268 --> n271
    class n271 normalNode
    n272[reference_name]
    n271 --> n272
    class n272 leafNode
    n273[reference]
    n271 --> n273
    class n273 leafNode
    n274[reference_type]
    n271 --> n274
    class n274 leafNode
    n275[envelope_type]
    n271 --> n275
    class n275 leafNode
    n276[resistance_additional]
    n268 --> n276
    class n276 normalNode
    n277[reference_name]
    n276 --> n277
    class n277 leafNode
    n278[reference]
    n276 --> n278
    class n278 leafNode
    n279[reference_type]
    n276 --> n279
    class n279 leafNode
    n280[envelope_type]
    n276 --> n280
    class n280 leafNode
    n281[supply]
    n267 --> n281
    class n281 normalNode
    n282[name]
    n281 --> n282
    class n282 leafNode
    n283[description]
    n281 --> n283
    class n283 leafNode
    n284[voltage]
    n281 --> n284
    class n284 normalNode
    n285[reference_name]
    n284 --> n285
    class n285 leafNode
    n286[reference]
    n284 --> n286
    class n286 leafNode
    n287[reference_type]
    n284 --> n287
    class n287 leafNode
    n288[envelope_type]
    n284 --> n288
    class n288 leafNode
    n289[current]
    n281 --> n289
    class n289 normalNode
    n290[reference_name]
    n289 --> n290
    class n290 leafNode
    n291[reference]
    n289 --> n291
    class n291 leafNode
    n292[reference_type]
    n289 --> n292
    class n292 leafNode
    n293[envelope_type]
    n289 --> n293
    class n293 leafNode
    n294[mode]
    n267 --> n294
    class n294 leafNode
    n295[time]
    n267 --> n295
    class n295 leafNode
    n296(position_control)
    n1 --> n296
    class n296 complexNode
    n297[magnetic_axis]
    n296 --> n297
    class n297 normalNode
    n298[r]
    n297 --> n298
    class n298 normalNode
    n299[reference_name]
    n298 --> n299
    class n299 leafNode
    n300[reference]
    n298 --> n300
    class n300 leafNode
    n301[reference_type]
    n298 --> n301
    class n301 leafNode
    n302[envelope_type]
    n298 --> n302
    class n302 leafNode
    n303[z]
    n297 --> n303
    class n303 normalNode
    n304[reference_name]
    n303 --> n304
    class n304 leafNode
    n305[reference]
    n303 --> n305
    class n305 leafNode
    n306[reference_type]
    n303 --> n306
    class n306 leafNode
    n307[envelope_type]
    n303 --> n307
    class n307 leafNode
    n308[geometric_axis]
    n296 --> n308
    class n308 normalNode
    n309[r]
    n308 --> n309
    class n309 normalNode
    n310[reference_name]
    n309 --> n310
    class n310 leafNode
    n311[reference]
    n309 --> n311
    class n311 leafNode
    n312[reference_type]
    n309 --> n312
    class n312 leafNode
    n313[envelope_type]
    n309 --> n313
    class n313 leafNode
    n314[z]
    n308 --> n314
    class n314 normalNode
    n315[reference_name]
    n314 --> n315
    class n315 leafNode
    n316[reference]
    n314 --> n316
    class n316 leafNode
    n317[reference_type]
    n314 --> n317
    class n317 leafNode
    n318[envelope_type]
    n314 --> n318
    class n318 leafNode
    n319[minor_radius]
    n296 --> n319
    class n319 normalNode
    n320[reference_name]
    n319 --> n320
    class n320 leafNode
    n321[reference]
    n319 --> n321
    class n321 leafNode
    n322[reference_type]
    n319 --> n322
    class n322 leafNode
    n323[envelope_type]
    n319 --> n323
    class n323 leafNode
    n324[elongation]
    n296 --> n324
    class n324 normalNode
    n325[reference_name]
    n324 --> n325
    class n325 leafNode
    n326[reference]
    n324 --> n326
    class n326 leafNode
    n327[reference_type]
    n324 --> n327
    class n327 leafNode
    n328[envelope_type]
    n324 --> n328
    class n328 leafNode
    n329[elongation_upper]
    n296 --> n329
    class n329 normalNode
    n330[reference_name]
    n329 --> n330
    class n330 leafNode
    n331[reference]
    n329 --> n331
    class n331 leafNode
    n332[reference_type]
    n329 --> n332
    class n332 leafNode
    n333[envelope_type]
    n329 --> n333
    class n333 leafNode
    n334[elongation_lower]
    n296 --> n334
    class n334 normalNode
    n335[reference_name]
    n334 --> n335
    class n335 leafNode
    n336[reference]
    n334 --> n336
    class n336 leafNode
    n337[reference_type]
    n334 --> n337
    class n337 leafNode
    n338[envelope_type]
    n334 --> n338
    class n338 leafNode
    n339[triangularity]
    n296 --> n339
    class n339 normalNode
    n340[reference_name]
    n339 --> n340
    class n340 leafNode
    n341[reference]
    n339 --> n341
    class n341 leafNode
    n342[reference_type]
    n339 --> n342
    class n342 leafNode
    n343[envelope_type]
    n339 --> n343
    class n343 leafNode
    n344[triangularity_upper]
    n296 --> n344
    class n344 normalNode
    n345[reference_name]
    n344 --> n345
    class n345 leafNode
    n346[reference]
    n344 --> n346
    class n346 leafNode
    n347[reference_type]
    n344 --> n347
    class n347 leafNode
    n348[envelope_type]
    n344 --> n348
    class n348 leafNode
    n349[triangularity_lower]
    n296 --> n349
    class n349 normalNode
    n350[reference_name]
    n349 --> n350
    class n350 leafNode
    n351[reference]
    n349 --> n351
    class n351 leafNode
    n352[reference_type]
    n349 --> n352
    class n352 leafNode
    n353[envelope_type]
    n349 --> n353
    class n353 leafNode
    n354[triangularity_inner]
    n296 --> n354
    class n354 normalNode
    n355[reference_name]
    n354 --> n355
    class n355 leafNode
    n356[reference]
    n354 --> n356
    class n356 leafNode
    n357[reference_type]
    n354 --> n357
    class n357 leafNode
    n358[envelope_type]
    n354 --> n358
    class n358 leafNode
    n359[triangularity_outer]
    n296 --> n359
    class n359 normalNode
    n360[reference_name]
    n359 --> n360
    class n360 leafNode
    n361[reference]
    n359 --> n361
    class n361 leafNode
    n362[reference_type]
    n359 --> n362
    class n362 leafNode
    n363[envelope_type]
    n359 --> n363
    class n363 leafNode
    n364[triangularity_minor]
    n296 --> n364
    class n364 normalNode
    n365[reference_name]
    n364 --> n365
    class n365 leafNode
    n366[reference]
    n364 --> n366
    class n366 leafNode
    n367[reference_type]
    n364 --> n367
    class n367 leafNode
    n368[envelope_type]
    n364 --> n368
    class n368 leafNode
    n369[squareness_upper_outer]
    n296 --> n369
    class n369 normalNode
    n370[reference_name]
    n369 --> n370
    class n370 leafNode
    n371[reference]
    n369 --> n371
    class n371 leafNode
    n372[reference_type]
    n369 --> n372
    class n372 leafNode
    n373[envelope_type]
    n369 --> n373
    class n373 leafNode
    n374[squareness_upper_inner]
    n296 --> n374
    class n374 normalNode
    n375[reference_name]
    n374 --> n375
    class n375 leafNode
    n376[reference]
    n374 --> n376
    class n376 leafNode
    n377[reference_type]
    n374 --> n377
    class n377 leafNode
    n378[envelope_type]
    n374 --> n378
    class n378 leafNode
    n379[squareness_lower_outer]
    n296 --> n379
    class n379 normalNode
    n380[reference_name]
    n379 --> n380
    class n380 leafNode
    n381[reference]
    n379 --> n381
    class n381 leafNode
    n382[reference_type]
    n379 --> n382
    class n382 leafNode
    n383[envelope_type]
    n379 --> n383
    class n383 leafNode
    n384[squareness_lower_inner]
    n296 --> n384
    class n384 normalNode
    n385[reference_name]
    n384 --> n385
    class n385 leafNode
    n386[reference]
    n384 --> n386
    class n386 leafNode
    n387[reference_type]
    n384 --> n387
    class n387 leafNode
    n388[envelope_type]
    n384 --> n388
    class n388 leafNode
    n389[x_point]
    n296 --> n389
    class n389 normalNode
    n390[r]
    n389 --> n390
    class n390 normalNode
    n391[reference_name]
    n390 --> n391
    class n391 leafNode
    n392[reference]
    n390 --> n392
    class n392 leafNode
    n393[reference_type]
    n390 --> n393
    class n393 leafNode
    n394[envelope_type]
    n390 --> n394
    class n394 leafNode
    n395[z]
    n389 --> n395
    class n395 normalNode
    n396[reference_name]
    n395 --> n396
    class n396 leafNode
    n397[reference]
    n395 --> n397
    class n397 leafNode
    n398[reference_type]
    n395 --> n398
    class n398 leafNode
    n399[envelope_type]
    n395 --> n399
    class n399 leafNode
    n400[strike_point]
    n296 --> n400
    class n400 normalNode
    n401[r]
    n400 --> n401
    class n401 normalNode
    n402[reference_name]
    n401 --> n402
    class n402 leafNode
    n403[reference]
    n401 --> n403
    class n403 leafNode
    n404[reference_type]
    n401 --> n404
    class n404 leafNode
    n405[envelope_type]
    n401 --> n405
    class n405 leafNode
    n406[z]
    n400 --> n406
    class n406 normalNode
    n407[reference_name]
    n406 --> n407
    class n407 leafNode
    n408[reference]
    n406 --> n408
    class n408 leafNode
    n409[reference_type]
    n406 --> n409
    class n409 leafNode
    n410[envelope_type]
    n406 --> n410
    class n410 leafNode
    n411[active_limiter_point]
    n296 --> n411
    class n411 normalNode
    n412[r]
    n411 --> n412
    class n412 normalNode
    n413[reference_name]
    n412 --> n413
    class n413 leafNode
    n414[reference]
    n412 --> n414
    class n414 leafNode
    n415[reference_type]
    n412 --> n415
    class n415 leafNode
    n416[envelope_type]
    n412 --> n416
    class n416 leafNode
    n417[z]
    n411 --> n417
    class n417 normalNode
    n418[reference_name]
    n417 --> n418
    class n418 leafNode
    n419[reference]
    n417 --> n419
    class n419 leafNode
    n420[reference_type]
    n417 --> n420
    class n420 leafNode
    n421[envelope_type]
    n417 --> n421
    class n421 leafNode
    n422[boundary_outline]
    n296 --> n422
    class n422 normalNode
    n423[r]
    n422 --> n423
    class n423 normalNode
    n424[reference_name]
    n423 --> n424
    class n424 leafNode
    n425[reference]
    n423 --> n425
    class n425 leafNode
    n426[reference_type]
    n423 --> n426
    class n426 leafNode
    n427[envelope_type]
    n423 --> n427
    class n427 leafNode
    n428[z]
    n422 --> n428
    class n428 normalNode
    n429[reference_name]
    n428 --> n429
    class n429 leafNode
    n430[reference]
    n428 --> n430
    class n430 leafNode
    n431[reference_type]
    n428 --> n431
    class n431 leafNode
    n432[envelope_type]
    n428 --> n432
    class n432 leafNode
    n433[z_r_max]
    n296 --> n433
    class n433 normalNode
    n434[reference_name]
    n433 --> n434
    class n434 leafNode
    n435[reference]
    n433 --> n435
    class n435 leafNode
    n436[reference_type]
    n433 --> n436
    class n436 leafNode
    n437[envelope_type]
    n433 --> n437
    class n437 leafNode
    n438[z_r_min]
    n296 --> n438
    class n438 normalNode
    n439[reference_name]
    n438 --> n439
    class n439 leafNode
    n440[reference]
    n438 --> n440
    class n440 leafNode
    n441[reference_type]
    n438 --> n441
    class n441 leafNode
    n442[envelope_type]
    n438 --> n442
    class n442 leafNode
    n443(gap)
    n296 --> n443
    class n443 complexNode
    n444[name]
    n443 --> n444
    class n444 leafNode
    n445[description]
    n443 --> n445
    class n445 leafNode
    n446[r]
    n443 --> n446
    class n446 leafNode
    n447[z]
    n443 --> n447
    class n447 leafNode
    n448[angle]
    n443 --> n448
    class n448 leafNode
    n449[value]
    n443 --> n449
    class n449 normalNode
    n450[reference_name]
    n449 --> n450
    class n450 leafNode
    n451[reference]
    n449 --> n451
    class n451 leafNode
    n452[reference_type]
    n449 --> n452
    class n452 leafNode
    n453[envelope_type]
    n449 --> n453
    class n453 leafNode
    n454[current_centroid]
    n296 --> n454
    class n454 normalNode
    n455[r]
    n454 --> n455
    class n455 normalNode
    n456[reference_name]
    n455 --> n456
    class n456 leafNode
    n457[reference]
    n455 --> n457
    class n457 leafNode
    n458[reference_type]
    n455 --> n458
    class n458 leafNode
    n459[envelope_type]
    n455 --> n459
    class n459 leafNode
    n460[z]
    n454 --> n460
    class n460 normalNode
    n461[reference_name]
    n460 --> n461
    class n461 leafNode
    n462[reference]
    n460 --> n462
    class n462 leafNode
    n463[reference_type]
    n460 --> n463
    class n463 leafNode
    n464[envelope_type]
    n460 --> n464
    class n464 leafNode
    n465[mode]
    n296 --> n465
    class n465 leafNode
    n466[time]
    n296 --> n466
    class n466 leafNode
    n467[tf]
    n1 --> n467
    class n467 normalNode
    n468[b_field_tor_vacuum_r]
    n467 --> n468
    class n468 normalNode
    n469[reference_name]
    n468 --> n469
    class n469 leafNode
    n470[reference]
    n468 --> n470
    class n470 leafNode
    n471[reference_type]
    n468 --> n471
    class n471 leafNode
    n472[envelope_type]
    n468 --> n472
    class n472 leafNode
    n473[mode]
    n467 --> n473
    class n473 leafNode
    n474[time]
    n467 --> n474
    class n474 leafNode
    n475[time]
    n1 --> n475
    class n475 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```