'''
Wrapper for bowtie2
This wrapper covers ONLY fastq queries, ONLY phred33 quality, ONLY presets, NO scoring tweaking,
NO reporting tweaking, NO effort tweaking, PE only fw/rev, NO output options except metric file,
print NOTHING to stderr except errors.
'''
from .ICRAUtils import _shell_command
import logging

log_ = logging.getLogger(__name__)

BOWTIE_BIN = 'bowtie2'

class MapPreset:
    VERY_SENSITIVE = 'very-sensitive'
    SENSITIVE = 'sensitive'
    FAST = 'fast'
    VERY_FAST = 'very-fast'
    ALL_LIST = [VERY_FAST, FAST, SENSITIVE, VERY_SENSITIVE]

def do_pair_simple(fq1, fq2, outprefix, indexf, senspreset, report_alns, max_ins, threads):
    if fq2 is None:
        dose(fq1, outprefix, indexf, True, False, senspreset, report_alns, None, threads)
    else:
        dope(fq1, fq2, outprefix, indexf, True, False, senspreset, report_alns, 0, max_ins, True, True, False, False,
             False, None, threads)


def dope(input1, input2, output_prefix, indexf, bam=True,  # positional args
         local=False,  # local or end-to-end
         preset=MapPreset.SENSITIVE,  # using class MapPreset
         report_alns=1,  # positive integer or 'all'
         minins=0, maxins=500, no_mixed=False, no_discordant=False,  # PE options
         dovetail=False, no_contain=False, no_overlap=False,  # PE options
         metfile=None,  # Optional output metric to file
         threads=1):
    if local:
        preset = preset + '-local'
    alns = '-a ' if report_alns == 'all' else '-k {} '.format(report_alns) if report_alns > 1 else ''
    no_mixed = '--no-mixed ' if no_mixed else ''
    no_discordant = '--no-discordant ' if no_discordant else ''
    dovetail = '--dovetail' if dovetail else ''
    no_contain = '--no-contain' if no_contain else ''
    no_overlap = '--no-overlap' if no_overlap else ''
    metfile = '--met-file {} '.format(metfile) if metfile is not None else ''
    bam = '| samtools view -bS -@ {} - > {}.bam'.format(threads - 1, output_prefix) if bam else ''
    sam = '' if bam else '-S {}.sam '
    cmd = ('{bin} -x {indexf} -1 {input1} -2 {input2} {sam}--{preset} {alns} ' + \
           '-I {minins} -X {maxins} {no_mixed}{no_discordant}{dovetail}{no_contain}{no_overlap} ' + \
           '{metfile} --quiet -p {threads} {bam}').format(bin=BOWTIE_BIN, **locals())
    _ = _shell_command(cmd, loglevel=logging.DEBUG)
    # TODO: return something?


def dose(inputf, output_prefix, indexf, bam=True,  # positional args
         local=False,  # local or end-to-end
         preset=MapPreset.SENSITIVE,  # using class MapPreset
         report_alns=1,  # positive integer or 'all'
         metfile=None,  # Optional output metric to file
         threads=1):
    if local:
        preset = preset + '-local'
    alns = '-a ' if report_alns == 'all' else '-k {} '.format(report_alns) if report_alns > 1 else ''
    metfile = '--met-file {} '.format(metfile) if metfile is not None else ''
    bam = '| samtools view -bS -@ {} - > {}.bam'.format(threads - 1, output_prefix) if bam else ''
    sam = '' if bam else '-S {}.sam '
    cmd = ('{bin} -x {indexf} -U {inputf} {sam}--{preset} {alns}' + \
           '{metfile} --quiet -p {threads} {bam}').format(bin=BOWTIE_BIN, **locals())
    print(cmd)
    retval = _shell_command(cmd, loglevel=logging.DEBUG)
    if len(retval.splitlines()) > 0 and retval.splitlines()[-1].startswith('(ERR):'):
        log_.error(retval)
        assert 1==0, 'Bowtie failed'


