cwlVersion: v1.2

class: CommandLineTool
label: run ctapipe processing with dirac_ctapipe-process_wrapper
baseCommand: dirac_ctapipe-process_wrapper

#requirements:
#  InitialWorkDirRequirement:
#    listing:
#      - $(inputs.inputDir)

inputs:
    config:
        type: File
        inputBinding:
            prefix: --config
            position: 3
    config_prod5b:
        type: File
        inputBinding:
            prefix: --config
            position: 4
#    inputDir:
#        type: Directory
#        inputBinding:
#            position: 2
#    setup_path:
#        type: File
#        inputBinding:
#            prefix: --file
#            position: 1

outputs:
    data_directory:
        type: Directory
        outputBinding:
            glob: Data
