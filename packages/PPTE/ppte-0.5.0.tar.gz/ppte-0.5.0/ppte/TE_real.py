import random
import os


def check_output_file(output_path):
    if os.path.exists(output_path):
        raise FileExistsError(f"Output file '{output_path}' already exists. Please choose a different name.")

def CHRnorm(chrA,chrB):
    ### normalize chrA according the style if chrB
    if chrA.isdigit() and chrB.isdigit():
         return chrA
    elif chrA.isdigit() and not chrB.isdigit():
        if not chrB[3:].isdigit():
            raise ValueError("Chromosome names must be either plain numbers ('1') or prefixed with 'chr' ('chr1')")
        else:
            chrA = chrB[:3] + chrA
    elif not chrA.isdigit() and chrB.isdigit():
            chrA = chrA[3:]
    else:
        if chrA[:3].upper() != chrB[:3].upper():
            raise ValueError("Chromosome names must be either plain numbers ('1') or prefixed with 'chr' ('chr1')")
        else:
            chrA = chrB[:3] + chrA[3:]
    return chrA

class RealTE:
    def __init__(self, args):
        # self.reference = args.reference
        self.INSfile = args.knownINS
        self.DELfile = args.knownDEL
        self.CHR = args.CHR
        self.nTE = args.nTE
        self.ins_ratio = args.ins_ratio
        self.outprefix = args.outprefix
        self.random_seed = args.seed
        if self.random_seed is not None:
            random.seed(self.random_seed)

    def _run(self):
        """
        Entry point for the `generate-bed` subcommand.
        Dispatches to appropriate parser depending on input file type.
        """
        # 1. 解析文件
        self.parse_INS_file()
        _, ext = os.path.splitext(self.DELfile)
        if ext.lower() == ".txt":
            self.parse_DEL_ucsc()
        elif ext.lower() == ".out":
            self.parse_DEL_repeatmasker()
        else:
            raise ValueError("DEL file name must end with .txt (UCSC) or .out (RepeatMasker).")

        # 2. Remove overlapping regions between INS and DEL
        self.remove_dup_DEL()

        # 3. Generate BED file
        self.build_bed()

    def build_bed(self):
        # merge 
        nINS = int(self.nTE * self.ins_ratio)
        nDEL = self.nTE - nINS
        if nINS > len(self.INS) or nDEL > len(self.DEL): 
            raise ValueError(f"generated TE count exceeds total; require INS < {len(self.INS)} and DEL < {len(self.DEL)}")
        INSlist = random.sample(self.INS, nINS)
        DELlist = random.sample(self.DEL, nDEL)
        merged = INSlist + DELlist
        merged.sort()
        # bedfile output
        bed_name = self.outprefix + ".bed"
        check_output_file(bed_name)
        with open(bed_name, "w") as f:
            for start, end, teID, _ in merged:
                f.write("\t".join([self.CHR, str(start), str(end), teID]) + "\n")

    
    def parse_DEL_ucsc(self):
        """
        Parse UCSC repeat annotation file (.txt) and return a list of parsed records.
        self.DEL
        """
        self.DEL = []
        TE_CLASSES = {'LINE', 'SINE', 'LTR', 'Helitron'}
        ## nomalize the chr ID
        #with open(self.DELfile, "r") as f:
        #    first_line = f.readline().strip()
        #    chrom = first_line.split('\t')[5]
        #    print(f"chromosome from DEL file: {chrom}")
        #    self.CHR = CHRnorm(self.CHR, chrom)
        # process file
        with open(self.DELfile) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                fields = line.strip().split('\t')
                chrom = fields[5]
                # nomalize the chr ID
                self.CHR = CHRnorm(self.CHR, chrom)
                repClass = fields[11]
                if chrom == self.CHR and repClass in TE_CLASSES:
                    start = int(fields[6])
                    end = int(fields[7])
                    teID = f"DEL-{chrom}-{start}-{end}-{fields[12]}-{fields[10]}"
                    self.DEL.append((start, end, teID, "DEL"))
                    # self.TEpool[teID] = fasta.fetch(self.CHR, start, end)

    def parse_DEL_repeatmasker(self):
        """
        Parse repeatmasker output file (.out) and return a list of parsed records.
        self.DEL
        """
        self.DEL = []
        TE_CLASSES = {'LINE', 'SINE', 'LTR', 'RC'}
        # process file
        with open(self.DELfile) as f:
            for line in f:
                if not line[0].isdigit():
                    continue
                fields = line.strip().split()
                chrom = fields[4]
                # nomalize the chr ID
                self.CHR = CHRnorm(self.CHR, chrom)
                repClass = fields[10].split("/")[0]
                if chrom == self.CHR and repClass in TE_CLASSES:
                    start = int(fields[5])
                    end = int(fields[6])
                    teID = f"DEL-{chrom}-{start}-{end}-{fields[10]}-{fields[9]}"
                    self.DEL.append((start, end, teID, "DEL"))
        
    
    def parse_INS_file(self):
        """
        Parse inbuilt TE insertion file to bed file
        self.INS
        """
        # nomalize the chr ID
        self.INS = []
        with open(self.INSfile, "r") as f:
            chrom = f.readline().strip().lstrip(">").split("-")[0]
            self.CHR = CHRnorm(self.CHR, chrom)
        # process file
        with open(self.INSfile) as fin:
            for line in fin:
                if line.startswith(">"):
                    teID = line.strip().lstrip(">")
                    info = teID.split("-")
                    chrom = info[0]
                    if chrom == self.CHR:
                        # bed file is 0-based position
                        start = int(info[1]) - 1 
                        end = int(info[1])
                        self.INS.append((start, end, teID, "INS"))


    def remove_dup_DEL(self):
        """
        Remove DELs that overlap with INSs.
        """
        i, j = 0, 0
        rm_idx = []

        while i < len(self.INS) and j < len(self.DEL):
            a_start, a_end, *_ = self.INS[i]
            b_start, b_end, *_ = self.DEL[j]

            # If B[j] overlaps with A[i]
            if a_start < b_end and a_end > b_start:
                rm_idx.append(j)

            if a_end < b_end:
                i += 1
            else:
                j += 1
        # remove
        delete_set = set(rm_idx)
        self.DEL = [item for i, item in enumerate(self.DEL) if i not in delete_set]

def run(args):
    RealTE(args)._run()