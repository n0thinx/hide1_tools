import os
import re
import json
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import MultiFileUploadForm
from ntc_templates.parse import parse_output
from activity_log.utils import log_activity
from collections import OrderedDict
from django.http import FileResponse, Http404, HttpResponse
from django.template.loader import get_template
import logging

start_cpu = 'last 60 minutes'
end_cpu = 'last 72 hours'

os.environ["NTC_TEMPLATES_DIR"] = os.path.join(settings.BASE_DIR, "parser_app", "templates")
ALLOWED_EXTENSIONS = [".txt", ".log"]

env_patterns = {
    "c1000": (r"cisco C1(.*?)\(Marvell", "cisco_ios_c1000"),
    "c9200cx": (r"cisco C9200CX(.*?)\(ARM64\) processor", "cisco_ios_c9200cx"),
    "c9000": (r"cisco C9(.*?)\(ARM64\) processor", "cisco_ios_c9000"),
    "c9300": (r"cisco C93(.*?)\(X86\) processor", "cisco_ios_c9300"),
    "c9500": (r"cisco C95(.*?)\(X86\) processor", "cisco_ios_c9500"),
    "ws-c3": (r"cisco WS-C3(.*?)\(MIPS\) processor", "cisco_ios_ws-c3"),
    "isr_4300": (r"cisco ISR4(.*?) processor", "cisco_ios_isr_4300"),
}

textfsm_templates = {
    # "c1000": {
    #     "show environment all": "show_environment_all",
    # },
    # "isr_4300": {
    #     "show environment all": "show_environment_all",
    # },
    # "c9200cx": {
    #     "show environment sensor": "show_environment_sensor_9000",
    #     "show environment power": "show_environment_power_c9200cx",
    # },
    # "c9000": {
    #     "show environment sensor": "show_environment_sensor_9000",
    #     "show environment psu": "show_environment_psu_9000",
    #     "show environment fan": "show_environment_fan_9000",
    # },
    # "ws-c3": {
    #     "show environment sensor": "show_environment_sensor_ws-c3",
    #     "show environment psu": "show_environment_psu_ws-c3",
    #     "show environment fan": "show_environment_fan_ws-c3",
    # },
    # "c9300": {
    #     "show environment sensor": "show_environment_sensor_9000",
    #     "show environment psu": "show_environment_psu_9000",
    #     "show environment fan": "show_environment_fan_9000",
    # },
    # "c9500_17_09": {
    #     "show environment sensor": "show_environment_sensor_9500_17_9",
    #     "show environment psu": "show_environment_psu_9500_17_9",
    #     "show environment fan": "show_environment_fan_9500_17_9",
    # },
    # "c9500_17_12": {
    #     "show environment sensor": "show_environment_sensor_9500_17_12",
    #     "show environment psu": "show_environment_psu_9500_17_12",
    #     "show environment fan": "show_environment_fan_9500_17_12",
    # },
}

default_templates = {
    # "show processes memory sorted": "show_processes_memory_sorted",
    # "show version": "show_version",
    # "show inventory": "show_inventory",
    # "show interfaces": "show_interfaces",
    "show cdp neighbors detail" : "show_cdp_neighbors_detail"
}

def detect_env_model(text):
    """Detects the correct TextFSM template based on model type."""
    for model, (pattern, template) in env_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return model
    return "unknown"

def parse_command(platform, template, command, text):
    """Parses a given show command output using NTC templates."""
    return parse_output(platform=platform, command=command, data=text)

logger = logging.getLogger(__name__)

