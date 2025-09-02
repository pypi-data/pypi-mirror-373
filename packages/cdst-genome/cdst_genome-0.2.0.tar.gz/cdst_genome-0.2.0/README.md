# CDST

CoDing Sequence Typer (CDST) is a simple, efficient, decentralized, and easily shareable genome typing and clustering method similar to cg/wgMLST, based on MD5 hash mapping of coding sequences (CDS) from genome assemblies.

----------------------------------------------------
## DEPENDENCIES

Before running CDST, ensure that the following dependencies are installed:

Python Packages:

- argparse
- hashlib
- json
- pandas
- biopython
- networkx
- scipy

Install them using:
```
pip install biopython pandas networkx scipy
```
## Tested Environment

We tested the pipeline in the following environment:

- Python 3.12
- Biopython 1.85
- pandas 2.2.2
- SciPy 1.13.1
- scikit-learn 1.5.1
- networkx 3.3
- matplotlib 3.9.x
- joblib 1.4.x

Other versions may also work, but have not been systematically tested.  

## INSTALLATION

Clone this repository and navigate into the project folder:
```
git clone https://github.com/l1-mh/cdst.git
cd cdst
```

Make the script executable:
```
chmod +x cdst.py
```

Alternatively, you can run it directly using Python:
```
python cdst.py --help
```

## USAGE

CDST provides multiple subcommands for different analysis steps.

### Run the Full Pipeline Above:
```
cdst.py run -i sample_cds/*.ffn -o output/ -T both
```

### Generate the Distance Matrix, MST, and Hierarchical Clusters from CDS Sequences:

1. Generate JSON database of MD5 Hashes from CDS FASTA Files:
```
cdst.py generate -i sample_cds/*.ffn -o output/
```

2. Compute Distance Matrices:
```
cdst.py matrix -j output/md5_hashes.json -o output/
```

3. Generate Minimum Spanning Tree (MST):
```
cdst.py mst -m output/difference_matrix.csv -o output/
```

4. (Optional) Generate Hierarchical Clustering Tree:
```
cdst.py hc -m output/difference_matrix.csv -o output/
```

### Merge Databases:

Can do with only JSON databases. But merging JSON databases with Distance Matrixes (with --matrix flag) will save you time.

Use --mst flag if you want to produce the MST.

Make sure that every corresponding Distance Matrix file are in the same folder with JSON database and the file names are as below:
- /dir1/md5_hashes.json
- /dir1/comparison_matrix.csv
```
python cdst.py join -d dir1/ dir2/ -o merged_output/ --matrix --mst
```

### Compare New Samples Against an Existing Dataset:

```
python cdst.py test -i new_samples/*.ffn -j output/md5_hashes.json -o output/
```

## INPUT FILES

CDST requires FASTA-formatted CDS sequences as input. Each sequence should be in standard FASTA format (also known as .FFN format), such as:
```
>gene1
ATGCGTACGTAGCTAGCTAG
>gene2
ATGCGTAGCTAGCTAGTACG
```

### Predicting CDS from Genome Assemblies

If you have a genome assembly (FASTA format), you need to predict CDS sequences before using CDST. We recommend Prodigal, a widely used gene prediction tool for prokaryotic genomes. 

Run the following command to predict CDS from an assembly file:
```
prodigal -i assembly.fasta -d cds_output.ffn
```
The resulting cds_output.ffn file can be directly used as input for CDST.

- You may use other CDS prediction tools like Glimmer or Augustus, but ensure consistency across samples.

- If your dataset already contains FASTA-formatted CDS, no additional processing is needed.

- CDS sequences containing ambiguous characters (e.g., N) will be ignored by CDST.

## OUTPUT FILES

Depending on the commands used, the following files will be generated:
- md5_hashes.json:        Stores MD5 hashes for CDS sequences.
- comparison_matrix.csv:  Number of shared hashes between samples.
- difference_matrix.csv:  Distance matrix based on hash differences.
- edge_list.csv:          Edge list representation of pairwise distances.
- mst.csv:                Minimum Spanning Tree (MST) edge list.
- hc.newick:              Hierarchical Clustering tree in Newick format.
- comparison_results.csv: Closest matches (for new samples comparisons only).

