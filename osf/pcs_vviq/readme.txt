Data were analyzed on R version 4.2.2. R Studio version 2022.12.0+353 (2022.12.0+353)
Packages info: generate with sessionInfo()  R version 4.2.2 (2022-10-31)Platform: aarch64-apple-darwin20 (64-bit)Running under: macOS Ventura 13.5.2Matrix products: defaultLAPACK: /Library/Frameworks/R.framework/Versions/4.2-arm64/Resources/lib/libRlapack.dyliblocale:[1] en_US.UTF-8/en_US.UTF-8/en_US.UTF-8/C/en_US.UTF-8/en_US.UTF-8attached base packages:[1] stats     graphics  grDevices utils     datasets  methods   base     other attached packages: [1] osfr_0.2.9         psych_2.2.9        effectsize_0.8.3   bfrr_0.0.0.9000    cocor_1.1-4        ggside_0.2.2       [7] scales_1.2.1       ggstatsplot_0.11.1 ggpubr_0.5.0       writexl_1.4.2      readxl_1.4.2       lubridate_1.9.2   [13] forcats_1.0.0      stringr_1.5.0      dplyr_1.1.2        purrr_1.0.1        readr_2.1.4        tidyr_1.3.0       [19] tibble_3.2.1       ggplot2_3.4.2      tidyverse_2.0.0           

Data, Code and Figures are present in the Data and Code folder. 

- Raw data (Qualtrics output with participants identifiers removed): 
1) Exp 1: SWASH/VVIQ: "SWASH_VVIQ_raw.xlsx"
PCS/VVIQ: "PCS_VVIQ_raw.xlsx"
2) Exp 2: SWASH: "aph_swash_raw.xlsx"
PCS: "aph_pcs_raw.xlsx"

These data contain:
PC or SWASH items: 1) Hand lowering, 2) moving hands together, 3) mosquito hallucination, 4) sweet, 5) sour, 6) arm rigidity, 7) arm immobilization, 8) music hallucination, 9) negative visual hallucination, 10) amnesia, 11) Urge for post-session 12) amnesia for post-session.
"Taste" and "Posthypnotic" items/column that are used to calculate mean SWASH and mean PCS are not present, but each is generated from the combination of two responses. Specifically, "Taste" is the mean of the responses to the items "sweet" and "sour", corresponding to the ‘SweetSubRating’ and ‘SourSubRating’ columns. "Posthypnotic" is the geometric mean of the items urge and amnesia for post session, corresponding to the ‘PostHypnoticSub1’ and ‘PostHypnoticSub2’ columns. (See "Scripts" section). The PCS and SWASH scoring is described at https://osf.io/4x25a/VVIQ: 16 items: items numeration follows the standard order in which the VVIQ questionnaire is presented. Please follow this link which briefly describes items order https://doi.org/10.1037/t05959-000 by the main author of the questionnaire and the following link which provides all the questionnaire items in the order they are presented to participants: https://www.papersurvey.io/templates/142/vividness-of-visual-imagery-questionnaire-vviq.pdf
Other data: Demographics, consisting of Age and Gender columns. 

- Scripts: please run the scripts following the order below.
1) Step 1: Script to preprocess data: "preprocdata.Rmd"
This script calculates posthypnotic and taste items for swash and pcs, mean vviq, mean swash, mean pcs, generates the 3 groups factor (blinded aphantasics, non-aphantasics, self-reported aphantasics), and the experiment factor (1 and 2). It produces two sets of excel files that are used in the main script. 

2) Step 2: Script to run main analyses: "PCImg_share_fin_2.Rmd"
This script runs all statistical analyses reported in the manuscript: linear model, BF, t-tests. It also calculates demographics variables and descriptives for the measures of interest. Finally, it produces the figures presented in main manuscript.

3) Step 3: Script "Supplementary.Rmd" to run analyses and produce figures presented in Supplementary Material. 

