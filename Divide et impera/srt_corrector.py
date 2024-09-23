def modify_srt_file(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    modified_lines = []
    for i in range(0, len(lines), 4):
        seq_number = lines[i].strip()
        time_range = lines[i + 1].strip()
        caption = lines[i + 2].strip().upper()  # Convert caption to uppercase

        # Extract start and end times
        start_time, end_time = time_range.split(' --> ')

        # Extract next start time if available
        if i + 5 < len(lines):
            next_start_time = lines[i + 5].split(' --> ')[0].strip()
        else:
            # Handle the last caption
            next_start_time = end_time  # Keep the end time of the last caption as the next start time

        # Append modified lines
        modified_lines.extend([seq_number, '\n', f"{start_time} --> {next_start_time}", '\n', caption, '\n', '\n'])

    with open(output_file, 'w') as f:
        f.writelines(modified_lines)

modify_srt_file("../audio_temp/sub.srt", "audio_temp/sub_final.srt")
