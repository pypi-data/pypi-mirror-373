import pandas as pd
import os
import re
import numpy as np
from pprint import pprint
from Bio.Data.IUPACData import protein_letters_1to3_extended as PROTEIN_LETTERS_1TO3


def get_paeruginosa_polymorphisms(input_xls: str):
    xls = input_xls
    xls.sheet_names
    data_wp = pd.read_excel(xls, "with polymorphisms")
    data_wop = pd.read_excel(xls, "without polymorphisms")

    # Select columns
    gene_cols = [i for i in data_wp if i.startswith("PA")]
    id_vars = ["ISOLATE ID", "ST"]
    selected_cols = id_vars + gene_cols

    data_wp = data_wp[selected_cols]
    data_wop = data_wop[selected_cols]

    # wide to long
    data_wp_long = pd.melt(data_wp, id_vars=id_vars, value_vars=selected_cols, var_name="locus_gene", value_name="muts_wp")
    data_wop_long = pd.melt(
        data_wop, id_vars=id_vars, value_vars=selected_cols, var_name="locus_gene", value_name="muts_wop"
    )

    # Merge
    merged_data = pd.merge(data_wp_long, data_wop_long, on=["ISOLATE ID", "ST", "locus_gene"], how="left")
    merged_data = merged_data[~merged_data["muts_wp"].isna()]

    # Extract locus and gene
    merged_data["locus_tag"] = merged_data["locus_gene"].str.extract("(PA\d+).+")
    merged_data["gene"] = merged_data["locus_gene"].str.extract("PA\d+(.+)")
    merged_data["locus_tag"] = merged_data["locus_tag"].str.strip()
    merged_data["gene"] = merged_data["gene"].str.strip()

    # For each row get which mutations are polymorphisms and which are not
    def find_poly_muts(row):
        def split_muts(s):
            if s is np.nan or s == "" or s is None:
                return []
            else:
                return [i.strip() for i in s.split(",")]

        def transform_aa_codes(mut, tran=PROTEIN_LETTERS_1TO3):
            matches_substitution = re.match("^[A-Z]\d+[A-Z]$", mut)
            matches_deletion = re.match("^(aa|nt)\d+∆(\d+|\D+)$", mut)
            matches_insertion = re.match("^(aa|nt)\d+Ins(\d+|\D+)$", mut)
            if matches_substitution:
                ref_aa, pos, new_aa = re.findall("(^[A-Z])(\d+)([A-Z]$)", mut)[0]
                return f"{tran[ref_aa]}{pos}{tran[new_aa]}"
            elif matches_deletion:
                mut_type, pos, value = re.findall("^(aa|nt)(\d+)∆(\d+|\D+)$", mut)[0]
                # print(f"Matched deletion: {mut} pos={pos} change={value} type={mut_type}")

                # -- Expected in snippy --
                # frameshift deletion snippy (frameshift) = p.Val82fs | c.240_247delGCCGGCCA 
                # conservative inframe deletion snippy (not frameshift) = p.Ser912_Glu913del | p.Ile15del | c.43_45delATC
                # disruptive inframe deletion snippy (not frameshift) = p.Ala44_Ala45del | p.Gln103del | c.308_310delAGC

                # WARNING NO TRANSFORMATION PERFORMED
                return mut
            elif matches_insertion:
                mut_type, pos, value = re.findall("^(aa|nt)(\d+)Ins(\d+|\D+)$", mut)[0]
                # print(f"Matched insertion: {mut} pos={pos} change={value} type={mut_type}")

                # -- Expected in snippy --
                # frameshift insertion snippy (frameshift) = p.Ala348fs | c.1205_1206insC | c.398dupC | c.613_616dupAAGA 
                # conservative inframe insertion snippy (not frameshift) = p.Asp577_Arg582dup | p.Gly1060_Trp1061insGluGly | c.3175_3180dupGAGGGC
                # disruptive inframe insertion snippy (not frameshift) = p.Phe438_Gly440dup | p.Leu331_Ala332insValLeu | c.989_994dupTGCTGG

                # WARNING NO TRANSFORMATION PERFORMED
                return mut

            elif mut=="DELETED":
                # WARNING NO TRANSFORMATION PERFORMED
                return mut
            else:
                print(f"Did not adapt mutation: {mut}")
                # WARNING NO TRANSFORMATION PERFORMED
                return mut

        muts_wp = [transform_aa_codes(i) for i in split_muts(row["muts_wp"]) if i]
        muts_wop = [transform_aa_codes(i) for i in split_muts(row["muts_wop"]) if i]

        poly = []
        nonpoly = []
        for i in muts_wp:
            if i in muts_wop:
                nonpoly.append(i)
            else:
                poly.append(i)

        row["poly_muts"] = poly
        row["nonpoly_muts"] = nonpoly
        return row


    merged_data = merged_data.apply(find_poly_muts, axis=1)

    polymorphisms_d = {}
    for row in merged_data[["locus_tag", "poly_muts"]].to_dict("records"):
        lt = row["locus_tag"]
        plms = row["poly_muts"]
        for plm in plms:
            if polymorphisms_d.get(lt):
                polymorphisms_d[lt] = {*polymorphisms_d[lt], *{plm}}
            else:
                polymorphisms_d[lt] = {plm}
    # pprint(d, compact=True, width=150)

    return merged_data, polymorphisms_d


