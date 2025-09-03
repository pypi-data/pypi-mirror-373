cwlVersion: v1.2
class: Workflow

inputs:
  name_package: string
  version_number: string
  job_type: string
  compiler: string
  start_run_number: int
  run_number: int
  site: string
  particle: string
  pointing_dir: string
  zenith_angle: int
  output_pattern: string
  base_path: string
  storage_elements: string
  catalogs: string
  output_type: string
outputs: []

steps:
  setup_software:
    run: setup-software.cwl
    in:
      name_package: name_package
      version_number: version_number
      job_type: job_type
      compiler: compiler
    out: [dirac, setup_path]
  run_simulation:
    run: dirac_prod_run.cwl
    in:
      setup_path : setup_software/setup_path
      start_run_number: start_run_number
      run_number: run_number
      site: site
      particle: particle
      pointing_dir: pointing_dir
      zenith_angle: zenith_angle
    out: [data_directory]
  manage_data:
    run: cta-user-managedata.cwl
    in:
      output_pattern: output_pattern
      base_path: base_path
      storage_elements: storage_elements
      catalogs: catalogs
      output_type: output_type
      dataDir: run_simulation/data_directory
    out: []
