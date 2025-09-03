def sample_data(
        input_path,
        output_path=None,
        n=100,
        random_sampling=True,
) -> None:
    import os
    import json
    import random

    if output_path is None:
        basename = os.path.basename(input_path)
        filename = os.path.splitext(basename)[0]
        sample_way = "random" if random_sampling else "top"
        output_path = input_path.replace(filename, f'{filename}~{sample_way}_sample{n}')

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    is_jsonl_format = input_path.lower().endswith('.jsonl')

    data_records = []
    if is_jsonl_format:
        with open(input_path, 'r', encoding='utf-8') as file_handler:
            for line in file_handler:
                if line.strip():
                    try:
                        data_records.append(json.loads(line))
                    except json.JSONDecodeError:
                        print(f"Warning: Skipping invalid JSON line")
    else:
        with open(input_path, 'r', encoding='utf-8') as file_handler:
            try:
                file_content = json.load(file_handler)
                if isinstance(file_content, list):
                    data_records = file_content
                else:
                    data_records = [file_content]
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON file: {error}")

    if not data_records:
        print("Warning: Input file contains no valid data")
        with open(output_path, 'w', encoding='utf-8') as file_handler:
            if is_jsonl_format:
                pass
            else:
                file_handler.write('[]')
        return

    total_record_count = len(data_records)
    if isinstance(n, float):
        if not 0.0 <= n <= 1.0:
            raise ValueError("Ratio must be between 0.0 and 1.0")
        sample_count = max(1, int(total_record_count * n))
    else:
        sample_count = min(n, total_record_count)

    if random_sampling:
        selected_samples = random.sample(data_records, sample_count)
    else:
        selected_samples = data_records[:sample_count]

    output_is_jsonl = is_jsonl_format or output_path.lower().endswith('.jsonl')

    with open(output_path, 'w', encoding='utf-8') as file_handler:
        if output_is_jsonl:
            for item in selected_samples:
                file_handler.write(json.dumps(item, ensure_ascii=False) + '\n')
        else:
            is_single_object = len(data_records) == 1 and not isinstance(data_records[0], list) and len(selected_samples) == 1
            if is_single_object:
                json.dump(selected_samples[0], file_handler, ensure_ascii=False, indent=2)
            else:
                json.dump(selected_samples, file_handler, ensure_ascii=False, indent=2)

    print(f"Successfully sampled {len(selected_samples)} from {total_record_count} records")