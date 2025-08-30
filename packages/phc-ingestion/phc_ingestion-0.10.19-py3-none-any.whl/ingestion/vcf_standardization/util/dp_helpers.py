def try_move_dp_value(self):

    # Info section -> get depth or dp
    depth = self.info.get("depth", False)
    if not depth:
        depth = self.info.get("DP", False)
        if not depth:
            return self

    self.frmt.append("DP")
    self.smpl.append(depth)
    self.ad_af_dp["DP"] = depth
    return self


def try_afdp_to_dp(self):
    # Rename AFDP to just DP in FORMAT for each variant
    for entry in zip(self.frmt, self.smpl):
        if entry[0] == "AFDP":
            self.frmt[self.frmt.index("AFDP")] = "DP"
            self.ad_af_dp["DP"] = entry[1]
            break
    return self


def try_calculate_dp_from_ad(self):
    depth = str(sum([int(i) for i in self.ad_af_dp["AD"].split(",")]))
    self.frmt.append("DP")
    self.smpl.append(depth)
    self.ad_af_dp["DP"] = depth
    return self
