%YAML 1.1
---
cwlVersion: v1.2
class: CommandLineTool
baseCommand:
  - ctapipe-process
  - --DataWriter.write_dl1_parameters=False
  - --DataWriter.write_dl1_images=False
  - --DataWriter.write_dl2=True
doc: |
  Processes a single file from DL1 to DL2 using the ctapipe-process tool.
  (DPPS-UC-130-1.2.2). Minimally, Hillas-style geometry reconstruction is
  performed, but energy, gammaness, mono reconstruction may be included by using
  an appropriate data processing configuration.
label: process single dl1 to dl2
inputs:
  processing_config:
    type: File?
    inputBinding:
      prefix: --config
    doc: |
      Sets the reconstruction parameters that apply to DL1 to DL2.
      See `ctapipe-process --help-all` for a list of all options, or the output
      of `ctapipe-quickstart` for sample configuration files.

  dl1:
    type: [File, string]
    doc: |
      path to input file, which can be at any data level transformable to DL2
      that is supported by the installed ctapipe io plugins. I can also be a
      URL.
    inputBinding:
      prefix: --input

  dl2_filename:
    type: string
    doc: name of the DL2 output file
    inputBinding:
      prefix: --output

  provenance_log_filename:
    type: string
    doc: file in which to write the local ctapipe-process provenance.
    default: ctapipe-process_dl1_dl2.provenance.log
    inputBinding:
      prefix: --provenance-log

outputs:
  dl2:
    type: File
    doc: HDF5 format output file.
    outputBinding:
      glob: $(inputs.dl2_filename)

  provenance_log:
    type: File
    doc: ctapipe format provenance log for this step.
    outputBinding:
      glob: $(inputs.provenance_log_filename)
