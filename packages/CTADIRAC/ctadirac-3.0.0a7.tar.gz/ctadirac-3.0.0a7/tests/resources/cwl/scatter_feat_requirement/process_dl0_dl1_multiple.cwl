%YAML 1.1
---
cwlVersion: v1.2
class: Workflow

requirements:
  ScatterFeatureRequirement: {}

inputs:
  input_files: File[]
  intermediate_filenames: string[]
  output_filename: string
  processing_config: File?


steps:
  process_dl0_to_dl1:
    run: process_dl0_dl1.cwl
    scatter: [dl0, dl1_filename]
    scatterMethod: dotproduct # zip arguments
    in:
      dl0: input_files
      dl1_filename: intermediate_filenames
      processing_config: processing_config
    out:
      - dl1
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
