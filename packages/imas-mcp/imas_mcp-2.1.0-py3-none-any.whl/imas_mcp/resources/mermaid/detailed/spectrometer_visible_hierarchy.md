```mermaid
flowchart TD
    root["spectrometer_visible IDS"]

    n1[spectrometer_visible]
    root --> n1
    class n1 normalNode
    n2[detector_layout]
    n1 --> n2
    class n2 leafNode
    n3(channel)
    n1 --> n3
    class n3 complexNode
    n4[name]
    n3 --> n4
    class n4 leafNode
    n5[object_observed]
    n3 --> n5
    class n5 leafNode
    n6[type]
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
    n10(detector)
    n3 --> n10
    class n10 complexNode
    n11[geometry_type]
    n10 --> n11
    class n11 leafNode
    n12[centre]
    n10 --> n12
    class n12 normalNode
    n13[r]
    n12 --> n13
    class n13 leafNode
    n14[phi]
    n12 --> n14
    class n14 leafNode
    n15[z]
    n12 --> n15
    class n15 leafNode
    n16[radius]
    n10 --> n16
    class n16 leafNode
    n17[x1_unit_vector]
    n10 --> n17
    class n17 normalNode
    n18[x]
    n17 --> n18
    class n18 leafNode
    n19[y]
    n17 --> n19
    class n19 leafNode
    n20[z]
    n17 --> n20
    class n20 leafNode
    n21[x2_unit_vector]
    n10 --> n21
    class n21 normalNode
    n22[x]
    n21 --> n22
    class n22 leafNode
    n23[y]
    n21 --> n23
    class n23 leafNode
    n24[z]
    n21 --> n24
    class n24 leafNode
    n25[x3_unit_vector]
    n10 --> n25
    class n25 normalNode
    n26[x]
    n25 --> n26
    class n26 leafNode
    n27[y]
    n25 --> n27
    class n27 leafNode
    n28[z]
    n25 --> n28
    class n28 leafNode
    n29[x1_width]
    n10 --> n29
    class n29 leafNode
    n30[x2_width]
    n10 --> n30
    class n30 leafNode
    n31[outline]
    n10 --> n31
    class n31 normalNode
    n32[x1]
    n31 --> n32
    class n32 leafNode
    n33[x2]
    n31 --> n33
    class n33 leafNode
    n34[surface]
    n10 --> n34
    class n34 leafNode
    n35(aperture)
    n3 --> n35
    class n35 complexNode
    n36[geometry_type]
    n35 --> n36
    class n36 leafNode
    n37[centre]
    n35 --> n37
    class n37 normalNode
    n38[r]
    n37 --> n38
    class n38 leafNode
    n39[phi]
    n37 --> n39
    class n39 leafNode
    n40[z]
    n37 --> n40
    class n40 leafNode
    n41[radius]
    n35 --> n41
    class n41 leafNode
    n42[x1_unit_vector]
    n35 --> n42
    class n42 normalNode
    n43[x]
    n42 --> n43
    class n43 leafNode
    n44[y]
    n42 --> n44
    class n44 leafNode
    n45[z]
    n42 --> n45
    class n45 leafNode
    n46[x2_unit_vector]
    n35 --> n46
    class n46 normalNode
    n47[x]
    n46 --> n47
    class n47 leafNode
    n48[y]
    n46 --> n48
    class n48 leafNode
    n49[z]
    n46 --> n49
    class n49 leafNode
    n50[x3_unit_vector]
    n35 --> n50
    class n50 normalNode
    n51[x]
    n50 --> n51
    class n51 leafNode
    n52[y]
    n50 --> n52
    class n52 leafNode
    n53[z]
    n50 --> n53
    class n53 leafNode
    n54[x1_width]
    n35 --> n54
    class n54 leafNode
    n55[x2_width]
    n35 --> n55
    class n55 leafNode
    n56[outline]
    n35 --> n56
    class n56 normalNode
    n57[x1]
    n56 --> n57
    class n57 leafNode
    n58[x2]
    n56 --> n58
    class n58 leafNode
    n59[surface]
    n35 --> n59
    class n59 leafNode
    n60[etendue]
    n3 --> n60
    class n60 leafNode
    n61[etendue_method]
    n3 --> n61
    class n61 normalNode
    n62[name]
    n61 --> n62
    class n62 leafNode
    n63[index]
    n61 --> n63
    class n63 leafNode
    n64[description]
    n61 --> n64
    class n64 leafNode
    n65[line_of_sight]
    n3 --> n65
    class n65 normalNode
    n66[first_point]
    n65 --> n66
    class n66 normalNode
    n67[r]
    n66 --> n67
    class n67 leafNode
    n68[phi]
    n66 --> n68
    class n68 leafNode
    n69[z]
    n66 --> n69
    class n69 leafNode
    n70[second_point]
    n65 --> n70
    class n70 normalNode
    n71[r]
    n70 --> n71
    class n71 leafNode
    n72[phi]
    n70 --> n72
    class n72 leafNode
    n73[z]
    n70 --> n73
    class n73 leafNode
    n74[detector_image]
    n3 --> n74
    class n74 normalNode
    n75[geometry_type]
    n74 --> n75
    class n75 leafNode
    n76[outline]
    n74 --> n76
    class n76 normalNode
    n77[r]
    n76 --> n77
    class n77 leafNode
    n78[phi]
    n76 --> n78
    class n78 leafNode
    n79[z]
    n76 --> n79
    class n79 leafNode
    n80[circular]
    n74 --> n80
    class n80 normalNode
    n81[radius]
    n80 --> n81
    class n81 leafNode
    n82[ellipticity]
    n80 --> n82
    class n82 leafNode
    n83[fibre_image]
    n3 --> n83
    class n83 normalNode
    n84[geometry_type]
    n83 --> n84
    class n84 leafNode
    n85[outline]
    n83 --> n85
    class n85 normalNode
    n86[r]
    n85 --> n86
    class n86 leafNode
    n87[phi]
    n85 --> n87
    class n87 leafNode
    n88[z]
    n85 --> n88
    class n88 leafNode
    n89[circular]
    n83 --> n89
    class n89 normalNode
    n90[radius]
    n89 --> n90
    class n90 leafNode
    n91[ellipticity]
    n89 --> n91
    class n91 leafNode
    n92[light_collection_efficiencies]
    n3 --> n92
    class n92 normalNode
    n93[values]
    n92 --> n93
    class n93 leafNode
    n94[positions]
    n92 --> n94
    class n94 normalNode
    n95[r]
    n94 --> n95
    class n95 leafNode
    n96[phi]
    n94 --> n96
    class n96 leafNode
    n97[z]
    n94 --> n97
    class n97 leafNode
    n98[active_spatial_resolution]
    n3 --> n98
    class n98 normalNode
    n99[centre]
    n98 --> n99
    class n99 normalNode
    n100[r]
    n99 --> n100
    class n100 leafNode
    n101[phi]
    n99 --> n101
    class n101 leafNode
    n102[z]
    n99 --> n102
    class n102 leafNode
    n103[width]
    n98 --> n103
    class n103 normalNode
    n104[r]
    n103 --> n104
    class n104 leafNode
    n105[phi]
    n103 --> n105
    class n105 leafNode
    n106[z]
    n103 --> n106
    class n106 leafNode
    n107[time]
    n98 --> n107
    class n107 leafNode
    n108(polarizer)
    n3 --> n108
    class n108 complexNode
    n109[geometry_type]
    n108 --> n109
    class n109 leafNode
    n110[centre]
    n108 --> n110
    class n110 normalNode
    n111[r]
    n110 --> n111
    class n111 leafNode
    n112[phi]
    n110 --> n112
    class n112 leafNode
    n113[z]
    n110 --> n113
    class n113 leafNode
    n114[radius]
    n108 --> n114
    class n114 leafNode
    n115[x1_unit_vector]
    n108 --> n115
    class n115 normalNode
    n116[x]
    n115 --> n116
    class n116 leafNode
    n117[y]
    n115 --> n117
    class n117 leafNode
    n118[z]
    n115 --> n118
    class n118 leafNode
    n119[x2_unit_vector]
    n108 --> n119
    class n119 normalNode
    n120[x]
    n119 --> n120
    class n120 leafNode
    n121[y]
    n119 --> n121
    class n121 leafNode
    n122[z]
    n119 --> n122
    class n122 leafNode
    n123[x3_unit_vector]
    n108 --> n123
    class n123 normalNode
    n124[x]
    n123 --> n124
    class n124 leafNode
    n125[y]
    n123 --> n125
    class n125 leafNode
    n126[z]
    n123 --> n126
    class n126 leafNode
    n127[x1_width]
    n108 --> n127
    class n127 leafNode
    n128[x2_width]
    n108 --> n128
    class n128 leafNode
    n129[outline]
    n108 --> n129
    class n129 normalNode
    n130[x1]
    n129 --> n130
    class n130 leafNode
    n131[x2]
    n129 --> n131
    class n131 leafNode
    n132[surface]
    n108 --> n132
    class n132 leafNode
    n133[polarizer_active]
    n3 --> n133
    class n133 leafNode
    n134(grating_spectrometer)
    n3 --> n134
    class n134 complexNode
    n135[grating]
    n134 --> n135
    class n135 leafNode
    n136[slit_width]
    n134 --> n136
    class n136 leafNode
    n137[wavelengths]
    n134 --> n137
    class n137 leafNode
    n138[radiance_spectral]
    n134 --> n138
    class n138 normalNode
    n139[data]
    n138 --> n139
    class n139 leafNode
    n140[time]
    n138 --> n140
    class n140 leafNode
    n141[intensity_spectrum]
    n134 --> n141
    class n141 normalNode
    n142[data]
    n141 --> n142
    class n142 leafNode
    n143[time]
    n141 --> n143
    class n143 leafNode
    n144[exposure_time]
    n134 --> n144
    class n144 leafNode
    n145[processed_line]
    n134 --> n145
    class n145 normalNode
    n146[name]
    n145 --> n146
    class n146 leafNode
    n147[wavelength_central]
    n145 --> n147
    class n147 leafNode
    n148[radiance]
    n145 --> n148
    class n148 normalNode
    n149[data]
    n148 --> n149
    class n149 leafNode
    n150[time]
    n148 --> n150
    class n150 leafNode
    n151[intensity]
    n145 --> n151
    class n151 normalNode
    n152[data]
    n151 --> n152
    class n152 leafNode
    n153[time]
    n151 --> n153
    class n153 leafNode
    n154[radiance_calibration]
    n134 --> n154
    class n154 leafNode
    n155[radiance_calibration_date]
    n134 --> n155
    class n155 leafNode
    n156[wavelength_calibration]
    n134 --> n156
    class n156 normalNode
    n157[offset]
    n156 --> n157
    class n157 leafNode
    n158[gain]
    n156 --> n158
    class n158 leafNode
    n159[wavelength_calibration_date]
    n134 --> n159
    class n159 leafNode
    n160[instrument_function]
    n134 --> n160
    class n160 leafNode
    n161(filter_spectrometer)
    n3 --> n161
    class n161 complexNode
    n162[filter]
    n161 --> n162
    class n162 normalNode
    n163[wavelength_central]
    n162 --> n163
    class n163 leafNode
    n164[wavelength_width]
    n162 --> n164
    class n164 leafNode
    n165[processed_line]
    n161 --> n165
    class n165 normalNode
    n166[name]
    n165 --> n166
    class n166 leafNode
    n167[wavelength_central]
    n165 --> n167
    class n167 leafNode
    n168[output_voltage]
    n161 --> n168
    class n168 normalNode
    n169[data]
    n168 --> n169
    class n169 leafNode
    n170[time]
    n168 --> n170
    class n170 leafNode
    n171[photoelectric_voltage]
    n161 --> n171
    class n171 normalNode
    n172[data]
    n171 --> n172
    class n172 leafNode
    n173[time]
    n171 --> n173
    class n173 leafNode
    n174[photon_count]
    n161 --> n174
    class n174 normalNode
    n175[data]
    n174 --> n175
    class n175 leafNode
    n176[time]
    n174 --> n176
    class n176 leafNode
    n177[exposure_time]
    n161 --> n177
    class n177 leafNode
    n178[wavelengths]
    n161 --> n178
    class n178 leafNode
    n179[radiance_calibration]
    n161 --> n179
    class n179 leafNode
    n180[radiance_calibration_date]
    n161 --> n180
    class n180 leafNode
    n181[sensitivity]
    n161 --> n181
    class n181 leafNode
    n182[validity_timed]
    n3 --> n182
    class n182 normalNode
    n183[data]
    n182 --> n183
    class n183 leafNode
    n184[time]
    n182 --> n184
    class n184 leafNode
    n185[validity]
    n3 --> n185
    class n185 leafNode
    n186(isotope_ratios)
    n3 --> n186
    class n186 complexNode
    n187[validity_timed]
    n186 --> n187
    class n187 leafNode
    n188[validity]
    n186 --> n188
    class n188 leafNode
    n189[signal_to_noise]
    n186 --> n189
    class n189 leafNode
    n190[method]
    n186 --> n190
    class n190 normalNode
    n191[name]
    n190 --> n191
    class n191 leafNode
    n192[index]
    n190 --> n192
    class n192 leafNode
    n193[description]
    n190 --> n193
    class n193 leafNode
    n194(isotope)
    n186 --> n194
    class n194 complexNode
    n195[element]
    n194 --> n195
    class n195 normalNode
    n196[a]
    n195 --> n196
    class n196 leafNode
    n197[z_n]
    n195 --> n197
    class n197 leafNode
    n198[atoms_n]
    n195 --> n198
    class n198 leafNode
    n199[name]
    n194 --> n199
    class n199 leafNode
    n200[density_ratio]
    n194 --> n200
    class n200 leafNode
    n201[cold_neutrals_fraction]
    n194 --> n201
    class n201 leafNode
    n202[hot_neutrals_fraction]
    n194 --> n202
    class n202 leafNode
    n203[cold_neutrals_temperature]
    n194 --> n203
    class n203 leafNode
    n204[hot_neutrals_temperature]
    n194 --> n204
    class n204 leafNode
    n205[time]
    n194 --> n205
    class n205 leafNode
    n206[time]
    n186 --> n206
    class n206 leafNode
    n207(polarization_spectroscopy)
    n3 --> n207
    class n207 complexNode
    n208[e_field_lh_r]
    n207 --> n208
    class n208 leafNode
    n209[e_field_lh_z]
    n207 --> n209
    class n209 leafNode
    n210[e_field_lh_phi]
    n207 --> n210
    class n210 leafNode
    n211[b_field_modulus]
    n207 --> n211
    class n211 leafNode
    n212[n_e]
    n207 --> n212
    class n212 leafNode
    n213[temperature_cold_neutrals]
    n207 --> n213
    class n213 leafNode
    n214[temperature_hot_neutrals]
    n207 --> n214
    class n214 leafNode
    n215[velocity_cold_neutrals]
    n207 --> n215
    class n215 leafNode
    n216[velocity_hot_neutrals]
    n207 --> n216
    class n216 leafNode
    n217[time]
    n207 --> n217
    class n217 leafNode
    n218(geometry_matrix)
    n3 --> n218
    class n218 complexNode
    n219[with_reflections]
    n218 --> n219
    class n219 normalNode
    n220[data]
    n219 --> n220
    class n220 leafNode
    n221[voxel_indices]
    n219 --> n221
    class n221 leafNode
    n222[without_reflections]
    n218 --> n222
    class n222 normalNode
    n223[data]
    n222 --> n223
    class n223 leafNode
    n224[voxel_indices]
    n222 --> n224
    class n224 leafNode
    n225[interpolated]
    n218 --> n225
    class n225 normalNode
    n226[r]
    n225 --> n226
    class n226 leafNode
    n227[z]
    n225 --> n227
    class n227 leafNode
    n228[phi]
    n225 --> n228
    class n228 leafNode
    n229[data]
    n225 --> n229
    class n229 leafNode
    n230[voxel_map]
    n218 --> n230
    class n230 leafNode
    n231[voxels_n]
    n218 --> n231
    class n231 leafNode
    n232[emission_grid]
    n218 --> n232
    class n232 normalNode
    n233[grid_type]
    n232 --> n233
    class n233 normalNode
    n234[name]
    n233 --> n234
    class n234 leafNode
    n235[index]
    n233 --> n235
    class n235 leafNode
    n236[description]
    n233 --> n236
    class n236 leafNode
    n237[dim1]
    n232 --> n237
    class n237 leafNode
    n238[dim2]
    n232 --> n238
    class n238 leafNode
    n239[dim3]
    n232 --> n239
    class n239 leafNode
    n240(optical_element)
    n3 --> n240
    class n240 complexNode
    n241[type]
    n240 --> n241
    class n241 normalNode
    n242[name]
    n241 --> n242
    class n242 leafNode
    n243[index]
    n241 --> n243
    class n243 leafNode
    n244[description]
    n241 --> n244
    class n244 leafNode
    n245[front_surface]
    n240 --> n245
    class n245 normalNode
    n246[curvature_type]
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
    n250[x1_curvature]
    n245 --> n250
    class n250 leafNode
    n251[x2_curvature]
    n245 --> n251
    class n251 leafNode
    n252[back_surface]
    n240 --> n252
    class n252 normalNode
    n253[curvature_type]
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
    n257[x1_curvature]
    n252 --> n257
    class n257 leafNode
    n258[x2_curvature]
    n252 --> n258
    class n258 leafNode
    n259[thickness]
    n240 --> n259
    class n259 leafNode
    n260(material_properties)
    n240 --> n260
    class n260 complexNode
    n261[type]
    n260 --> n261
    class n261 normalNode
    n262[name]
    n261 --> n262
    class n262 leafNode
    n263[index]
    n261 --> n263
    class n263 leafNode
    n264[description]
    n261 --> n264
    class n264 leafNode
    n265[wavelengths]
    n260 --> n265
    class n265 leafNode
    n266[refractive_index]
    n260 --> n266
    class n266 leafNode
    n267[extinction_coefficient]
    n260 --> n267
    class n267 leafNode
    n268[transmission_coefficient]
    n260 --> n268
    class n268 leafNode
    n269[roughness]
    n260 --> n269
    class n269 leafNode
    n270(geometry)
    n240 --> n270
    class n270 complexNode
    n271[geometry_type]
    n270 --> n271
    class n271 leafNode
    n272[centre]
    n270 --> n272
    class n272 normalNode
    n273[r]
    n272 --> n273
    class n273 leafNode
    n274[phi]
    n272 --> n274
    class n274 leafNode
    n275[z]
    n272 --> n275
    class n275 leafNode
    n276[radius]
    n270 --> n276
    class n276 leafNode
    n277[x1_unit_vector]
    n270 --> n277
    class n277 normalNode
    n278[x]
    n277 --> n278
    class n278 leafNode
    n279[y]
    n277 --> n279
    class n279 leafNode
    n280[z]
    n277 --> n280
    class n280 leafNode
    n281[x2_unit_vector]
    n270 --> n281
    class n281 normalNode
    n282[x]
    n281 --> n282
    class n282 leafNode
    n283[y]
    n281 --> n283
    class n283 leafNode
    n284[z]
    n281 --> n284
    class n284 leafNode
    n285[x3_unit_vector]
    n270 --> n285
    class n285 normalNode
    n286[x]
    n285 --> n286
    class n286 leafNode
    n287[y]
    n285 --> n287
    class n287 leafNode
    n288[z]
    n285 --> n288
    class n288 leafNode
    n289[x1_width]
    n270 --> n289
    class n289 leafNode
    n290[x2_width]
    n270 --> n290
    class n290 leafNode
    n291[outline]
    n270 --> n291
    class n291 normalNode
    n292[x1]
    n291 --> n292
    class n292 leafNode
    n293[x2]
    n291 --> n293
    class n293 leafNode
    n294[surface]
    n270 --> n294
    class n294 leafNode
    n295[fibre_bundle]
    n3 --> n295
    class n295 normalNode
    n296(geometry)
    n295 --> n296
    class n296 complexNode
    n297[geometry_type]
    n296 --> n297
    class n297 leafNode
    n298[centre]
    n296 --> n298
    class n298 normalNode
    n299[r]
    n298 --> n299
    class n299 leafNode
    n300[phi]
    n298 --> n300
    class n300 leafNode
    n301[z]
    n298 --> n301
    class n301 leafNode
    n302[radius]
    n296 --> n302
    class n302 leafNode
    n303[x1_unit_vector]
    n296 --> n303
    class n303 normalNode
    n304[x]
    n303 --> n304
    class n304 leafNode
    n305[y]
    n303 --> n305
    class n305 leafNode
    n306[z]
    n303 --> n306
    class n306 leafNode
    n307[x2_unit_vector]
    n296 --> n307
    class n307 normalNode
    n308[x]
    n307 --> n308
    class n308 leafNode
    n309[y]
    n307 --> n309
    class n309 leafNode
    n310[z]
    n307 --> n310
    class n310 leafNode
    n311[x3_unit_vector]
    n296 --> n311
    class n311 normalNode
    n312[x]
    n311 --> n312
    class n312 leafNode
    n313[y]
    n311 --> n313
    class n313 leafNode
    n314[z]
    n311 --> n314
    class n314 leafNode
    n315[x1_width]
    n296 --> n315
    class n315 leafNode
    n316[x2_width]
    n296 --> n316
    class n316 leafNode
    n317[outline]
    n296 --> n317
    class n317 normalNode
    n318[x1]
    n317 --> n318
    class n318 leafNode
    n319[x2]
    n317 --> n319
    class n319 leafNode
    n320[surface]
    n296 --> n320
    class n320 leafNode
    n321[fibre_radius]
    n295 --> n321
    class n321 leafNode
    n322[fibre_positions]
    n295 --> n322
    class n322 normalNode
    n323[x1]
    n322 --> n323
    class n323 leafNode
    n324[x2]
    n322 --> n324
    class n324 leafNode
    n325[latency]
    n1 --> n325
    class n325 leafNode
    n326[time]
    n1 --> n326
    class n326 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```