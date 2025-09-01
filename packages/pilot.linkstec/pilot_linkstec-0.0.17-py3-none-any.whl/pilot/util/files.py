import os
import csv

class FileUtil:
    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def read(path: str, encoding: str = "utf-8") -> str:
        with open(path, "r", encoding=encoding) as f:
            return f.read()

    @staticmethod
    def write(path: str, data: str, encoding: str = "utf-8") -> None:
        with open(path, "w", encoding=encoding) as f:
            f.write(data)

    @staticmethod
    def export_files_to_csv(folder: str, csv_path: str) -> None:
        import re
        rows = []
        max_depth = 0
        file_infos = []
        for root, _, files in os.walk(folder):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), folder)
                parts = rel_path.split(os.sep)
                file_infos.append((parts, rel_path, root))
                if len(parts) > max_depth:
                    max_depth = len(parts)
        headers = ["No", "file", "ext", "folder_rel_path", "prefix_before_number"] + [f"fold{i + 1}" for i in range(max_depth - 1)]
        for idx, (parts, rel_path, folder_full_path) in enumerate(file_infos, 1):
            file_name = parts[-1]
            ext = os.path.splitext(file_name)[1][1:]
            folders = parts[:-1]
            folder_rel_path = os.path.relpath(folder_full_path, folder)
            match = re.match(r"([^\d]*)(\d.*)?", file_name)
            prefix_before_number = match.group(1) if match and match.group(2) else ""
            row = [idx, file_name, ext, folder_rel_path, prefix_before_number] + folders + [""] * (max_depth - 1 - len(folders))
            rows.append(row)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)