import os
# localrules: download_sequences, download_metadata, download_exclude, download_clades, preprocess, download_color_ordering, download_curated_pango, download_pango_aliases

subsample_number = 100
subsample_ratio = 0.01
split_number = 10

# Filter to list of strain names
# Filter to pango designated sequences

rule all:
    input: "nextclade.tsv"

rule download_metadata:
    output: "data/metadata.tsv.gz"
    shell: "aws s3 cp s3://nextstrain-ncov-private/metadata.tsv.gz {output}"

rule download_sequences:
    output: "data/sequences.fasta.xz"
    shell: "aws s3 cp s3://nextstrain-ncov-private/sequences.fasta.xz {output}"

rule download_curated_pango:
    output: "pre-processed/lineages.csv"
    params: "https://raw.githubusercontent.com/cov-lineages/pango-designation/master/lineages.csv"
    shell: "curl {params} -o {output}"

rule extract_metadata_strain_names:
    input: rules.download_metadata.output
    output: "pre-processed/metadata_strainnames.txt"
    shell: "gzcat {input} | tsv-select -H -f strain >{output} "

rule normalize_pango_strain_names:
    message: "Convert pango strain names to nextclade strain names"
    input:
        metadata_strainnames = rules.extract_metadata_strain_names.output,
        pango = rules.download_curated_pango.output,
    output:
        pango_designations = "pre-processed/designations.csv",
        pango_designated_strains = "pre-processed/designated_strains.txt",
    shell:
        """
        python3 scripts/pango_strain_rename.py \
            --metadata-strainnames {input.metadata_strainnames} \
            --pango-in {input.pango} \
            --pango-designations {output.pango_designations} \
            --pango-designated-strains {output.pango_designated_strains} \
            2>&1
        """

rule select_sequences:
    input: 
        fasta = rules.download_sequences.output,
        strain_list = rules.normalize_pango_strain_names.output.pango_designated_strains,
    output: "data/designated.fasta.gz"
    shell: "xzcat --threads 4 {input.fasta} | seqkit grep --threads 6 -f {input.strain_list} -o {output}"

rule subsample_sequences:
    input: rules.select_sequences.output
    output: temp("data/subsample.fasta.gz")
    shell: "seqkit sample -p {subsample_ratio} -o {output} {input}" 

rule split_sequences:
    input: rules.subsample_sequences.output
    output: temp(expand("split/{{filename}}.part_{part:03d}.fasta.gz", part=range(1,split_number+1)))
    params: lambda w: f"data/{w.filename}.fasta.gz"
    shell: 
        """
        mv {input} {params}; \
        seqkit split2 {params} -p {split_number} -O split; \
        rm {params}
        """

rule download_nextclade_dataset:
    output: directory("data/nextclade_dataset")
    shell: "nextclade dataset get --name='sars-cov-2' --output-dir={output}"

rule run_nextclade:
    input:
        sequences = expand("split/designated_subsample.part_{{part}}.fasta.gz"),
        tree = "data/auspice.json",
        dataset = rules.download_nextclade_dataset.output
    output:
        output_tsv = temp("results/nextclade_results_{part}.tsv"),
    params:
        output_alignments = "data/alignments_{part}",
        staged_fasta = "tmp/staged_fasta_{part}.fasta"
    shell:
        """
        gunzip -c {input.sequences} > {params.staged_fasta}; \
        nextclade run \
            -i {params.staged_fasta} \
            --input-dataset {input.dataset} \
            -a {input.tree} \
            -t {output.output_tsv} \
            -d {params.output_alignments};
        rm -r {params.output_alignments}; \
        rm {params.staged_fasta};
        """

rule collect_nextclade_results:
    input: expand("results/nextclade_results_{part:03d}.tsv", part=range(1,split_number+1))
    output: "nextclade.tsv"
    shell: "cat {input} | dos2unix > {output}"
