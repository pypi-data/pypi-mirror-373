import re


def is_frameshift_ins(var):
    # Try HGVS notation
    isinframe = frameshift_ins_hgvs(var)

    if isinframe != "":
        return isinframe

    # Try VCF notation
    isinframe = frameshift_ins_vcf(var)
    return isinframe


def is_frameshift_del(var):

    # Try HGVS notation
    isinframe = frameshift_del_hgvs(var)

    if isinframe != "":
        return isinframe

    # Try VCF notation
    isinframe = frameshift_del_vcf(var)
    return isinframe

def frameshift_del_vcf(var):
    pattern = re.compile(r'(chr[0-9|X|Y]+):([0-9]+)([A|G|C|T]+)>([A|C|T|G]+)')
    match = pattern.search(var)
    if not match:
        # raise ValueError("Invalid insertion identifier format")
        print("invalid deletion identifier (vcf: ", var)
        return ""
    ref = match.group(3)
    alt = match.group(4)

    num_nucleotides = len(ref) -1

    if num_nucleotides % 3 == 0:
        isinframe = "in-frame"
    else:
        isinframe = "frameshift"

    #print("VCF: ",isinframe,": ",num_nucleotides,": ",ref)
    return isinframe

def frameshift_del_hgvs(var):
    # Regular expression to match the insertion format
    pattern = re.compile(r'del([A-Za-z0-9_]?)')

    # Find the insertion part
    match = pattern.search(var)
    if not match:
        #raise ValueError("Invalid insertion identifier format")
        #print("invalid deletion identifier: ", var)
        return ""

    insertion = match.group(1)

    # Check if the insertion is defined as letters or numbers
    if insertion.isdigit():
        # If it's a number, it represents the number of nucleotides directly
        num_nucleotides = int(insertion)
    elif '_' in insertion:
        # If it's a range, calculate the number of nucleotides
        start, end = map(int, insertion.split('_'))
        num_nucleotides = end - start + 1
    else:
        # If it's letters, calculate the number of nucleotides
        num_nucleotides = len(insertion)

    # Check if the number of nucleotides is divisible by 3
    if num_nucleotides % 3 == 0:
        isinframe = "frameshift"
    else:
        isinframe = "in-frame"

    return isinframe

def frameshift_ins_vcf(var):
    pattern = re.compile(r'(chr[0-9|X|Y]+):([0-9]+)([A|G|C|T]+)>([A|C|T|G]+)')
    match = pattern.search(var)
    if not match:
        # raise ValueError("Invalid insertion identifier format")
        #print("invalid insertion identifier (vcf: ", var)
        return ""
    ref = match.group(3)
    alt = match.group(4)

    num_nucleotides = len(alt) -1
    #print("ins ",alt)

    if num_nucleotides % 3 == 0:
        isinframe = "in-frame"
    else:
        isinframe = "frameshift"

    #print("VCF: ",isinframe,": ",num_nucleotides,": ",ref)
    return isinframe


def frameshift_ins_hgvs(var):
    # Regular expression to match the insertion format
    pattern = re.compile(r'ins([A-Za-z0-9_]?)')

    # Find the insertion part
    match = pattern.search(var)
    if not match:
        # raise ValueError("Invalid insertion identifier format")
        #print("invalid insertion identifier: ", var)
        return ""

    insertion = match.group(1)

    # Check if the insertion is defined as letters or numbers
    if insertion.isdigit():
        # If it's a number, it represents the number of nucleotides directly
        num_nucleotides = int(insertion)
    elif '_' in insertion:
        # If it's a range, calculate the number of nucleotides
        start, end = map(int, insertion.split('_'))
        num_nucleotides = end - start + 1
    else:
        # If it's letters, calculate the number of nucleotides
        num_nucleotides = len(insertion)

    # Check if the number of nucleotides is divisible by 3
    if num_nucleotides % 3 == 0:
        return "frameshift"
    else:
        return "in-frame"
