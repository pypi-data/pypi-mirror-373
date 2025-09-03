%YAML 1.1
---
cwlVersion: v1.2
class: ExpressionTool
doc: |
  compute output filenames from input filenames

requirements:
  InlineJavascriptRequirement: {}

inputs:
  input_file: File
  data_level:
    type: string
    default: dl1

outputs:
  output_filename: string
  log_filename: string
  provenance_log_filename: string

expression: |
  ${
    var name = inputs.input_file.basename;
    var ext = "." + inputs.data_level + ".h5"
    var output;

    if (name.match(/simtel(\.zst|\.gz)?$/) !== null) {
      output = name.replace(/\.simtel(\.zst|\.gz)?$/, ext);
    } else if (name.match(/(\.dl.*)\.h5$/) !== null) {
      output = name.replace(/(\.dl.*)\.h5$/, ext);
    } else {
      throw new Error("Input file '" + name + "' does not match expected pattern.")
    }
    return {
      output_filename: output,
      log_filename: output + ".log",
      provenance_log_filename: output + ".provlog",
    }
  }