def download_json(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    user_folder = os.path.join(settings.MEDIA_ROOT, request.user.username)
    json_filename = os.path.join(user_folder, "parsed_output.json")

    logger.debug(f"Checking for file at: {json_filename}")

    if os.path.exists(json_filename):
        # DON'T use "with" here
        json_file = open(json_filename, 'rb')
        return FileResponse(json_file, as_attachment=True, filename='parsed_output.json')
    else:
        logger.error("JSON file not found.")
        raise Http404("JSON file not found.")

def extract_cpu_usage(text):
    cpu_usage = []

    find_cpu = re.search(start_cpu + '(.*?)' + end_cpu, text, re.DOTALL)

    if find_cpu is None:
        max_cpu = 'Cant find max CPU'
        avg = 'Cant find average CPU'
    else:
        cpu_row_max = (find_cpu.group(1).split("\n", 2)[-1]).rsplit("\n", 13)[0]

        cpu_first_row = cpu_row_max.splitlines()[-2]

        cpu_second_row = cpu_row_max.splitlines()[-1]

        arr_first_row = list(cpu_first_row[4:])
        arr_second_row = list(cpu_second_row[4:])

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

        max_cpu = str(max(cpu_usage))

        cpu_row_avg = ((find_cpu.group(1).split("\n", 2)[-1]).rsplit("\n", 3)[0]).splitlines()[-10:]

        avg_raw = [i for i in cpu_row_avg if '#' in i]

        if len(avg_raw) == 0:
            avg_cpu = '<10%'
        else:
            avg_cpu = re.sub("[^0-9]", "", avg_raw[0])

    return {
        "CPU Usage": [
            {
                "cpu_max": max_cpu,
                "cpu_avg": avg_cpu
            }
        ]
    } 

def calculate_memory_usage(memory_data):
    try:
        memory_total = int(memory_data["memory_total"])
        memory_used = int(memory_data["memory_used"])
        if memory_total == 0:
            memory_percent = 0
        else:
            memory_percent = round((memory_used / memory_total) * 100, 2)
        memory_data["memory_usage_percent"] = memory_percent
    except (KeyError, ValueError, TypeError):
        memory_data["memory_usage_percent"] = "N/A"
    return memory_data

def deduplicate_serial_and_hardware(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() in ["serial", "hardware"] and isinstance(value, list):
                data[key] = list(dict.fromkeys(value))
            else:
                deduplicate_serial_and_hardware(value)
    elif isinstance(data, list):
        for item in data:
            deduplicate_serial_and_hardware(item)

def detect_ios_version(text):
    match = re.search(r"Version (\d+\.\d+)", text)
    return match.group(1).replace(".", "_") if match else "unknown"

def upload_file(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    user_folder = os.path.join(settings.MEDIA_ROOT, request.user.username)
    os.makedirs(user_folder, exist_ok=True)
    json_filename = os.path.join(user_folder, "parsed_output.json")

    if request.method == "GET" and request.GET.get("action") == "upload":
        form = MultiFileUploadForm()
        return render(request, "parser_app/upload.html", {"form": form})

    if request.method == "POST":
        form = MultiFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_files = request.FILES.getlist("files")
            parsed_results = {}

            for uploaded_file in uploaded_files:
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                if file_extension not in ALLOWED_EXTENSIONS:
                    continue

                file_path = os.path.join(user_folder, uploaded_file.name)

                with open(file_path, "wb") as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                with open(file_path, "r", encoding="utf8", errors="ignore") as f:
                    text = f.read()

                switch_model = detect_env_model(text)
                switch_version = detect_ios_version(text)

                versioned_platform_key = f"{switch_model}_{switch_version}"
                parsed_data = {}

                # Try to detect the proper key for textfsm_templates
                parser_platform_key = None
                platform_templates = {}

                if versioned_platform_key in textfsm_templates:
                    platform_templates = textfsm_templates[versioned_platform_key]
                    parser_platform_key = versioned_platform_key
                elif switch_model in textfsm_templates:
                    platform_templates = textfsm_templates[switch_model]
                    parser_platform_key = switch_model

                # Step 1: Always parse commands from default_templates using "cisco_ios"
                for command, template in default_templates.items():
                    parsed_output = parse_command("cisco_ios", template, command, text)
                    
                    if command == "show processes memory sorted" and isinstance(parsed_output, list) and parsed_output:
                        parsed_output[0] = calculate_memory_usage(parsed_output[0])
                    
                    parsed_data[command] = parsed_output

                # Step 2: Parse platform-specific templates (if found)
                if platform_templates:
                    for command, template in platform_templates.items():
                        # Only parse if this command hasn’t already been parsed from default_templates
                        if command not in parsed_data:
                            parsed_output = parse_command(parser_platform_key, template, command, text)
                            parsed_data[command] = parsed_output
                    print(f"[INFO] Using platform key: {parser_platform_key} for file: {uploaded_file.name}")
                else:
                    print(f"[WARN] No platform-specific templates found for {uploaded_file.name}, using only default_templates")


                #cpu_data = extract_cpu_usage(text)
                deduplicate_serial_and_hardware(parsed_data)

                ordered_data = OrderedDict()
                #ordered_data.update(cpu_data)
                ordered_data.update(parsed_data)

                parsed_results[uploaded_file.name] = {
                    "model": parser_platform_key,
                    "data": ordered_data,
                }

            uploaded_names = ", ".join([f.name for f in uploaded_files])
            log_activity(request.user, f"Uploaded files: {uploaded_names}")

            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(parsed_results, json_file, indent=4)

            return render(request, "parser_app/result.html", {"parsed_data": parsed_results})
    else:
        form = MultiFileUploadForm()

        if os.path.exists(json_filename):
            with open(json_filename, "r", encoding="utf-8") as json_file:
                parsed_results = json.load(json_file)
            return render(request, "parser_app/result.html", {"parsed_data": parsed_results})

    return render(request, "parser_app/upload.html", {"form": form})
