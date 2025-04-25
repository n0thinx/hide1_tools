import os
import re
import json
from django.shortcuts import render
from django.conf import settings
from .forms import MultiFileUploadForm
from ntc_templates.parse import parse_output

start_cpu = 'last 60 minutes'
end_cpu = 'last 72 hours'

# Set NTC Templates directory
os.environ["NTC_TEMPLATES_DIR"] = os.path.join(settings.BASE_DIR, "parser_app", "templates")

# Regex patterns for different Cisco models
env_patterns = {
    "c1000": (r"cisco C1(.*?)\(Marvell", "cisco_ios_c1000"),
    "c9x": (r"cisco C9(.*?)\(ARM64\) processor", "cisco_ios_c9x"),
    "c9500": (r"cisco C9(.*?)\(X86\) processor", "cisco_ios_c9500"),
    "ws-c3": (r"cisco WS-C3(.*?)\(MIPS\) processor", "cisco_ios_ws-c3"),
}

def detect_env_model(text):
    """Detects the correct TextFSM template based on model type."""
    for model, (pattern, template) in env_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):  # Added re.IGNORECASE for case-insensitive match
            return template
    return "cisco_ios"  # Default to generic Cisco IOS template

def parse_command(template, command, text):
    """Parses a given show command output using NTC templates."""
    return parse_output(platform=template, command=command, data=text)

def extract_cpu_usage(text):
    cpu_usage = []

    # finding cisco cpu history for given text file with given parameter
    find_cpu = re.search(start_cpu + '(.*?)' + end_cpu, text, re.DOTALL)

    # -------------------------FINDING MAX CPU-----------------------------

    # Convert re.search result from find_cpu to string
    # Using split to delete few first row and rsplit to delete few last row
    # split for first 2 row, rsplit for last 13 row
    if find_cpu is None:
        max_cpu = 'Cant find max CPU'
        avg = 'Cant find average CPU'
    else:
        cpu_row_max = (find_cpu.group(1).split("\n", 2)[-1]).rsplit("\n", 13)[0]

        # get row from last 2 line
        cpu_first_row = cpu_row_max.splitlines()[-2]

        # get row from last line
        cpu_second_row = cpu_row_max.splitlines()[-1]

        # make an array which element is every single character in a row
        # remove first 4 character
        arr_first_row = list(cpu_first_row[4:])
        arr_second_row = list(cpu_second_row[4:])

        # make a for loop to join 2 array above
        if len(arr_first_row) == 0 :
            for i in range(0, len(arr_second_row)):
                if arr_second_row[i] == ' ':
                    arr_second_row[i] = ' '
                arr_join = arr_second_row[i]
                cpu_usage.append(arr_join)    
        elif len(arr_first_row) < len(arr_second_row):
            for i in range(0, len(arr_first_row)):
                if arr_first_row[i] == ' ':
                    arr_first_row[i] = ' '
                if arr_second_row[i] == ' ':
                    arr_second_row[i] = ' '
                arr_join = arr_first_row[i] + arr_second_row[i]
                cpu_usage.append(arr_join)
        else:
            for i in range(0, len(arr_second_row)):
                if arr_first_row[i] == ' ':
                    arr_first_row[i] = ' '
                if arr_second_row[i] == ' ':
                    arr_second_row[i] = ' '
                arr_join = arr_first_row[i] + arr_second_row[i]
                cpu_usage.append(arr_join)

        # convert cpu_usage array to int to get max value of its element
        # then return it to string again to write the result
        max_cpu = str(max(cpu_usage))

        # -------------------------FINDING CPU AVERAGE-----------------------------

        # split for first 2 row
        # rsplit for last 3 row
        # make an array from last 10 row

        cpu_row_avg = ((find_cpu.group(1).split("\n", 2)[-1]).rsplit("\n", 3)[0]).splitlines()[-10:]

        # check for # in every element of the cpu_row_avg
        avg_raw = [i for i in cpu_row_avg if '#' in i]

        # if there is no # in array, then it must be below 10% average
        if len(avg_raw) == 0:
            avg_cpu = '<10%'

        # else get first element of array because it must be highest
        # remove any non numerical character
        else:
            avg_cpu = re.sub("[^0-9]", "", avg_raw[0])

    return [
    {
        "cpu_max": max_cpu,
        "cpu_avg": avg_cpu
    }
]

def upload_file(request):
    if request.method == "POST":
        form = MultiFileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_files = request.FILES.getlist("files")
            parsed_results = {}

            required_parsers = {"version": "show version"}
            optional_parsers = {
                "inventory": "show inventory",
                "interfaces": "show interfaces",
                "cdp_neighbors_detail": "show cdp neighbors detail",
                "environment_custom": "show environment all",
                "environment_sensor": "show environment sensor",
                "environment_psu": "show environment psu",
                "environment_fan": "show environment fan",
            }

            selected_parsers = {
                key: value for key, value in optional_parsers.items()
                if form.cleaned_data.get(f"include_{key}", False)
            }

            for uploaded_file in uploaded_files:
                file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

                with open(file_path, "wb") as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                with open(file_path, "r", encoding="utf8", errors="ignore") as f:
                    text = f.read()

                # Detect environment model
                env_template = detect_env_model(text)
                print(f"Detected Template for {uploaded_file.name}: {env_template}")  # Debugging

                parsed_data = {}
                for key, cmd in {**required_parsers, **selected_parsers}.items():
                    if isinstance(cmd, list):  # If multiple commands exist, parse all
                        parsed_data[key] = {c: parse_command(env_template, c, text) for c in cmd}
                    else:
                        parsed_data[key] = parse_command(env_template, cmd, text)

                # Store environment model and parsed data
                parsed_results[uploaded_file.name] = {
                    "environment": env_template,
                    "data": parsed_data,
                }

            print(f"Final Parsed Results: {json.dumps(parsed_results, indent=4)}")  # Debugging

            json_filename = os.path.join(settings.MEDIA_ROOT, "parsed_output.json")
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(parsed_results, json_file, indent=4)

            return render(request, "parser_app/result.html", {"parsed_data": parsed_results})

    else:
        form = MultiFileUploadForm()

    return render(request, "parser_app/upload.html", {"form": form})
