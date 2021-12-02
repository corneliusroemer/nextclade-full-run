import os
# localrules: download_sequences, download_metadata, download_exclude, download_clades, preprocess, download_color_ordering, download_curated_pango, download_pango_aliases

subsample_number = 1000
split_number = 10

rule all:
    input: "nextclade.tsv"

rule download_sequences:
    output: "data/sequences.fasta.xz"
    shell: "aws s3 cp s3://nextstrain-ncov-private/sequences.fasta.xz {output}"

rule subsample_sequences:
    input: rules.download_sequences.output
    output: temp("data/subsample.fasta")
    shell: "var=$( {{ gzcat {input} ||:; }} | seqkit head -n {subsample_number} -o {output})" 

rule split_sequences:
    input: "data/subsample.fasta"
    output: temp(expand("split/subsample.part_{part:03d}.fasta", part=range(1,split_number+1)))
    shell: "seqkit split2 {input} -p {split_number} -O split" 

rule download_nextclade_dataset:
    output: directory("data/nextclade_dataset")
    shell: "nextclade dataset get --name='sars-cov-2' --output-dir={output}"

rule run_nextclade:
    input:
        sequences = "split/subsample.part_{part}.fasta",
        tree = "data/auspice.json",
        dataset = rules.download_nextclade_dataset.output
    output:
        output_tsv = temp("results/nextclade_results_{part}.tsv"),
    params:
        output_alignments = "data/alignments_{part}"
    shell:
        """
        nextclade run \
            -i {input.sequences} \
            --input-dataset {input.dataset} \
            -a {input.tree} \
            -t {output.output_tsv} \
            -d {params.output_alignments};
        rm -r {params.output_alignments}
        """

rule collect_nextclade_results:
    input: expand("results/nextclade_results_{part:03d}.tsv", part=range(1,split_number+1))
    output: "nextclade.tsv"
    shell: "cat {input} | dos2unix > {output}"
