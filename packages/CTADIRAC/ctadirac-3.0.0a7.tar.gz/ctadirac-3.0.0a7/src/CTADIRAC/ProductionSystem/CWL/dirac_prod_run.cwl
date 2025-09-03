cwlVersion: v1.2

class: CommandLineTool
label: run MC simulation with dirac_prod_run
baseCommand: dirac_prod_run

inputs:
    setup_path:
        type: File
        inputBinding:
            prefix: --file
            position: 10
    start_run_number:
        type: int
        inputBinding:
            prefix: --start_run
            position: 1
            separate: true
    run_number:
        type: int
        inputBinding:
            prefix: --run
            position: 2
            separate: true
    moon:
        type: string?
        inputBinding:
            position: 3
    sct:
        type: string?
        inputBinding:
            position: 4
    magic:
        type: string?
        inputBinding:
            position: 5
    site:
        type: string
        inputBinding:
            position: 6
    particle:
        type: string
        inputBinding:
            position: 7
    pointing_dir:
        type: string
        inputBinding:
            position: 8
    zenith_angle:
        type: int
        inputBinding:
            position: 9

outputs:
    data_directory:
        type: Directory
        outputBinding:
            glob: Data
