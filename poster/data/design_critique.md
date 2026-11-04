# Design critique: LLM-Ideoplasticity A0 poster

Reviewed `poster/LLM-Ideoplasticity_Poster_A0.pdf` (build of 2026-11-03) against `poster/src/BRIEF.md`, the owner's ACL-SRW 2023 and HaSPeR posters, and the project site. Method: whole-page renders at 900 px (the 3 m view) and 2400 px, a 1-arcmin (3 m) render and a blurred grey squint render, 18 overlapping tiles at 110 dpi, and close crops at 150 to 400 dpi. Type sizes come from `get_text('dict')`, positions from text spans and vector drawings, and contrast is WCAG, from sampled pixels. Coordinates are in mm from the top-left corner of the page (x across, y down). Renders and scripts are in the scratchpad folder `critique/`.

## Verdict

The poster is disciplined, faithful to the house skeleton and well above template quality, but it is overfilled. Every text size sits a step below the brief, and the cramming shows exactly where it hurts most: the thesis line, the closing line and the fine print.

**From 3 m.** The eye goes band title, then the six black 72 pt numbers, then hero panel (a), then the thesis line, then the MTMM block and the cyan polytope.
- The thesis sentence lands if it is read.
- The punchline pair does not land. "Local plasticity / global compression" appears only as 18.5 pt strip labels and as heads 3 and 4, 360 mm apart.
- The big numbers mean nothing at that distance, because their labels are not legible.

**Reading flow.** The order of sections 1 to 7 is obvious. Two placements are off:
- The Grok flips sit between §1 and §2, instead of with the RSS and LDS cards they illustrate.
- The exploratory MTMM is the heaviest mass in the lower half.

**Charts as a family.** The poster-made charts read as one family. The three pasted paper figures (1, 2 and 3) do not, because of their sans labels, outline pills and violet LLM hulls.

**Template smells.** The six-up KPI strip with micro small-caps labels, the bordered verdict chips and hero pills, the five-tint flowchart, and six cards that all follow the same formula-then-paragraph pattern.

## MUST FIX (defects)

**1. The stat strip does not carry the punchline.** Stage, x 292–821, y 322–380. Effort M.
- What is wrong:
  - The brief's pair exists here only as the group labels "Local plasticity" and "Global compression": 18.5 pt small caps in #6E65CE, the smallest type in the strip.
  - At 3 m the strip reads as six unitless 72 pt numbers. The labels are 21 pt, the descriptions 19.5 pt over two lines.
  - In the squint test, these numbers are the darkest mass below the band. The eye lands on them and learns nothing.
- Fix:
  - Make the group labels two-line headers: "Local plasticity" and "Global compression" in Fraunces SemiBold 32 pt #5445B5, each with its phrase beneath in Fraunces italic 24 pt ("one model, many positions" / "many models, one region").
  - Numbers 84 pt; labels 24 pt.
  - Descriptions on one line at 20 pt, for example: "Gemma-4-26B, personal blog (PSS)", "Qwen-Turbo, Swahili (LDS)", "GPT-5-mini, 2009 (DS)".
  - Add one shared note: "distances on the 0–1 CHES compass".
  - This also removes the "party- / family" line break and the colon/semicolon mix.
  - Net growth is about 5 mm; the hero crop in item 2 pays for it.

**2. The hero (Figure 1) labels break the owner's rules at the most-seen spot.** Stage, x 292–821, y 152–296. Effort M (mask the SVG and overlay HTML), or L (re-render).
- What is wrong:
  - Pasted matplotlib outline pills: "Progressive Left" (twice), "Authoritarian Right" and "Centrist Left". They are DejaVu Sans, in pale text: green #5FBE5C at 2.3:1 (an off-palette colour, and used on the LLM panel) and cyan #0FAFD7 at 2.6:1.
  - The "Progressive Left" pill in (b) (x 632–681, y 180–197) crosses the magenta peak's centre line at x ≈ 675.
  - The bold sans axis label "lrecon" reads as "Irecon".
  - The quadrant names (Lib-Left, Auth-Right and so on) are 1.05 to 1.31:1 contrast, effectively invisible.
  - The P₁/P₂ markers are explained nowhere.
  - Panel (b) is a pale lilac wash that reads weaker than (a) at 3 m, so "one region" is not visible.
