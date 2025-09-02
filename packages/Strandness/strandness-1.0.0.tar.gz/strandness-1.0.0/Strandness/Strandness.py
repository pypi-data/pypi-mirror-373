#!/usr/bin/env python
import numpy as np
import pandas as pd
import os
import sys, getopt
import os.path
import argparse
import math
import gzip
import subprocess
import shutil
from collections import Counter, defaultdict

import pysam
from intervaltree import IntervalTree

dir = os.path.dirname(__file__)
version_py = os.path.join(dir, "_version.py")
exec(open(version_py).read())

# ------------------------------------------------------------
# GTF parsing → exon interval index (per chrom + strand)
# ------------------------------------------------------------

def _parse_gtf_attrs(attr_field: str):
    d = {}
    for item in attr_field.strip().split(";"):
        item = item.strip()
        if not item or " " not in item:
            continue
        k, v = item.split(" ", 1)
        d[k] = v.strip().strip('"')
    return d

def build_exon_index(gtf_path):
    """
    Build per-chromosome, per-strand IntervalTrees of merged gene exons.
    Returns:
      exon_trees: dict[chrom][strand] -> IntervalTree(start,end,data=gene_id)
    """
    opener = gzip.open if gtf_path.endswith(".gz") else open
    exons = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # [chrom][strand][gene_id] -> [(s,e)]
    with opener(gtf_path, "rt") as f:
        for line in f:
            if not line or line.startswith("#"):
                continue
            toks = line.rstrip("\n").split("\t")
            if len(toks) < 9:
                continue
            chrom, src, feature, start, end, score, strand, frame, attrs = toks
            if feature != "exon" or strand not in {"+","-"}:
                continue
            a = _parse_gtf_attrs(attrs)
            gene_id = a.get("gene_id") or a.get("gene_name") or a.get("transcript_id")
            if not gene_id:
                continue
            s = int(start) - 1  # GTF 1-based → 0-based
            e = int(end)
            exons[chrom][strand][gene_id].append((s,e))

    exon_trees = defaultdict(lambda: defaultdict(IntervalTree))
    for chrom in exons:
        for strand in exons[chrom]:
            for gene_id, ivs in exons[chrom][strand].items():
                ivs.sort()
                merged = []
                cs, ce = ivs[0]
                for s,e in ivs[1:]:
                    if s <= ce:
                        ce = max(ce, e)
                    else:
                        merged.append((cs,ce))
                        cs,ce = s,e
                merged.append((cs,ce))
                for s,e in merged:
                    exon_trees[chrom][strand].addi(s,e,gene_id)
    return exon_trees

# ------------------------------------------------------------
# Alignment with HISAT2 (used when -F fastq)
# ------------------------------------------------------------

def _which(cmd): return shutil.which(cmd) is not None

