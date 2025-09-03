%YAML 1.1
---
cwlVersion: v1.2
class: Workflow
requirements:
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
doc: |
  Process an input file to from DL0 to separate DL1 and DL2 outputs.
inputs:
  processing_config:
    doc: data processing configuration for ctapipe-process.
    type: File?

  dl0:
    doc: DL0 data file in format supported by ctapipe.
    type: File

outputs:
  dl1:
    type: File
    doc: DL1 data file in ctapipe hdf5 format
    outputSource: dl0_to_dl1/dl1
  dl2:
    type: File
    doc: DL2 data file in ctapipe hdf5 format
    outputSource: dl1_to_dl2/dl2

steps:
  dl0_to_dl1:
    run: process_dl0_dl1.cwl
    in:
      processing_config: processing_config
      dl0: dl0
      dl1_filename:
        valueFrom: $(inputs.dl0.basename.replace(/\.simtel\.zst$/, '.dl1.h5'))
    out: [dl1, provenance_log]

  dl1_to_dl2:
    run: process_dl1_dl2.cwl
    in:
      processing_config: processing_config
      dl1: dl0_to_dl1/dl1
      dl2_filename:
        valueFrom: $(inputs.dl1.basename.replace(/\.dl1.h5$/, '.dl2.h5'))
    out: [dl2, provenance_log]