- Fix:
  - Delete the pill, label and quadrant-name path groups from `fig1a_parties.svg` and `fig1b_llms.svg`. The pills are the white-filled rectangles with green or cyan strokes, and the label glyphs share those fills.
  - Overlay HTML labels instead: Pagella italic 20 pt, in #1F94CC on (a) and #BC45D8 on (b), with no boxes and with short curved leaders that end on each peak.
  - Axis names in Pagella italic 22 pt, with glosses ("lrecon, economic left → right"; "galtan, lib → auth").
  - Either drop P₁/P₂ or define them in the caption.
  - Crop the viewBox to the peak tops (about y 172). This frees roughly 19 mm for items 1 and 3.
  - Optional (effort L): deepen (b)'s surface to #EC8DFF at 60% or more, and draw the parties' 90% floor contour from (a) as a dashed #1F94CC outline on (b). Both panels use the same camera, so the overlay is straightforward.

**3. The thesis line is the most cramped line on the page.** Full width, y 128–150. Effort S–M.
- What is wrong:
  - The 50 pt sentence starts 5 mm below the gradient rule.
  - Its bounding box ends 0.9 mm above the box of the "1 From a Point to a Distribution" head.
  - The hero pills start 3.3 mm below its descenders, and the Whitman epigraph 2.2 mm below.
  - Above every other section head the clear space is 7.5 to 9.7 mm.
- Fix:
  - Grow the thesis row from 27 to 38 mm and centre the line optically: about 9 mm above the cap height and 10 mm below the descenders. Set it at 54 pt.
  - Fund the space from the hero crop (item 2) on the stage and the pipeline cut (item 4) in the sidebar.
  - Move the epigraph (item 24).

**4. The Measurement Framework pipeline has colliding labels.** Sidebar, x 20–122, y 490–586. Effort S (delete) or M (rebuild).
- What is wrong:
  - At 17 pt, the descenders of "Register", "Paraphrase", "Reasoning", "Language" and "Arg. Role" collide with the bold acronyms beneath them.
  - The "p" of "precondition" touches the bottom of the JBS box.
  - Most labels sit 1 mm or less from their box borders.
  - The JBS arrow runs along the top edge of the group box instead of landing into it.
  - The five fill tints and straight arrows read as a flowchart template, and the figure repeats the six axes that the cards already show at eye level.
- Fix:
  - Preferred: delete the figure, and run the §2 text, the compass key (80 mm) and the axis list at full column width. This saves about 40 mm of sidebar.
  - If you keep it: rebuild it as inline SVG with 1.25 leading, at least 2 mm of inner padding, one lavender tint, and curved arrows that end perpendicular to their targets.

**5. The MTMM matrix is below the type floor and its colour scale misleads.** Lower right, x 563–702, y 770–915. Effort M.
- What is wrong:
  - Type is below the 16 pt floor, in a poster-made chart: headers 15.2 pt, cell values 15.7 pt, legend 14.4 to 14.7 pt.
  - Values such as "−.852" fill the 18 mm cells with less than 1 mm to spare.
  - The ramp is sequential on a signed measure:
    - The strongest positive correlation (.724) is the palest cell.
    - Values near zero (−.005, .040) come out mid-purple.
    - The negatives are darkest, so near-zero cells read as strong.
  - The pale-pink +1 end borrows the LLM magenta for a metric scale.
  - The upper triangle duplicates the lower one.
  - In the grey squint test this block outranks the hero and the polytope.
- Fix:
  - Show the lower triangle only, without the diagonal (21 cells, 6 × 6).
  - Use a diverging scale with white at 0: positive towards #5445B5, negative towards #9CA3AF.
  - Values 18 pt, headers 19 pt, legend 17 pt.
  - Keep the convergent and algebraic outlines.

