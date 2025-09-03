cwlVersion: v1.2

class: CommandLineTool
label: upload file on SE and register in catalog
baseCommand: cta-user-managedata

requirements:
  InitialWorkDirRequirement:
    listing:
      - $(inputs.dataDir)

inputs:
    output_pattern:
        type: string
        inputBinding:
            position: 1
    base_path:
        type: string
        inputBinding:
            position: 2
    storage_elements:
        type: string
        inputBinding:
            position: 3
    catalogs:
        type: string
        inputBinding:
            position: 4
    output_type:
        type: string
        inputBinding:
            position: 5
    dataDir:
        type: Directory
        inputBinding:
            position: 6

outputs: []