# merged_data, polymorphisms_d = get_paeruginosa_polymorphisms(pd.ExcelFile("/home/usuario/Proyectos/Results/tests/polimorfismos_carla/1-s2.0-S1198743X21002330-mmc3.xlsx"))

# merged_data.groupby(["locus_tag", "ST"], dropna=False, group_keys=True)[
#     ["ISOLATE ID", "muts_wp", "poly_muts", "nonpoly_muts"]
# ].apply(lambda x: x).to_excel("/home/usuario/Proyectos/Results/test.xlsx")



# Polymorphisms (obtained from get_paeruginosa_polymorphisms function)
# ONLY SUBSTITUTIONS ARE ADAPTED TO SNIPPY
PAERUGINOSA_POLYMORPHISMS = {
 'PA0004': {'Ile769Val', 'His148Asn'},
 'PA0424': {'Val132Met', 'Ala103Thr', 'Val132Ala', 'Ala103Gly', 'Val126Glu'},
 'PA0425': {'Asp373Asn', 'Val286Ile', 'Asp373Glu'},
 'PA0426': {'Glu845Asp', 'Ile745Val', 'Glu429Asp', 'Val1014Ile', 'Gly957Asp', 'Ile186Val', 'His525Asn', 'Asn312Ser', 'Asn248Lys'},
 'PA0427': {'Val72Leu', 'Asp448Asn', 'Ala261Thr', 'Ala478Thr', 'Thr477Ser'},
 'PA0807': {'Ala196Val', 'Ala208Val', 'Ala219Thr', 'Ala51Thr', 'Arg182Cys', 'Arg66Cys', 'Arg66Gly', 'Asp197Glu', 'Asp235Gly', 'Asp75Gly', 'Ile171Val',
            'Ile67Thr', 'Lys63Glu', 'Thr40Ile', 'Val19Met'},
 'PA0958': {'nt1206InsC', 'Val127Leu'},
 'PA1798': {'Ala115Glu', 'Ala293Val', 'Ala82Thr', 'Arg243His', 'Arg356Leu', 'Arg421Cys', 'Glu343Asp', 'His398Arg', 'Ser352Ile', 'Thr131Pro',
            'Tyr407His', 'Val146Ala', 'Val295Ile', 'Val304Ile', 'Val313Ile', 'Val327Leu'},
 'PA1799': {'Leu153Arg', 'Leu58Arg', 'Ala44Ser', 'Ala41Gly', 'Met160Thr', 'Ser170Asn', 'Thr135Ala', 'Arg34His', 'Ala129Thr'},
 'PA2018': {'Arg1033Leu', 'Arg722Ser', 'Arg786His', 'Asn1036Thr', 'Asp428Asn', 'Gln1039Arg', 'Gln282Arg', 'Gln840Glu', 'Gln843Pro', 'Glu152Asp',
            'Gly1035Asp', 'Gly589Ala', 'Ile536Val', 'Leu984Phe', 'Phe29Ser', 'Pro1032Ser', 'Thr543Ala', 'Thr742Ile', 'Tyr181Asp', 'Val980Ile'},
 'PA2019': {'Ala113Thr', 'Ala27Thr', 'Ala30Thr', 'Ala36Thr', 'Ala375Pro', 'Ala383Pro', 'Arg151His', 'Arg282Cys', 'Arg351Ser', 'Asp135Tyr',
            'Asp346His', 'Gln4His', 'Gly344Asp', 'His119Tyr', 'Leu12Pro', 'Leu22Met', 'Leu331Met', 'Leu331Val', 'Leu389Gln', 'Lys329Gln', 'Ser320Ala',
            'Ser382Gly', 'Trp358Arg', 'Val309Ile', 'Val44Ile'},
 'PA2020': {'Ala35Val', 'Arg200Ser', 'Asn186Ser', 'Asp83Glu', 'Gly89Ser', 'Leu128Met', 'Leu138Arg', 'Leu174Gln', 'Leu196Ile', 'Lys131Arg',
            'Ser44Phe'},
 'PA2023': {'Lys236Thr'},
 'PA2491': {'Ala175Val', 'Ala75Val', 'Arg108Cys', 'Asp249Asn', 'Glu181Asp', 'Gly212Asp', 'Leu186Phe', 'Lys17Thr', 'Ser289Thr', 'Val318Ile',
            'Val73Ala'},
 'PA2492': {'Phe172Ile', 'Ala299Thr', 'Met7Val', 'Pro60Ser', 'Glu26Gly'},
 'PA2493': {'Ala231Thr', 'Ala27Val', 'Ala383Gly', 'Ala407Val', 'Ala79Gly', 'Asp353Glu', 'Asp370Glu', 'Gln368Arg', 'Glu2Val', 'Pro397Gln', 'Ser22Gly',
            'Ser403Thr', 'Ser8Phe', 'Thr285Ile'},
 'PA2494': {'Gln788Arg', 'Ala843Thr', 'Asp230Ala', 'Ala598Glu', 'Phe509Val', 'Asp666Glu'},
 'PA2495': {'Ala140Thr', 'Ala360Thr', 'Ala38Thr', 'Ala410Ser', 'Ala4Thr', 'Arg150His', 'Gly16Ser', 'Leu15Val', 'Ser13Pro', 'Ser77Asn', 'Thr275Ser',
            'Thr34Pro', 'Thr34Ser'},
 'PA3047': {'Met85Val', 'Ala358Val', 'Ala474Thr', 'Ala394Pro', 'Gln212Lys', 'Gln156His'},
 'PA3168': {'aa911∆2', 'Gly897Asp', 'Ser912Ala', 'Asp652Tyr', 'Thr847Ala', 'Gly889Arg'},
 'PA3574': {'Gly206Ser', 'Asp187His', 'Asn130Ser'},
 'PA3721': {'Gln182Lys', 'Asp79Glu', 'Ser209Arg', 'Pro210Leu', 'Ala186Thr', 'Glu153Gln', 'Gly71Glu', 'Ala145Val', 'Leu206Val'},
 'PA3999': {'Ala363Gly', 'Thr286Ser', 'Val50Ile', 'Val29Ile'},
 'PA4020': {'Ala286Val', 'Ala303Val', 'Arg322Gln', 'Asp351Gly', 'Asp411Ala', 'Met297Leu', 'Met297Val', 'Ser306Arg', 'Val124Ile', 'Val358Ile',
            'X452ext'},
 'PA4109': {'Ala10Ser', 'Ala175Thr', 'Ala51Thr', 'Arg244Trp', 'Glu114Ala', 'Gly231Ser', 'Gly283Glu', 'His209Tyr', 'Ile251Val', 'Leu113Gln',
            'Met288Arg', 'Met61Leu', 'Ser179Thr'},
 'PA4110': {'Ala156Val', 'Ala170Thr', 'Ala36Thr', 'Ala55Thr', 'Ala97Val', 'Arg235His', 'Arg273Lys', 'Arg284His', 'Arg5Gly', 'Arg79Gln', 'Gln117Glu',
            'Gln117Leu', 'Gln155Arg', 'Glu198Lys', 'Gly129Ser', 'Gly229Ser', 'Gly27Asp', 'Gly391Ala', 'Gly391Pro', 'Ile365Val', 'Leu176Arg',
            'Leu200Ile', 'Phe19Leu', 'Pro23Ser', 'Pro274Leu', 'Pro274Thr', 'Pro7Ser', 'Ser173Arg', 'Ser254Asn', 'Thr105Ala', 'Thr21Ala', 'Val205Leu',
            'Val356Ile'},
 'PA4266': {'Ile186Val', 'Lys496Arg'},
 'PA4418': {'Leu3Val', 'Thr514Ser', 'Thr91Ala', 'Ser455Phe', 'Ala139Ser', 'Ala481Ser', 'Asn117Ser'},
 'PA4522': {'Ala134Val', 'Ala136Val', 'Ala29Thr', 'Ala85Gly', 'Arg11Leu', 'Asp183Tyr', 'Asp28Gly', 'Gln44His', 'Gln44Lys', 'Glu170Gly', 'Glu68Asp',
            'Gly148Ala', 'Pro126Gln', 'Ser175Leu'},
 'PA4597': {'Ala14Val', 'Ala152Thr', 'Ala163Thr', 'Ala260Val', 'Ala30Val', 'Ala372Val', 'Ala40Gly', 'Ala48Val', 'Arg263Gln', 'Arg263Trp', 'Asp351Ala',
            'Asp35His', 'Asp68Gly', 'Gln267Arg', 'Gly120Ser', 'Gly184Ser', 'Leu250Phe', 'Leu291Phe', 'Leu81Ile', 'Lys413Met', 'Met69Val', 'Phe6Leu',
            'Ser176Gly', 'Ser264Asn', 'Thr323Ser', 'Thr376Ala', 'Thr376Ser', 'Val146Ile'},
 'PA4598': {'Ala1039Thr', 'Ala1039Val', 'Ala155Thr', 'Ala536Ser', 'Ala566Thr', 'Ala566Val', 'Ala647Val', 'Ala734Val', 'Ala748Val', 'Ala958Ser',
            'Ala959Ser', 'Arg540Gly', 'Asn669Asp', 'Gln149His', 'Glu257Gln', 'Glu314Asp', 'Glu314Gln', 'Glu602Lys', 'Glu650Gln', 'Ile610Val',
            'Ile703Val', 'Ile960Leu', 'Ile982Val', 'Lys1031Arg', 'Lys804Arg', 'Lys863Gln', 'Ser1040Thr', 'Ser281Leu', 'Ser606Leu', 'Ser845Ala',
            'Ser896Thr', 'Thr304Ala', 'Thr87Ser', 'Val343Ala', 'Val364Leu', 'Val384Leu', 'Val434Ala', 'Val523Ala', 'Val607Ala', 'Val660Ile',
            'aa1027InsLLS'},
 'PA4599': {'Ala262Glu', 'Ala277Thr', 'Ala31Val', 'Ala378Thr', 'Ala384Val', 'Ala49Val', 'Arg76Gln', 'Arg76Gly', 'Asp226Glu', 'Asp298Ala', 'Gln300Arg',
            'Gln381Leu', 'Glu251Gln', 'Glu26Ala', 'Glu347Lys', 'His310Arg', 'Ile133Val', 'Met34Ile', 'Pro351Leu', 'Pro383Ser', 'Pro47Ser',
            'Ser157Thr', 'Ser313Gly', 'Ser330Ala', 'Ser341Ala', 'Thr175Ala'},
 'PA4600': {'Ile149Leu', 'Arg21His', 'Arg82Leu', 'Asp56Gly', 'Ala170Thr', 'His109Tyr'},
 'PA4776': {'Asp61Glu', 'Leu71Arg', 'Glu131Asp'},
 'PA4777': {'Ala119Thr', 'Ala413Thr', 'Ala462Thr', 'Ala4Thr', 'Asp70Asn', 'Gly362Ser', 'Gly68Ser', 'His311Gln', 'His340Arg', 'Pro369Ala', 'Pro369Ser',
            'Ser2Pro', 'Tyr345His', 'Val15Ile', 'Val6Ala'},
 'PA4964': {'Ala587Thr', 'Asn633Ser', 'Asp754Asn', 'Gln359Arg', 'Gln405Arg', 'Glu225Asp', 'Glu513Asp', 'His262Gln', 'Pro752Thr', 'Ser197Leu',
            'Ser331Thr', 'Val419Leu', 'Val646Leu'},
 'PA4967': {'Ala473Val', 'Val200Met', 'Asp142Asn', 'His50Tyr', 'Asp533Glu', 'Ile57Val'},
 'PA5471': {'Ala245Val', 'Ala352Val', 'Arg204Cys', 'Arg302Cys', 'Arg322His', 'Arg322Ser', 'Asn238Ser', 'Asp104Glu', 'Asp119Glu', 'Asp159Ala',
            'Asp161Gly', 'Asp207Asn', 'Cys40Arg', 'Glu307Asp', 'Gly157Asp', 'Gly258Ser', 'His182Gln', 'Ile237Val', 'Ile346Val', 'Leu196Pro',
            'Leu88Pro', 'Pro244Leu', 'Ser112Asn', 'Ser314Asn', 'Val242Met', 'Val243Ala'},
 'PA5485': {'Val89Asp', 'Val40Ile', 'Arg189His', 'Phe9Ile', 'Thr258Ala', 'Gln110Arg'}
}