if __name__ == '__main__':
    from addloglevels import sethandlers
    from os.path import join
    from os import chdir

    sethandlers()

    indexf = '/rugpfs/fs0/physics/scratch/dzeevi/Data/Databases/OM-RGC/OM-RGC'
    infol = '/rugpfs/fs0/physics/scratch/dzeevi/Data/Samples/bioGEOTRACES/PRJNA385854'
    outfol = '/rugpfs/fs0/physics/scratch/dzeevi/Analyses/2019-Oceans/tmp/OM_RGC_Mapping/1'
    chdir(outfol)
    with qp(jobname='bwm', max_r=10, q=['hpc'], trds_def=8) as q:
        q.startpermanentrun()
        waiton = [q.method(dope, (), dict(input1=join(infol, 'SRR5787995_1.fastq.gz'),
                                          input2=join(infol, 'SRR5787995_2.fastq.gz'),
                                          output_prefix=join(outfol, 'SRR5787995.local'),
                                          indexf=indexf,
                                          bam=True,
                                          local=True,
                                          report_alns=20,
                                          metfile=join(outfol, 'SRR5787995.local.met'),
                                          threads=8)),
                  q.method(dose, (), dict(inputf=join(infol, 'SRR5787995_1.fastq.gz'),
                                          output_prefix=join(outfol, 'SRR5787995_1.local'),
                                          indexf=indexf,
                                          bam=True,
                                          local=True,
                                          report_alns=20,
                                          metfile=join(outfol, 'SRR5787995_1.local.met'),
                                          threads=8))]
        q.wait(waiton)

