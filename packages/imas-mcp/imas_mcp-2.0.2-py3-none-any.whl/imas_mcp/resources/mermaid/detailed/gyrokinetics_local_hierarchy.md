```mermaid
flowchart TD
    root["gyrokinetics_local IDS"]

    n1(gyrokinetics_local)
    root --> n1
    class n1 complexNode
    n2[normalizing_quantities]
    n1 --> n2
    class n2 normalNode
    n3[t_e]
    n2 --> n3
    class n3 leafNode
    n4[n_e]
    n2 --> n4
    class n4 leafNode
    n5[r]
    n2 --> n5
    class n5 leafNode
    n6[b_field_phi]
    n2 --> n6
    class n6 leafNode
    n7(flux_surface)
    n1 --> n7
    class n7 complexNode
    n8[r_minor_norm]
    n7 --> n8
    class n8 leafNode
    n9[elongation]
    n7 --> n9
    class n9 leafNode
    n10[delongation_dr_minor_norm]
    n7 --> n10
    class n10 leafNode
    n11[dgeometric_axis_r_dr_minor]
    n7 --> n11
    class n11 leafNode
    n12[dgeometric_axis_z_dr_minor]
    n7 --> n12
    class n12 leafNode
    n13[q]
    n7 --> n13
    class n13 leafNode
    n14[magnetic_shear_r_minor]
    n7 --> n14
    class n14 leafNode
    n15[pressure_gradient_norm]
    n7 --> n15
    class n15 leafNode
    n16[ip_sign]
    n7 --> n16
    class n16 leafNode
    n17[b_field_phi_sign]
    n7 --> n17
    class n17 leafNode
    n18[shape_coefficients_c]
    n7 --> n18
    class n18 leafNode
    n19[dc_dr_minor_norm]
    n7 --> n19
    class n19 leafNode
    n20[shape_coefficients_s]
    n7 --> n20
    class n20 leafNode
    n21[ds_dr_minor_norm]
    n7 --> n21
    class n21 leafNode
    n22[linear]
    n1 --> n22
    class n22 normalNode
    n23[wavevector]
    n22 --> n23
    class n23 normalNode
    n24[radial_wavevector_norm]
    n23 --> n24
    class n24 leafNode
    n25[binormal_wavevector_norm]
    n23 --> n25
    class n25 leafNode
    n26(eigenmode)
    n23 --> n26
    class n26 complexNode
    n27[poloidal_turns]
    n26 --> n27
    class n27 leafNode
    n28[growth_rate_norm]
    n26 --> n28
    class n28 leafNode
    n29[frequency_norm]
    n26 --> n29
    class n29 leafNode
    n30[growth_rate_tolerance]
    n26 --> n30
    class n30 leafNode
    n31[angle_pol]
    n26 --> n31
    class n31 leafNode
    n32[time_norm]
    n26 --> n32
    class n32 leafNode
    n33(fields)
    n26 --> n33
    class n33 complexNode
    n34[phi_potential_perturbed_weight]
    n33 --> n34
    class n34 leafNode
    n35[phi_potential_perturbed_parity]
    n33 --> n35
    class n35 leafNode
    n36[a_field_parallel_perturbed_weight]
    n33 --> n36
    class n36 leafNode
    n37[a_field_parallel_perturbed_parity]
    n33 --> n37
    class n37 leafNode
    n38[b_field_parallel_perturbed_weight]
    n33 --> n38
    class n38 leafNode
    n39[b_field_parallel_perturbed_parity]
    n33 --> n39
    class n39 leafNode
    n40[phi_potential_perturbed_norm]
    n33 --> n40
    class n40 leafNode
    n41[a_field_parallel_perturbed_norm]
    n33 --> n41
    class n41 leafNode
    n42[b_field_parallel_perturbed_norm]
    n33 --> n42
    class n42 leafNode
    n43[initial_value_run]
    n26 --> n43
    class n43 leafNode
    n44(moments_norm_gyrocenter)
    n26 --> n44
    class n44 complexNode
    n45[density]
    n44 --> n45
    class n45 leafNode
    n46[j_parallel]
    n44 --> n46
    class n46 leafNode
    n47[pressure_parallel]
    n44 --> n47
    class n47 leafNode
    n48[pressure_perpendicular]
    n44 --> n48
    class n48 leafNode
    n49[pressure]
    n44 --> n49
    class n49 leafNode
    n50[heat_flux_parallel]
    n44 --> n50
    class n50 leafNode
    n51[v_parallel_energy_perpendicular]
    n44 --> n51
    class n51 leafNode
    n52[v_perpendicular_square_energy]
    n44 --> n52
    class n52 leafNode
    n53(moments_norm_particle)
    n26 --> n53
    class n53 complexNode
    n54[density]
    n53 --> n54
    class n54 leafNode
    n55[j_parallel]
    n53 --> n55
    class n55 leafNode
    n56[pressure_parallel]
    n53 --> n56
    class n56 leafNode
    n57[pressure_perpendicular]
    n53 --> n57
    class n57 leafNode
    n58[pressure]
    n53 --> n58
    class n58 leafNode
    n59[heat_flux_parallel]
    n53 --> n59
    class n59 leafNode
    n60[v_parallel_energy_perpendicular]
    n53 --> n60
    class n60 leafNode
    n61[v_perpendicular_square_energy]
    n53 --> n61
    class n61 leafNode
    n62(moments_norm_gyrocenter_bessel_0)
    n26 --> n62
    class n62 complexNode
    n63[density]
    n62 --> n63
    class n63 leafNode
    n64[j_parallel]
    n62 --> n64
    class n64 leafNode
    n65[pressure_parallel]
    n62 --> n65
    class n65 leafNode
    n66[pressure_perpendicular]
    n62 --> n66
    class n66 leafNode
    n67[pressure]
    n62 --> n67
    class n67 leafNode
    n68[heat_flux_parallel]
    n62 --> n68
    class n68 leafNode
    n69[v_parallel_energy_perpendicular]
    n62 --> n69
    class n69 leafNode
    n70[v_perpendicular_square_energy]
    n62 --> n70
    class n70 leafNode
    n71(moments_norm_gyrocenter_bessel_1)
    n26 --> n71
    class n71 complexNode
    n72[density]
    n71 --> n72
    class n72 leafNode
    n73[j_parallel]
    n71 --> n73
    class n73 leafNode
    n74[pressure_parallel]
    n71 --> n74
    class n74 leafNode
    n75[pressure_perpendicular]
    n71 --> n75
    class n75 leafNode
    n76[pressure]
    n71 --> n76
    class n76 leafNode
    n77[heat_flux_parallel]
    n71 --> n77
    class n77 leafNode
    n78[v_parallel_energy_perpendicular]
    n71 --> n78
    class n78 leafNode
    n79[v_perpendicular_square_energy]
    n71 --> n79
    class n79 leafNode
    n80(linear_weights)
    n26 --> n80
    class n80 complexNode
    n81[particles_phi_potential]
    n80 --> n81
    class n81 leafNode
    n82[particles_a_field_parallel]
    n80 --> n82
    class n82 leafNode
    n83[particles_b_field_parallel]
    n80 --> n83
    class n83 leafNode
    n84[energy_phi_potential]
    n80 --> n84
    class n84 leafNode
    n85[energy_a_field_parallel]
    n80 --> n85
    class n85 leafNode
    n86[energy_b_field_parallel]
    n80 --> n86
    class n86 leafNode
    n87[momentum_phi_parallel_phi_potential]
    n80 --> n87
    class n87 leafNode
    n88[momentum_phi_parallel_a_field_parallel]
    n80 --> n88
    class n88 leafNode
    n89[momentum_phi_parallel_b_field_parallel]
    n80 --> n89
    class n89 leafNode
    n90[momentum_phi_perpendicular_phi_potential]
    n80 --> n90
    class n90 leafNode
    n91[momentum_phi_perpendicular_a_field_parallel]
    n80 --> n91
    class n91 leafNode
    n92[momentum_phi_perpendicular_b_field_parallel]
    n80 --> n92
    class n92 leafNode
    n93(linear_weights_rotating_frame)
    n26 --> n93
    class n93 complexNode
    n94[particles_phi_potential]
    n93 --> n94
    class n94 leafNode
    n95[particles_a_field_parallel]
    n93 --> n95
    class n95 leafNode
    n96[particles_b_field_parallel]
    n93 --> n96
    class n96 leafNode
    n97[energy_phi_potential]
    n93 --> n97
    class n97 leafNode
    n98[energy_a_field_parallel]
    n93 --> n98
    class n98 leafNode
    n99[energy_b_field_parallel]
    n93 --> n99
    class n99 leafNode
    n100[momentum_phi_parallel_phi_potential]
    n93 --> n100
    class n100 leafNode
    n101[momentum_phi_parallel_a_field_parallel]
    n93 --> n101
    class n101 leafNode
    n102[momentum_phi_parallel_b_field_parallel]
    n93 --> n102
    class n102 leafNode
    n103[momentum_phi_perpendicular_phi_potential]
    n93 --> n103
    class n103 leafNode
    n104[momentum_phi_perpendicular_a_field_parallel]
    n93 --> n104
    class n104 leafNode
    n105[momentum_phi_perpendicular_b_field_parallel]
    n93 --> n105
    class n105 leafNode
    n106(non_linear)
    n1 --> n106
    class n106 complexNode
    n107[binormal_wavevector_norm]
    n106 --> n107
    class n107 leafNode
    n108[radial_wavevector_norm]
    n106 --> n108
    class n108 leafNode
    n109[angle_pol]
    n106 --> n109
    class n109 leafNode
    n110[time_norm]
    n106 --> n110
    class n110 leafNode
    n111[time_interval_norm]
    n106 --> n111
    class n111 leafNode
    n112[quasi_linear]
    n106 --> n112
    class n112 leafNode
    n113(fluxes_5d)
    n106 --> n113
    class n113 complexNode
    n114[particles_phi_potential]
    n113 --> n114
    class n114 leafNode
    n115[particles_a_field_parallel]
    n113 --> n115
    class n115 leafNode
    n116[particles_b_field_parallel]
    n113 --> n116
    class n116 leafNode
    n117[energy_phi_potential]
    n113 --> n117
    class n117 leafNode
    n118[energy_a_field_parallel]
    n113 --> n118
    class n118 leafNode
    n119[energy_b_field_parallel]
    n113 --> n119
    class n119 leafNode
    n120[momentum_phi_parallel_phi_potential]
    n113 --> n120
    class n120 leafNode
    n121[momentum_phi_parallel_a_field_parallel]
    n113 --> n121
    class n121 leafNode
    n122[momentum_phi_parallel_b_field_parallel]
    n113 --> n122
    class n122 leafNode
    n123[momentum_phi_perpendicular_phi_potential]
    n113 --> n123
    class n123 leafNode
    n124[momentum_phi_perpendicular_a_field_parallel]
    n113 --> n124
    class n124 leafNode
    n125[momentum_phi_perpendicular_b_field_parallel]
    n113 --> n125
    class n125 leafNode
    n126(fluxes_4d)
    n106 --> n126
    class n126 complexNode
    n127[particles_phi_potential]
    n126 --> n127
    class n127 leafNode
    n128[particles_a_field_parallel]
    n126 --> n128
    class n128 leafNode
    n129[particles_b_field_parallel]
    n126 --> n129
    class n129 leafNode
    n130[energy_phi_potential]
    n126 --> n130
    class n130 leafNode
    n131[energy_a_field_parallel]
    n126 --> n131
    class n131 leafNode
    n132[energy_b_field_parallel]
    n126 --> n132
    class n132 leafNode
    n133[momentum_phi_parallel_phi_potential]
    n126 --> n133
    class n133 leafNode
    n134[momentum_phi_parallel_a_field_parallel]
    n126 --> n134
    class n134 leafNode
    n135[momentum_phi_parallel_b_field_parallel]
    n126 --> n135
    class n135 leafNode
    n136[momentum_phi_perpendicular_phi_potential]
    n126 --> n136
    class n136 leafNode
    n137[momentum_phi_perpendicular_a_field_parallel]
    n126 --> n137
    class n137 leafNode
    n138[momentum_phi_perpendicular_b_field_parallel]
    n126 --> n138
    class n138 leafNode
    n139(fluxes_3d)
    n106 --> n139
    class n139 complexNode
    n140[particles_phi_potential]
    n139 --> n140
    class n140 leafNode
    n141[particles_a_field_parallel]
    n139 --> n141
    class n141 leafNode
    n142[particles_b_field_parallel]
    n139 --> n142
    class n142 leafNode
    n143[energy_phi_potential]
    n139 --> n143
    class n143 leafNode
    n144[energy_a_field_parallel]
    n139 --> n144
    class n144 leafNode
    n145[energy_b_field_parallel]
    n139 --> n145
    class n145 leafNode
    n146[momentum_phi_parallel_phi_potential]
    n139 --> n146
    class n146 leafNode
    n147[momentum_phi_parallel_a_field_parallel]
    n139 --> n147
    class n147 leafNode
    n148[momentum_phi_parallel_b_field_parallel]
    n139 --> n148
    class n148 leafNode
    n149[momentum_phi_perpendicular_phi_potential]
    n139 --> n149
    class n149 leafNode
    n150[momentum_phi_perpendicular_a_field_parallel]
    n139 --> n150
    class n150 leafNode
    n151[momentum_phi_perpendicular_b_field_parallel]
    n139 --> n151
    class n151 leafNode
    n152(fluxes_3d_k_x_sum)
    n106 --> n152
    class n152 complexNode
    n153[particles_phi_potential]
    n152 --> n153
    class n153 leafNode
    n154[particles_a_field_parallel]
    n152 --> n154
    class n154 leafNode
    n155[particles_b_field_parallel]
    n152 --> n155
    class n155 leafNode
    n156[energy_phi_potential]
    n152 --> n156
    class n156 leafNode
    n157[energy_a_field_parallel]
    n152 --> n157
    class n157 leafNode
    n158[energy_b_field_parallel]
    n152 --> n158
    class n158 leafNode
    n159[momentum_phi_parallel_phi_potential]
    n152 --> n159
    class n159 leafNode
    n160[momentum_phi_parallel_a_field_parallel]
    n152 --> n160
    class n160 leafNode
    n161[momentum_phi_parallel_b_field_parallel]
    n152 --> n161
    class n161 leafNode
    n162[momentum_phi_perpendicular_phi_potential]
    n152 --> n162
    class n162 leafNode
    n163[momentum_phi_perpendicular_a_field_parallel]
    n152 --> n163
    class n163 leafNode
    n164[momentum_phi_perpendicular_b_field_parallel]
    n152 --> n164
    class n164 leafNode
    n165(fluxes_2d_k_x_sum)
    n106 --> n165
    class n165 complexNode
    n166[particles_phi_potential]
    n165 --> n166
    class n166 leafNode
    n167[particles_a_field_parallel]
    n165 --> n167
    class n167 leafNode
    n168[particles_b_field_parallel]
    n165 --> n168
    class n168 leafNode
    n169[energy_phi_potential]
    n165 --> n169
    class n169 leafNode
    n170[energy_a_field_parallel]
    n165 --> n170
    class n170 leafNode
    n171[energy_b_field_parallel]
    n165 --> n171
    class n171 leafNode
    n172[momentum_phi_parallel_phi_potential]
    n165 --> n172
    class n172 leafNode
    n173[momentum_phi_parallel_a_field_parallel]
    n165 --> n173
    class n173 leafNode
    n174[momentum_phi_parallel_b_field_parallel]
    n165 --> n174
    class n174 leafNode
    n175[momentum_phi_perpendicular_phi_potential]
    n165 --> n175
    class n175 leafNode
    n176[momentum_phi_perpendicular_a_field_parallel]
    n165 --> n176
    class n176 leafNode
    n177[momentum_phi_perpendicular_b_field_parallel]
    n165 --> n177
    class n177 leafNode
    n178(fluxes_2d_k_x_k_y_sum)
    n106 --> n178
    class n178 complexNode
    n179[particles_phi_potential]
    n178 --> n179
    class n179 leafNode
    n180[particles_a_field_parallel]
    n178 --> n180
    class n180 leafNode
    n181[particles_b_field_parallel]
    n178 --> n181
    class n181 leafNode
    n182[energy_phi_potential]
    n178 --> n182
    class n182 leafNode
    n183[energy_a_field_parallel]
    n178 --> n183
    class n183 leafNode
    n184[energy_b_field_parallel]
    n178 --> n184
    class n184 leafNode
    n185[momentum_phi_parallel_phi_potential]
    n178 --> n185
    class n185 leafNode
    n186[momentum_phi_parallel_a_field_parallel]
    n178 --> n186
    class n186 leafNode
    n187[momentum_phi_parallel_b_field_parallel]
    n178 --> n187
    class n187 leafNode
    n188[momentum_phi_perpendicular_phi_potential]
    n178 --> n188
    class n188 leafNode
    n189[momentum_phi_perpendicular_a_field_parallel]
    n178 --> n189
    class n189 leafNode
    n190[momentum_phi_perpendicular_b_field_parallel]
    n178 --> n190
    class n190 leafNode
    n191(fluxes_1d)
    n106 --> n191
    class n191 complexNode
    n192[particles_phi_potential]
    n191 --> n192
    class n192 leafNode
    n193[particles_a_field_parallel]
    n191 --> n193
    class n193 leafNode
    n194[particles_b_field_parallel]
    n191 --> n194
    class n194 leafNode
    n195[energy_phi_potential]
    n191 --> n195
    class n195 leafNode
    n196[energy_a_field_parallel]
    n191 --> n196
    class n196 leafNode
    n197[energy_b_field_parallel]
    n191 --> n197
    class n197 leafNode
    n198[momentum_phi_parallel_phi_potential]
    n191 --> n198
    class n198 leafNode
    n199[momentum_phi_parallel_a_field_parallel]
    n191 --> n199
    class n199 leafNode
    n200[momentum_phi_parallel_b_field_parallel]
    n191 --> n200
    class n200 leafNode
    n201[momentum_phi_perpendicular_phi_potential]
    n191 --> n201
    class n201 leafNode
    n202[momentum_phi_perpendicular_a_field_parallel]
    n191 --> n202
    class n202 leafNode
    n203[momentum_phi_perpendicular_b_field_parallel]
    n191 --> n203
    class n203 leafNode
    n204[fields_4d]
    n106 --> n204
    class n204 normalNode
    n205[phi_potential_perturbed_norm]
    n204 --> n205
    class n205 leafNode
    n206[a_field_parallel_perturbed_norm]
    n204 --> n206
    class n206 leafNode
    n207[b_field_parallel_perturbed_norm]
    n204 --> n207
    class n207 leafNode
    n208[fields_intensity_3d]
    n106 --> n208
    class n208 normalNode
    n209[phi_potential_perturbed_norm]
    n208 --> n209
    class n209 leafNode
    n210[a_field_parallel_perturbed_norm]
    n208 --> n210
    class n210 leafNode
    n211[b_field_parallel_perturbed_norm]
    n208 --> n211
    class n211 leafNode
    n212[fields_intensity_2d_surface_average]
    n106 --> n212
    class n212 normalNode
    n213[phi_potential_perturbed_norm]
    n212 --> n213
    class n213 leafNode
    n214[a_field_parallel_perturbed_norm]
    n212 --> n214
    class n214 leafNode
    n215[b_field_parallel_perturbed_norm]
    n212 --> n215
    class n215 leafNode
    n216[fields_zonal_2d]
    n106 --> n216
    class n216 normalNode
    n217[phi_potential_perturbed_norm]
    n216 --> n217
    class n217 leafNode
    n218[a_field_parallel_perturbed_norm]
    n216 --> n218
    class n218 leafNode
    n219[b_field_parallel_perturbed_norm]
    n216 --> n219
    class n219 leafNode
    n220[fields_intensity_1d]
    n106 --> n220
    class n220 normalNode
    n221[phi_potential_perturbed_norm]
    n220 --> n221
    class n221 leafNode
    n222[a_field_parallel_perturbed_norm]
    n220 --> n222
    class n222 leafNode
    n223[b_field_parallel_perturbed_norm]
    n220 --> n223
    class n223 leafNode
    n224(fluxes_5d_rotating_frame)
    n106 --> n224
    class n224 complexNode
    n225[particles_phi_potential]
    n224 --> n225
    class n225 leafNode
    n226[particles_a_field_parallel]
    n224 --> n226
    class n226 leafNode
    n227[particles_b_field_parallel]
    n224 --> n227
    class n227 leafNode
    n228[energy_phi_potential]
    n224 --> n228
    class n228 leafNode
    n229[energy_a_field_parallel]
    n224 --> n229
    class n229 leafNode
    n230[energy_b_field_parallel]
    n224 --> n230
    class n230 leafNode
    n231[momentum_phi_parallel_phi_potential]
    n224 --> n231
    class n231 leafNode
    n232[momentum_phi_parallel_a_field_parallel]
    n224 --> n232
    class n232 leafNode
    n233[momentum_phi_parallel_b_field_parallel]
    n224 --> n233
    class n233 leafNode
    n234[momentum_phi_perpendicular_phi_potential]
    n224 --> n234
    class n234 leafNode
    n235[momentum_phi_perpendicular_a_field_parallel]
    n224 --> n235
    class n235 leafNode
    n236[momentum_phi_perpendicular_b_field_parallel]
    n224 --> n236
    class n236 leafNode
    n237(fluxes_4d_rotating_frame)
    n106 --> n237
    class n237 complexNode
    n238[particles_phi_potential]
    n237 --> n238
    class n238 leafNode
    n239[particles_a_field_parallel]
    n237 --> n239
    class n239 leafNode
    n240[particles_b_field_parallel]
    n237 --> n240
    class n240 leafNode
    n241[energy_phi_potential]
    n237 --> n241
    class n241 leafNode
    n242[energy_a_field_parallel]
    n237 --> n242
    class n242 leafNode
    n243[energy_b_field_parallel]
    n237 --> n243
    class n243 leafNode
    n244[momentum_phi_parallel_phi_potential]
    n237 --> n244
    class n244 leafNode
    n245[momentum_phi_parallel_a_field_parallel]
    n237 --> n245
    class n245 leafNode
    n246[momentum_phi_parallel_b_field_parallel]
    n237 --> n246
    class n246 leafNode
    n247[momentum_phi_perpendicular_phi_potential]
    n237 --> n247
    class n247 leafNode
    n248[momentum_phi_perpendicular_a_field_parallel]
    n237 --> n248
    class n248 leafNode
    n249[momentum_phi_perpendicular_b_field_parallel]
    n237 --> n249
    class n249 leafNode
    n250(fluxes_3d_rotating_frame)
    n106 --> n250
    class n250 complexNode
    n251[particles_phi_potential]
    n250 --> n251
    class n251 leafNode
    n252[particles_a_field_parallel]
    n250 --> n252
    class n252 leafNode
    n253[particles_b_field_parallel]
    n250 --> n253
    class n253 leafNode
    n254[energy_phi_potential]
    n250 --> n254
    class n254 leafNode
    n255[energy_a_field_parallel]
    n250 --> n255
    class n255 leafNode
    n256[energy_b_field_parallel]
    n250 --> n256
    class n256 leafNode
    n257[momentum_phi_parallel_phi_potential]
    n250 --> n257
    class n257 leafNode
    n258[momentum_phi_parallel_a_field_parallel]
    n250 --> n258
    class n258 leafNode
    n259[momentum_phi_parallel_b_field_parallel]
    n250 --> n259
    class n259 leafNode
    n260[momentum_phi_perpendicular_phi_potential]
    n250 --> n260
    class n260 leafNode
    n261[momentum_phi_perpendicular_a_field_parallel]
    n250 --> n261
    class n261 leafNode
    n262[momentum_phi_perpendicular_b_field_parallel]
    n250 --> n262
    class n262 leafNode
    n263(fluxes_3d_k_x_sum_rotating_frame)
    n106 --> n263
    class n263 complexNode
    n264[particles_phi_potential]
    n263 --> n264
    class n264 leafNode
    n265[particles_a_field_parallel]
    n263 --> n265
    class n265 leafNode
    n266[particles_b_field_parallel]
    n263 --> n266
    class n266 leafNode
    n267[energy_phi_potential]
    n263 --> n267
    class n267 leafNode
    n268[energy_a_field_parallel]
    n263 --> n268
    class n268 leafNode
    n269[energy_b_field_parallel]
    n263 --> n269
    class n269 leafNode
    n270[momentum_phi_parallel_phi_potential]
    n263 --> n270
    class n270 leafNode
    n271[momentum_phi_parallel_a_field_parallel]
    n263 --> n271
    class n271 leafNode
    n272[momentum_phi_parallel_b_field_parallel]
    n263 --> n272
    class n272 leafNode
    n273[momentum_phi_perpendicular_phi_potential]
    n263 --> n273
    class n273 leafNode
    n274[momentum_phi_perpendicular_a_field_parallel]
    n263 --> n274
    class n274 leafNode
    n275[momentum_phi_perpendicular_b_field_parallel]
    n263 --> n275
    class n275 leafNode
    n276(fluxes_2d_k_x_sum_rotating_frame)
    n106 --> n276
    class n276 complexNode
    n277[particles_phi_potential]
    n276 --> n277
    class n277 leafNode
    n278[particles_a_field_parallel]
    n276 --> n278
    class n278 leafNode
    n279[particles_b_field_parallel]
    n276 --> n279
    class n279 leafNode
    n280[energy_phi_potential]
    n276 --> n280
    class n280 leafNode
    n281[energy_a_field_parallel]
    n276 --> n281
    class n281 leafNode
    n282[energy_b_field_parallel]
    n276 --> n282
    class n282 leafNode
    n283[momentum_phi_parallel_phi_potential]
    n276 --> n283
    class n283 leafNode
    n284[momentum_phi_parallel_a_field_parallel]
    n276 --> n284
    class n284 leafNode
    n285[momentum_phi_parallel_b_field_parallel]
    n276 --> n285
    class n285 leafNode
    n286[momentum_phi_perpendicular_phi_potential]
    n276 --> n286
    class n286 leafNode
    n287[momentum_phi_perpendicular_a_field_parallel]
    n276 --> n287
    class n287 leafNode
    n288[momentum_phi_perpendicular_b_field_parallel]
    n276 --> n288
    class n288 leafNode
    n289(fluxes_2d_k_x_k_y_sum_rotating_frame)
    n106 --> n289
    class n289 complexNode
    n290[particles_phi_potential]
    n289 --> n290
    class n290 leafNode
    n291[particles_a_field_parallel]
    n289 --> n291
    class n291 leafNode
    n292[particles_b_field_parallel]
    n289 --> n292
    class n292 leafNode
    n293[energy_phi_potential]
    n289 --> n293
    class n293 leafNode
    n294[energy_a_field_parallel]
    n289 --> n294
    class n294 leafNode
    n295[energy_b_field_parallel]
    n289 --> n295
    class n295 leafNode
    n296[momentum_phi_parallel_phi_potential]
    n289 --> n296
    class n296 leafNode
    n297[momentum_phi_parallel_a_field_parallel]
    n289 --> n297
    class n297 leafNode
    n298[momentum_phi_parallel_b_field_parallel]
    n289 --> n298
    class n298 leafNode
    n299[momentum_phi_perpendicular_phi_potential]
    n289 --> n299
    class n299 leafNode
    n300[momentum_phi_perpendicular_a_field_parallel]
    n289 --> n300
    class n300 leafNode
    n301[momentum_phi_perpendicular_b_field_parallel]
    n289 --> n301
    class n301 leafNode
    n302(fluxes_1d_rotating_frame)
    n106 --> n302
    class n302 complexNode
    n303[particles_phi_potential]
    n302 --> n303
    class n303 leafNode
    n304[particles_a_field_parallel]
    n302 --> n304
    class n304 leafNode
    n305[particles_b_field_parallel]
    n302 --> n305
    class n305 leafNode
    n306[energy_phi_potential]
    n302 --> n306
    class n306 leafNode
    n307[energy_a_field_parallel]
    n302 --> n307
    class n307 leafNode
    n308[energy_b_field_parallel]
    n302 --> n308
    class n308 leafNode
    n309[momentum_phi_parallel_phi_potential]
    n302 --> n309
    class n309 leafNode
    n310[momentum_phi_parallel_a_field_parallel]
    n302 --> n310
    class n310 leafNode
    n311[momentum_phi_parallel_b_field_parallel]
    n302 --> n311
    class n311 leafNode
    n312[momentum_phi_perpendicular_phi_potential]
    n302 --> n312
    class n312 leafNode
    n313[momentum_phi_perpendicular_a_field_parallel]
    n302 --> n313
    class n313 leafNode
    n314[momentum_phi_perpendicular_b_field_parallel]
    n302 --> n314
    class n314 leafNode
    n315(model)
    n1 --> n315
    class n315 complexNode
    n316[include_a_field_parallel]
    n315 --> n316
    class n316 leafNode
    n317[include_b_field_parallel]
    n315 --> n317
    class n317 leafNode
    n318[use_mhd_approximation]
    n315 --> n318
    class n318 leafNode
    n319[include_coriolis_drift]
    n315 --> n319
    class n319 leafNode
    n320[include_centrifugal_effects]
    n315 --> n320
    class n320 leafNode
    n321[collisions_pitch_only]
    n315 --> n321
    class n321 leafNode
    n322[collisions_momentum_conservation]
    n315 --> n322
    class n322 leafNode
    n323[collisions_energy_conservation]
    n315 --> n323
    class n323 leafNode
    n324[collisions_finite_larmor_radius]
    n315 --> n324
    class n324 leafNode
    n325[adiabatic_electrons]
    n315 --> n325
    class n325 leafNode
    n326[species_all]
    n1 --> n326
    class n326 normalNode
    n327[beta_reference]
    n326 --> n327
    class n327 leafNode
    n328[velocity_phi_norm]
    n326 --> n328
    class n328 leafNode
    n329[debye_length_norm]
    n326 --> n329
    class n329 leafNode
    n330[shearing_rate_norm]
    n326 --> n330
    class n330 leafNode
    n331[angle_pol_equilibrium]
    n326 --> n331
    class n331 leafNode
    n332(species)
    n1 --> n332
    class n332 complexNode
    n333[charge_norm]
    n332 --> n333
    class n333 leafNode
    n334[mass_norm]
    n332 --> n334
    class n334 leafNode
    n335[density_norm]
    n332 --> n335
    class n335 leafNode
    n336[density_log_gradient_norm]
    n332 --> n336
    class n336 leafNode
    n337[temperature_norm]
    n332 --> n337
    class n337 leafNode
    n338[temperature_log_gradient_norm]
    n332 --> n338
    class n338 leafNode
    n339[velocity_phi_gradient_norm]
    n332 --> n339
    class n339 leafNode
    n340[potential_energy_norm]
    n332 --> n340
    class n340 leafNode
    n341[potential_energy_gradient_norm]
    n332 --> n341
    class n341 leafNode
    n342[collisions]
    n1 --> n342
    class n342 normalNode
    n343[collisionality_norm]
    n342 --> n343
    class n343 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```