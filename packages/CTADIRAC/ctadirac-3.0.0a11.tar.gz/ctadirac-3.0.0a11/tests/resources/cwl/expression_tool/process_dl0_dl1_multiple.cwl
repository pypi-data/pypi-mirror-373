%YAML 1.1
---
cwlVersion: v1.2
class: Workflow
doc: |
  Process multiple dl0 files using process_dl0_dl1 and then merge
  the individual result files into one common output file using
  the merge tool.
  This is useful for processing simulation files in DIRAC as processing
  a single file per DIRAC job would result in very many, very short
  jobs that are not ideal for the workflow management system.

inputs:
  input_files: File
  intermediate_filenames: string
  output_filename: string
  processing_config: File?


steps:
  filenames:
    run: ./internal/output_names.cwl
    in:
      input_file: input_files
    out: [output_filename, log_filename, provenance_log_filename]

  process_dl0_to_dl1:
    run: process_dl0_dl1.cwl
    in:
      dl0: input_files
      dl1_filename: filenames/output_filename
      log_filename: filenames/log_filename
      provenance_log_filename: filenames/provenance_log_filename
      processing_config: processing_config
    out:
      - dl1
      - log
      - provenance_log
  merge:
    run: merge.cwl
    in:
      input_files: process_dl0_to_dl1/dl1
      output_filename: output_filename
    out:
      - merged_output
      - log
      - provenance_log

outputs:
  merged_output:
    type: File
    outputSource: merge/merged_output

  merge_log:
    type: File
    outputSource: merge/log

  merge_provenance_log:
    type: File
    outputSource: merge/provenance_log

  intermediate_provenance_log:
    type: File
    outputSource: process_dl0_to_dl1/provenance_log

  intermediate_log:
    type: File
    outputSource: process_dl0_to_dl1/log
