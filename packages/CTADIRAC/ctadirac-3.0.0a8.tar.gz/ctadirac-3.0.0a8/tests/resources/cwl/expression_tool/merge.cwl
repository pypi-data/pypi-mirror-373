%YAML 1.1
---
cwlVersion: v1.2
class: CommandLineTool
baseCommand:
  - ctapipe-merge
  - --log-level=INFO
doc: |
  Merge multiple ctapipe output files into a single output file using ctapipe-merge.
  (DPPS-UC-130-1.8)
label: process single dl0 to dl1

inputs:
  output_filename:
    type: string
    doc: name of the output filename
    inputBinding:
      position: 1
      prefix: --output

  config:
    type: File?
    inputBinding:
      position: 2
      prefix: --config
    doc: The configuration file for ctapipe-merge

  log_filename:
    type: string
    doc: file in which to write log output
    default: ctapipe-merge.log
    inputBinding:
      position: 3
      prefix: --log-file

  provenance_log_filename:
    type: string
    doc: file in which to write the local provenance.
    default: ctapipe-merge.provenance.log
    inputBinding:
      position: 4
      prefix: --provenance-log

  input_files:
    type: File
    doc: |
      Paths to ctapipe files to be merged into output_filename
    inputBinding:
      position: 5


outputs:
  merged_output:
    type: File
    doc: output file.
    outputBinding:
      glob: $(inputs.output_filename)

  log:
    type: File
    doc:  log file for this step.
    outputBinding:
      glob: $(inputs.log_filename)

  provenance_log:
    type: File
    doc: ctapipe format provenance log for this step.
    outputBinding:
      glob: $(inputs.provenance_log_filename)
