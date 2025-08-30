def try_move_af_value(self):
    # Relocate and transform AF from the FORMAT section to the INFO section for each variant
    zipped = dict(zip([i.upper() for i in self.frmt], self.smpl))
    af = float(zipped.get("AF", False))
    if not af:
        af = float(zipped.get("VF", False))
        if not af:
            return self

    self.info.update({"AF": "{:.4f}".format(af)})
    self.ad_af_dp["AF"] = "{:.4f}".format(af)
    return self


def try_calculate_af(self):
    # Recalculate AF values from AD, includes biallelic/multiallelic handling for future decomposition
    # i.e. chr8	127790148	.	CTTT	C,CT	7243.73	.	SOR=0.309	GT:AD:DP	1/2:5,189,62:256
    ad_split = self.ad_af_dp["AD"].split(",")

    afs = []
    # Start at the first REF allele
    for ad in ad_split[1:]:
        if ad == "0":
            af = 0.0
        else:
            af = float(int(ad) / sum([int(i) for i in ad_split]))
        afs.append("{:.4f}".format(af))

    self.info.update({"AF": "{:.4f}".format(af)})
    self.ad_af_dp["AF"] = "{:.4f}".format(af)

    return self
