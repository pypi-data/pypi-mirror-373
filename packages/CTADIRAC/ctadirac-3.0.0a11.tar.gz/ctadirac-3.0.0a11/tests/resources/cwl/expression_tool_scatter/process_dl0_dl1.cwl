%YAML 1.1
---
cwlVersion: v1.2
class: CommandLineTool
baseCommand:
  - ctapipe-process
  - --DataWriter.write_dl1_parameters=True
  - --DataWriter.write_dl2=False
doc: |
  Processes a single file from DL0 to DL1 using the ctapipe-process tool.
  (DPPS-UC-130-1.2.1)
label: process single dl0 to dl1
inputs:
  processing_config:
    type: File?
    inputBinding:
      prefix: --config
    doc: |
      Sets the reconstruction parameters that apply to DL0 to DL1.
      See `ctapipe-process --help-all` for a list of all options, or the output
      of `ctapipe-quickstart` for sample configuration files.

  dl0:
    type: [File, string]
    doc: |
      path to input file, which can be at any data level transformable to DL1
      that is supported by the installed ctapipe io plugins. I can also be a
      URL.
    inputBinding:
      prefix: --input

  dl1_filename:
    type: string
    doc: name of the DL1 output file
    inputBinding:
      prefix: --output

  log_filename:
    type: string
    doc: file in which to write log output
    default: ctapipe-process.log
    inputBinding:
      prefix: --log-file

  provenance_log_filename:
    type: string
    doc: file in which to write the local ctapipe-process provenance.
    default: ctapipe-process_dl0_dl1.provenance.log
    inputBinding:
      prefix: --provenance-log

outputs:
  dl1:
    type: File
    doc: HDF5 format output file.
    outputBinding:
      glob: $(inputs.dl1_filename)

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
