# Strandness  
This tutorial will introduce how to run Strandness to analyze strandness of RNAs-seq data.

### Strandness can be used to analyze strandness of RNAs-seq data.  

#### Using an existing BAM (fastest):
#### usage: 
```python infer_rnaseq_strand.py \
  -F bam \
  -I /data/aln \
  -f sample \
  -G /refs/genes.gtf.gz \
  -O /data/out \
  -o sample_strand
``` 

#### From FASTQs with HISAT2 (paired-end):
#### usage: 
```
   python infer_rnaseq_strand.py \
  -F fastq \
  -I /data/fastq \
  -f sample \
  -G /refs/genes.gtf.gz \
  -X /refs/hisat2/grch38_index  \
  -O /data/out \
  -o sample_strand \
  -1 /data/fastq/sample_R1.fastq.gz \
  -2 /data/fastq/sample_R2.fastq.gz \
  -T 16
``` 

#### From FASTQs with HISAT2 (pSingle-end):
#### usage: 
```
   python infer_rnaseq_strand.py \
  -F fastq \
  -I /data/fastq \
  -f sample_SE \
  -G /refs/genes.gtf.gz \
  -X /refs/hisat2/grch38_index \
  -O /data/out \
  -o sampleSE_strand \
  -1 /data/fastq/sample_SE.fastq.gz
``` 


### Installation 
#### requirement for installation
python>=3.8  
numpy  
pandas  
argparse  

#### pip install DLR-ICF==1.10.0
https://pypi.org/project/DLR-ICF/1.10.0/  

#### conda install -c bxhu dlr_icf
https://anaconda.org/bxhu/dlr_icf  

