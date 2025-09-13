from inspector_functions.check import compare_files_with_templates

if __name__ == "__main__":
    output_dir = "output_split_statistics_check"
    template_dir = "template"

    compare_files_with_templates(output_dir, template_dir)
