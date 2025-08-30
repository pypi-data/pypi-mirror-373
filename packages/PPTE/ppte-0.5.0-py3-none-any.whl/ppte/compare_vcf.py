import pysam

def load_vcf(vcf_file, sampleID):
    pos_list = []
    gt_list = []
    vcf = pysam.VariantFile(vcf_file)

    if sampleID not in vcf.header.samples:
        raise ValueError(f"Sample ID '{sampleID}' not found in VCF header")
    
    for record in vcf.fetch():    
        sample = record.samples[sampleID]
        gt = sample.get('GT')  
        # filt positions withou any variants
        if any(allele is None for allele in gt) or all(allele == 0 for allele in gt):
            continue
        pos_list.append(record.pos)
        gt_list.append(gt)
    
    return pos_list, gt_list


def calculate_metrics(tp, fp, fn):
    '''
    Calculate F1, precision, recall from confusion counts.
    '''
    # Parameter check
    assert tp >= 0 and fp >= 0 and fn >= 0, "tp, fp, fn must be non-negative integers"
    # Calculate Recall and Precision
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    # Calculate F1
    if (recall + precision) > 0:
        F1 = 2 * recall * precision / (recall + precision)
    else:
        F1 = 0
    return F1, precision, recall


class CompareVCF:
    def __init__(self, args):
        self.nHap = args.nHap
        self.truth_file = args.truth
        self.compare_file = args.pred
        self.max_dist = args.max_dist
        self.truthID = args.truthID
        self.predID = args.predID
        self.MatchFile = args.outprefix
    
    def _run(self):
        if self.nHap > 1:
            self.convert_to_ploidy()
            bench_pos, bench_gt = load_vcf("polyhap.vcf", self.truthID)
        else:
            bench_pos, bench_gt = load_vcf(self.truth_file, self.truthID)
        compare_pos, compare_gt = load_vcf(self.compare_file, self.predID)
        tp, fp, fn = self.calculate_confusion_counts(bench_pos, bench_gt, compare_pos, compare_gt)
        print(f"There are {self.nMatch} variants matched.")
        self.F1, self.precision, self.recall = calculate_metrics(tp, fp, fn)
        print(f"True Positive: {tp}, False Positive: {fp}, False negative: {fn}")
        print(f"Recall: {self.recall:.4f}, Precision: {self.precision:.4f}, F1: {self.F1:.4f}")
    
    # 应该把这个函数放到VCF文件生成里
    def convert_to_ploidy(self):
        # self.nHap
        # self.truth_file
        with open(self.truth_file, 'r') as fin, open("polyhap.vcf", 'w') as fout:
            for line in fin:
                if line.startswith('##'):
                    # 直接输出注释行
                    fout.write(line)
                elif line.startswith('#CHROM'):
                    # 处理表头
                    fields = line.strip().split('\t')
                    fixed_cols = fields[:9]
                    samples = fields[9:]
                    # 检查样本数能否被ploidy整除
                    if len(samples) % self.nHap != 0:
                        raise ValueError(f"Error: number of haplotypes ({len(samples)}) is not divisible by ploidy ({self.nHap})")
                    # 合并样本名
                    merged_samples = []
                    for i in range(0, len(samples), self.nHap):
                        group = samples[i:i+self.nHap]
                        merged_name = "_".join(group)
                        merged_samples.append(merged_name)
                    fout.write('\t'.join(fixed_cols + merged_samples) + '\n')
                else:
                    # 处理数据行
                    fields = line.strip().split('\t')
                    fixed_cols = fields[:9]
                    genotypes = fields[9:]
                    merged_gts = []
                    for i in range(0, len(genotypes), self.nHap):
                        group = genotypes[i:i+self.nHap]
                        # 只保留GT字段里的数字，假设只有GT且格式简单
                        # 如果是复杂格式，需要再扩展
                        merged_gt = '|'.join(group)
                        merged_gts.append(merged_gt)
                    fout.write('\t'.join(fixed_cols + merged_gts) + '\n')


    def calculate_confusion_counts(self, bench_pos, bench_gt, compare_pos, compare_gt):
        # get matched data
        i, j = 0, 0
        b_len = len(bench_pos)
        c_len = len(compare_pos)
        match_idxb = []
        match_idxc = []
        fo = open(self.MatchFile + ".csv", "w")  
        while i < b_len and j < c_len:
            pos_a = bench_pos[i]
            pos_b = compare_pos[j]
            if pos_b > pos_a + self.max_dist:
                i += 1
            elif pos_a - self.max_dist <= pos_b <= pos_a + self.max_dist:
                outLine = [str(i) for i in [bench_pos[i], bench_gt[i], compare_pos[j], compare_gt[j]]]
                fo.write(",".join(outLine) + "\n")
                match_idxb.append(i)
                match_idxc.append(j)
                i += 1
                j += 1
            else:
                j += 1
        fo.close()
        
        
        # calculate confusion counts
        nMatch = len(match_idxb)
        self.nMatch = nMatch
        only_comp = c_len - nMatch# only in compare vcf
        fn = b_len - nMatch  # only in bench vcf
        bgt = [bench_gt[i] for i in match_idxb]
        cgt = [compare_gt[i] for i in match_idxc]
        # sorted, because the 1/0 should same as 0/1
        tp = sum(1 for a, b in zip(bgt, cgt) if sorted(a) == sorted(b))
        gt_diff = nMatch - tp
        
        # FP: only in comparison VCF + mismatched genotypes
        fp = only_comp + gt_diff
        
        return tp, fp, fn

def run(args):
    CompareVCF(args)._run()