'''
Usage: 
  bowtie2 [options]* -x <bt2-idx> {-1 <m1> -2 <m2> | -U <r> | --interleaved <i>} [-S <sam>]

  <bt2-idx>  Index filename prefix (minus trailing .X.bt2).
             NOTE: Bowtie 1 and Bowtie 2 indexes are not compatible.
  <m1>       Files with #1 mates, paired with files in <m2>.
             Could be gzip'ed (extension: .gz) or bzip2'ed (extension: .bz2).
  <m2>       Files with #2 mates, paired with files in <m1>.
             Could be gzip'ed (extension: .gz) or bzip2'ed (extension: .bz2).
  <r>        Files with unpaired reads.
             Could be gzip'ed (extension: .gz) or bzip2'ed (extension: .bz2).
  <i>        Files with interleaved paired-end FASTQ reads
             Could be gzip'ed (extension: .gz) or bzip2'ed (extension: .bz2).
  <sam>      File for SAM output (default: stdout)

  <m1>, <m2>, <r> can be comma-separated lists (no whitespace) and can be
  specified many times.  E.g. '-U file1.fq,file2.fq -U file3.fq'.

Options (defaults in parentheses):

 Input:
  -q                 query input files are FASTQ .fq/.fastq (default)
  --tab5             query input files are TAB5 .tab5
  --tab6             query input files are TAB6 .tab6
  --qseq             query input files are in Illumina's qseq format
  -f                 query input files are (multi-)FASTA .fa/.mfa
  -r                 query input files are raw one-sequence-per-line
  -c                 <m1>, <m2>, <r> are sequences themselves, not files
  -s/--skip <int>    skip the first <int> reads/pairs in the input (none)
  -u/--upto <int>    stop after first <int> reads/pairs (no limit)
  -5/--trim5 <int>   trim <int> bases from 5'/left end of reads (0)
  -3/--trim3 <int>   trim <int> bases from 3'/right end of reads (0)
  --phred33          qualities are Phred+33 (default)
  --phred64          qualities are Phred+64
  --int-quals        qualities encoded as space-delimited integers

 Presets:                 Same as:
  For --end-to-end:
   --very-fast            -D 5 -R 1 -N 0 -L 22 -i S,0,2.50
   --fast                 -D 10 -R 2 -N 0 -L 22 -i S,0,2.50
   --sensitive            -D 15 -R 2 -N 0 -L 22 -i S,1,1.15 (default)
   --very-sensitive       -D 20 -R 3 -N 0 -L 20 -i S,1,0.50

  For --local:
   --very-fast-local      -D 5 -R 1 -N 0 -L 25 -i S,1,2.00
   --fast-local           -D 10 -R 2 -N 0 -L 22 -i S,1,1.75
   --sensitive-local      -D 15 -R 2 -N 0 -L 20 -i S,1,0.75 (default)
   --very-sensitive-local -D 20 -R 3 -N 0 -L 20 -i S,1,0.50

 Alignment:
  -N <int>           max # mismatches in seed alignment; can be 0 or 1 (0)
  -L <int>           length of seed substrings; must be >3, <32 (22)
  -i <func>          interval between seed substrings w/r/t read len (S,1,1.15)
  --n-ceil <func>    func for max # non-A/C/G/Ts permitted in aln (L,0,0.15)
  --dpad <int>       include <int> extra ref chars on sides of DP table (15)
  --gbar <int>       disallow gaps within <int> nucs of read extremes (4)
  --ignore-quals     treat all quality values as 30 on Phred scale (off)
  --nofw             do not align forward (original) version of read (off)
  --norc             do not align reverse-complement version of read (off)
  --no-1mm-upfront   do not allow 1 mismatch alignments before attempting to
                     scan for the optimal seeded alignments
  --end-to-end       entire read must align; no clipping (on)
   OR
  --local            local alignment; ends might be soft clipped (off)

 Scoring:
  --ma <int>         match bonus (0 for --end-to-end, 2 for --local) 
  --mp <int>         max penalty for mismatch; lower qual = lower penalty (6)
  --np <int>         penalty for non-A/C/G/Ts in read/ref (1)
  --rdg <int>,<int>  read gap open, extend penalties (5,3)
  --rfg <int>,<int>  reference gap open, extend penalties (5,3)
  --score-min <func> min acceptable alignment score w/r/t read length
                     (G,20,8 for local, L,-0.6,-0.6 for end-to-end)

 Reporting:
  (default)          look for multiple alignments, report best, with MAPQ
   OR
  -k <int>           report up to <int> alns per read; MAPQ not meaningful
   OR
  -a/--all           report all alignments; very slow, MAPQ not meaningful

 Effort:
  -D <int>           give up extending after <int> failed extends in a row (15)
  -R <int>           for reads w/ repetitive seeds, try <int> sets of seeds (2)

 Paired-end:
  -I/--minins <int>  minimum fragment length (0)
  -X/--maxins <int>  maximum fragment length (500)
  --fr/--rf/--ff     -1, -2 mates align fw/rev, rev/fw, fw/fw (--fr)
  --no-mixed         suppress unpaired alignments for paired reads
  --no-discordant    suppress discordant alignments for paired reads
  --dovetail         concordant when mates extend past each other
  --no-contain       not concordant when one mate alignment contains other
  --no-overlap       not concordant when mates overlap at all

 Output:
  -t/--time          print wall-clock time taken by search phases
  --un <path>        write unpaired reads that didn't align to <path>
  --al <path>        write unpaired reads that aligned at least once to <path>
  --un-conc <path>   write pairs that didn't align concordantly to <path>
  --al-conc <path>   write pairs that aligned concordantly at least once to <path>
  (Note: for --un, --al, --un-conc, or --al-conc, add '-gz' to the option name, e.g.
  --un-gz <path>, to gzip compress output, or add '-bz2' to bzip2 compress output.)
  --quiet            print nothing to stderr except serious errors
  --met-file <path>  send metrics to file at <path> (off)
  --met-stderr       send metrics to stderr (off)
  --met <int>        report internal counters & metrics every <int> secs (1)
  --no-unal          suppress SAM records for unaligned reads
  --no-head          suppress header lines, i.e. lines starting with @
  --no-sq            suppress @SQ header lines
  --rg-id <text>     set read group id, reflected in @RG line and RG:Z: opt field
  --rg <text>        add <text> ("lab:value") to @RG line of SAM header.
                     Note: @RG line only printed when --rg-id is set.
  --omit-sec-seq     put '*' in SEQ and QUAL fields for secondary alignments.
  --sam-noqname-trunc Suppress standard behavior of truncating readname at first whitespace 
                      at the expense of generating non-standard SAM.

 Performance:
  -p/--threads <int> number of alignment threads to launch (1)
  --reorder          force SAM output order to match order of input reads
  --mm               use memory-mapped I/O for index; many 'bowtie's can share

 Other:
  --qc-filter        filter out reads that are bad according to QSEQ filter
  --seed <int>       seed for random number generator (0)
  --non-deterministic seed rand. gen. arbitrarily instead of using read attributes
  --version          print version information and quit
  -h/--help          print this usage message
'''