def align_full_hisat2(fq1, fq2, index_prefix, out_bam, threads=8, hisat2_extra=None):
    """
    Align full FASTQ(s) with HISAT2 → samtools view/sort/index.
    Produces sorted BAM + BAI at out_bam (+ .bai).
    """
    if not (_which("hisat2") and _which("samtools")):
        raise RuntimeError("hisat2 and samtools must be in PATH when using -F fastq")

    hisat2_cmd = ["hisat2", "-p", str(threads), "-x", index_prefix]
    if fq2:
        hisat2_cmd += ["-1", fq1, "-2", fq2]
    else:
        hisat2_cmd += ["-U", fq1]
    if hisat2_extra:
        hisat2_cmd += hisat2_extra

    # hisat2 (SAM to stdout) | samtools view -b -u | samtools sort
    view_cmd = ["samtools", "view", "-@",
                str(threads), "-b", "-u", "-"]
    sort_cmd = ["samtools", "sort", "-@", str(threads), "-o", out_bam]
    index_cmd = ["samtools", "index", out_bam]

    p1 = subprocess.Popen(hisat2_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(view_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p1.stdout.close()
    p3 = subprocess.Popen(sort_cmd, stdin=p2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2.stdout.close()

    _, err3 = p3.communicate()
    # Drain p1/p2 stderr to avoid broken pipes masking errors
    _, err1 = p1.communicate()
    _, err2 = p2.communicate()

    if p1.returncode != 0:
        raise RuntimeError(f"HISAT2 failed:\n{err1.decode('utf-8', errors='ignore')}")
    if p2.returncode != 0:
        raise RuntimeError(f"samtools view failed:\n{err2.decode('utf-8', errors='ignore')}")
    if p3.returncode != 0:
        raise RuntimeError(f"samtools sort failed:\n{err3.decode('utf-8', errors='ignore')}")

    subprocess.check_call(index_cmd)

# ------------------------------------------------------------
# Strandedness inference (R1-based convention)
# ------------------------------------------------------------

def infer_strandedness_from_bam(bam_path, exon_trees, require_unique=True):
    """
    Streams the entire BAM (no downsampling) and scores informative alignments.
    Counts only:
      - primary, mapped alignments
      - for paired-end: R1 in proper pairs
      - for SE: all primary alignments
      - unique mappers if require_unique (NH==1)
      - reads overlapping exactly one gene on exactly one strand
    Returns dict with counts, fractions, decision, and tool flag suggestions.
    """
    bam = pysam.AlignmentFile(bam_path, "rb")
    counts = Counter()
    observed_paired = False

    for read in bam.fetch(until_eof=True):
        if read.is_unmapped or read.is_secondary or read.is_supplementary:
            continue
        if require_unique and read.has_tag("NH") and read.get_tag("NH") != 1:
            continue

        if read.is_paired:
            observed_paired = True
            if not read.is_read1 or not read.is_proper_pair:
                continue  # strandedness is defined w.r.t. R1
        # else single-end ok

        chrom = bam.get_reference_name(read.reference_id)
        if chrom is None:
            continue
        r_start = read.reference_start
        r_end = read.reference_end
        if r_start is None or r_end is None:
            continue

        plus_hits  = exon_trees.get(chrom, {}).get("+", IntervalTree()).overlap(r_start, r_end)
        minus_hits = exon_trees.get(chrom, {}).get("-", IntervalTree()).overlap(r_start, r_end)
        genes_plus  = set(iv.data for iv in plus_hits)
        genes_minus = set(iv.data for iv in minus_hits)

        # ambiguous if overlapping both strands or >1 gene
        if (genes_plus and genes_minus) or (len(genes_plus) + len(genes_minus) != 1):
            counts["ambiguous"] += 1
            continue

        g_strand = "+" if genes_plus else "-"
        read_strand = "-" if read.is_reverse else "+"

        if read_strand == g_strand:
            counts["sense"] += 1
        else:
            counts["antisense"] += 1

    bam.close()

    informative = counts["sense"] + counts["antisense"]
    frac_sense = (counts["sense"] / informative) if informative else 0.0
    frac_antisense = (counts["antisense"] / informative) if informative else 0.0

    # Conservative threshold (adjustable)
    decision = "Unstranded"
    fc_flag, htseq_flag, salmon_hint = "-s 0", "--stranded=no", "IU (paired) or U (single-end)"
    if informative >= 1000:
        if frac_sense >= 0.8:
            decision = "Stranded (Forward: R1 = sense)"
            fc_flag, htseq_flag, salmon_hint = "-s 1", "--stranded=yes", "ISF (paired) or SF (single-end)"
        elif frac_antisense >= 0.8:
            decision = "Stranded (Reverse: R1 = antisense)"
            fc_flag, htseq_flag, salmon_hint = "-s 2", "--stranded=reverse", "ISR (paired) or SR (single-end)"

    return {
        "observed_paired": observed_paired,
        "n_informative": int(informative),
        "counts": dict(counts),
        "frac_sense": frac_sense,
        "frac_antisense": frac_antisense,
        "decision": decision,
        "recommendations": {
            "featureCounts": fc_flag,
            "HTSeq": htseq_flag,
            "Salmon": salmon_hint
        }
    }

# ------------------------------------------------------------
# annotation() — mirrors your demo’s structure
# ------------------------------------------------------------

def annotation(format, inputpath, filename, outpath, gtf, outfile,
               hisat2_index=None, fastq1=None, fastq2=None, bam_path=None,
               threads=8, allow_multimappers=False, hisat2_extra=None):
    """
    format: 'bam' or 'fastq'
    - If 'bam': uses BAM at {bam_path} or {inputpath}/{filename}.bam
    - If 'fastq': aligns FULL FASTQs with HISAT2 to {outpath}/{outfile}.sorted.bam
    """
    os.makedirs(outpath, exist_ok=True)

    # Build exon index once (used for strandedness scoring)
    print("[*] Building exon index from GTF ...", file=sys.stderr)
    exon_trees = build_exon_index(gtf)

    # Resolve input BAM (align if needed)
    if format == "bam":
        if bam_path is None:
            bam_path = os.path.join(inputpath, filename + ".bam")
        if not os.path.exists(bam_path):
            raise FileNotFoundError(f"BAM not found: {bam_path}")
    elif format == "fastq":
        if not hisat2_index:
            raise ValueError("When -F fastq, provide HISAT2 index prefix via -X/--hisat2-index")
        # If not explicitly provided, assume _R1/_R2 naming
        if fastq1 is None:
            fastq1 = os.path.join(inputpath, filename + "_R1.fastq.gz")
        if fastq2 is None:
            candidate = os.path.join(inputpath, filename + "_R2.fastq.gz")
            fastq2 = candidate if os.path.exists(candidate) else None

        out_bam = os.path.join(outpath, outfile + ".sorted.bam")
        print("[*] Aligning full FASTQ(s) with HISAT2 → samtools sort/index ...", file=sys.stderr)
        align_full_hisat2(fastq1, fastq2, hisat2_index, out_bam, threads=threads, hisat2_extra=hisat2_extra)
        bam_path = out_bam
    else:
        raise ValueError("format must be 'bam' or 'fastq'")

    # Infer strandedness
    print("[*] Scoring read orientations across entire BAM ...", file=sys.stderr)
    res = infer_strandedness_from_bam(
        bam_path=bam_path,
        exon_trees=exon_trees,
        require_unique=(not allow_multimappers)
    )

    # Save concise report
    report_txt = os.path.join(outpath, outfile + ".strand_report.txt")
    with open(report_txt, "w") as fh:
        fh.write("=== Strandedness Report ===\n")
        fh.write(f"Input mode     : {'paired-end (R1 evaluated)' if res['observed_paired'] else 'single-end or unknown (R1 rule)'}\n")
        fh.write(f"Informative n  : {res['n_informative']}\n")
        c = res['counts']
        fh.write(f"Counts         : sense={c.get('sense',0)} antisense={c.get('antisense',0)} ambiguous={c.get('ambiguous',0)}\n")
        fh.write(f"Fractions      : sense={res['frac_sense']:.4f} antisense={res['frac_antisense']:.4f}\n")
        fh.write(f"Call           : {res['decision']}\n")
        fh.write("\nRecommended flags:\n")
        fh.write(f"  featureCounts : {res['recommendations']['featureCounts']}\n")
        fh.write(f"  HTSeq         : {res['recommendations']['HTSeq']}\n")
        fh.write(f"  Salmon        : {res['recommendations']['Salmon']}\n")
        fh.write("\nNotes:\n")
        fh.write("  • Calls are defined with respect to Read1 (R1). For SE, treat the only read as R1.\n")
        fh.write("  • Thresholds are conservative (≥0.8). Use raw fractions if you need a different cutoff.\n")
        fh.write("  • Use --allow-multimappers to include NH>1 alignments.\n")

    # Save tabular counts/fractions
    tsv_path = os.path.join(outpath, outfile + ".strand_counts.tsv")
    pd.DataFrame([{
        "observed_paired": res["observed_paired"],
        "informative": res["n_informative"],
        "sense": res["counts"].get("sense",0),
        "antisense": res["counts"].get("antisense",0),
        "ambiguous": res["counts"].get("ambiguous",0),
        "frac_sense": round(res["frac_sense"], 6),
        "frac_antisense": round(res["frac_antisense"], 6),
        "decision": res["decision"],
        "featureCounts_flag": res["recommendations"]["featureCounts"],
        "HTSeq_flag": res["recommendations"]["HTSeq"],
        "Salmon_hint": res["recommendations"]["Salmon"]
    }]).to_csv(tsv_path, sep="\t", index=False)

    # Echo summary to stdout (like your demo)
    print("\n=== Strandedness Report ===")
    print(f"Input mode     : {'paired-end (R1 evaluated)' if res['observed_paired'] else 'single-end or unknown (R1 rule)'}")
    print(f"Informative n  : {res['n_informative']}")
    print(f"Counts         : sense={res['counts'].get('sense',0)} "
          f"antisense={res['counts'].get('antisense',0)} "
          f"ambiguous={res['counts'].get('ambiguous',0)}")
    print(f"Fractions      : sense={res['frac_sense']:.4f} antisense={res['frac_antisense']:.4f}")
    print(f"Call           : {res['decision']}")
    print("\nRecommended flags:")
    print(f"  featureCounts : {res['recommendations']['featureCounts']}")
    print(f"  HTSeq         : {res['recommendations']['HTSeq']}")
    print(f"  Salmon        : {res['recommendations']['Salmon']}")
    print(f"\nSaved:\n  {report_txt}\n  {tsv_path}\n")

# ------------------------------------------------------------
# main() — mirrors your demo (flags + echo params + call)
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-F', '--format', type=str, default='bam',
                        choices=['bam', 'fastq'],
                        help="Input type: 'bam' uses an existing BAM; 'fastq' aligns the full FASTQ(s) with HISAT2.")
    parser.add_argument('-I', '--inputpath', dest='inputpath', required=True,
                        help='Path to input files (BAM or FASTQ directory).')
    parser.add_argument('-f', '--filename', dest='filename', required=True,
                        help='Base name of input (e.g. sample → sample.bam or sample_R1.fastq.gz by default).')
    parser.add_argument('-G', '--gtf', dest='gtf', required=True,
                        help='GTF (can be .gtf or .gtf.gz). Exon records are used.')
    parser.add_argument('-X', '--hisat2-index', dest='hisat2_index', required=False,
                        help='HISAT2 index prefix (required when -F fastq).')
    parser.add_argument('-O', '--outpath', dest='outpath', required=True,
                        help='Output directory.')
    parser.add_argument('-o', '--outfile', dest='outfile', required=True,
                        help='Output file prefix.')

    # Optional explicit paths (so you aren’t locked to default naming)
    parser.add_argument('-B', '--bam', dest='bam_path', required=False,
                        help='Explicit BAM path (overrides inputpath/filename.bam).')
    parser.add_argument('-1', '--fastq1', dest='fastq1', required=False,
                        help='Explicit FASTQ read1 path (overrides inputpath/filename_R1.fastq.gz).')
    parser.add_argument('-2', '--fastq2', dest='fastq2', required=False,
                        help='Explicit FASTQ read2 path. Omit for single-end.')
    parser.add_argument('-T', '--threads', dest='threads', type=int, default=8,
                        help='Threads for HISAT2/samtools when -F fastq.')
    parser.add_argument('--allow-multimappers', action='store_true',
                        help='Include NH>1 alignments (default: exclude).')
    parser.add_argument('--hisat2-extra', dest='hisat2_extra', nargs=argparse.REMAINDER,
                        help='Any extra args to pass to HISAT2 (e.g., --dta). Everything after this flag is sent to hisat2.')

    parser.add_argument("-V", "--version", action="version",version="DLR_ICF_main {}".format(__version__)\
                      ,help="Print version and exit")

    args = parser.parse_args()
    print('###Parameters:')
    print(args)
    print('###Parameters')

    annotation(args.format, args.inputpath, args.filename,
               args.outpath, args.gtf, args.outfile,
               hisat2_index=args.hisat2_index,
               fastq1=args.fastq1, fastq2=args.fastq2, bam_path=args.bam_path,
               threads=args.threads, allow_multimappers=args.allow_multimappers,
               hisat2_extra=args.hisat2_extra)

if __name__ == '__main__':
    main()
