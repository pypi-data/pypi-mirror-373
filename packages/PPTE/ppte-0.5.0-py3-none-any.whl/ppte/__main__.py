# __main__.py
import argparse
from . import build_pool, TE_real, simulate, compare_vcf, reads

def main():
    parser = argparse.ArgumentParser(prog="ppte", 
                                     description="PPTEs: A Pangenome Polymorphic Transposable Elements simulation toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. TErandom
    p1 = subparsers.add_parser("TErandom", 
                               help="Generate pTE position from known deletion sites and random TE insertion")
    # Base
    p1.add_argument("--consensus", "-C", type=str,  required=True,
                    help="Path to the TE consensus FASTA file")
    p1.add_argument("--knownDEL", "-L", type=str, required=True, 
                    help="Input known TE deletion file (RepeatMasker .out or UCSC .txt)")
    p1.add_argument("--nTE", "-N", type=int, default=500, 
                    help="Number of polymorphic TE (pTE) insertions to simulate (default: 500)")
    p1.add_argument("--ins-ratio", "-R", type=float, default=0.4, 
                    help="Proportion of insertion events among all simulated pTE (0-1, default: 0.4)")
    p1.add_argument("--outprefix", "-O", type=str, default="TEpool", 
                    help="Output prefix for the generated TE pool FASTA file and the bed file (default: TEpool)")
    p1.add_argument("--CHR", "-H", type=str, required=True, 
                    help="Chromosome to simulate TE insertions on (e.g., chr21 or 21)")
    # SNP and INDEL
    p1.add_argument("--snp-rate", "-S", type=float, default=0.02, 
                    help="SNP mutation rate per base (default: 0.02)")
    p1.add_argument("--indel-rate", "-I", type=float, default=0.005, 
                    help="Indel mutation rate per base (default: 0.005)")
    p1.add_argument("--indel-ins", "-r", type=float, default=0.4, 
                    help="Proportion of insertion events among INDELs (0-1, default: 0.4)")
    p1.add_argument("--indel-geom-p", "-G", type=float, default=0.7, 
                    help="Parameter 'p' of geometric distribution for indel lengths (default: 0.7)")
    # Truncation
    p1.add_argument("--truncated-ratio", "-T", type=float, default=0.3, 
                    help="Proportion of TE sequences to truncate (0-1, default: 0.3)")
    p1.add_argument("--truncated-max-length", "-K", type=float, default=0.5, 
                    help="Maximum proportion of sequence length to truncate (0-1, default: 0.5)")
    # PolyA
    p1.add_argument("--polyA-ratio", "-A", type=float, default=0.8, 
                    help="Proportion of TE sequences to add polyA tail (0-1, default: 0.8)")
    p1.add_argument("--polyA-min", "-M", type=int, default=5, 
                    help="Minimum polyA tail length (default: 5)")
    p1.add_argument("--polyA-max", "-X", type=int, default=20, 
                    help="Maximum polyA tail length (default: 20)")
    # Other
    p1.add_argument("--seed", "-D", type=int, default=None, 
                    help="Random seed for reproducibility (default: None)")
    p1.add_argument("--verbose", "-V", action="store_false", 
                    help="Disable verbose logging (default: True)")
    p1.set_defaults(func=build_pool.run)

    # 2. TEreal
    p2 = subparsers.add_parser("TEreal", 
                               help="Generate pTE position from Known TE insertion and deletion")
    # Input
    p2.add_argument("--knownINS", "-K", type=str, required=True, 
                    help="Input known TE insertion file (e.g., MEI_Callset)")
    p2.add_argument("--knownDEL", "-L", type=str, required=True, 
                    help="Input known TE deletion file (RepeatMasker .out or UCSC .txt)")
    p2.add_argument("--CHR", "-C", type=str, required=True, 
                    help="Chromosome to simulate TE insertions on (e.g., chr21 or 21)")
    # Output
    p2.add_argument("--outprefix", "-O", type=str, default="real", 
                    help="Output prefix for generated BED file (default: 'real')")
    p2.add_argument("--nTE", "-N", type=int, default=500, 
                    help="Number of polymorphic TE (pTE) insertions to simulate (default: 500)")
    p2.add_argument("--ins-ratio", "-R", type=float, default=0.4, 
                    help="Proportion of insertion events among all simulated pTE (0-1, default: 0.4)")
    # Other
    p2.add_argument("--seed", "-D", type=int, default=None, 
                    help="Random seed for reproducibility (default: None)")
    p2.add_argument("--verbose", "-V", action="store_false", 
                    help="Disable verbose logging (default: True)")
    p2.set_defaults(func=TE_real.run)

    # 3. simulate
    p3 = subparsers.add_parser("simulate", 
                               help="Simulate TE insertions/deletions and generate VCF and modified genome FASTA")
    # Input
    p3.add_argument("--ref", "-F", type=str, required=True, 
                    help="Reference genome FASTA file")
    p3.add_argument("--pool", "-P", type=str, required=True, 
                    help="FASTA file of TE sequences generated from 'TEpool'")
    p3.add_argument("--bed", "-B", type=str, required=True, 
                    help="BED file containing TE positions (can be generated by 'TEreal')")
    # Output
    p3.add_argument("--outprefix", "-O", type=str, default="Sim", 
                    help="Prefix for output files (VCF + modified genome FASTA)")
    # Options
    p3.add_argument("--num", "-N", type=int, required=True, 
                    help="Number of genomes to simulate")
    p3.add_argument("--diverse", "-I", action="store_true",
                    help="Introduce sequence diversity among individuals for the same TE event")
    p3.add_argument("--diverse_config", "-c", type=str,
                    help="Path to a configuration file for introducing sequence diversity among individuals for the same TE event")
    p3.add_argument("--af-min", "-A", type=float, default=0.1, 
                    help="Minimum allele frequency for simulated TE insertions (default: 0.1)")
    p3.add_argument("--af-max", "-X", type=float, default=0.9, 
                    help="Maximum allele frequency for simulated TE insertions (default: 0.9)")
    p3.add_argument("--tsd-min", "-M", type=int, default=5, 
                    help="Minimum TSD length (default: 5)")
    p3.add_argument("--tsd-max", "-Y", type=int, default=20, 
                    help="Maximum TSD length (default: 20)")
    p3.add_argument("--sense-strand-ratio", "-S", type=float, default=0.5, 
                    help="Proportion of TE insertions in the sense strand (default: 0.5)")
    # Other
    p3.add_argument("--seed", "-D", type=int, default=None, 
                    help="Random seed for reproducibility (default: None)")
    p3.add_argument("--verbose", "-V", action="store_false", 
                    help="Disable verbose logging")
    p3.set_defaults(func=simulate.run)

    # 4. compare
    p4 = subparsers.add_parser("compare", 
                               help="Compare predicted VCF to ground truth VCF")
    # Input
    p4.add_argument("--truth", "-T", type=str, required=True, 
                    help="Ground truth VCF file")
    p4.add_argument("--pred", "-P", type=str, required=True, 
                    help="Predicted VCF file to compare")
    # Output
    p4.add_argument("--outprefix", "-O", type=str, required=True, 
                    help="Output matched TEs")
    # Options
    p4.add_argument("--nHap", "-N", type=int, default=2, 
                    help="Number of haplotypes in the genome (default: 2)")
    p4.add_argument("--truthID", "-I", type=str, required=True, 
                    help="Sample ID in the truth VCF")
    p4.add_argument("--predID", "-J", type=str, required=True, 
                    help="Sample ID in the predicted VCF")
    p4.add_argument("--max_dist", "-M", type=int, default=100, 
                    help="Maximum allowed distance (bp) to consider two variants as matching")
    p4.set_defaults(func=compare_vcf.run)

    # 5. Read simulation
    p5 = subparsers.add_parser("readsim", 
                               help="generate short or long reads from the simulated genome")
    # general
    p5.add_argument("--type", "-T", choices=["short", "long"],
                    type=str, required=True, help="Simulate short reads or long reads")
    p5.add_argument("--genome", "-G", type=str, required=True, 
                    help="The file contains genomes where reads simulated from")
    p5.add_argument("--depth", "-P", type=int, required=True, 
                    help="Depth of simulated reads")    
    #p5.add_argument("--ngenome", "-N", type=int, default= 1, 
    #                help="Number of genomes for simultaneous reads simulation")
    #p5.add_argument("--outprefix", "-O", type=str, required=True, 
    #                help="prefix of output files")    
    # long reads settings
    p5.add_argument("--Lerror", "-E", type=float, default= 0.15, 
                    help="sequencing error rate for long reads")
    p5.add_argument("--Lmean", "-M", type=int,  default= 9000,
                    help="average size of read length (only for long reads)")
    p5.add_argument("--Lstd", "-S", type=int, default= 7000,  
                    help="read length standard deviation (only for long reads)")
    # short reads settings
    p5.add_argument("--length", "-i", type=int, default= 150, 
                    help="read length (only for short reads)")
    p5.add_argument("--Fmean", "-m", type=int, default= 300, 
                    help="average size of fragment length (only for short reads)")
    p5.add_argument("--Fstd", "-s", type=int, default= 30,  
                    help="Fragment size standard deviation (only for short reads)")
    # random seed
    p5.add_argument("--seed", "-D", type=int, default=None, 
                    help="Random seed for reproducibility (default: None)")
    p5.set_defaults(func=reads.run)
    
    args = parser.parse_args()
    if args.command == "simulate":
        if args.diverse_config and not args.diverse:
            parser.error("--diverse_config requires --diverse to be set")
    args.func(args)

if __name__ == "__main__":
    main()
