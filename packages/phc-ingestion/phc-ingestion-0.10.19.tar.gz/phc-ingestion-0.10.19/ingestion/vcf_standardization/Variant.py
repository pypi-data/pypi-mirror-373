from ingestion.vcf_standardization.util.af_helpers import try_move_af_value, try_calculate_af
from ingestion.vcf_standardization.util.dp_helpers import (
    try_move_dp_value,
    try_afdp_to_dp,
    try_calculate_dp_from_ad,
)


class Variant:
    def __init__(self, fields):
        self.chr = fields[0]
        self.pos = fields[1]
        self.rsid = fields[2]
        self.ref = fields[3]
        self.alt = fields[4]
        self.qual = fields[5]
        self.filt = fields[6]
        self.info = {x.split("=")[0]: x.split("=")[1] for x in fields[7].split(";") if "=" in x}
        self.frmt = fields[8].split(":")
        self.smpl = fields[9].split(":")
        self.ad_af_dp: dict[str, bool | str] = {"AD": False, "AF": False, "DP": False}

    def standardize_allele_frequency(self, log):
        # Detect if allele frequency is present either in the INFO or FORMAT/SAMPLE fields
        for k, v in self.info.items():
            if k in ["af", "AF"]:
                # Cast to float, update dict, and remove old entry
                new_entry = "{:.4f}".format(float(v))
                self.info.pop(k)
                self.info.update({"AF": new_entry})

                # Replace with standardized AF
                self.ad_af_dp["AF"] = new_entry
                break

        # If AF is not present in INFO, check FORMAT/SAMPLE fields
        if not self.ad_af_dp["AF"]:
            self = try_move_af_value(self)

            # Last resort, calculate AF from AD
            if not self.ad_af_dp["AF"] and self.ad_af_dp["AD"]:
                self = try_calculate_af(self)

        return self

    def standardize_depth(self, log):
        # Check for depth in FORMAT, if there, all is good
        for entry in zip(self.frmt, self.smpl):
            if entry[0] == "DP":
                self.ad_af_dp["DP"] = entry[1]
                break

        if not self.ad_af_dp["DP"]:
            # search for DP or depth in INFO, move to FORMAT/SAMPLE
            self = try_move_dp_value(self)

            # search for AFDP in FORMAT
            if not self.ad_af_dp["DP"]:
                self = try_afdp_to_dp(self)

                # Last resort, calculate DP from AD
                if not self.ad_af_dp["DP"] and self.ad_af_dp["AD"]:
                    self = try_calculate_dp_from_ad(self)

        return self

    def standardize_allelic_depth(self, log):
        if not self.ad_af_dp["AD"] and self.ad_af_dp["AF"] and self.ad_af_dp["DP"]:
            alt_depth = round(float(self.ad_af_dp["DP"]) * float(self.ad_af_dp["AF"]))
            ref_depth = int(self.ad_af_dp["DP"]) - alt_depth
            ad = f"{ref_depth},{alt_depth}"
            self.ad_af_dp["AD"] = ad
            self.frmt.append("AD")
            self.smpl.append(ad)

        return self

    def standardize_genotype(self, log):
        if not "GT" in self.frmt and self.ad_af_dp["AF"]:
            gt = "1/1" if float(self.ad_af_dp["AF"]) > 0.9 else "0/1"
            self.frmt.append("GT")
            self.smpl.append(gt)

        return self

    def add_vendsig(self, vendsig_dict, log):
        # Add VENDSIG to INFO
        vendor = vendsig_dict.get("vendor", "")
        if not vendor:
            return self

        if vendor == "caris":
            vendsig_lookup = vendsig_dict.get(
                f"{self.chr}:{self.pos}:{self.ref}:{self.alt}", "Unknown"
            )
            self.info.update({"VENDSIG": vendsig_lookup})

        elif vendor == "foundation":
            var_gene_id = self.info.get("gene_name")
            var_depth = self.info.get("depth")
            vendsig_lookup = vendsig_dict.get(f"{var_gene_id}:{var_depth}", "Unknown")
            self.info.update({"VENDSIG": vendsig_lookup})

        return self

    def prune_var(self, log):
        # Pruning FORMAT to only include GT, AD, and DP values.
        # Pruning VARIANT column to only include the corresponding values.
        # Pruning INFO column to only include AF and VENDSIG values.
        zipped = dict(zip(self.frmt, self.smpl))
        frmt_smpl_dict = {frmt: smpl for frmt, smpl in zipped.items() if frmt in ["GT", "AD", "DP"]}
        self.frmt = list(frmt_smpl_dict.keys())
        self.smpl = list(frmt_smpl_dict.values())
        self.info = {k: v for k, v in self.info.items() if k in ["AF", "VENDSIG"]}

    def reassemble_variant(self):
        # Reassemble variant into string
        updated_variant = "\t".join(
            [
                self.chr,
                self.pos,
                self.rsid,
                self.ref,
                self.alt,
                self.qual,
                self.filt,
                ";".join([f"{k}={v}" for k, v in self.info.items()]),
                ":".join(self.frmt),
                ":".join(self.smpl),
            ]
        )
        return updated_variant

    @classmethod
    def check_formatting(cls, var: str):
        # Loose formatting check, return as Variant class object
        split_var = var.split("\t")
        if len(split_var) < 8 or not split_var[1].isdigit():
            raise RuntimeError(f"Variant contains incorrect number, or invalid fields:  {var}")

        if len(split_var) == 8:
            split_var.append(".")  # Add placeholder for FORMAT
            split_var.append(".")  # Add placeholder for SAMPLE

        elif len(split_var) == 9:
            split_var.append(".")  # Add placeholder for SAMPLE

        working_variant = cls(split_var)
        return working_variant
