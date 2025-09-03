import RNA
import subprocess, tempfile, textwrap, shlex, pathlib

seq1 = "AGTGCAGAGAAAATCGGCCAGTTTTCTCTGCCTGCAGTCCGCATGCCGTATCGGGCCTTGGGTTCTAACCTGTTGCGTAGATTTATGCAGCGGACTGCCTTTCTCCCAAAGTGATAAACCGGACAGTATCATGGACCGGTTTTCCCGGTAATCCGTATTTACAAGGCTGGTTTCACT"  

#reference folding of the native IS621 bRNA
seq2 = "AGTGCAGAGAAAATCGGCCAGTTTTCTCTGCCTGCAGTCCGCATGCCGTATCGGGCCTTGGGTTCTAACCTGTTGCGTAGATTTATGCAGCGGACTGCCTTTCTCCCAAAGTGATAAACCGGACAGTATCATGGACCGGTTTTCCCGGTAATCCGTATTTACAAGGCTGGTTTCACT"
db2 =  "...(((((((((((......))))))))))).((((((((((.(((............(((((....)))))..............))))).)))))))).........((((....(((.............((((((.....)))))...)...............)))..))))"

#predict the MFE folding of the designed bRNA
seq1 = seq1
db1, mfe = RNA.fold(seq1)

# prepare FASTA-like input that RNAforester accepts
payload = textwrap.dedent(f"""
>x
{seq1}
{db1}
>y
{seq2}
{db2}
""").lstrip()
print(payload)
# build CLI
args = ["RNAforester"]
args.append("-r")          #relative scoring from 0-1: sr(a,b) = 2*s(a,b)/(s(a,a)+s(b,b))
args.append("--score")   # print only the optimal score

# run
proc = subprocess.run(args, input=payload.encode(), capture_output=True, check=True)
out = proc.stdout.decode().strip()

# when --score is used, stdout is usually just a number
try:
    score = float(out.splitlines()[-1].split()[0])
except Exception:
    score = None

print(score)