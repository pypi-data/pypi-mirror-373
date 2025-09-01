import traceback

import adagenes as ag


class RandomVariantFilter():

    def process_data(self, bframe, number:int, same_positions=False):
        """
        Returns variants that are annotated with a specific feature

        :param bframe:
        :param number:
        :return:
        """
        if isinstance(bframe, dict):
            bframe = ag.BiomarkerFrame(data=bframe)
        biomarker_data = bframe.data

        positions = []

        i = 0
        biomarker_data_new = {}
        if bframe.is_sorted is False:
            for var in biomarker_data:
                if i < number:
                    biomarker_data_new[var] = biomarker_data[var]
                i += 1
        else:
            new_sorted = []
            for var in bframe.sorted_variants:
                if i < number:
                    biomarker_data_new[var] = biomarker_data[var]

                    if same_positions is False:
                        try:
                            chr, ref_seq, pos, ref, alt = ag.parse_genome_position(var)
                            if pos is not None:
                                if pos not in positions:
                                    new_sorted.append(var)
                                    positions.append(pos)
                        except:
                            print(traceback.format_exc())

                    new_sorted.append(var)
                i += 1
            bframe.sorted_variants = new_sorted
        bframe.data = biomarker_data_new

        return bframe

