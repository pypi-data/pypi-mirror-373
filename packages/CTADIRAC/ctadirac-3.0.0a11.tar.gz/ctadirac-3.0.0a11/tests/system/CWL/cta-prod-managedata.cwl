cwlVersion: v1.2

class: CommandLineTool
label: upload file on SE and register in catalog
baseCommand: cta-prod-managedata

inputs:
    metadata:
        type: string
        inputBinding:
            position: 1
    file_metadata:
        type: string
        inputBinding:
            position: 2
    base_path:
        type: string
        inputBinding:
            position: 3
    output_pattern:
        type: string
        inputBinding:
            position: 4
    name_package:
        type: string
        inputBinding:
            position: 5
    program_category:
        type: string
        inputBinding:
            position: 6
    catalogs:
        type: string
        inputBinding:
            position: 7
    output_type:
        type: string
        inputBinding:
            position: 8

outputs: []
