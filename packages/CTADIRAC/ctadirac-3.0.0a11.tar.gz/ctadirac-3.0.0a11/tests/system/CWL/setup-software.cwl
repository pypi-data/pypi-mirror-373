cwlVersion: v1.2

class: CommandLineTool
label: setup cta prod software
baseCommand: cta-prod-setup-software

inputs:
    name_package:
        type: string
        inputBinding:
            prefix: -p
            position: 1
    version_number:
        type: string
        inputBinding:
            prefix: -v
            position: 2
    job_type:
        type: string
        default: simulations
        inputBinding:
            prefix: -a
            position: 3
    compiler:
        type: string
        inputBinding:
            prefix: -g
            position: 4
outputs:
    dirac:
        type:
            type: array
            items: File
        outputBinding:
            glob: "dirac*"
    setup_path:
        type: File
        outputBinding:
            glob: "setup_script_path.txt"
