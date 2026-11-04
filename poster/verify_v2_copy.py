"""Read-only copy-preservation checks for the A0 v2 poster.

Run with `python poster/verify_v2_copy.py` after building v2. The embedded
baseline records the original poster files. This script never changes a file.
Whitespace and font ligatures are normalized; wording, punctuation, digits,
case, math glyphs and chart labels are otherwise retained.
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
import pymupdf

ROOT = Path(__file__).resolve().parent
BASELINE = {
    "assets/figures/fig1a_parties.svg": "846e1730e2a2fb5844fc3a499ee7cbc0464d22a51e5350ffd05e5028753153b4",
    "assets/figures/fig1b_llms.svg": "2428ef30a9b805ba3a84f36107a5383f20e29f14be523f3a6182329d3c2522ad",
    "assets/figures/figures.json": "4cb51bfff0b849a4af53cf78ef3f8255aa98baa2f2171b220afe52ebb5dc12a5",
    "assets/figures/pipeline.svg": "c11bc04c2bcf46c43d18e0a6ec26e2fb396ffae4f44d2dd10a8c43102925d1f7",
    "assets/figures/polytope_3d.svg": "9f9e17bc4849dc6374e24c49d31da03b9bed5fb3810f92288f60b2d452033381",
    "assets/figures/polytope_chrono_2d.svg": "a4c7badc0bb1d973ce6c2885461f3eb87fd5cc36214ade0d58aca254cd788ee2",
    "assets/figures/polytope_chrono_2d_2009.svg": "78f071e51bc3367ea2976b0a89c6428da0e995b3d2abb607eb7e1e5b767f9ede",
    "assets/figures/polytope_chrono_2d_2014.svg": "ab9aa5fc408e3160879366b3fd3582238e40a9dd9f407411ddc53cbea42acea6",
    "assets/figures/polytope_chrono_2d_2019.svg": "7b80f456570b4904df67bad4b0da592df9eb7e05f010b697975b4bf5188e6df9",
    "assets/figures/polytope_chrono_3d.svg": "62d49ef6327b09dc90c52de90b849980af7f23846d7a8250a30e4db8d816c2b8",
    "assets/figures/polytope_chrono_3d_2009.svg": "2d6a07ac798b6032eb21fc447d763679f28db88d53a97719c58a57868787041a",
    "assets/figures/polytope_chrono_3d_2014.svg": "0d6d03eacf8aa756825df47d033e0fbfa787a40873122c39f72b303012a9ebc3",
    "assets/figures/polytope_chrono_3d_2019.svg": "a007378b45321d209ece03b1f48c3f48ff67c2d22ef4c8d713a5192c29cce2be",
    "assets/fonts/BanglaPoster-Regular.ttf": "ea7fd71d25bc92c4e110ec9981928741623773ef6f1648f5626265583bb56c9c",
    "assets/fonts/BanglaPoster-SemiBold.ttf": "1a1181237b03015fc2b36a44950086cd898af2bfcae4ab8cca72fce92ab12933",
    "assets/fonts/fonts.css": "e4365de6964356d1f1700e1d19e82a43f2df146bfbe01889a821f2914cff3c82",
    "assets/fonts/FrauncesPoster-Italic.ttf": "020c2195d41a19c18d77c402a1daad03e6bf8f4ea4a77aee14f2e03a0f3035f6",
    "assets/fonts/FrauncesPoster-Medium.ttf": "189b641410f08c6a9d755cbf9d66ac3ff6bed255f052cdfd320facbc0e7821fa",
    "assets/fonts/FrauncesPoster-MediumItalic.ttf": "a1b0164cdd2f1eb3ef244dfd1f807f115b57a5150557a1370e6082ffe2aabf85",
    "assets/fonts/FrauncesPoster-Regular.ttf": "e4b534918fc2929bd615bb06dcb1a42ade1d6b980464df9e091a93df953d58c0",
    "assets/fonts/FrauncesPoster-SemiBold.ttf": "e523dae7345d01c6132da56590782efaaa3b166acd08826a754bf8a996b943c8",
    "assets/fonts/FrauncesPosterMid-Medium.ttf": "8b945d32aa99dc966e78622bc2c889a04ac69090d3e18e24c54b05e401843f97",
    "assets/fonts/FrauncesPosterMid-MediumItalic.ttf": "4284d1ff53bd669f51915486211201db1283181d03077e9a6ab5aeebf6336031",
    "assets/fonts/FrauncesPosterMid-SemiBold.ttf": "2647dce6c4a192181b4d20ae8c90f8e8959da964874d5bff83e0241da99423b1",
    "assets/fonts/FrauncesPosterText-Medium.ttf": "d79d200abb5a3f1efd2d5159d0c40fe2cded7f157e1838bddab2b6efa83d123c",
    "assets/fonts/FrauncesPosterText-MediumItalic.ttf": "16a789af8924cda4e67fc69adaa5074861e71f4338bc0fbad86c9541cfd6f0a4",
    "assets/fonts/FrauncesPosterText-SemiBold.ttf": "d5019c442e2940bff1cb14beec39834c87bccaf6e7404db215af86f11e9345b2",
    "assets/fonts/JetBrainsMonoPoster-Medium.ttf": "e1ad5b7344e19680a47c7284c5621b7ecaf51d34fe31dc79662339ab1ca3db93",
    "assets/fonts/JetBrainsMonoPoster-Regular.ttf": "37efd912e6dc7ecddb52a02498fe2ea84a391c89faf88319c00e35fa7bec5cc5",
    "assets/fonts/JetBrainsMonoPoster-SemiBold.ttf": "ba06acc8c7a71cd8f7834092e6792e30d92d6db9f1701b8f920d86343b0366fb",
    "assets/fonts/licenses/GUST_LatinModern.txt": "49ea6cb9257bbee0a3979c48a774cd221550ac1c20c95549efe45fc99cc18050",
    "assets/fonts/licenses/OFL_Fraunces.txt": "bdf4c22802eaf804f998195871c6b8938aac2ac14b2d78a8bd66a6f1eced833b",
    "assets/fonts/licenses/OFL_JetBrainsMono.txt": "b2fe5e8987594e9ffd1d2ca52a2f5d73eb8335243893c5d6254b5ad69269591d",
    "assets/fonts/licenses/OFL_NotoSerifBengali.txt": "754f0e221aa7d5a915489f3bf1f20fe53ddc35ab2834a4d91656d78f9622de70",
    "assets/fonts/LMMonoPoster-Regular.ttf": "51b40599b12f3c7cdfae3c73584a2f9e469bf414736d49800158ab40ffbaa8cb",
    "assets/fonts/LMRomanPoster-Bold.ttf": "f45d7dd82cb1b2ce717ef2cf9c2f76e7c01d4a914ccd9f6b76c6dddb609e334f",
    "assets/fonts/LMRomanPoster-Italic.ttf": "8af883e569a2a12d3d417063da311aa389248c33691b547d7cbe4beae1ed465b",
    "assets/fonts/LMRomanPoster-Regular.ttf": "7a5a00c58ded1c5cc2f4042c4203f2648ce445e077e72297faa728c3d4980962",
    "assets/fonts/PagellaPoster-Bold.ttf": "e0b4a1cdf02c5a5d79047cc7accd96ab48992dd69dffd5a508e7c197ef79bd8f",
    "assets/fonts/PagellaPoster-BoldItalic.ttf": "3c35994dea36d0a4e5fadf8ed63176d874756daee12096fe84f5fc4a0bba718a",
    "assets/fonts/PagellaPoster-Italic.ttf": "4d96aa2655586824ca750767a222fa660100c4a649190a1af8850b8f62a88c57",
    "assets/fonts/PagellaPoster-Regular.ttf": "6ba9e2ffcd142b31d28dfc47ca7a3c57c6d316db7706959dfffe1f3c8205026d",
    "assets/icons/deepseek.svg": "0f0827d6d85974bf965954cd70913051e5ce7619c7ba01a0b096e005959db5f2",
    "assets/icons/gemini.png": "6ba54ed1042a7eb8fc125ebd6df7d424a8c371c610070991a5035a6bff3c4658",
    "assets/icons/gemma.png": "e3a335dcd06d64fcc027a5fe4f39ce89ec043e7305e281e170b57e31abbac15d",
    "assets/icons/gpt.svg": "12c696769e08fc3c20a67f05b547a2526fc1160b2293eb79885bdddb44cb9c5b",
    "assets/icons/grok.svg": "92b914b286254c4fad73c421aaeec7f80fba0d5736fc7abbb5ba47b41d1f5751",
    "assets/icons/ibm.svg": "be9dc16f8ddcf829ce8ccf6cce3706e172e15640278b137f4c5681c7c2926829",
    "assets/icons/meta.png": "2c15771b2ab39dd02eea9c01ec444d89b0441134c1e223b80de36ea8f4925340",
    "assets/icons/model_icons.json": "794da7be8e806653b287a2bade285bb8e1adf8022178610b331e38c66bfdf8fa",
    "assets/icons/qwen.png": "4cd181931b8044080723e5124d14cd4de2f2e160bd7d83c0465c6de7d8bdc2a8",
    "assets/icons/ui/arxiv_colour.svg": "2dcd8840f46859c5e29b5df20b15f98aa87254e09ecdedb2c11a1ed5028504fc",
    "assets/icons/ui/arxiv_white.svg": "1261b43c74121823decb7893afb633e91bca71fecdfad12ed0f4288a5afaa716",
    "assets/icons/ui/bulb.svg": "7367e63226bedede965e3c2be96e293981d611580c1d44d344b6862848dc90ae",
    "assets/icons/ui/envelope_ink.svg": "1f475e9ffac808c51d12e459d52d1c1c1b0c72d596d017361a9cd8bd2c3eeff9",
    "assets/icons/ui/envelope_purple.svg": "d5b8d1717bf1a9299451fb207d129be9b7c52de4d3a87f51c9ad1047bdfaa5fc",
    "assets/icons/ui/envelope_white.svg": "2fa228cf74d168043bc5fc837293c6f1bc0a0137472a99c2d9dfe4a0dcdc290b",
    "assets/icons/ui/github_ink.svg": "5035fb39870fcffc622cf01b55577ad7e0b5a76e53c78beace1ac938baf97389",
    "assets/icons/ui/github_purple.svg": "af0b13aade77536ab14195b4d9eef042c751b0bfb6d1f458f7dab3933fae9d34",
    "assets/icons/ui/github_white.svg": "83e43846df9f47ed8e6fcf60d9357fe6778cde4afcf294642f0940fd9e72780e",
    "assets/icons/ui/globe_asia_ink.svg": "861de46b3012fd130ea9fad1c9347ada3c738390a7ff5b5a36be506bfaee8a90",
    "assets/icons/ui/globe_asia_purple.svg": "0216ee2a040b770f85cc0094370c0a16c96fea227cae84cc366d8b3477ee541c",
    "assets/icons/ui/globe_asia_white.svg": "bf072fa5c608efde5c2193f10c975f41a48a0e235c049cc0c2acbc8d7ae5e3f5",
    "assets/icons/ui/globe_ink.svg": "147911dd4f60517e9a50a34f7f6130017d0a941b8855b0dbbd8c1aeb18656256",
    "assets/icons/ui/globe_purple.svg": "074413e7de51d3eec5f3631c55664f8e7a518e1f9c01d5b3aeebd7b5eceac2dd",
    "assets/icons/ui/globe_white.svg": "e1d6e5a4504fae10cb3182bf07b9c485e40913faaa34dccde4b13e5ed8285787",
    "assets/icons/ui/heart_red.svg": "c64869885d1debf61b1ed06a6e2392b9b6a50ea8a3aab0465930e97809f0d45d",
    "assets/icons/ui/twitter_ink.svg": "06e205137f42f4b0410cab7457bfadf73383f76cdb027d9f6fdce6393fb5783f",
    "assets/icons/ui/twitter_purple.svg": "0eb235ad46321c8d0a5fe983c93b344ebd2e91c2146d9514c78196bf6766e3e3",
    "assets/icons/ui/twitter_white.svg": "799f14b5aabbb07361fee352bf50bed99bbd1f3f8c73ea8a3e4e7f191c6e3a3c",
    "assets/logos/aacl_2026_logo.svg": "302fbce5539a902de1cce9ac9c75a610432f4c5d8896f8782ec0ae14719ecc81",
    "assets/logos/aacl_2026_logo_v2.png": "d1b66818a66d3abf53c8c1066a73188d3c1b33fcb69aaa807955db8c77e73b00",
    "assets/logos/iut_emblem.svg": "c8f1c876d96931d594ad799c768869e874e28267382ac2e03fee8ef515caba76",
    "assets/logos/iut_emblem_band.svg": "e8123a15af6f8d28f0d2eb4be751498de7834a06d34bc17266d4ff8c086f3be5",
    "assets/logos/iut_lockup_white.svg": "2ce45f675fa40f397faf0061121090487cb34af37e81bca5c5c54b4475516470",
    "assets/logos/iut_wordmark_trace.svg": "8bd0a37973d32fd36aa10498b8796b0a75eb5e43f69c567c03d13114efe59392",
    "assets/logos/iut_wordmark_white.svg": "182320e85c9bc1177447c79ed8fe4fd283627576fed4393088e560c706b97e19",
    "assets/logos/oic_emblem.svg": "39941f59c8c64b5270faeadc9b3642c1901ec601b13807b1670271225162e442",
    "assets/logos/project_logo_band.png": "354541d75c8ea6378ca3036fde841683ae94264b85d7fdbb3bdd6f3fe6511991",
    "assets/logos/project_logo_qr.png": "b08fda5193fe9a0fce43b99fdfe12cc26d73bab45001cae19d1ada4823bb9216",
    "assets/MANIFEST.md": "f6eb175bef26679787e3397399862456a5d68c02792ffcb8db1e2641ccdb50ee",
    "assets/qr/qr_card.svg": "22b2411ab73530c01b3780dadb5afbb8460d93d77f7e3bd3f00c5047c843a4fd",
    "assets/qr/qr_card_white.svg": "ec40ad78a539b265566fa976c4f83d7a69ac5316b889ace6f5c1f6d05dcae67c",
    "assets/qr/qr_card_white_compact.svg": "b03598147d2db485c6aa380cc8f219eb8126fa33f810586ed7cf188d95572f43",
    "assets/qr/qr_modules.svg": "7f0311d87683fe60301d183738dd11281d08a43ab4a56f0cee500005a8e63028",
    "assets/tools/build_wordmark.py": "b00dad4a0749b151fa120637c2db899fb0a16b8a8b5d9db03f9a3b45e9dcc8ae",
    "assets/tools/chrome.py": "d64f055ff9fb147b3eb6955f29abb5292ecdec9508b4bc21fea0882bff572bec",
    "assets/tools/compare_emblems.py": "f47c042e4c850051cd61173b0b8b7937c78efe92be07ef557cf329abdff5dc4c",
    "assets/tools/compare_project_logos.py": "9ee54ff1a27d098138be395574ef52d6efed09edf5c747acd250bccd4d80428f",
    "assets/tools/decode_refs.py": "731a86de7133185b8bb418e011f5309427763d9f4b4f40f984a88f3b2a0a31d1",
    "assets/tools/extract_ref_logos.py": "223ac91ac3b5bdb3659dab96275edcde598bd21b4e1f2b035f344b4967212c1c",
    "assets/tools/fit_wordmark_font.py": "3feff7bdc1e86aef0016331b02403127534e7512ea8e22d6e62885d8ecc49dc0",
    "assets/tools/font_features.py": "3f29aba2eb868e08dd263583376983e587d29d10cb71165726702d7517d44e50",
    "assets/tools/identify_wordmark_font.py": "5b8279a15bc55bd84e18736dcc79ae1b9ac56667e86502189d3b391cbc30fec8",
    "assets/tools/inspect_figures.py": "f46c0eef49837650f63bf1ce661d80b4633640ce7234ca738f20f684b0ceb503",
    "assets/tools/inspect_flyer.py": "5cd070874f9c5b4e6791cd378f1d7b7076de23f821f83d09b0313e3b6d365d3a",
    "assets/tools/inspect_letterhead.py": "fb14ab6e46878b14fd7aea9acf1ab364bf905ba09fea0be70afd39d11ff2f094",
    "assets/tools/inspect_refs.py": "2526a37c8c43e9cc481ca404797f0b7d1aa0d21466c99ea3939afbdd8dbbfe19",
    "assets/tools/make_figures.py": "a3943ebe6db6fa3ddf28052cdb4eec04835850814b89b7e3b91a2f96305c55cc",
    "assets/tools/make_fonts.py": "0094b5f73a4d80ec1018ea068615728701cc30e4624d2401ba1f39a99a4e97f7",
    "assets/tools/make_icons.py": "53e8036028b80b675441f24eba4482dd3d050e3c895297964f7cdd9449e66040",
    "assets/tools/make_iut_lockup.py": "f71ad8596e28c94a37da5d362ff1179ec7954537bc3c30ccbfb58d5e3764be98",
    "assets/tools/make_project_logos.py": "0eff5b002d937bb035d953b7dd4375ac2f107cd134156f2663cdaef659100218",
    "assets/tools/make_qr.py": "57deeae48f3a9e48fc2cee5962fe71e31f069bca3ce9129e0b7ad81f332a4b17",
    "assets/tools/make_raster_icons.py": "7009b40bab18d22349a3701f44c7ba8f5f745b65c2c79e39a82f606bc23908aa",
    "assets/tools/make_ui_icons.py": "25848543d9ea823a2f5a028c584ade58e961ac835f7b723f83acc332bd67233a",
    "assets/tools/measure_emblem_aspect.py": "8daf11a3343b835f8943d05a6aaf81f0c1097fc18b98588c910c3f6fbbdd08db",
    "assets/tools/measure_emblem_aspect2.py": "f267162d4e07763aa7880cc5fc089ed9c2295b760188b943f8efe4d6cc69affc",
    "assets/tools/otf2ttf_lm.py": "9ab45e5ed1e4f3fe6a5d9cb2120b85286793c07d7adf11bab5358208ad5bf477",
    "assets/tools/otf2ttf_pagella.py": "fec564c939f8303ed38f0803490a61f065968b10cda8bb1cb6525631e3b64fee",
    "assets/tools/preview_band.py": "fac8dfe45b20157537deb7bd4c4d3a40b329b721763efc5450c34de2f5c81576",
    "assets/tools/preview_ref_lockup.py": "75b9afe713ab9d664bcb3d619d5f130c4e3328fb01985c43670b6139e80fc632",
    "assets/tools/scan_iut_sources.py": "11cae53b9d9246fef44d4bcab18c872160fd8a3092339903baeb7123a1fc7870",
    "assets/tools/test_aacl.py": "f4bb2cc04967f133eadd8429fda8cde581175535c909f58f2e4ccacc1bcc9b95",
    "assets/tools/test_figures.py": "a3c088ca98f198b6050a6f2b418f7be6dec36c92062132a55975431b1de13761",
    "assets/tools/test_fonts.py": "ba4e3eac6eab571655da0ebea80b28d90ee46d165b95dab2923b68ce37d8a4d2",
    "assets/tools/test_fonts2.py": "85d89dce7d63865a4a9bd727a9ee0b88d2ae2a13272306f0f98eec021b6136a7",
    "assets/tools/test_icons.py": "b6021c9c3a9465e66d6d48bf3dbeaadfaa4d9a4d0ac19e426e003a0f0d3268e7",
    "assets/tools/test_lockup.py": "ada403126e0a358c8761d2bc71251fdbbb913a1f0f1598605ee8baa99d65662b",
    "assets/tools/test_math.py": "fd59f5afd992dd2130944f2abf2e0f2f4653c3236ddea77a672e5c702857bb38",
    "assets/tools/test_panels.py": "23066d3473179c0ca3c199b94ed6dfc544ccb99113f5437e79a7c278ab2e3b7a",
    "assets/tools/test_qr.py": "7b8583f96f58400ad7c0ccbf986c2803477497501f525c92759895c752bbc013",
    "assets/tools/test_weight.py": "90b451592d3c2e9234fb61ed4fd643fff2950f572312db34a5c70590160e2a72",
    "assets/tools/trace_trials.py": "6ace0a3eaf3541cd96938925622cc443fa73fda723faddbf1a91a86325ebc0c0",
    "assets/tools/view_hero_raster.py": "be658814bcadffa767eb47a10de81ef003c3805a24a53b0ea01efa8b5028121d",
    "assets/tools/wordmark_fit.json": "5e39726b3eda5bd54e914aa14a66755791c718db97487ab68ba275d5381a652d",
    "assets/tools/zoom_fig_pdfs.py": "d438182256a52bfc2ef0dd0f8f1b521db5459b4f933f75745862966bc8d6dcec",
    "assets/tools/zoom_hero_compare.py": "b80068cb4b03dab52bab465a568fe7a471608a6e6fc7e1acea0740563388058f",
    "assets/vendor/input/tex/extensions/boldsymbol.js": "d6771fee0772db2657796c8d0e20e1878bb3237f6d3ed1e828e1834a4ff743ca",
    "assets/vendor/tex-svg.js": "d4295dc33744836935c1399feece5159577b34c5c8ffb9f1c6324cd82e03a882",
    "build/poster.built.html": "5e415636050c875c6e50a88da0a205c0e09a292f879cebfc44bba1aeaf754d87",
    "build.py": "abbbd23585818ae1901d22f616e50efdd0bd1e95a12caca9e1bb05767e836c6e",
    "charts/band_contours.svg": "6f4432d7bc7da65ff7285376bb4bcac008f8f61ddc9fbecf577fb8e85e273833",
    "charts/chrono_2d_2009.svg": "65eba48f98476af2c88cb46b78074be081f46d34089d1bf2032fbc1cf0350300",
    "charts/chrono_2d_2014.svg": "5989b436ec8833f0e77098e9364a54f1800a699ee4573fc232e3fe6c7d2d509d",
    "charts/chrono_2d_2019.svg": "c553f49ab2f50b789615aace99212bfb894c622b07a9ed215f369bad8ba8ded4",
    "charts/compass_legend.svg": "affa33923a9389bc2ae153b60e83dc86e591a5c8b97e69310f9a6619a07f6b69",
    "charts/contact_sheet.html": "12c8d4e0e33d65a68ff63b9415bb83e6eefca9da745b46e19a8cbd25bf46fe06",
    "charts/contact_sheet.png": "cc906a2dda8196a70f3cf8a38ce1a9ec7a1d74bd5f485e1e52e5b8cd53d98ff5",
    "charts/coverage_bars.svg": "a5df2b9a02c5f66d88e3ba72e8e20d16dea2ef8c45048594cc6cd3feb20a74f9",
    "charts/ds_compass.svg": "ab248c8d604e4cbaedfd75bb8bf549896f04b05251c2cb6df48acb7991f0b7c0",
    "charts/hull_glyphs/deepseek.svg": "1db6a7d4c8c63d7e177094190ba826d97a7befc737d2305c59e830a6d7cfe53c",
    "charts/hull_glyphs/gemini.svg": "4afd5c746416443b3b36b9651b538492c001e204c60e5ae8f084b49807f84fb4",
    "charts/hull_glyphs/gemma.svg": "f89a2d080c1a1d8d4abd3c0fd1530583d897389745a8f12d8393c2b4a5ea6e7c",
    "charts/hull_glyphs/gpt5mini.svg": "89fec3cff4e2b38f8e846f661c2782acf9cadd70b13fa2f55514d228dbfabb62",
    "charts/hull_glyphs/granite.svg": "44b81339c1ee884aeb63ab24c9325ac87d7263275772da4cb7bbc0d2d4b8af05",
    "charts/hull_glyphs/grok.svg": "9159c3962656d2251bee6f2bf00e616a64af3c2195d7e530116dd903ae85a0b6",
    "charts/hull_glyphs/llama3.svg": "a89e0f08eaacb7a3de52978b283e366b491a9cb16760f3c677c2c6b1b85a694f",
    "charts/hull_glyphs/llama4.svg": "72237d887798b8c7895daa33195c798e77622f68f2fb948390faaeef3ebab2a1",
    "charts/hull_glyphs/qwen.svg": "f11740a50e0dab32f1064c387975e4c9e9f70d46d415786f97d6ddc2a37482a9",
    "charts/ias_dumbbell.svg": "6d3e6d2bf7afedf89f09591240e34591ec06f90f6e991628b29acdc649566038",
    "charts/instrument_matrix.svg": "25db75ce9958833a1b6715754503da1a1bc066864ae581a02adddab2acc68c05",
    "charts/lds_bars.svg": "d9582f417aeb91541f2b0582e8d1cd504b8dbd36a8bedef621917bf49555cae1",
    "charts/lds_bars_tall.svg": "3c7eb13aa42d70fac74a4bad1d79a57db6c8bb8348b0e2c8df4e6b7cfc70b333",
    "charts/lds_compass.svg": "5bd9cb3c27d096519b281debe90ec2b0dc3bd622d8625772dd14b862cd196037",
    "charts/monoculture.svg": "03d22b1758e5118546fae76a8bc1d07f760604bc47ec5dc3af0f7dbb6addbaec",
    "charts/mtmm.svg": "073ba3d4ea2afd8fb36dbe0892e8043b609564c5638bb98558f7a67eacf4c22d",
    "charts/pca_bars.svg": "590360feeff05abefc3899b43b945f55d23a5822c6cb8d2a64231b7e6dbd27c5",
    "charts/pipeline.svg": "8d6cb4feb196ec0890771fe517f4a4e14386ac721f81b1aa1977629000fdabf0",
    "charts/pis_bars.svg": "e5b7414a96f765c555cbcabbd70dd2413dad9eb9e3d0bd78a92a6b739632a545",
    "charts/pis_bars_tall.svg": "c060a421f70136d4a23a80dbe63260bb7bf5f513194a282c9d8e5494587af480",
    "charts/pis_compass.svg": "06c27b98218eed554481ff6bfca8a1815fe9377a6075de18f6692e4284b6f00d",
    "charts/point_to_shape.svg": "028414be000c1dc7b3e356cdbd0217a7dbe3d680f31dcecded99dd69ef5bcad5",
    "charts/pss_bars.svg": "b191f2a9ffbc8e9b83610ab50e4a551b1b0f6f13cd2a5296db3dc963b7626d15",
    "charts/pss_compass.svg": "caba31fc7b95a961fc262a073ccef758175657342e8c4add4747ed7cd37edbe2",
    "charts/README.md": "2210afc6042c2ab7fdd759667fb8671b29504c36a8ec100ce5807fa3b52b5599",
    "charts/rss_compass.svg": "bc68c0553b1832ae904080ffaf77198f2b99fec22dcd8578f58150c363487cae",
    "charts/rss_waffle.svg": "a04f1606631faeab14c920b4d57b0df99cb6250c7a4138cddd85c8d040999908",
    "LLM-Ideoplasticity_Poster_A0.pdf": "fedc97a156c47ab58e9ca6b804b5e025305887abb2956e1c369e8439df29fda9",
    "LLM-Ideoplasticity_Poster_A0_flattened.pdf": "eba2ea91dd9596114565c86859ec5a9e5093def0c4bb849a27955556c0b998f5",
    "src/BRIEF.md": "5fc3a221f277893dfc8f9b03c366ce224989a35a55c11505911e8715b4ea7b37",
    "src/charts/build_charts.py": "3b7bee9a9c84875056d17e6c4fdf98f6bed3aded1c92a3b2e1e5517ff8fcefad",
    "src/charts/chrono_clean.py": "42d672f383172dd264a0aef62379800a3378a8c4ff289efe96d5734a66b8d70a",
    "src/charts/chrono_verify.py": "2a45ed64f240ad966e2b3335b15f028e07a81c73cd5a6a3eddc2d819a6e3a24c",
    "src/charts/facts.py": "5d570d5540748b4017305e789292e085f67efd0433c9c128fe9330e4b08f87a3",
    "src/charts/sample_palette.py": "0426581fa1d4ebcfe3c192e29dbb4c2770bd62be2493a6eaaf9bef92a4d1e45f",
    "src/charts/svgkit.py": "1a36be906b0b69a5eaef5a6d9f5f66fa0c2dde55f5369b79d0a0b41b9db97133",
    "src/charts/tex_cache/snippets.json": "fcb3193da4f24c4830f4546435441e9fbb753f7d0b1b58e195d66ef1a6e417b2",
    "src/charts/tex_cache/snips.aux": "67b32dce0f49801ffe559bb8d2b4fbdc43a6c18522e08615b67a0263201f0807",
    "src/charts/tex_cache/snips.log": "e0a80a3cef42500f2649405c0218e720a51f2db748aba71c79cf7cbfb36bb494",
    "src/charts/tex_cache/snips.pdf": "c06977469e503f1bfee25e7d7bc485d8a1fafddfad92bbead123560d6b79b0e0",
    "src/charts/tex_cache/snips.tex": "819c6055334606f0383261e8d755e06ed9a6349527b410763f39ce62a24a32db",
    "src/charts/texkit.py": "56692c7c991811f77afa9675c9410289db753b81fa7df9452c7db1d684177eb9",
    "src/copy.md": "c94b5abf8615506980908b519d71514852e21d93afdf2b514801ccab153fa382",
    "src/poster.css": "24631d599b9a5566be3c2f46e62cbd8267dafae43ca27c68e76f8bca79a968c6",
    "src/poster.html": "18c41e5bc9104036ad6e19b4a9e46b0fb5dec706a9d91cd04854062aa599be98",
    "src/tokens.css": "acfdd8e12a04dc2e2cd928b05ffbdd3052cb0711253746bd335f67415c7e7ce6"
}


def compact(value: str) -> str:
    value = unicodedata.normalize('NFKC', value).replace('\u00ad', '')
    return ''.join(value.split())


def semantic(node: Tag, skip_svg: bool = False) -> str:
    """Extract visible text and outlined glyph data-text, in DOM order."""
    if node.name in ('script', 'style', 'defs', 'title', 'desc'):
        return ''
    if skip_svg and node.name == 'svg':
        return ''
    value = node.get('data-text', '')
    for child in node.children:
        if isinstance(child, NavigableString):
            # Comments subclass NavigableString but are not visible text.
            if type(child) is NavigableString:
                value += str(child)
        elif isinstance(child, Tag):
            value += semantic(child, skip_svg)
    return value


def diff_excerpt(old: str, new: str) -> dict:
    import difflib
    matcher = difflib.SequenceMatcher(None, old, new, autojunk=False)
    changes = []
    for op, a0, a1, b0, b1 in matcher.get_opcodes():
        if op != 'equal':
            changes.append({'operation': op,
                            'original': old[max(0, a0 - 45):min(len(old), a1 + 45)],
                            'v2': new[max(0, b0 - 45):min(len(new), b1 + 45)]})
            if len(changes) >= 8:
                break
    return {'original_characters': len(old), 'v2_characters': len(new), 'changes': changes}


def html_inventory(path: Path) -> dict:
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    body = soup.body
    charts = {}
    for svg in soup.select('svg.ch'):
        name = next((x for x in svg.get('class', []) if x.startswith('ch-')), 'unnamed')
        charts.setdefault(name, []).append(compact(semantic(svg)))
    math = collections.Counter(compact(semantic(svg)) for svg in soup.select('svg.tx'))
    # These independent inventories expose table changes and preserve copy if
    # typography wrappers change. Exact full prose comparison remains stricter.
    table = [[compact(semantic(cell)) for cell in row.find_all(['td', 'th'], recursive=False)]
             for row in soup.select('table.fingerprints tr')]
    images = [t.get('src', '') for t in soup.select('img')]
    links = collections.Counter(t['href'] for t in soup.select('a[href]'))
    return {'prose': compact(semantic(body, skip_svg=True)), 'math': math,
            'charts': charts, 'table': table, 'images': images, 'links': links}


def svg_labels(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'xml')
    return compact(semantic(soup.svg))


def pdf_inventory(path: Path) -> dict:
    doc = pymupdf.open(path)
    text = '\n'.join(page.get_text() for page in doc)
    clean = compact(text)
    return {'pages': len(doc), 'page_sizes_pt': [[round(p.rect.width, 3), round(p.rect.height, 3)] for p in doc],
            'text': clean, 'characters': collections.Counter(clean),
            'numbers': collections.Counter(re.findall(r'(?<![\w.])[−-]?\d+(?:\.\d+)?%?', text)),
            'links': collections.Counter(link.get('uri') for p in doc for link in p.get_links() if link.get('uri'))}


def main() -> int:
    checks = []

    def check(name: str, passed: bool, **details):
        checks.append({'check': name, 'passed': bool(passed), **details})

    changed = []
    for name, expected in BASELINE.items():
        path = ROOT / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if actual != expected:
            changed.append(name)
    check('Original files are byte-identical to baseline', not changed,
          files_checked=len(BASELINE), changed_files=changed)

    old_html = ROOT / 'build/poster.built.html'
    new_html = ROOT / 'build_v2/poster.built.html'
    old_pdf = ROOT / 'LLM-Ideoplasticity_Poster_A0.pdf'
    new_pdf = ROOT / 'LLM-Ideoplasticity_Poster_A0_v2.pdf'
    pending = [str(p.relative_to(ROOT)) for p in (new_html, new_pdf) if not p.is_file()]
    if new_html.is_file():
        original = html_inventory(old_html)
        revised = html_inventory(new_html)
        same = original['prose'] == revised['prose']
        check('HTML visible prose, headings, captions and reference copy', same,
              **({'normalized_characters': len(original['prose'])} if same else diff_excerpt(original['prose'], revised['prose'])))
        check('Math expression inventory including outlined glyphs', original['math'] == revised['math'],
              expressions=sum(original['math'].values()),
              missing=dict(original['math'] - revised['math']), added=dict(revised['math'] - original['math']))
        check('Inline chart labels, numerals and formulas', original['charts'] == revised['charts'],
              charts_checked=len(original['charts']),
              changed_charts=[name for name in set(original['charts']) | set(revised['charts'])
                              if original['charts'].get(name) != revised['charts'].get(name)])
        check('Fingerprint table cells', original['table'] == revised['table'],
              rows_checked=len(original['table']))
        check('HTML hyperlink targets', original['links'] == revised['links'],
              original=dict(original['links']), v2=dict(revised['links']))
        check('HTML external image slots retained', len(original['images']) == len(revised['images']),
              original_images=len(original['images']), v2_images=len(revised['images']))

        # Any external SVG redirected to the v2 figure folder receives a
        # separate text audit. Outlined source glyphs and live SVG text use the
        # same semantic representation. Reordering labels is allowed, while
        # character inventories are retained as a second check.
        for old_src, new_src in zip(original['images'], revised['images']):
            if old_src == new_src or not old_src.endswith('.svg') or not new_src.endswith('.svg'):
                continue
            a = (old_html.parent / old_src).resolve()
            b = (new_html.parent / new_src).resolve()
            if not a.is_file() or not b.is_file():
                check('External SVG exists: ' + new_src, False)
                continue
            left, right = svg_labels(a), svg_labels(b)
            exact = left == right
            same_glyphs = collections.Counter(left) == collections.Counter(right)
            check('External SVG label copy: ' + a.name, same_glyphs,
                  exact_sequence=exact, original_labels=left, v2_labels=right,
                  missing=dict(collections.Counter(left) - collections.Counter(right)),
                  added=dict(collections.Counter(right) - collections.Counter(left)))

    if new_pdf.is_file():
        original_pdf, revised_pdf = pdf_inventory(old_pdf), pdf_inventory(new_pdf)
        check('PDF remains one A0 portrait page', revised_pdf['pages'] == 1 and
              all(abs(x - y) < 0.5 for x, y in zip(revised_pdf['page_sizes_pt'][0], [2383.94, 3370.39])),
              page_sizes_pt=revised_pdf['page_sizes_pt'])
        missing_chars = original_pdf['characters'] - revised_pdf['characters']
        added_chars = revised_pdf['characters'] - original_pdf['characters']
        check('PDF original searchable character inventory retained', not missing_chars,
              original_characters=len(original_pdf['text']), v2_characters=len(revised_pdf['text']),
              missing=dict(missing_chars), added=dict(added_chars),
              note='Added searchable glyphs are permitted when formerly outlined SVG labels become live text.')
        missing_numbers = original_pdf['numbers'] - revised_pdf['numbers']
        check('PDF original numeric tokens retained', not missing_numbers, missing=dict(missing_numbers))
        check('PDF original clickable link targets retained',
              not (original_pdf['links'] - revised_pdf['links']),
              missing=dict(original_pdf['links'] - revised_pdf['links']))

    result = {'status': 'FAIL' if any(not c['passed'] for c in checks) else ('PENDING' if pending else 'PASS'),
              'pending_files': pending, 'checks': checks,
              'scope_note': 'Copy verification complements, but does not replace, rendered visual/overflow QA. '
                            'Whitespace and compatibility ligatures are normalized. PDF extraction can depend on font encoding.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['status'] == 'FAIL' else 2 if pending else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