**6. The Grok flips are misread by proximity and use chips.** Sidebar, x 20–277, y 354–459. Effort S–M.
- What is wrong:
  - Each verdict chip sits about 29 mm from its own label and about 5 mm from the next label. The rows therefore read "Disagree Reasoning × 10" and "Completely Disagree Bangla".
  - The chips are bordered pills in off-palette red and blue (#DD405B, #3F7AD8, #E99BA9, #9CB8E7). They are the most saturated marks in the sidebar at 3 m.
  - The statement IDs S21_09 and S1_09 (16.5 pt mono) are noise for a poster reader.
- Fix:
  - Put each verdict right after its label (flex-start, 3 mm gap), and divide the two halves with a 0.22 mm vertical rule.
  - Replace the chips with a four-step Likert scale in Pagella small caps ("sd · d · a · sa"). Set the chosen step in bold #211CBF with a 0.6 mm underline and the others in #9CA3AF, so that "opposite answers" show as opposite ends of one scale.
  - Delete the IDs.

**7. The band's QR card and logo break the safe margin and the band balance.** Band, y 0–123. Effort S–M.
- What is wrong:
  - The QR card spans y 5.8–116.9, so it starts 5.8 mm from the page edge, inside the 10 mm safe zone.
  - The project logo starts at 7.4 mm and the title ascenders at about 9 mm.
  - The IUT and AACL stack spans about 17.8–105.8, so the left and right elements share neither a top line nor a bottom line, and the card looks jammed in.
  - The IUT seal sits 1.6 mm right of the plate's left edge (x 21.7 against 20.1).
- Fix:
  - Keep the 80 mm code. Trim the card's top padding from 7.9 to 5 mm and its SCAN ME zone from 23 to 14 mm, which gives a card about 100 mm tall.
  - Centre the card on the left stack's axis (y ≈ 61), so it spans y 11–111.
  - Align the seal at x 20.1.
  - Give the centre stack at least 11 mm of top clearance, either by restoring the brief's 130 mm band or by moving the emails line to the fine print.

**8. Figures 2 and 3 (pasted) break the colour rule and the type rules.** Polytope at x 18–165, y 770–940; year hulls at x 333–466, y 877–938. Effort M.
- What is wrong:
  - The LLM hulls render violet-lilac (about #B4A0FA, magenta blended through cyan), which this poster's own system reads as lavender chrome. The coverage bars right beside them are magenta.
  - Axis text is DejaVu Sans:
    - In Figure 2 the tick labels are about 7 pt and the axis names about 11 pt, and "lrgen" collides with the end of its axis.
    - In Figure 3 the ticks and labels are about 4 to 5 pt, illegible at any distance.
  - The triangulated facet mesh in Figure 2 is the busiest texture in the lower half.
- Fix:
  - Fill the LLM hulls with #EC8DFF at 45–50% with #BC45D8 edges, drawn above the cyan rather than blended under it.
  - Remove the facet edges, or set them to 15% opacity.
  - Strip the axis text from both SVGs, and overlay three Pagella italic 18 pt axis names on Figure 2.

**9. The closing line and the fine print are crushed.** Full width, y 1119–1166. Effort S–M.
- What is wrong:
  - The closing line's bounding box sits 1.8 mm under the table legend (1119.8) and the §7 bullets (1119.4), and 1.7 mm above the references (1137.3).
  - The last line of fine print ends at 1164.0, 1.9 mm above the footer gradient rule (1165.9).
  - In copy.md, *ought* is emphasised, but the line is all italic and the word was not set upright, so the emphasis is lost.
- Fix:
  - Give the closing line 8 mm of air above and below, and leave at least 5 mm between the fine print and the rule.
  - Move the Limitations paragraph into the §7 space freed by item 10, and spread the references over three columns (three lines).
  - Set "ought" upright within the italic line.

**10. The heads of §6 and §7 are 22 mm apart.** Lower block. Effort M; follows from item 5.
- What is wrong: "6 Per-Model Fingerprints" has its baseline at 962.6 and rule at 967.1; "7 Why It Matters" has its baseline at 984.5 and rule at 988.8. Heads 4 and 5 share 763.9, so the break is conspicuous. The cause is that §5 runs 22 mm longer than §4.
- Fix: the 6 × 6 triangle from item 5 saves about 18 mm, and cutting the Figure 5 caption to one line saves 8 mm. Then set §7 on §6's baseline, and use the freed space at the foot of column 3 for Limitations (item 9).

**11. Compass labels touch the dividers, and the card padding is uneven.** Cards, y 424–741. Effort S–M.
- What is wrong:
  - PSS "Gemma-4-26B" ends 1.1 mm from the vertical divider, and RSS "Gemini-2.5-FL" 0.8 mm.
  - PIS "Gemma-4-26B" ends 0.6 mm from the panel's right edge, and DS "Gemma-4-26B" 1.0 mm.
  - LDS "French" crosses the divider by 2.3 mm.
  - The compass has 3.8 mm of padding at the sides but 7.0 mm below.
- Fix:
  - Move the model-and-year key out of the plot into a centred subcaption under each compass, as the brief asks, and shrink the compass to 72 mm.
  - At minimum, inset every in-plot label at least 1.5 mm from the rules (text-anchor end near the right edges), and make the bottom padding equal to the side padding.

**12. Names and marks are inconsistent.** Effort S.
- Table headers (y ≈ 1003–1009) say "DeepSeek-v4", "Llama3-70B", "Qwen-turbo" and "Grok-4.1", and the LDS compass says "DeepSeek-v4". Elsewhere the names are "DeepSeek-V4-Flash", "Llama-3-70B", "Qwen-Turbo" and "Grok-4.1-Fast". Use one form per model.
- The flips say "Bangla" (y 424) while the LDS chart and compass say "Bengali". Pick one.
- Reference [1] reads "Proc. IJCNLP-AACL, 2026", but the logo and footer read "AACL-IJCNLP 2026".
- The IAS legend writes ".15", the table legend "0.15".
- The Figure 1 caption capitalises "Cyan" and "Magenta" mid-sentence; use lowercase.
- Spacing around ≈ varies: "≈ 0.60" against "≈0.29".

**13. The coverage-bar labels have low contrast.** x 533–547, y 806–862. Effort S.
- What is wrong: "100%" is #1F94CC on the cyan track (#D5F1FD), 2.9:1 at 16.2 pt. The row label "lrgen implied" is cryptic.
- Fix: set "100%" in #0E6E9C or ink at 17 pt, or place it just outside the end of the track. Rename the row "lrgen thickness (vol ÷ area)".

## SHOULD (clear improvements)

**14. Cut content instead of shrinking it.** Whole page. Effort L.
- What is wrong:
  - Every size is below the brief:

    | Element | Measured (pt) | Brief (pt) |
    |---|---|---|
    | Title | 100 | 110–120 |
    | Subtitle | 45 | 52–58 |
    | Authors | 31 | 38–42 |
    | Affiliation | 22.5 | 28–30 |
    | Section heads | 44 | 48–52 |
    | Sidebar body | 24 | 27 |
    | Card body | 23 | 24–25 |
    | Captions | 20–21 | 21–22 |
    | Big stats | 72 | 84–100 |

  - About 70 chart-label spans are at 16.1–16.8 pt, against the brief's 17 pt minimum.
  - There are 25 distinct sizes between 16 and 25 pt (16.1, 16.2, 16.4, 16.5, 16.8, 17.0, 17.1, 17.3, 18.0, 18.3, 18.5, ...). This is the fingerprint of fit-to-box scaling, not a type scale.
  - The clear space above section heads is 7.5 to 9.7 mm, tight for A0.
- Fix:
  - Cut: the pipeline (item 4); the MTMM upper triangle (item 5); LDS lollipop columns 2 and 3 (item 19); and the statement IDs.
  - Replace Figure 3's three 47 mm panels with one 70 mm panel overlaying the three waves: party hulls as cyan outlines, cohort hulls as magenta fills. Alternatively drop it, since the table's glyph row already shows per-wave hulls for each model.
  - Then lock a scale and stop fitting each block separately: 17 / 19 / 21 / 24 / 27 / 36 / 48 pt, with display sizes 56 / 84 / 112 pt. Allow 12 mm above each section head.

**15. Restore the one-line definitions on the cards.** Six cards. Effort M.
- What is wrong: The brief asks for "one-line definition" on each card, and copy.md has them (for example "Displacement from a neutral baseline under an altered prompt register"). The layout shows formulas instead, which a passer-by cannot parse. Six identical formula-then-paragraph cards read like a generated feature grid.
- Fix: put the plain definition first, under the card name, in Pagella italic 22 pt. Set the formula below it at 18 pt in #4B5563, or drop it.

**16. Restore the Contributions box.** Sidebar. Effort M.
- What is wrong: It is in the brief, and both earlier posters have one (HaSPeR's "Contributions" box; ACL 2023's "3 Contributions"). `box_contributions` exists in copy.md, but the layout dropped it, so the poster never says in one place what is new.
- Fix: in the space freed by item 4, add a house-style box (white small-caps title on a #6E65CE bar, #F5F5FE body) with three one-line bullets.

**17. Add a reading key next to the compasses.** §3, under the lead. Effort S.
- What is wrong: The six card compasses and the table glyphs carry no axes. The only key is in §2 (x 126–188, y 523–585), 150 to 300 mm away and not labelled as a key.
- Fix: add one line with a 12 mm mini compass: "x = lrecon (economic left → right), y = galtan (lib → auth), both 0–1". The copy already has `compass_caption` for this.

**18. Make the RSS mini-chart readable.** RSS card, x 322–337, y 604–625. Effort M.
- What is wrong: The chain-of-thought and direct hulls form a tangle about 15 mm across at the divider, and the reader cannot tell which hull is which. The ∞ marks in the waffle are 13.6 pt.
- Fix:
  - Add a ×3 magnifier, as on the DS card.
  - Show direct as hollow points with a dashed outline, and chain-of-thought as filled points with a solid hull, each labelled at its hull.
  - Add a corner key like the DS card's "hollow start, solid end".
  - Set the ∞ marks at 16 pt.

**19. Simplify the LDS lollipops.** LDS card, x 647–818, y 603–628. Effort M.
- What is wrong: Three columns stand on three independent baselines. Only 5 of the 12 values are printed. The deep against pale magenta is not explained, and the card text calls the lollipops "bars".
- Fix: keep the four largest with their values, and replace columns 2 and 3 with one line: "eight others: 0.15–0.21". Change "(bars)" to "(right)".

**20. Give the IAS dumbbell an axis title.** IAS card, x 571–705, y 658–735. Effort S.
- What is wrong: The 4.2–4.8 axis has no title. Hollow against solid means for against against here, but start against end on the DS card beside it. The names are ragged by about 2 mm because the logos differ in width.
- Fix: add the axis title "judge score (1–5)" at 17 pt, set "○ for ● against" as a column head, and give the logos a fixed-width slot.

**21. Prevent a misread of Figure 2.** Caption, x 24–160, y 913–938. Effort S.
- What is wrong: The pooled LLM hull looks about a quarter of the party hull, while the bars beside it say 2.56%.
- Fix: add one sentence: "A single model's hull is only 1.55–4.11% of the outer volume (bars)." This contrasts the two figures without captioning the polytope with 2.56%.

**22. Stop the mono and math faces leaking into the text.** Whole page. Effort S–M.
- What is wrong:
  - JetBrains Mono accounts for 239 of the 693 text spans (34%): years, "×10, 2009", the IDs, axis names in the keys and coverage labels, "PC1".
  - The same variables appear as italic Pagella in the body and the table note.
  - MathJax sets formulas and inline numbers in Computer Modern, a fourth text face. In one §5 sentence, "|r| ≤ 0.21" sits beside Pagella "0.724".
- Fix:
  - Keep mono for table and chart numerals only. Set years and variable names in Pagella, with variables in italic.
  - Use MathJax 4 with its Pagella font, or set inline numbers as plain text.

## COULD (taste)

**23. Re-break the subtitle.** Band, y 41–77. Effort S.
- What is wrong: The break "…in the Political / Behavior of LLMs…" splits a noun phrase.
- Fix: break after "Behavior". The lines become about 368 and 329 mm, and both fit the 509 mm centre column.

**24. Move the epigraph out of the hero.** Stage, x 704–821, y 152–186. Effort S.
- What is wrong: It floats in panel (b)'s airspace, 2.2 mm under the thesis line, and reads as a figure annotation.
- Fix: move it to the head of the sidebar, as the brief places it, or right-align it inside the enlarged thesis row at 18 pt.

**25. Polish.** Effort S.
- The point-to-shape arrow ends about 3 mm short of the right compass (tip at x ≈ 189, edge at 192). Make the gap 1 mm or less.
- Names under Evaluated Models are ragged by 4 mm (x 28.7 / 31.0 / 32.7). Use a fixed 7 mm logo slot.
- §5 opens with a fragment ("As distinct facets of one phenomenon.") and ends with a one-word line ("denominator."). Write "Yes, as distinct facets…" and rewrap.
- The "—" in the RSS row of the table is unexplained. Add "— undefined (direct PIS = 0)" to the table note.
- Corner radii differ: AACL plate 2 mm, QR card about 5 mm, boxes 1.2 mm, cards 1.4 mm. Use 2 mm for both band plates.

## Protect

Keep all of the following through further edits:
- The house skeleton: the solid band with faint contours, the gradient hairlines, the centred numbered heads over grey rules, the small-caps box bars and the heart footer.
- The IUT lockup and AACL plate as rendered, and the QR code with its centred logo.
- The three-column grid. The cards and lower blocks sit on the column edges to within 0.3 mm.
- The colour semantics of the poster-made charts. The coverage bars are the best chart on the page: drawn to scale, with a cyan party track, a magenta cohort bar, per-model ticks and a proper key. The monoculture dumbbells come close behind.
- The point-to-shape mini figure, the DS magnifier inset, the table's row of hull glyphs, the instrument-to-metric map in §7 and the Bangla excerpt.
- The bookend of thesis line and closing line in Fraunces italic.

No fix should add boxes, tints or new colours.
